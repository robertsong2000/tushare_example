"""
配置管理模块

负责管理 Tushare API 配置、环境变量和应用设置。
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """配置管理类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            env_file: 环境配置文件路径，默认为 .env
        """
        self.project_root = Path(__file__).parent.parent.parent
        
        # 加载环境变量
        if env_file:
            load_dotenv(env_file)
        else:
            # 尝试从多个位置加载 .env 文件
            env_paths = [
                self.project_root / '.env',
                self.project_root / '.env.local',
                os.path.expanduser('~/.tushare.env')
            ]
            for env_path in env_paths:
                if env_path.exists():
                    load_dotenv(env_path)
                    break
        
        # 初始化配置
        self._load_config()
        self._setup_logging()
        self._validate_config()
    
    def _load_config(self):
        """加载所有配置项"""
        # Tushare API 配置
        self.tushare_token = os.getenv('TUSHARE_TOKEN', '')
        self.tushare_timeout = int(os.getenv('TUSHARE_TIMEOUT', '30'))
        self.tushare_retry_times = int(os.getenv('TUSHARE_RETRY_TIMES', '3'))
        
        # 目录配置
        self.data_dir = Path(os.getenv('DATA_DIR', self.project_root / 'data'))
        self.cache_dir = Path(os.getenv('CACHE_DIR', self.project_root / 'cache'))
        self.charts_dir = Path(os.getenv('CHARTS_DIR', self.project_root / 'charts'))
        
        # 图表配置
        self.chart_width = int(os.getenv('CHART_WIDTH', '1200'))
        self.chart_height = int(os.getenv('CHART_HEIGHT', '800'))
        self.chart_dpi = int(os.getenv('CHART_DPI', '100'))
        
        # 创建必要目录
        for directory in [self.data_dir, self.cache_dir, self.charts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """设置日志配置"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.project_root / 'tushare_examples.log')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _validate_config(self):
        """验证配置的有效性"""
        if not self.tushare_token:
            self.logger.warning(
                "Tushare token 未设置。请在 .env 文件中设置 TUSHARE_TOKEN，"
                "或访问 https://tushare.pro/ 注册获取 token"
            )
    
    def validate_token(self) -> bool:
        """
        验证 Tushare token 是否有效
        
        Returns:
            bool: token 是否有效
        """
        if not self.tushare_token:
            return False
        
        # 简单的 token 格式验证
        if len(self.tushare_token) < 30:
            self.logger.warning("Tushare token 格式可能不正确")
            return False
        
        return True
    
    def get_data_path(self, filename: str) -> Path:
        """
        获取数据文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            Path: 完整的文件路径
        """
        return self.data_dir / filename
    
    def get_cache_path(self, filename: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            Path: 完整的文件路径
        """
        return self.cache_dir / filename
    
    def get_chart_path(self, filename: str) -> Path:
        """
        获取图表文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            Path: 完整的文件路径
        """
        return self.charts_dir / filename
    
    def __repr__(self) -> str:
        """配置信息的字符串表示"""
        return f"""Tushare Examples 配置:
- Token: {'已设置' if self.tushare_token else '未设置'}
- 超时时间: {self.tushare_timeout}秒
- 重试次数: {self.tushare_retry_times}次
- 数据目录: {self.data_dir}
- 缓存目录: {self.cache_dir}
- 图表目录: {self.charts_dir}
- 图表尺寸: {self.chart_width}x{self.chart_height}
"""


# 全局配置实例
config = Config()


def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        Config: 配置实例
    """
    return config


def set_token(token: str):
    """
    设置 Tushare token
    
    Args:
        token: Tushare API token
    """
    global config
    config.tushare_token = token
    config.logger.info("Tushare token 已更新")


if __name__ == "__main__":
    # 配置测试
    print(config)
    print(f"Token 验证: {config.validate_token()}")