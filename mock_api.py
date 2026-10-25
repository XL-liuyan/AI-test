"""本地 Mock API 服务（纯标准库，无额外依赖）。

用法:
    python mock_api.py        # 默认监听 127.0.0.1:8000

端点:
    GET  /health    -> {"status": "ok"}
    GET  /users     -> {"data": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    POST /echo      -> {"echo": <请求体>}
    其他            -> 404 {"error": "not found"}
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8000

USERS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        elif self.path == "/users":
            self._send(200, {"data": USERS})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8") if raw else "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(400, {"error": "invalid json"})
            return
        if self.path == "/echo":
            self._send(200, {"echo": payload})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        # 关闭默认访问日志噪音；如需调试可注释掉本方法
        pass


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Mock API running at http://{HOST}:{PORT}")
    server.serve_forever()
