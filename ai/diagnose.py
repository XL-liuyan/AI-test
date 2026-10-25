"""失败诊断：跑指定测试文件，把失败信息交给 DeepSeek 分析并生成报告。"""
from datetime import datetime
from pathlib import Path

from ai.deepseek import DeepSeekLLM
from ai.pytest_runner import run_pytest
from config import settings


def diagnose_file(path: Path) -> tuple[int, str, Path | None]:
    """执行目标测试文件；失败时让 DeepSeek 给出根因与修改建议。

    返回 (退出码, AI 分析文本, 报告文件路径或 None)。
    """
    if not path.is_absolute():
        path = settings.PROJECT_ROOT / path

    code_text = path.read_text(encoding="utf-8")
    exit_code, output = run_pytest(str(path))

    if exit_code == 0:
        return 0, "测试全部通过，无需诊断。", None

    llm = DeepSeekLLM()
    analysis = llm.chat(
        [
            {
                "role": "system",
                "content": (
                    "你是资深接口测试工程师。基于给出的测试代码与执行输出诊断失败原因。"
                    "输出格式：1) 失败根因 2) 可直接落地的修改建议 3) 一句话总结。用中文，简洁。"
                ),
            },
            {
                "role": "user",
                "content": f"【测试代码】\n{code_text}\n\n【执行输出（--tb=short）】\n{output}",
            },
        ]
    )

    report = settings.PROJECT_ROOT / "reports" / f"diagnosis_{datetime.now():%Y%m%d_%H%M%S}.md"
    report.write_text(
        f"# 失败诊断报告\n\n"
        f"- 测试文件：{path}\n- 退出码：{exit_code}\n- 时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
        f"## 执行输出\n```\n{output}\n```\n\n## AI 分析\n\n{analysis}\n",
        encoding="utf-8",
    )
    return exit_code, analysis, report
