# Engine 核心模块

雪球爬虫项目的核心引擎模块，提供认证、数据存储、爬虫服务等核心功能。

## 📁 模块结构

```
engine/
├── __init__.py
├── README.md                 # 本文档
├── auto_cookie.py           # 自动Cookie生成器
├── crawler_service.py       # 爬虫服务层
├── csv_storage.py          # CSV存储管理器
├── database.py             # 数据库连接和操作
├── logger.py               # 日志配置模块
├── xueqiu_auth.py         # 雪球认证系统
└── xueqiu_deobfuscator.js  # JavaScript反混淆代码
```

## 🔧 核心组件

### 1. 认证系统 (`xueqiu_auth.py`)

雪球认证管理器，负责Cookie的获取、验证和会话管理。

#### 主要功能：
- ✅ 自动Cookie生成和验证
- ✅ 认证状态检查（游客/登录状态）
- ✅ 会话管理和资源优化
- ✅ Cookie过期处理

#### 使用示例：
```python
from engine.xueqiu_auth import get_auth, get_authenticated_session

# 获取认证状态
auth = get_auth()
status = auth.get_auth_status()
print(f"认证状态: {status['message']}")

# 获取已认证的会话
session = get_authenticated_session()
response = session.get('https://xueqiu.com')
```

### 2. 自动Cookie生成器 (`auto_cookie.py`)

基于逆向工程的Cookie自动生成，专注于反爬虫参数处理。

#### 主要功能：
- 🍪 自动获取雪球基础Cookie
- 🔒 生成acw_sc__v2反爬虫参数
- ⚡ JavaScript执行优化（超时控制、资源管理）
- 🛡️ 备用生成算法

#### 使用示例：
```python
from engine.auto_cookie import get_auto_cookie_generator

generator = get_auto_cookie_generator()
cookies = generator.generate_fresh_cookies()
```

### 3. 数据存储系统

#### 3.1 数据库管理 (`database.py`)

高性能数据库连接池和操作接口。

**特性：**
- 🏊 连接池复用（默认5个连接，最大10个）
- 🔗 线程安全的连接管理
- ⚡ 批量操作支持
- 🛡️ 连接有效性检查

**使用示例：**
```python
from engine.database import DatabaseManager, StockRepository

# 创建数据库管理器
db_manager = DatabaseManager(pool_size=5)

# 使用上下文管理器
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stocks")
    result = cursor.fetchall()
```

#### 3.2 CSV存储管理器 (`csv_storage.py`)

高效的CSV文件存储，支持大数据处理。

**特性：**
- 📦 分块读写（10K写入/50K读取）
- 🗂️ 自动目录管理
- 📊 大文件检测（50MB阈值）
- 💾 备份和导出功能

**使用示例：**
```python
from engine.csv_storage import CSVStorage

# 创建存储管理器
storage = CSVStorage(csv_path='data/csv')

# 保存数据（支持分块）
storage.save_to_csv(data, 'stock_list', chunk_size=10000)

# 按日期保存K线数据
storage.save_kline_data_by_date(kline_data, '2023-12-01')
```

### 4. 统一数据仓库 (`database.py` 中的 `DataRepository`)

提供统一的存储接口，支持数据库和CSV两种模式。

**特性：**
- 🔄 存储类型切换（database/csv）
- 📊 存储信息查询
- 📝 批量数据操作
- 💾 自动备份

**使用示例：**
```python
from engine.database import DataRepository

# 创建数据仓库（自动从配置读取存储类型）
repo = DataRepository()

# 保存股票数据
repo.save_stock_basic_info(stock_data)

# 获取未处理的股票列表
unprocessed = repo.get_unprocessed_financial_stocks()
```

### 5. 爬虫服务层 (`crawler_service.py`)

高级爬虫服务，封装所有爬虫操作。

**功能模块：**
- 📈 股票列表爬取
- 🏢 公司信息爬取  
- 💰 财务数据爬取
- 📊 K线数据爬取
- 🔄 存储类型切换

**使用示例：**
```python
from engine.crawler_service import CrawlerService

# 创建爬虫服务
service = CrawlerService(storage_type='database')

# 执行完整爬取流程
service.run_full_crawl()

# 或单独执行特定爬取
service.run_stock_list_crawl()
service.run_company_info_crawl()
```

### 6. 日志系统 (`logger.py`)

统一的日志配置和管理。

**特性：**
- 📝 结构化日志格式
- 📁 自动日志文件管理
- 🎛️ 可配置日志级别
- 🖥️ 控制台和文件双重输出

**使用示例：**
```python
from engine.logger import get_logger

logger = get_logger(__name__)
logger.info("操作开始")
logger.error("发生错误", exc_info=True)
```

## ⚙️ 配置说明

Engine模块依赖 `config/settings.py` 中的配置：

```python
# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'xueqiu',
    'charset': 'utf8mb4'
}

# 存储配置
STORAGE_CONFIG = {
    'type': 'database',  # 'database' 或 'csv'
    'csv_path': 'data/csv',
    'csv_encoding': 'utf-8-sig',
    'backup_path': 'data/backup'
}

# 爬虫配置
CRAWLER_CONFIG = {
    'max_retries': 3,
    'timeout': 30,
    'request_delay': 1,
    'page_size': 100
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'logs/xueqiu_crawler.log'
}
```

## 🚀 性能优化

### 已实施的优化措施：

1. **连接池优化** - 减少50-80%数据库连接开销
2. **分块处理** - 支持GB级数据文件处理
3. **会话管理** - 1小时会话过期，避免资源泄漏
4. **JavaScript执行** - 5秒超时，进程组管理
5. **内存优化** - 大文件流式处理，防止内存溢出

### 性能指标：

- 🏊 **数据库连接**: 池化复用，最大并发10连接
- 📦 **CSV处理**: 10K条/块写入，50K条/块读取
- ⏱️ **请求超时**: JavaScript 5秒，HTTP 30秒
- 💾 **内存控制**: 50MB文件自动分块处理

## 🔄 使用流程

### 典型使用场景：

1. **初始化认证**
   ```python
   from engine.xueqiu_auth import get_auth
   auth = get_auth()
   status = auth.get_auth_status()
   ```

2. **创建爬虫服务**
   ```python
   from engine.crawler_service import CrawlerService
   service = CrawlerService()
   ```

3. **执行数据爬取**
   ```python
   # 完整爬取
   service.run_full_crawl()
   
   # 或单独爬取
   service.run_stock_list_crawl()
   ```

4. **数据存储查询**
   ```python
   storage_info = service.get_storage_info()
   print(storage_info)
   ```

## 🛠️ 扩展开发

### 添加新的存储类型：

1. 在 `DataRepository` 中添加新的存储类型判断
2. 实现对应的存储管理器类
3. 更新配置文件

### 添加新的爬虫服务：

1. 在 `crawlers/` 目录创建新的爬虫类
2. 继承 `BaseCrawler` 基类
3. 在 `CrawlerService` 中添加对应方法

## 📝 注意事项

1. **Cookie管理**: Cookie会自动过期，需要定期更新
2. **连接池**: 使用完毕后建议调用 `close_all_connections()`
3. **大文件**: CSV文件超过50MB会自动分块处理
4. **日志级别**: 生产环境建议使用 `INFO` 级别
5. **会话清理**: 长期运行的应用建议定期调用 `cleanup_session()`

## 🐛 故障排除

### 常见问题：

1. **Cookie验证失败**
   - 检查网络连接
   - 重新运行 `python get_cookie.py`

2. **数据库连接错误**
   - 检查数据库配置
   - 确认数据库服务状态

3. **CSV文件权限错误**
   - 检查目录权限
   - 确认磁盘空间充足

4. **JavaScript执行超时**
   - 检查Node.js安装
   - 网络连接问题

## 📞 技术支持

如有问题，请检查：
1. 日志文件：`logs/xueqiu_crawler.log`
2. 配置文件：`config/settings.py`
3. Cookie状态：运行认证测试

---

*最后更新：2025-11-22*