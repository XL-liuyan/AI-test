"""Agent 闭环：生成/修复用例直到通过或达到上限。

流程：生成（或给定文件）→ 执行 → 通过则结束；失败则把代码+输出交给 DeepSeek
重写文件 → 再执行 …（最多 max_attempts 轮）。每轮结果写入 reports/agent_*.md。
"""
import re
from datetime import datetime
from pathlib import Path

from ai.deepseek import DeepSeekLLM
from ai.pytest_runner import run_pytest
from ai.use_case_gen import generate_tests
from config import settings

FIX_SYSTEM_PROMPT = (
    "你是资深接口自动化测试工程师。下面会给出一个 pytest 测试文件的当前代码，以及它的执行输出（可能包含失败）。\n"
    "请直接输出修正后的完整测试文件代码（只输出一个 ```python 代码块，不要任何解释文字）：\n"
    "1. 保留所有能通过的用例，只修复失败的\n"
    "2. 断言必须符合接口真实响应结构：被测服务 GET /health -> {\"status\":\"ok\"}；"
    "GET /users -> {\"data\":[{\"id\":1,\"name\":\"Alice\"},{\"id\":2,\"name\":\"Bob\"}]}；"
    "POST /echo -> {\"echo\":<原样回显请求体>}；其余路径 404 {\"error\":\"not found\"}\n"
    "3. 用例函数接收 api_client fixture，不要 import requests、不要自行构造客户端\n"
)


def run_agent(target: str = "", task_desc: str = "", max_attempts: int = 3) -> dict:
    """执行 Agent 闭环。

    返回：{"path", "history": [{"attempt","passed","output","fix_note"}...], "passed", "report"}
    """
    llm = DeepSeekLLM()

    if target:
        path = Path(target)
        if not path.is_absolute():
            path = settings.PROJECT_ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        created_by_ai = False
    else:
        if not task_desc:
            raise ValueError("agent 模式需要提供用例描述或现有测试文件路径")
        path, _ = generate_tests(task_desc)
        created_by_ai = True

    history: list[dict] = []
    for attempt in range(1, max_attempts + 1):
        exit_code, output = run_pytest(str(path))
        passed = exit_code == 0
        entry = {"attempt": attempt, "passed": passed, "output": output[:4000]}
        history.append(entry)

        if passed:
            break

        # 失败 → 让 AI 直接重写整个文件
        code_text = path.read_text(encoding="utf-8")
        fix = llm.chat(
            [
                {"role": "system", "content": FIX_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"【当前代码】\n{code_text}\n\n【第 {attempt} 次执行输出】\n{history[-1]['output']}",
                },
            ],
            temperature=0.2,
            max_tokens=3000,
        )
        match = re.search(r"```python\s*(.*?)\s*```", fix, re.S)
        new_code = match.group(1) if match else fix.strip()
        path.write_text(new_code, encoding="utf-8")
        entry["fix_note"] = f"AI 已重写文件（{len(new_code)} 字符）"

    passed = bool(history and history[-1]["passed"])
    report = settings.PROJECT_ROOT / "reports" / f"agent_{datetime.now():%Y%m%d_%H%M%S}.md"
    lines = [
        "# Agent 闭环报告",
        "",
        f"- 时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
        f"- 目标文件：{path}",
        f"- 来源：{'自然语言生成' if created_by_ai else '用户指定文件'}",
        f"- 轮数上限：{max_attempts}",
        f"- 最终结果：{'全部通过' if passed else '未通过'}",
        "",
        "## 每轮迭代",
        "",
    ]
    for h in history:
        status = "通过" if h["passed"] else "失败"
        lines.append(f"- 第 {h['attempt']} 轮：{status}")
        if h.get("fix_note"):
            lines.append(f"  - {h['fix_note']}")
    if not passed:
        lines.append("\n## 最后失败输出\n```\n" + history[-1]["output"] + "\n```")
    report.write_text("\n".join(lines), encoding="utf-8")

    return {"path": path, "history": history, "passed": passed, "report": report}
