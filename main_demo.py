#!/usr/bin/env python3
"""
Tushare 股票数据获取示例 - 综合演示脚本

该脚本演示了如何使用本项目的各个模块来获取和分析股票数据。
包括股票基本信息查询、K线数据分析、技术指标计算、财务数据分析等功能。

使用方法:
    python main_demo.py
    
或者带参数运行:
    python main_demo.py --stock 000001.SZ --days 180
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tushare_examples.config import get_config, set_token
from src.tushare_examples.client import TushareClient
from src.tushare_examples.examples.stock_basic import demo_stock_basic_info
from src.tushare_examples.examples.kline_analysis import demo_kline_analysis
from src.tushare_examples.examples.financial_analysis import demo_financial_analysis
from src.tushare_examples.examples.news_analysis import demo_news_analysis
from src.tushare_examples.examples.price_query import demo_price_query
from src.tushare_examples.visualizer import demo_visualization


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('tushare_demo.log')
        ]
    )


def check_token():
    """检查和设置 Tushare token"""
    config = get_config()
    
    if not config.validate_token():
        print("=" * 60)
        print("Tushare Token 未设置或无效")
        print("=" * 60)
        print("请按以下步骤设置 Tushare Token:")
        print("1. 访问 https://tushare.pro/ 注册账号")
        print("2. 获取 API Token")
        print("3. 将 .env.template 复制为 .env 文件")
        print("4. 在 .env 文件中设置 TUSHARE_TOKEN=你的token")
        print("5. 或者在运行时输入 token")
        
        token_input = input("\n请输入您的 Tushare Token (回车跳过): ").strip()
        if token_input:
            set_token(token_input)
            print("Token 已设置，继续演示...")
        else:
            print("未设置 Token，将使用模拟数据进行演示...")
            return False
    
    return True


def run_comprehensive_demo(stock_code: str = "000001.SZ", days: int = 180):
    """
    运行综合演示
    
    Args:
        stock_code: 股票代码
        days: 分析天数
    """
    print("=" * 80)
    print("Tushare 股票数据获取示例 - 综合演示")
    print("=" * 80)
    
    has_token = check_token()
    
    if has_token:
        print(f"\n使用股票代码: {stock_code}")
        print(f"分析天数: {days}")
        
        try:
            # 测试 API 连接
            print("\n测试 Tushare API 连接...")
            client = TushareClient()
            test_data = client.get_stock_basic()
            
            if not test_data.empty:
                print(f"✓ API 连接成功，获取到 {len(test_data)} 只股票信息")
            else:
                print("⚠ API 连接成功，但未获取到数据")
                
        except Exception as e:
            print(f"✗ API 连接失败: {str(e)}")
            print("将使用模拟数据进行演示...")
            has_token = False
    
    # 演示各个模块
    demos = [
        ("股票基本信息查询", demo_stock_basic_info),
        ("股价实时查询", demo_price_query),
        ("新闻和公告分析", demo_news_analysis),
        ("数据可视化功能", demo_visualization),
    ]
    
    if has_token:
        # 只有在有 token 的情况下才运行需要真实数据的演示
        demos.extend([
            ("K线数据分析", demo_kline_analysis),
            ("财务数据分析", demo_financial_analysis),
        ])
    
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            demo_func()
        except Exception as e:
            print(f"演示 '{demo_name}' 时出现错误: {str(e)}")
            logging.error(f"演示 '{demo_name}' 失败", exc_info=True)
        
        input("\n按 Enter 键继续下一个演示...")
    
    print("\n" + "=" * 80)
    print("所有演示完成！")
    print("=" * 80)
    
    # 显示生成的文件
    config = get_config()
    print(f"\n生成的文件位置:")
    print(f"- 数据文件: {config.data_dir}")
    print(f"- 图表文件: {config.charts_dir}")
    print(f"- 缓存文件: {config.cache_dir}")
    print(f"- 日志文件: {config.project_root / 'tushare_demo.log'}")


def run_specific_demo(demo_type: str, **kwargs):
    """
    运行特定类型的演示
    
    Args:
        demo_type: 演示类型
        **kwargs: 其他参数
    """
    demos = {
        'basic': ('股票基本信息查询', demo_stock_basic_info),
        'kline': ('K线数据分析', demo_kline_analysis),
        'financial': ('财务数据分析', demo_financial_analysis),
        'news': ('新闻和公告分析', demo_news_analysis),
        'price': ('股价实时查询', demo_price_query),
        'visualization': ('数据可视化', demo_visualization)
    }
    
    if demo_type not in demos:
        print(f"不支持的演示类型: {demo_type}")
        print(f"支持的类型: {list(demos.keys())}")
        return
    
    demo_name, demo_func = demos[demo_type]
    
    print(f"=" * 60)
    print(f"运行演示: {demo_name}")
    print(f"=" * 60)
    
    try:
        demo_func()
        print(f"\n演示 '{demo_name}' 完成！")
    except Exception as e:
        print(f"演示 '{demo_name}' 时出现错误: {str(e)}")
        logging.error(f"演示 '{demo_name}' 失败", exc_info=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Tushare 股票数据获取示例演示脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main_demo.py                           # 运行完整演示
  python main_demo.py --demo basic              # 只运行股票基本信息演示
  python main_demo.py --demo kline --stock 600519.SH  # 运行K线分析演示
  python main_demo.py --token your_token_here   # 使用指定token运行演示
        """
    )
    
    parser.add_argument('--demo', 
                       choices=['basic', 'kline', 'financial', 'news', 'price', 'visualization'],
                       help='运行特定演示类型')
    
    parser.add_argument('--stock', 
                       default='000001.SZ',
                       help='股票代码 (默认: 000001.SZ)')
    
    parser.add_argument('--days', 
                       type=int, 
                       default=180,
                       help='分析天数 (默认: 180)')
    
    parser.add_argument('--token',
                       help='Tushare API Token')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_logging()
    
    # 设置token（如果提供）
    if args.token:
        set_token(args.token)
    
    # 运行演示
    if args.demo:
        run_specific_demo(args.demo, stock=args.stock, days=args.days)
    else:
        run_comprehensive_demo(args.stock, args.days)


if __name__ == "__main__":
    main()