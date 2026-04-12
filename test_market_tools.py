"""测试多市场工具功能"""

import sys
sys.path.insert(0, '/home/idiotdj/work/code/myrepo/TradingAgents')

from tradingagents.dataflows.market_enums import detect_market, MarketType, normalize_ticker

# 测试市场检测
print("=" * 50)
print("测试市场检测功能")
print("=" * 50)

test_cases = [
    ("AAPL", MarketType.STOCK_US, "Apple Inc."),
    ("MSFT", MarketType.STOCK_US, "Microsoft"),
    ("NVDA", MarketType.STOCK_US, "NVIDIA"),
    ("00700.HK", MarketType.STOCK_HK, "腾讯控股"),
    ("09988.HK", MarketType.STOCK_HK, "阿里巴巴"),
    ("600519.SS", MarketType.STOCK_CN_SH, "贵州茅台"),
    ("000001.SZ", MarketType.STOCK_CN_SZ, "平安银行"),
    ("300750.SZ", MarketType.STOCK_CN_SZ, "宁德时代"),
    ("688111.SS", MarketType.STOCK_CN_SH, "华大基因"),
    ("BTC-USD", MarketType.CRYPTO_BTC, "Bitcoin"),
    ("ETH-USD", MarketType.CRYPTO_BTC, "Ethereum"),
]

passed = 0
failed = 0

for ticker, expected, name in test_cases:
    result = detect_market(ticker)
    if result == expected:
        print(f"✅ {ticker} -> {result.value} ({name})")
        passed += 1
    else:
        print(f"❌ {ticker} -> {result.value} (expected {expected.value})")
        failed += 1

print()
print("=" * 50)
print(f"测试结果: {passed} passed, {failed} failed")
print("=" * 50)

# 测试符号标准化
print()
print("测试符号标准化功能")
print("=" * 50)

standardize_cases = [
    ("aapl", "AAPL"),
    ("AAPL", "AAPL"),
    ("600519", "600519.SS"),
    ("000001", "000001.SZ"),
    ("700", "00700.HK"),
    ("btc-usd", "BTC-USD"),
]

for ticker, expected in standardize_cases:
    result = normalize_ticker(ticker)
    if result == expected:
        print(f"✅ {ticker} -> {result}")
    else:
        print(f"❌ {ticker} -> {result} (expected {expected})")

print()
print("✅ 测试完成!")