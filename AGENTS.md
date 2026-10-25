# 项目约定（供 Codex 等 AI 编码助手参考）

本仓库是本地 API 自动化测试平台骨架（阶段 0/1）。

- 启动本地 Mock 服务：`python mock_api.py`（127.0.0.1:8000）
- 运行测试：`.venv\Scripts\python -m pytest`（Windows）
- 用例放在 `tests/`，通过 `api_client` fixture 发请求，不要在每个用例里裸用 requests
- 请求封装在 `api/client.py`，配置统一走 `config/settings.py` 与 `.env`，不硬编码地址
- 新增/修改代码后必须跑通 `pytest` 才能交付
- 代码用中文写清晰注释，保持向后兼容
- AI 能力在 `ai/`（DeepSeek 客户端 + 用例生成/失败诊断/报告摘要/Agent 闭环），入口 `scripts/ai_tool.py`
- `ai/agent_loop.py` 是 Agent 闭环：生成或给定用例 → 执行 → 失败让 AI 重写 → 回归，入口 `scripts/ai_tool.py agent`
- Web 控制台：`web/app.py`（本地服务，默认 127.0.0.1:8002），前端在 `web/static/index.html`；修改后重启并自测 API（/api/status、/api/run-tests 等）
- GitHub 真实 API 演示：`tests/test_github_api.py`，fixture `github_client` 在 `tests/conftest.py`（网络不可达自动 skip）；改后必须跑 `pytest tests/test_github_api.py`
- 修改 `ai/` 或新增子命令后，用 `.venv\Scripts\python scripts\ai_tool.py` 自测一遍
