"""
股票新闻和公告分析示例

演示如何使用 Tushare API 获取股票相关新闻、公告和研报数据，
并进行文本分析、情感分析和可视化展示。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter
import re

from ..client import TushareClient, TushareClientError

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class NewsAnalyzer:
    """新闻和公告分析器"""
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化新闻分析器
        
        Args:
            client: Tushare 客户端实例
        """
        self.client = client or TushareClient()
        self.logger = logging.getLogger(__name__)
        
        # 情感分析关键词
        self.positive_keywords = [
            '增长', '上涨', '盈利', '利好', '突破', '创新', '合作', '收购', 
            '扩张', '业绩', '超预期', '看好', '推荐', '买入', '持有'
        ]
        
        self.negative_keywords = [
            '下跌', '亏损', '风险', '警告', '下调', '减持', '卖出', '退市',
            '调查', '违规', '处罚', '停牌', '延期', '取消', '失败'
        ]
    
    def get_stock_news(self, 
                      ts_code: Optional[str] = None,
                      days: int = 30,
                      limit: int = 100) -> pd.DataFrame:
        """
        获取股票相关新闻
        
        Args:
            ts_code: 股票代码，如果为None则获取全市场新闻
            days: 获取最近多少天的新闻
            limit: 新闻数量限制
            
        Returns:
            pd.DataFrame: 新闻数据
        """
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            self.logger.info(f"获取 {start_date} 到 {end_date} 的新闻数据")
            
            # 获取新闻数据
            news_data = self.client.get_news(
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            if news_data.empty:
                self.logger.warning("未获取到新闻数据")
                return pd.DataFrame()
            
            # 如果指定了股票代码，过滤相关新闻
            if ts_code:
                # 提取股票简称用于匹配
                stock_info = self.client.get_stock_basic(list_status='L')
                if not stock_info.empty:
                    stock_name = stock_info[stock_info['ts_code'] == ts_code]['name'].iloc[0] if len(stock_info[stock_info['ts_code'] == ts_code]) > 0 else None
                    if stock_name:
                        # 过滤包含股票名称的新闻
                        news_data = news_data[news_data['title'].str.contains(stock_name, na=False) | 
                                            news_data['content'].str.contains(stock_name, na=False)]
            
            self.logger.info(f"成功获取 {len(news_data)} 条新闻")
            return news_data
            
        except Exception as e:
            self.logger.error(f"获取新闻数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_announcements(self,
                              ts_code: str,
                              days: int = 30,
                              limit: int = 100) -> pd.DataFrame:
        """
        获取股票公告数据
        
        Args:
            ts_code: 股票代码
            days: 获取最近多少天的公告
            limit: 公告数量限制
            
        Returns:
            pd.DataFrame: 公告数据
        """
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            self.logger.info(f"获取 {ts_code} 在 {start_date} 到 {end_date} 的公告数据")
            
            # 获取公告数据
            announcement_data = self.client.get_announcement(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            if announcement_data.empty:
                self.logger.warning(f"未获取到 {ts_code} 的公告数据")
            else:
                self.logger.info(f"成功获取 {ts_code} 的 {len(announcement_data)} 条公告")
            
            return announcement_data
            
        except Exception as e:
            self.logger.error(f"获取公告数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_research_reports(self,
                           ts_code: Optional[str] = None,
                           days: int = 30,
                           limit: int = 50) -> pd.DataFrame:
        """
        获取研报数据
        
        Args:
            ts_code: 股票代码
            days: 获取最近多少天的研报
            limit: 研报数量限制
            
        Returns:
            pd.DataFrame: 研报数据
        """
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            self.logger.info(f"获取研报数据: {start_date} 到 {end_date}")
            
            # 获取研报数据
            report_data = self.client.get_report(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            if report_data.empty:
                self.logger.warning("未获取到研报数据")
            else:
                self.logger.info(f"成功获取 {len(report_data)} 份研报")
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"获取研报数据失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_sentiment(self, text_data: pd.Series) -> pd.DataFrame:
        """
        简单的情感分析
        
        Args:
            text_data: 文本数据序列
            
        Returns:
            pd.DataFrame: 情感分析结果
        """
        sentiment_scores = []
        
        for text in text_data:
            if pd.isna(text):
                sentiment_scores.append({'positive': 0, 'negative': 0, 'neutral': 1})
                continue
                
            text = str(text).lower()
            
            # 计算正面关键词数量
            positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
            
            # 计算负面关键词数量
            negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
            
            # 计算情感得分
            total_keywords = positive_count + negative_count
            if total_keywords == 0:
                sentiment = {'positive': 0, 'negative': 0, 'neutral': 1}
            else:
                sentiment = {
                    'positive': positive_count / total_keywords,
                    'negative': negative_count / total_keywords,
                    'neutral': 0
                }
                sentiment['neutral'] = 1 - sentiment['positive'] - sentiment['negative']
            
            sentiment_scores.append(sentiment)
        
        return pd.DataFrame(sentiment_scores)
    
    def analyze_news_frequency(self, news_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析新闻频率和热度
        
        Args:
            news_data: 新闻数据
            
        Returns:
            Dict: 分析结果
        """
        if news_data.empty:
            return {}
        
        try:
            # 按日期统计新闻数量
            if 'datetime' in news_data.columns:
                news_data['date'] = pd.to_datetime(news_data['datetime']).dt.date
            elif 'pub_time' in news_data.columns:
                news_data['date'] = pd.to_datetime(news_data['pub_time']).dt.date
            else:
                self.logger.warning("未找到日期列，无法进行时间序列分析")
                return {}
            
            daily_counts = news_data.groupby('date').size().to_dict()
            
            # 分析新闻来源
            source_counts = {}
            if 'channels' in news_data.columns:
                source_counts = news_data['channels'].value_counts().to_dict()
            elif 'src' in news_data.columns:
                source_counts = news_data['src'].value_counts().to_dict()
            
            # 关键词分析
            all_titles = ' '.join(news_data['title'].fillna('').astype(str))
            # 简单的关键词提取（实际应用中可能需要更复杂的NLP处理）
            words = re.findall(r'[\u4e00-\u9fff]+', all_titles)
            word_freq = Counter([word for word in words if len(word) > 1])
            
            return {
                'total_news': len(news_data),
                'daily_counts': daily_counts,
                'source_counts': source_counts,
                'top_keywords': dict(word_freq.most_common(10)),
                'date_range': {
                    'start': min(daily_counts.keys()) if daily_counts else None,
                    'end': max(daily_counts.keys()) if daily_counts else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"新闻频率分析失败: {str(e)}")
            return {}
    
    def generate_news_report(self, 
                           ts_code: Optional[str] = None,
                           days: int = 30) -> Dict[str, Any]:
        """
        生成综合新闻分析报告
        
        Args:
            ts_code: 股票代码，如果为None则分析全市场
            days: 分析最近多少天
            
        Returns:
            Dict: 综合分析报告
        """
        self.logger.info(f"生成新闻分析报告: {ts_code or '全市场'}")
        
        report = {
            'stock_code': ts_code,
            'analysis_period': days,
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 获取新闻数据
            news_data = self.get_stock_news(ts_code, days)
            report['news_analysis'] = self.analyze_news_frequency(news_data)
            
            # 新闻情感分析
            if not news_data.empty and 'title' in news_data.columns:
                sentiment_result = self.analyze_sentiment(news_data['title'])
                report['sentiment_analysis'] = {
                    'avg_positive': sentiment_result['positive'].mean(),
                    'avg_negative': sentiment_result['negative'].mean(),
                    'avg_neutral': sentiment_result['neutral'].mean(),
                    'sentiment_distribution': sentiment_result.mean().to_dict()
                }
            
            # 如果指定了股票代码，获取公告和研报
            if ts_code:
                # 获取公告数据
                announcements = self.get_stock_announcements(ts_code, days)
                report['announcements'] = {
                    'total_count': len(announcements),
                    'recent_announcements': announcements.head().to_dict('records') if not announcements.empty else []
                }
                
                # 获取研报数据
                reports = self.get_research_reports(ts_code, days)
                report['research_reports'] = {
                    'total_count': len(reports),
                    'recent_reports': reports.head().to_dict('records') if not reports.empty else []
                }
            
            self.logger.info("新闻分析报告生成完成")
            return report
            
        except Exception as e:
            self.logger.error(f"生成新闻报告失败: {str(e)}")
            report['error'] = str(e)
            return report


def demo_news_analysis():
    """新闻分析演示"""
    print("=" * 60)
    print("股票新闻和公告分析演示")
    print("=" * 60)
    
    try:
        analyzer = NewsAnalyzer()
        
        # 1. 全市场新闻分析
        print("\n1. 全市场新闻分析")
        market_report = analyzer.generate_news_report(days=7)
        
        if 'news_analysis' in market_report:
            news_analysis = market_report['news_analysis']
            print(f"最近7天新闻总数: {news_analysis.get('total_news', 0)}")
            
            if 'top_keywords' in news_analysis:
                print("热门关键词:")
                for word, count in list(news_analysis['top_keywords'].items())[:5]:
                    print(f"  {word}: {count}")
        
        # 2. 特定股票新闻分析
        print("\n2. 特定股票新闻分析 (平安银行)")
        stock_code = "000001.SZ"
        stock_report = analyzer.generate_news_report(stock_code, days=30)
        
        print(f"股票代码: {stock_report['stock_code']}")
        
        if 'sentiment_analysis' in stock_report:
            sentiment = stock_report['sentiment_analysis']
            print(f"情感分析:")
            print(f"  正面情感: {sentiment['avg_positive']:.2%}")
            print(f"  负面情感: {sentiment['avg_negative']:.2%}")
            print(f"  中性情感: {sentiment['avg_neutral']:.2%}")
        
        if 'announcements' in stock_report:
            ann_count = stock_report['announcements']['total_count']
            print(f"最近30天公告数量: {ann_count}")
        
        if 'research_reports' in stock_report:
            report_count = stock_report['research_reports']['total_count']
            print(f"最近30天研报数量: {report_count}")
        
        # 3. 展示最新新闻
        print("\n3. 最新市场新闻 (前5条)")
        latest_news = analyzer.get_stock_news(days=3, limit=5)
        
        if not latest_news.empty:
            for i, row in latest_news.head().iterrows():
                title = row.get('title', '无标题')
                pub_time = row.get('pub_time', row.get('datetime', '未知时间'))
                print(f"  [{pub_time}] {title}")
        else:
            print("  暂无新闻数据")
        
        print("\n" + "=" * 60)
        print("新闻分析演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    demo_news_analysis()