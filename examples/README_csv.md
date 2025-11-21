# CSV存储功能说明

## 概述

项目现在支持两种存储模式：
- **数据库模式**: 使用MySQL数据库存储数据
- **CSV模式**: 使用CSV文件存储数据

通过配置文件可以一键切换存储方式，两种模式提供完全相同的API接口。

## 配置说明

### 存储配置 (config/settings.py)

```python
STORAGE_CONFIG = {
    'type': 'database',  # 'database' 或 'csv'
    'csv_path': 'data/csv',  # CSV文件存储路径
    'csv_encoding': 'utf-8-sig',  # CSV编码，支持Excel
    'create_backup': True,  # 是否创建备份
    'backup_path': 'data/backup'  # 备份路径
}
```

### 切换存储方式

#### 方法1: 修改配置文件
编辑 `config/settings.py`，修改 `STORAGE_CONFIG['type']` 的值：
- `'database'`: 使用数据库存储
- `'csv'`: 使用CSV文件存储

#### 方法2: 命令行参数
```bash
# 使用数据库存储
python main.py --type stock --storage database

# 使用CSV存储
python main.py --type stock --storage csv
```

#### 方法3: 代码中指定
```python
# 数据库模式
service = CrawlerService(storage_type='database')

# CSV模式
service = CrawlerService(storage_type='csv')
```

## CSV文件结构

### 目录结构
```
data/csv/
├── stocks/           # 股票基本信息
│   ├── stock_list.csv
│   └── stock_info.csv
├── companies/        # 公司信息
│   └── company_profile.csv
├── financial/        # 财务数据
│   ├── financial_data.csv
│   └── finmain_log.csv
└── kline/           # K线数据
    └── kline_data.csv
```

### 文件说明

#### stock_list.csv
股票列表和基本信息
- symbol: 股票代码
- name: 股票名称
- current: 当前价格
- percent: 涨跌幅
- volume: 成交量
- amount: 成交额
- marketcapital: 市值
- pe_ttm: 市盈率
- high52w: 52周最高
- low52w: 52周最低

#### company_profile.csv
公司详细信息
- compcode: 公司代码
- compname: 公司名称
- engname: 英文名称
- founddate: 成立日期
- regcapital: 注册资本
- chairman: 董事长
- manager: 总经理
- leconstant: 所在地
- accfirm: 会计师事务所
- regaddr: 注册地址
- officeaddr: 办公地址
- compintro: 公司介绍
- bizscope: 经营范围
- majorbiz: 主营业务
- compsname: 股票简称
- region: 地区

#### financial_data.csv
财务数据
- compcode: 公司代码
- reportdate: 报告期
- basiceps: 基本每股收益
- epsdiluted: 稀释每股收益
- epsweighted: 加权每股收益
- naps: 每股净资产
- opercashpershare: 每股经营现金流
- peropecashpershare: 每股现金流量净额
- netassgrowrate: 净资产增长率
- dilutedroe: 稀释净资产收益率
- weightedroe: 加权净资产收益率
- mainbusincgrowrate: 主营业务收入增长率
- netincgrowrate: 净利润增长率
- totassgrowrate: 总资产增长率
- salegrossprofitrto: 销售毛利率
- mainbusiincome: 主营业务收入
- mainbusiprofit: 主营业务利润
- totprofit: 利润总额
- netprofit: 净利润
- totalassets: 总资产
- totalliab: 总负债
- totsharequi: 股东权益合计
- operrevenue: 营业收入
- invnetcashflow: 投资现金流净额
- finnetcflow: 筹资现金流净额
- chgexchgchgs: 汇率变动影响
- cashnetr: 现金及现金等价物净增加额
- cashequfinbal: 现金及现金等价物余额

#### kline_data.csv
K线数据
- symbol: 股票代码
- timestamp: 时间戳
- volume: 成交量
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- chg: 涨跌额
- percent: 涨跌幅
- turnoverrate: 换手率
- period: 周期 (day/week/month)
- type: 类型 (before/after)

## 使用示例

### 基础使用
```python
from database.database import DataRepository

# CSV模式
repo = DataRepository(storage_type='csv')

# 保存股票数据
stock_data = {
    'symbol': 'SH600000',
    'name': '浦发银行',
    'current': 10.50,
    'percent': 2.5
}
repo.save_stock_basic_info(stock_data)

# 读取数据
stocks = repo.get_stock_symbols()
```

### CSV存储高级功能
```python
from database.csv_storage import CSVStorage

# 初始化CSV存储
csv_storage = CSVStorage(csv_path='data/my_csv')

# 保存数据
csv_storage.save_to_csv(data, 'stock_list')

# 追加数据（避免重复）
csv_storage.append_data(data, 'stock_list', 'symbol')

# 创建备份
csv_storage.create_backup('stock_list')

# 导出到Excel
csv_storage.export_to_excel(['stock_list', 'company_profile'], 'output.xlsx')

# 获取文件信息
info = csv_storage.get_file_info('stock_list')
```

## 命令行使用

### 基本命令
```bash
# 使用默认存储方式爬取所有数据
python main.py --type all

# 指定使用CSV存储
python main.py --type all --storage csv

# 指定使用数据库存储
python main.py --type all --storage database

# 只爬取股票列表
python main.py --type stock --storage csv
```

### 信息查询
```bash
# 查看当前存储信息
python main.py --info

# 查看CSV存储信息
python main.py --info --storage csv

# 查看数据库存储信息
python main.py --info --storage database
```

### 备份操作
```bash
# 创建备份
python main.py --backup

# 为CSV存储创建备份
python main.py --backup --storage csv
```

## 性能对比

### CSV模式优势
- 无需数据库服务器
- 数据易于查看和编辑
- 便于数据交换和分享
- 适合小规模数据

### 数据库模式优势
- 高性能查询
- 支持复杂SQL查询
- 适合大规模数据
- 更好的数据完整性

### 性能测试结果
- 小规模数据（<1000条）：CSV模式更快
- 大规模数据（>10000条）：数据库模式更快
- 查询操作：数据库模式明显更快
- 写入操作：小数据量CSV更快，大数据量数据库更快

## 最佳实践

### 选择存储方式
1. **开发测试阶段**: 使用CSV模式，便于调试
2. **生产环境**: 使用数据库模式，性能更好
3. **数据交换**: 使用CSV模式，便于导出
4. **大规模应用**: 使用数据库模式

### CSV文件管理
1. 定期清理旧文件
2. 创建备份避免数据丢失
3. 使用合适的编码（utf-8-sig支持Excel）
4. 定期导出Excel进行数据分析

### 配置建议
1. 开发环境：`type: 'csv'`
2. 生产环境：`type: 'database'`
3. 数据备份：`create_backup: True`
4. 编码设置：`csv_encoding: 'utf-8-sig'`

## 故障排除

### 常见问题
1. **CSV文件乱码**: 使用 `utf-8-sig` 编码
2. **Excel打不开**: 检查文件编码和格式
3. **数据重复**: 使用 `append_data` 方法避免重复
4. **性能问题**: 大数据量建议使用数据库模式

### 错误处理
所有操作都包含完善的错误处理和日志记录，可以通过日志文件排查问题。

## 扩展功能

### 自定义CSV存储
```python
from database.csv_storage import CSVStorage

# 自定义路径和编码
csv_storage = CSVStorage(
    csv_path='custom/path',
    encoding='gbk'  # 支持中文编码
)
```

### 数据转换
```python
# CSV转Excel
csv_storage.export_to_excel(table_names, 'output.xlsx')

# 批量数据处理
for data in batch_data:
    csv_storage.append_data(data, 'table_name', 'unique_key')
```