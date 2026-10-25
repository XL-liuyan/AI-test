"""Web 控制台：在浏览器里跑测试、看报告、调 AI 助手。

启动（项目根目录）：
    .venv\\Scripts\\python web\\app.py
访问 http://127.0.0.1:8002

说明：本服务直接调用本机的 pytest 与 DeepSeek（ai/ 包），
属于平台的本地组件，不依赖任何网页托管平台。
"""
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"
REPORTS_DIR = PROJECT_ROOT / "reports"
HOST, PORT = "127.0.0.1", 8002
MOCK_PID_FILE = WEB_DIR / "mock.pid"

# 让项目内的包可直接 import（ai / config / api / utils）
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.agent_loop import run_agent
from ai.diagnose import diagnose_file
from ai.report_summary import summarize
from ai.use_case_gen import generate_tests
from config import settings

_lock = threading.Lock()


# ---------- 进程工具 ----------

def _run_cmd(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    """在项目根目录执行命令，返回 (退出码, 合并输出)。"""
    proc = subprocess.run(
        cmd, cwd=PROJECT_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _pid_alive(pid: int) -> bool:
    if os.name == "nt":
        code, out = _run_cmd(["tasklist", "/FI", f"PID eq {pid}", "/NH"])
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _mock_running() -> bool:
    if not MOCK_PID_FILE.exists():
        return False
    try:
        pid = int(MOCK_PID_FILE.read_text().strip())
    except ValueError:
        return False
    return _pid_alive(pid)


def _mock_start() -> bool:
    if _mock_running():
        return True
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.Popen(
        [sys.executable, "mock_api.py"], cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags,
    )
    MOCK_PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    return True


def _mock_stop() -> None:
    if not MOCK_PID_FILE.exists():
        return
    pid = int(MOCK_PID_FILE.read_text().strip())
    if _pid_alive(pid):
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    MOCK_PID_FILE.unlink(missing_ok=True)


# ---------- 业务动作 ----------

def _run_tests(target: str = "") -> dict:
    args = [target] if target else []
    code, out = _run_cmd([sys.executable, "-m", "pytest", "--tb=short", *args])
    return {
        "exit_code": code,
        "output": out,
        "report": "/reports/report.html" if (REPORTS_DIR / "report.html").exists() else None,
    }


def _generate(description: str) -> dict:
    path, doc = generate_tests(description)
    code, out = _run_cmd([sys.executable, "-m", "pytest", "--tb=short", str(path)])
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "testcase_doc": str(doc.relative_to(PROJECT_ROOT)),
        "exit_code": code,
        "output": out,
    }


def _diagnose(target: str) -> dict:
    p = Path(target)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    code, analysis, report = diagnose_file(p)
    return {
        "exit_code": code,
        "analysis": analysis,
        "report": str(report.relative_to(PROJECT_ROOT)) if report else None,
    }


def _agent(target: str = "", description: str = "") -> dict:
    kwargs = {"max_attempts": 3}
    if target:
        kwargs["target"] = target
    else:
        kwargs["task_desc"] = description
    result = run_agent(**kwargs)
    return {
        "passed": result["passed"],
        "history": [
            {"attempt": h["attempt"], "passed": h["passed"], "fix_note": h.get("fix_note")}
            for h in result["history"]
        ],
        "report": str(result["report"].relative_to(PROJECT_ROOT)),
    }


def _summary(target: str = "") -> dict:
    code, summary_text, report = summarize(target)
    return {
        "exit_code": code,
        "summary": summary_text,
        "report": str(report.relative_to(PROJECT_ROOT)),
    }


def _list_reports() -> list[dict]:
    items = []
    if REPORTS_DIR.exists():
        for f in sorted(REPORTS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                st = f.stat()
                items.append({
                    "name": f.name,
                    "size": st.st_size,
                    "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "kind": "html" if f.suffix == ".html" else "md",
                    "url": f"/reports/{urllib.parse.quote(f.name)}",
                })
    return items


def _extract_case_titles(code: str) -> list[dict]:
    """从测试文件提取用例编号与标题（用于用例库展示）。

    优先取 docstring 的 [用例编号]/[用例标题]；没有则退回函数名。
    """
    items = []
    for m in re.finditer(r"def\s+(test_\w+)\s*\([^)]*\):\s*(?:\"\"\"(.*?)\"\"\")?", code, re.S):
        fname, doc = m.group(1), (m.group(2) or "")
        no = re.search(r"\[用例编号\]\s*(\S+)", doc)
        title = re.search(r"\[用例标题\]\s*(.+)", doc)
        items.append({
            "no": no.group(1).strip() if no else "-",
            "title": title.group(1).strip() if title else fname,
        })
    return items


def _list_test_files() -> list[dict]:
    """列出 tests/ 下所有测试文件（含 AI 生成的 tests/generated/），带用例标题。"""
    items = []
    tests_dir = PROJECT_ROOT / "tests"
    if tests_dir.exists():
        for f in sorted(tests_dir.rglob("*.py")):
            if "__pycache__" in f.parts:
                continue
            st = f.stat()
            try:
                cases = _extract_case_titles(f.read_text(encoding="utf-8"))
            except Exception:
                cases = []
            items.append({
                "path": str(f.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "size": st.st_size,
                "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "cases": cases,
                "case_count": len(cases),
            })
    return items


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    server_version = "AutoTestConsole/1.0"

    def log_message(self, fmt, *args):
        pass  # 静默访问日志

    def _send_bytes(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send_bytes(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                         "application/json; charset=utf-8")

    def _text(self, code: int, text: str, ctype: str = "text/plain; charset=utf-8") -> None:
        self._send_bytes(code, text.encode("utf-8"), ctype)

    # ---- GET ----

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        p = parsed.path

        if p in ("/", "/index.html"):
            idx = STATIC_DIR / "index.html"
            if idx.exists():
                self._send_bytes(200, idx.read_bytes(), "text/html; charset=utf-8")
            else:
                self._text(500, "缺少 web/static/index.html")
        elif p.startswith("/static/"):
            name = urllib.parse.unquote(p[len("/static/"):])
            target = (STATIC_DIR / name).resolve()
            if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.is_file():
                self._text(404, "not found")
                return
            ctype = "text/html; charset=utf-8" if target.suffix == ".html" else \
                    "text/css; charset=utf-8" if target.suffix == ".css" else \
                    "application/javascript; charset=utf-8" if target.suffix == ".js" else \
                    "application/octet-stream"
            self._send_bytes(200, target.read_bytes(), ctype)
        elif p == "/api/status":
            self._json(200, {
                "mock_running": _mock_running(),
                "base_url": settings.BASE_URL,
                "deepseek_configured": bool(settings.DEEPSEEK_API_KEY),
            })
        elif p == "/api/reports":
            self._json(200, {"items": _list_reports()})
        elif p == "/api/tests":
            self._json(200, {"items": _list_test_files()})
        elif p.startswith("/reports/"):
            name = urllib.parse.unquote(p[len("/reports/"):])
            target = (REPORTS_DIR / name).resolve()
            if not str(target).startswith(str(REPORTS_DIR.resolve())) or not target.is_file():
                self._text(404, "not found")
                return
            if target.suffix == ".html":
                # 报告在控制台内嵌预览时放大（zoom 1.3，Chromium 内核支持）
                raw = target.read_bytes()
                injected = (
                    b'<style>body{zoom:1.3}@media(max-width:900px){body{zoom:1.15}}</style>'
                )
                if b"<head>" in raw:
                    raw = raw.replace(b"<head>", b"<head>" + injected, 1)
                self._send_bytes(200, raw, "text/html; charset=utf-8")
            else:
                self._send_bytes(200, target.read_bytes(), "text/markdown; charset=utf-8")
        elif p.startswith("/tests/"):
            rel = urllib.parse.unquote(p[len("/tests/"):])
            target = (PROJECT_ROOT / rel).resolve()
            tests_dir = (PROJECT_ROOT / "tests").resolve()
            if not str(target).startswith(str(tests_dir)) or not target.is_file():
                self._text(404, "not found")
                return
            self._send_bytes(200, target.read_bytes(), "text/plain; charset=utf-8")
        else:
            self._text(404, "not found")

    # ---- POST ----

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            data = {}

        if self.path == "/api/mock/start":
            with _lock:
                _mock_start()
            self._json(200, {"mock_running": _mock_running()})
        elif self.path == "/api/mock/stop":
            with _lock:
                _mock_stop()
            self._json(200, {"mock_running": _mock_running()})
        elif self.path == "/api/run-tests":
            try:
                self._json(200, _run_tests((data.get("target") or "").strip()))
            except Exception as e:
                self._json(500, {"error": str(e)})
        elif self.path == "/api/generate":
            desc = (data.get("description") or "").strip()
            if not desc:
                self._json(400, {"error": "description 不能为空"})
                return
            try:
                self._json(200, _generate(desc))
            except Exception as e:
                self._json(500, {"error": str(e)})
        elif self.path == "/api/diagnose":
            target = (data.get("target") or "").strip()
            if not target:
                self._json(400, {"error": "target 不能为空"})
                return
            try:
                self._json(200, _diagnose(target))
            except Exception as e:
                self._json(500, {"error": str(e)})
        elif self.path == "/api/agent":
            target = (data.get("target") or "").strip()
            desc = (data.get("description") or "").strip()
            if not target and not desc:
                self._json(400, {"error": "需要提供用例描述或目标测试文件"})
                return
            try:
                self._json(200, _agent(target, desc))
            except Exception as e:
                self._json(500, {"error": str(e)})
        elif self.path == "/api/summary":
            try:
                self._json(200, _summary((data.get("target") or "").strip()))
            except Exception as e:
                self._json(500, {"error": str(e)})
        else:
            self._text(404, "not found")


if __name__ == "__main__":
    print(f"Web console running at http://{HOST}:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
