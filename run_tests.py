#!/usr/bin/env python3
"""
TradingAgents 一键测试脚本
运行所有测试并生成报告
"""

import sys
import subprocess
import os
from pathlib import Path


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def run_tests(test_path: str, description: str) -> bool:
    """运行单个测试并返回结果"""
    print(f"\n📋 {description}")
    print(f"   路径: {test_path}")
    
    # 检查是否为 pytest 测试文件
    test_file = Path(test_path)
    if test_file.exists():
        # 尝试作为 pytest 运行
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            cwd=Path(__file__).parent,
            capture_output=True,
        )
        
        # 如果没有收集到测试，尝试直接运行脚本
        if "no tests ran" in result.stdout.decode() or "no tests ran" in result.stderr.decode():
            print("   (非 pytest 格式，尝试直接运行)")
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=Path(__file__).parent,
            )
        
        return result.returncode == 0
    else:
        print(f"   ⚠️ 文件不存在: {test_path}")
        return False


def main():
    """主函数"""
    print_header("TradingAgents 一键测试")
    print("项目根目录:", Path(__file__).parent)
    
    all_passed = True
    results = []
    
    # 测试 1: 市场类型枚举测试
    print_header("测试 1: 市场类型枚举")
    passed = run_tests("tests/test_market_enums.py", "市场类型检测")
    results.append(("市场类型检测", passed))
    if not passed:
        all_passed = False
    
    # 测试 2: 模拟交易测试
    print_header("测试 2: 交易模拟器")
    passed = run_tests("test_simulator.py", "交易模拟器")
    results.append(("交易模拟器", passed))
    if not passed:
        all_passed = False
    
    # 测试 3: 回测引擎测试
    print_header("测试 3: 回测引擎")
    passed = run_tests("test_backtest.py", "回测引擎")
    results.append(("回测引擎", passed))
    if not passed:
        all_passed = False
    
    # 测试 4: 多市场工具测试
    print_header("测试 4: 多市场工具")
    passed = run_tests("test_market_tools.py", "多市场工具")
    results.append(("多市场工具", passed))
    if not passed:
        all_passed = False
    
    # 输出总结
    print_header("测试结果总结")
    print("\n")
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status}  {name}")
    
    print("\n" + "-" * 60)
    
    if all_passed:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n💥 部分测试失败，请检查上述输出")
        return 1


if __name__ == "__main__":
    sys.exit(main())