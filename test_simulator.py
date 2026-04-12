"""测试交易模拟器"""

import sys
sys.path.insert(0, '/home/idiotdj/work/code/myrepo/TradingAgents')

from tradingagents.simulator import (
    TradingSimulator,
    OrderType,
    OrderSide,
    create_simulator,
)

# 创建模拟器
print("=" * 60)
print("创建交易模拟器")
print("=" * 60)
sim = create_simulator(initial_cash=100000)
print(f"初始资金: ${sim.cash:.2f}")

# 测试更新市场数据
print("\n" + "=" * 60)
print("测试市场数据更新")
print("=" * 60)

# 美股
sim.update_market_price("AAPL", 150.0)
print(f"AAPL 价格: ${sim.market_data['AAPL']['price']:.2f}")

# 港股
sim.update_market_price("00700.HK", 350.0)
print(f"00700.HK 价格: ${sim.market_data['00700.HK']['price']:.2f}")

# A股
sim.update_market_price("600519.SS", 1800.0)
print(f"600519.SS 价格: ${sim.market_data['600519.SS']['price']:.2f}")

# 加密货币
sim.update_market_price("BTC-USD", 50000.0)
print(f"BTC-USD 价格: ${sim.market_data['BTC-USD']['price']:.2f}")

# 测试买入美股
print("\n" + "=" * 60)
print("测试买入 AAPL (100股)")
print("=" * 60)
order = sim.submit_order("AAPL", OrderSide.BUY, OrderType.MARKET, 100)
print(f"订单: {order}")
print(f"现金: ${sim.cash:.2f}")
print(f"持仓: {sim.positions}")

# 测试买入港股
print("\n" + "=" * 60)
print("测试买入 00700.HK (1000股)")
print("=" * 60)
order = sim.submit_order("00700.HK", OrderSide.BUY, OrderType.MARKET, 1000)
print(f"订单: {order}")
print(f"现金: ${sim.cash:.2f}")

# 测试卖出
print("\n" + "=" * 60)
print("测试卖出 AAPL (50股)")
print("=" * 60)
sim.update_market_price("AAPL", 155.0)  # 更新价格
order = sim.submit_order("AAPL", OrderSide.SELL, OrderType.MARKET, 50)
print(f"订单: {order}")
print(f"现金: ${sim.cash:.2f}")

# 获取组合摘要
print("\n" + "=" * 60)
print("组合摘要")
print("=" * 60)
summary = sim.get_portfolio_summary()
print(f"现金: ${summary['cash']:.2f}")
print(f"持仓市值: ${summary['positions_value']:.2f}")
print(f"总市值: ${summary['total_value']:.2f}")
print(f"总盈亏: ${summary['total_pnl']:.2f} ({summary['total_pnl_pct']:.2f}%)")
print(f"持仓详情:")
for symbol, pos in summary['positions'].items():
    print(f"  {symbol}: {pos['quantity']}股, 均价${pos['avg_price']:.2f}, 当前${pos['current_price']:.2f}, 盈亏${pos['unrealized_pnl']:.2f}")

print("\n" + "=" * 60)
print("✅ 交易模拟器测试完成!")
print("=" * 60)