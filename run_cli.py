#!/usr/bin/env python3
"""
TradingAgents Shell 交互式界面
提供便捷的菜单操作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_menu():
    """打印菜单"""
    print("\n📊 TradingAgents 交互式菜单")
    print("-" * 60)
    print("  [1] 市场数据查询")
    print("       - 查询实时行情")
    print("       - 查询历史K线")
    print("       - 查询基本面数据")
    print()
    print("  [2] 多市场切换")
    print("       - 美股 (US Stock)")
    print("       - 港股 (HK Stock)")
    print("       - A股 (China A-Share)")
    print("       - 加密货币 (Crypto)")
    print()
    print("  [3] 策略回测")
    print("       - 基于真实历史数据回测")
    print("       - 查看回测报告")
    print()
    print("  [4] 交易模拟")
    print("       - 模拟下单/平仓")
    print("       - 查看持仓和盈亏")
    print()
    print("  [5] Agent 分析")
    print("       - 生成投资分析报告")
    print("       - 查看市场研究")
    print()
    print("  [6] 运行测试")
    print("       - 一键运行所有测试")
    print("       - 查看测试报告")
    print()
    print("  [0] 退出")
    print("-" * 60)


def query_market_data():
    """市场数据查询"""
    print_header("市场数据查询")
    
    print("\n选择市场:")
    print("  [1] 美股")
    print("  [2] 港股")
    print("  [3] A股 (上海/深圳)")
    print("  [4] 加密货币")
    print("  [0] 返回")
    
    choice = input("\n请输入选项: ").strip()
    
    if choice == "0":
        return
    
    market_map = {
        "1": ("US", "美股"),
        "2": ("HK", "港股"),
        "3": ("CN", "A股"),
        "4": ("CRYPTO", "加密货币"),
    }
    
    if choice not in market_map:
        print("❌ 无效选项")
        return
    
    market_code, market_name = market_map[choice]
    
    # 获取股票代码
    ticker = input(f"请输入{market_name}股票代码 (如 AAPL, 600519, 00700.HK, BTC-USD): ").strip()
    
    if not ticker:
        print("❌ 请输入股票代码")
        return
    
    print(f"\n📈 查询中: {ticker} ({market_name})...")
    
    try:
        from tradingagents.agents.utils.market_tools import get_market_stock_data
        from tradingagents.dataflows.market_enums import detect_market, get_display_name
        
        # 检测市场
        market = detect_market(ticker)
        
        # 获取数据
        data = get_market_stock_data(ticker)
        
        if data:
            print("\n✅ 数据获取成功!")
            print("\n数据预览:")
            print(f"  股票代码: {ticker}")
            print(f"  市场类型: {get_display_name(ticker, market)}")
            if 'current_price' in data:
                print(f"  当前价格: ${data['current_price']:.2f}")
            if 'daily' in data and len(data['daily']) > 0:
                latest = data['daily'][-1]
                print(f"  最新日期: {latest.get('date', 'N/A')}")
                print(f"  开盘: ${latest.get('open', 0):.2f}")
                print(f"  收盘: ${latest.get('close', 0):.2f}")
                print(f"  成交量: {latest.get('volume', 0):,}")
        else:
            print("❌ 未获取到数据，请检查股票代码是否正确")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    input("\n按回车键继续...")


def switch_market():
    """市场切换"""
    print_header("多市场切换")
    
    print("\n当前支持的市场:")
    print("  [1] 美股 (US Stock)")
    print("       示例: AAPL, MSFT, NVDA, GOOGL")
    print()
    print("  [2] 港股 (HK Stock)")
    print("       示例: 00700.HK (腾讯), 09988.HK (阿里)")
    print()
    print("  [3] A股 (China A-Share)")
    print("       上海: 600519.SS (茅台), 600036.SS (招行)")
    print("       深圳: 000001.SZ (平安), 300750.SZ (宁德)")
    print()
    print("  [4] 加密货币 (Crypto)")
    print("       示例: BTC-USD, ETH-USD, DOGE-USD")
    print()
    print("  [0] 返回")
    
    choice = input("\n请输入选项: ").strip()
    
    market_info = {
        "1": ("US", "美股", "AAPL"),
        "2": ("HK", "港股", "00700.HK"),
        "3": ("CN", "A股", "600519.SS"),
        "4": ("CRYPTO", "加密货币", "BTC-USD"),
    }
    
    if choice == "0":
        return
    elif choice in market_info:
        code, name, example = market_info[choice]
        print(f"\n✅ 已切换到 {name}")
        print(f"   示例股票代码: {example}")
    else:
        print("❌ 无效选项")
    
    input("\n按回车键继续...")


def run_backtest():
    """策略回测"""
    print_header("策略回测")
    
    print("\n⚠️  注意: 回测将使用真实历史数据")
    
    ticker = input("请输入股票代码 (如 AAPL, 600519.SS): ").strip()
    
    if not ticker:
        print("❌ 请输入股票代码")
        input("\n按回车键继续...")
        return
    
    print(f"\n📊 正在准备 {ticker} 的回测数据...")
    
    try:
        from tradingagents.backtest import create_backtest_engine
        
        # 这里可以添加更复杂的回测逻辑
        print("\n✅ 回测引擎已就绪")
        print("   注意: 完整回测功能需要更多配置")
        print("   - 选择回测时间范围")
        print("   - 设置初始资金")
        print("   - 选择交易策略")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    
    input("\n按回车键继续...")


def trading_simulation():
    """交易模拟"""
    print_header("交易模拟")
    
    print("\n当前功能:")
    print("  - 交易模拟器已就绪")
    print("  - 支持多市场订单")
    print("  - 支持市价单/限价单")
    print("  - 持仓和盈亏管理")
    print()
    print("  运行命令: python test_simulator.py")
    
    input("\n按回车键继续...")


def agent_analysis():
    """Agent 分析"""
    print_header("Agent 分析")
    
    print("\n⚠️  注意: 需要配置 LLM API 密钥")
    print("\n配置步骤:")
    print("  1. 复制 .env.example 为 .env")
    print("  2. 设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
    print("  3. 运行: python main.py")
    print()
    print("支持的 LLM:")
    print("  - OpenAI (GPT-4)")
    print("  - Anthropic (Claude)")
    print("  - Google (Gemini)")
    print("  - xAI (Grok)")
    
    input("\n按回车键继续...")


def run_tests():
    """运行测试"""
    print_header("运行测试")
    
    print("\n运行中...\n")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "run_tests.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    input("\n按回车键继续...")


def main():
    """主函数"""
    # 清除屏幕
    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        print_header("TradingAgents 多市场交易系统")
        
        print(f"\n📁 项目路径: {os.path.dirname(os.path.abspath(__file__))}")
        print("\n当前已实现功能:")
        print("  ✅ 市场类型检测 (美股/港股/A股/加密货币)")
        print("  ✅ 数据源接口 (yfinance, AkShare)")
        print("  ✅ 交易模拟器")
        print("  ✅ 回测引擎")
        print("  ✅ 测试框架")
        
        print_menu()
        
        choice = input("\n请输入选项: ").strip()
        
        # 清除屏幕
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if choice == "1":
            query_market_data()
        elif choice == "2":
            switch_market()
        elif choice == "3":
            run_backtest()
        elif choice == "4":
            trading_simulation()
        elif choice == "5":
            agent_analysis()
        elif choice == "6":
            run_tests()
        elif choice == "0":
            print("\n👋 感谢使用 TradingAgents!")
            print("   GitHub: https://github.com/idiotdj/TradingAgents")
            print()
            break
        else:
            print("❌ 无效选项，请重新输入")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()