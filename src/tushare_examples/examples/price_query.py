"""
股价查询模块

提供股票实时价格查询、历史价格分析和价格变化监控功能。
支持单只股票和批量股票的价格查询。
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import time

from ..client import TushareClient, TushareClientError


class StockPriceAnalyzer:
    """股价分析器"""
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化股价分析器
        
        Args:
            client: Tushare 客户端实例
        """
        self.client = client or TushareClient()
        self.logger = logging.getLogger(__name__)
    
    def get_current_price(self, ts_code: str) -> Dict[str, Any]:
        """
        获取股票当前价格信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            Dict: 股价信息字典
        """
        try:
            self.logger.info(f"正在获取 {ts_code} 的当前价格信息...")
            
            # 获取股票实时信息
            stock_info = self.client.get_stock_realtime_info(ts_code)
            
            if 'error' in stock_info:
                self.logger.error(f"获取股价失败: {stock_info['error']}")
                return stock_info
            
            # 格式化数据
            formatted_info = self._format_price_info(stock_info)
            
            self.logger.info(f"成功获取 {ts_code} 的价格信息")
            return formatted_info
            
        except Exception as e:
            error_msg = f"获取 {ts_code} 价格信息失败: {str(e)}"
            self.logger.error(error_msg)
            return {'error': error_msg}
    
    def get_multiple_prices(self, ts_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取多只股票的价格信息
        
        Args:
            ts_codes: 股票代码列表
            
        Returns:
            Dict: 股票代码到价格信息的映射
        """
        results = {}
        
        for ts_code in ts_codes:
            self.logger.info(f"获取 {ts_code} 价格信息...")
            results[ts_code] = self.get_current_price(ts_code)
            
            # 避免API调用过于频繁
            time.sleep(0.2)
        
        return results
    
    def get_price_history(self,
                         ts_code: str,
                         days: int = 30) -> pd.DataFrame:
        """
        获取股票历史价格数据
        
        Args:
            ts_code: 股票代码
            days: 历史天数
            
        Returns:
            pd.DataFrame: 历史价格数据
        """
        try:
            self.logger.info(f"获取 {ts_code} 最近 {days} 天的历史价格...")
            
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            # 获取历史数据
            history_data = self.client.get_daily_data(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if history_data.empty:
                self.logger.warning(f"未获取到 {ts_code} 的历史数据")
                return pd.DataFrame()
            
            # 按日期排序
            history_data = history_data.sort_values('trade_date')
            
            # 计算技术指标
            history_data = self._calculate_price_indicators(history_data)
            
            self.logger.info(f"成功获取 {ts_code} 的 {len(history_data)} 天历史数据")
            return history_data
            
        except Exception as e:
            self.logger.error(f"获取历史价格失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_price_trend(self,
                           ts_code: str,
                           days: int = 30) -> Dict[str, Any]:
        """
        分析股价趋势
        
        Args:
            ts_code: 股票代码
            days: 分析天数
            
        Returns:
            Dict: 趋势分析结果
        """
        try:
            # 获取历史数据
            history_data = self.get_price_history(ts_code, days)
            
            if history_data.empty:
                return {'error': '无法获取历史数据进行趋势分析'}
            
            # 获取当前价格
            current_info = self.get_current_price(ts_code)
            
            if 'error' in current_info:
                return current_info
            
            # 计算趋势指标
            analysis = {
                'ts_code': ts_code,
                'name': current_info.get('name', 'N/A'),
                'current_price': current_info.get('close', 0),
                'analysis_period': days,
                'data_points': len(history_data)
            }
            
            if len(history_data) >= 2:
                # 价格变化分析
                first_price = history_data.iloc[0]['close']
                last_price = history_data.iloc[-1]['close']
                period_change = ((last_price - first_price) / first_price) * 100
                
                # 最高最低价
                max_price = history_data['high'].max()
                min_price = history_data['low'].min()
                
                # 平均价格和波动率
                avg_price = history_data['close'].mean()
                price_volatility = history_data['close'].std()
                
                # 成交量分析
                avg_volume = history_data['vol'].mean()
                
                analysis.update({
                    'period_change_pct': round(period_change, 2),
                    'max_price': max_price,
                    'min_price': min_price,
                    'avg_price': round(avg_price, 2),
                    'volatility': round(price_volatility, 2),
                    'avg_volume': round(avg_volume, 0),
                    'trend_direction': 'up' if period_change > 0 else 'down' if period_change < 0 else 'flat'
                })
                
                # 技术指标分析
                if 'ma5' in history_data.columns:
                    current_ma5 = history_data.iloc[-1]['ma5']
                    current_ma20 = history_data.iloc[-1].get('ma20', 0)
                    
                    analysis.update({
                        'ma5': round(current_ma5, 2),
                        'ma20': round(current_ma20, 2) if current_ma20 else None,
                        'price_vs_ma5': 'above' if analysis['current_price'] > current_ma5 else 'below',
                        'price_vs_ma20': 'above' if current_ma20 and analysis['current_price'] > current_ma20 else 'below' if current_ma20 else None
                    })
            
            return analysis
            
        except Exception as e:
            error_msg = f"趋势分析失败: {str(e)}"
            self.logger.error(error_msg)
            return {'error': error_msg}
    
    def _format_price_info(self, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化股价信息显示
        
        Args:
            stock_info: 原始股票信息
            
        Returns:
            Dict: 格式化后的信息
        """
        formatted = {
            'ts_code': stock_info.get('ts_code', 'N/A'),
            'name': stock_info.get('name', 'N/A'),
            'trade_date': stock_info.get('trade_date', 'N/A'),
            'current_price': stock_info.get('close', 0),
            'open_price': stock_info.get('open', 0),
            'high_price': stock_info.get('high', 0),
            'low_price': stock_info.get('low', 0),
            'pre_close': stock_info.get('pre_close', 0),
            'volume': stock_info.get('vol', 0),
            'amount': stock_info.get('amount', 0),
            'industry': stock_info.get('industry', 'N/A'),
            'area': stock_info.get('area', 'N/A'),
            'market': stock_info.get('market', 'N/A')
        }
        
        # 计算涨跌幅和涨跌额
        if formatted['pre_close'] and formatted['pre_close'] != 0:
            price_change = formatted['current_price'] - formatted['pre_close']
            pct_change = (price_change / formatted['pre_close']) * 100
            
            formatted.update({
                'price_change': round(price_change, 2),
                'pct_change': round(pct_change, 2),
                'change_direction': 'up' if price_change > 0 else 'down' if price_change < 0 else 'flat'
            })
        else:
            formatted.update({
                'price_change': 0,
                'pct_change': 0,
                'change_direction': 'flat'
            })
        
        return formatted
    
    def _calculate_price_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算价格技术指标
        
        Args:
            data: 原始价格数据
            
        Returns:
            pd.DataFrame: 包含技术指标的数据
        """
        df = data.copy()
        
        # 计算移动平均线
        if len(df) >= 5:
            df['ma5'] = df['close'].rolling(window=5).mean()
        if len(df) >= 10:
            df['ma10'] = df['close'].rolling(window=10).mean()
        if len(df) >= 20:
            df['ma20'] = df['close'].rolling(window=20).mean()
        
        # 计算涨跌幅
        df['pct_change'] = df['close'].pct_change() * 100
        
        # 计算价格变化
        df['price_change'] = df['close'] - df['pre_close']
        
        return df
    
    def format_price_display(self, price_info: Dict[str, Any]) -> str:
        """
        格式化股价信息为显示字符串
        
        Args:
            price_info: 股价信息字典
            
        Returns:
            str: 格式化的显示字符串
        """
        if 'error' in price_info:
            return f"❌ 错误: {price_info['error']}"
        
        # 获取涨跌方向的符号和颜色
        direction = price_info.get('change_direction', 'flat')
        if direction == 'up':
            symbol = "📈"
            change_symbol = "+"
        elif direction == 'down':
            symbol = "📉"
            change_symbol = ""
        else:
            symbol = "➡️"
            change_symbol = ""
        
        # 格式化显示
        display_text = f"""
{symbol} {price_info.get('name', 'N/A')} ({price_info.get('ts_code', 'N/A')})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 当前价格: {price_info.get('current_price', 0):.2f} 元
📊 涨跌幅: {change_symbol}{price_info.get('pct_change', 0):.2f}% ({change_symbol}{price_info.get('price_change', 0):.2f})
📅 交易日期: {price_info.get('trade_date', 'N/A')}

💹 今日行情:
  开盘: {price_info.get('open_price', 0):.2f}   最高: {price_info.get('high_price', 0):.2f}
  最低: {price_info.get('low_price', 0):.2f}   昨收: {price_info.get('pre_close', 0):.2f}

📈 成交情况:
  成交量: {price_info.get('volume', 0):,.0f} 手
  成交额: {price_info.get('amount', 0):,.0f} 千元

ℹ️  基本信息:
  行业: {price_info.get('industry', 'N/A')}
  地区: {price_info.get('area', 'N/A')}
  市场: {price_info.get('market', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return display_text.strip()


def demo_price_query():
    """股价查询演示"""
    print("=" * 60)
    print("股票价格查询演示")
    print("=" * 60)
    
    try:
        analyzer = StockPriceAnalyzer()
        
        # 示例股票代码
        demo_stocks = ["000001.SZ", "600519.SH", "000002.SZ"]
        
        print("1. 单只股票价格查询")
        stock_code = demo_stocks[0]
        print(f"\n查询股票: {stock_code}")
        
        price_info = analyzer.get_current_price(stock_code)
        formatted_display = analyzer.format_price_display(price_info)
        print(formatted_display)
        
        print("\n" + "=" * 60)
        print("2. 批量股票价格查询")
        
        print(f"\n查询股票列表: {', '.join(demo_stocks)}")
        multiple_prices = analyzer.get_multiple_prices(demo_stocks)
        
        for ts_code, info in multiple_prices.items():
            if 'error' not in info:
                print(f"\n{info.get('name', 'N/A')} ({ts_code}): {info.get('current_price', 0):.2f} ({info.get('pct_change', 0):+.2f}%)")
            else:
                print(f"\n{ts_code}: 获取失败 - {info['error']}")
        
        print("\n" + "=" * 60)
        print("3. 股价趋势分析")
        
        trend_analysis = analyzer.analyze_price_trend(stock_code, days=30)
        
        if 'error' not in trend_analysis:
            print(f"\n📊 {trend_analysis['name']} 30天趋势分析:")
            print(f"   期间涨跌: {trend_analysis.get('period_change_pct', 0):+.2f}%")
            print(f"   最高价: {trend_analysis.get('max_price', 0):.2f}")
            print(f"   最低价: {trend_analysis.get('min_price', 0):.2f}")
            print(f"   平均价: {trend_analysis.get('avg_price', 0):.2f}")
            print(f"   趋势方向: {trend_analysis.get('trend_direction', 'N/A')}")
        else:
            print(f"❌ 趋势分析失败: {trend_analysis['error']}")
        
        print("\n" + "=" * 60)
        print("股价查询演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    demo_price_query()