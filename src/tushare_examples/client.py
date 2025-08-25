"""
Tushare API 客户端封装

提供对 Tushare API 的统一访问接口，包含错误处理、重试机制和数据缓存功能。
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
import tushare as ts
from .config import get_config


class TushareClientError(Exception):
    """Tushare 客户端异常"""
    pass


class TushareClient:
    """Tushare API 客户端"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 Tushare 客户端
        
        Args:
            token: Tushare API token，如果未提供则从配置中获取
        """
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # 设置 token
        self.token = token or self.config.tushare_token
        if not self.token:
            raise TushareClientError(
                "Tushare token 未设置。请在配置文件中设置 TUSHARE_TOKEN 或传入 token 参数"
            )
        
        # 初始化 Tushare
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
        self.logger.info("Tushare 客户端初始化成功")
    
    def _make_request(self, api_name: str, **kwargs) -> pd.DataFrame:
        """
        发起 API 请求，包含重试机制
        
        Args:
            api_name: API 接口名称
            **kwargs: API 参数
            
        Returns:
            pd.DataFrame: 返回的数据
            
        Raises:
            TushareClientError: API 调用失败
        """
        retry_count = 0
        last_error = None
        
        while retry_count < self.config.tushare_retry_times:
            try:
                # 获取 API 方法
                api_method = getattr(self.pro, api_name)
                
                # 发起请求
                self.logger.debug(f"调用 {api_name} API，参数: {kwargs}")
                result = api_method(**kwargs)
                
                if result is not None and not result.empty:
                    self.logger.info(f"{api_name} API 调用成功，返回 {len(result)} 条记录")
                    return result
                else:
                    self.logger.warning(f"{api_name} API 返回空数据")
                    return pd.DataFrame()
                    
            except Exception as e:
                last_error = e
                retry_count += 1
                
                self.logger.warning(
                    f"{api_name} API 调用失败 (第{retry_count}次): {str(e)}"
                )
                
                if retry_count < self.config.tushare_retry_times:
                    # 指数退避
                    sleep_time = 2 ** retry_count
                    self.logger.info(f"等待 {sleep_time} 秒后重试...")
                    time.sleep(sleep_time)
        
        # 所有重试都失败
        error_msg = f"{api_name} API 调用失败，已重试 {self.config.tushare_retry_times} 次"
        if last_error:
            error_msg += f"，最后一次错误: {str(last_error)}"
        
        raise TushareClientError(error_msg)
    
    def get_stock_basic(self, 
                       list_status: str = 'L',
                       exchange: Optional[str] = None,
                       market: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票基本信息
        
        Args:
            list_status: 上市状态 L上市 D退市 P暂停上市，默认L
            exchange: 交易所 SSE上交所 SZSE深交所
            market: 市场类别 主板 创业板 科创板 CDR
            
        Returns:
            pd.DataFrame: 股票基本信息
        """
        params = {'list_status': list_status}
        if exchange:
            params['exchange'] = exchange
        if market:
            params['market'] = market
            
        return self._make_request('stock_basic', **params)
    
    def get_daily_data(self,
                      ts_code: str,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            pd.DataFrame: 日线数据
        """
        params = {'ts_code': ts_code}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('daily', **params)
    
    def get_weekly_data(self,
                       ts_code: str,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            pd.DataFrame: 周线数据
        """
        params = {'ts_code': ts_code}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('weekly', **params)
    
    def get_monthly_data(self,
                        ts_code: str,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            pd.DataFrame: 月线数据
        """
        params = {'ts_code': ts_code}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('monthly', **params)
    
    def get_income_statement(self,
                           ts_code: str,
                           period: Optional[str] = None,
                           report_type: str = '1') -> pd.DataFrame:
        """
        获取利润表数据
        
        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            report_type: 报告类型 1合并报表 2单季合并 3调整单季合并表 4调整合并报表 5调整前合并报表
            
        Returns:
            pd.DataFrame: 利润表数据
        """
        params = {'ts_code': ts_code, 'report_type': report_type}
        if period:
            params['period'] = period
            
        return self._make_request('income', **params)
    
    def get_balance_sheet(self,
                         ts_code: str,
                         period: Optional[str] = None,
                         report_type: str = '1') -> pd.DataFrame:
        """
        获取资产负债表数据
        
        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            report_type: 报告类型
            
        Returns:
            pd.DataFrame: 资产负债表数据
        """
        params = {'ts_code': ts_code, 'report_type': report_type}
        if period:
            params['period'] = period
            
        return self._make_request('balancesheet', **params)
    
    def get_cashflow_statement(self,
                              ts_code: str,
                              period: Optional[str] = None,
                              report_type: str = '1') -> pd.DataFrame:
        """
        获取现金流量表数据
        
        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            report_type: 报告类型
            
        Returns:
            pd.DataFrame: 现金流量表数据
        """
        params = {'ts_code': ts_code, 'report_type': report_type}
        if period:
            params['period'] = period
            
        return self._make_request('cashflow', **params)
    
    def get_financial_indicator(self,
                               ts_code: str,
                               period: Optional[str] = None) -> pd.DataFrame:
        """
        获取财务指标数据
        
        Args:
            ts_code: 股票代码
            period: 报告期 YYYYMMDD
            
        Returns:
            pd.DataFrame: 财务指标数据
        """
        params = {'ts_code': ts_code}
        if period:
            params['period'] = period
            
        return self._make_request('fina_indicator', **params)
    
    def get_daily_basic(self,
                       ts_code: Optional[str] = None,
                       trade_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取每日基本面数据
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期 YYYYMMDD
            
        Returns:
            pd.DataFrame: 每日基本面数据
        """
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
            
        return self._make_request('daily_basic', **params)
    
    def get_news(self,
                src: Optional[str] = None,
                start_date: Optional[str] = None,
                end_date: Optional[str] = None,
                limit: int = 100) -> pd.DataFrame:
        """
        获取财经新闻
        
        Args:
            src: 新闻来源
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 单次获取数量限制
            
        Returns:
            pd.DataFrame: 财经新闻数据
        """
        params = {'limit': limit}
        if src:
            params['src'] = src
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('news', **params)
    
    def get_announcement(self,
                        ts_code: Optional[str] = None,
                        ann_date: Optional[str] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        year: Optional[str] = None,
                        limit: int = 100) -> pd.DataFrame:
        """
        获取上市公司公告
        
        Args:
            ts_code: 股票代码
            ann_date: 公告日期 YYYYMMDD
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            year: 年份 YYYY
            limit: 单次获取数量限制
            
        Returns:
            pd.DataFrame: 公告数据
        """
        params = {'limit': limit}
        if ts_code:
            params['ts_code'] = ts_code
        if ann_date:
            params['ann_date'] = ann_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if year:
            params['year'] = year
            
        return self._make_request('anns', **params)
    
    def get_report(self,
                  ts_code: Optional[str] = None,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  limit: int = 100) -> pd.DataFrame:
        """
        获取券商研报数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            limit: 单次获取数量限制
            
        Returns:
            pd.DataFrame: 研报数据
        """
        params = {'limit': limit}
        if ts_code:
            params['ts_code'] = ts_code
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return self._make_request('report', **params)
    
    def get_realtime_quote(self,
                          ts_codes: str) -> pd.DataFrame:
        """
        获取实时股价数据
        
        Args:
            ts_codes: 股票代码，多个用逗号分隔
            
        Returns:
            pd.DataFrame: 实时行情数据
        """
        params = {'ts_code': ts_codes}
        return self._make_request('query', **params)
    
    def get_latest_price(self,
                        ts_code: str,
                        trade_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取最新股价数据（使用daily接口获取最新交易日数据）
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期 YYYYMMDD，不填则获取最新
            
        Returns:
            pd.DataFrame: 最新价格数据
        """
        params = {'ts_code': ts_code}
        if trade_date:
            params['trade_date'] = trade_date
        else:
            # 获取最近的交易日数据
            from datetime import datetime, timedelta
            # 获取最近10个交易日的数据，然后取最新的
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=15)).strftime('%Y%m%d')
            params['start_date'] = start_date
            params['end_date'] = end_date
            
        return self._make_request('daily', **params)
    
    def get_stock_realtime_info(self,
                               ts_code: str) -> Dict[str, Any]:
        """
        获取股票实时信息（综合最新价格和基本信息）
        
        Args:
            ts_code: 股票代码
            
        Returns:
            Dict: 股票实时信息
        """
        try:
            # 获取股票基本信息
            stock_basic = self.get_stock_basic()
            stock_info = stock_basic[stock_basic['ts_code'] == ts_code]
            
            if stock_info.empty:
                return {'error': f'未找到股票代码 {ts_code} 的信息'}
            
            stock_data = stock_info.iloc[0]
            
            # 获取最新价格数据
            latest_price_data = self.get_latest_price(ts_code)
            
            result = {
                'ts_code': ts_code,
                'name': stock_data.get('name', 'N/A'),
                'industry': stock_data.get('industry', 'N/A'),
                'area': stock_data.get('area', 'N/A'),
                'market': stock_data.get('market', 'N/A'),
                'list_date': stock_data.get('list_date', 'N/A'),
            }
            
            if not latest_price_data.empty:
                # 取最新的交易日数据
                latest_data = latest_price_data.iloc[0]
                result.update({
                    'trade_date': latest_data.get('trade_date', 'N/A'),
                    'open': latest_data.get('open', 0),
                    'high': latest_data.get('high', 0),
                    'low': latest_data.get('low', 0),
                    'close': latest_data.get('close', 0),
                    'pre_close': latest_data.get('pre_close', 0),
                    'change': latest_data.get('change', 0),
                    'pct_chg': latest_data.get('pct_chg', 0),
                    'vol': latest_data.get('vol', 0),
                    'amount': latest_data.get('amount', 0),
                })
                
                # 计算涨跌幅和涨跌额
                if result['pre_close'] and result['pre_close'] != 0:
                    price_change = result['close'] - result['pre_close']
                    pct_change = (price_change / result['pre_close']) * 100
                    result['price_change'] = price_change
                    result['pct_change_calculated'] = pct_change
            else:
                result['error'] = '暂无最新交易数据'
            
            return result
            
        except Exception as e:
            return {'error': f'获取股票信息失败: {str(e)}'}
    
    def save_data(self, data: pd.DataFrame, filename: str, format: str = 'csv'):
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
            format: 保存格式 'csv', 'json', 'excel'
        """
        if data.empty:
            self.logger.warning("数据为空，跳过保存")
            return
        
        file_path = self.config.get_data_path(filename)
        
        try:
            if format.lower() == 'csv':
                data.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif format.lower() == 'json':
                data.to_json(file_path, orient='records', force_ascii=False, indent=2)
            elif format.lower() in ['excel', 'xlsx']:
                data.to_excel(file_path, index=False)
            else:
                raise ValueError(f"不支持的保存格式: {format}")
                
            self.logger.info(f"数据已保存到: {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            raise TushareClientError(f"保存数据失败: {str(e)}")
    
    def load_data(self, filename: str, format: str = 'csv') -> pd.DataFrame:
        """
        从文件加载数据
        
        Args:
            filename: 文件名
            format: 文件格式 'csv', 'json', 'excel'
            
        Returns:
            pd.DataFrame: 加载的数据
        """
        file_path = self.config.get_data_path(filename)
        
        if not file_path.exists():
            self.logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        try:
            if format.lower() == 'csv':
                return pd.read_csv(file_path)
            elif format.lower() == 'json':
                return pd.read_json(file_path)
            elif format.lower() in ['excel', 'xlsx']:
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {format}")
                
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            raise TushareClientError(f"加载数据失败: {str(e)}")


if __name__ == "__main__":
    # 客户端测试
    try:
        client = TushareClient()
        
        # 测试获取股票基本信息
        print("测试获取股票基本信息...")
        stocks = client.get_stock_basic()
        print(f"获取到 {len(stocks)} 只股票信息")
        print(stocks.head())
        
    except Exception as e:
        print(f"测试失败: {str(e)}")