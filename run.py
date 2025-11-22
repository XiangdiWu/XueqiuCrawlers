#!/usr/bin/env python3
"""
雪球股票数据爬虫
主要功能：
1. 爬取股票基础信息
2. 爬取K线数据（按日期存储）
3. 爬取公司信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.stock_crawler import StockCrawler
from crawlers.kline_crawler import KlineCrawler
from engine.database import DataRepository
from engine.logger import logger

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🚀 雪球股票数据爬虫")
    print("="*50)
    print("1. 爬取股票基础信息")
    print("2. 爬取K线数据（后复权）")
    print("3. 爬取所有数据")
    print("0. 退出")
    print("="*50)

def crawl_stock_basic_info():
    """爬取股票基础信息"""
    print("\n📈 开始爬取股票基础信息...")
    crawler = StockCrawler(DataRepository())
    crawler.crawl_stock_list()
    print("✅ 股票基础信息爬取完成！")

def crawl_kline_data():
    """爬取K线数据"""
    print("\n📊 开始爬取K线数据（后复权）...")
    crawler = KlineCrawler(DataRepository())
    crawler.crawl_kline_data('after')
    print("✅ K线数据爬取完成！")

def crawl_all_data():
    """爬取所有数据"""
    print("\n🔄 开始爬取所有数据...")
    
    # 1. 股票基础信息
    print("1/2 爬取股票基础信息...")
    stock_crawler = StockCrawler(DataRepository())
    stock_crawler.crawl_stock_list()
    
    # 2. K线数据
    print("2/2 爬取K线数据...")
    kline_crawler = KlineCrawler(DataRepository())
    kline_crawler.crawl_kline_data('after')
    
    print("✅ 所有数据爬取完成！")

def main():
    """主函数"""
    data_repo = DataRepository()
    
    while True:
        show_menu()
        choice = input("请选择功能 (0-3): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            crawl_stock_basic_info()
        elif choice == '2':
            crawl_kline_data()
        elif choice == '3':
            crawl_all_data()
        else:
            print("❌ 无效选择，请重新输入！")

if __name__ == "__main__":
    main()