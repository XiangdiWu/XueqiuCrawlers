"""
自定义爬虫示例
"""
import sys
import os
import json
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.base_crawler import BaseCrawler
from database.database import DataRepository
from utils.logger import get_logger


class CustomStockCrawler(BaseCrawler):
    """自定义股票爬虫示例"""
    
    def __init__(self):
        super().__init__()
        self.data_repo = DataRepository()
    
    def crawl_custom_data(self, symbol):
        """爬取自定义数据示例"""
        print(f"爬取 {symbol} 的自定义数据...")
        
        # 构建自定义URL
        url = f"{self.config['base_url']}/stock/quote.json?symbol={symbol}&_={self.get_timestamp()}"
        
        try:
            # 发送请求
            response = self.make_request(url)
            data = response.json()
            
            # 解析数据
            custom_data = self._parse_custom_data(data, symbol)
            
            # 保存数据（这里只是示例，实际需要根据数据库结构调整）
            print(f"解析到的数据: {custom_data}")
            
            return custom_data
            
        except Exception as e:
            print(f"爬取自定义数据失败: {e}")
            return None
    
    def _parse_custom_data(self, data, symbol):
        """解析自定义数据"""
        return {
            'symbol': symbol,
            'name': data.get('name', ''),
            'current': data.get('current', 0),
            'timestamp': self.get_timestamp()
        }
    
    def batch_crawl(self, symbols):
        """批量爬取示例"""
        print(f"批量爬取 {len(symbols)} 支股票...")
        
        results = []
        for i, symbol in enumerate(symbols, 1):
            print(f"处理第 {i}/{len(symbols)} 支: {symbol}")
            
            try:
                data = self.crawl_custom_data(symbol)
                if data:
                    results.append(data)
                
                # 添加延迟
                self.delay()
                
            except Exception as e:
                print(f"处理 {symbol} 失败: {e}")
                continue
        
        print(f"批量爬取完成，成功 {len(results)} 支")
        return results


class CustomFinancialCrawler(BaseCrawler):
    """自定义财务爬虫示例"""
    
    def crawl_specific_financial_data(self, symbol, year):
        """爬取特定年份的财务数据"""
        print(f"爬取 {symbol} {year} 年的财务数据...")
        
        # 构建URL
        url = (
            f"{self.config['base_url']}/stock/f10/custom.json"
            f"?symbol={symbol}&year={year}&_={self.get_timestamp()}"
        )
        
        try:
            response = self.make_request(url)
            data = response.json()
            
            # 解析特定财务数据
            financial_data = self._parse_specific_financial_data(data, symbol, year)
            
            print(f"财务数据: {financial_data}")
            return financial_data
            
        except Exception as e:
            print(f"爬取财务数据失败: {e}")
            return None
    
    def _parse_specific_financial_data(self, data, symbol, year):
        """解析特定财务数据"""
        return {
            'symbol': symbol,
            'year': year,
            'revenue': data.get('revenue', 0),
            'profit': data.get('profit', 0),
            'assets': data.get('assets', 0)
        }


def example_custom_crawler():
    """自定义爬虫使用示例"""
    print("=== 自定义爬虫示例 ===")
    
    # 创建自定义爬虫
    custom_crawler = CustomStockCrawler()
    
    # 爬取单支股票
    print("1. 爬取单支股票...")
    # result = custom_crawler.crawl_custom_data('SZ000001')
    # print(f"结果: {result}")
    
    # 批量爬取
    print("2. 批量爬取...")
    symbols = ['SZ000001', 'SZ000002', 'SH600000']
    # results = custom_crawler.batch_crawl(symbols)
    # print(f"批量结果: {results}")


def example_custom_financial_crawler():
    """自定义财务爬虫示例"""
    print("=== 自定义财务爬虫示例 ===")
    
    # 创建自定义财务爬虫
    financial_crawler = CustomFinancialCrawler()
    
    # 爬取特定年份财务数据
    print("爬取2023年财务数据...")
    # result = financial_crawler.crawl_specific_financial_data('SZ000001', 2023)
    # print(f"财务数据: {result}")


def example_extending_base_crawler():
    """扩展基础爬虫示例"""
    print("=== 扩展基础爬虫示例 ===")
    
    class ExtendedCrawler(BaseCrawler):
        """扩展爬虫示例"""
        
        def __init__(self, custom_headers=None):
            super().__init__()
            # 添加自定义请求头
            if custom_headers:
                self.session.headers.update(custom_headers)
        
        def crawl_with_retry(self, url, max_retries=5):
            """带自定义重试的请求"""
            print(f"使用自定义重试策略请求: {url}")
            
            for attempt in range(max_retries):
                try:
                    response = self.make_request(url)
                    return response
                except Exception as e:
                    print(f"第 {attempt + 1} 次尝试失败: {e}")
                    if attempt < max_retries - 1:
                        # 自定义延迟策略
                        delay_time = min(2 ** attempt, 10)  # 指数退避，最大10秒
                        print(f"等待 {delay_time} 秒后重试...")
                        time.sleep(delay_time)
            
            raise Exception(f"请求失败，已重试 {max_retries} 次")
    
    # 使用扩展爬虫
    extended_crawler = ExtendedCrawler({
        'Custom-Header': 'CustomValue'
    })
    
    # 示例请求
    # url = f"{extended_crawler.config['base_url']}/test.json"
    # response = extended_crawler.crawl_with_retry(url)
    # print(f"扩展爬虫结果: {response.json()}")


def main():
    """主函数"""
    logger = get_logger('example_custom')
    
    try:
        # 示例1: 自定义爬虫
        example_custom_crawler()
        
        # 示例2: 自定义财务爬虫
        example_custom_financial_crawler()
        
        # 示例3: 扩展基础爬虫
        example_extending_base_crawler()
        
        print("自定义爬虫示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()