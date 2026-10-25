"""Agent 闭环演示：故意写错两个断言，等 AI 自动修复。"""
def test_health_ok(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_users_wrong_shape(api_client):
    resp = api_client.get("/users")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert body["data"] == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


def test_echo_wrong_shape(api_client):
    payload = {"k": "v"}
    resp = api_client.post("/echo", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"echo": payload}