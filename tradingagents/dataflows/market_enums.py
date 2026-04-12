"""市场类型枚举和符号标准化工具"""

from enum import Enum
from typing import Optional
import re


class MarketType(Enum):
    """市场类型枚举"""
    STOCK_US = "us"          # 美股
    STOCK_HK = "hk"          # 港股
    STOCK_CN_SH = "cn_sh"    # A股 - 上海
    STOCK_CN_SZ = "cn_sz"    # A股 - 深圳
    CRYPTO_BTC = "crypto"    # 加密货币
    UNKNOWN = "unknown"


# 符号格式正则表达式
PATTERNS = {
    MarketType.STOCK_US: r'^[A-Z]{1,5}$',
    MarketType.STOCK_HK: r'^\d{5}\.HK$',
    MarketType.STOCK_CN_SH: r'^\d{6}\.SS$',
    MarketType.STOCK_CN_SZ: r'^\d{6}\.SZ$',
    MarketType.CRYPTO_BTC: r'^[A-Z]{2,10}-[A-Z]{3}$',
}


def detect_market(ticker: str) -> MarketType:
    """自动检测股票代码所属市场
    
    Args:
        ticker: 股票代码
        
    Returns:
        MarketType: 市场类型
        
    Examples:
        >>> detect_market("AAPL")
        <MarketType.STOCK_US: 'us'>
        >>> detect_market("00700.HK")
        <MarketType.STOCK_HK: 'hk'>
        >>> detect_market("600519.SS")
        <MarketType.STOCK_CN_SH: 'cn_sh'>
        >>> detect_market("000001.SZ")
        <MarketType.STOCK_CN_SZ: 'cn_sz'>
        >>> detect_market("BTC-USD")
        <MarketType.CRYPTO_BTC: 'crypto'>
    """
    if not ticker:
        return MarketType.UNKNOWN
    
    ticker = ticker.upper().strip()
    
    # 检查加密货币 (如 BTC-USD, ETH-USD)
    if '-' in ticker and len(ticker.split('-')) == 2:
        return MarketType.CRYPTO_BTC
    
    # 检查港股 (如 00700.HK)
    if re.match(PATTERNS[MarketType.STOCK_HK], ticker):
        return MarketType.STOCK_HK
    
    # 检查A股上海 (如 600519.SS)
    if re.match(PATTERNS[MarketType.STOCK_CN_SH], ticker):
        return MarketType.STOCK_CN_SH
    
    # 检查A股深圳 (如 000001.SZ)
    if re.match(PATTERNS[MarketType.STOCK_CN_SZ], ticker):
        return MarketType.STOCK_CN_SZ
    
    # 检查美股 (纯字母)
    if re.match(PATTERNS[MarketType.STOCK_US], ticker):
        return MarketType.STOCK_US
    
    return MarketType.UNKNOWN


def normalize_ticker(ticker: str, target_market: Optional[MarketType] = None) -> str:
    """标准化股票代码格式
    
    Args:
        ticker: 原始股票代码
        target_market: 目标市场类型 (如果为 None, 则自动检测)
        
    Returns:
        str: 标准化后的股票代码
        
    Examples:
        >>> normalize_ticker("aapl")
        'AAPL'
        >>> normalize_ticker("600519")
        '600519.SS'
        >>> normalize_ticker("700")
        '00700.HK'
    """
    if not ticker:
        return ticker
    
    ticker = ticker.strip().upper()
    
    # 如果未指定目标市场,自动检测
    if target_market is None:
        target_market = detect_market(ticker)
    
    if target_market == MarketType.STOCK_US:
        # 美股: 保持纯字母格式
        return re.sub(r'[^A-Z]', '', ticker)
    
    elif target_market == MarketType.STOCK_HK:
        # 港股: 补齐 5 位数字 + .HK
        digits = re.sub(r'[^0-9]', '', ticker)
        if len(digits) < 5:
            digits = digits.zfill(5)
        return f"{digits}.HK"
    
    elif target_market == MarketType.STOCK_CN_SH:
        # A股上海: 6位数字 + .SS
        digits = re.sub(r'[^0-9]', '', ticker)
        if len(digits) < 6:
            digits = digits.zfill(6)
        return f"{digits}.SS"
    
    elif target_market == MarketType.STOCK_CN_SZ:
        # A股深圳: 6位数字 + .SZ
        digits = re.sub(r'[^0-9]', '', ticker)
        if len(digits) < 6:
            digits = digits.zfill(6)
        return f"{digits}.SZ"
    
    elif target_market == MarketType.CRYPTO_BTC:
        # 加密货币: 保持 XXX-USD 格式
        if '-' not in ticker:
            return f"{ticker}-USD"
        return ticker
    
    return ticker


def get_display_name(ticker: str, market: Optional[MarketType] = None) -> str:
    """获取显示用的股票名称
    
    Args:
        ticker: 股票代码
        market: 市场类型 (如果为 None, 则自动检测)
        
    Returns:
        str: 显示名称
        
    Examples:
        >>> get_display_name("600519.SS")
        '贵州茅台 (600519)'
        >>> get_display_name("AAPL")
        'Apple Inc. (AAPL)'
    """
    if market is None:
        market = detect_market(ticker)
    
    if market == MarketType.STOCK_CN_SH:
        return f"{ticker} (上海)"
    elif market == MarketType.STOCK_CN_SZ:
        return f"{ticker} (深圳)"
    elif market == MarketType.STOCK_HK:
        return f"{ticker} (港股)"
    elif market == MarketType.CRYPTO_BTC:
        return f"{ticker} (加密货币)"
    else:
        return f"{ticker} (美股)"


def is_trading_time(market: MarketType) -> bool:
    """检查当前是否为交易时间
    
    Args:
        market: 市场类型
        
    Returns:
        bool: 是否在交易时间内
    """
    from datetime import datetime, time
    import pytz
    
    now = datetime.now()
    
    if market == MarketType.STOCK_US:
        # 美股: EST 时区 9:30-16:00
        est = pytz.timezone('America/New_York')
        now_est = now.astimezone(est)
        current_time = now_est.time()
        return time(9, 30) <= current_time <= time(16, 0)
    
    elif market in (MarketType.STOCK_CN_SH, MarketType.STOCK_CN_SZ):
        # A股: CST 时区 9:30-15:00
        cst = pytz.timezone('Asia/Shanghai')
        now_cst = now.astimezone(cst)
        current_time = now_cst.time()
        # 午间休息 11:30-13:00
        if time(9, 30) <= current_time <= time(11, 30):
            return True
        if time(13, 0) <= current_time <= time(15, 0):
            return True
        return False
    
    elif market == MarketType.STOCK_HK:
        # 港股: HKT 时区 9:30-16:00
        hkt = pytz.timezone('Asia/Hong_Kong')
        now_hkt = now.astimezone(hkt)
        current_time = now_hkt.time()
        # 午间休息 12:00-13:00
        if time(9, 30) <= current_time <= time(12, 0):
            return True
        if time(13, 0) <= current_time <= time(16, 0):
            return True
        return False
    
    elif market == MarketType.CRYPTO_BTC:
        # 加密货币 7x24 小时交易
        return True
    
    return True


# 时区映射
MARKET_TIMEZONES = {
    MarketType.STOCK_US: "America/New_York",      # EST/EDT
    MarketType.STOCK_HK: "Asia/Hong_Kong",        # HKT
    MarketType.STOCK_CN_SH: "Asia/Shanghai",      # CST
    MarketType.STOCK_CN_SZ: "Asia/Shanghai",      # CST
    MarketType.CRYPTO_BTC: "UTC",                 # UTC
}


def get_market_timezone(market: MarketType) -> str:
    """获取市场对应时区
    
    Args:
        market: 市场类型
        
    Returns:
        str: 时区名称
    """
    return MARKET_TIMEZONES.get(market, "UTC")