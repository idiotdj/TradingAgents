"""多市场股票数据获取工具

支持美股、港股、A股、加密货币的数据获取
"""

from langchain_core.tools import tool
from typing import Annotated, Optional
import logging

from tradingagents.dataflows.market_enums import detect_market, MarketType, normalize_ticker
from tradingagents.dataflows.interface import route_to_vendor

logger = logging.getLogger(__name__)


@tool
def get_market_stock_data(
    symbol: Annotated[str, "ticker symbol of the company or crypto"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Automatically detects market type and selects appropriate data source.
    
    Supports:
    - US stocks: AAPL, NVDA, MSFT (uses yfinance)
    - HK stocks: 00700.HK, 09988.HK (uses AkShare)
    - CN stocks (Shanghai): 600519.SS, 688111.SS (uses AkShare)
    - CN stocks (Shenzhen): 000001.SZ, 300750.SZ (uses AkShare)
    - Crypto: BTC-USD, ETH-USD (uses yfinance)
    
    Args:
        symbol (str): Ticker symbol with proper format
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
        
    Returns:
        str: Formatted stock price data
    """
    try:
        # 检测市场类型
        market = detect_market(symbol)
        logger.info(f"Detected market for {symbol}: {market}")
        
        # 标准化符号
        normalized_symbol = normalize_ticker(symbol, market)
        
        if market == MarketType.STOCK_US:
            # 美股 - 使用 yfinance
            return route_to_vendor("get_stock_data", normalized_symbol, start_date, end_date)
        
        elif market in (MarketType.STOCK_CN_SH, MarketType.STOCK_CN_SZ, MarketType.STOCK_HK):
            # 港股/A股 - 尝试使用 AkShare
            try:
                from tradingagents.dataflows.akshare_data import get_stock_akshare
                return get_stock_akshare(normalized_symbol, start_date, end_date)
            except ImportError:
                return "Error: akshare not installed. Install with: pip install akshare"
        
        elif market == MarketType.CRYPTO_BTC:
            # 加密货币 - 使用 yfinance
            return route_to_vendor("get_stock_data", normalized_symbol, start_date, end_date)
        
        else:
            # 默认使用原路由
            return route_to_vendor("get_stock_data", symbol, start_date, end_date)
            
    except Exception as e:
        logger.error(f"Error getting stock data for {symbol}: {e}")
        return f"Error getting data for {symbol}: {str(e)}"


@tool
def get_market_fundamentals(
    symbol: Annotated[str, "ticker symbol of the company or crypto"],
) -> str:
    """
    Retrieve fundamental data for a given ticker.
    Automatically detects market type and selects appropriate data source.
    
    Args:
        symbol (str): Ticker symbol with proper format
        
    Returns:
        str: Formatted fundamental data
    """
    try:
        market = detect_market(symbol)
        normalized_symbol = normalize_ticker(symbol, market)
        
        if market == MarketType.STOCK_US:
            # 美股 - 使用原接口
            return route_to_vendor("get_fundamentals", normalized_symbol)
        
        elif market in (MarketType.STOCK_CN_SH, MarketType.STOCK_CN_SZ, MarketType.STOCK_HK):
            # 港股/A股 - 使用 AkShare
            try:
                from tradingagents.dataflows.akshare_data import get_fundamentals_akshare
                return get_fundamentals_akshare(normalized_symbol)
            except ImportError:
                return "Error: akshare not installed"
        
        elif market == MarketType.CRYPTO_BTC:
            # 加密货币 - 返回基本信息
            return f"# 加密货币基本信息: {symbol}\n\nNote: Crypto fundamentals data is limited. Consider using CoinGecko API for detailed info."
        
        else:
            return route_to_vendor("get_fundamentals", symbol)
            
    except Exception as e:
        logger.error(f"Error getting fundamentals for {symbol}: {e}")
        return f"Error: {str(e)}"


@tool
def get_market_news(
    symbol: Annotated[str, "ticker symbol of the company or crypto"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve news data for a given ticker.
    Automatically detects market type and selects appropriate data source.
    
    Args:
        symbol (str): Ticker symbol with proper format
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
        
    Returns:
        str: Formatted news data
    """
    try:
        market = detect_market(symbol)
        normalized_symbol = normalize_ticker(symbol, market)
        
        if market in (MarketType.STOCK_CN_SH, MarketType.STOCK_CN_SZ, MarketType.STOCK_HK):
            # 港股/A股 - 使用 AkShare
            try:
                from tradingagents.dataflows.akshare_data import get_news_akshare
                return get_news_akshare(normalized_symbol, start_date, end_date)
            except ImportError:
                return "Error: akshare not installed"
        
        # 其他市场使用原接口
        return route_to_vendor("get_news", normalized_symbol, start_date, end_date)
            
    except Exception as e:
        logger.error(f"Error getting news for {symbol}: {e}")
        return f"Error: {str(e)}"


# 导出所有工具
__all__ = [
    'get_market_stock_data',
    'get_market_fundamentals', 
    'get_market_news',
]