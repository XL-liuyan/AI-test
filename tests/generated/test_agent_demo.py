"""Agent 闭环演示：故意写错两个断言，等 AI 自动修复。"""


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


def test_users_wrong_shape(api_client):
    """
    [用例编号] TC-002
    [用例标题] 用户列表返回 data 字段结构
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 调用 GET /users 接口
    2. 校验 data 字段为包含 Alice/Bob 的列表
    [预期结果] 状态码为 200，data 字段精确匹配预期列表
    """
    resp = api_client.get("/users")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert body["data"] == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


def test_echo_wrong_shape(api_client):
    """
    [用例编号] TC-003
    [用例标题] echo 接口回显请求体
    [前置条件] Mock API 服务已在 http://127.0.0.1:8000 启动
    [测试步骤]
    1. 构造请求体 {"k": "v"}
    2. 调用 POST /echo 接口
    3. 校验 echo 字段与请求体一致
    [预期结果] 状态码为 200，echo 字段与请求体完全一致
    """
    payload = {"k": "v"}
    resp = api_client.post("/echo", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"echo": payload}
