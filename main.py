import sys
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import date

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get stock code and date from command line arguments
# Usage: python main.py <stock_code> [date]
# Example: python main.py AAPL 2026-04-12
if len(sys.argv) < 2:
    print("❌ 请提供股票代码!")
    print("用法: python main.py <股票代码> [日期]")
    print("示例: python main.py AAPL 2026-04-12")
    print("      python main.py PDD")
    sys.exit(1)

stock_code = sys.argv[1].upper()
trade_date = sys.argv[2] if len(sys.argv) > 2 else str(date.today())

print(f"📊 分析股票: {stock_code} | 日期: {trade_date}")

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "MiniMax-M2.5"  # MiniMax model
config["quick_think_llm"] = "MiniMax-M2.5"  # MiniMax model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance, no extra API keys needed)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: alpha_vantage, yfinance
    "technical_indicators": "yfinance",      # Options: alpha_vantage, yfinance
    "fundamental_data": "yfinance",          # Options: alpha_vantage, yfinance
    "news_data": "yfinance",                 # Options: alpha_vantage, yfinance,
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate(stock_code, trade_date)
print(decision)

# Generate markdown report automatically
ta.generate_markdown_report(trade_date)

print(f"\n✅ 分析完成! 报告位置: results/{stock_code}/analysis_report.md")

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
