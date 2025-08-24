"""
技术指标计算模块

提供常用的股票技术分析指标计算功能，包括移动平均线、MACD、RSI、布林带等。
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional, Tuple


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        """初始化技术指标计算器"""
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """
        简单移动平均线 (Simple Moving Average)
        
        Args:
            data: 价格数据
            window: 移动窗口大小
            
        Returns:
            pd.Series: SMA 数值
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """
        指数移动平均线 (Exponential Moving Average)
        
        Args:
            data: 价格数据
            window: 移动窗口大小
            
        Returns:
            pd.Series: EMA 数值
        """
        return data.ewm(span=window).mean()
    
    @staticmethod
    def macd(data: pd.Series, 
             fast_period: int = 12, 
             slow_period: int = 26, 
             signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        MACD 指标 (Moving Average Convergence Divergence)
        
        Args:
            data: 收盘价数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            Dict: 包含 MACD、Signal、Histogram 的字典
        """
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        相对强弱指数 (Relative Strength Index)
        
        Args:
            data: 收盘价数据
            window: 计算窗口
            
        Returns:
            pd.Series: RSI 数值
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def bollinger_bands(data: pd.Series, 
                       window: int = 20, 
                       num_std: float = 2) -> Dict[str, pd.Series]:
        """
        布林带 (Bollinger Bands)
        
        Args:
            data: 收盘价数据
            window: 移动平均窗口
            num_std: 标准差倍数
            
        Returns:
            Dict: 包含上轨、中轨、下轨的字典
        """
        sma = TechnicalIndicators.sma(data, window)
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return {
            'Upper': upper_band,
            'Middle': sma,
            'Lower': lower_band
        }
    
    @staticmethod
    def kdj(high: pd.Series, 
            low: pd.Series, 
            close: pd.Series,
            k_period: int = 9,
            d_period: int = 3,
            j_period: int = 3) -> Dict[str, pd.Series]:
        """
        KDJ 指标
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            k_period: K 值计算周期
            d_period: D 值计算周期
            j_period: J 值计算周期
            
        Returns:
            Dict: 包含 K、D、J 值的字典
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        rsv = 100 * (close - lowest_low) / (highest_high - lowest_low)
        
        k = rsv.ewm(com=d_period-1).mean()
        d = k.ewm(com=j_period-1).mean()
        j = 3 * k - 2 * d
        
        return {
            'K': k,
            'D': d,
            'J': j
        }
    
    @staticmethod
    def atr(high: pd.Series, 
            low: pd.Series, 
            close: pd.Series, 
            window: int = 14) -> pd.Series:
        """
        平均真实范围 (Average True Range)
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            window: 计算窗口
            
        Returns:
            pd.Series: ATR 数值
        """
        high_low = high - low
        high_close_prev = np.abs(high - close.shift(1))
        low_close_prev = np.abs(low - close.shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = pd.Series(true_range).rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def williams_r(high: pd.Series, 
                   low: pd.Series, 
                   close: pd.Series, 
                   window: int = 14) -> pd.Series:
        """
        威廉指标 (Williams %R)
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            window: 计算窗口
            
        Returns:
            pd.Series: Williams %R 数值
        """
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        
        return wr
    
    @staticmethod
    def cci(high: pd.Series, 
            low: pd.Series, 
            close: pd.Series, 
            window: int = 20) -> pd.Series:
        """
        商品通道指数 (Commodity Channel Index)
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            window: 计算窗口
            
        Returns:
            pd.Series: CCI 数值
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=window).mean()
        mad = typical_price.rolling(window=window).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        return cci
    
    def calculate_all_indicators(self, 
                                data: pd.DataFrame, 
                                price_columns: Dict[str, str] = None) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            data: 包含OHLC数据的DataFrame
            price_columns: 价格列名映射，默认为标准格式
            
        Returns:
            pd.DataFrame: 包含所有技术指标的数据
        """
        if price_columns is None:
            price_columns = {
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'vol'
            }
        
        result = data.copy()
        
        try:
            # 获取价格数据
            close = data[price_columns['close']]
            high = data[price_columns['high']]
            low = data[price_columns['low']]
            
            # 移动平均线
            result['MA5'] = self.sma(close, 5)
            result['MA10'] = self.sma(close, 10)
            result['MA20'] = self.sma(close, 20)
            result['MA60'] = self.sma(close, 60)
            
            # 指数移动平均线
            result['EMA12'] = self.ema(close, 12)
            result['EMA26'] = self.ema(close, 26)
            
            # MACD
            macd_data = self.macd(close)
            result['MACD'] = macd_data['MACD']
            result['MACD_Signal'] = macd_data['Signal']
            result['MACD_Histogram'] = macd_data['Histogram']
            
            # RSI
            result['RSI'] = self.rsi(close)
            
            # 布林带
            bb_data = self.bollinger_bands(close)
            result['BB_Upper'] = bb_data['Upper']
            result['BB_Middle'] = bb_data['Middle']
            result['BB_Lower'] = bb_data['Lower']
            
            # KDJ
            kdj_data = self.kdj(high, low, close)
            result['KDJ_K'] = kdj_data['K']
            result['KDJ_D'] = kdj_data['D']
            result['KDJ_J'] = kdj_data['J']
            
            # ATR
            result['ATR'] = self.atr(high, low, close)
            
            # Williams %R
            result['Williams_R'] = self.williams_r(high, low, close)
            
            # CCI
            result['CCI'] = self.cci(high, low, close)
            
            self.logger.info(f"成功计算了 {len(result.columns) - len(data.columns)} 个技术指标")
            
        except Exception as e:
            self.logger.error(f"计算技术指标时出错: {str(e)}")
            
        return result
    
    def get_trading_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 包含技术指标的数据
            
        Returns:
            pd.DataFrame: 包含交易信号的数据
        """
        signals = data.copy()
        
        try:
            # MACD 金叉死叉信号
            signals['MACD_Golden_Cross'] = (
                (signals['MACD'] > signals['MACD_Signal']) & 
                (signals['MACD'].shift(1) <= signals['MACD_Signal'].shift(1))
            )
            signals['MACD_Death_Cross'] = (
                (signals['MACD'] < signals['MACD_Signal']) & 
                (signals['MACD'].shift(1) >= signals['MACD_Signal'].shift(1))
            )
            
            # RSI 超买超卖信号
            signals['RSI_Overbought'] = signals['RSI'] > 70
            signals['RSI_Oversold'] = signals['RSI'] < 30
            
            # 布林带突破信号
            signals['BB_Upper_Break'] = signals['close'] > signals['BB_Upper']
            signals['BB_Lower_Break'] = signals['close'] < signals['BB_Lower']
            
            # KDJ 金叉死叉信号
            signals['KDJ_Golden_Cross'] = (
                (signals['KDJ_K'] > signals['KDJ_D']) & 
                (signals['KDJ_K'].shift(1) <= signals['KDJ_D'].shift(1))
            )
            signals['KDJ_Death_Cross'] = (
                (signals['KDJ_K'] < signals['KDJ_D']) & 
                (signals['KDJ_K'].shift(1) >= signals['KDJ_D'].shift(1))
            )
            
            # 移动平均线信号
            signals['MA_Golden_Cross'] = (
                (signals['close'] > signals['MA20']) & 
                (signals['close'].shift(1) <= signals['MA20'].shift(1))
            )
            signals['MA_Death_Cross'] = (
                (signals['close'] < signals['MA20']) & 
                (signals['close'].shift(1) >= signals['MA20'].shift(1))
            )
            
            self.logger.info("成功生成交易信号")
            
        except Exception as e:
            self.logger.error(f"生成交易信号时出错: {str(e)}")
            
        return signals


def demo_technical_indicators():
    """技术指标计算演示"""
    print("=" * 60)
    print("技术指标计算演示")
    print("=" * 60)
    
    # 创建示例数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    
    # 模拟股价数据
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    high_prices = close_prices + np.random.uniform(0, 2, 100)
    low_prices = close_prices - np.random.uniform(0, 2, 100)
    open_prices = close_prices + np.random.uniform(-1, 1, 100)
    volumes = np.random.uniform(1000000, 5000000, 100)
    
    data = pd.DataFrame({
        'trade_date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'vol': volumes
    })
    
    # 计算技术指标
    calculator = TechnicalIndicators()
    data_with_indicators = calculator.calculate_all_indicators(data)
    
    # 生成交易信号
    data_with_signals = calculator.get_trading_signals(data_with_indicators)
    
    # 显示结果
    print("\n原始数据 (前5行):")
    print(data[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head().to_string())
    
    print("\n技术指标 (前5行):")
    indicator_columns = ['MA5', 'MA20', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower']
    print(data_with_indicators[indicator_columns].head().to_string())
    
    print("\n交易信号统计:")
    signal_columns = [col for col in data_with_signals.columns if 'Cross' in col or 'Overbought' in col or 'Oversold' in col or 'Break' in col]
    for col in signal_columns:
        signal_count = data_with_signals[col].sum()
        print(f"{col}: {signal_count} 次")
    
    print("\n" + "=" * 60)
    print("技术指标演示完成！")


if __name__ == "__main__":
    demo_technical_indicators()