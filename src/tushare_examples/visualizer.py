"""
数据可视化模块

提供丰富的股票数据可视化功能，支持K线图、技术指标图、财务图表等多种图表类型。
支持静态图表（matplotlib）和交互式图表（plotly）。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import mplfinance as mpf
import logging
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime

from .config import get_config

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')


class StockVisualizer:
    """股票数据可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # 颜色配置
        self.colors = {
            'up': '#ff4444',      # 上涨红色
            'down': '#00aa00',    # 下跌绿色
            'ma5': '#ff9900',     # MA5橙色
            'ma10': '#9900ff',    # MA10紫色
            'ma20': '#0099ff',    # MA20蓝色
            'ma60': '#ff0099',    # MA60粉色
            'volume': '#cccccc',  # 成交量灰色
            'macd': '#ff4444',    # MACD红色
            'signal': '#0066ff',  # 信号线蓝色
            'rsi': '#ff6600'      # RSI橙色
        }
    
    def plot_candlestick_mplfinance(self,
                                   data: pd.DataFrame,
                                   title: str = "股票K线图",
                                   ma_periods: List[int] = None,
                                   volume: bool = True,
                                   style: str = 'charles',
                                   figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        使用 mplfinance 绘制专业K线图
        
        Args:
            data: K线数据，需包含 Date, Open, High, Low, Close, Volume 列
            title: 图表标题
            ma_periods: 移动平均线周期
            volume: 是否显示成交量
            style: 图表样式
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if ma_periods is None:
            ma_periods = [5, 10, 20]
        
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        # 数据预处理
        df = data.copy()
        if 'trade_date' in df.columns:
            df['Date'] = pd.to_datetime(df['trade_date'])
            df.set_index('Date', inplace=True)
        
        # 重命名列以符合 mplfinance 要求
        column_mapping = {
            'open': 'Open',
            'high': 'High', 
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # 准备移动平均线
        mav_list = []
        for period in ma_periods:
            ma_col = f'MA{period}'
            if ma_col in df.columns:
                mav_list.append(period)
        
        # 绘制K线图
        kwargs = {
            'type': 'candle',
            'style': style,
            'title': title,
            'figsize': figsize,
            'volume': volume,
            'returnfig': True
        }
        
        if mav_list:
            kwargs['mav'] = mav_list
        
        try:
            fig, axes = mpf.plot(df, **kwargs)
            self.logger.info(f"成功绘制K线图: {title}")
            return fig
        except Exception as e:
            self.logger.error(f"绘制K线图失败: {str(e)}")
            raise
    
    def plot_interactive_candlestick(self,
                                    data: pd.DataFrame,
                                    title: str = "交互式K线图",
                                    ma_periods: List[int] = None,
                                    volume: bool = True) -> go.Figure:
        """
        绘制交互式K线图
        
        Args:
            data: K线数据
            title: 图表标题
            ma_periods: 移动平均线周期
            volume: 是否显示成交量
            
        Returns:
            plotly.graph_objects.Figure: 交互式图表
        """
        if ma_periods is None:
            ma_periods = [5, 10, 20]
        
        # 创建子图
        if volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.7, 0.3],
                subplot_titles=[title, "成交量"]
            )
        else:
            fig = go.Figure()
        
        # 添加K线图
        candlestick = go.Candlestick(
            x=data['trade_date'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            increasing_line_color=self.colors['up'],
            decreasing_line_color=self.colors['down'],
            name="K线"
        )
        
        if volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        # 添加移动平均线
        ma_colors = [self.colors['ma5'], self.colors['ma10'], self.colors['ma20'], self.colors['ma60']]
        for i, period in enumerate(ma_periods):
            ma_col = f'MA{period}'
            if ma_col in data.columns:
                color = ma_colors[i] if i < len(ma_colors) else f'rgb({np.random.randint(0,255)},{np.random.randint(0,255)},{np.random.randint(0,255)})'
                ma_line = go.Scatter(
                    x=data['trade_date'],
                    y=data[ma_col],
                    mode='lines',
                    name=f'MA{period}',
                    line=dict(color=color, width=1)
                )
                if volume:
                    fig.add_trace(ma_line, row=1, col=1)
                else:
                    fig.add_trace(ma_line)
        
        # 添加成交量
        if volume and 'vol' in data.columns:
            colors = [self.colors['up'] if close >= open_price else self.colors['down'] 
                     for close, open_price in zip(data['close'], data['open'])]
            
            volume_bars = go.Bar(
                x=data['trade_date'],
                y=data['vol'],
                marker_color=colors,
                name="成交量",
                opacity=0.7
            )
            fig.add_trace(volume_bars, row=2, col=1)
        
        # 更新布局
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            height=600 if volume else 400,
            template="plotly_white"
        )
        
        # 更新x轴
        fig.update_xaxes(
            type='date',
            tickformat='%Y-%m-%d'
        )
        
        return fig
    
    def plot_technical_indicators(self,
                                 data: pd.DataFrame,
                                 indicators: List[str] = None,
                                 interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        绘制技术指标图
        
        Args:
            data: 包含技术指标的数据
            indicators: 要绘制的指标列表
            interactive: 是否使用交互式图表
            
        Returns:
            图表对象
        """
        if indicators is None:
            indicators = ['MACD', 'RSI', 'KDJ']
        
        if interactive:
            return self._plot_interactive_indicators(data, indicators)
        else:
            return self._plot_static_indicators(data, indicators)
    
    def _plot_static_indicators(self, data: pd.DataFrame, indicators: List[str]) -> plt.Figure:
        """绘制静态技术指标图"""
        n_indicators = len(indicators)
        fig, axes = plt.subplots(n_indicators, 1, figsize=(12, 3*n_indicators), sharex=True)
        
        if n_indicators == 1:
            axes = [axes]
        
        for i, indicator in enumerate(indicators):
            ax = axes[i]
            
            if indicator == 'MACD':
                self._plot_macd_static(ax, data)
            elif indicator == 'RSI':
                self._plot_rsi_static(ax, data)
            elif indicator == 'KDJ':
                self._plot_kdj_static(ax, data)
            elif indicator == 'BB':
                self._plot_bollinger_static(ax, data)
            
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        # 设置x轴
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def _plot_interactive_indicators(self, data: pd.DataFrame, indicators: List[str]) -> go.Figure:
        """绘制交互式技术指标图"""
        n_indicators = len(indicators)
        
        fig = make_subplots(
            rows=n_indicators, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=indicators
        )
        
        for i, indicator in enumerate(indicators):
            row = i + 1
            
            if indicator == 'MACD':
                self._plot_macd_interactive(fig, data, row)
            elif indicator == 'RSI':
                self._plot_rsi_interactive(fig, data, row)
            elif indicator == 'KDJ':
                self._plot_kdj_interactive(fig, data, row)
            elif indicator == 'BB':
                self._plot_bollinger_interactive(fig, data, row)
        
        fig.update_layout(
            title="技术指标分析",
            height=300 * n_indicators,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def _plot_macd_static(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制静态MACD图"""
        if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            ax.plot(data['trade_date'], data['MACD'], label='MACD', color=self.colors['macd'])
            ax.plot(data['trade_date'], data['MACD_Signal'], label='Signal', color=self.colors['signal'])
            ax.bar(data['trade_date'], data['MACD_Histogram'], label='Histogram', alpha=0.7, width=0.8)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax.set_title('MACD')
            ax.set_ylabel('MACD')
    
    def _plot_macd_interactive(self, fig: go.Figure, data: pd.DataFrame, row: int):
        """绘制交互式MACD图"""
        if all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['MACD'],
                name='MACD', line=dict(color=self.colors['macd'])
            ), row=row, col=1)
            
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['MACD_Signal'],
                name='Signal', line=dict(color=self.colors['signal'])
            ), row=row, col=1)
            
            fig.add_trace(go.Bar(
                x=data['trade_date'], y=data['MACD_Histogram'],
                name='Histogram', opacity=0.7
            ), row=row, col=1)
    
    def _plot_rsi_static(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制静态RSI图"""
        if 'RSI' in data.columns:
            ax.plot(data['trade_date'], data['RSI'], label='RSI', color=self.colors['rsi'])
            ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线')
            ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线')
            ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
            ax.set_title('RSI')
            ax.set_ylabel('RSI')
            ax.set_ylim(0, 100)
    
    def _plot_rsi_interactive(self, fig: go.Figure, data: pd.DataFrame, row: int):
        """绘制交互式RSI图"""
        if 'RSI' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['RSI'],
                name='RSI', line=dict(color=self.colors['rsi'])
            ), row=row, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=row, col=1)
            fig.add_hline(y=50, line_dash="solid", line_color="gray", row=row, col=1)
    
    def _plot_kdj_static(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制静态KDJ图"""
        if all(col in data.columns for col in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
            ax.plot(data['trade_date'], data['KDJ_K'], label='K', linewidth=1)
            ax.plot(data['trade_date'], data['KDJ_D'], label='D', linewidth=1)
            ax.plot(data['trade_date'], data['KDJ_J'], label='J', linewidth=1)
            ax.axhline(y=80, color='red', linestyle='--', alpha=0.7)
            ax.axhline(y=20, color='green', linestyle='--', alpha=0.7)
            ax.set_title('KDJ')
            ax.set_ylabel('KDJ')
            ax.set_ylim(0, 100)
    
    def _plot_kdj_interactive(self, fig: go.Figure, data: pd.DataFrame, row: int):
        """绘制交互式KDJ图"""
        if all(col in data.columns for col in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
            for line, color in [('K', 'blue'), ('D', 'orange'), ('J', 'red')]:
                fig.add_trace(go.Scatter(
                    x=data['trade_date'], y=data[f'KDJ_{line}'],
                    name=line, line=dict(color=color)
                ), row=row, col=1)
            
            fig.add_hline(y=80, line_dash="dash", line_color="red", row=row, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", row=row, col=1)
    
    def _plot_bollinger_static(self, ax: plt.Axes, data: pd.DataFrame):
        """绘制静态布林带图"""
        if all(col in data.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower', 'close']):
            ax.plot(data['trade_date'], data['close'], label='收盘价', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Upper'], label='上轨', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Middle'], label='中轨', linewidth=1)
            ax.plot(data['trade_date'], data['BB_Lower'], label='下轨', linewidth=1)
            ax.fill_between(data['trade_date'], data['BB_Upper'], data['BB_Lower'], 
                           alpha=0.1, color='gray')
            ax.set_title('布林带')
            ax.set_ylabel('价格')
    
    def _plot_bollinger_interactive(self, fig: go.Figure, data: pd.DataFrame, row: int):
        """绘制交互式布林带图"""
        if all(col in data.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower', 'close']):
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['close'],
                name='收盘价', line=dict(color='black')
            ), row=row, col=1)
            
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['BB_Upper'],
                name='上轨', line=dict(color='red', dash='dash')
            ), row=row, col=1)
            
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['BB_Middle'],
                name='中轨', line=dict(color='blue')
            ), row=row, col=1)
            
            fig.add_trace(go.Scatter(
                x=data['trade_date'], y=data['BB_Lower'],
                name='下轨', line=dict(color='red', dash='dash'),
                fill='tonexty', fillcolor='rgba(200,200,200,0.1)'
            ), row=row, col=1)
    
    def plot_comparison_chart(self,
                             data_dict: Dict[str, pd.DataFrame],
                             price_column: str = 'close',
                             normalize: bool = True,
                             interactive: bool = False) -> Union[plt.Figure, go.Figure]:
        """
        绘制多股票对比图
        
        Args:
            data_dict: 股票数据字典，key为股票代码，value为数据
            price_column: 用于对比的价格列
            normalize: 是否标准化（以第一天为基准）
            interactive: 是否使用交互式图表
            
        Returns:
            图表对象
        """
        if interactive:
            return self._plot_interactive_comparison(data_dict, price_column, normalize)
        else:
            return self._plot_static_comparison(data_dict, price_column, normalize)
    
    def _plot_static_comparison(self, data_dict: Dict[str, pd.DataFrame], 
                               price_column: str, normalize: bool) -> plt.Figure:
        """绘制静态对比图"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for stock_code, data in data_dict.items():
            if price_column in data.columns:
                prices = data[price_column].copy()
                
                if normalize and not prices.empty:
                    prices = (prices / prices.iloc[0] - 1) * 100  # 转换为百分比变化
                
                ax.plot(data['trade_date'], prices, label=stock_code, linewidth=2)
        
        ax.set_title('股票价格对比' if not normalize else '股票涨跌幅对比')
        ax.set_ylabel('价格' if not normalize else '涨跌幅 (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 设置x轴
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def _plot_interactive_comparison(self, data_dict: Dict[str, pd.DataFrame], 
                                    price_column: str, normalize: bool) -> go.Figure:
        """绘制交互式对比图"""
        fig = go.Figure()
        
        for stock_code, data in data_dict.items():
            if price_column in data.columns:
                prices = data[price_column].copy()
                
                if normalize and not prices.empty:
                    prices = (prices / prices.iloc[0] - 1) * 100
                
                fig.add_trace(go.Scatter(
                    x=data['trade_date'],
                    y=prices,
                    mode='lines',
                    name=stock_code,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title='股票价格对比' if not normalize else '股票涨跌幅对比',
            yaxis_title='价格' if not normalize else '涨跌幅 (%)',
            template="plotly_white",
            height=500
        )
        
        return fig
    
    def plot_correlation_heatmap(self,
                                data_dict: Dict[str, pd.DataFrame],
                                price_column: str = 'close') -> plt.Figure:
        """
        绘制股票相关性热图
        
        Args:
            data_dict: 股票数据字典
            price_column: 用于计算相关性的价格列
            
        Returns:
            plt.Figure: 热图
        """
        # 构建价格矩阵
        price_matrix = pd.DataFrame()
        
        for stock_code, data in data_dict.items():
            if price_column in data.columns and 'trade_date' in data.columns:
                temp_data = data[['trade_date', price_column]].copy()
                temp_data.columns = ['trade_date', stock_code]
                temp_data.set_index('trade_date', inplace=True)
                
                if price_matrix.empty:
                    price_matrix = temp_data
                else:
                    price_matrix = price_matrix.join(temp_data, how='outer')
        
        # 计算相关性
        correlation_matrix = price_matrix.corr()
        
        # 绘制热图
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, ax=ax, fmt='.3f')
        ax.set_title('股票价格相关性热图')
        
        plt.tight_layout()
        return fig
    
    def save_chart(self, fig: Union[plt.Figure, go.Figure], filename: str, format: str = 'png'):
        """
        保存图表
        
        Args:
            fig: 图表对象
            filename: 文件名
            format: 保存格式
        """
        file_path = self.config.get_chart_path(filename)
        
        try:
            if isinstance(fig, plt.Figure):
                fig.savefig(file_path, dpi=self.config.chart_dpi, bbox_inches='tight', format=format)
            elif hasattr(fig, 'write_image'):  # Plotly figure
                fig.write_image(file_path, format=format, width=self.config.chart_width, 
                               height=self.config.chart_height)
            
            self.logger.info(f"图表已保存到: {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存图表失败: {str(e)}")
            raise


def demo_visualization():
    """数据可视化演示"""
    print("=" * 60)
    print("股票数据可视化演示")
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
        'vol': volumes,
        'MA5': close_prices,  # 简化的移动平均线
        'MA20': close_prices,
        'RSI': np.random.uniform(30, 70, 100),
        'MACD': np.random.randn(100) * 0.5,
        'MACD_Signal': np.random.randn(100) * 0.3,
        'MACD_Histogram': np.random.randn(100) * 0.2
    })
    
    # 创建可视化器
    visualizer = StockVisualizer()
    
    print("\n1. 绘制专业K线图...")
    try:
        fig1 = visualizer.plot_candlestick_mplfinance(data, title="示例股票K线图")
        visualizer.save_chart(fig1, "demo_candlestick.png")
        print("K线图已保存")
    except Exception as e:
        print(f"绘制K线图失败: {e}")
    
    print("\n2. 绘制交互式K线图...")
    try:
        fig2 = visualizer.plot_interactive_candlestick(data, title="交互式K线图")
        visualizer.save_chart(fig2, "demo_interactive_candlestick.html")
        print("交互式K线图已保存")
    except Exception as e:
        print(f"绘制交互式K线图失败: {e}")
    
    print("\n3. 绘制技术指标图...")
    try:
        fig3 = visualizer.plot_technical_indicators(data, ['MACD', 'RSI'])
        visualizer.save_chart(fig3, "demo_indicators.png")
        print("技术指标图已保存")
    except Exception as e:
        print(f"绘制技术指标图失败: {e}")
    
    plt.show()
    
    print("\n" + "=" * 60)
    print("可视化演示完成！图表已保存到 charts 目录")


if __name__ == "__main__":
    demo_visualization()