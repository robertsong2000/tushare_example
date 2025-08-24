"""
Tushare 股票数据获取示例项目

本项目提供了一系列使用 Tushare API 获取股票数据的实用示例，
包括股票基本信息查询、K线数据获取、技术指标计算、财务数据分析等功能。

作者: Tushare Examples Team
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Tushare Examples Team"

from .config import Config
from .client import TushareClient

__all__ = ["Config", "TushareClient"]