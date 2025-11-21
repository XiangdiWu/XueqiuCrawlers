# 使用示例

本目录包含了雪球股票数据爬虫项目的全面使用示例，涵盖了从基础使用到高级功能的各个方面。

## 示例文件说明

### 1. basic_usage.py - 基础使用示例
- 演示如何使用 `CrawlerService` 执行完整的爬取流程
- 展示如何分别执行各个爬虫功能
- 适合初学者快速上手

```bash
python examples/basic_usage.py
```

### 2. individual_crawlers.py - 单独爬虫使用示例
- 演示如何单独使用各个爬虫类
- 包含 `StockCrawler`、`FinancialCrawler`、`KlineCrawler` 的使用
- 适合需要精细控制爬取过程的场景

```bash
python examples/individual_crawlers.py
```

### 3. database_operations.py - 数据库操作示例
- 演示 `DatabaseManager` 和 `StockRepository` 的使用
- 包含查询、插入、更新等数据库操作
- 展示如何直接操作数据库

```bash
python examples/database_operations.py
```

### 4. custom_crawler.py - 自定义爬虫示例
- 演示如何扩展基础爬虫类
- 展示如何创建自定义爬虫
- 包含批量爬取、自定义重试策略等高级功能

```bash
python examples/custom_crawler.py
```

### 5. configuration_example.py - 配置使用示例
- 演示如何使用和修改配置
- 展示环境变量配置、自定义配置等
- 包含配置验证功能

```bash
python examples/configuration_example.py
```

### 6. error_handling.py - 错误处理示例
- 演示各种错误处理策略
- 包含重试机制、优雅关闭、资源清理等
- 展示如何构建健壮的爬虫应用

```bash
python examples/error_handling.py
```

### 7. batch_processing.py - 批处理示例
- 演示不同的批处理策略
- 包含顺序处理、多线程处理、进度跟踪等
- 展示检查点处理和错误恢复

```bash
python examples/batch_processing.py
```

### 8. testing_example.py - 测试示例
- 演示如何为爬虫项目编写测试
- 包含单元测试、集成测试、性能测试等
- 展示Mock测试和压力测试

```bash
python examples/testing_example.py
```

### 9. advanced_usage.py - 高级使用示例
- 演示高级功能和设计模式
- 包含定时任务、异步爬取、数据管道等
- 展示缓存管理、监控和配置管理

```bash
python examples/advanced_usage.py
```

## 运行环境要求

确保已安装所需依赖：

```bash
pip install -r requirements.txt
```

部分高级示例可能需要额外依赖：

```bash
# 异步支持
pip install aiohttp

# 定时任务
pip install schedule

# 进度条
pip install tqdm

# 多线程支持（内置）
# 无需额外安装
```

## 使用建议

### 初学者路径
1. 先运行 `basic_usage.py` 了解基本用法
2. 学习 `database_operations.py` 了解数据库操作
3. 查看 `configuration_example.py` 学习配置管理

### 进阶用户路径
1. 学习 `custom_crawler.py` 扩展功能
2. 掌握 `error_handling.py` 提高稳定性
3. 使用 `batch_processing.py` 优化性能

### 高级用户路径
1. 研究 `testing_example.py` 确保代码质量
2. 探索 `advanced_usage.py` 实现复杂功能
3. 结合多个示例构建完整解决方案

## 注意事项

1. **数据库配置**: 运行前请确保数据库配置正确
2. **网络环境**: 部分示例需要网络连接
3. **权限要求**: Cookie获取需要Chrome浏览器
4. **性能考虑**: 批量操作时注意控制请求频率
5. **日志查看**: 详细日志保存在 `logs/` 目录

## 自定义示例

可以根据自己的需求修改示例代码：

1. 修改配置参数适应不同环境
2. 调整爬取策略满足特定需求
3. 扩展数据处理逻辑
4. 添加新的监控和告警功能

## 常见问题

### Q: 示例运行失败怎么办？
A: 检查以下几点：
- 依赖是否安装完整
- 数据库配置是否正确
- 网络连接是否正常
- 日志文件中的错误信息

### Q: 如何调整爬取频率？
A: 修改 `config/settings.py` 中的 `CRAWLER_CONFIG` 配置

### Q: 如何添加新的数据源？
A: 参考 `custom_crawler.py` 中的示例，继承 `BaseCrawler` 类

### Q: 如何处理大量数据？
A: 参考 `batch_processing.py` 中的批处理和分页策略

## 贡献

欢迎提交新的示例代码或改进建议！