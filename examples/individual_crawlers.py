"""
单独使用各个爬虫的示例
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.stock_crawler import StockCrawler
from crawlers.financial_crawler import FinancialCrawler
from crawlers.kline_crawler import KlineCrawler
from database.database import DataRepository
from utils.logger import get_logger


def example_stock_crawler():
    """股票爬虫使用示例"""
    print("=== 股票爬虫示例 ===")
    
    # 创建爬虫实例
    stock_crawler = StockCrawler()
    
    # 爬取股票列表
    print("爬取股票列表...")
    stock_crawler.crawl_stock_list()
    
    # 爬取公司信息
    print("爬取公司信息...")
    stock_crawler.crawl_company_info()


def example_financial_crawler():
    """财务数据爬虫使用示例"""
    print("=== 财务数据爬虫示例 ===")
    
    # 创建爬虫实例
    financial_crawler = FinancialCrawler()
    
    # 爬取财务数据
    print("爬取财务数据...")
    financial_crawler.crawl_financial_data()


def example_kline_crawler():
    """K线数据爬虫使用示例"""
    print("=== K线数据爬虫示例 ===")
    
    # 创建爬虫实例
    kline_crawler = KlineCrawler()
    
    # 爬取K线数据
    print("爬取K线数据...")
    kline_crawler.crawl_kline_data()


def main():
    """主函数"""
    logger = get_logger('example_individual')
    
    try:
        # 示例1: 股票爬虫
        example_stock_crawler()
        
        # 示例2: 财务数据爬虫
        # example_financial_crawler()
        
        # 示例3: K线数据爬虫
        # example_kline_crawler()
        
        print("单独爬虫示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()