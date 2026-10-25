"""示例用例：针对本地 Mock API 的冒烟测试。

运行前先启动 Mock 服务：python mock_api.py
"""
import pytest


def test_health_ok(api_client):
    """
    [用例编号] TC-001
    [用例标题] 健康检查接口返回 ok
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /health 接口
    2. 校验状态码与 status 字段
    [预期结果] 状态码为 200，status 字段为 ok
    """
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_users(api_client):
    """
    [用例编号] TC-002
    [用例标题] 用户列表返回默认两条数据
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /users 接口
    2. 校验 data 列表长度与首条记录
    [预期结果] 状态码为 200，data 为两条记录且首条 id=1
    """
    resp = api_client.get("/users")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert data[0]["id"] == 1


def test_echo_post(api_client):
    """
    [用例编号] TC-003
    [用例标题] echo 接口原样回显请求体
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 构造请求体 {"hello": "world"}
    2. 调用 POST /echo 接口
    3. 校验 echo 字段与请求体一致
    [预期结果] 状态码为 200，echo 字段与请求体完全一致
    """
    payload = {"hello": "world"}
    resp = api_client.post("/echo", json=payload)
    assert resp.status_code == 200
    assert resp.json()["echo"] == payload


def test_not_found(api_client):
    """
    [用例编号] TC-004
    [用例标题] 未知路径返回 404
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /definitely-not-exist
    2. 校验状态码
    [预期结果] 状态码为 404
    """
    resp = api_client.get("/definitely-not-exist")
    assert resp.status_code == 404
