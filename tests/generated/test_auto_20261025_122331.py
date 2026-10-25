def test_health_status_ok(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_users_returns_two_records(api_client):
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
    payload = {"message": "hello", "value": 123}
    response = api_client.post("/echo", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "echo" in body
    assert body["echo"] == payload