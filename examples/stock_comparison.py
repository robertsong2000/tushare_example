#!/usr/bin/env python3
"""
多股票对比分析示例

演示如何同时分析多只股票，进行价格对比、相关性分析、行业对比等。
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tushare_examples.client import TushareClient
from src.tushare_examples.examples.kline_analysis import KLineAnalyzer
from src.tushare_examples.visualizer import StockVisualizer

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class StockComparator:
    """股票对比分析器"""
    
    def __init__(self):
        """初始化对比分析器"""
        self.client = TushareClient()
        self.kline_analyzer = KLineAnalyzer(self.client)
        self.visualizer = StockVisualizer()
        self.logger = logging.getLogger(__name__)
    
    def get_multiple_stocks_data(self, 
                               stock_codes: list,
                               start_date: str = None,
                               end_date: str = None) -> dict:
        """
        获取多只股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 股票代码为key，数据为value的字典
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        stock_data = {}
        
        for stock_code in stock_codes:
            try:
                print(f"获取 {stock_code} 的数据...")
                data = self.kline_analyzer.get_kline_data(
                    ts_code=stock_code,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not data.empty:
                    stock_data[stock_code] = data
                    print(f"✓ 成功获取 {stock_code} 的 {len(data)} 条记录")
                else:
                    print(f"✗ 未能获取 {stock_code} 的数据")
                    
            except Exception as e:
                print(f"✗ 获取 {stock_code} 数据失败: {str(e)}")
                continue
        
        return stock_data
    
    def calculate_performance_metrics(self, stock_data: dict) -> pd.DataFrame:
        """
        计算各股票的表现指标
        
        Args:
            stock_data: 股票数据字典
            
        Returns:
            pd.DataFrame: 表现指标对比表
        """
        metrics = []
        
        for stock_code, data in stock_data.items():
            if data.empty:
                continue
                
            # 计算基本指标
            first_price = data.iloc[0]['close']
            last_price = data.iloc[-1]['close']
            max_price = data['high'].max()
            min_price = data['low'].min()
            
            # 计算收益率
            total_return = (last_price - first_price) / first_price * 100
            
            # 计算波动率 (年化)
            daily_returns = data['close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100  # 年化波动率
            
            # 计算最大回撤
            cumulative_returns = (1 + daily_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100
            
            # 计算夏普比率 (假设无风险利率3%)
            risk_free_rate = 0.03
            excess_return = daily_returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_return / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
            
            # 计算平均成交量
            avg_volume = data['vol'].mean()
            
            metrics.append({
                'stock_code': stock_code,
                'start_price': first_price,
                'end_price': last_price,
                'max_price': max_price,
                'min_price': min_price,
                'total_return_pct': total_return,
                'volatility_pct': volatility,
                'max_drawdown_pct': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'avg_volume': avg_volume
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_correlation_matrix(self, stock_data: dict) -> pd.DataFrame:
        """
        计算股票价格相关性矩阵
        
        Args:
            stock_data: 股票数据字典
            
        Returns:
            pd.DataFrame: 相关性矩阵
        """
        # 构建价格矩阵
        price_data = pd.DataFrame()
        
        for stock_code, data in stock_data.items():
            if not data.empty:
                prices = data.set_index('trade_date')['close']
                prices.name = stock_code
                price_data = pd.concat([price_data, prices], axis=1)
        
        # 计算相关性
        correlation_matrix = price_data.corr()
        
        return correlation_matrix
    
    def plot_price_comparison(self, stock_data: dict, normalize: bool = True) -> plt.Figure:
        """
        绘制价格对比图
        
        Args:
            stock_data: 股票数据字典
            normalize: 是否标准化价格
            
        Returns:
            plt.Figure: 价格对比图
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for stock_code, data in stock_data.items():
            if data.empty:
                continue
                
            prices = data['close'].copy()
            dates = data['trade_date']
            
            if normalize:
                # 标准化为百分比变化
                prices = (prices / prices.iloc[0] - 1) * 100
                ylabel = '涨跌幅 (%)'
                title = '股票价格对比 (标准化)'
            else:
                ylabel = '价格'
                title = '股票价格对比 (绝对价格)'
            
            ax.plot(dates, prices, label=stock_code, linewidth=2)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 如果标准化，添加零线
        if normalize:
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_volume_comparison(self, stock_data: dict) -> plt.Figure:
        """
        绘制成交量对比图
        
        Args:
            stock_data: 股票数据字典
            
        Returns:
            plt.Figure: 成交量对比图
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for stock_code, data in stock_data.items():
            if data.empty or 'vol' not in data.columns:
                continue
                
            # 计算移动平均成交量以平滑曲线
            volume_ma = data['vol'].rolling(window=10).mean()
            
            ax.plot(data['trade_date'], volume_ma / 1e8, label=stock_code, linewidth=1.5)
        
        ax.set_title('成交量对比 (10日移动平均)', fontsize=14, fontweight='bold')
        ax.set_ylabel('成交量 (亿股)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_performance_comparison(self, metrics_df: pd.DataFrame) -> plt.Figure:
        """
        绘制表现指标对比图
        
        Args:
            metrics_df: 表现指标数据框
            
        Returns:
            plt.Figure: 表现对比图
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 总收益率对比
        ax1 = axes[0, 0]
        colors = ['green' if x >= 0 else 'red' for x in metrics_df['total_return_pct']]
        bars1 = ax1.bar(metrics_df['stock_code'], metrics_df['total_return_pct'], color=colors, alpha=0.7)
        ax1.set_title('总收益率对比')
        ax1.set_ylabel('收益率 (%)')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars1, metrics_df['total_return_pct']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (1 if value >= 0 else -3),
                    f'{value:.1f}%', ha='center', va='bottom' if value >= 0 else 'top')
        
        # 波动率对比
        ax2 = axes[0, 1]
        bars2 = ax2.bar(metrics_df['stock_code'], metrics_df['volatility_pct'], color='orange', alpha=0.7)
        ax2.set_title('年化波动率对比')
        ax2.set_ylabel('波动率 (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 最大回撤对比
        ax3 = axes[1, 0]
        bars3 = ax3.bar(metrics_df['stock_code'], metrics_df['max_drawdown_pct'], color='red', alpha=0.7)
        ax3.set_title('最大回撤对比')
        ax3.set_ylabel('最大回撤 (%)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 夏普比率对比
        ax4 = axes[1, 1]
        colors = ['green' if x >= 0 else 'red' for x in metrics_df['sharpe_ratio']]
        bars4 = ax4.bar(metrics_df['stock_code'], metrics_df['sharpe_ratio'], color=colors, alpha=0.7)
        ax4.set_title('夏普比率对比')
        ax4.set_ylabel('夏普比率')
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_correlation_heatmap(self, correlation_matrix: pd.DataFrame) -> plt.Figure:
        """
        绘制相关性热图
        
        Args:
            correlation_matrix: 相关性矩阵
            
        Returns:
            plt.Figure: 相关性热图
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='coolwarm', 
                   center=0,
                   square=True, 
                   fmt='.3f',
                   cbar_kws={'label': '相关系数'},
                   ax=ax)
        
        ax.set_title('股票价格相关性热图', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def generate_comparison_report(self, stock_codes: list) -> dict:
        """
        生成对比分析报告
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            dict: 分析报告
        """
        print(f"开始生成对比分析报告...")
        print(f"分析股票: {stock_codes}")
        
        # 获取数据
        stock_data = self.get_multiple_stocks_data(stock_codes)
        
        if not stock_data:
            return {'error': '未能获取任何股票数据'}
        
        # 计算指标
        metrics_df = self.calculate_performance_metrics(stock_data)
        correlation_matrix = self.calculate_correlation_matrix(stock_data)
        
        # 生成图表
        print("生成对比图表...")
        
        # 价格对比图
        price_fig = self.plot_price_comparison(stock_data, normalize=True)
        self.visualizer.save_chart(price_fig, 'stock_price_comparison.png')
        
        # 成交量对比图
        volume_fig = self.plot_volume_comparison(stock_data)
        self.visualizer.save_chart(volume_fig, 'stock_volume_comparison.png')
        
        # 表现指标对比图
        if not metrics_df.empty:
            performance_fig = self.plot_performance_comparison(metrics_df)
            self.visualizer.save_chart(performance_fig, 'stock_performance_comparison.png')
        
        # 相关性热图
        if not correlation_matrix.empty and len(correlation_matrix) > 1:
            correlation_fig = self.plot_correlation_heatmap(correlation_matrix)
            self.visualizer.save_chart(correlation_fig, 'stock_correlation_heatmap.png')
        
        plt.show()
        
        report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analyzed_stocks': list(stock_data.keys()),
            'data_points': {code: len(data) for code, data in stock_data.items()},
            'performance_metrics': metrics_df.to_dict('records') if not metrics_df.empty else [],
            'correlation_matrix': correlation_matrix.to_dict() if not correlation_matrix.empty else {},
            'charts_generated': [
                'stock_price_comparison.png',
                'stock_volume_comparison.png',
                'stock_performance_comparison.png',
                'stock_correlation_heatmap.png'
            ]
        }
        
        return report
    
    def print_comparison_summary(self, report: dict):
        """打印对比分析摘要"""
        if 'error' in report:
            print(f"错误: {report['error']}")
            return
        
        print("\n" + "=" * 60)
        print("股票对比分析摘要")
        print("=" * 60)
        
        print(f"分析时间: {report['analysis_date']}")
        print(f"分析股票: {', '.join(report['analyzed_stocks'])}")
        
        metrics = report['performance_metrics']
        if metrics:
            print(f"\n表现指标对比:")
            print("-" * 40)
            
            for metric in metrics:
                print(f"\n{metric['stock_code']}:")
                print(f"  总收益率: {metric['total_return_pct']:.2f}%")
                print(f"  年化波动率: {metric['volatility_pct']:.2f}%")
                print(f"  最大回撤: {metric['max_drawdown_pct']:.2f}%")
                print(f"  夏普比率: {metric['sharpe_ratio']:.3f}")
        
        correlation = report['correlation_matrix']
        if correlation and len(correlation) > 1:
            print(f"\n相关性分析:")
            print("-" * 40)
            
            # 找出最高和最低相关性（排除自相关）
            all_correlations = []
            for stock1 in correlation:
                for stock2 in correlation[stock1]:
                    if stock1 != stock2:
                        corr_value = correlation[stock1][stock2]
                        all_correlations.append((stock1, stock2, corr_value))
            
            if all_correlations:
                all_correlations.sort(key=lambda x: x[2], reverse=True)
                
                print(f"最高相关性: {all_correlations[0][0]} vs {all_correlations[0][1]} ({all_correlations[0][2]:.3f})")
                print(f"最低相关性: {all_correlations[-1][0]} vs {all_correlations[-1][1]} ({all_correlations[-1][2]:.3f})")
        
        print(f"\n图表文件已保存到 charts 目录:")
        for chart in report['charts_generated']:
            print(f"  - {chart}")


def demo_stock_comparison():
    """股票对比分析演示"""
    print("=" * 60)
    print("多股票对比分析演示")
    print("=" * 60)
    
    # 示例股票：银行股对比
    stock_codes = [
        "000001.SZ",  # 平安银行
        "600036.SH",  # 招商银行
        "601166.SH",  # 兴业银行
        "600000.SH"   # 浦发银行
    ]
    
    try:
        comparator = StockComparator()
        
        # 生成对比分析报告
        report = comparator.generate_comparison_report(stock_codes)
        
        # 打印摘要
        comparator.print_comparison_summary(report)
        
        print("\n" + "=" * 60)
        print("多股票对比分析演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行演示
    demo_stock_comparison()