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