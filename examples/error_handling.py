"""
错误处理示例
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from services.crawler_service import CrawlerService
from crawlers.base_crawler import BaseCrawler
from database.database import DataRepository
from utils.logger import get_logger


def example_basic_error_handling():
    """基础错误处理示例"""
    print("=== 基础错误处理示例 ===")
    
    try:
        # 创建爬虫服务
        crawler_service = CrawlerService()
        
        # 尝试执行可能失败的操作
        print("尝试执行爬虫操作...")
        # crawler_service.run_stock_list_crawl()
        
    except ConnectionError as e:
        print(f"连接错误: {e}")
        print("建议: 检查网络连接和代理设置")
        
    except TimeoutError as e:
        print(f"超时错误: {e}")
        print("建议: 增加超时时间或检查网络状况")
        
    except Exception as e:
        print(f"未知错误: {e}")
        print("建议: 查看详细日志获取更多信息")


def example_database_error_handling():
    """数据库错误处理示例"""
    print("=== 数据库错误处理示例 ===")
    
    try:
        # 使用错误的数据库配置创建连接
        wrong_config = {
            'host': 'wrong_host',
            'user': 'wrong_user',
            'password': 'wrong_password',
            'db': 'wrong_db',
            'port': 9999,
            'charset': 'utf8mb4'
        }
        
        # 创建数据库管理器（这里会失败）
        # db_manager = DatabaseManager()
        # db_manager.config = wrong_config
        
        print("尝试连接数据库...")
        # result = db_manager.execute_query("SELECT 1")
        
    except ConnectionRefusedError as e:
        print(f"数据库连接被拒绝: {e}")
        print("建议: 检查数据库服务是否运行，端口是否正确")
        
    except Exception as e:
        print(f"数据库错误: {e}")
        print("建议: 检查数据库配置和网络连接")


def example_crawler_error_handling():
    """爬虫错误处理示例"""
    print("=== 爬虫错误处理示例 ===")
    
    class SafeCrawler(BaseCrawler):
        """安全爬虫示例"""
        
        def safe_request(self, url):
            """安全请求方法"""
            try:
                response = self.make_request(url)
                return response
                
            except requests.exceptions.ConnectionError as e:
                print(f"网络连接错误: {e}")
                return None
                
            except requests.exceptions.Timeout as e:
                print(f"请求超时: {e}")
                return None
                
            except requests.exceptions.HTTPError as e:
                print(f"HTTP错误: {e}")
                return None
                
            except Exception as e:
                print(f"未知错误: {e}")
                return None
        
        def crawl_with_fallback(self, symbol):
            """带回退机制的爬取"""
            urls = [
                f"{self.config['base_url']}/stock/quote.json?symbol={symbol}",
                f"{self.config['stock_base_url']}/v5/stock/quote.json?symbol={symbol}",
            ]
            
            for i, url in enumerate(urls):
                print(f"尝试第 {i+1} 个URL: {url}")
                
                response = self.safe_request(url)
                if response and response.status_code == 200:
                    return response.json()
                
                # 如果不是最后一次尝试，等待一下
                if i < len(urls) - 1:
                    self.delay()
            
            print("所有URL都尝试失败")
            return None
    
    # 使用安全爬虫
    safe_crawler = SafeCrawler()
    
    # 测试错误处理
    # result = safe_crawler.crawl_with_fallback('INVALID_SYMBOL')
    # print(f"结果: {result}")


def example_retry_mechanism():
    """重试机制示例"""
    print("=== 重试机制示例 ===")
    
    import time
    import random
    
    def unreliable_operation():
        """模拟不可靠的操作"""
        # 50%的概率失败
        if random.random() < 0.5:
            raise Exception("随机失败")
        return "成功"
    
    def operation_with_retry(max_retries=3, delay=1):
        """带重试的操作"""
        for attempt in range(max_retries):
            try:
                print(f"尝试第 {attempt + 1} 次...")
                result = unreliable_operation()
                print(f"操作成功: {result}")
                return result
                
            except Exception as e:
                print(f"操作失败: {e}")
                
                if attempt < max_retries - 1:
                    print(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    print("已达到最大重试次数")
                    raise
    
    # 测试重试机制
    try:
        result = operation_with_retry()
        print(f"最终结果: {result}")
    except Exception as e:
        print(f"操作最终失败: {e}")


def example_logging_error_handling():
    """日志错误处理示例"""
    print("=== 日志错误处理示例 ===")
    
    logger = get_logger('error_example')
    
    # 记录不同级别的错误
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    # 记录异常
    try:
        # 模拟错误
        result = 1 / 0
        
    except Exception as e:
        logger.error(f"发生异常: {e}", exc_info=True)
        print("异常已记录到日志")


def example_graceful_shutdown():
    """优雅关闭示例"""
    print("=== 优雅关闭示例 ===")
    
    import signal
    import sys
    
    class GracefulCrawler:
        def __init__(self):
            self.running = True
            self.setup_signal_handlers()
        
        def setup_signal_handlers(self):
            """设置信号处理器"""
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
        
        def signal_handler(self, signum, frame):
            """信号处理器"""
            print(f"\n收到信号 {signum}，准备优雅关闭...")
            self.running = False
        
        def run(self):
            """运行爬虫"""
            count = 0
            while self.running and count < 10:
                print(f"处理第 {count + 1} 项...")
                count += 1
                
                # 模拟处理时间
                import time
                time.sleep(1)
            
            if self.running:
                print("正常完成")
            else:
                print("被中断，优雅退出")
    
    # 测试优雅关闭（在实际使用中，可以按Ctrl+C测试）
    crawler = GracefulCrawler()
    # crawler.run()


def example_resource_cleanup():
    """资源清理示例"""
    print("=== 资源清理示例 ===")
    
    class ResourceCrawler:
        def __init__(self):
            self.connections = []
            self.files = []
        
        def create_resources(self):
            """创建资源"""
            print("创建资源...")
            # 模拟创建数据库连接
            self.connections.append(f"connection_{len(self.connections)}")
            # 模拟打开文件
            self.files.append(f"file_{len(self.files)}")
        
        def cleanup_resources(self):
            """清理资源"""
            print("清理资源...")
            # 关闭连接
            for conn in self.connections:
                print(f"关闭连接: {conn}")
            self.connections.clear()
            
            # 关闭文件
            for file in self.files:
                print(f"关闭文件: {file}")
            self.files.clear()
        
        def work(self):
            """工作方法"""
            try:
                self.create_resources()
                print("执行工作...")
                # 模拟可能失败的工作
                # raise Exception("工作失败")
                
            except Exception as e:
                print(f"工作失败: {e}")
                raise
            finally:
                # 无论成功失败都要清理资源
                self.cleanup_resources()
    
    # 测试资源清理
    crawler = ResourceCrawler()
    crawler.work()


def main():
    """主函数"""
    logger = get_logger('example_error')
    
    try:
        # 示例1: 基础错误处理
        example_basic_error_handling()
        
        # 示例2: 数据库错误处理
        example_database_error_handling()
        
        # 示例3: 爬虫错误处理
        example_crawler_error_handling()
        
        # 示例4: 重试机制
        example_retry_mechanism()
        
        # 示例5: 日志错误处理
        example_logging_error_handling()
        
        # 示例6: 优雅关闭
        example_graceful_shutdown()
        
        # 示例7: 资源清理
        example_resource_cleanup()
        
        print("错误处理示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()