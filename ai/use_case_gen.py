"""自然语言 → pytest 用例文件 → 保存到 tests/generated/。"""
import re
from datetime import datetime
from pathlib import Path

from ai.deepseek import DeepSeekLLM
from config import settings

SYSTEM_PROMPT = (
    "你是一名 Python 接口自动化测试工程师。根据用户需求编写 pytest 测试代码，硬性要求：\n"
    "1. 只输出一个 ```python 代码块，不要任何解释文字或额外输出\n"
    "2. 用例函数统一接收名为 api_client 的 fixture（由 tests/conftest.py 提供），不要 import requests、不要自己构造客户端\n"
    "3. 每个用例是独立的 def test_xxx(api_client)，断言具体明确\n"
    "4. 被测服务是本地 Mock API（http://127.0.0.1:8000），响应格式如下：\n"
    "   - GET /health -> {\"status\": \"ok\"}\n"
    "   - GET /users -> {\"data\": [{\"id\": 1, \"name\": \"Alice\"}, {\"id\": 2, \"name\": \"Bob\"}]}\n"
    "   - POST /echo -> {\"echo\": <原样回显请求体>}\n"
    "   - 其余路径返回 404 {\"error\": \"not found\"}\n"
    "   断言必须按上述真实响应结构编写（注意 /users 的数据在 data 字段里，/echo 的返回包在 echo 字段里）\n"
)


def generate_tests(description: str, name: str = "") -> Path:
    """把自然语言需求交给 DeepSeek，生成用例文件并返回路径。"""
    llm = DeepSeekLLM()
    content = llm.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"需求：{description}"},
        ],
        temperature=0.2,
        max_tokens=3000,
    )
    match = re.search(r"```python\s*(.*?)\s*```", content, re.S)
    code = match.group(1) if match else content.strip()

    if not name:
        name = datetime.now().strftime("auto_%Y%m%d_%H%M%S")
    path = settings.PROJECT_ROOT / "tests" / "generated" / f"test_{name}.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return path
