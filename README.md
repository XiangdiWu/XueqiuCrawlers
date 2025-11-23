# 🚀 雪球股票数据爬虫系统

一个功能完整的雪球股票数据采集系统，支持获取股票基础信息、K线数据、公司信息和财务数据。

## ✨ 主要特性

- 🎯 **全市场数据采集**：支持获取全市场所有股票的日频数据
- 📊 **多数据类型**：股票信息、K线数据、公司信息、财务数据、完整财务报表
- 🔄 **断点续传**：支持恢复未完成的爬取任务
- 📁 **灵活存储**：支持CSV文件和MySQL数据库存储
- 🛡️ **鲁棒性强**：内置重试机制和错误处理
- 📈 **实时更新**：支持获取最新交易日数据
- 🎛️ **交互式菜单**：友好的命令行界面
- 📋 **财务分析**：支持生成Excel财务分析报表

## 📋 系统要求

- Python 3.7+
- MySQL (可选，用于数据库存储)
- 稳定的网络连接

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

**主要依赖包**：
- `requests`：HTTP请求库
- `pymysql`：MySQL数据库连接
- `pandas`：数据处理
- `openpyxl`：Excel文件操作（财务报表功能）
- `schedule`：定时任务
- `aiohttp`：异步HTTP请求

### 2. 获取雪球Cookie
```bash
# 浏览器登录雪球后运行
python get_cookie.py
```

### 3. 运行程序
```bash
python run.py
```

## 📊 功能模块

### 🎯 核心功能

| 功能 | 描述 | 数据类型 |
|------|------|----------|
| 📈 K线数据 | 股票历史价格和成交量 | OHLCV数据 |
| 🏢 公司信息 | 上市公司基础信息 | 基本面数据 |
| 💰 财务数据 | 关键财务指标 | 财务指标 |
| 📋 财务报表 | 完整三张财务报表 | 利润表/资产负债表/现金流量表 |
| 📊 股票列表 | A股股票基础信息 | 股票目录 |

### 🔥 特色功能

#### 全市场日频数据采集 ⭐
```python
# 获取某一天全市场所有股票的数据
crawler.crawl_market_daily_data('2025-11-22', 'after')
```

**输出示例**：
```csv
symbol,timestamp,volume,open,high,low,close,chg,percent,turnoverrate,period,type,crawl_time,crawl_date
SZ000001,1732214400.0,15000000,10.50,10.80,10.20,10.75,0.25,2.38,1.25,day,after,2025-11-22 20:00:00,2025-11-22
SZ000002,1732214400.0,12000000,8.30,8.50,8.10,8.45,0.15,1.81,0.95,day,after,2025-11-22 20:00:00,2025-11-22
...
```

## 📁 项目结构

```
XueqiuCrawlers/
├── 📂 crawlers/              # 爬虫模块
│   ├── base_crawler.py       # 爬虫基类
│   ├── kline_crawler.py      # K线数据爬虫 ⭐
│   ├── stock_info_crawler.py # 股票信息爬虫
│   ├── company_info_crawler.py # 公司信息爬虫
│   ├── financial_crawler.py  # 财务数据爬虫
│   ├── financial_statements_crawler.py # 财务报表爬虫 ⭐
│   └── readme.md             # 爬虫模块说明
├── 📂 engine/                # 核心引擎
│   ├── database.py           # 数据库操作
│   ├── csv_storage.py        # CSV存储
│   ├── xueqiu_auth.py        # 认证管理
│   └── logger.py             # 日志系统
├── 📂 config/                 # 配置文件
├── 📂 data/                   # 数据存储
│   └── csv/                  # CSV文件
├── 📂 logs/                   # 日志文件
├── 📂 recycling/              # 参考代码
├── get_cookie.py             # Cookie获取工具
├── run.py                    # 主程序入口
└── requirements.txt          # 依赖列表
```

## 🎮 使用指南

### 启动程序
```bash
python run.py
```

### 主菜单选项
```
==================================================
🚀 雪球股票数据爬虫
==================================================
1. 爬取公司信息（不必需）
2. 获取股票信息（完整字段）
3. 创建股票列表（简化字段，不必需）
4. 爬取日频K线数据（按日期存储） ⭐
5. 爬取财务数据（按证券代码存储）
6. 爬取完整财务报表（利润表/资产负债表/现金流量表）🆕
7. 爬取所有数据
0. 退出
==================================================
```

### K线数据菜单
```
📊 K线数据爬取选项
========================================
1. 爬取所有股票K线数据（后复权）
2. 爬取所有股票K线数据（前复权）
3. 爬取所有股票K线数据（不复权）
4. 爬取指定数量股票K线数据
5. 爬取单只股票K线数据
6. 恢复爬取（只处理未完成的股票）
7. 🆕 爬取全市场股票某日数据 ⭐
8. 查看K线数据
9. 查看处理进度
0. 返回主菜单
```

## 📊 数据格式

### K线数据字段
| 字段 | 描述 | 示例 |
|------|------|------|
| symbol | 股票代码 | SZ000001 |
| timestamp | 时间戳 | 1732214400.0 |
| open | 开盘价 | 10.50 |
| high | 最高价 | 10.80 |
| low | 最低价 | 10.20 |
| close | 收盘价 | 10.75 |
| volume | 成交量 | 15000000 |
| chg | 涨跌额 | 0.25 |
| percent | 涨跌幅 | 2.38 |
| turnoverrate | 换手率 | 1.25 |

### 财务数据字段（31个指标）

#### 🎯 每股指标
| 字段 | 描述 | 示例 |
|------|------|------|
| basiceps | 基本每股收益 | 1.39 |
| epsdiluted | 稀释每股收益 | 1.35 |
| naps | 每股净资产 | 12.82 |
| opercashpershare | 每股经营现金流 | 2.15 |

#### 💰 盈利能力指标
| 字段 | 描述 | 示例 |
|------|------|------|
| netprofit | 净利润 | 1000000000 |
| mainbusiincome | 主营业务收入 | 5000000000 |
| dilutedroe | 稀释ROE | 15.2 |
| salegrossprofitrto | 销售毛利率 | 25.8 |

#### 📈 成长性指标
| 字段 | 描述 | 示例 |
|------|------|------|
| netincgrowrate | 净利润增长率 | 10.5 |
| mainbusincgrowrate | 主营收入增长率 | 8.3 |

#### 🏦 资产负债指标
| 字段 | 描述 | 示例 |
|------|------|------|
| totalassets | 总资产 | 50000000000 |
| totalliab | 总负债 | 30000000000 |
| totsharequi | 股东权益 | 20000000000 |

#### 💵 现金流指标
| 字段 | 描述 | 示例 |
|------|------|------|
| operrevenue | 营业收入 | 5000000000 |
| invnetcashflow | 投资现金流 | -500000000 |
| cashnetr | 现金净增加额 | 100000000 |

**⚠️ 注意**：雪球API提供的是财务指标，非完整财务报表。如需完整财务报表，请使用财务报表爬虫功能。

## 🛠️ 高级配置

### 数据库配置
编辑 `config/database_config.json`：
```json
{
  "host": "localhost",
  "port": 3306,
  "user": "your_username",
  "password": "your_password",
  "database": "stock_data"
}
```

### 爬虫配置
编辑 `config/crawler_config.json`：
```json
{
  "timeout": 30,
  "max_retries": 3,
  "request_delay": 0.3,
  "batch_size": 100
}
```

## 📝 使用示例

### Python API 使用
```python
from crawlers.kline_crawler import KlineCrawler
from crawlers.financial_statements_crawler import FinancialStatementsCrawler
from engine.database import DataRepository

# 初始化爬虫
kline_crawler = KlineCrawler(DataRepository())
statements_crawler = FinancialStatementsCrawler(DataRepository())

# 获取全市场今日数据
kline_crawler.crawl_market_daily_data('2025-11-22', 'after')

# 获取单只股票历史数据
data = kline_crawler.crawl_single_stock_kline('SZ000001', 'after')

# 获取完整财务报表
statements = statements_crawler.get_all_statements('SZ000001')

# 生成财务分析报告
statements_crawler.generate_financial_analysis_report('SZ000001', generate_excel=True)

# 批量处理
kline_crawler.crawl_kline_data('after', max_stocks=50)
```

### 数据查询示例
```python
from engine.csv_storage import CSVStorage

storage = CSVStorage()

# 获取某日全市场数据
data = storage.get_kline_data_by_date('2025-11-22')

# 获取某只股票数据
data = storage.get_kline_data_by_symbol('SZ000001')
```

## 🔧 故障排除

### 常见问题

1. **Cookie失效**
   ```bash
   # 重新获取Cookie
   python get_cookie.py
   ```

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

3. **数据存储失败**
   - 检查磁盘空间
   - 确认写入权限

4. **认证失败**
   - 确认雪球账号状态
   - 重新登录获取Cookie

### 日志查看
```bash
# 查看最新日志
tail -f logs/crawler.log

# 查看错误日志
grep ERROR logs/crawler.log
```

## 📈 性能优化

- **并发处理**：支持多线程爬取
- **批量操作**：减少数据库访问次数
- **缓存机制**：避免重复请求
- **增量更新**：只获取新数据

## 🚨 重要提醒

1. **合规使用**：请遵守雪球网站的使用条款
2. **数据延迟**：非实时数据，可能有延迟
3. **存储空间**：历史数据占用空间较大
4. **网络限制**：避免过于频繁的请求

## 📞 技术支持

- 📧 问题反馈：请提交Issue
- 📖 详细文档：查看各模块README

## 📋 财务报表爬虫 🆕

### 🎯 功能特性
- **完整三张报表**：利润表、资产负债表、现金流量表
- **多API端点**：自动尝试多个雪球API端点，提高成功率
- **断点续传**：支持恢复未完成的报表爬取任务

### 📊 支持的报表类型
| 报表类型 | 描述 | 主要字段 |
|----------|------|----------|
| 利润表 | 收入、成本、利润数据 | total_revenue, net_profit, operating_cost等 |
| 资产负债表 | 资产、负债、权益数据 | total_assets, total_liab, equity等 |
| 现金流量表 | 经营、投资、筹资现金流 | ncf_from_oa, invnetcashflow等 |

### 🛠️ 使用方法
```python
from crawlers.financial_statements_crawler import FinancialStatementsCrawler

# 初始化爬虫
crawler = FinancialStatementsCrawler()

# 获取单只股票所有报表
statements = crawler.get_all_statements('SZ000001')

# 批量爬取财务报表
crawler.crawl_financial_statements()
```

## 🔄 更新日志

### v2.1.0 (2025-11-22)
- ✨ 新增完整财务报表爬虫功能
- 📊 支持利润表、资产负债表、现金流量表
- 🔄 优化API端点选择和错误处理
- 📈 增强财务指标计算功能

### v2.0.0 (2025-11-22)
- ✨ 新增全市场日频数据采集功能
- 🔄 优化K线爬虫，支持多种复权类型
- 🛡️ 增强错误处理和重试机制
- 📊 改进数据存储格式

### v1.5.0
- 🔧 添加断点续传功能
- 📁 支持CSV和数据库混合存储
- 🎛️ 优化交互式菜单

### v1.0.0
- 🚀 初始版本发布
- 📊 基础爬虫功能

## 📄 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

---

**⭐ 如果这个项目对你有帮助，请给个Star！**