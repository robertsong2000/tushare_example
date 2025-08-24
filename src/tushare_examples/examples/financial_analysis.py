"""
财务数据获取和分析示例

演示如何使用 Tushare API 获取上市公司财务报表数据，包括利润表、资产负债表、现金流量表等，
并进行财务指标分析和可视化展示。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

from ..client import TushareClient, TushareClientError

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FinancialAnalyzer:
    """财务数据分析器"""
    
    def __init__(self, client: Optional[TushareClient] = None):
        """
        初始化财务分析器
        
        Args:
            client: Tushare 客户端实例
        """
        self.client = client or TushareClient()
        self.logger = logging.getLogger(__name__)
    
    def get_income_statement(self, 
                           ts_code: str, 
                           years: int = 5) -> pd.DataFrame:
        """
        获取利润表数据
        
        Args:
            ts_code: 股票代码
            years: 获取最近几年的数据
            
        Returns:
            pd.DataFrame: 利润表数据
        """
        try:
            self.logger.info(f"获取 {ts_code} 最近{years}年的利润表数据")
            
            # 获取最近几年的报告期
            current_year = datetime.now().year
            periods = []
            for i in range(years):
                year = current_year - i
                periods.extend([
                    f"{year}1231",  # 年报
                    f"{year}0930",  # 三季报
                    f"{year}0630",  # 中报
                    f"{year}0331"   # 一季报
                ])
            
            all_data = []
            for period in periods:
                try:
                    data = self.client.get_income_statement(ts_code, period)
                    if not data.empty:
                        all_data.append(data)
                except:
                    continue
            
            if all_data:
                result = pd.concat(all_data, ignore_index=True)
                result = result.drop_duplicates(subset=['ts_code', 'end_date'])
                result = result.sort_values('end_date', ascending=False)
                
                self.logger.info(f"成功获取 {len(result)} 条利润表记录")
                return result
            else:
                self.logger.warning(f"未获取到 {ts_code} 的利润表数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取利润表数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, 
                         ts_code: str, 
                         years: int = 5) -> pd.DataFrame:
        """
        获取资产负债表数据
        
        Args:
            ts_code: 股票代码
            years: 获取最近几年的数据
            
        Returns:
            pd.DataFrame: 资产负债表数据
        """
        try:
            self.logger.info(f"获取 {ts_code} 最近{years}年的资产负债表数据")
            
            current_year = datetime.now().year
            periods = []
            for i in range(years):
                year = current_year - i
                periods.extend([f"{year}1231", f"{year}0930", f"{year}0630", f"{year}0331"])
            
            all_data = []
            for period in periods:
                try:
                    data = self.client.get_balance_sheet(ts_code, period)
                    if not data.empty:
                        all_data.append(data)
                except:
                    continue
            
            if all_data:
                result = pd.concat(all_data, ignore_index=True)
                result = result.drop_duplicates(subset=['ts_code', 'end_date'])
                result = result.sort_values('end_date', ascending=False)
                
                self.logger.info(f"成功获取 {len(result)} 条资产负债表记录")
                return result
            else:
                self.logger.warning(f"未获取到 {ts_code} 的资产负债表数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取资产负债表数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_cashflow_statement(self, 
                              ts_code: str, 
                              years: int = 5) -> pd.DataFrame:
        """
        获取现金流量表数据
        
        Args:
            ts_code: 股票代码
            years: 获取最近几年的数据
            
        Returns:
            pd.DataFrame: 现金流量表数据
        """
        try:
            self.logger.info(f"获取 {ts_code} 最近{years}年的现金流量表数据")
            
            current_year = datetime.now().year
            periods = []
            for i in range(years):
                year = current_year - i
                periods.extend([f"{year}1231", f"{year}0930", f"{year}0630", f"{year}0331"])
            
            all_data = []
            for period in periods:
                try:
                    data = self.client.get_cashflow_statement(ts_code, period)
                    if not data.empty:
                        all_data.append(data)
                except:
                    continue
            
            if all_data:
                result = pd.concat(all_data, ignore_index=True)
                result = result.drop_duplicates(subset=['ts_code', 'end_date'])
                result = result.sort_values('end_date', ascending=False)
                
                self.logger.info(f"成功获取 {len(result)} 条现金流量表记录")
                return result
            else:
                self.logger.warning(f"未获取到 {ts_code} 的现金流量表数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取现金流量表数据失败: {str(e)}")
            return pd.DataFrame()
    
    def get_financial_indicators(self, 
                                ts_code: str, 
                                years: int = 5) -> pd.DataFrame:
        """
        获取财务指标数据
        
        Args:
            ts_code: 股票代码
            years: 获取最近几年的数据
            
        Returns:
            pd.DataFrame: 财务指标数据
        """
        try:
            self.logger.info(f"获取 {ts_code} 最近{years}年的财务指标数据")
            
            current_year = datetime.now().year
            periods = []
            for i in range(years):
                year = current_year - i
                periods.extend([f"{year}1231", f"{year}0930", f"{year}0630", f"{year}0331"])
            
            all_data = []
            for period in periods:
                try:
                    data = self.client.get_financial_indicator(ts_code, period)
                    if not data.empty:
                        all_data.append(data)
                except:
                    continue
            
            if all_data:
                result = pd.concat(all_data, ignore_index=True)
                result = result.drop_duplicates(subset=['ts_code', 'end_date'])
                result = result.sort_values('end_date', ascending=False)
                
                self.logger.info(f"成功获取 {len(result)} 条财务指标记录")
                return result
            else:
                self.logger.warning(f"未获取到 {ts_code} 的财务指标数据")
                return pd.DataFrame()
                
        except TushareClientError as e:
            self.logger.error(f"获取财务指标数据失败: {str(e)}")
            return pd.DataFrame()
    
    def analyze_profitability(self, income_data: pd.DataFrame) -> Dict[str, Any]:
        """
        盈利能力分析
        
        Args:
            income_data: 利润表数据
            
        Returns:
            Dict: 盈利能力分析结果
        """
        if income_data.empty:
            return {}
        
        analysis = {}
        
        # 获取年报数据（只分析年报）
        annual_data = income_data[income_data['end_date'].str.endswith('1231')]
        
        if not annual_data.empty:
            annual_data = annual_data.sort_values('end_date')
            
            # 营业收入增长率
            if len(annual_data) > 1:
                revenue_growth = []
                for i in range(1, len(annual_data)):
                    current_revenue = annual_data.iloc[i]['revenue']
                    previous_revenue = annual_data.iloc[i-1]['revenue']
                    if previous_revenue and previous_revenue != 0:
                        growth = (current_revenue - previous_revenue) / previous_revenue * 100
                        revenue_growth.append(growth)
                
                analysis['revenue_growth_rates'] = revenue_growth
                analysis['avg_revenue_growth'] = np.mean(revenue_growth) if revenue_growth else 0
            
            # 净利润增长率
            if len(annual_data) > 1:
                profit_growth = []
                for i in range(1, len(annual_data)):
                    current_profit = annual_data.iloc[i]['n_income']
                    previous_profit = annual_data.iloc[i-1]['n_income']
                    if previous_profit and previous_profit != 0:
                        growth = (current_profit - previous_profit) / previous_profit * 100
                        profit_growth.append(growth)
                
                analysis['profit_growth_rates'] = profit_growth
                analysis['avg_profit_growth'] = np.mean(profit_growth) if profit_growth else 0
            
            # 毛利率趋势
            gross_margins = []
            for _, row in annual_data.iterrows():
                if row['revenue'] and row['revenue'] != 0:
                    gross_margin = (row['revenue'] - row['oper_cost']) / row['revenue'] * 100
                    gross_margins.append(gross_margin)
            
            analysis['gross_margins'] = gross_margins
            analysis['avg_gross_margin'] = np.mean(gross_margins) if gross_margins else 0
            
            # 净利率趋势
            net_margins = []
            for _, row in annual_data.iterrows():
                if row['revenue'] and row['revenue'] != 0:
                    net_margin = row['n_income'] / row['revenue'] * 100
                    net_margins.append(net_margin)
            
            analysis['net_margins'] = net_margins
            analysis['avg_net_margin'] = np.mean(net_margins) if net_margins else 0
        
        return analysis
    
    def analyze_solvency(self, balance_data: pd.DataFrame) -> Dict[str, Any]:
        """
        偿债能力分析
        
        Args:
            balance_data: 资产负债表数据
            
        Returns:
            Dict: 偿债能力分析结果
        """
        if balance_data.empty:
            return {}
        
        analysis = {}
        
        # 获取年报数据
        annual_data = balance_data[balance_data['end_date'].str.endswith('1231')]
        
        if not annual_data.empty:
            annual_data = annual_data.sort_values('end_date')
            
            # 资产负债率
            debt_ratios = []
            for _, row in annual_data.iterrows():
                if row['total_assets'] and row['total_assets'] != 0:
                    debt_ratio = row['total_liab'] / row['total_assets'] * 100
                    debt_ratios.append(debt_ratio)
            
            analysis['debt_ratios'] = debt_ratios
            analysis['avg_debt_ratio'] = np.mean(debt_ratios) if debt_ratios else 0
            
            # 流动比率
            current_ratios = []
            for _, row in annual_data.iterrows():
                if row['total_cur_liab'] and row['total_cur_liab'] != 0:
                    current_ratio = row['total_cur_assets'] / row['total_cur_liab']
                    current_ratios.append(current_ratio)
            
            analysis['current_ratios'] = current_ratios
            analysis['avg_current_ratio'] = np.mean(current_ratios) if current_ratios else 0
            
            # 速动比率（简化计算）
            quick_ratios = []
            for _, row in annual_data.iterrows():
                if row['total_cur_liab'] and row['total_cur_liab'] != 0:
                    # 速动资产 = 流动资产 - 存货
                    quick_assets = row['total_cur_assets'] - (row.get('inventories', 0) or 0)
                    quick_ratio = quick_assets / row['total_cur_liab']
                    quick_ratios.append(quick_ratio)
            
            analysis['quick_ratios'] = quick_ratios
            analysis['avg_quick_ratio'] = np.mean(quick_ratios) if quick_ratios else 0
        
        return analysis
    
    def plot_financial_trends(self, 
                             income_data: pd.DataFrame,
                             figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
        """
        绘制财务趋势图
        
        Args:
            income_data: 利润表数据
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        # 获取年报数据
        annual_data = income_data[income_data['end_date'].str.endswith('1231')]
        
        if annual_data.empty:
            raise ValueError("没有年报数据可用于绘图")
        
        annual_data = annual_data.sort_values('end_date')
        annual_data['year'] = annual_data['end_date'].str[:4]
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # 营业收入趋势
        ax1 = axes[0, 0]
        ax1.plot(annual_data['year'], annual_data['revenue'] / 1e8, marker='o', linewidth=2)
        ax1.set_title('营业收入趋势', fontsize=12, fontweight='bold')
        ax1.set_ylabel('营业收入 (亿元)')
        ax1.grid(True, alpha=0.3)
        
        # 净利润趋势
        ax2 = axes[0, 1]
        ax2.plot(annual_data['year'], annual_data['n_income'] / 1e8, 
                marker='o', linewidth=2, color='green')
        ax2.set_title('净利润趋势', fontsize=12, fontweight='bold')
        ax2.set_ylabel('净利润 (亿元)')
        ax2.grid(True, alpha=0.3)
        
        # 毛利率和净利率趋势
        ax3 = axes[1, 0]
        gross_margins = []
        net_margins = []
        
        for _, row in annual_data.iterrows():
            if row['revenue'] and row['revenue'] != 0:
                gross_margin = (row['revenue'] - row['oper_cost']) / row['revenue'] * 100
                net_margin = row['n_income'] / row['revenue'] * 100
                gross_margins.append(gross_margin)
                net_margins.append(net_margin)
            else:
                gross_margins.append(0)
                net_margins.append(0)
        
        ax3.plot(annual_data['year'], gross_margins, marker='o', label='毛利率', linewidth=2)
        ax3.plot(annual_data['year'], net_margins, marker='s', label='净利率', linewidth=2)
        ax3.set_title('盈利能力趋势', fontsize=12, fontweight='bold')
        ax3.set_ylabel('利润率 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 收入增长率
        ax4 = axes[1, 1]
        if len(annual_data) > 1:
            growth_rates = []
            years = []
            for i in range(1, len(annual_data)):
                current_revenue = annual_data.iloc[i]['revenue']
                previous_revenue = annual_data.iloc[i-1]['revenue']
                if previous_revenue and previous_revenue != 0:
                    growth = (current_revenue - previous_revenue) / previous_revenue * 100
                    growth_rates.append(growth)
                    years.append(annual_data.iloc[i]['year'])
            
            if growth_rates:
                colors = ['green' if x >= 0 else 'red' for x in growth_rates]
                ax4.bar(years, growth_rates, color=colors, alpha=0.7)
                ax4.set_title('营业收入增长率', fontsize=12, fontweight='bold')
                ax4.set_ylabel('增长率 (%)')
                ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_balance_sheet_analysis(self, 
                                   balance_data: pd.DataFrame,
                                   figsize: Tuple[int, int] = (15, 8)) -> plt.Figure:
        """
        绘制资产负债分析图
        
        Args:
            balance_data: 资产负债表数据
            figsize: 图表大小
            
        Returns:
            plt.Figure: 图表对象
        """
        annual_data = balance_data[balance_data['end_date'].str.endswith('1231')]
        
        if annual_data.empty:
            raise ValueError("没有年报数据可用于绘图")
        
        annual_data = annual_data.sort_values('end_date')
        annual_data['year'] = annual_data['end_date'].str[:4]
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # 资产负债率趋势
        ax1 = axes[0]
        debt_ratios = []
        for _, row in annual_data.iterrows():
            if row['total_assets'] and row['total_assets'] != 0:
                debt_ratio = row['total_liab'] / row['total_assets'] * 100
                debt_ratios.append(debt_ratio)
            else:
                debt_ratios.append(0)
        
        ax1.plot(annual_data['year'], debt_ratios, marker='o', linewidth=2, color='red')
        ax1.set_title('资产负债率趋势', fontsize=12, fontweight='bold')
        ax1.set_ylabel('资产负债率 (%)')
        ax1.grid(True, alpha=0.3)
        
        # 流动比率趋势
        ax2 = axes[1]
        current_ratios = []
        for _, row in annual_data.iterrows():
            if row['total_cur_liab'] and row['total_cur_liab'] != 0:
                current_ratio = row['total_cur_assets'] / row['total_cur_liab']
                current_ratios.append(current_ratio)
            else:
                current_ratios.append(0)
        
        ax2.plot(annual_data['year'], current_ratios, marker='s', linewidth=2, color='blue')
        ax2.set_title('流动比率趋势', fontsize=12, fontweight='bold')
        ax2.set_ylabel('流动比率')
        ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='安全线')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 资产结构
        ax3 = axes[2]
        if not annual_data.empty:
            latest_data = annual_data.iloc[-1]
            
            # 资产结构饼图
            asset_structure = {
                '流动资产': latest_data['total_cur_assets'],
                '非流动资产': latest_data['total_assets'] - latest_data['total_cur_assets']
            }
            
            labels = list(asset_structure.keys())
            sizes = list(asset_structure.values())
            colors = ['lightblue', 'lightcoral']
            
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
            ax3.set_title(f'资产结构 ({annual_data.iloc[-1]["year"]})', 
                         fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def generate_financial_report(self, ts_code: str) -> Dict[str, Any]:
        """
        生成综合财务分析报告
        
        Args:
            ts_code: 股票代码
            
        Returns:
            Dict: 财务分析报告
        """
        self.logger.info(f"生成 {ts_code} 的财务分析报告")
        
        report = {
            'ts_code': ts_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_summary': {},
            'profitability_analysis': {},
            'solvency_analysis': {},
            'recommendations': []
        }
        
        # 获取财务数据
        income_data = self.get_income_statement(ts_code)
        balance_data = self.get_balance_sheet(ts_code)
        indicators_data = self.get_financial_indicators(ts_code)
        
        # 数据摘要
        report['data_summary'] = {
            'income_records': len(income_data),
            'balance_records': len(balance_data),
            'indicators_records': len(indicators_data)
        }
        
        # 盈利能力分析
        if not income_data.empty:
            report['profitability_analysis'] = self.analyze_profitability(income_data)
        
        # 偿债能力分析
        if not balance_data.empty:
            report['solvency_analysis'] = self.analyze_solvency(balance_data)
        
        # 生成投资建议
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成投资建议"""
        recommendations = []
        
        prof_analysis = report.get('profitability_analysis', {})
        solv_analysis = report.get('solvency_analysis', {})
        
        # 盈利能力建议
        avg_revenue_growth = prof_analysis.get('avg_revenue_growth', 0)
        if avg_revenue_growth > 20:
            recommendations.append("营业收入增长强劲，显示良好的成长性")
        elif avg_revenue_growth < 0:
            recommendations.append("营业收入增长乏力，需关注业务发展状况")
        
        avg_net_margin = prof_analysis.get('avg_net_margin', 0)
        if avg_net_margin > 15:
            recommendations.append("净利率较高，盈利能力强")
        elif avg_net_margin < 5:
            recommendations.append("净利率偏低，盈利能力有待提升")
        
        # 偿债能力建议
        avg_debt_ratio = solv_analysis.get('avg_debt_ratio', 0)
        if avg_debt_ratio > 70:
            recommendations.append("资产负债率较高，需关注财务风险")
        elif avg_debt_ratio < 30:
            recommendations.append("资产负债率适中，财务结构较为稳健")
        
        avg_current_ratio = solv_analysis.get('avg_current_ratio', 0)
        if avg_current_ratio < 1:
            recommendations.append("流动比率偏低，短期偿债能力需要关注")
        elif avg_current_ratio > 2:
            recommendations.append("流动比率良好，短期偿债能力强")
        
        if not recommendations:
            recommendations.append("建议结合更多指标进行综合分析")
        
        return recommendations


def demo_financial_analysis():
    """财务分析演示"""
    print("=" * 60)
    print("财务数据获取和分析演示")
    print("=" * 60)
    
    try:
        # 创建分析器
        analyzer = FinancialAnalyzer()
        
        # 示例股票代码（贵州茅台）
        ts_code = "600519.SH"
        print(f"\n分析股票: {ts_code}")
        
        # 生成财务分析报告
        print("\n1. 生成财务分析报告...")
        report = analyzer.generate_financial_report(ts_code)
        
        print(f"\n财务数据摘要:")
        for key, value in report['data_summary'].items():
            print(f"{key}: {value}")
        
        # 盈利能力分析
        print(f"\n2. 盈利能力分析:")
        prof_analysis = report['profitability_analysis']
        if prof_analysis:
            print(f"平均营业收入增长率: {prof_analysis.get('avg_revenue_growth', 0):.2f}%")
            print(f"平均净利润增长率: {prof_analysis.get('avg_profit_growth', 0):.2f}%")
            print(f"平均毛利率: {prof_analysis.get('avg_gross_margin', 0):.2f}%")
            print(f"平均净利率: {prof_analysis.get('avg_net_margin', 0):.2f}%")
        
        # 偿债能力分析
        print(f"\n3. 偿债能力分析:")
        solv_analysis = report['solvency_analysis']
        if solv_analysis:
            print(f"平均资产负债率: {solv_analysis.get('avg_debt_ratio', 0):.2f}%")
            print(f"平均流动比率: {solv_analysis.get('avg_current_ratio', 0):.2f}")
            print(f"平均速动比率: {solv_analysis.get('avg_quick_ratio', 0):.2f}")
        
        # 投资建议
        print(f"\n4. 投资建议:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"{i}. {recommendation}")
        
        # 获取财务数据用于绘图
        print(f"\n5. 生成财务趋势图...")
        income_data = analyzer.get_income_statement(ts_code, years=5)
        balance_data = analyzer.get_balance_sheet(ts_code, years=5)
        
        if not income_data.empty:
            # 绘制财务趋势图
            fig1 = analyzer.plot_financial_trends(income_data)
            chart_path1 = analyzer.client.config.get_chart_path(f"{ts_code}_financial_trends.png")
            fig1.savefig(chart_path1, dpi=300, bbox_inches='tight')
            print(f"财务趋势图已保存: {chart_path1}")
        
        if not balance_data.empty:
            # 绘制资产负债分析图
            fig2 = analyzer.plot_balance_sheet_analysis(balance_data)
            chart_path2 = analyzer.client.config.get_chart_path(f"{ts_code}_balance_analysis.png")
            fig2.savefig(chart_path2, dpi=300, bbox_inches='tight')
            print(f"资产负债分析图已保存: {chart_path2}")
        
        plt.show()  # 显示图表
        
        print("\n" + "=" * 60)
        print("财务分析演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


if __name__ == "__main__":
    demo_financial_analysis()