# 雪球股票数据爬虫

这是一个重构后的雪球股票数据爬虫项目，采用分层架构设计，具有更好的可维护性和扩展性。

## 项目结构

```
xueqiu/
├── config/                 # 配置文件
│   └── settings.py        # 应用配置
├── database/              # 数据库层
│   └── database.py       # 数据库操作
├── utils/                 # 工具类
│   ├── cookie_manager.py  # Cookie管理
│   └── logger.py         # 日志配置
├── crawlers/              # 爬虫层
│   ├── base_crawler.py    # 基础爬虫类
│   ├── stock_crawler.py   # 股票数据爬虫
│   ├── financial_crawler.py # 财务数据爬虫
│   └── kline_crawler.py   # K线数据爬虫
├── services/              # 服务层
│   └── crawler_service.py # 爬虫服务
├── logs/                  # 日志目录
├── main.py               # 主程序入口
├── requirements.txt      # 依赖包
└── README.md            # 项目说明
```

## 功能特性

1. **分层架构**: 采用配置层、数据库层、工具层、爬虫层、服务层的分层设计
2. **模块化**: 每个功能模块独立，便于维护和扩展
3. **错误处理**: 完善的异常处理和重试机制
4. **日志记录**: 详细的日志记录，便于调试和监控
5. **配置管理**: 集中的配置管理，便于环境切换
6. **数据库连接池**: 使用上下文管理器管理数据库连接

## 安装依赖

```bash
pip install -r requirements.txt
```

## 🔐 Cookie配置

### 方式一：手动配置（推荐）

为了保护隐私，推荐使用手动配置Cookie：

```bash
# 交互式配置Cookie
python setup_cookies.py

# 或者直接运行
python -c "from utils.manual_cookie import ManualCookieManager; ManualCookieManager.interactive_setup()"
```

#### 获取Cookie步骤：
1. 在Chrome浏览器中登录雪球网站 (https://xueqiu.com)
2. 按F12打开开发者工具
3. 点击 Network（网络）标签
4. 刷新页面，找到任意一个xueqiu.com的请求
5. 在请求头中找到 'Cookie' 字段
6. 复制Cookie值，提取需要的部分

#### 必需的Cookie项：
- `u`: 用户ID（登录后会有具体数值，游客为0）
- `s`: 会话ID（登录后生成）

### 方式二：自动获取（需要系统权限）

项目也支持自动从Chrome浏览器获取Cookie，但需要系统权限：

```bash
# 测试自动获取Cookie
python test_keychain.py
```

⚠️ **注意**: 自动获取会访问系统钥匙串，可能涉及隐私风险。

### 检查Cookie状态

```bash
# 检查当前Cookie配置状态
python -c "from utils.manual_cookie import ManualCookieManager; ManualCookieManager.check_cookie_status()"
```

## 使用方法

### 爬取所有数据
```bash
python main.py --type all
```

### 只爬取股票列表
```bash
python main.py --type stock
```

### 只爬取公司信息
```bash
python main.py --type company
```

### 只爬取财务数据
```bash
python main.py --type financial
```

### 只爬取K线数据
```bash
python main.py --type kline
```

## 配置说明

主要配置在 `config/settings.py` 文件中：

- **数据库配置**: 修改 `DATABASE_CONFIG` 中的数据库连接信息
- **爬虫配置**: 修改 `CRAWLER_CONFIG` 中的请求延迟、重试次数等
- **日志配置**: 修改 `LOG_CONFIG` 中的日志级别和输出文件

## 数据库表结构

项目需要以下数据库表：

1. **stocks**: 股票基本信息表
2. **comp**: 公司信息表  
3. **finmain**: 主要财务数据表
4. **kline**: K线数据表
5. **finmain_log**: 财务数据处理日志表
6. **kline_log**: K线数据处理日志表

## 注意事项

1. 需要安装Chrome浏览器，用于获取Cookie
2. 确保数据库连接配置正确
3. 爬取速度不宜过快，避免被限制访问
4. 日志目录会自动创建

## 架构优势

相比原始版本，重构后的架构具有以下优势：

1. **可维护性**: 代码结构清晰，职责分离明确
2. **可扩展性**: 易于添加新的爬虫功能
3. **可测试性**: 各模块独立，便于单元测试
4. **可配置性**: 集中配置管理，支持不同环境
5. **健壮性**: 完善的错误处理和日志记录