"""轻量 API 客户端封装：统一日志、超时与错误处理。"""
import logging

import requests

logger = logging.getLogger("api")


class ApiClient:
    """基于 requests.Session 的客户端，所有用例通过它发请求。"""

    def __init__(self, base_url: str, timeout: float = 10.0, headers: dict | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def request(self, method: str, path: str, **kwargs):
        """发送请求并打印日志，返回 requests.Response。

        kwargs 会原样传给 requests（如 json=、params=、headers=）。
        """
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        logger.info("-> %s %s", method.upper(), url)
        resp = self.session.request(method, url, **kwargs)
        logger.info(
            "<- %s %s (%.1fs)",
            resp.status_code,
            resp.text[:200],
            resp.elapsed.total_seconds(),
        )
        return resp

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("DELETE", path, **kwargs)
