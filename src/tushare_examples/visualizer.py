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
    
    def plot_news_sentiment(self,
                           sentiment_data: pd.DataFrame,
                           title: str = "新闻情感分析",
                           figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        绘制新闻情感分析图表
        
        Args:
            sentiment_data: 情感分析数据，包含positive, negative, neutral列
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 情感分布饼图
        sentiment_avg = sentiment_data.mean()
        colors = ['#ff6b6b', '#4ecdc4', '#95a5a6']
        labels = ['正面', '负面', '中性']
        values = [sentiment_avg['positive'], sentiment_avg['negative'], sentiment_avg['neutral']]
        
        ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('情感分布')
        
        # 情感时间序列（如果有时间信息）
        if len(sentiment_data) > 1:
            x = range(len(sentiment_data))
            ax2.plot(x, sentiment_data['positive'], color='green', label='正面', marker='o')
            ax2.plot(x, sentiment_data['negative'], color='red', label='负面', marker='s')
            ax2.plot(x, sentiment_data['neutral'], color='gray', label='中性', marker='^')
            ax2.set_xlabel('时间序列')
            ax2.set_ylabel('情感得分')
            ax2.set_title('情感变化趋势')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, '数据不足\n无法显示趋势', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=14)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        self.logger.info(f"成功绘制情感分析图表: {title}")
        return fig
    
    def plot_news_frequency(self,
                          daily_counts: Dict,
                          title: str = "新闻发布频率",
                          figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        绘制新闻发布频率图表
        
        Args:
            daily_counts: 每日新闻数量字典
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        if not daily_counts:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title)
            return fig
        
        # 转换日期和数量
        dates = list(daily_counts.keys())
        counts = list(daily_counts.values())
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制柱状图
        bars = ax.bar(dates, counts, color=self.colors['ma5'], alpha=0.7)
        
        # 添加数值标签
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   str(count), ha='center', va='bottom')
        
        ax.set_xlabel('日期')
        ax.set_ylabel('新闻数量')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # 旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self.logger.info(f"成功绘制新闻频率图表: {title}")
        return fig
    
    def plot_news_sources(self,
                         source_counts: Dict,
                         title: str = "新闻来源分布",
                         figsize: Tuple[int, int] = None,
                         top_n: int = 10) -> plt.Figure:
        """
        绘制新闻来源分布图表
        
        Args:
            source_counts: 新闻来源统计字典
            title: 图表标题
            figsize: 图表大小
            top_n: 显示前N个来源
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        if not source_counts:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title)
            return fig
        
        # 取前N个来源
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        sources = [item[0] for item in sorted_sources]
        counts = [item[1] for item in sorted_sources]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制水平柱状图
        colors = plt.cm.Set3(np.linspace(0, 1, len(sources)))
        bars = ax.barh(sources, counts, color=colors)
        
        # 添加数值标签
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   str(count), ha='left', va='center')
        
        ax.set_xlabel('新闻数量')
        ax.set_ylabel('新闻来源')
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        self.logger.info(f"成功绘制新闻来源图表: {title}")
        return fig
    
    def plot_keywords_cloud(self,
                          keywords: Dict[str, int],
                          title: str = "新闻关键词",
                          figsize: Tuple[int, int] = None,
                          max_words: int = 20) -> plt.Figure:
        """
        绘制关键词词云图（简化版）
        
        Args:
            keywords: 关键词频率字典
            title: 图表标题
            figsize: 图表大小
            max_words: 最大显示词数
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        if not keywords:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '暂无关键词数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title)
            return fig
        
        # 取前N个关键词
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:max_words]
        words = [item[0] for item in sorted_keywords]
        frequencies = [item[1] for item in sorted_keywords]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 使用柱状图显示关键词频率
        colors = plt.cm.viridis(np.linspace(0, 1, len(words)))
        bars = ax.bar(range(len(words)), frequencies, color=colors)
        
        # 设置x轴标签
        ax.set_xticks(range(len(words)))
        ax.set_xticklabels(words, rotation=45, ha='right')
        
        # 添加数值标签
        for bar, freq in zip(bars, frequencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   str(freq), ha='center', va='bottom')
        
        ax.set_xlabel('关键词')
        ax.set_ylabel('频率')
        ax.set_title(title)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        self.logger.info(f"成功绘制关键词图表: {title}")
        return fig
    
    def create_news_dashboard(self,
                            news_report: Dict[str, Any],
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        创建新闻分析仪表板
        
        Args:
            news_report: 新闻分析报告
            save_path: 保存路径
            
        Returns:
            plt.Figure: 仪表板图表
        """
        fig = plt.figure(figsize=(16, 12))
        
        # 创建子图网格
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        stock_code = news_report.get('stock_code', '全市场')
        
        try:
            # 1. 新闻频率图
            if 'news_analysis' in news_report and 'daily_counts' in news_report['news_analysis']:
                ax1 = fig.add_subplot(gs[0, 0])
                daily_counts = news_report['news_analysis']['daily_counts']
                if daily_counts:
                    dates = list(daily_counts.keys())
                    counts = list(daily_counts.values())
                    ax1.bar(dates, counts, color=self.colors['ma5'], alpha=0.7)
                    ax1.set_title('新闻发布频率')
                    ax1.set_ylabel('数量')
                    plt.setp(ax1.get_xticklabels(), rotation=45)
                else:
                    ax1.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=ax1.transAxes)
            
            # 2. 情感分析饼图
            if 'sentiment_analysis' in news_report:
                ax2 = fig.add_subplot(gs[0, 1])
                sentiment = news_report['sentiment_analysis']['sentiment_distribution']
                labels = ['正面', '负面', '中性']
                values = [sentiment['positive'], sentiment['negative'], sentiment['neutral']]
                colors_pie = ['#2ecc71', '#e74c3c', '#95a5a6']
                ax2.pie(values, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
                ax2.set_title('情感分布')
            
            # 3. 新闻来源分布
            if 'news_analysis' in news_report and 'source_counts' in news_report['news_analysis']:
                ax3 = fig.add_subplot(gs[1, :])
                source_counts = news_report['news_analysis']['source_counts']
                if source_counts:
                    sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:8]
                    sources = [item[0] for item in sorted_sources]
                    counts = [item[1] for item in sorted_sources]
                    ax3.barh(sources, counts, color=plt.cm.Set3(np.linspace(0, 1, len(sources))))
                    ax3.set_title('新闻来源分布')
                    ax3.set_xlabel('数量')
                else:
                    ax3.text(0.5, 0.5, '暂无来源数据', ha='center', va='center', transform=ax3.transAxes)
            
            # 4. 关键词频率
            if 'news_analysis' in news_report and 'top_keywords' in news_report['news_analysis']:
                ax4 = fig.add_subplot(gs[2, :])
                keywords = news_report['news_analysis']['top_keywords']
                if keywords:
                    words = list(keywords.keys())[:10]
                    frequencies = list(keywords.values())[:10]
                    ax4.bar(range(len(words)), frequencies, color=plt.cm.viridis(np.linspace(0, 1, len(words))))
                    ax4.set_xticks(range(len(words)))
                    ax4.set_xticklabels(words, rotation=45, ha='right')
                    ax4.set_title('热门关键词')
                    ax4.set_ylabel('频率')
                else:
                    ax4.text(0.5, 0.5, '暂无关键词数据', ha='center', va='center', transform=ax4.transAxes)
            
        except Exception as e:
            self.logger.error(f"创建仪表板失败: {str(e)}")
        
        # 设置总标题
        analysis_period = news_report.get('analysis_period', 30)
        fig.suptitle(f'{stock_code} 新闻分析仪表板 (最近{analysis_period}天)', 
                    fontsize=16, fontweight='bold')
        
        if save_path:
            self.save_chart(fig, save_path)
        
        self.logger.info(f"成功创建新闻仪表板: {stock_code}")
        return fig
    
    def plot_price_info_card(self,
                           price_info: Dict[str, Any],
                           figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        绘制股价信息卡片
        
        Args:
            price_info: 股价信息字典
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (10, 6)
        
        if 'error' in price_info:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"错误: {price_info['error']}", 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=16, color='red')
            ax.set_title('股价信息获取失败')
            ax.axis('off')
            return fig
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 获取数据
        ts_code = price_info.get('ts_code', 'N/A')
        name = price_info.get('name', 'N/A')
        current_price = price_info.get('current_price', 0)
        pct_change = price_info.get('pct_change', 0)
        change_direction = price_info.get('change_direction', 'flat')
        
        # 颜色设置
        color = '#ff4444' if change_direction == 'up' else '#00aa00' if change_direction == 'down' else '#666666'
        
        # 1. 价格显示
        ax1.text(0.5, 0.7, f'{current_price:.2f}', ha='center', va='center', 
                fontsize=24, fontweight='bold', color=color)
        ax1.text(0.5, 0.4, f'{pct_change:+.2f}%', ha='center', va='center', 
                fontsize=16, color=color)
        ax1.text(0.5, 0.1, f'{name}\n({ts_code})', ha='center', va='center', 
                fontsize=12)
        ax1.set_title('当前股价', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. 价格范围
        prices = [
            price_info.get('low_price', 0),
            price_info.get('open_price', 0), 
            current_price,
            price_info.get('high_price', 0)
        ]
        labels = ['最低', '开盘', '当前', '最高']
        colors_bar = ['green', 'blue', color, 'red']
        
        bars = ax2.bar(labels, prices, color=colors_bar, alpha=0.7)
        ax2.set_title('价格范围', fontsize=14, fontweight='bold')
        ax2.set_ylabel('价格 (元)')
        
        # 添加数值标签
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{price:.2f}', ha='center', va='bottom', fontsize=10)
        
        # 3. 成交情况
        volume = price_info.get('volume', 0)
        amount = price_info.get('amount', 0)
        
        ax3.text(0.5, 0.7, f'{volume:,.0f}', ha='center', va='center', 
                fontsize=16, fontweight='bold')
        ax3.text(0.5, 0.5, '手', ha='center', va='center', fontsize=12)
        ax3.text(0.5, 0.3, f'{amount:,.0f}', ha='center', va='center', 
                fontsize=14)
        ax3.text(0.5, 0.1, '千元', ha='center', va='center', fontsize=12)
        ax3.set_title('成交情况', fontsize=14, fontweight='bold')
        ax3.axis('off')
        
        # 4. 基本信息
        info_text = f"""行业: {price_info.get('industry', 'N/A')}
地区: {price_info.get('area', 'N/A')}
市场: {price_info.get('market', 'N/A')}
交易日: {price_info.get('trade_date', 'N/A')}"""
        
        ax4.text(0.1, 0.5, info_text, ha='left', va='center', 
                fontsize=11, transform=ax4.transAxes)
        ax4.set_title('基本信息', fontsize=14, fontweight='bold')
        ax4.axis('off')
        
        plt.tight_layout()
        
        self.logger.info(f"成功绘制股价信息卡片: {ts_code}")
        return fig
    
    def plot_price_trend(self,
                        history_data: pd.DataFrame,
                        title: str = "股价走势图",
                        figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        绘制股价走势图
        
        Args:
            history_data: 历史价格数据
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (self.config.chart_width/100, self.config.chart_height/100)
        
        if history_data.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '暂无历史数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title)
            return fig
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[3, 1])
        
        # 转换日期
        dates = pd.to_datetime(history_data['trade_date'])
        
        # 1. 价格走势图
        ax1.plot(dates, history_data['close'], color=self.colors['ma20'], linewidth=2, label='收盘价')
        
        # 添加移动平均线
        if 'ma5' in history_data.columns:
            ax1.plot(dates, history_data['ma5'], color=self.colors['ma5'], linewidth=1, label='MA5')
        if 'ma10' in history_data.columns:
            ax1.plot(dates, history_data['ma10'], color=self.colors['ma10'], linewidth=1, label='MA10')
        if 'ma20' in history_data.columns:
            ax1.plot(dates, history_data['ma20'], color=self.colors['ma60'], linewidth=1, label='MA20')
        
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.set_ylabel('价格 (元)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 成交量
        colors_vol = ['red' if close >= open_price else 'green' 
                     for close, open_price in zip(history_data['close'], history_data['open'])]
        
        ax2.bar(dates, history_data['vol'], color=colors_vol, alpha=0.6)
        ax2.set_ylabel('成交量 (手)')
        ax2.set_xlabel('日期')
        ax2.grid(True, alpha=0.3)
        
        # 旋转日期标签
        plt.setp(ax2.get_xticklabels(), rotation=45)
        plt.tight_layout()
        
        self.logger.info(f"成功绘制股价走势图: {title}")
        return fig
    
    def plot_multiple_prices_comparison(self,
                                       multiple_prices: Dict[str, Dict[str, Any]],
                                       title: str = "多股价格对比",
                                       figsize: Tuple[int, int] = None) -> plt.Figure:
        """
        绘制多股价格对比图
        
        Args:
            multiple_prices: 多股价格数据
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        if figsize is None:
            figsize = (12, 8)
        
        # 过滤有效数据
        valid_data = {k: v for k, v in multiple_prices.items() if 'error' not in v}
        
        if not valid_data:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, '暂无有效数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title(title)
            return fig
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 准备数据
        stock_names = []
        current_prices = []
        pct_changes = []
        volumes = []
        
        for ts_code, info in valid_data.items():
            stock_names.append(f"{info.get('name', 'N/A')}\n({ts_code})")
            current_prices.append(info.get('current_price', 0))
            pct_changes.append(info.get('pct_change', 0))
            volumes.append(info.get('volume', 0))
        
        # 1. 当前价格对比
        bars1 = ax1.bar(range(len(stock_names)), current_prices, 
                        color=plt.cm.viridis(np.linspace(0, 1, len(stock_names))))
        ax1.set_title('当前价格对比')
        ax1.set_ylabel('价格 (元)')
        ax1.set_xticks(range(len(stock_names)))
        ax1.set_xticklabels(stock_names, fontsize=9)
        
        # 添加数值标签
        for bar, price in zip(bars1, current_prices):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{price:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 2. 涨跌幅对比
        colors_change = ['red' if pct >= 0 else 'green' for pct in pct_changes]
        bars2 = ax2.bar(range(len(stock_names)), pct_changes, color=colors_change, alpha=0.7)
        ax2.set_title('涨跌幅对比')
        ax2.set_ylabel('涨跌幅 (%)')
        ax2.set_xticks(range(len(stock_names)))
        ax2.set_xticklabels(stock_names, fontsize=9)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # 添加数值标签
        for bar, pct in zip(bars2, pct_changes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., 
                    height + (height*0.1 if height >= 0 else height*0.1),
                    f'{pct:+.2f}%', ha='center', 
                    va='bottom' if height >= 0 else 'top', fontsize=9)
        
        # 3. 成交量对比
        bars3 = ax3.bar(range(len(stock_names)), volumes, 
                        color=plt.cm.plasma(np.linspace(0, 1, len(stock_names))))
        ax3.set_title('成交量对比')
        ax3.set_ylabel('成交量 (手)')
        ax3.set_xticks(range(len(stock_names)))
        ax3.set_xticklabels(stock_names, fontsize=9)
        
        # 4. 综合信息表
        table_data = []
        for ts_code, info in valid_data.items():
            table_data.append([
                info.get('name', 'N/A')[:6],  # 截取前6个字符
                f"{info.get('current_price', 0):.2f}",
                f"{info.get('pct_change', 0):+.2f}%",
                info.get('industry', 'N/A')[:4]  # 截取前4个字符
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['股票', '价格', '涨跌幅', '行业'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        ax4.axis('off')
        ax4.set_title('综合信息')
        
        plt.tight_layout()
        
        self.logger.info(f"成功绘制多股价格对比图: {len(valid_data)}只股票")
        return fig


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