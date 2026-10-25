"""真实 API 演示场景：GitHub REST API。

免费、无需 key（无 token 限 60 次/小时，.env 配 GITHUB_TOKEN 可到 5000）。
对易变数据（star 数等）只断言结构与类型，不做死值断言——这是对真实接口
"稳定断言"的示例：真实服务数据会变，断言要面向契约而非当前值。
"""
import pytest


def test_rate_limit(github_client):
    """
    [用例编号] TC-001
    [用例标题] 速率限制接口可达且返回结构正确
    [前置条件] 外网可访问 api.github.com（网络不可达时用例自动跳过）
    [测试步骤]
    1. 调用 GET /rate_limit
    2. 校验状态码与 resources/core 结构
    [预期结果] 状态码为 200，resources 与 core 字段存在
    """
    resp = github_client.get("/rate_limit")
    assert resp.status_code == 200
    body = resp.json()
    assert "resources" in body
    assert "core" in body["resources"]


def test_repo_basic_fields(github_client):
    """
    [用例编号] TC-002
    [用例标题] 固定仓库返回关键字段与类型
    [前置条件] 外网可访问 api.github.com（网络不可达时用例自动跳过）
    [测试步骤]
    1. 调用 GET /repos/octocat/Hello-World
    2. 校验 full_name、star 数类型、owner.login
    [预期结果] 状态码为 200，full_name 精确匹配，字段类型正确
    """
    resp = github_client.get("/repos/octocat/Hello-World")
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "octocat/Hello-World"
    assert isinstance(body["stargazers_count"], int)
    assert body["owner"]["login"] == "octocat"


def test_user_profile(github_client):
    """
    [用例编号] TC-003
    [用例标题] 固定用户资料返回登录名与字段存在性
    [前置条件] 外网可访问 api.github.com（网络不可达时用例自动跳过）
    [测试步骤]
    1. 调用 GET /users/octocat
    2. 校验 login、public_repos 字段
    [预期结果] 状态码为 200，login 为 octocat，字段存在且类型正确
    """
    resp = github_client.get("/users/octocat")
    assert resp.status_code == 200
    body = resp.json()
    assert body["login"] == "octocat"
    assert "public_repos" in body
    assert isinstance(body["public_repos"], int)


def test_not_found_repo(github_client):
    """
    [用例编号] TC-004
    [用例标题] 不存在的仓库返回 404 契约
    [前置条件] 外网可访问 api.github.com（网络不可达时用例自动跳过）
    [测试步骤]
    1. 调用 GET /repos/auto-test-platform/no-such-repo
    2. 校验状态码与错误消息
    [预期结果] 状态码为 404，message 为 Not Found
    """
    resp = github_client.get("/repos/auto-test-platform/no-such-repo")
    assert resp.status_code == 404
    assert resp.json()["message"] == "Not Found"
