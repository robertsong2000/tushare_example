# Tushare 股票数据获取示例

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org)
[![Tushare](https://img.shields.io/badge/Tushare-Pro-green.svg)](https://tushare.pro)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个完整的 Tushare 股票数据获取、分析和可视化示例项目，帮助用户快速上手使用 Tushare API 进行股票数据分析。

## ✨ 项目特性

- 🔑 **完整的 API 封装**：对 Tushare API 进行友好封装，包含错误处理和重试机制
- 📊 **丰富的数据分析**：股票基本信息、K线数据、财务报表、技术指标分析
- 📈 **多样化可视化**：支持 K线图、技术指标图、财务图表等多种可视化
- 🔍 **智能股票筛选**：基于多种条件的股票筛选和评分系统
- 📝 **详细的示例代码**：包含完整的使用示例和演示脚本
- 🎨 **交互式图表**：支持静态和交互式图表展示
- 💾 **灵活的数据存储**：支持 CSV、JSON、Excel 多种格式

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- Tushare Pro 账号和 Token

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd tushare_example

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 Token

```bash
# 复制配置模板
cp .env.template .env

# 编辑 .env 文件，设置你的 Tushare Token
# TUSHARE_TOKEN=your_tushare_token_here
```

如何获取 Tushare Token：
1. 访问 [Tushare Pro](https://tushare.pro/) 注册账号
2. 在个人中心获取 API Token
3. 将 Token 填入 `.env` 文件

### 4. 运行演示

```bash
# 运行完整演示
python main_demo.py

# 运行特定演示
python main_demo.py --demo basic        # 股票基本信息
python main_demo.py --demo kline        # K线数据分析
python main_demo.py --demo financial    # 财务数据分析
python main_demo.py --demo visualization # 数据可视化

# 指定股票和参数
python main_demo.py --stock 600519.SH --days 180
```

## 📖 功能模块

### 🏢 股票基本信息查询

```python
from src.tushare_examples.examples.stock_basic import StockInfoAnalyzer

analyzer = StockInfoAnalyzer()

# 获取所有股票信息
all_stocks = analyzer.get_all_stocks()

# 搜索股票
maotai_stocks = analyzer.search_stocks("茅台")

# 按行业筛选
bank_stocks = analyzer.get_stocks_by_industry("银行")
```

### 📈 K线数据分析

```python
from src.tushare_examples.examples.kline_analysis import KLineAnalyzer

analyzer = KLineAnalyzer()

# 获取K线数据
kline_data = analyzer.get_kline_data(
    ts_code="000001.SZ",
    start_date="20231001"
)

# 绘制K线图
fig = analyzer.plot_candlestick(
    kline_data, 
    title="平安银行K线图",
    ma_lines=[5, 10, 20]
)

# 趋势分析
analysis = analyzer.analyze_trend(kline_data)
```

### 💰 财务数据分析

```python
from src.tushare_examples.examples.financial_analysis import FinancialAnalyzer

analyzer = FinancialAnalyzer()

# 获取财务报表
income_data = analyzer.get_income_statement("600519.SH")
balance_data = analyzer.get_balance_sheet("600519.SH")

# 盈利能力分析
profitability = analyzer.analyze_profitability(income_data)

# 生成财务报告
report = analyzer.generate_financial_report("600519.SH")
```

### 🔧 技术指标计算

```python
from src.tushare_examples.indicators import TechnicalIndicators

calculator = TechnicalIndicators()

# 计算各种技术指标
data_with_indicators = calculator.calculate_all_indicators(kline_data)

# 生成交易信号
signals = calculator.get_trading_signals(data_with_indicators)
```

### 📊 数据可视化

```python
from src.tushare_examples.visualizer import StockVisualizer

visualizer = StockVisualizer()

# 专业K线图
fig1 = visualizer.plot_candlestick_mplfinance(data)

# 交互式K线图
fig2 = visualizer.plot_interactive_candlestick(data)

# 技术指标图
fig3 = visualizer.plot_technical_indicators(data, ['MACD', 'RSI', 'KDJ'])

# 多股票对比
fig4 = visualizer.plot_comparison_chart(stock_data_dict)
```

## 📁 项目结构

```
tushare_example/
├── src/tushare_examples/          # 主要源代码
│   ├── __init__.py                # 包初始化
│   ├── config.py                  # 配置管理
│   ├── client.py                  # Tushare API 客户端
│   ├── indicators.py              # 技术指标计算
│   ├── visualizer.py              # 数据可视化
│   └── examples/                  # 示例模块
│       ├── stock_basic.py         # 股票基本信息
│       ├── kline_analysis.py      # K线数据分析
│       └── financial_analysis.py  # 财务数据分析
├── examples/                      # 独立示例脚本
│   ├── stock_screener.py          # 股票筛选器
│   └── stock_comparison.py        # 多股票对比
├── data/                          # 数据文件目录
├── cache/                         # 缓存目录
├── charts/                        # 图表输出目录
├── main_demo.py                   # 主演示脚本
├── requirements.txt               # 依赖列表
├── .env.template                  # 环境配置模板
└── README.md                      # 项目文档
```

## 🎯 使用案例

### 案例1：获取股票基本信息

```python
# 获取所有上市公司信息
python -c "
from src.tushare_examples.examples.stock_basic import demo_stock_basic_info
demo_stock_basic_info()
"
```

### 案例2：分析股票K线和技术指标

```python
# 分析平安银行的K线数据
python -c "
from src.tushare_examples.examples.kline_analysis import KLineAnalyzer
analyzer = KLineAnalyzer()
data = analyzer.get_kline_data('000001.SZ')
fig = analyzer.plot_candlestick(data, title='平安银行K线图')
fig.show()
"
```

### 案例3：财务数据分析

```python
# 分析贵州茅台的财务状况
python -c "
from src.tushare_examples.examples.financial_analysis import FinancialAnalyzer
analyzer = FinancialAnalyzer()
report = analyzer.generate_financial_report('600519.SH')
print('财务分析报告:', report)
"
```

### 案例4：股票筛选

```python
# 运行股票筛选器
python examples/stock_screener.py
```

### 案例5：多股票对比

```python
# 运行银行股对比分析
python examples/stock_comparison.py
```

## 📊 技术指标支持

| 指标类型 | 支持的指标 | 说明 |
|---------|-----------|------|
| 移动平均 | SMA, EMA | 简单移动平均、指数移动平均 |
| 趋势指标 | MACD, DMI | 异同移动平均线、趋向指标 |
| 摆动指标 | RSI, KDJ, Williams %R | 相对强弱指数、随机指标 |
| 波动指标 | Bollinger Bands, ATR | 布林带、平均真实波幅 |
| 量价指标 | OBV, CCI | 能量潮、商品通道指数 |

## 🎨 可视化功能

- **K线图**：专业的蜡烛图展示，支持多种时间周期
- **技术指标图**：MACD、RSI、KDJ等技术指标可视化
- **财务图表**：营收趋势、利润分析、资产负债结构
- **对比分析**：多股票价格对比、相关性分析
- **交互式图表**：基于 Plotly 的交互式图表
- **自定义样式**：支持多种图表样式和配色方案

## ⚠️ 注意事项

1. **API 限制**：Tushare Pro 对 API 调用频率有限制，请合理使用
2. **数据权限**：某些高级数据需要对应的积分权限
3. **网络要求**：需要稳定的网络连接来获取实时数据
4. **数据准确性**：请注意数据的时效性，建议结合多种数据源
5. **投资风险**：本项目仅用于学习和研究，不构成投资建议

## 🔧 配置选项

可以在 `.env` 文件中配置以下选项：

```bash
# Tushare API 配置
TUSHARE_TOKEN=your_token_here
TUSHARE_TIMEOUT=30
TUSHARE_RETRY_TIMES=3

# 目录配置
DATA_DIR=./data
CACHE_DIR=./cache
CHARTS_DIR=./charts

# 图表配置
CHART_WIDTH=1200
CHART_HEIGHT=800
CHART_DPI=100

# 日志配置
LOG_LEVEL=INFO
```

## 🤝 贡献指南

我们欢迎各种形式的贡献：

1. **Bug 报告**：发现问题请提交 Issue
2. **功能建议**：有新想法请提交 Feature Request
3. **代码贡献**：提交 Pull Request
4. **文档改进**：帮助完善文档

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd tushare_example

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black src/
flake8 src/
```

## 📄 许可证

本项目采用 MIT 许可证。详情请参考 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Tushare](https://tushare.pro/) - 提供优质的金融数据接口
- [matplotlib](https://matplotlib.org/) - 强大的 Python 绘图库
- [pandas](https://pandas.pydata.org/) - 数据分析工具
- [plotly](https://plotly.com/) - 交互式图表库

## 📞 联系我们

- 项目主页：[GitHub Repository](#)
- 问题反馈：[Issues](#)
- 邮箱：developer@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！