# Crawlers 目录说明

本目录包含雪球股票数据爬虫的核心模块，负责从雪球网站获取各种类型的股票数据。

## 📁 目录结构

```
crawlers/
├── __init__.py                 # 包初始化文件
├── base_crawler.py            # 爬虫基类
├── company_info_crawler.py    # 公司信息爬虫
├── financial_crawler.py       # 财务指标爬虫
├── financial_statements_crawler.py  # 财务报表爬虫 ⭐
├── kline_crawler.py           # K线数据爬虫
├── stock_info_crawler.py      # 股票基础信息爬虫
└── readme.md                  # 本文件
```

## 🚀 爬虫模块详解

### 1. base_crawler.py - 爬虫基类
所有爬虫的基类，提供通用功能：
- 会话管理和Cookie处理
- 配置文件加载
- 日志记录
- 错误处理机制

### 2. stock_info_crawler.py - 股票基础信息爬虫
**功能**：获取股票基础信息
- 获取股票列表（A股全部）
- 获取单只股票详细信息
- 批量获取股票信息
- 按板块获取股票

**输出字段**：
```
symbol, name, code, market, industry, area, pe, pb, market_cap, flow_cap
```

### 3. kline_crawler.py - K线数据爬虫 ⭐
**功能**：获取股票K线数据，支持多种模式

#### 🎯 核心功能
1. **历史K线数据**：获取单只股票完整历史日线数据
2. **全市场日频数据**：获取某一天全市场所有股票的日频数据
3. **批量处理**：支持批量处理多只股票
4. **断点续传**：支持恢复未完成的爬取任务

#### 📊 支持的复权类型
- `before`：前复权
- `after`：后复权  
- `none`：不复权

#### 🎛️ 主要方法
```python
# 获取全市场某日数据（推荐）
crawler.crawl_market_daily_data('2025-11-22', 'after')

# 获取单只股票历史数据
crawler.crawl_single_stock_kline('SZ000001', 'after')

# 批量获取历史数据
crawler.crawl_kline_data('after', max_stocks=100)

# 恢复未完成的爬取
crawler.resume_crawl('after')
```

#### 📋 输出字段
```csv
symbol,timestamp,volume,open,high,low,close,chg,percent,turnoverrate,period,type,crawl_time,crawl_date
```

### 4. company_info_crawler.py - 公司信息爬虫
**功能**：获取上市公司详细信息

**输出字段**：
```
compcode, compsname, compname, engname, founddate, regcapital, chairman, manager, regaddr, officeaddr, ...
```

### 5. financial_crawler.py - 财务指标爬虫
**功能**：获取公司财务指标数据

**📊 数据类型说明**：
雪球API提供的是**财务指标数据**，包含以下类别：

#### 🎯 每股指标 (6个)
- `basiceps`：基本每股收益
- `epsdiluted`：稀释每股收益  
- `epsweighted`：加权每股收益
- `naps`：每股净资产
- `opercashpershare`：每股经营现金流
- `peropecashpershare`：每股净资产现金流
- `totalshare`：总股本

#### 💰 盈利能力指标 (7个)
- `salegrossprofitrto`：销售毛利率
- `mainbusiincome`：主营业务收入
- `mainbusiprofit`：主营业务利润
- `totprofit`：利润总额
- `netprofit`：净利润
- `dilutedroe`：稀释ROE
- `weightedroe`：加权ROE

#### 📈 成长性指标 (4个)
- `netassgrowrate`：净资产增长率
- `mainbusincgrowrate`：主营收入增长率
- `netincgrowrate`：净利润增长率
- `totassgrowrate`：总资产增长率

#### 🏦 资产负债指标 (3个)
- `totalassets`：总资产
- `totalliab`：总负债
- `totsharequi`：股东权益

#### 💵 现金流指标 (6个)
- `operrevenue`：营业收入
- `invnetcashflow`：投资现金流
- `finnetcflow`：筹资现金流
- `chgexchgchgs`：汇率变动影响
- `cashnetr`：现金净增加额
- `cashequfinbal`：现金及等价物余额

### 6. financial_statements_crawler.py - 财务报表爬虫 ⭐
**功能**：获取完整的三张财务报表数据

#### 📋 支持的报表类型
1. **利润表 (Income Statement)**：反映企业经营成果
2. **资产负债表 (Balance Sheet)**：反映企业财务状况
3. **现金流量表 (Cash Flow Statement)**：反映企业现金流动情况

#### 🎯 核心功能
- **完整报表数据**：获取详细的财务报表科目，而非简单的财务指标
- **多期间数据**：支持获取多个报告期间的数据
- **数据格式化**：自动处理数据格式和单位转换
- **财务分析**：内置财务比率计算和分析功能
- **Excel导出**：支持生成专业的Excel财务分析报告

#### 📊 报表科目示例

**利润表主要科目**：
```
营业收入, 营业成本, 毛利润, 营业利润, 利润总额, 净利润
基本每股收益, 稀释每股收益, 其他综合收益, 综合收益总额
```

**资产负债表主要科目**：
```
货币资金, 应收账款, 存货, 流动资产合计, 非流动资产合计, 资产总计
流动负债合计, 非流动负债合计, 负债合计, 所有者权益合计, 负债和所有者权益总计
```

**现金流量表主要科目**：
```
经营活动现金流量小计, 投资活动现金流量小计, 筹资活动现金流量小计
现金及现金等价物净增加额, 期初现金及现金等价物余额, 期末现金及现金等价物余额
```

#### 🛠️ 主要方法
```python
# 获取单只股票的三张报表
crawler.crawl_financial_statements('SZ000001', count=8)

# 获取利润表
income_data = crawler.get_income_statement('SZ000001', count=8)

# 获取资产负债表
balance_data = crawler.get_balance_sheet('SZ000001', count=8)

# 获取现金流量表
cash_flow_data = crawler.get_cash_flow_statement('SZ000001', count=8)

# 生成Excel财务分析报告
crawler.generate_excel_report('SZ000001', 'financial_report.xlsx')
```

#### 📋 输出字段
每张报表包含以下通用字段：
```
symbol, name, report_date, report_type, crawl_time
```

加上各报表的详细财务科目数据

#### 💡 财务分析功能
- **资产结构分析**：流动资产/非流动资产比例
- **负债结构分析**：流动负债/非流动负债比例  
- **偿债能力分析**：流动比率、速动比率、资产负债率
- **盈利能力分析**：ROE、ROA、毛利率、净利率
- **现金流分析**：经营现金流/营业收入比例
- **成长性分析**：收入增长率、利润增长率

**⚠️ 重要说明**：
- `financial_crawler.py` 提供的是**财务指标**数据，适合快速筛选和分析
- `financial_statements_crawler.py` 提供的是**完整财务报表**，适合深度财务分析
- 两者可以配合使用，满足不同层次的财务分析需求

## 🛠️ 使用示例

### 基本使用

#### K线数据爬虫
```python
from crawlers.kline_crawler import KlineCrawler
from engine.database import DataRepository

# 初始化爬虫
crawler = KlineCrawler(DataRepository())

# 获取全市场今日数据
crawler.crawl_market_daily_data('2025-11-22', 'after')

# 获取单只股票数据
data = crawler.crawl_single_stock_kline('SZ000001', 'after')
```

#### 财务报表爬虫
```python
from crawlers.financial_statements_crawler import FinancialStatementsCrawler
from engine.database import DataRepository

# 初始化爬虫
crawler = FinancialStatementsCrawler(DataRepository())

# 获取单只股票的三张报表
statements = crawler.crawl_financial_statements('SZ000001', count=8)

# 生成Excel财务分析报告
crawler.generate_excel_report('SZ000001', 'financial_report.xlsx')

# 获取特定报表
income = crawler.get_income_statement('SZ000001', count=8)
balance = crawler.get_balance_sheet('SZ000001', count=8)
cash_flow = crawler.get_cash_flow_statement('SZ000001', count=8)
```

### 批量处理
```python
# 限制处理数量
crawler.crawl_kline_data('after', max_stocks=50)

# 恢复未完成的任务
crawler.resume_crawl('after')
```

## ⚙️ 配置说明

爬虫配置文件位于 `config/` 目录：
- `crawler_config.json`：爬虫基础配置
- `database_config.json`：数据库配置

## 📝 日志和错误处理

- 日志文件位于 `logs/` 目录
- 支持自动重试机制（默认3次）
- 详细的错误信息和统计报告

## 🔑 认证要求

所有爬虫都需要有效的雪球Cookie：
1. 浏览器登录雪球：https://xueqiu.com
2. 运行 `python get_cookie.py` 获取Cookie
3. Cookie会自动保存供后续使用

## 📊 数据存储

支持多种存储方式：
- **CSV文件**：按日期/股票代码分类存储
- **MySQL数据库**：结构化存储，支持复杂查询
- **混合模式**：CSV + 数据库

## 🚨 注意事项

1. **请求频率**：内置请求间隔，避免被限制
2. **数据准确性**：建议在交易日获取实时数据
3. **存储空间**：历史数据可能占用较大空间
4. **合规性**：请遵守雪球的使用条款

## 🔄 更新日志

- **v2.2**：新增完整财务报表爬虫，支持利润表、资产负债表、现金流量表
- **v2.1**：优化财务指标爬虫，增强数据格式化
- **v2.0**：新增全市场日频数据获取功能
- **v1.5**：添加断点续传和批量处理
- **v1.0**：基础爬虫功能

## 📞 技术支持

如有问题，请检查：
1. Cookie是否有效
2. 网络连接是否正常
3. 日志文件中的错误信息
4. 配置文件是否正确