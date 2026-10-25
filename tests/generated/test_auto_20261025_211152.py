import pytest


def test_health_check(api_client):
    """
    [用例编号] TC-001
    [用例标题] 健康检查接口返回 ok 状态
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /health 接口
    2. 检查响应状态码与响应体
    [预期结果] 状态码为 200，响应体为 {"status": "ok"}
    """
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_users_list(api_client):
    """
    [用例编号] TC-002
    [用例标题] 用户列表接口返回包含 Alice 和 Bob 的数据
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /users 接口
    2. 检查响应状态码
    3. 校验 data 字段内容与用户信息
    [预期结果] 状态码为 200，data 字段为包含 id=1 name=Alice 与 id=2 name=Bob 的列表
    """
    response = api_client.get("/users")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert body["data"] == [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]


def test_echo_returns_request_body(api_client):
    """
    [用例编号] TC-003
    [用例标题] echo 接口原样回显请求体
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 构造请求体 {"message": "hello", "value": 123}
    2. 调用 POST /echo 接口并传入请求体
    3. 检查响应状态码与 echo 字段内容
    [预期结果] 状态码为 200，echo 字段内容与请求体完全一致
    """
    payload = {"message": "hello", "value": 123}
    response = api_client.post("/echo", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "echo" in body
    assert body["echo"] == payload