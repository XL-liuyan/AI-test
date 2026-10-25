def test_health_status_ok(api_client):
    """
    [用例编号] TC-001
    [用例标题] 健康检查接口返回 ok 状态
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /health 接口
    2. 校验状态码与 status 字段
    [预期结果] 状态码为 200，status 字段为 ok
    """
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_users_returns_two_records(api_client):
    """
    [用例编号] TC-002
    [用例标题] 用户列表返回两条记录（Alice/Bob）
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /users 接口
    2. 校验 data 字段存在且为列表
    3. 校验列表长度与两条记录内容
    [预期结果] 状态码为 200，data 为包含 id=1 Alice 与 id=2 Bob 的列表
    """
    response = api_client.get("/users")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 2
    assert body["data"][0]["id"] == 1
    assert body["data"][0]["name"] == "Alice"
    assert body["data"][1]["id"] == 2
    assert body["data"][1]["name"] == "Bob"


def test_echo_returns_payload(api_client):
    """
    [用例编号] TC-003
    [用例标题] echo 接口原样回显请求体
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 构造请求体 {"message": "hello", "value": 123}
    2. 调用 POST /echo 接口
    3. 校验 echo 字段与请求体一致
    [预期结果] 状态码为 200，echo 字段与请求体完全一致
    """
    payload = {"message": "hello", "value": 123}
    response = api_client.post("/echo", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "echo" in body
    assert body["echo"] == payload
