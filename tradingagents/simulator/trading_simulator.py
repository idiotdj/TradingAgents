"""交易模拟器模块

支持多市场的模拟交易系统
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

from tradingagents.dataflows.market_enums import MarketType, detect_market

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"      # 市价单
    LIMIT = "limit"       # 限价单
    STOP = "stop"         # 止损单
    STOP_LIMIT = "stop_limit"  # 止损限价单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"       # 待成交
    FILLED = "filled"         # 已成交
    PARTIAL = "partial"       # 部分成交
    CANCELLED = "cancelled"   # 已取消
    REJECTED = "rejected"     # 已拒绝


class Position:
    """持仓"""
    
    def __init__(
        self,
        symbol: str,
        market: MarketType,
        quantity: float,
        avg_price: float,
        current_price: float,
    ):
        self.symbol = symbol
        self.market = market
        self.quantity = quantity
        self.avg_price = avg_price
        self.current_price = current_price
        self.unrealized_pnl = (current_price - avg_price) * quantity
        self.unrealized_pnl_pct = ((current_price - avg_price) / avg_price) * 100
    
    def update_price(self, current_price: float):
        """更新当前价格和盈亏"""
        self.current_price = current_price
        self.unrealized_pnl = (current_price - self.avg_price) * self.quantity
        self.unrealized_pnl_pct = ((current_price - self.avg_price) / self.avg_price) * 100


class Order:
    """订单"""
    
    def __init__(
        self,
        order_id: str,
        symbol: str,
        market: MarketType,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ):
        self.order_id = order_id
        self.symbol = symbol
        self.market = market
        self.side = side
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.filled_quantity = 0
        self.filled_price = 0
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.cancel_reason: Optional[str] = None
    
    def fill(self, filled_quantity: float, filled_price: float):
        """成交"""
        self.filled_quantity = filled_quantity
        self.filled_price = filled_price
        self.status = OrderStatus.FILLED
        self.updated_at = datetime.now()
    
    def partial_fill(self, filled_quantity: float, filled_price: float):
        """部分成交"""
        self.filled_quantity += filled_quantity
        self.filled_price = filled_price
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIAL
        self.updated_at = datetime.now()
    
    def cancel(self):
        """取消订单"""
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def __repr__(self):
        return f"Order({self.order_id}, {self.symbol}, {self.side.value}, {self.order_type.value}, {self.quantity}, status={self.status.value})"


class TradingSimulator:
    """交易模拟器"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.001,
        slippage: float = 0.001,
    ):
        """初始化模拟器
        
        Args:
            initial_cash: 初始资金
            commission_rate: 手续费率
            slippage: 滑点率
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        # 持仓和订单
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.order_counter = 0
        
        # 交易记录
        self.trade_history: List[Dict[str, Any]] = []
        
        # 市场数据缓存
        self.market_data: Dict[str, Dict] = {}
        
        logger.info(f"TradingSimulator initialized with cash: ${initial_cash:.2f}")
    
    def update_market_price(self, symbol: str, price: float, volume: float = 0):
        """更新市场数据
        
        Args:
            symbol: 股票代码
            price: 当前价格
            volume: 成交量
        """
        self.market_data[symbol] = {
            "price": price,
            "volume": volume,
            "timestamp": datetime.now(),
        }
        
        # 更新持仓的当前价格
        if symbol in self.positions:
            self.positions[symbol].update_price(price)
    
    def can_trade(self, symbol: str, side: OrderSide, quantity: float) -> tuple[bool, str]:
        """检查是否可以交易
        
        Returns:
            (can_trade, reason)
        """
        market = detect_market(symbol)
        
        # 检查市场交易时间
        from tradingagents.dataflows.market_enums import is_trading_time
        if market != MarketType.CRYPTO_BTC and not is_trading_time(market):
            return False, f"Market {market.value} is not in trading hours"
        
        # 获取当前价格
        if symbol not in self.market_data:
            return False, f"No market data for {symbol}"
        
        current_price = self.market_data[symbol]["price"]
        
        # 检查资金是否足够
        if side == OrderSide.BUY:
            estimated_cost = quantity * current_price * (1 + self.slippage)
            commission = estimated_cost * self.commission_rate
            total_cost = estimated_cost + commission
            
            if self.cash < total_cost:
                return False, f"Insufficient cash: need ${total_cost:.2f}, have ${self.cash:.2f}"
        
        # 检查持仓是否足够
        elif side == OrderSide.SELL:
            if symbol not in self.positions:
                return False, f"No position for {symbol}"
            if self.positions[symbol].quantity < quantity:
                return False, f"Insufficient position: need {quantity}, have {self.positions[symbol].quantity}"
        
        return True, ""
    
    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Optional[Order]:
        """提交订单
        
        Args:
            symbol: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 数量
            price: 限价 (仅限 Limit 和 Stop_Limit)
            stop_price: 止损价
            
        Returns:
            Order 对象 或 None
        """
        market = detect_market(symbol)
        
        # 创建订单
        self.order_counter += 1
        order = Order(
            order_id=f"ORD-{self.order_counter:06d}",
            symbol=symbol,
            market=market,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
        
        # 检查是否可以交易
        can_trade, reason = self.can_trade(symbol, side, quantity)
        if not can_trade:
            order.status = OrderStatus.REJECTED
            order.cancel_reason = reason
            self.orders.append(order)
            logger.warning(f"Order rejected: {reason}")
            return order
        
        # 市价单立即成交
        if order_type == OrderType.MARKET:
            self._execute_market_order(order)
        # 限价单挂单
        else:
            self.orders.append(order)
            logger.info(f"Order submitted: {order}")
        
        return order
    
    def _execute_market_order(self, order: Order):
        """执行市价单"""
        current_price = self.market_data[order.symbol]["price"]
        
        # 考虑滑点
        if order.side == OrderSide.BUY:
            exec_price = current_price * (1 + self.slippage)
        else:
            exec_price = current_price * (1 - self.slippage)
        
        # 计算手续费
        total_value = exec_price * order.quantity
        commission = total_value * self.commission_rate
        
        if order.side == OrderSide.BUY:
            # 买入
            if self.cash < total_value + commission:
                order.status = OrderStatus.REJECTED
                return
            
            self.cash -= (total_value + commission)
            
            # 更新或创建持仓
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                total_cost = pos.avg_price * pos.quantity + exec_price * order.quantity
                pos.quantity += order.quantity
                pos.avg_price = total_cost / pos.quantity
                pos.update_price(exec_price)
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    market=order.market,
                    quantity=order.quantity,
                    avg_price=exec_price,
                    current_price=exec_price,
                )
        else:
            # 卖出
            if order.symbol not in self.positions:
                order.status = OrderStatus.REJECTED
                return
            
            pos = self.positions[order.symbol]
            self.cash += (total_value - commission)
            pos.quantity -= order.quantity
            
            if pos.quantity <= 0:
                del self.positions[order.symbol]
        
        order.fill(order.quantity, exec_price)
        
        # 记录交易
        self.trade_history.append({
            "timestamp": datetime.now(),
            "order": order,
            "exec_price": exec_price,
            "commission": commission,
        })
        
        logger.info(f"Order executed: {order}, price: ${exec_price:.2f}")
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        for order in self.orders:
            if order.order_id == order_id and order.status == OrderStatus.PENDING:
                order.cancel()
                logger.info(f"Order cancelled: {order_id}")
                return True
        return False
    
    def get_portfolio_value(self) -> float:
        """获取组合市值"""
        positions_value = sum(
            pos.current_price * pos.quantity
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合摘要"""
        positions_value = sum(
            pos.current_price * pos.quantity
            for pos in self.positions.values()
        )
        
        total_pnl = 0
        for pos in self.positions.values():
            total_pnl += pos.unrealized_pnl
        
        return {
            "cash": self.cash,
            "positions_value": positions_value,
            "total_value": self.cash + positions_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": ((self.cash + positions_value - self.initial_cash) / self.initial_cash) * 100,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_pct": pos.unrealized_pnl_pct,
                }
                for symbol, pos in self.positions.items()
            },
            "pending_orders": len([o for o in self.orders if o.status == OrderStatus.PENDING]),
        }
    
    def process_orders(self):
        """处理待成交订单 (用于限价单)"""
        to_remove = []
        
        for order in self.orders:
            if order.status != OrderStatus.PENDING:
                continue
            
            if order.order_type == OrderType.LIMIT and order.price:
                current_price = self.market_data.get(order.symbol, {}).get("price", 0)
                
                # 检查是否触发
                if order.side == OrderSide.BUY and current_price <= order.price:
                    self._execute_market_order(order)
                    to_remove.append(order)
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    self._execute_market_order(order)
                    to_remove.append(order)
            
            elif order.order_type == OrderType.STOP and order.stop_price:
                current_price = self.market_data.get(order.symbol, {}).get("price", 0)
                
                if order.side == OrderSide.BUY and current_price >= order.stop_price:
                    self._execute_market_order(order)
                    to_remove.append(order)
                elif order.side == OrderSide.SELL and current_price <= order.stop_price:
                    self._execute_market_order(order)
                    to_remove.append(order)
        
        for order in to_remove:
            self.orders.remove(order)
    
    def reset(self):
        """重置模拟器"""
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self.trade_history.clear()
        self.market_data.clear()
        logger.info("TradingSimulator reset")


# 便捷函数
def create_simulator(
    initial_cash: float = 100000.0,
    commission_rate: float = 0.001,
) -> TradingSimulator:
    """创建交易模拟器"""
    return TradingSimulator(
        initial_cash=initial_cash,
        commission_rate=commission_rate,
    )


__all__ = [
    'TradingSimulator',
    'Order',
    'Position',
    'OrderType',
    'OrderSide',
    'OrderStatus',
    'create_simulator',
]