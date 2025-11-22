#!/usr/bin/env python3
"""
雪球股票数据爬虫
主要功能：
Step 1: 测试认证状态
    若认证状态异常，提示先获取雪球Cookie，运行get_cookie.py
    若认证状态正常，进入Step 2
Step 2: 根据选项爬取指定数据，并保存到数据库
    选项如下：
    1. 爬取公司信息
    2. 爬取股票基础信息
    3. 爬取K线数据（按日期存储）
    4. 爬取财务数据（按证券代码存储）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawlers.stock_info_crawler import StockInfoCrawler
from crawlers.kline_crawler import KlineCrawler
from crawlers.company_info_crawler import CompanyInfoCrawler
from crawlers.financial_crawler import FinancialCrawler
from engine.database import DataRepository
from engine.logger import logger
from engine.xueqiu_auth import get_auth

def test_authentication():
    """测试认证状态"""
    print("\n🔍 测试认证状态...")
    print("-" * 30)
    
    auth = get_auth()
    cookies = auth.get_cookies()
    
    if not cookies:
        print("❌ 认证状态异常：未找到Cookie")
        print("\n💡 解决方案：")
        print("请先获取雪球Cookie，运行以下命令：")
        print("   python engine/get_cookie.py")
        print("\n📖 获取Cookie引导：")
        print("   1. 浏览器登录雪球：https://xueqiu.com")
        print("   2. F12 → Network → 复制Cookie字符串")
        print("   3. 粘贴到 cookie_input.txt 文件")
        print("   4. 重新运行 get_cookie.py")
        return False
    
    # 检查用户ID
    user_id = cookies.get('u', '0')
    if user_id == '0':
        print("⚠️  认证状态异常：游客模式（u=0）")
        print("\n💡 解决方案：")
        print("请使用登录后的Cookie，运行以下命令重新获取：")
        print("   python engine/get_cookie.py")
        return False
    
    print(f"✅ 认证状态正常：用户ID {user_id}")
    
    # 验证Cookie有效性
    if auth._validate_cookies(cookies):
        print("✅ Cookie验证通过")
        return True
    else:
        print("⚠️  Cookie验证失败")
        print("💡 建议重新获取Cookie：python engine/get_cookie.py")
        return False


def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🚀 雪球股票数据爬虫")
    print("="*50)
    print("1. 爬取公司信息")
    print("2. 爬取股票基础信息")
    print("3. 爬取K线数据（按日期存储）")
    print("4. 爬取财务数据（按证券代码存储）")
    print("5. 爬取所有数据")
    print("0. 退出")
    print("="*50)

def crawl_company_info():
    """爬取公司信息"""
    print("\n🏢 开始爬取公司信息...")
    crawler = CompanyInfoCrawler(DataRepository())
    crawler.crawl_company_info()
    print("✅ 公司信息爬取完成！")

def crawl_stock_basic_info():
    """爬取股票基础信息"""
    print("\n📈 开始爬取股票基础信息...")
    crawler = StockInfoCrawler(DataRepository())
    crawler.crawl_stock_list()
    print("✅ 股票基础信息爬取完成！")

def crawl_kline_data():
    """爬取K线数据（按日期存储）"""
    print("\n📊 开始爬取K线数据（按日期存储）...")
    crawler = KlineCrawler(DataRepository())
    crawler.crawl_kline_data('after')
    print("✅ K线数据爬取完成！")

def crawl_financial_data():
    """爬取财务数据（按证券代码存储）"""
    print("\n💰 开始爬取财务数据（按证券代码存储）...")
    crawler = FinancialCrawler(DataRepository())
    crawler.crawl_financial_data()
    print("✅ 财务数据爬取完成！")

def crawl_all_data():
    """爬取所有数据"""
    print("\n🔄 开始爬取所有数据...")
    
    # 1. 公司信息
    print("1/4 爬取公司信息...")
    company_crawler = CompanyInfoCrawler(DataRepository())
    company_crawler.crawl_company_info()
    
    # 2. 股票基础信息
    print("2/4 爬取股票基础信息...")
    stock_crawler = StockInfoCrawler(DataRepository())
    stock_crawler.crawl_stock_list()
    
    # 3. K线数据
    print("3/4 爬取K线数据...")
    kline_crawler = KlineCrawler(DataRepository())
    kline_crawler.crawl_kline_data('after')
    
    # 4. 财务数据
    print("4/4 爬取财务数据...")
    financial_crawler = FinancialCrawler(DataRepository())
    financial_crawler.crawl_financial_data()
    
    print("✅ 所有数据爬取完成！")

def main():
    """主函数"""
    # Step 1: 测试认证状态
    print("🔐 Step 1: 测试认证状态")
    if not test_authentication():
        print("\n❌ 认证状态异常，请先解决认证问题")
        return
    
    # Step 2: 显示菜单并执行选择的功能
    print("\n📋 Step 2: 选择要爬取的数据类型")
    
    while True:
        show_menu()
        choice = input("请选择功能 (0-5): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            crawl_company_info()
        elif choice == '2':
            crawl_stock_basic_info()
        elif choice == '3':
            crawl_kline_data()
        elif choice == '4':
            crawl_financial_data()
        elif choice == '5':
            crawl_all_data()
        else:
            print("❌ 无效选择，请重新输入！")

if __name__ == "__main__":
    main()