"""
K线数据获取和可视化示例

演示如何使用 Tushare API 获取K线数据，计算技术指标，并进行可视化展示。
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import warnings

from ..client import TushareClient, TushareClientError
from ..indicators import TechnicalIndicators

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 忽略警告
warnings.filterwarnings('ignore')


class KLineAnalyzer:
    """K线数据分析器"""
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化K线分析器
        
        Args:
            client: Tushare 客户端实例
        """
        self.client = client or TushareClient()
        self.indicator_calculator = TechnicalIndicators()
        self.logger = logging.getLogger(__name__)
    
    def get_kline_data(self,
                      ts_code: str,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      period: str = 'daily') -> pd.DataFrame:
        """
        获取K线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD  
            period: 周期类型 'daily', 'weekly', 'monthly'
            
        Returns:
            pd.DataFrame: K线数据
        """
        try:
            # 如果没有指定日期，默认获取最近一年的数据
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            self.logger.info(f"获取 {ts_code} 的{period}K线数据，时间范围: {start_date} - {end_date}")
            
            # 根据周期选择API方法
            if period == 'daily':
                data = self.client.get_daily_data(ts_code, start_date, end_date)
            elif period == 'weekly':
                data = self.client.get_weekly_data(ts_code, start_date, end_date)
            elif period == 'monthly':
                data = self.client.get_monthly_data(ts_code, start_date, end_date)
            else:
                raise ValueError(f"不支持的周期类型: {period}")
            
            if not data.empty:
                # 数据预处理
                data['trade_date'] = pd.to_datetime(data['trade_date'])
                data = data.sort_values('trade_date')
                data.reset_index(drop=True, inplace=True)
                
                # 计算技术指标
                data = self.indicator_calculator.calculate_all_indicators(data)
                
                self.logger.info(f"成功获取 {len(data)} 条K线数据")
                return data
            else:
                self.logger.warning(f"未获取到 {ts_code} 的K线数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取K线数据失败: {str(e)}")
            return pd.DataFrame()
    
    def plot_candlestick(self,
                        data: pd.DataFrame,
                        title: str = None,
                        volume: bool = True,
                        ma_lines: List[int] = None,
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        绘制蜡烛图
        
        Args:
            data: K线数据
            title: 图表标题
            volume: 是否显示成交量
            ma_lines: 移动平均线周期列表
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if data.empty:
            raise ValueError("数据为空，无法绘制图表")
        
        if ma_lines is None:
            ma_lines = [5, 10, 20]
        
        # 创建子图
        if volume:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, 
                                         gridspec_kw={'height_ratios': [3, 1]},
                                         sharex=True)
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=figsize)
        
        # 绘制蜡烛图
        self._draw_candlesticks(ax1, data)
        
        # 绘制移动平均线
        for ma_period in ma_lines:
            ma_col = f'MA{ma_period}'
            if ma_col in data.columns:
                ax1.plot(data['trade_date'], data[ma_col], 
                        label=f'MA{ma_period}', linewidth=1)
        
        # 设置主图
        ax1.set_title(title or '股票K线图', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylabel('价格', fontsize=12)
        
        # 绘制成交量
        if volume and 'vol' in data.columns:
            self._draw_volume(ax2, data)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.grid(True, alpha=0.3)
        
        # 设置X轴格式
        if volume:
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def _draw_candlesticks(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制蜡烛图"""
        for i, row in data.iterrows():
            date = row['trade_date']
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            
            # 颜色设定：红涨绿跌
            color = 'red' if close_price >= open_price else 'green'
            
            # 绘制影线
            ax.plot([date, date], [low_price, high_price], 
                   color='black', linewidth=1)
            
            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            
            if height > 0:
                rect = Rectangle((date, bottom), timedelta(days=0.6), height,
                               facecolor=color, alpha=0.8, edgecolor='black')
                ax.add_patch(rect)
            else:
                # 十字星
                ax.plot([date - timedelta(days=0.3), date + timedelta(days=0.3)], 
                       [close_price, close_price], color='black', linewidth=2)
    
    def _draw_volume(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制成交量"""
        for i, row in data.iterrows():
            date = row['trade_date']
            volume = row['vol']
            color = 'red' if row['close'] >= row['open'] else 'green'
            
            ax.bar(date, volume, color=color, alpha=0.7, width=0.8)
    
    def plot_indicators(self,
                       data: pd.DataFrame,
                       indicators: List[str] = None,
                       figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
        """
        绘制技术指标图
        
        Args:
            data: 包含技术指标的数据
            indicators: 要绘制的指标列表
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if indicators is None:
            indicators = ['MACD', 'RSI', 'KDJ']
        
        n_indicators = len(indicators)
        fig, axes = plt.subplots(n_indicators, 1, figsize=figsize, sharex=True)
        
        if n_indicators == 1:
            axes = [axes]
        
        for i, indicator in enumerate(indicators):
            ax = axes[i]
            
            if indicator == 'MACD':
                self._plot_macd(ax, data)
            elif indicator == 'RSI':
                self._plot_rsi(ax, data)
            elif indicator == 'KDJ':
                self._plot_kdj(ax, data)
            elif indicator == 'BB':
                self._plot_bollinger_bands(ax, data)
            
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')
        
        # 设置X轴格式
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def _plot_macd(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制MACD指标"""
        if 'MACD' in data.columns:
            ax.plot(data['trade_date'], data['MACD'], label='MACD', linewidth=1)
            ax.plot(data['trade_date'], data['MACD_Signal'], label='Signal', linewidth=1)
            ax.bar(data['trade_date'], data['MACD_Histogram'], 
                  label='Histogram', alpha=0.7, width=0.8)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax.set_title('MACD')
            ax.set_ylabel('MACD')
    
    def _plot_rsi(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制RSI指标"""
        if 'RSI' in data.columns:
            ax.plot(data['trade_date'], data['RSI'], label='RSI', linewidth=1)
            ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线')
            ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线')
            ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
            ax.set_title('RSI')
            ax.set_ylabel('RSI')
            ax.set_ylim(0, 100)
    
    def _plot_kdj(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制KDJ指标"""
        if all(col in data.columns for col in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
            ax.plot(data['trade_date'], data['KDJ_K'], label='K', linewidth=1)
            ax.plot(data['trade_date'], data['KDJ_D'], label='D', linewidth=1)
            ax.plot(data['trade_date'], data['KDJ_J'], label='J', linewidth=1)
            ax.axhline(y=80, color='red', linestyle='--', alpha=0.7)
            ax.axhline(y=20, color='green', linestyle='--', alpha=0.7)
            ax.set_title('KDJ')
            ax.set_ylabel('KDJ')
            ax.set_ylim(0, 100)
    
    def _plot_bollinger_bands(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制布林带"""
        if all(col in data.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
            ax.plot(data['trade_date'], data['close'], label='收盘价', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Upper'], label='上轨', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Middle'], label='中轨', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Lower'], label='下轨', linewidth=1)
            ax.fill_between(data['trade_date'], data['BB_Upper'], data['BB_Lower'], 
                           alpha=0.1, color='gray')
            ax.set_title('布林带')
            ax.set_ylabel('价格')
    
    def analyze_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        趋势分析
        
        Args:
            data: K线数据
            
        Returns:
            Dict: 分析结果
        """
        if data.empty:
            return {}
        
        latest = data.iloc[-1]
        analysis = {
            'latest_price': latest['close'],
            'price_change': latest['close'] - data.iloc[0]['close'],
            'price_change_pct': (latest['close'] - data.iloc[0]['close']) / data.iloc[0]['close'] * 100,
            'highest_price': data['high'].max(),
            'lowest_price': data['low'].min(),
            'average_volume': data['vol'].mean()
        }
        
        # 技术指标分析
        if 'RSI' in data.columns:
            analysis['rsi_status'] = self._get_rsi_status(latest['RSI'])
        
        if 'MACD' in data.columns:
            analysis['macd_trend'] = 'bullish' if latest['MACD'] > latest['MACD_Signal'] else 'bearish'
        
        # 移动平均线分析
        ma_analysis = {}
        for ma in [5, 10, 20, 60]:
            ma_col = f'MA{ma}'
            if ma_col in data.columns:
                ma_analysis[f'ma{ma}_position'] = 'above' if latest['close'] > latest[ma_col] else 'below'
        
        analysis['ma_analysis'] = ma_analysis
        
        return analysis
    
    def _get_rsi_status(self, rsi_value: float) -> str:
        """获取RSI状态"""
        if rsi_value > 70:
            return 'overbought'
        elif rsi_value < 30:
            return 'oversold'
        else:
            return 'normal'
    
    def save_chart(self, fig: plt.Figure, filename: str):
        """保存图表"""
        chart_path = self.client.config.get_chart_path(filename)
        fig.savefig(chart_path, dpi=300, bbox_inches='tight')
        self.logger.info(f"图表已保存到: {chart_path}")


def demo_kline_analysis():
    """K线分析演示"""
    print("=" * 60)
    print("K线数据获取和分析演示")
    print("=" * 60)
    
    try:
        # 创建分析器
        analyzer = KLineAnalyzer()
        
        # 示例股票代码（平安银行）
        ts_code = "000001.SZ"
        print(f"\n分析股票: {ts_code}")
        
        # 获取K线数据
        print("\n1. 获取K线数据...")
        kline_data = analyzer.get_kline_data(
            ts_code=ts_code,
            start_date="20231001",  # 从2023年10月开始
            period='daily'
        )
        
        if kline_data.empty:
            print("无法获取K线数据，请检查股票代码或网络连接")
            return
        
        print(f"获取到 {len(kline_data)} 条K线数据")
        print("\nK线数据示例:")
        print(kline_data[['trade_date', 'open', 'high', 'low', 'close', 'vol']].head().to_string())
        
        # 显示技术指标
        print("\n2. 技术指标计算结果:")
        indicator_columns = ['MA5', 'MA20', 'RSI', 'MACD', 'MACD_Signal']
        print(kline_data[indicator_columns].tail().to_string())
        
        # 趋势分析
        print("\n3. 趋势分析:")
        trend_analysis = analyzer.analyze_trend(kline_data)
        for key, value in trend_analysis.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                if isinstance(value, float):
                    print(f"{key}: {value:.4f}")
                else:
                    print(f"{key}: {value}")
        
        # 绘制图表
        print("\n4. 生成图表...")
        
        # K线图
        print("绘制K线图...")
        fig1 = analyzer.plot_candlestick(
            kline_data, 
            title=f"{ts_code} K线图",
            ma_lines=[5, 10, 20]
        )
        analyzer.save_chart(fig1, f"{ts_code}_candlestick.png")
        
        # 技术指标图
        print("绘制技术指标图...")
        fig2 = analyzer.plot_indicators(
            kline_data,
            indicators=['MACD', 'RSI', 'KDJ']
        )
        analyzer.save_chart(fig2, f"{ts_code}_indicators.png")
        
        plt.show()  # 显示图表
        
        print("\n" + "=" * 60)
        print("K线分析演示完成！")
        print("图表已保存到 charts 目录")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    demo_kline_analysis()