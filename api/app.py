"""
TradingAgents API 服务
基于 FastAPI 的 REST API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="TradingAgents API",
    description="多市场交易 Agent API",
    version="0.1.0",
)


# 数据模型
class MarketQuery(BaseModel):
    """市场查询请求"""
    ticker: str
    market: Optional[str] = None  # us, hk, cn, crypto


class MarketData(BaseModel):
    """市场数据响应"""
    ticker: str
    market: str
    current_price: Optional[float] = None
    daily: List[dict] = []


class BacktestRequest(BaseModel):
    """回测请求"""
    ticker: str
    start_date: str
    end_date: str
    initial_cash: float = 100000.0
    strategy: str = "simple"  # simple, ma, rsi


class BacktestResult(BaseModel):
    """回测结果"""
    start_date: str
    end_date: str
    initial_cash: float
    final_cash: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    win_rate: float


class TradeOrder(BaseModel):
    """交易订单"""
    ticker: str
    side: str  # buy, sell
    quantity: float
    order_type: str = "market"  # market, limit
    price: Optional[float] = None


# API 端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "TradingAgents API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/market/query", response_model=MarketData)
async def query_market(data: MarketQuery):
    """查询市场数据
    
    Args:
        data: 市场查询请求
        
    Returns:
        MarketData: 市场数据
    """
    try:
        from tradingagents.dataflows.market_enums import detect_market, get_display_name
        from tradingagents.agents.utils.market_tools import get_market_stock_data
        
        # 检测市场
        if data.market:
            from tradingagents.dataflows.market_enums import MarketType
            market_type = MarketType[data.market.upper()]
        else:
            market_type = detect_market(data.ticker)
        
        # 获取数据
        result = get_market_stock_data(data.ticker)
        
        if result:
            return MarketData(
                ticker=data.ticker,
                market=market_type.value,
                current_price=result.get("current_price"),
                daily=result.get("daily", [])[-30:],  # 最近30天
            )
        else:
            raise HTTPException(status_code=404, detail="未找到数据")
            
    except Exception as e:
        logger.error(f"查询市场数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/backtest", response_model=BacktestResult)
async def run_backtest(data: BacktestRequest):
    """运行回测
    
    Args:
        data: 回测请求
        
    Returns:
        BacktestResult: 回测结果
    """
    try:
        from tradingagents.backtest import create_backtest_engine
        from datetime import datetime
        
        # 简单的回测实现
        engine = create_backtest_engine(initial_cash=data.initial_cash)
        
        # 这里需要实现完整的回测逻辑
        # 简化版本返回模拟数据
        return BacktestResult(
            start_date=data.start_date,
            end_date=data.end_date,
            initial_cash=data.initial_cash,
            final_cash=data.initial_cash,
            total_return=0.0,
            annual_return=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            total_trades=0,
            win_rate=0.0,
        )
            
    except Exception as e:
        logger.error(f"回测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trade/order")
async def place_order(order: TradeOrder):
    """下单
    
    Args:
        order: 交易订单
        
    Returns:
        dict: 订单结果
    """
    try:
        from tradingagents.simulator import create_simulator, OrderSide, OrderType
        
        # 创建模拟器
        sim = create_simulator()
        
        # 更新市场数据 (需要真实数据)
        # 这里简化处理
        sim.update_market_price(order.ticker, 100.0)
        
        # 下单
        side = OrderSide.BUY if order.side == "buy" else OrderSide.SELL
        order_type = OrderType.MARKET if order.order_type == "market" else OrderType.LIMIT
        
        result = sim.submit_order(
            symbol=order.ticker,
            side=side,
            order_type=order_type,
            quantity=order.quantity,
            price=order.price,
        )
        
        return {
            "order_id": result.order_id if result else None,
            "status": result.status.value if result else "failed",
            "ticker": order.ticker,
            "side": order.side,
            "quantity": order.quantity,
        }
            
    except Exception as e:
        logger.error(f"下单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/markets")
async def list_markets():
    """列出支持的市场"""
    return {
        "markets": [
            {"code": "us", "name": "美股", "examples": ["AAPL", "MSFT", "NVDA"]},
            {"code": "hk", "name": "港股", "examples": ["00700.HK", "09988.HK"]},
            {"code": "cn", "name": "A股", "examples": ["600519.SS", "000001.SZ"]},
            {"code": "crypto", "name": "加密货币", "examples": ["BTC-USD", "ETH-USD"]},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)