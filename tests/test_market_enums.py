"""测试市场类型枚举和符号标准化工具"""

import pytest
from tradingagents.dataflows.market_enums import (
    detect_market,
    MarketType,
    normalize_ticker,
    get_display_name,
    is_trading_time,
    get_market_timezone,
)


class TestDetectMarket:
    """测试市场检测"""
    
    def test_detect_us_stock(self):
        """测试美股检测"""
        assert detect_market("AAPL") == MarketType.STOCK_US
        assert detect_market("MSFT") == MarketType.STOCK_US
        assert detect_market("NVDA") == MarketType.STOCK_US
    
    def test_detect_hk_stock(self):
        """测试港股检测"""
        assert detect_market("00700.HK") == MarketType.STOCK_HK
        assert detect_market("09988.HK") == MarketType.STOCK_HK
    
    def test_detect_cn_sh_stock(self):
        """测试A股上海检测"""
        assert detect_market("600519.SS") == MarketType.STOCK_CN_SH
        assert detect_market("688111.SS") == MarketType.STOCK_CN_SH
    
    def test_detect_cn_sz_stock(self):
        """测试A股深圳检测"""
        assert detect_market("000001.SZ") == MarketType.STOCK_CN_SZ
        assert detect_market("300750.SZ") == MarketType.STOCK_CN_SZ
    
    def test_detect_crypto(self):
        """测试加密货币检测"""
        assert detect_market("BTC-USD") == MarketType.CRYPTO_BTC
        assert detect_market("ETH-USD") == MarketType.CRYPTO_BTC
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        assert detect_market("aapl") == MarketType.STOCK_US
        assert detect_market("AAPL") == MarketType.STOCK_US
    
    def test_empty_input(self):
        """测试空输入"""
        assert detect_market("") == MarketType.UNKNOWN
        assert detect_market(None) == MarketType.UNKNOWN  # type: ignore


class TestNormalizeTicker:
    """测试符号标准化"""
    
    def test_normalize_us_stock(self):
        """测试美股符号标准化"""
        assert normalize_ticker("aapl") == "AAPL"
        assert normalize_ticker("AAPL") == "AAPL"
    
    def test_normalize_hk_stock(self):
        """测试港股符号标准化"""
        assert normalize_ticker("700") == "00700.HK"
        assert normalize_ticker("00700") == "00700.HK"
        assert normalize_ticker("00700.HK") == "00700.HK"
    
    def test_normalize_cn_sh_stock(self):
        """测试A股上海符号标准化"""
        assert normalize_ticker("600519") == "600519.SS"
        assert normalize_ticker("600519.SS") == "600519.SS"
    
    def test_normalize_cn_sz_stock(self):
        """测试A股深圳符号标准化"""
        assert normalize_ticker("000001") == "000001.SZ"
        assert normalize_ticker("000001.SZ") == "000001.SZ"
    
    def test_normalize_crypto(self):
        """测试加密货币符号标准化"""
        assert normalize_ticker("btc-usd") == "BTC-USD"
        assert normalize_ticker("BTC-USD") == "BTC-USD"
        assert normalize_ticker("btc") == "BTC-USD"


class TestGetDisplayName:
    """测试显示名称"""
    
    def test_display_name_us(self):
        """测试美股显示名称"""
        name = get_display_name("AAPL")
        assert "AAPL" in name
        assert "美股" in name
    
    def test_display_name_hk(self):
        """测试港股显示名称"""
        name = get_display_name("00700.HK")
        assert "00700.HK" in name
        assert "港股" in name
    
    def test_display_name_cn_sh(self):
        """测试A股上海显示名称"""
        name = get_display_name("600519.SS")
        assert "600519.SS" in name
        assert "上海" in name
    
    def test_display_name_cn_sz(self):
        """测试A股深圳显示名称"""
        name = get_display_name("000001.SZ")
        assert "000001.SZ" in name
        assert "深圳" in name


class TestGetMarketTimezone:
    """测试时区获取"""
    
    def test_timezone_mapping(self):
        """测试时区映射"""
        assert get_market_timezone(MarketType.STOCK_US) == "America/New_York"
        assert get_market_timezone(MarketType.STOCK_HK) == "Asia/Hong_Kong"
        assert get_market_timezone(MarketType.STOCK_CN_SH) == "Asia/Shanghai"
        assert get_market_timezone(MarketType.STOCK_CN_SZ) == "Asia/Shanghai"
        assert get_market_timezone(MarketType.CRYPTO_BTC) == "UTC"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])