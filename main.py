#!/usr/bin/env python3
"""
雪球股票数据爬虫主程序
"""
import argparse
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.crawler_service import CrawlerService
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='雪球股票数据爬虫')
    parser.add_argument('--type', choices=['all', 'stock', 'company', 'financial', 'kline'],
                       default='all', help='爬取类型')
    parser.add_argument('--storage', choices=['database', 'csv'], 
                       help='存储类型 (默认使用配置文件设置)')
    parser.add_argument('--info', action='store_true', help='显示存储信息')
    parser.add_argument('--backup', action='store_true', help='创建备份')
    parser.add_argument('--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 初始化服务
    storage_type = args.storage if args.storage else None
    service = CrawlerService(storage_type=storage_type)
    
    # 显示存储信息
    if args.info:
        info = service.get_storage_info()
        print(f"存储类型: {info['type']}")
        if info['type'] == 'database':
            print("数据库表信息:")
            for table, count in info.get('tables', {}).items():
                print(f"  {table}: {count} 条记录")
        else:
            print("CSV文件信息:")
            for table, file_info in info.get('files', {}).items():
                if file_info.get('exists'):
                    print(f"  {table}: {file_info['record_count']} 条记录")
        return
    
    # 创建备份
    if args.backup:
        success = service.create_backup()
        if success:
            print("备份创建成功")
        else:
            print("备份创建失败")
        return
    
    print(f"使用存储类型: {service.storage_type}")
    
    try:
        if args.type == 'all':
            service.run_full_crawl()
        elif args.type == 'stock':
            service.run_stock_list_crawl()
        elif args.type == 'company':
            service.run_company_info_crawl()
        elif args.type == 'financial':
            service.run_financial_crawl()
        elif args.type == 'kline':
            service.run_kline_crawl()
        
        logger.info("爬取任务完成")
        
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()