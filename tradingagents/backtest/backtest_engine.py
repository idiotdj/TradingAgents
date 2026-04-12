"""回测引擎模块

多市场策略回测系统
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging

from tradingagents.simulator import TradingSimulator, OrderSide, OrderType
from tradingagents.dataflows.market_enums import detect_market, MarketType

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """交易记录"""
    timestamp: datetime
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    price: float
    commission: float
    pnl: float = 0.0  # 已实现盈亏


@dataclass
class DailyRecord:
    """每日记录"""
    date: datetime
    portfolio_value: float
    cash: float
    positions_value: float
    daily_return: float = 0.0
    cumulative_return: float = 0.0


@dataclass
class BacktestResult:
    """回测结果"""
    # 基本信息
    start_date: datetime
    end_date: datetime
    initial_cash: float
    final_cash: float
    
    # 收益率指标
    total_return: float = 0.0
    annual_return: float = 0.0
    
    # 风险指标
    max_drawdown: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    
    # 交易指标
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    # 每日记录
    daily_records: List[DailyRecord] = field(default_factory=list)
    
    # 交易记录
    trades: List[TradeRecord] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "initial_cash": self.initial_cash,
            "final_cash": self.final_cash,
            "total_return": f"{self.total_return * 100:.2f}%",
            "annual_return": f"{self.annual_return * 100:.2f}%",
            "max_drawdown": f"{self.max_drawdown * 100:.2f}%",
            "volatility": f"{self.volatility * 100:.2f}%",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": f"{self.win_rate * 100:.2f}%",
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": f"{self.profit_factor:.2f}",
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.001,
    ):
        """初始化回测引擎
        
        Args:
            initial_cash: 初始资金
            commission_rate: 手续费率
        """
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.simulator = TradingSimulator(
            initial_cash=initial_cash,
            commission_rate=commission_rate,
        )
        
        # 回测数据
        self.daily_records: List[DailyRecord] = []
        self.trades: List[TradeRecord] = []
        
        # 回调函数
        self.on_trade_callback: Optional[Callable] = None
        self.on_day_end_callback: Optional[Callable] = None
    
    def set_trade_callback(self, callback: Callable):
        """设置交易回调"""
        self.on_trade_callback = callback
    
    def set_day_end_callback(self, callback: Callable):
        """设置每日结束回调"""
        self.on_day_end_callback = callback
    
    def run(
        self,
        data: Dict[str, List[Dict]],  # {symbol: [{date, open, high, low, close, volume}]}
        strategy: Callable,  # 策略函数: (simulator, date, market_data) -> List[orders]
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> BacktestResult:
        """运行回测
        
        Args:
            data: 市场数据字典
            strategy: 策略函数
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            BacktestResult: 回测结果
        """
        logger.info(f"Starting backtest with initial cash: ${self.initial_cash:.2f}")
        
        # 获取所有日期
        all_dates = set()
        for symbol_data in data.values():
            for record in symbol_data:
                all_dates.add(datetime.strptime(record["date"], "%Y-%m-%d"))
        
        dates = sorted(all_dates)
        
        if start_date:
            dates = [d for d in dates if d >= start_date]
        if end_date:
            dates = [d for d in dates if d <= end_date]
        
        logger.info(f"Backtest period: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
        
        # 初始化
        self.simulator.reset()
        self.daily_records = []
        self.trades = []
        
        prev_portfolio_value = self.initial_cash
        
        # 逐日回测
        for date in dates:
            # 准备当日市场数据
            market_data = {}
            for symbol, symbol_data in data.items():
                for record in symbol_data:
                    if record["date"] == date.strftime("%Y-%m-%d"):
                        market_data[symbol] = {
                            "open": record.get("open", 0),
                            "high": record.get("high", 0),
                            "low": record.get("low", 0),
                            "close": record.get("close", 0),
                            "volume": record.get("volume", 0),
                        }
                        # 更新模拟器价格
                        self.simulator.update_market_price(
                            symbol, 
                            record.get("close", 0),
                            record.get("volume", 0)
                        )
                        break
            
            # 执行策略
            try:
                orders = strategy(self.simulator, date, market_data)
                
                # 执行订单
                for order in orders:
                    self._execute_order(order)
                    
            except Exception as e:
                logger.error(f"Error executing strategy on {date}: {e}")
            
            # 处理挂单
            self.simulator.process_orders()
            
            # 记录每日数据
            portfolio_value = self.simulator.get_portfolio_value()
            daily_return = (portfolio_value - prev_portfolio_value) / prev_portfolio_value
            cumulative_return = (portfolio_value - self.initial_cash) / self.initial_cash
            
            record = DailyRecord(
                date=date,
                portfolio_value=portfolio_value,
                cash=self.simulator.cash,
                positions_value=portfolio_value - self.simulator.cash,
                daily_return=daily_return,
                cumulative_return=cumulative_return,
            )
            self.daily_records.append(record)
            
            # 回调
            if self.on_day_end_callback:
                self.on_day_end_callback(date, record)
            
            prev_portfolio_value = portfolio_value
        
        # 计算结果
        result = self._calculate_results(dates[0], dates[-1])
        
        logger.info(f"Backtest completed. Total return: {result.total_return * 100:.2f}%")
        
        return result
    
    def _execute_order(self, order: Dict):
        """执行订单"""
        symbol = order["symbol"]
        side = OrderSide.BUY if order["side"] == "buy" else OrderSide.SELL
        order_type = OrderType.MARKET if order.get("type") == "market" else OrderType.LIMIT
        quantity = order["quantity"]
        price = order.get("price")
        
        result = self.simulator.submit_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
        
        if result and result.status.value == "filled":
            # 记录交易
            trade = TradeRecord(
                timestamp=datetime.now(),
                symbol=symbol,
                side=order["side"],
                quantity=quantity,
                price=result.filled_price,
                commission=quantity * result.filled_price * self.commission_rate,
            )
            self.trades.append(trade)
            
            # 回调
            if self.on_trade_callback:
                self.on_trade_callback(trade)
    
    def _calculate_results(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """计算回测结果"""
        final_value = self.simulator.get_portfolio_value()
        
        # 收益率
        total_return = (final_value - self.initial_cash) / self.initial_cash
        
        # 年化收益率
        days = (end_date - start_date).days
        years = days / 365
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        max_value = self.initial_cash
        max_drawdown = 0
        for record in self.daily_records:
            if record.portfolio_value > max_value:
                max_value = record.portfolio_value
            drawdown = (max_value - record.portfolio_value) / max_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 波动率
        if len(self.daily_records) > 1:
            returns = [r.daily_return for r in self.daily_records]
            volatility = (sum([(r - sum(returns)/len(returns))**2 for r in returns]) / len(returns)) ** 0.5
            volatility = volatility * (252 ** 0.5)  # 年化
        else:
            volatility = 0
        
        # 夏普比率
        sharpe_ratio = (annual_return - 0.02) / volatility if volatility > 0 else 0
        
        # 交易统计
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        losing_trades = sum(1 for t in self.trades if t.pnl < 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 盈亏分析
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [abs(t.pnl) for t in self.trades if t.pnl < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        profit_factor = sum(wins) / sum(losses) if losses else 0
        
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_cash=self.initial_cash,
            final_cash=final_value,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            daily_records=self.daily_records,
            trades=self.trades,
        )


# 便捷函数
def create_backtest_engine(
    initial_cash: float = 100000.0,
    commission_rate: float = 0.001,
) -> BacktestEngine:
    """创建回测引擎"""
    return BacktestEngine(
        initial_cash=initial_cash,
        commission_rate=commission_rate,
    )


__all__ = [
    'BacktestEngine',
    'BacktestResult',
    'TradeRecord',
    'DailyRecord',
    'create_backtest_engine',
]