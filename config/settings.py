"""统一配置入口：从项目根目录 .env 读取，带默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 读取 .env（不存在则静默跳过，使用默认值）
load_dotenv(PROJECT_ROOT / ".env")

# 被测服务地址（示例默认指向本地 Mock 服务）
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# 阶段2 起 AI 能力使用（DeepSeek 兼容 OpenAI 格式）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# GitHub API 演示场景：可选 token（不填也能用，限 60 次/小时）
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

REPORT_DIR = PROJECT_ROOT / "reports"
LOG_DIR = PROJECT_ROOT / "logs"
