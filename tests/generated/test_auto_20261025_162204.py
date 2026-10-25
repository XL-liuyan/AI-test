import pytest


def test_health_check(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_users_data(api_client):
    response = api_client.get("/users")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 2
    assert body["data"][0] == {"id": 1, "name": "Alice"}
    assert body["data"][1] == {"id": 2, "name": "Bob"}


def test_post_echo_returns_original_body(api_client):
    payload = {"username": "alice", "password": "secret123"}
    response = api_client.post("/echo", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "echo" in body
    assert body["echo"] == payload