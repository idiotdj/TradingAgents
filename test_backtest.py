"""测试回测引擎"""

import sys
sys.path.insert(0, '/home/idiotdj/work/code/myrepo/TradingAgents')

from tradingagents.backtest import create_backtest_engine, BacktestResult
from datetime import datetime, timedelta

# 准备测试数据 - 模拟30天数据
def generate_test_data(start_price: float, days: int = 30, volatility: float = 0.02):
    """生成测试数据"""
    data = []
    price = start_price
    base_date = datetime(2024, 1, 1)
    
    for i in range(days):
        import random
        change = random.gauss(0, volatility)
        price = price * (1 + change)
        
        data.append({
            "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "open": price * 0.99,
            "high": price * 1.02,
            "low": price * 0.98,
            "close": price,
            "volume": 1000000,
        })
    
    return data


# 简单的均线策略
def ma_strategy(simulator, date, market_data):
    """简单均线策略示例"""
    orders = []
    
    for symbol, data in market_data.items():
        close = data.get("close", 0)
        
        # 简单的买入信号: 价格低于 100 时买入
        if close < 100 and symbol not in simulator.positions:
            # 买入 10 股
            orders.append({
                "symbol": symbol,
                "side": "buy",
                "type": "market",
                "quantity": 10,
            })
        
        # 简单的卖出信号: 价格高于 110 时卖出
        elif close > 110 and symbol in simulator.positions:
            # 卖出全部
            pos = simulator.positions[symbol]
            orders.append({
                "symbol": symbol,
                "side": "sell",
                "type": "market",
                "quantity": pos.quantity,
            })
    
    return orders


# 创建回测引擎
print("=" * 60)
print("创建回测引擎")
print("=" * 60)
engine = create_backtest_engine(initial_cash=100000)
print(f"初始资金: ${engine.initial_cash:.2f}")

# 准备数据
print("\n" + "=" * 60)
print("准备测试数据")
print("=" * 60)

data = {
    "AAPL": generate_test_data(150, 30),
    "MSFT": generate_test_data(300, 30),
}

print(f"AAPL 数据: {len(data['AAPL'])} 条")
print(f"MSFT 数据: {len(data['MSFT'])} 条")
print(f"第一条: {data['AAPL'][0]}")
print(f"最后一条: {data['AAPL'][-1]}")

# 运行回测
print("\n" + "=" * 60)
print("运行回测")
print("=" * 60)

result = engine.run(data, ma_strategy)

# 输出结果
print("\n" + "=" * 60)
print("回测结果")
print("=" * 60)

print(f"回测期间: {result.start_date.strftime('%Y-%m-%d')} 至 {result.end_date.strftime('%Y-%m-%d')}")
print(f"初始资金: ${result.initial_cash:.2f}")
print(f"最终资金: ${result.final_cash:.2f}")
print()
print("收益率指标:")
print(f"  总收益率: {result.total_return * 100:.2f}%")
print(f"  年化收益率: {result.annual_return * 100:.2f}%")
print()
print("风险指标:")
print(f"  最大回撤: {result.max_drawdown * 100:.2f}%")
print(f"  波动率: {result.volatility * 100:.2f}%")
print(f"  夏普比率: {result.sharpe_ratio:.2f}")
print()
print("交易统计:")
print(f"  总交易次数: {result.total_trades}")
print(f"  盈利交易: {result.winning_trades}")
print(f"  亏损交易: {result.losing_trades}")
print(f"  胜率: {result.win_rate * 100:.2f}%")
print(f"  平均盈利: ${result.avg_win:.2f}")
print(f"  平均亏损: ${result.avg_loss:.2f}")
print(f"  盈利因子: {result.profit_factor:.2f}")

# 输出每日记录
print("\n" + "=" * 60)
print("每日记录 (前5天)")
print("=" * 60)
for record in result.daily_records[:5]:
    print(f"{record.date.strftime('%Y-%m-%d')}: ${record.portfolio_value:.2f}, 日收益: {record.daily_return*100:.2f}%")

print("\n" + "=" * 60)
print("✅ 回测引擎测试完成!")
print("=" * 60)