"""真实 API 演示场景：GitHub REST API。

免费、无需 key（无 token 限 60 次/小时，.env 配 GITHUB_TOKEN 可到 5000）。
对易变数据（star 数等）只断言结构与类型，不做死值断言——这是对真实接口
"稳定断言"的示例：真实服务数据会变，断言要面向契约而非当前值。
"""
import pytest


def test_rate_limit(github_client):
    """速率限制接口：永远可查，验证 API 可达与返回结构。"""
    resp = github_client.get("/rate_limit")
    assert resp.status_code == 200
    body = resp.json()
    assert "resources" in body
    assert "core" in body["resources"]


def test_repo_basic_fields(github_client):
    """固定仓库 octocat/Hello-World：验证关键字段与类型。"""
    resp = github_client.get("/repos/octocat/Hello-World")
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "octocat/Hello-World"
    assert isinstance(body["stargazers_count"], int)
    assert body["owner"]["login"] == "octocat"


def test_user_profile(github_client):
    """固定用户 octocat：验证登录名与字段存在性。"""
    resp = github_client.get("/users/octocat")
    assert resp.status_code == 200
    body = resp.json()
    assert body["login"] == "octocat"
    assert "public_repos" in body
    assert isinstance(body["public_repos"], int)


def test_not_found_repo(github_client):
    """不存在的仓库：验证 404 契约。"""
    resp = github_client.get("/repos/auto-test-platform/no-such-repo")
    assert resp.status_code == 404
    assert resp.json()["message"] == "Not Found"
