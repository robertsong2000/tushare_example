"""
股票基本信息查询示例

演示如何使用 Tushare API 获取和分析股票基本信息。
"""

import pandas as pd
import logging
from typing import Optional, List, Dict, Any
from ..client import TushareClient, TushareClientError


class StockInfoAnalyzer:
    """股票信息分析器"""
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化股票信息分析器
        
        Args:
            client: Tushare 客户端实例
        """
        self.client = client or TushareClient()
        self.logger = logging.getLogger(__name__)
    
    def get_all_stocks(self, save_to_file: bool = True) -> pd.DataFrame:
        """
        获取所有上市股票基本信息
        
        Args:
            save_to_file: 是否保存到文件
            
        Returns:
            pd.DataFrame: 股票基本信息
        """
        try:
            self.logger.info("正在获取所有股票基本信息...")
            stocks = self.client.get_stock_basic(list_status='L')
            
            if not stocks.empty:
                # 添加一些有用的列
                stocks['list_years'] = pd.to_datetime('today').year - pd.to_datetime(stocks['list_date']).dt.year
                
                self.logger.info(f"成功获取 {len(stocks)} 只股票信息")
                
                if save_to_file:
                    self.client.save_data(stocks, 'all_stocks.csv')
                
                return stocks
            else:
                self.logger.warning("未获取到股票数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取股票信息失败: {str(e)}")
            return pd.DataFrame()
    
    def search_stocks(self, 
                     keyword: str, 
                     search_fields: List[str] = None) -> pd.DataFrame:
        """
        根据关键词搜索股票
        
        Args:
            keyword: 搜索关键词
            search_fields: 搜索字段列表，默认为 ['symbol', 'name', 'industry']
            
        Returns:
            pd.DataFrame: 匹配的股票信息
        """
        if search_fields is None:
            search_fields = ['symbol', 'name', 'industry']
        
        # 获取所有股票信息
        all_stocks = self.get_all_stocks(save_to_file=False)
        
        if all_stocks.empty:
            return pd.DataFrame()
        
        # 构建搜索条件
        search_condition = pd.Series([False] * len(all_stocks))
        
        for field in search_fields:
            if field in all_stocks.columns:
                field_condition = all_stocks[field].astype(str).str.contains(
                    keyword, case=False, na=False
                )
                search_condition = search_condition | field_condition
        
        result = all_stocks[search_condition]
        
        self.logger.info(f"关键词 '{keyword}' 搜索到 {len(result)} 只股票")
        
        return result
    
    def get_stocks_by_industry(self, industry: str) -> pd.DataFrame:
        """
        按行业获取股票
        
        Args:
            industry: 行业名称
            
        Returns:
            pd.DataFrame: 该行业的股票信息
        """
        return self.search_stocks(industry, ['industry'])
    
    def get_stocks_by_area(self, area: str) -> pd.DataFrame:
        """
        按地区获取股票
        
        Args:
            area: 地区名称
            
        Returns:
            pd.DataFrame: 该地区的股票信息
        """
        return self.search_stocks(area, ['area'])
    
    def get_stocks_by_market(self, market: str) -> pd.DataFrame:
        """
        按市场获取股票
        
        Args:
            market: 市场类型（主板、创业板、科创板等）
            
        Returns:
            pd.DataFrame: 该市场的股票信息
        """
        try:
            stocks = self.client.get_stock_basic(market=market)
            self.logger.info(f"获取到 {market} 市场 {len(stocks)} 只股票")
            return stocks
        except TushareClientError as e:
            self.logger.error(f"获取 {market} 市场股票失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_stock_distribution(self) -> Dict[str, Any]:
        """
        分析股票分布情况
        
        Returns:
            Dict: 分析结果
        """
        stocks = self.get_all_stocks(save_to_file=False)
        
        if stocks.empty:
            return {}
        
        analysis = {
            'total_count': len(stocks),
            'exchange_distribution': stocks['exchange'].value_counts().to_dict(),
            'market_distribution': stocks['market'].value_counts().to_dict(),
            'area_distribution': stocks['area'].value_counts().head(10).to_dict(),
            'industry_distribution': stocks['industry'].value_counts().head(10).to_dict(),
            'list_year_distribution': pd.to_datetime(stocks['list_date']).dt.year.value_counts().head(10).to_dict()
        }
        
        return analysis
    
    def get_recently_listed_stocks(self, days: int = 30) -> pd.DataFrame:
        """
        获取最近上市的股票
        
        Args:
            days: 最近多少天
            
        Returns:
            pd.DataFrame: 最近上市的股票
        """
        stocks = self.get_all_stocks(save_to_file=False)
        
        if stocks.empty:
            return pd.DataFrame()
        
        # 计算最近上市的股票
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        stocks['list_date'] = pd.to_datetime(stocks['list_date'])
        
        recent_stocks = stocks[stocks['list_date'] >= cutoff_date]
        recent_stocks = recent_stocks.sort_values('list_date', ascending=False)
        
        self.logger.info(f"最近 {days} 天上市了 {len(recent_stocks)} 只股票")
        
        return recent_stocks
    
    def print_stock_summary(self, stocks: pd.DataFrame):
        """
        打印股票信息摘要
        
        Args:
            stocks: 股票数据
        """
        if stocks.empty:
            print("没有股票数据")
            return
        
        print(f"\n股票信息摘要:")
        print(f"总数量: {len(stocks)}")
        print(f"\n交易所分布:")
        print(stocks['exchange'].value_counts())
        print(f"\n市场分布:")
        print(stocks['market'].value_counts())
        print(f"\n前10大行业:")
        print(stocks['industry'].value_counts().head(10))
        print(f"\n前10大地区:")
        print(stocks['area'].value_counts().head(10))


def demo_stock_basic_info():
    """股票基本信息查询演示"""
    print("=" * 60)
    print("Tushare 股票基本信息查询示例")
    print("=" * 60)
    
    try:
        # 创建分析器
        analyzer = StockInfoAnalyzer()
        
        # 1. 获取所有股票信息
        print("\n1. 获取所有股票基本信息")
        all_stocks = analyzer.get_all_stocks()
        analyzer.print_stock_summary(all_stocks)
        
        # 2. 搜索股票
        print("\n2. 搜索股票示例")
        
        # 搜索茅台相关股票
        maotai_stocks = analyzer.search_stocks("茅台")
        print(f"\n搜索 '茅台' 相关股票:")
        if not maotai_stocks.empty:
            print(maotai_stocks[['ts_code', 'symbol', 'name', 'industry', 'area']].to_string())
        
        # 搜索银行股
        bank_stocks = analyzer.get_stocks_by_industry("银行")
        print(f"\n银行行业股票 (前10只):")
        if not bank_stocks.empty:
            print(bank_stocks[['ts_code', 'symbol', 'name', 'area']].head(10).to_string())
        
        # 3. 按市场分类
        print("\n3. 按市场分类查询")
        
        # 科创板股票
        kcb_stocks = analyzer.get_stocks_by_market("科创板")
        print(f"\n科创板股票数量: {len(kcb_stocks)}")
        if not kcb_stocks.empty:
            print("科创板股票示例 (前5只):")
            print(kcb_stocks[['ts_code', 'symbol', 'name', 'industry']].head().to_string())
        
        # 4. 最近上市股票
        print("\n4. 最近上市股票")
        recent_stocks = analyzer.get_recently_listed_stocks(days=90)
        print(f"\n最近90天上市股票数量: {len(recent_stocks)}")
        if not recent_stocks.empty:
            print("最近上市股票示例 (前5只):")
            print(recent_stocks[['ts_code', 'symbol', 'name', 'list_date', 'industry']].head().to_string())
        
        # 5. 股票分布分析
        print("\n5. 股票分布分析")
        distribution = analyzer.analyze_stock_distribution()
        print(f"\n股票分布统计:")
        for key, value in distribution.items():
            if isinstance(value, dict) and key != 'total_count':
                print(f"\n{key}:")
                for k, v in list(value.items())[:5]:  # 只显示前5项
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        
        print("\n" + "=" * 60)
        print("演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    demo_stock_basic_info()