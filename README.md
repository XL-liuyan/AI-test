# auto-test-platform

本地 AI 智能体自动化测试平台 —— 当前为阶段 0/1：API 自动化测试骨架。

## 目录结构

```
D:\auto-test-platform\
├── api\              # API 客户端封装（统一请求、日志、超时）
├── config\           # 配置（settings.py 读取 .env）
├── tests\            # 测试用例（conftest.py 提供公共 fixture）
├── utils\            # 通用工具（日志等）
├── mock_api.py       # 本地 Mock 服务（纯标准库，无需额外依赖）
├── pytest.ini        # pytest 配置
└── requirements.txt  # 依赖清单
```

## 快速开始

1. 创建虚拟环境并安装依赖（首次）：

   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```

2. 启动本地 Mock 服务（默认 127.0.0.1:8000）：

   ```
   python mock_api.py
   ```

3. 运行测试：

   ```
   .venv\Scripts\python -m pytest
   ```

4. 查看报告：用浏览器打开 `reports\report.html`

## 约定

- 用例统一放在 `tests/`，发请求一律通过 `api_client` fixture，不要在用例里裸用 requests
- 被测服务地址写在 `.env` 的 `BASE_URL`（示例默认指向本地 Mock）
- 新增接口：在 `mock_api.py` 加端点；新增用例：在 `tests/` 加 `test_*.py`

## 阶段 2：AI 测试助手（已接入 DeepSeek）

三条子命令（都用虚拟环境的 python 运行）：

```
# 1. 自然语言生成用例并自动执行
.venv\Scripts\python scripts\ai_tool.py generate "写3个用例：健康检查、用户列表、echo回显"

# 2. 诊断某个测试文件的失败（跑出失败后交给 DeepSeek 分析根因）
.venv\Scripts\python scripts\ai_tool.py diagnose tests\generated\test_auto_xxx.py

# 3. 运行全部测试并让 AI 写中文摘要
.venv\Scripts\python scripts\ai_tool.py summary
```

- 生成的用例落在 `tests\generated\`，诊断报告与摘要落在 `reports\`（markdown）
- 需要 `DEEPSEEK_API_KEY` 环境变量（已在你系统中配置，无需再填）
- 实现位置：`ai\` 包（deepseek 客户端 / 用例生成 / 失败诊断 / 报告摘要）

## 阶段 3：Agent 闭环（AI 自主修复）

```
# 自然语言 → 生成用例 → 执行 → 失败则 AI 重写文件 → 回归，直到通过或达到上限（默认3轮）
.venv\Scripts\python scripts\ai_tool.py agent "写3个用例：健康检查、用户列表、echo回显"

# 对现有测试文件做闭环修复
.venv\Scripts\python scripts\ai_tool.py agent tests\generated\test_xxx.py
.venv\Scripts\python scripts\ai_tool.py agent tests\generated\test_xxx.py 5   # 最多5轮
```

每轮结果与最终结论写入 `reports\agent_*.md`。

## 阶段 4：Web 控制台（本地）

```
.venv\Scripts\python web\app.py        # 启动后浏览器打开 http://127.0.0.1:8002
```

或直接双击 `scripts\start_web.bat`。

- 浏览器里点按钮即可：启动/停止 Mock、跑测试、AI 生成用例 / 诊断失败 / 测试摘要 / Agent 闭环、浏览全部报告
- 控制台是**本地服务**（不是网页托管产物），因为它要直接执行你本机的 pytest 与 DeepSeek 调用
- 前端在 `web\static\index.html`，后端 `web\app.py`（纯标准库，无新依赖）

## 真实 API 演示场景（GitHub）

`tests\test_github_api.py` 直接测 GitHub REST API（免费、无需 key）：

- 用例覆盖：rate_limit / 仓库关键字段 / 用户资料 / 404 契约
- 无 token 限 60 次/小时；`.env` 配置 `GITHUB_TOKEN` 可提升到 5000
- 网络不可达时自动跳过（离线 / CI 不报红）
- 对易变数据（star 数等）只断言结构与类型——真实接口"稳定断言"的示例写法

```
.venv\Scripts\python -m pytest tests\test_github_api.py
```

## Git 版本管理

- 仓库已在本地初始化（main 分支），代码与文档入库；`.venv`、`reports`、`logs`、`.env`、`web/mock.pid` 已忽略
- 提交署名：3045099065 / 3045099065@qq.com（想改名：`git config user.name "你的名字"`）
- 推送到远端：在 GitHub / Gitee 新建空仓库后执行

```
git remote add origin <仓库地址>
git push -u origin main
```

## 路线图

- 阶段 4 余下：定时调度（每天自动回归 + AI 摘要）+ 报告中心完善
