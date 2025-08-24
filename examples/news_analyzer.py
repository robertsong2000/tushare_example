#!/usr/bin/env python3
"""
股票新闻分析演示

演示如何使用 Tushare API 获取和分析股票新闻、公告和研报数据。
包括新闻情感分析、热度统计、可视化展示等功能。
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tushare_examples.examples.news_analysis import NewsAnalyzer
from src.tushare_examples.visualizer import StockVisualizer
from src.tushare_examples.client import TushareClient


class NewsAnalysisDemo:
    """新闻分析演示类"""
    
    def __init__(self):
        """初始化演示器"""
        self.analyzer = NewsAnalyzer()
        self.visualizer = StockVisualizer()
        self.logger = logging.getLogger(__name__)
    
    def demo_market_news_analysis(self):
        """演示全市场新闻分析"""
        print("\n" + "="*60)
        print("全市场新闻分析演示")
        print("="*60)
        
        try:
            # 获取最近7天的市场新闻
            print("正在获取最近7天的市场新闻...")
            market_report = self.analyzer.generate_news_report(days=7)
            
            if 'news_analysis' in market_report:
                news_stats = market_report['news_analysis']
                print(f"✅ 新闻分析完成")
                print(f"   - 新闻总数: {news_stats.get('total_news', 0)}")
                
                # 显示热门关键词
                if 'top_keywords' in news_stats:
                    print(f"   - 热门关键词:")
                    for i, (word, count) in enumerate(list(news_stats['top_keywords'].items())[:5], 1):
                        print(f"     {i}. {word}: {count}次")
                
                # 显示新闻来源分布
                if 'source_counts' in news_stats:
                    print(f"   - 主要新闻来源:")
                    for i, (source, count) in enumerate(list(news_stats['source_counts'].items())[:3], 1):
                        print(f"     {i}. {source}: {count}篇")
                
                # 生成可视化图表
                if news_stats.get('daily_counts'):
                    print("\n正在生成市场新闻可视化图表...")
                    
                    # 新闻频率图
                    freq_fig = self.visualizer.plot_news_frequency(
                        news_stats['daily_counts'],
                        title="市场新闻发布频率"
                    )
                    self.visualizer.save_chart(freq_fig, "market_news_frequency.png")
                    
                    # 新闻来源图
                    if news_stats.get('source_counts'):
                        source_fig = self.visualizer.plot_news_sources(
                            news_stats['source_counts'],
                            title="市场新闻来源分布"
                        )
                        self.visualizer.save_chart(source_fig, "market_news_sources.png")
                    
                    # 关键词图
                    if news_stats.get('top_keywords'):
                        keyword_fig = self.visualizer.plot_keywords_cloud(
                            news_stats['top_keywords'],
                            title="市场热门关键词"
                        )
                        self.visualizer.save_chart(keyword_fig, "market_keywords.png")
                    
                    print("✅ 图表已保存到 charts 目录")
                
            else:
                print("❌ 暂无新闻数据")
                
        except Exception as e:
            print(f"❌ 市场新闻分析失败: {str(e)}")
    
    def demo_stock_news_analysis(self, stock_codes: list):
        """演示个股新闻分析"""
        print("\n" + "="*60)
        print("个股新闻分析演示")
        print("="*60)
        
        for stock_code in stock_codes:
            print(f"\n分析股票: {stock_code}")
            print("-" * 40)
            
            try:
                # 生成个股新闻报告
                stock_report = self.analyzer.generate_news_report(stock_code, days=30)
                
                print(f"📊 {stock_code} 新闻分析结果:")
                
                # 新闻统计
                if 'news_analysis' in stock_report:
                    news_stats = stock_report['news_analysis']
                    total_news = news_stats.get('total_news', 0)
                    print(f"   - 相关新闻数量: {total_news}")
                    
                    if total_news > 0:
                        # 显示关键词
                        if 'top_keywords' in news_stats:
                            keywords = list(news_stats['top_keywords'].items())[:3]
                            print(f"   - 关键词: {', '.join([word for word, _ in keywords])}")
                
                # 情感分析
                if 'sentiment_analysis' in stock_report:
                    sentiment = stock_report['sentiment_analysis']
                    positive_pct = sentiment['avg_positive'] * 100
                    negative_pct = sentiment['avg_negative'] * 100
                    neutral_pct = sentiment['avg_neutral'] * 100
                    
                    print(f"   - 情感分析:")
                    print(f"     正面: {positive_pct:.1f}%")
                    print(f"     负面: {negative_pct:.1f}%")
                    print(f"     中性: {neutral_pct:.1f}%")
                    
                    # 生成情感分析图表
                    sentiment_data = pd.DataFrame([sentiment['sentiment_distribution']])
                    sentiment_fig = self.visualizer.plot_news_sentiment(
                        sentiment_data,
                        title=f"{stock_code} 新闻情感分析"
                    )
                    chart_name = f"{stock_code.replace('.', '_')}_sentiment.png"
                    self.visualizer.save_chart(sentiment_fig, chart_name)
                
                # 公告信息
                if 'announcements' in stock_report:
                    ann_count = stock_report['announcements']['total_count']
                    print(f"   - 最近30天公告: {ann_count}条")
                
                # 研报信息
                if 'research_reports' in stock_report:
                    report_count = stock_report['research_reports']['total_count']
                    print(f"   - 最近30天研报: {report_count}份")
                
                # 生成综合仪表板
                if any(key in stock_report for key in ['news_analysis', 'sentiment_analysis']):
                    dashboard_name = f"{stock_code.replace('.', '_')}_dashboard.png"
                    dashboard_fig = self.visualizer.create_news_dashboard(
                        stock_report,
                        save_path=dashboard_name
                    )
                    print(f"   - 已生成仪表板: {dashboard_name}")
                
            except Exception as e:
                print(f"❌ {stock_code} 分析失败: {str(e)}")
    
    def demo_news_sentiment_comparison(self, stock_codes: list):
        """演示多股票新闻情感对比"""
        print("\n" + "="*60)
        print("多股票新闻情感对比")
        print("="*60)
        
        sentiment_data = []
        
        for stock_code in stock_codes:
            try:
                print(f"正在分析 {stock_code} 的新闻情感...")
                
                # 获取新闻数据
                news_data = self.analyzer.get_stock_news(stock_code, days=15, limit=50)
                
                if not news_data.empty and 'title' in news_data.columns:
                    # 情感分析
                    sentiment_result = self.analyzer.analyze_sentiment(news_data['title'])
                    avg_sentiment = sentiment_result.mean()
                    
                    sentiment_data.append({
                        'stock_code': stock_code,
                        'positive': avg_sentiment['positive'],
                        'negative': avg_sentiment['negative'],
                        'neutral': avg_sentiment['neutral'],
                        'news_count': len(news_data)
                    })
                else:
                    print(f"   {stock_code}: 暂无相关新闻")
                    
            except Exception as e:
                print(f"   {stock_code}: 分析失败 - {str(e)}")
        
        if sentiment_data:
            # 创建对比表格
            comparison_df = pd.DataFrame(sentiment_data)
            print(f"\n📊 情感对比结果:")
            print(comparison_df.to_string(index=False, float_format='%.3f'))
            
            # 生成对比图表
            try:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # 情感分布对比
                x = np.arange(len(comparison_df))
                width = 0.25
                
                ax1.bar(x - width, comparison_df['positive'], width, label='正面', color='green', alpha=0.7)
                ax1.bar(x, comparison_df['negative'], width, label='负面', color='red', alpha=0.7)
                ax1.bar(x + width, comparison_df['neutral'], width, label='中性', color='gray', alpha=0.7)
                
                ax1.set_xlabel('股票代码')
                ax1.set_ylabel('情感得分')
                ax1.set_title('多股票新闻情感对比')
                ax1.set_xticks(x)
                ax1.set_xticklabels(comparison_df['stock_code'], rotation=45)
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # 新闻数量对比
                ax2.bar(comparison_df['stock_code'], comparison_df['news_count'], 
                       color='skyblue', alpha=0.7)
                ax2.set_xlabel('股票代码')
                ax2.set_ylabel('新闻数量')
                ax2.set_title('相关新闻数量对比')
                plt.setp(ax2.get_xticklabels(), rotation=45)
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                self.visualizer.save_chart(fig, "sentiment_comparison.png")
                print("✅ 对比图表已保存: sentiment_comparison.png")
                
            except Exception as e:
                print(f"❌ 生成对比图表失败: {str(e)}")
        else:
            print("❌ 没有足够的数据进行对比分析")
    
    def demo_latest_announcements(self, stock_codes: list):
        """演示最新公告获取"""
        print("\n" + "="*60)
        print("最新公告获取演示")
        print("="*60)
        
        for stock_code in stock_codes:
            try:
                print(f"\n📢 {stock_code} 最新公告:")
                
                # 获取最近15天的公告
                announcements = self.analyzer.get_stock_announcements(stock_code, days=15, limit=5)
                
                if not announcements.empty:
                    print(f"   最近15天共有 {len(announcements)} 条公告")
                    
                    # 显示最新的3条公告
                    for i, (_, ann) in enumerate(announcements.head(3).iterrows(), 1):
                        ann_date = ann.get('ann_date', '未知日期')
                        title = ann.get('title', '无标题')
                        ann_type = ann.get('ann_type', '未知类型')
                        print(f"   {i}. [{ann_date}] {title} ({ann_type})")
                else:
                    print(f"   最近15天暂无公告")
                    
            except Exception as e:
                print(f"   {stock_code}: 获取公告失败 - {str(e)}")


def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 股票新闻分析演示系统")
    print("=" * 60)
    
    # 创建演示器
    demo = NewsAnalysisDemo()
    
    # 演示股票列表
    demo_stocks = [
        "000001.SZ",  # 平安银行
        "600519.SH",  # 贵州茅台
        "000002.SZ",  # 万科A
    ]
    
    try:
        # 1. 全市场新闻分析
        demo.demo_market_news_analysis()
        
        # 2. 个股新闻分析
        demo.demo_stock_news_analysis(demo_stocks)
        
        # 3. 情感对比分析
        demo.demo_news_sentiment_comparison(demo_stocks)
        
        # 4. 最新公告演示
        demo.demo_latest_announcements(demo_stocks)
        
        print("\n" + "="*60)
        print("🎉 所有演示完成！")
        print("📁 图表文件已保存到 charts 目录")
        print("📊 可查看生成的新闻分析图表和仪表板")
        
    except KeyboardInterrupt:
        print("\n\n用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        logging.error(f"演示失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()