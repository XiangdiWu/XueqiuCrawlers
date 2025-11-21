"""
基础使用示例
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.crawler_service import CrawlerService
from database.database import DataRepository
from utils.logger import get_logger


def main():
    """基础使用示例"""
    # 设置日志
    logger = get_logger('example_basic')
    
    try:
        # 创建爬虫服务
        crawler_service = CrawlerService()
        
        # 方式1: 执行完整爬取流程
        print("=== 执行完整爬取流程 ===")
        # crawler_service.run_full_crawl()
        
        # 方式2: 分别执行各个爬虫
        print("\n=== 分别执行各个爬虫 ===")
        
        # 爬取股票列表
        print("1. 爬取股票列表...")
        # crawler_service.run_stock_list_crawl()
        
        # 爬取公司信息
        print("2. 爬取公司信息...")
        # crawler_service.run_company_info_crawl()
        
        # 爬取财务数据
        print("3. 爬取财务数据...")
        # crawler_service.run_financial_crawl()
        
        # 爬取K线数据
        print("4. 爬取K线数据...")
        # crawler_service.run_kline_crawl()
        
        print("基础使用示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()