"""
高级使用示例
"""
import sys
import os
import asyncio
import schedule
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.crawler_service import CrawlerService
from crawlers.stock_crawler import StockCrawler
from database.database import DataRepository
from utils.logger import get_logger


def example_scheduled_crawling():
    """定时爬取示例"""
    print("=== 定时爬取示例 ===")
    
    def scheduled_job():
        """定时任务"""
        print(f"开始执行定时任务: {datetime.now()}")
        
        try:
            crawler_service = CrawlerService()
            
            # 只爬取股票列表（示例）
            print("执行股票列表爬取...")
            # crawler_service.run_stock_list_crawl()
            
            print("定时任务完成")
            
        except Exception as e:
            print(f"定时任务失败: {e}")
    
    # 设置定时任务
    print("设置定时任务...")
    
    # 每天上午9点执行
    schedule.every().day.at("09:00").do(scheduled_job)
    
    # 每小时执行一次
    # schedule.every().hour.do(scheduled_job)
    
    # 每10分钟执行一次
    # schedule.every(10).minutes.do(scheduled_job)
    
    print("定时任务已设置，按Ctrl+C退出")
    
    try:
        # 运行调度器（这里只演示几次）
        for i in range(3):
            schedule.run_pending()
            time.sleep(1)
            print(f"检查调度器... {i+1}")
        
        print("调度器演示完成")
        
    except KeyboardInterrupt:
        print("调度器已停止")


def example_async_crawling():
    """异步爬取示例"""
    print("=== 异步爬取示例 ===")
    
    import aiohttp
    import asyncio
    
    class AsyncStockCrawler:
        """异步股票爬虫"""
        
        def __init__(self):
            self.base_url = "https://xueqiu.com"
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
            }
        
        async def fetch_stock_data(self, session, symbol):
            """异步获取股票数据"""
            url = f"{self.base_url}/stock/quote.json?symbol={symbol}"
            
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return symbol, data
                    else:
                        return symbol, None
                        
            except Exception as e:
                print(f"获取 {symbol} 失败: {e}")
                return symbol, None
        
        async def crawl_multiple_stocks(self, symbols):
            """异步爬取多个股票"""
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self.fetch_stock_data(session, symbol) 
                    for symbol in symbols
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_results = []
                for result in results:
                    if isinstance(result, tuple) and result[1] is not None:
                        successful_results.append(result)
                
                return successful_results
    
    # 使用异步爬虫
    async def run_async_crawler():
        symbols = ['SZ000001', 'SZ000002', 'SH600000', 'SH600001']
        
        async_crawler = AsyncStockCrawler()
        results = await async_crawler.crawl_multiple_stocks(symbols)
        
        print(f"异步爬取完成，成功: {len(results)}/{len(symbols)}")
        for symbol, data in results:
            print(f"  {symbol}: 数据获取成功")
        
        return results
    
    # 运行异步爬虫
    try:
        asyncio.run(run_async_crawler())
    except Exception as e:
        print(f"异步爬取失败: {e}")


def example_data_pipeline():
    """数据处理管道示例"""
    print("=== 数据处理管道示例 ===")
    
    class DataPipeline:
        """数据处理管道"""
        
        def __init__(self):
            self.processors = []
        
        def add_processor(self, processor):
            """添加处理器"""
            self.processors.append(processor)
            return self
        
        def process(self, data):
            """处理数据"""
            result = data
            for i, processor in enumerate(self.processors):
                try:
                    result = processor(result)
                    print(f"处理器 {i+1} 完成")
                except Exception as e:
                    print(f"处理器 {i+1} 失败: {e}")
                    break
            
            return result
    
    # 定义处理器
    def data_validator(data):
        """数据验证处理器"""
        if not data:
            raise ValueError("数据为空")
        return data
    
    def data_cleaner(data):
        """数据清洗处理器"""
        if isinstance(data, dict):
            # 移除空值
            cleaned = {k: v for k, v in data.items() if v is not None}
            return cleaned
        return data
    
    def data_transformer(data):
        """数据转换处理器"""
        if isinstance(data, dict):
            # 转换数据类型
            if 'price' in data:
                try:
                    data['price'] = float(data['price'])
                except (ValueError, TypeError):
                    data['price'] = 0.0
        return data
    
    def data_enricher(data):
        """数据增强处理器"""
        if isinstance(data, dict):
            # 添加时间戳
            data['processed_at'] = datetime.now().isoformat()
        return data
    
    # 使用数据管道
    pipeline = DataPipeline()
    pipeline.add_processor(data_validator)
    pipeline.add_processor(data_cleaner)
    pipeline.add_processor(data_transformer)
    pipeline.add_processor(data_enricher)
    
    # 测试数据
    test_data = {
        'symbol': 'SZ000001',
        'name': '平安银行',
        'price': '10.50',
        'volume': 1000000,
        'market_cap': None  # 这个会被清洗掉
    }
    
    print("原始数据:", test_data)
    
    processed_data = pipeline.process(test_data)
    print("处理后数据:", processed_data)


def example_cache_management():
    """缓存管理示例"""
    print("=== 缓存管理示例 ===")
    
    import json
    import hashlib
    from functools import wraps
    
    class CacheManager:
        """缓存管理器"""
        
        def __init__(self, cache_dir='cache'):
            self.cache_dir = cache_dir
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
        
        def _get_cache_key(self, key):
            """生成缓存键"""
            return hashlib.md5(key.encode()).hexdigest()
        
        def _get_cache_path(self, cache_key):
            """获取缓存文件路径"""
            return os.path.join(self.cache_dir, f"{cache_key}.json")
        
        def get(self, key, max_age_hours=1):
            """获取缓存"""
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            
            if not os.path.exists(cache_path):
                return None
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # 检查是否过期
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time > timedelta(hours=max_age_hours):
                    os.remove(cache_path)
                    return None
                
                return cache_data['data']
                
            except Exception as e:
                print(f"读取缓存失败: {e}")
                return None
        
        def set(self, key, data):
            """设置缓存"""
            cache_key = self._get_cache_key(key)
            cache_path = self._get_cache_path(cache_key)
            
            try:
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
                return True
                
            except Exception as e:
                print(f"写入缓存失败: {e}")
                return False
        
        def clear(self):
            """清空缓存"""
            try:
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                return True
            except Exception as e:
                print(f"清空缓存失败: {e}")
                return False
    
    def cached_function(cache_manager, max_age_hours=1):
        """缓存装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
                
                # 尝试从缓存获取
                cached_result = cache_manager.get(cache_key, max_age_hours)
                if cached_result is not None:
                    print(f"从缓存获取: {func.__name__}")
                    return cached_result
                
                # 执行函数并缓存结果
                print(f"执行函数: {func.__name__}")
                result = func(*args, **kwargs)
                cache_manager.set(cache_key, result)
                
                return result
            return wrapper
        return decorator
    
    # 使用缓存管理器
    cache_manager = CacheManager()
    
    @cached_function(cache_manager, max_age_hours=0.1)  # 6分钟过期
    def expensive_operation(symbol):
        """模拟耗时操作"""
        time.sleep(1)  # 模拟1秒的操作
        return f"数据_{symbol}_{datetime.now().second}"
    
    # 测试缓存
    print("第一次调用（会执行函数）:")
    result1 = expensive_operation('SZ000001')
    print(f"结果: {result1}")
    
    print("\n第二次调用（从缓存获取）:")
    result2 = expensive_operation('SZ000001')
    print(f"结果: {result2}")
    
    print(f"\n缓存测试完成，结果相同: {result1 == result2}")


def example_monitoring():
    """监控示例"""
    print("=== 监控示例 ===")
    
    class CrawlerMonitor:
        """爬虫监控器"""
        
        def __init__(self):
            self.stats = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'start_time': datetime.now(),
                'errors': []
            }
        
        def record_request(self, success=True, error=None):
            """记录请求"""
            self.stats['total_requests'] += 1
            
            if success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
                if error:
                    self.stats['errors'].append({
                        'timestamp': datetime.now().isoformat(),
                        'error': str(error)
                    })
        
        def get_success_rate(self):
            """获取成功率"""
            if self.stats['total_requests'] == 0:
                return 0.0
            return self.stats['successful_requests'] / self.stats['total_requests']
        
        def get_runtime(self):
            """获取运行时间"""
            return datetime.now() - self.stats['start_time']
        
        def get_stats(self):
            """获取统计信息"""
            runtime = self.get_runtime()
            return {
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': f"{self.get_success_rate():.2%}",
                'runtime': str(runtime),
                'requests_per_minute': self.stats['total_requests'] / max(runtime.total_seconds() / 60, 1),
                'recent_errors': self.stats['errors'][-5:]  # 最近5个错误
            }
        
        def print_stats(self):
            """打印统计信息"""
            stats = self.get_stats()
            print("爬虫监控统计:")
            print(f"  总请求数: {stats['total_requests']}")
            print(f"  成功请求数: {stats['successful_requests']}")
            print(f"  失败请求数: {stats['failed_requests']}")
            print(f"  成功率: {stats['success_rate']}")
            print(f"  运行时间: {stats['runtime']}")
            print(f"  请求速率: {stats['requests_per_minute']:.2f} 请求/分钟")
            
            if stats['recent_errors']:
                print("  最近错误:")
                for error in stats['recent_errors']:
                    print(f"    {error['timestamp']}: {error['error']}")
    
    # 使用监控器
    monitor = CrawlerMonitor()
    
    # 模拟一些请求
    for i in range(10):
        import random
        success = random.random() > 0.3  # 70%成功率
        error = None if success else f"模拟错误 {i}"
        
        monitor.record_request(success, error)
        time.sleep(0.1)
    
    # 显示统计信息
    monitor.print_stats()


def example_configuration_management():
    """配置管理示例"""
    print("=== 配置管理示例 ===")
    
    import json
    
    class ConfigManager:
        """配置管理器"""
        
        def __init__(self, config_file='config.json'):
            self.config_file = config_file
            self.config = self.load_config()
        
        def load_config(self):
            """加载配置"""
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"加载配置失败: {e}")
            
            # 默认配置
            return {
                'crawler': {
                    'request_delay': 0.3,
                    'max_retries': 3,
                    'timeout': 30
                },
                'database': {
                    'host': 'localhost',
                    'port': 3311
                },
                'logging': {
                    'level': 'INFO'
                }
            }
        
        def save_config(self):
            """保存配置"""
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"保存配置失败: {e}")
                return False
        
        def get(self, key, default=None):
            """获取配置值"""
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        
        def set(self, key, value):
            """设置配置值"""
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            return self.save_config()
        
        def update_config(self, updates):
            """批量更新配置"""
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict:
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(self.config, updates)
            return self.save_config()
    
    # 使用配置管理器
    config_manager = ConfigManager('examples/test_config.json')
    
    print("当前配置:")
    print(f"  爬虫延迟: {config_manager.get('crawler.request_delay')}")
    print(f"  数据库主机: {config_manager.get('database.host')}")
    print(f"  日志级别: {config_manager.get('logging.level')}")
    
    # 修改配置
    print("\n修改配置...")
    config_manager.set('crawler.request_delay', 0.5)
    config_manager.set('new_section.new_key', 'new_value')
    
    # 批量更新
    config_manager.update_config({
        'crawler': {
            'max_retries': 5,
            'new_crawler_setting': True
        }
    })
    
    print("配置已更新并保存")
    
    # 清理测试文件
    if os.path.exists('examples/test_config.json'):
        os.remove('examples/test_config.json')
        print("测试配置文件已清理")


def main():
    """主函数"""
    logger = get_logger(__name__)
    
    try:
        # 示例1: 定时爬取
        example_scheduled_crawling()
        
        # 示例2: 异步爬取
        example_async_crawling()
        
        # 示例3: 数据处理管道
        example_data_pipeline()
        
        # 示例4: 缓存管理
        example_cache_management()
        
        # 示例5: 监控
        example_monitoring()
        
        # 示例6: 配置管理
        example_configuration_management()
        
        print("高级使用示例完成！")
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()