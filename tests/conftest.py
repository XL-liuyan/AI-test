"""API 用例的公共 fixture。"""
import pytest

from api.client import ApiClient
from config import settings

GITHUB_BASE_URL = "https://api.github.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    return settings.BASE_URL


@pytest.fixture(scope="session")
def api_client(base_url: str) -> ApiClient:
    return ApiClient(base_url)


@pytest.fixture(scope="session")
def github_client() -> ApiClient:
    """GitHub 真实 API 演示客户端。

    网络不可达时自动跳过用例（离线/CI 环境不报红）。
    可选 GITHUB_TOKEN（.env）可把限额从 60 次/小时提升到 5000。
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "auto-test-platform-demo",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    client = ApiClient(GITHUB_BASE_URL, headers=headers)
    try:
        resp = client.get("/rate_limit", timeout=5)
        if resp.status_code not in (200, 403):
            pytest.skip(f"GitHub API 不可达（状态 {resp.status_code}）")
    except Exception:
        pytest.skip("GitHub API 不可达（网络受限）")
    return client
