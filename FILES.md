# 项目文件清单

本文档列出了 Tushare 股票数据获取示例项目的完整文件结构和说明。

## 📁 项目根目录

```
tushare_example/
├── 📄 README.md                    # 项目主要文档
├── 📄 QUICKSTART.md               # 快速开始指南
├── 📄 API.md                      # API详细文档
├── 📄 FILES.md                    # 本文件清单
├── 📄 requirements.txt            # Python依赖列表
├── 📄 .env.template               # 环境配置模板
├── 📄 main_demo.py               # 主演示脚本
├── 📁 src/                       # 源代码目录
├── 📁 examples/                  # 独立示例脚本
├── 📁 data/                      # 数据文件目录
├── 📁 cache/                     # 缓存目录
└── 📁 charts/                    # 图表输出目录
```

## 📁 源代码目录 (src/)

```
src/tushare_examples/
├── 📄 __init__.py                # 包初始化文件
├── 📄 config.py                  # 配置管理模块
├── 📄 client.py                  # Tushare API客户端
├── 📄 indicators.py              # 技术指标计算模块
├── 📄 visualizer.py              # 数据可视化模块
└── 📁 examples/                  # 示例模块目录
    ├── 📄 __init__.py            # 示例包初始化
    ├── 📄 stock_basic.py         # 股票基本信息示例
    ├── 📄 kline_analysis.py      # K线数据分析示例
    └── 📄 financial_analysis.py  # 财务数据分析示例
```

## 📁 独立示例目录 (examples/)

```
examples/
├── 📄 stock_screener.py          # 智能股票筛选器
└── 📄 stock_comparison.py        # 多股票对比分析
```

## 📄 文件详细说明

### 核心文件

| 文件名 | 大小 | 说明 |
|--------|------|------|
| **README.md** | ~9KB | 项目主要文档，包含完整的使用指南和功能介绍 |
| **QUICKSTART.md** | ~4KB | 5分钟快速开始指南，适合初次使用者 |
| **API.md** | ~12KB | 详细的API文档，包含所有类和方法的说明 |
| **requirements.txt** | ~0.4KB | Python依赖包列表 |
| **.env.template** | ~0.3KB | 环境配置模板文件 |
| **main_demo.py** | ~7KB | 主演示脚本，支持命令行参数 |

### 源代码文件

| 文件路径 | 功能说明 |
|----------|----------|
| **src/tushare_examples/__init__.py** | 包初始化，导出主要类 |
| **src/tushare_examples/config.py** | 配置管理，环境变量、Token管理、目录配置 |
| **src/tushare_examples/client.py** | API客户端，封装Tushare接口，错误处理和重试 |
| **src/tushare_examples/indicators.py** | 技术指标计算，MA、MACD、RSI、KDJ等 |
| **src/tushare_examples/visualizer.py** | 数据可视化，K线图、技术指标图、对比图 |

### 示例模块文件

| 文件路径 | 功能说明 |
|----------|----------|
| **src/tushare_examples/examples/stock_basic.py** | 股票基本信息查询、搜索、筛选功能 |
| **src/tushare_examples/examples/kline_analysis.py** | K线数据获取、技术指标计算、趋势分析 |
| **src/tushare_examples/examples/financial_analysis.py** | 财务报表分析、盈利能力、偿债能力分析 |

### 独立示例文件

| 文件路径 | 功能说明 |
|----------|----------|
| **examples/stock_screener.py** | 智能股票筛选器，多条件筛选和评分系统 |
| **examples/stock_comparison.py** | 多股票对比分析，相关性分析、性能对比 |

## 📁 运行时生成的目录

运行项目后会自动创建以下目录和文件：

### 数据目录 (data/)
```
data/
├── all_stocks.csv                # 所有股票基本信息
├── stock_screening_results_*.csv # 股票筛选结果
└── *.csv/json/xlsx              # 其他保存的数据文件
```

### 图表目录 (charts/)
```
charts/
├── *_candlestick.png            # K线图
├── *_indicators.png             # 技术指标图
├── *_financial_trends.png       # 财务趋势图
├── *_balance_analysis.png       # 资产负债分析图
├── stock_comparison_*.png       # 股票对比图
└── *.html                       # 交互式图表文件
```

### 缓存目录 (cache/)
```
cache/
└── *.cache                      # API响应缓存文件
```

### 日志文件
```
tushare_demo.log                 # 演示运行日志
tushare_examples.log             # 程序运行日志
```

## 🔧 配置文件

### .env 文件配置项

创建 `.env` 文件（从 `.env.template` 复制），配置以下项目：

```bash
# 必需配置
TUSHARE_TOKEN=your_token_here    # Tushare API Token

# 可选配置
TUSHARE_TIMEOUT=30               # API超时时间（秒）
TUSHARE_RETRY_TIMES=3            # 重试次数
DATA_DIR=./data                  # 数据目录
CACHE_DIR=./cache                # 缓存目录
CHARTS_DIR=./charts              # 图表目录
CHART_WIDTH=1200                 # 图表宽度
CHART_HEIGHT=800                 # 图表高度
CHART_DPI=100                    # 图表DPI
LOG_LEVEL=INFO                   # 日志级别
```

## 📦 依赖包说明

主要依赖包及其用途：

| 包名 | 版本要求 | 用途说明 |
|------|----------|----------|
| **tushare** | >=1.2.89 | Tushare数据接口 |
| **pandas** | >=1.3.0 | 数据处理和分析 |
| **numpy** | >=1.21.0 | 数值计算 |
| **matplotlib** | >=3.5.0 | 基础绘图 |
| **seaborn** | >=0.11.0 | 统计图表 |
| **plotly** | >=5.0.0 | 交互式图表 |
| **mplfinance** | >=0.12.0 | 专业金融图表 |
| **python-dotenv** | >=0.19.0 | 环境变量管理 |
| **requests** | >=2.26.0 | HTTP请求 |

可选依赖：
| 包名 | 用途 |
|------|-----|
| **talib** | 更多技术指标计算 |
| **sqlalchemy** | 数据库存储支持 |

## 📊 文件大小统计

| 目录/文件类型 | 文件数量 | 总大小 |
|--------------|----------|--------|
| **文档文件** | 4个 | ~25KB |
| **源代码** | 8个 | ~45KB |
| **示例脚本** | 3个 | ~25KB |
| **配置文件** | 2个 | ~1KB |
| **总计** | 17个 | ~96KB |

## 🎯 文件使用指南

### 新手用户
1. 先阅读 `QUICKSTART.md`
2. 运行 `main_demo.py`
3. 查看生成的示例文件

### 开发者
1. 阅读 `API.md` 了解接口
2. 查看 `src/` 目录下的源代码
3. 参考 `examples/` 目录的高级示例

### 数据分析师
1. 使用 `examples/stock_screener.py` 进行股票筛选
2. 使用 `examples/stock_comparison.py` 进行对比分析
3. 自定义修改参数满足特定需求

## 📝 维护说明

### 添加新功能
1. 在 `src/tushare_examples/` 下创建新模块
2. 在 `examples/` 下创建使用示例
3. 更新 `README.md` 和 `API.md`

### 添加新示例
1. 在 `examples/` 下创建新脚本
2. 在脚本中包含完整的演示代码
3. 更新本文件清单

### 版本发布
1. 更新版本号
2. 更新依赖包版本
3. 测试所有示例脚本
4. 更新文档

---

📚 更多信息请参考各个文档文件，祝您使用愉快！