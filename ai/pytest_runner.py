"""运行 pytest 并捕获输出的小工具。"""
import subprocess
import sys

from config import settings


def run_pytest(*args: str, timeout: int = 300) -> tuple[int, str]:
    """在项目根目录运行 pytest，返回 (退出码, 合并输出文本)。

    使用当前解释器（venv 的 python），自动附加 --tb=short 精简回溯。
    """
    cmd = [sys.executable, "-m", "pytest", "--tb=short", *args]
    proc = subprocess.run(
        cmd,
        cwd=settings.PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
