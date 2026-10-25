"""AI 测试助手入口。

用法（在项目根目录，用虚拟环境的 python 运行）：
    .venv\\Scripts\\python scripts\\ai_tool.py generate "写3个健康检查用例"
    .venv\\Scripts\\python scripts\\ai_tool.py diagnose tests/generated/test_auto_xxx.py
    .venv\\Scripts\\python scripts\\ai_tool.py summary
不带参数则显示帮助。
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.agent_loop import run_agent
from ai.diagnose import diagnose_file
from ai.pytest_runner import run_pytest
from ai.report_summary import summarize
from ai.use_case_gen import generate_tests


def _show_run(code: int, output: str) -> None:
    print(output)
    print(f"退出码: {code}")


def cmd_generate(description: list[str]) -> int:
    if not description:
        description = [input("请输入用例需求描述：").strip()]
    desc = description[0]
    print(f"正在让 DeepSeek 生成用例：{desc}")
    path, doc = generate_tests(desc)
    print(f"已生成: {path}")
    print(f"用例文档: {doc}")
    code, output = run_pytest(str(path))
    _show_run(code, output)
    return 0 if code == 0 else 1


def cmd_diagnose(args: list[str]) -> int:
    if not args:
        args = [input("请输入要诊断的测试文件路径：").strip()]
    target = PROJECT_ROOT / args[0]
    if not target.exists():
        print(f"文件不存在: {target}")
        return 1
    print(f"正在执行并让 DeepSeek 诊断：{target}")
    code, analysis, report = diagnose_file(target)
    print(analysis)
    if report:
        print(f"诊断报告已保存: {report}")
    return 0 if code == 0 else 1


def cmd_summary(args: list[str]) -> int:
    target = args[0] if args else ""
    print("正在运行测试并让 DeepSeek 写摘要...")
    code, summary, report = summarize(target)
    print(summary)
    print(f"摘要报告已保存: {report}")
    return 0


def cmd_agent(args: list[str]) -> int:
    """Agent 闭环：生成/修复用例直到通过或达到上限。"""
    max_attempts = 3
    if args and args[0].isdigit():
        max_attempts = int(args[0])
        args = args[1:]
    target = args[0] if args else ""

    if target and (Path(target).suffix == ".py" or (PROJECT_ROOT / target).exists()):
        print(f"Agent 闭环启动：修复现有文件 {target}（最多 {max_attempts} 轮）")
        result = run_agent(target=target, max_attempts=max_attempts)
    else:
        desc = target or input("请输入用例需求描述：").strip()
        print(f"Agent 闭环启动：生成并调优用例（最多 {max_attempts} 轮）")
        result = run_agent(task_desc=desc, max_attempts=max_attempts)

    for h in result["history"]:
        note = f" -> {h['fix_note']}" if h.get("fix_note") else ""
        print(f"  第 {h['attempt']} 轮：{'通过' if h['passed'] else '失败'}{note}")
    print("最终结果：" + ("全部通过" if result["passed"] else "未通过"))
    print(f"闭环报告：{result['report']}")
    return 0 if result["passed"] else 1


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("=== AI 测试助手 ===")
        print("用法: python scripts/ai_tool.py [agent|generate|diagnose|summary] [参数]")
        print("示例:")
        print('  agent "写3个用例：健康检查、用户列表、echo回显"（生成→执行→自动修复→回归）')
        print('  generate "写3个用例：健康检查、用户列表、echo回显"')
        print("  diagnose tests/generated/test_auto_xxx.py")
        print("  summary")
        return 0
    cmd = args[0].lower()
    if cmd == "agent":
        return cmd_agent(args[1:])
    if cmd == "generate":
        return cmd_generate(args[1:])
    if cmd == "diagnose":
        return cmd_diagnose(args[1:])
    if cmd == "summary":
        return cmd_summary(args[1:])
    print(f"未知命令: {cmd}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
