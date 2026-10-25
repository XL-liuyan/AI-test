"""根级 conftest：保证项目根目录进入 sys.path，并初始化统一日志。"""
import pytest

from utils.logger import setup_logging


@pytest.fixture(scope="session", autouse=True)
def _init_logging():
    """会话开始时初始化一次日志（控制台 + logs/runtime.log）。"""
    setup_logging()
