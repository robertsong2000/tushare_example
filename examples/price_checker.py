#!/usr/bin/env python3
"""
股票价格查询演示

交互式股票价格查询工具，支持用户输入股票代码获取实时股价、
历史走势分析和可视化图表展示。
"""

import sys
from pathlib import Path
import logging
import argparse
import re

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tushare_examples.examples.price_query import StockPriceAnalyzer
from src.tushare_examples.visualizer import StockVisualizer
from src.tushare_examples.client import TushareClient


class InteractivePriceQuery:
    """交互式股价查询系统"""
    
    def __init__(self):
        """初始化查询系统"""
        self.analyzer = StockPriceAnalyzer()
        self.visualizer = StockVisualizer()
        self.logger = logging.getLogger(__name__)
        
        # 常用股票代码示例
        self.popular_stocks = {
            '平安银行': '000001.SZ',
            '万科A': '000002.SZ', 
            '中国平安': '601318.SH',
            '贵州茅台': '600519.SH',
            '招商银行': '600036.SH',
            '五粮液': '000858.SZ',
            '比亚迪': '002594.SZ',
            '宁德时代': '300750.SZ'
        }
    
    def validate_stock_code(self, stock_code: str) -> str:
        """
        验证和标准化股票代码
        
        Args:
            stock_code: 用户输入的股票代码
            
        Returns:
            str: 标准化的股票代码
        """
        # 移除空格并转换为大写
        code = stock_code.strip().upper()
        
        # 检查是否为6位数字
        if re.match(r'^\\d{6}$', code):
            # 根据开头数字自动添加后缀
            if code.startswith(('000', '001', '002', '003')):
                return f"{code}.SZ"
            elif code.startswith(('600', '601', '603', '688')):
                return f"{code}.SH"
            else:
                # 默认深圳
                return f"{code}.SZ"
        
        # 检查是否已经包含后缀
        if re.match(r'^\\d{6}\\.(SZ|SH)$', code):
            return code
        
        # 检查是否在常用股票中
        for name, ts_code in self.popular_stocks.items():
            if name in stock_code or stock_code in name:
                return ts_code
        
        # 如果都不匹配，返回原始输入
        return code
    
    def query_single_stock(self, stock_code: str, show_chart: bool = True):
        """
        查询单只股票价格
        
        Args:
            stock_code: 股票代码
            show_chart: 是否显示图表
        """
        print(f"\\n🔍 正在查询股票: {stock_code}")
        print("-" * 50)
        
        try:
            # 获取股价信息
            price_info = self.analyzer.get_current_price(stock_code)
            
            if 'error' in price_info:
                print(f"❌ 查询失败: {price_info['error']}")
                return
            
            # 显示格式化的股价信息
            formatted_display = self.analyzer.format_price_display(price_info)
            print(formatted_display)
            
            if show_chart:
                print("\\n📊 正在生成图表...")
                try:
                    # 生成价格信息卡片
                    price_card = self.visualizer.plot_price_info_card(price_info)
                    chart_filename = f"{stock_code.replace('.', '_')}_price_card.png"
                    self.visualizer.save_chart(price_card, chart_filename)
                    print(f"📊 价格信息图表已保存: {chart_filename}")
                    
                    # 获取历史数据并生成走势图
                    print("📈 正在获取历史走势数据...")
                    history_data = self.analyzer.get_price_history(stock_code, days=30)
                    
                    if not history_data.empty:
                        trend_chart = self.visualizer.plot_price_trend(
                            history_data, 
                            title=f"{price_info.get('name', stock_code)} 30天价格走势"
                        )
                        trend_filename = f"{stock_code.replace('.', '_')}_trend.png"
                        self.visualizer.save_chart(trend_chart, trend_filename)
                        print(f"📈 走势图已保存: {trend_filename}")
                    else:
                        print("⚠️ 暂无历史数据")
                except Exception as chart_error:
                    print(f"⚠️ 图表生成失败: {str(chart_error)}")
            
        except Exception as e:
            print(f"❌ 查询过程中出现错误: {str(e)}")
            self.logger.error(f"股价查询失败: {str(e)}", exc_info=True)
    
    def show_popular_stocks(self):
        """
        显示热门股票列表
        """
        print("\\n🔥 热门股票代码:")
        print("=" * 30)
        for i, (name, code) in enumerate(self.popular_stocks.items(), 1):
            print(f"{i:2d}. {name}: {code}")
    
    def interactive_mode(self):
        """
        交互式查询模式
        """
        print("\\n" + "=" * 60)
        print("🚀 股票价格查询系统")
        print("=" * 60)
        
        print("\\n💡 使用说明:")
        print("  - 输入6位股票代码 (如: 000001)")
        print("  - 输入完整代码 (如: 000001.SZ)")
        print("  - 输入 'help' 查看热门股票")
        print("  - 输入 'quit' 退出程序")
        
        while True:
            try:
                user_input = input("\\n📝 请输入股票代码: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 感谢使用股票价格查询系统！")
                    break
                
                if user_input.lower() == 'help':
                    self.show_popular_stocks()
                    continue
                
                # 单股票查询
                validated_code = self.validate_stock_code(user_input)
                self.query_single_stock(validated_code, show_chart=False)
                
            except KeyboardInterrupt:
                print("\\n\\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"\\n❌ 处理输入时出现错误: {str(e)}")
                self.logger.error(f"交互模式错误: {str(e)}", exc_info=True)
    
    def demo_mode(self):
        """
        演示模式
        """
        print("\\n" + "=" * 60)
        print("🎬 股票价格查询演示")
        print("=" * 60)
        
        # 演示单股查询
        demo_stock = "000001.SZ"
        print(f"\\n1️⃣ 单股查询演示 - {demo_stock}")
        self.query_single_stock(demo_stock, show_chart=False)
        
        print("\\n" + "=" * 60)
        print("🎉 演示完成！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="股票价格查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python price_checker.py                    # 启动交互模式
  python price_checker.py --demo            # 运行演示
  python price_checker.py --stock 000001    # 查询指定股票
        """
    )
    
    parser.add_argument('--demo', action='store_true',
                       help='运行演示模式')
    
    parser.add_argument('--stock', type=str,
                       help='查询单只股票 (股票代码)')
    
    parser.add_argument('--no-chart', action='store_true',
                       help='不生成图表')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建查询系统
    query_system = InteractivePriceQuery()
    
    try:
        if args.demo:
            # 演示模式
            query_system.demo_mode()
        elif args.stock:
            # 单股查询
            validated_code = query_system.validate_stock_code(args.stock)
            query_system.query_single_stock(validated_code, show_chart=not args.no_chart)
        else:
            # 交互模式
            query_system.interactive_mode()
            
    except KeyboardInterrupt:
        print("\\n\\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\\n❌ 程序运行错误: {str(e)}")
        logging.error(f"程序运行失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()