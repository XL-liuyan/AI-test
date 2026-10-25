"""自然语言 → pytest 用例文件 + 规范化用例文档 → 保存到 tests/generated/ 与 reports/。"""
import re
from datetime import datetime
from pathlib import Path

from ai.deepseek import DeepSeekLLM
from config import settings

SYSTEM_PROMPT = (
    "你是一名 Python 接口自动化测试工程师。根据用户需求编写 pytest 测试代码，硬性要求：\n"
    "1. 输出两个代码块，顺序固定：\n"
    "   第一个是 ```python 代码块（可执行用例，块内不要任何解释文字）；\n"
    "   第二个是 ```markdown 代码块（规范化用例文档，格式见第 6 条）\n"
    "2. 用例函数统一接收名为 api_client 的 fixture（由 tests/conftest.py 提供），不要 import requests、不要自己构造客户端\n"
    "3. 每个用例是独立的 def test_xxx(api_client)，断言具体明确\n"
    "4. 被测服务是本地 Mock API（http://127.0.0.1:8000），响应格式如下：\n"
    "   - GET /health -> {\"status\": \"ok\"}\n"
    "   - GET /users -> {\"data\": [{\"id\": 1, \"name\": \"Alice\"}, {\"id\": 2, \"name\": \"Bob\"}]}\n"
    "   - POST /echo -> {\"echo\": <原样回显请求体>}\n"
    "   - 其余路径返回 404 {\"error\": \"not found\"}\n"
    "   断言必须按上述真实响应结构编写（注意 /users 的数据在 data 字段里，/echo 的返回包在 echo 字段里）\n"
    "5. 每个测试函数的 docstring 必须包含规范用例元素，格式如下（一行一个标签，测试步骤为编号列表）：\n"
    "   [用例编号] TC-001\n"
    "   [用例标题] <一句话标题>\n"
    "   [前置条件] <前置条件描述>\n"
    "   [测试步骤]\n"
    "   1. <步骤>\n"
    "   2. <步骤>\n"
    "   [预期结果] <可验证的预期描述>\n"
    "   用例编号按 TC-001、TC-002... 顺序递增，docstring 写在函数内第一行\n"
    "6. markdown 代码块内容是规范化用例文档：第一行为文档标题（如：# 登录校验用例说明），\n"
    "   然后紧跟表格，表格列固定为：| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |，\n"
    "   每个用例一行，测试步骤内多条用 <br> 分隔，不要使用其他格式\n"
)


def _extract_case_table(code: str) -> str:
    """从代码 docstring 的 [标签] 元素提取为 markdown 表格（AI 未输出文档块时兜底）。"""
    rows = []
    for b in re.findall(r'"""(.*?)"""', code, re.S):
        num = re.search(r"\[用例编号\]\s*(\S+)", b)
        title = re.search(r"\[用例标题\]\s*(.+)", b)
        pre = re.search(r"\[前置条件\]\s*(.+)", b)
        steps = re.search(r"\[测试步骤\](.*?)\[预期结果\]", b, re.S)
        exp = re.search(r"\[预期结果\]\s*(.+)", b)
        step_txt = ""
        if steps:
            step_txt = "<br>".join(x.strip() for x in re.findall(r"^\s*\d+\.\s*(.+)$", steps.group(1), re.M))
        rows.append(
            f"| {num.group(1).strip() if num else '-'} "
            f"| {title.group(1).strip() if title else '-'} "
            f"| {pre.group(1).strip() if pre else '-'} "
            f"| {step_txt or '-'} "
            f"| {exp.group(1).strip() if exp else '-'} |"
        )
    return "\n".join(rows)


def generate_tests(description: str, name: str = "") -> tuple[Path, Path]:
    """把自然语言需求交给 DeepSeek，生成用例文件与规范化用例文档。

    返回 (pytest 代码路径, 用例说明文档路径)。
    """
    llm = DeepSeekLLM()
    content = llm.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"需求：{description}"},
        ],
        temperature=0.2,
        max_tokens=4000,
    )
    m_py = re.search(r"```python\s*(.*?)\s*```", content, re.S)
    code = m_py.group(1) if m_py else content.strip()
    m_md = re.search(r"```markdown\s*(.*?)\s*```", content, re.S)
    doc_md = m_md.group(1).strip() if m_md else ""

    if not name:
        name = datetime.now().strftime("auto_%Y%m%d_%H%M%S")
    py_path = settings.PROJECT_ROOT / "tests" / "generated" / f"test_{name}.py"
    py_path.parent.mkdir(parents=True, exist_ok=True)
    py_path.write_text(code, encoding="utf-8")

    if not doc_md:
        table = _extract_case_table(code)
        doc_md = (
            f"# {name} 用例说明\n\n"
            "| 用例编号 | 用例标题 | 前置条件 | 测试步骤 | 预期结果 |\n"
            "|---|---|---|---|---|\n"
            f"{table or '（未能从代码提取，请查看源码 docstring）'}\n"
        )
    md_path = settings.PROJECT_ROOT / "reports" / f"testcases_{name}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(doc_md, encoding="utf-8")
    return py_path, md_path
