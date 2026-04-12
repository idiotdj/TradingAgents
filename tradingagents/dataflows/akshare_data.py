"""AkShare 数据获取模块 - 港股和A股数据"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    logger.warning("akshare not installed. Install with: pip install akshare")
    ak = None  # type: ignore


def get_stock_akshare(
    symbol: str,
    start_date: str,
    end_date: str
) -> str:
    """获取A股/港股股票数据
    
    Args:
        symbol: 股票代码 (如 600519.SS, 00700.HK, 000001.SZ)
        start_date: 开始日期 (yyyy-mm-dd)
        end_date: 结束日期 (yyyy-mm-dd)
        
    Returns:
        str: 股票数据字符串
    """
    if not AKSHARE_AVAILABLE:
        return "Error: akshare not installed. Run: pip install akshare"
    
    try:
        # 判断市场类型
        symbol_upper = symbol.upper()
        
        if symbol_upper.endswith('.SS'):
            # 上海A股
            return _get_a_stock_sh(symbol_upper, start_date, end_date)
        elif symbol_upper.endswith('.SZ'):
            # 深圳A股
            return _get_a_stock_sz(symbol_upper, start_date, end_date)
        elif symbol_upper.endswith('.HK'):
            # 港股
            return _get_hk_stock(symbol_upper, start_date, end_date)
        else:
            return f"Error: Unknown symbol format: {symbol}"
            
    except Exception as e:
        logger.error(f"Error getting akshare data for {symbol}: {e}")
        return f"Error getting data for {symbol}: {str(e)}"


def _get_a_stock_sh(symbol: str, start_date: str, end_date: str) -> str:
    """获取上海A股数据"""
    try:
        # 去掉 .SS 后缀
        stock_code = symbol.replace('.SS', '')
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                start_date=start_date.replace('-', ''),
                                end_date=end_date.replace('-', ''))
        
        if df is None or df.empty:
            return f"No data found for {symbol}"
        
        # 格式化输出
        header = f"# 上海A股数据: {symbol}\n"
        header += f"# 数据日期: {start_date} 至 {end_date}\n"
        header += f"# 总记录数: {len(df)}\n\n"
        
        # 转换日期格式
        df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        return header + df.to_string(index=False)
    except Exception as e:
        return f"Error getting Shanghai A-share data: {str(e)}"


def _get_a_stock_sz(symbol: str, start_date: str, end_date: str) -> str:
    """获取深圳A股数据"""
    try:
        # 去掉 .SZ 后缀
        stock_code = symbol.replace('.SZ', '')
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=start_date.replace('-', ''),
                                end_date=end_date.replace('-', ''))
        
        if df is None or df.empty:
            return f"No data found for {symbol}"
        
        header = f"# 深圳A股数据: {symbol}\n"
        header += f"# 数据日期: {start_date} 至 {end_date}\n"
        header += f"# 总记录数: {len(df)}\n\n"
        
        df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        return header + df.to_string(index=False)
    except Exception as e:
        return f"Error getting Shenzhen A-share data: {str(e)}"


def _get_hk_stock(symbol: str, start_date: str, end_date: str) -> str:
    """获取港股数据"""
    try:
        # 去掉 .HK 后缀
        stock_code = symbol.replace('.HK', '')
        df = ak.stock_zh_hs_hist(symbol=stock_code, period="daily",
                                 start_date=start_date.replace('-', ''),
                                 end_date=end_date.replace('-', ''))
        
        if df is None or df.empty:
            return f"No data found for {symbol}"
        
        header = f"# 港股数据: {symbol}\n"
        header += f"# 数据日期: {start_date} 至 {end_date}\n"
        header += f"# 总记录数: {len(df)}\n\n"
        
        df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        
        return header + df.to_string(index=False)
    except Exception as e:
        return f"Error getting Hong Kong stock data: {str(e)}"


def get_fundamentals_akshare(ticker: str) -> str:
    """获取A股/港股基本面数据
    
    Args:
        ticker: 股票代码
        
    Returns:
        str: 基本面数据字符串
    """
    if not AKSHARE_AVAILABLE:
        return "Error: akshare not installed"
    
    try:
        ticker_upper = ticker.upper()
        
        if ticker_upper.endswith('.SS') or ticker_upper.endswith('.SZ'):
            # A股
            return _get_a_fundamentals(ticker_upper)
        elif ticker_upper.endswith('.HK'):
            # 港股
            return _get_hk_fundamentals(ticker_upper)
        else:
            return f"Unknown symbol format: {ticker}"
    except Exception as e:
        logger.error(f"Error getting fundamentals for {ticker}: {e}")
        return f"Error: {str(e)}"


def _get_a_fundamentals(ticker: str) -> str:
    """获取 A股基本面数据"""
    try:
        import pandas as pd
        
        # 去掉后缀
        stock_code = ticker.replace('.SS', '').replace('.SZ', '')
        
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 筛选对应股票
        stock_info = df[df['代码'] == stock_code]
        
        if stock_info.empty:
            return f"No fundamentals data found for {ticker}"
        
        # 提取关键信息
        info = stock_info.iloc[0]
        
        header = f"# A股基本面数据: {ticker}\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content = f"股票名称: {info.get('名称', 'N/A')}\n"
        content += f"股票代码: {info.get('代码', 'N/A')}\n"
        content += f"最新价: {info.get('最新价', 'N/A')}\n"
        content += f"涨跌幅: {info.get('涨跌幅', 'N/A')}%\n"
        content += f"涨跌额: {info.get('涨跌额', 'N/A')}\n"
        content += f"成交量: {info.get('成交量', 'N/A')}\n"
        content += f"成交额: {info.get('成交额', 'N/A')}\n"
        content += f"振幅: {info.get('振幅', 'N/A')}%\n"
        content += f"最高: {info.get('最高', 'N/A')}\n"
        content += f"最低: {info.get('最低', 'N/A')}\n"
        content += f"今开: {info.get('今开', 'N/A')}\n"
        content += f"昨收: {info.get('昨收', 'N/A')}\n"
        content += f"换手率: {info.get('换手率', 'N/A')}%\n"
        content += f"市盈率-动态: {info.get('市盈率-动态', 'N/A')}\n"
        content += f"市净率: {info.get('市净率', 'N/A')}\n"
        content += f"总市值: {info.get('总市值', 'N/A')}\n"
        content += f"流通市值: {info.get('流通市值', 'N/A')}\n"
        
        return header + content
    except Exception as e:
        return f"Error getting A-share fundamentals: {str(e)}"


def _get_hk_fundamentals(ticker: str) -> str:
    """获取港股基本面数据"""
    try:
        stock_code = ticker.replace('.HK', '')
        
        # 获取港股实时行情
        df = ak.stock_zh_hs_spot_em()
        
        # 筛选对应股票
        stock_info = df[df['代码'] == stock_code]
        
        if stock_info.empty:
            return f"No fundamentals data found for {ticker}"
        
        info = stock_info.iloc[0]
        
        header = f"# 港股基本面数据: {ticker}\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content = f"股票名称: {info.get('名称', 'N/A')}\n"
        content += f"股票代码: {info.get('代码', 'N/A')}\n"
        content += f"最新价: {info.get('最新价', 'N/A')}\n"
        content += f"涨跌幅: {info.get('涨跌幅', 'N/A')}%\n"
        content += f"涨跌额: {info.get('涨跌额', 'N/A')}\n"
        content += f"成交量: {info.get('成交量', 'N/A')}\n"
        content += f"成交额: {info.get('成交额', 'N/A')}\n"
        content += f"振幅: {info.get('振幅', 'N/A')}%\n"
        content += f"最高: {info.get('最高', 'N/A')}\n"
        content += f"最低: {info.get('最低', 'N/A')}\n"
        content += f"今开: {info.get('今开', 'N/A')}\n"
        content += f"昨收: {info.get('昨收', 'N/A')}\n"
        
        return header + content
    except Exception as e:
        return f"Error getting HK stock fundamentals: {str(e)}"


def get_news_akshare(ticker: str, start_date: str, end_date: str) -> str:
    """获取A股/港股新闻数据
    
    Args:
        ticker: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        str: 新闻数据字符串
    """
    if not AKSHARE_AVAILABLE:
        return "Error: akshare not installed"
    
    try:
        ticker_upper = ticker.upper()
        news_list = []
        
        if ticker_upper.endswith('.SS') or ticker_upper.endswith('.SZ'):
            # A股新闻
            stock_code = ticker_upper.replace('.SS', '').replace('.SZ', '')
            try:
                df = ak.stock_news_em(symbol=stock_code)
                if df is not None and not df.empty:
                    news_list.append(f"## {ticker} 新闻资讯\n")
                    for idx, row in df.head(10).iterrows():
                        news_list.append(f"- {row.get('标题', 'N/A')}")
            except:
                pass
                
        elif ticker_upper.endswith('.HK'):
            # 港股新闻
            stock_code = ticker_upper.replace('.HK', '')
            try:
                # 港股新闻接口可能有限制
                news_list.append(f"## {ticker} 新闻资讯")
                news_list.append("(港股新闻接口有限，可使用其他数据源)")
            except:
                pass
        
        if news_list:
            return "\n".join(news_list)
        return f"No news data available for {ticker}"
        
    except Exception as e:
        logger.error(f"Error getting news for {ticker}: {e}")
        return f"Error getting news: {str(e)}"


# 导出所有函数
__all__ = [
    'get_stock_akshare',
    'get_fundamentals_akshare',
    'get_news_akshare',
    'AKSHARE_AVAILABLE',
]