#!/usr/bin/env python3
"""
股票筛选器示例

演示如何使用 Tushare API 构建股票筛选器，根据各种条件筛选出符合要求的股票。
包括基本面筛选、技术面筛选、综合评分等功能。
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tushare_examples.client import TushareClient
from src.tushare_examples.examples.stock_basic import StockInfoAnalyzer
from src.tushare_examples.examples.kline_analysis import KLineAnalyzer
from src.tushare_examples.examples.financial_analysis import FinancialAnalyzer
from src.tushare_examples.indicators import TechnicalIndicators


class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        """初始化筛选器"""
        self.client = TushareClient()
        self.stock_analyzer = StockInfoAnalyzer(self.client)
        self.kline_analyzer = KLineAnalyzer(self.client)
        self.financial_analyzer = FinancialAnalyzer(self.client)
        self.tech_calculator = TechnicalIndicators()
        self.logger = logging.getLogger(__name__)
    
    def screen_by_basic_criteria(self, 
                                min_market_cap: float = 50,  # 亿元
                                max_pe_ratio: float = 30,
                                min_years_listed: int = 3,
                                industries: list = None) -> pd.DataFrame:
        """
        基本面筛选
        
        Args:
            min_market_cap: 最小市值（亿元）
            max_pe_ratio: 最大市盈率
            min_years_listed: 最小上市年数
            industries: 行业列表
            
        Returns:
            pd.DataFrame: 筛选结果
        """
        print(f"开始基本面筛选...")
        print(f"筛选条件: 市值>={min_market_cap}亿, PE<={max_pe_ratio}, 上市>={min_years_listed}年")
        
        # 获取所有股票基本信息
        all_stocks = self.stock_analyzer.get_all_stocks(save_to_file=False)
        
        if all_stocks.empty:
            print("无法获取股票基本信息")
            return pd.DataFrame()
        
        # 应用筛选条件
        filtered_stocks = all_stocks.copy()
        
        # 上市年数筛选
        current_year = datetime.now().year
        filtered_stocks['list_year'] = pd.to_datetime(filtered_stocks['list_date']).dt.year
        filtered_stocks['years_listed'] = current_year - filtered_stocks['list_year']
        filtered_stocks = filtered_stocks[filtered_stocks['years_listed'] >= min_years_listed]
        
        # 行业筛选
        if industries:
            filtered_stocks = filtered_stocks[filtered_stocks['industry'].isin(industries)]
        
        # 排除ST股票
        filtered_stocks = filtered_stocks[~filtered_stocks['name'].str.contains('ST', na=False)]
        
        print(f"基本面筛选完成，符合条件的股票: {len(filtered_stocks)} 只")
        return filtered_stocks
    
    def screen_by_technical_criteria(self, 
                                   stocks: pd.DataFrame,
                                   rsi_range: tuple = (30, 70),
                                   ma_trend: str = 'bullish',  # 'bullish', 'bearish', 'any'
                                   volume_increase: bool = True) -> pd.DataFrame:
        """
        技术面筛选
        
        Args:
            stocks: 待筛选的股票列表
            rsi_range: RSI范围
            ma_trend: 移动平均线趋势
            volume_increase: 是否要求成交量放大
            
        Returns:
            pd.DataFrame: 筛选结果
        """
        print(f"开始技术面筛选...")
        print(f"筛选条件: RSI在{rsi_range}范围, MA趋势{ma_trend}, 成交量{'放大' if volume_increase else '不限'}")
        
        results = []
        
        for i, stock in stocks.iterrows():
            ts_code = stock['ts_code']
            
            try:
                # 获取最近60天的K线数据
                kline_data = self.kline_analyzer.get_kline_data(
                    ts_code=ts_code,
                    start_date=(datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
                )
                
                if kline_data.empty or len(kline_data) < 20:
                    continue
                
                # 获取最新数据
                latest = kline_data.iloc[-1]
                
                # RSI筛选
                if 'RSI' in kline_data.columns:
                    rsi_value = latest['RSI']
                    if not (rsi_range[0] <= rsi_value <= rsi_range[1]):
                        continue
                
                # MA趋势筛选
                if ma_trend != 'any' and all(col in kline_data.columns for col in ['MA5', 'MA20']):
                    ma5 = latest['MA5']
                    ma20 = latest['MA20']
                    close_price = latest['close']
                    
                    if ma_trend == 'bullish':
                        if not (close_price > ma5 > ma20):
                            continue
                    elif ma_trend == 'bearish':
                        if not (close_price < ma5 < ma20):
                            continue
                
                # 成交量筛选
                if volume_increase and len(kline_data) >= 5:
                    recent_volume = kline_data.tail(5)['vol'].mean()
                    previous_volume = kline_data.iloc[-10:-5]['vol'].mean()
                    
                    if recent_volume <= previous_volume * 1.2:  # 成交量没有放大20%以上
                        continue
                
                # 添加技术指标到结果
                stock_result = stock.copy()
                stock_result['current_price'] = latest['close']
                stock_result['rsi'] = latest.get('RSI', np.nan)
                stock_result['ma5'] = latest.get('MA5', np.nan)
                stock_result['ma20'] = latest.get('MA20', np.nan)
                
                results.append(stock_result)
                
            except Exception as e:
                self.logger.warning(f"分析股票 {ts_code} 时出错: {str(e)}")
                continue
        
        result_df = pd.DataFrame(results) if results else pd.DataFrame()
        print(f"技术面筛选完成，符合条件的股票: {len(result_df)} 只")
        
        return result_df
    
    def calculate_composite_score(self, stocks: pd.DataFrame) -> pd.DataFrame:
        """
        计算综合评分
        
        Args:
            stocks: 股票数据
            
        Returns:
            pd.DataFrame: 包含评分的股票数据
        """
        print("开始计算综合评分...")
        
        if stocks.empty:
            return stocks
        
        scored_stocks = stocks.copy()
        scored_stocks['composite_score'] = 0.0
        scored_stocks['score_details'] = ''
        
        for i, stock in scored_stocks.iterrows():
            ts_code = stock['ts_code']
            score = 0.0
            details = []
            
            try:
                # 基础分数
                score += 1.0
                details.append("基础分:1")
                
                # RSI评分 (0-2分)
                if not pd.isna(stock.get('rsi')):
                    rsi = stock['rsi']
                    if 40 <= rsi <= 60:
                        rsi_score = 2.0
                    elif 30 <= rsi <= 70:
                        rsi_score = 1.0
                    else:
                        rsi_score = 0.0
                    
                    score += rsi_score
                    details.append(f"RSI:{rsi_score}")
                
                # MA趋势评分 (0-2分)
                if not pd.isna(stock.get('ma5')) and not pd.isna(stock.get('ma20')):
                    current_price = stock['current_price']
                    ma5 = stock['ma5']
                    ma20 = stock['ma20']
                    
                    if current_price > ma5 > ma20:
                        ma_score = 2.0
                    elif current_price > ma20:
                        ma_score = 1.0
                    else:
                        ma_score = 0.0
                    
                    score += ma_score
                    details.append(f"MA:{ma_score}")
                
                # 上市时间评分 (0-1分)
                years_listed = stock.get('years_listed', 0)
                if years_listed >= 10:
                    time_score = 1.0
                elif years_listed >= 5:
                    time_score = 0.5
                else:
                    time_score = 0.0
                
                score += time_score
                details.append(f"上市:{time_score}")
                
                scored_stocks.loc[i, 'composite_score'] = score
                scored_stocks.loc[i, 'score_details'] = ', '.join(details)
                
            except Exception as e:
                self.logger.warning(f"计算股票 {ts_code} 评分时出错: {str(e)}")
                continue
        
        # 按评分排序
        scored_stocks = scored_stocks.sort_values('composite_score', ascending=False)
        
        print(f"综合评分完成，平均评分: {scored_stocks['composite_score'].mean():.2f}")
        return scored_stocks
    
    def run_comprehensive_screening(self, 
                                  top_n: int = 20,
                                  industries: list = None,
                                  save_results: bool = True) -> pd.DataFrame:
        """
        运行综合筛选
        
        Args:
            top_n: 返回前N只股票
            industries: 行业筛选列表
            save_results: 是否保存结果
            
        Returns:
            pd.DataFrame: 筛选结果
        """
        print("=" * 60)
        print("开始综合股票筛选")
        print("=" * 60)
        
        # 第一步：基本面筛选
        basic_filtered = self.screen_by_basic_criteria(
            min_market_cap=50,
            max_pe_ratio=50,
            min_years_listed=3,
            industries=industries
        )
        
        if basic_filtered.empty:
            print("基本面筛选后无符合条件的股票")
            return pd.DataFrame()
        
        # 第二步：技术面筛选
        tech_filtered = self.screen_by_technical_criteria(
            stocks=basic_filtered.head(100),  # 先取前100只，避免API调用过多
            rsi_range=(30, 70),
            ma_trend='bullish',
            volume_increase=True
        )
        
        if tech_filtered.empty:
            print("技术面筛选后无符合条件的股票")
            return pd.DataFrame()
        
        # 第三步：综合评分
        final_results = self.calculate_composite_score(tech_filtered)
        
        # 取前N只
        top_stocks = final_results.head(top_n)
        
        # 保存结果
        if save_results and not top_stocks.empty:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'stock_screening_results_{timestamp}.csv'
            self.client.save_data(top_stocks, filename)
            print(f"筛选结果已保存: {filename}")
        
        return top_stocks
    
    def print_screening_results(self, results: pd.DataFrame):
        """打印筛选结果"""
        if results.empty:
            print("无筛选结果")
            return
        
        print(f"\n筛选结果 (共 {len(results)} 只股票):")
        print("=" * 100)
        
        display_columns = [
            'ts_code', 'name', 'industry', 'area', 
            'current_price', 'composite_score', 'score_details'
        ]
        
        # 只显示存在的列
        available_columns = [col for col in display_columns if col in results.columns]
        
        for i, stock in results.iterrows():
            print(f"\n{i+1}. {stock['name']} ({stock['ts_code']})")
            print(f"   行业: {stock.get('industry', 'N/A')}")
            print(f"   地区: {stock.get('area', 'N/A')}")
            if 'current_price' in stock:
                print(f"   当前价格: {stock['current_price']:.2f}")
            if 'composite_score' in stock:
                print(f"   综合评分: {stock['composite_score']:.2f}")
            if 'score_details' in stock:
                print(f"   评分详情: {stock['score_details']}")


def demo_stock_screening():
    """股票筛选演示"""
    print("=" * 60)
    print("股票筛选器演示")
    print("=" * 60)
    
    try:
        screener = StockScreener()
        
        # 运行综合筛选
        results = screener.run_comprehensive_screening(
            top_n=10,
            industries=['银行', '保险', '证券', '房地产', '白酒', '医药'],
            save_results=True
        )
        
        # 显示结果
        screener.print_screening_results(results)
        
        print("\n" + "=" * 60)
        print("股票筛选演示完成！")
        
    except Exception as e:
        print(f"筛选过程中出现错误: {str(e)}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行演示
    demo_stock_screening()