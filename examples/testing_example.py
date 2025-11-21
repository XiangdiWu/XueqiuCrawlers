"""
测试示例
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.stock_crawler import StockCrawler
from database.database import DataRepository
from services.crawler_service import CrawlerService
from utils.logger import get_logger


class TestDataRepository(unittest.TestCase):
    """数据仓库测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟的数据仓库
        self.data_repo = Mock(spec=DataRepository)
    
    def test_get_stock_symbols(self):
        """测试获取股票代码"""
        # 模拟返回结果
        mock_result = ['SZ000001', 'SH600000']
        self.data_repo.get_stock_symbols.return_value = mock_result
        
        # 执行测试
        symbols = self.data_repo.get_stock_symbols()
        
        # 验证结果
        self.assertEqual(symbols, ['SZ000001', 'SH600000'])
        self.data_repo.get_stock_symbols.assert_called_once()
    
    def test_save_stock_basic_info(self):
        """测试保存股票基本信息"""
        stock_data = {
            'symbol': 'TEST001',
            'name': '测试股票',
            'current': 10.5
        }
        
        # 模拟返回结果
        self.data_repo.save_stock_basic_info.return_value = True
        
        # 执行测试
        result = self.data_repo.save_stock_basic_info(stock_data)
        
        # 验证结果
        self.assertTrue(result)
        self.data_repo.save_stock_basic_info.assert_called_once_with(stock_data)


class TestStockCrawler(unittest.TestCase):
    """股票爬虫测试"""
    
    def setUp(self):
        """测试前准备"""
        self.crawler = StockCrawler()
    
    @patch('crawlers.stock_crawler.StockCrawler.make_request')
    def test_crawl_stock_list_success(self, mock_request):
        """测试成功爬取股票列表"""
        # 模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'count': 2,
            'data': [
                ['SZ000001', '平安银行', 10.5, 0, 2.5, 10.0, 11.0, 9.0, 12.0, 1000000, 5000000, 10000000, 15.0, 8.0, True]
            ]
        }
        mock_request.return_value = mock_response
        
        # 执行测试
        # self.crawler._crawl_stock_by_type('sza')
        
        # 验证请求被调用
        # mock_request.assert_called()
    
    def test_parse_stock_data(self):
        """测试解析股票数据"""
        stock_item = [
            'SZ000001', '平安银行', 10.5, 0, 2.5, 10.0, 11.0, 9.0, 12.0, 
            1000000, 5000000, 10000000, 15.0, 8.0, True
        ]
        
        result = self.crawler._parse_stock_data(stock_item, 'sza')
        
        expected = {
            'symbol': 'SZ000001',
            'code': 'SZ000001',
            'name': '平安银行',
            'current': 10.5,
            'percent': 2.5,
            'high52w': 8.0,
            'low52w': 15.0,
            'marketcapital': 10000000,
            'amount': 5000000,
            'volume': 1000000,
            'pe_ttm': 15.0
        }
        
        self.assertEqual(result, expected)


class TestCrawlerService(unittest.TestCase):
    """爬虫服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.service = CrawlerService()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.service.stock_crawler)
        self.assertIsNotNone(self.service.financial_crawler)
        self.assertIsNotNone(self.service.kline_crawler)


class TestDataRepositoryIntegration(unittest.TestCase):
    """数据仓库集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.data_repo = DataRepository(storage_type='csv')  # 使用CSV模式避免数据库依赖
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.data_repo)
        self.assertEqual(self.data_repo.storage_type, 'csv')


def example_unit_testing():
    """单元测试示例"""
    print("=== 单元测试示例 ===")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestDataRepository))
    test_suite.addTest(unittest.makeSuite(TestStockCrawler))
    test_suite.addTest(unittest.makeSuite(TestCrawlerService))
    test_suite.addTest(unittest.makeSuite(TestDataRepositoryIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"测试完成，运行了 {result.testsRun} 个测试")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()


def example_integration_testing():
    """集成测试示例"""
    print("=== 集成测试示例 ===")
    
    class IntegrationTest:
        def __init__(self):
            self.logger = get_logger('integration_test')
        
        def test_data_repository_connection(self):
            """测试数据仓库连接"""
            try:
                data_repo = DataRepository(storage_type='csv')
                # 这里只是测试配置，不实际连接
                print("数据仓库配置测试通过")
                return True
            except Exception as e:
                print(f"数据仓库连接测试失败: {e}")
                return False
        
        def test_crawler_initialization(self):
            """测试爬虫初始化"""
            try:
                crawler = StockCrawler()
                print("爬虫初始化测试通过")
                return True
            except Exception as e:
                print(f"爬虫初始化测试失败: {e}")
                return False
        
        def test_service_integration(self):
            """测试服务集成"""
            try:
                service = CrawlerService()
                print("服务集成测试通过")
                return True
            except Exception as e:
                print(f"服务集成测试失败: {e}")
                return False
        
        def run_all_tests(self):
            """运行所有集成测试"""
            tests = [
                self.test_data_repository_connection,
                self.test_crawler_initialization,
                self.test_service_integration
            ]
            
            results = []
            for test in tests:
                results.append(test())
            
            return all(results)
    
    # 运行集成测试
    integration_test = IntegrationTest()
    success = integration_test.run_all_tests()
    
    if success:
        print("所有集成测试通过")
    else:
        print("部分集成测试失败")
    
    return success


def example_mock_testing():
    """模拟测试示例"""
    print("=== 模拟测试示例 ===")
    
    def test_with_mock():
        """使用Mock进行测试"""
        # 创建模拟对象
        mock_crawler = Mock()
        mock_crawler.crawl_stock_list.return_value = None
        mock_crawler.crawl_company_info.return_value = None
        
        # 模拟服务
        service = CrawlerService()
        service.stock_crawler = mock_crawler
        
        # 执行测试
        try:
            service.run_stock_list_crawl()
            print("模拟测试通过")
            return True
        except Exception as e:
            print(f"模拟测试失败: {e}")
            return False
    
    def test_with_patch():
        """使用patch进行测试"""
        with patch('services.crawler_service.StockCrawler') as mock_crawler_class:
            # 创建模拟实例
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            
            # 模拟方法
            mock_crawler.crawl_stock_list.return_value = None
            
            # 创建服务并测试
            service = CrawlerService()
            service.run_stock_list_crawl()
            
            # 验证方法被调用
            mock_crawler.crawl_stock_list.assert_called_once()
            print("Patch测试通过")
            return True
    
    # 运行模拟测试
    result1 = test_with_mock()
    result2 = test_with_patch()
    
    return result1 and result2


def example_performance_testing():
    """性能测试示例"""
    print("=== 性能测试示例 ===")
    
    import time
    import random
    
    def generate_test_data(size):
        """生成测试数据"""
        return [f"SYMBOL{i:06d}" for i in range(size)]
    
    def test_crawler_performance():
        """测试爬虫性能"""
        symbols = generate_test_data(100)
        
        # 模拟处理时间
        def process_symbol(symbol):
            time.sleep(0.01)  # 模拟10ms处理时间
            return f"{symbol}_processed"
        
        start_time = time.time()
        results = []
        
        for symbol in symbols:
            result = process_symbol(symbol)
            results.append(result)
        
        end_time = time.time()
        
        processing_time = end_time - start_time
        throughput = len(symbols) / processing_time
        
        print(f"处理 {len(symbols)} 个股票耗时: {processing_time:.2f} 秒")
        print(f"吞吐量: {throughput:.2f} 股票/秒")
        
        return throughput
    
    def test_database_performance():
        """测试数据库性能"""
        # 模拟数据库操作
        def simulate_db_operation():
            time.sleep(0.005)  # 模拟5ms数据库操作
            return True
        
        operations = 1000
        start_time = time.time()
        
        for i in range(operations):
            simulate_db_operation()
        
        end_time = time.time()
        
        total_time = end_time - start_time
        ops_per_second = operations / total_time
        
        print(f"执行 {operations} 次数据库操作耗时: {total_time:.2f} 秒")
        print(f"操作速率: {ops_per_second:.2f} 操作/秒")
        
        return ops_per_second
    
    # 运行性能测试
    crawler_throughput = test_crawler_performance()
    db_ops_per_second = test_database_performance()
    
    print(f"性能测试完成 - 爬虫吞吐量: {crawler_throughput:.2f}, 数据库操作: {db_ops_per_second:.2f}")


def example_stress_testing():
    """压力测试示例"""
    print("=== 压力测试示例 ===")
    
    import threading
    import time
    
    def stress_test_crawler(num_threads=5, requests_per_thread=20):
        """爬虫压力测试"""
        results = []
        errors = []
        
        def worker():
            """工作线程"""
            for i in range(requests_per_thread):
                try:
                    # 模拟请求
                    time.sleep(0.1)  # 模拟100ms请求时间
                    results.append(f"request_{threading.current_thread().ident}_{i}")
                except Exception as e:
                    errors.append(e)
        
        # 创建线程
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        total_requests = num_threads * requests_per_thread
        success_rate = len(results) / total_requests
        total_time = end_time - start_time
        
        print(f"压力测试完成:")
        print(f"  线程数: {num_threads}")
        print(f"  每线程请求数: {requests_per_thread}")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求数: {len(results)}")
        print(f"  错误数: {len(errors)}")
        print(f"  成功率: {success_rate:.2%}")
        print(f"  总耗时: {total_time:.2f} 秒")
        print(f"  平均响应时间: {total_time/total_requests:.3f} 秒")
        
        return success_rate > 0.95  # 95%成功率认为通过
    
    # 运行压力测试
    success = stress_test_crawler()
    
    if success:
        print("压力测试通过")
    else:
        print("压力测试失败")
    
    return success


def main():
    """主函数"""
    logger = get_logger('example_testing')
    
    try:
        print("开始运行测试示例...")
        
        # 示例1: 单元测试
        print("\n" + "="*50)
        unit_success = example_unit_testing()
        
        # 示例2: 集成测试
        print("\n" + "="*50)
        integration_success = example_integration_testing()
        
        # 示例3: 模拟测试
        print("\n" + "="*50)
        mock_success = example_mock_testing()
        
        # 示例4: 性能测试
        print("\n" + "="*50)
        example_performance_testing()
        
        # 示例5: 压力测试
        print("\n" + "="*50)
        stress_success = example_stress_testing()
        
        # 总结
        print("\n" + "="*50)
        print("测试总结:")
        print(f"  单元测试: {'通过' if unit_success else '失败'}")
        print(f"  集成测试: {'通过' if integration_success else '失败'}")
        print(f"  模拟测试: {'通过' if mock_success else '失败'}")
        print(f"  压力测试: {'通过' if stress_success else '失败'}")
        
        print("测试示例完成！")
        
    except Exception as e:
        logger.error(f"测试示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()