# 快速开始指南

本指南将帮助您在 5 分钟内开始使用 Tushare 股票数据获取示例项目。

## 第一步：环境准备

### 1.1 检查 Python 版本

```bash
python --version
# 确保版本 >= 3.7
```

### 1.2 下载项目

```bash
# 如果有 git
git clone <repository-url>
cd tushare_example

# 或者直接下载解压
```

### 1.3 安装依赖

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 第二步：获取 Tushare Token

### 2.1 注册账号

1. 访问 [Tushare Pro官网](https://tushare.pro/)
2. 点击右上角"注册"
3. 填写邮箱和密码完成注册
4. 验证邮箱

### 2.2 获取 Token

1. 登录后进入"个人中心"
2. 在"API Token"页面复制你的token
3. Token 格式类似：`1234567890abcdef1234567890abcdef12345678`

### 2.3 配置 Token

```bash
# 复制配置模板
cp .env.template .env

# 编辑 .env 文件（使用任意文本编辑器）
# 将 your_tushare_token_here 替换为你的实际token
```

.env 文件内容示例：
```
TUSHARE_TOKEN=1234567890abcdef1234567890abcdef12345678
TUSHARE_TIMEOUT=30
TUSHARE_RETRY_TIMES=3
DATA_DIR=./data
CACHE_DIR=./cache
CHART_WIDTH=1200
CHART_HEIGHT=800
CHART_DPI=100
```

## 第三步：运行第一个示例

### 3.1 测试基本功能

```bash
python main_demo.py --demo basic
```

这将运行股票基本信息查询演示，如果成功，你会看到：
- 股票列表获取成功
- 搜索功能演示
- 各种筛选示例

### 3.2 运行完整演示

```bash
python main_demo.py
```

这将依次运行所有演示模块：
1. 股票基本信息查询
2. 数据可视化功能
3. K线数据分析（需要有效token）
4. 财务数据分析（需要有效token）

## 第四步：查看生成的文件

演示运行后，会在以下目录生成文件：

```
tushare_example/
├── data/                    # 数据文件
│   ├── all_stocks.csv      # 所有股票信息
│   └── ...
├── charts/                  # 图表文件
│   ├── demo_candlestick.png # K线图
│   ├── demo_indicators.png  # 技术指标图
│   └── ...
├── cache/                   # 缓存文件
└── tushare_demo.log        # 运行日志
```

## 第五步：尝试具体功能

### 5.1 分析特定股票

```bash
# 分析平安银行（000001.SZ）最近180天的数据
python main_demo.py --stock 000001.SZ --days 180

# 分析贵州茅台（600519.SH）
python main_demo.py --stock 600519.SH --demo kline
```

### 5.2 运行股票筛选器

```bash
python examples/stock_screener.py
```

这将运行智能股票筛选，根据多种条件筛选出优质股票。

### 5.3 多股票对比分析

```bash
python examples/stock_comparison.py
```

这将对比分析几只银行股的表现。

## 常见问题

### Q1: 提示 "Tushare token 未设置或无效"

**解决方案：**
1. 检查 `.env` 文件是否存在
2. 确认 token 是否正确复制（没有多余空格）
3. 确认 Tushare 账号状态正常

### Q2: 提示 "API 调用失败"

**可能原因：**
1. 网络连接问题
2. API 调用频率过高
3. 数据权限不足

**解决方案：**
1. 检查网络连接
2. 等待几分钟后重试
3. 登录 Tushare 查看账号积分和权限

### Q3: 图表无法显示

**解决方案：**
1. 确保安装了 matplotlib：`pip install matplotlib`
2. 如果是远程服务器，图表会保存到 charts 目录
3. 检查字体配置，某些系统可能需要额外字体

### Q4: 某些股票数据获取失败

**可能原因：**
1. 股票代码格式不正确
2. 股票已退市或暂停交易
3. 数据暂时不可用

**解决方案：**
1. 检查股票代码格式（如：000001.SZ、600519.SH）
2. 尝试其他活跃股票
3. 查看日志文件了解详细错误信息

## 下一步

现在你已经成功运行了基本示例，可以：

1. **学习源代码**：查看 `src/tushare_examples/` 目录了解实现细节
2. **自定义分析**：修改参数和条件，分析你感兴趣的股票
3. **扩展功能**：基于现有代码添加新的分析功能
4. **阅读文档**：查看 `README.md` 了解更多功能

## 获取帮助

如果遇到问题：

1. 查看 `tushare_demo.log` 日志文件
2. 参考 `README.md` 详细文档
3. 查看 Tushare 官方文档
4. 提交 Issue 反馈问题

祝您使用愉快！🎉