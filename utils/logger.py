"""统一日志配置：控制台 + logs/runtime.log。"""
import logging

from config import settings


def setup_logging(level: int = logging.INFO) -> None:
    """配置全局日志；重复调用不会叠加 handler。"""
    if logging.getLogger().handlers:
        return
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_DIR / "runtime.log", encoding="utf-8"),
    ]
    for h in handlers:
        h.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=handlers)
