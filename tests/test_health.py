"""示例用例：针对本地 Mock API 的冒烟测试。

运行前先启动 Mock 服务：python mock_api.py
"""
import pytest


def test_health_ok(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_users(api_client):
    resp = api_client.get("/users")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert data[0]["id"] == 1


def test_echo_post(api_client):
    payload = {"hello": "world"}
    resp = api_client.post("/echo", json=payload)
    assert resp.status_code == 200
    assert resp.json()["echo"] == payload


def test_not_found(api_client):
    resp = api_client.get("/definitely-not-exist")
    assert resp.status_code == 404
