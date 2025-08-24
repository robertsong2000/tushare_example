# API 文档

本文档详细介绍了 Tushare 股票数据获取示例项目的 API 接口和使用方法。

## 目录

- [配置管理 (Config)](#配置管理-config)
- [客户端 (TushareClient)](#客户端-tushareclient)
- [股票基本信息 (StockInfoAnalyzer)](#股票基本信息-stockinfoanalyzer)
- [K线分析 (KLineAnalyzer)](#k线分析-klineanalyzer)
- [财务分析 (FinancialAnalyzer)](#财务分析-financialanalyzer)
- [技术指标 (TechnicalIndicators)](#技术指标-technicalindicators)
- [数据可视化 (StockVisualizer)](#数据可视化-stockvisualizer)

## 配置管理 (Config)

### 类：`Config`

配置管理类，负责管理应用程序的各种配置选项。

#### 构造函数

```python
Config(env_file: Optional[str] = None)
```

**参数：**
- `env_file`: 环境配置文件路径，默认为 `.env`

#### 主要属性

```python
config = Config()

# API 配置
config.tushare_token        # Tushare API Token
config.tushare_timeout      # API 超时时间（秒）
config.tushare_retry_times  # 重试次数

# 目录配置
config.data_dir     # 数据目录路径
config.cache_dir    # 缓存目录路径
config.charts_dir   # 图表目录路径

# 图表配置
config.chart_width   # 图表宽度
config.chart_height  # 图表高度
config.chart_dpi     # 图表DPI
```

#### 主要方法

```python
# 验证 Token 有效性
is_valid = config.validate_token()

# 获取文件路径
data_path = config.get_data_path("filename.csv")
cache_path = config.get_cache_path("cache_file.json")
chart_path = config.get_chart_path("chart.png")
```

#### 使用示例

```python
from src.tushare_examples.config import Config, get_config

# 使用默认配置
config = get_config()

# 使用自定义配置文件
config = Config("custom.env")

# 检查配置
print(config)
```

## 客户端 (TushareClient)

### 类：`TushareClient`

Tushare API 客户端封装，提供统一的数据访问接口。

#### 构造函数

```python
TushareClient(token: Optional[str] = None)
```

**参数：**
- `token`: Tushare API Token，如果未提供则从配置中获取

#### 股票基本信息

```python
# 获取股票基本信息
stocks = client.get_stock_basic(
    list_status='L',        # 上市状态：L上市 D退市 P暂停
    exchange=None,          # 交易所：SSE上交所 SZSE深交所
    market=None             # 市场：主板 创业板 科创板
)
```

#### K线数据

```python
# 获取日线数据
daily_data = client.get_daily_data(
    ts_code="000001.SZ",           # 股票代码
    start_date="20230101",         # 开始日期
    end_date="20231231"            # 结束日期
)

# 获取周线数据
weekly_data = client.get_weekly_data(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231"
)

# 获取月线数据
monthly_data = client.get_monthly_data(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231"
)
```

#### 财务数据

```python
# 获取利润表
income = client.get_income_statement(
    ts_code="000001.SZ",
    period="20231231",      # 报告期
    report_type="1"         # 报告类型
)

# 获取资产负债表
balance = client.get_balance_sheet(
    ts_code="000001.SZ",
    period="20231231"
)

# 获取现金流量表
cashflow = client.get_cashflow_statement(
    ts_code="000001.SZ",
    period="20231231"
)

# 获取财务指标
indicators = client.get_financial_indicator(
    ts_code="000001.SZ",
    period="20231231"
)
```

#### 数据保存和加载

```python
# 保存数据
client.save_data(data, "filename.csv", format="csv")
client.save_data(data, "filename.json", format="json")
client.save_data(data, "filename.xlsx", format="excel")

# 加载数据
data = client.load_data("filename.csv", format="csv")
```

## 股票基本信息 (StockInfoAnalyzer)

### 类：`StockInfoAnalyzer`

股票基本信息分析器，提供股票筛选和分析功能。

#### 构造函数

```python
StockInfoAnalyzer(client: Optional[TushareClient] = None)
```

#### 主要方法

```python
analyzer = StockInfoAnalyzer()

# 获取所有股票
all_stocks = analyzer.get_all_stocks(save_to_file=True)

# 搜索股票
results = analyzer.search_stocks(
    keyword="茅台",
    search_fields=['symbol', 'name', 'industry']
)

# 按行业筛选
bank_stocks = analyzer.get_stocks_by_industry("银行")

# 按地区筛选
beijing_stocks = analyzer.get_stocks_by_area("北京")

# 按市场筛选
kcb_stocks = analyzer.get_stocks_by_market("科创板")

# 获取最近上市股票
recent_stocks = analyzer.get_recently_listed_stocks(days=30)

# 分析股票分布
analysis = analyzer.analyze_stock_distribution()
```

#### 返回数据格式

股票基本信息 DataFrame 包含以下列：

| 列名 | 描述 | 示例 |
|------|------|------|
| ts_code | 股票代码 | 000001.SZ |
| symbol | 股票简称 | 000001 |
| name | 股票名称 | 平安银行 |
| area | 地域 | 深圳 |
| industry | 行业 | 银行 |
| market | 市场类型 | 主板 |
| list_date | 上市日期 | 19910403 |

## K线分析 (KLineAnalyzer)

### 类：`KLineAnalyzer`

K线数据分析器，提供K线数据获取、技术指标计算和可视化功能。

#### 构造函数

```python
KLineAnalyzer(client: Optional[TushareClient] = None)
```

#### 主要方法

```python
analyzer = KLineAnalyzer()

# 获取K线数据
kline_data = analyzer.get_kline_data(
    ts_code="000001.SZ",
    start_date="20230101",      # 可选，默认最近一年
    end_date="20231231",        # 可选，默认今天
    period="daily"              # daily/weekly/monthly
)

# 绘制蜡烛图
fig = analyzer.plot_candlestick(
    data=kline_data,
    title="股票K线图",
    volume=True,                # 是否显示成交量
    ma_lines=[5, 10, 20],      # 移动平均线
    figsize=(12, 8)
)

# 绘制技术指标图
fig = analyzer.plot_indicators(
    data=kline_data,
    indicators=['MACD', 'RSI', 'KDJ'],
    figsize=(12, 10)
)

# 趋势分析
analysis = analyzer.analyze_trend(kline_data)

# 保存图表
analyzer.save_chart(fig, "chart.png")
```

#### K线数据格式

K线数据 DataFrame 包含以下列：

| 列名 | 描述 |
|------|------|
| trade_date | 交易日期 |
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| vol | 成交量 |
| amount | 成交额 |
| MA5/MA10/MA20 | 移动平均线 |
| RSI | 相对强弱指数 |
| MACD | MACD指标 |
| 其他技术指标 | ... |

## 财务分析 (FinancialAnalyzer)

### 类：`FinancialAnalyzer`

财务数据分析器，提供财务报表分析和可视化功能。

#### 构造函数

```python
FinancialAnalyzer(client: Optional[TushareClient] = None)
```

#### 主要方法

```python
analyzer = FinancialAnalyzer()

# 获取财务报表数据
income_data = analyzer.get_income_statement("600519.SH", years=5)
balance_data = analyzer.get_balance_sheet("600519.SH", years=5)
cashflow_data = analyzer.get_cashflow_statement("600519.SH", years=5)
indicators_data = analyzer.get_financial_indicators("600519.SH", years=5)

# 盈利能力分析
profitability = analyzer.analyze_profitability(income_data)

# 偿债能力分析
solvency = analyzer.analyze_solvency(balance_data)

# 绘制财务趋势图
fig1 = analyzer.plot_financial_trends(income_data)

# 绘制资产负债分析图
fig2 = analyzer.plot_balance_sheet_analysis(balance_data)

# 生成综合财务报告
report = analyzer.generate_financial_report("600519.SH")
```

#### 财务分析结果

盈利能力分析结果：
```python
{
    'revenue_growth_rates': [10.5, 15.2, 8.7],      # 营收增长率
    'avg_revenue_growth': 11.47,                     # 平均营收增长率
    'profit_growth_rates': [12.3, 18.5, 6.2],       # 利润增长率
    'avg_profit_growth': 12.33,                      # 平均利润增长率
    'gross_margins': [45.2, 47.8, 46.5],            # 毛利率
    'avg_gross_margin': 46.5,                        # 平均毛利率
    'net_margins': [25.1, 26.8, 24.9],              # 净利率
    'avg_net_margin': 25.6                           # 平均净利率
}
```

## 技术指标 (TechnicalIndicators)

### 类：`TechnicalIndicators`

技术指标计算器，提供各种技术指标的计算功能。

#### 静态方法

```python
# 简单移动平均线
ma = TechnicalIndicators.sma(data['close'], window=20)

# 指数移动平均线
ema = TechnicalIndicators.ema(data['close'], window=20)

# MACD指标
macd_result = TechnicalIndicators.macd(
    data['close'], 
    fast_period=12,
    slow_period=26,
    signal_period=9
)

# RSI指标
rsi = TechnicalIndicators.rsi(data['close'], window=14)

# 布林带
bb_result = TechnicalIndicators.bollinger_bands(
    data['close'],
    window=20,
    num_std=2
)

# KDJ指标
kdj_result = TechnicalIndicators.kdj(
    data['high'],
    data['low'], 
    data['close']
)
```

#### 批量计算

```python
calculator = TechnicalIndicators()

# 计算所有指标
data_with_indicators = calculator.calculate_all_indicators(kline_data)

# 生成交易信号
signals = calculator.get_trading_signals(data_with_indicators)
```

## 数据可视化 (StockVisualizer)

### 类：`StockVisualizer`

股票数据可视化器，提供多种图表绘制功能。

#### 构造函数

```python
StockVisualizer()
```

#### K线图

```python
visualizer = StockVisualizer()

# 专业K线图（使用mplfinance）
fig = visualizer.plot_candlestick_mplfinance(
    data=kline_data,
    title="股票K线图",
    ma_periods=[5, 10, 20],
    volume=True,
    style='charles'
)

# 交互式K线图（使用plotly）
fig = visualizer.plot_interactive_candlestick(
    data=kline_data,
    title="交互式K线图",
    ma_periods=[5, 10, 20],
    volume=True
)
```

#### 技术指标图

```python
# 静态技术指标图
fig = visualizer.plot_technical_indicators(
    data=kline_data,
    indicators=['MACD', 'RSI', 'KDJ'],
    interactive=False
)

# 交互式技术指标图
fig = visualizer.plot_technical_indicators(
    data=kline_data,
    indicators=['MACD', 'RSI', 'KDJ'],
    interactive=True
)
```

#### 对比图表

```python
# 多股票价格对比
stock_data_dict = {
    "000001.SZ": kline_data1,
    "600036.SH": kline_data2,
    "601166.SH": kline_data3
}

fig = visualizer.plot_comparison_chart(
    data_dict=stock_data_dict,
    price_column='close',
    normalize=True,        # 标准化处理
    interactive=False
)

# 相关性热图
fig = visualizer.plot_correlation_heatmap(
    data_dict=stock_data_dict,
    price_column='close'
)
```

#### 保存图表

```python
# 保存静态图表
visualizer.save_chart(matplotlib_fig, "chart.png", format="png")

# 保存交互式图表
visualizer.save_chart(plotly_fig, "chart.html", format="html")
```

## 错误处理

所有 API 都包含完善的错误处理机制：

```python
from src.tushare_examples.client import TushareClientError

try:
    client = TushareClient()
    data = client.get_stock_basic()
except TushareClientError as e:
    print(f"API调用失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 数据格式

### 日期格式

- 输入日期格式：`YYYYMMDD`（如：`20230101`）
- 输出日期格式：`pandas.Timestamp` 或 `datetime`

### 股票代码格式

- 深交所：`000001.SZ`、`300001.SZ`（创业板）
- 上交所：`600001.SH`、`688001.SH`（科创板）

### 数据单位

- 价格：元
- 成交量：股
- 成交额：元
- 财务数据：元（部分指标为万元或亿元，详见字段说明）

## 性能优化建议

1. **批量获取**：尽量使用批量API减少调用次数
2. **数据缓存**：启用缓存功能避免重复请求
3. **适当延时**：遵守API调用频率限制
4. **数据筛选**：只获取需要的时间范围和字段

## 常见问题

### Q: 如何处理缺失数据？

```python
# 检查空数据
if data.empty:
    print("数据为空")

# 处理缺失值
data = data.dropna()  # 删除缺失行
data = data.fillna(0)  # 填充为0
```

### Q: 如何自定义图表样式？

```python
# 修改颜色配置
visualizer.colors['up'] = '#ff0000'    # 上涨颜色
visualizer.colors['down'] = '#00ff00'  # 下跌颜色

# 自定义图表大小
fig = visualizer.plot_candlestick_mplfinance(
    data, figsize=(16, 10)
)
```

### Q: 如何扩展新的技术指标？

```python
class CustomIndicators(TechnicalIndicators):
    @staticmethod
    def custom_indicator(data, window=20):
        # 实现自定义指标逻辑
        return data.rolling(window).apply(custom_function)
```

这就是完整的 API 文档。如需更多详细信息，请参考源代码中的文档字符串。