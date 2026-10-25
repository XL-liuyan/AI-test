"""运行测试并让 DeepSeek 写中文摘要报告。"""
from datetime import datetime
from pathlib import Path

from ai.deepseek import DeepSeekLLM
from ai.pytest_runner import run_pytest
from config import settings


def summarize(target: str = "") -> tuple[int, str, Path]:
    """运行 pytest（可指定目标），把输出交给 DeepSeek 写摘要。

    返回 (退出码, AI 摘要文本, 报告文件路径)。
    """
    args = [target] if target else []
    exit_code, output = run_pytest(*args)

    llm = DeepSeekLLM()
    summary = llm.chat(
        [
            {
                "role": "system",
                "content": (
                    "你是测试报告分析员。基于 pytest 执行输出写一份中文摘要，包含："
                    "测试总览（通过/失败数量）、重点结论、值得关注的风险点。用列表，简洁。"
                ),
            },
            {
                "role": "user",
                "content": f"pytest 执行输出（退出码 {exit_code}）：\n{output}",
            },
        ]
    )

    report = settings.PROJECT_ROOT / "reports" / f"summary_{datetime.now():%Y%m%d_%H%M%S}.md"
    report.write_text(
        f"# 测试摘要报告\n\n"
        f"- 执行时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n- 退出码：{exit_code}\n"
        f"- 目标：{target or '全部测试'}\n\n"
        f"## 原始输出\n```\n{output}\n```\n\n## AI 摘要\n\n{summary}\n",
        encoding="utf-8",
    )
    return exit_code, summary, report
