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
    print("1. 爬取公司信息（不必需）")
    print("2. 获取股票信息（完整字段）")
    print("3. 创建股票列表（简化字段，不必需）")
    print("4. 爬取日频K线数据（按日期存储）")
    print("5. 爬取财务数据（按证券代码存储）")
    print("6. 爬取所有数据")
    print("0. 退出")
    print("="*50)

def crawl_company_info():
    """爬取公司信息"""
    print("\n🏢 公司信息爬取选项")
    print("=" * 40)
    print("1. 爬取所有公司信息")
    print("2. 按证券代码爬取单个公司信息")
    print("3. 批量爬取指定公司信息")
    print("4. 查看指定公司信息")
    print("5. 更新指定公司信息")
    print("6. 导出公司信息到CSV")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (0-6): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        print("\n🏢 开始爬取所有公司信息...")
        crawler = CompanyInfoCrawler(DataRepository())
        result = crawler.crawl_company_info()
        print(f"✅ 公司信息爬取完成！成功: {result['success']}, 失败: {result['error']}")
    elif choice == '2':
        symbol = input("请输入证券代码 (如 SZ000001): ").strip()
        if symbol:
            print(f"\n🏢 开始爬取公司信息: {symbol}")
            crawler = CompanyInfoCrawler(DataRepository())
            result = crawler.crawl_company_info_by_code(symbol)
            if result:
                print(f"✅ 公司信息爬取成功: {symbol} - {result.get('compsname', '')}")
            else:
                print(f"❌ 公司信息爬取失败: {symbol}")
        else:
            print("❌ 证券代码不能为空")
    elif choice == '3':
        symbols_input = input("请输入证券代码列表 (用逗号分隔，如 SZ000001,SH600001): ").strip()
        if symbols_input:
            symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]
            print(f"\n🏢 开始批量爬取公司信息，共{len(symbols)}支股票...")
            crawler = CompanyInfoCrawler(DataRepository())
            result = crawler.crawl_company_info_batch(symbols)
            print(f"✅ 批量爬取完成！成功: {result['success']}, 失败: {result['error']}")
        else:
            print("❌ 证券代码列表不能为空")
    elif choice == '4':
        symbol = input("请输入证券代码 (如 SZ000001): ").strip()
        if symbol:
            print(f"\n🔍 查询公司信息: {symbol}")
            crawler = CompanyInfoCrawler(DataRepository())
            info = crawler.get_company_info_by_symbol(symbol)
            if info:
                print(f"✅ 找到公司信息:")
                print(f"   证券代码: {info.get('compcode', '')}")
                print(f"   公司名称: {info.get('compsname', '')}")
                print(f"   法定名称: {info.get('compname', '')}")
                print(f"   英文名称: {info.get('engname', '')}")
                print(f"   成立时间: {info.get('founddate', '')}")
                print(f"   注册资本: {info.get('regcapital', '')}")
                print(f"   董事长: {info.get('chairman', '')}")
                print(f"   总经理: {info.get('manager', '')}")
                print(f"   注册地址: {info.get('regaddr', '')}")
                print(f"   办公地址: {info.get('officeaddr', '')}")
                print(f"   更新时间: {info.get('updated_at', '')}")
            else:
                print(f"❌ 未找到公司信息: {symbol}")
        else:
            print("❌ 证券代码不能为空")
    elif choice == '5':
        symbol = input("请输入证券代码 (如 SZ000001): ").strip()
        if symbol:
            print(f"\n🔄 更新公司信息: {symbol}")
            crawler = CompanyInfoCrawler(DataRepository())
            result = crawler.update_company_info_by_symbol(symbol)
            if result:
                print(f"✅ 公司信息更新成功: {symbol} - {result.get('compsname', '')}")
            else:
                print(f"❌ 公司信息更新失败: {symbol}")
        else:
            print("❌ 证券代码不能为空")
    elif choice == '6':
        print("\n📄 导出公司信息选项")
        print("1. 导出所有公司信息")
        print("2. 导出指定公司信息")
        export_choice = input("请选择 (1-2): ").strip()
        
        if export_choice == '1':
            print("\n📄 导出所有公司信息...")
            crawler = CompanyInfoCrawler(DataRepository())
            success = crawler.export_company_info_to_csv()
            if success:
                print("✅ 所有公司信息导出成功！")
            else:
                print("❌ 公司信息导出失败！")
        elif export_choice == '2':
            symbols_input = input("请输入证券代码列表 (用逗号分隔): ").strip()
            if symbols_input:
                symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]
                print(f"\n📄 导出指定公司信息，共{len(symbols)}支股票...")
                crawler = CompanyInfoCrawler(DataRepository())
                success = crawler.export_company_info_to_csv(symbols=symbols)
                if success:
                    print("✅ 指定公司信息导出成功！")
                else:
                    print("❌ 公司信息导出失败！")
            else:
                print("❌ 证券代码列表不能为空")
    else:
        print("❌ 无效选择")

def get_stock_info():
    """获取股票信息（完整字段，保存到stock_info）"""
    print("\n📈 获取股票信息选项")
    print("=" * 40)
    print("1. 获取今日股票信息")
    print("2. 获取指定日期股票信息")
    print("3. 查看指定日期股票信息")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        print("\n📈 开始获取今日股票信息...")
        crawler = StockInfoCrawler(DataRepository())
        crawler.crawl_stock_list()
        print("✅ 今日股票信息获取完成！")
    elif choice == '2':
        date_str = input("请输入日期 (YYYY-MM-DD，如 2024-01-01): ").strip()
        if date_str:
            print(f"\n📈 开始获取 {date_str} 的股票信息...")
            # 注意：当前stock_info_crawler只支持获取当天数据
            # 这里可以提示用户或修改爬虫以支持指定日期
            print("⚠️  注意：当前版本只支持获取当天数据")
            crawler = StockInfoCrawler(DataRepository())
            crawler.crawl_stock_list()
            print("✅ 股票信息获取完成！")
        else:
            print("❌ 日期不能为空")
    elif choice == '3':
        date_str = input("请输入日期 (YYYY-MM-DD，留空为今天): ").strip()
        if not date_str:
            date_str = None
        print(f"\n🔍 查看股票信息，日期: {date_str or '今天'}")
        crawler = StockInfoCrawler(DataRepository())
        if hasattr(crawler.data_repo, 'csv_storage') and crawler.data_repo.csv_storage:
            stocks = crawler.data_repo.csv_storage.get_stock_info_by_date(date_str or '2025-11-22')
            if stocks:
                print(f"✅ 找到 {len(stocks)} 条股票记录")
                print("\n前10条记录:")
                print("-" * 80)
                for i, stock in enumerate(stocks[:10], 1):
                    print(f"{i:2d}. {stock.get('symbol', ''):<10} {stock.get('name', ''):<15} "
                          f"价格:{stock.get('current', 0):>8.2f} "
                          f"涨跌:{stock.get('percent', 0):>6.2f}% "
                          f"成交量:{stock.get('volume', 0):>10,}")
                if len(stocks) > 10:
                    print(f"... 还有 {len(stocks) - 10} 条记录")
            else:
                print(f"❌ 未找到 {date_str or '今天'} 的股票信息")
        else:
            print("❌ 当前不支持数据库模式查看")
    else:
        print("❌ 无效选择")

def create_stock_list():
    """创建股票列表（简化字段，保存到stock_list）"""
    print("\n📋 创建股票列表选项")
    print("=" * 40)
    print("1. 从今日stock_info创建简化列表")
    print("2. 从指定日期stock_info创建简化列表")
    print("3. 查看指定日期股票列表")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        print("\n📋 从今日stock_info创建简化股票列表...")
        crawler = StockInfoCrawler(DataRepository())
        result = crawler.create_simplified_stock_list()
        if result:
            print("✅ 今日简化股票列表创建完成！")
        else:
            print("❌ 今日简化股票列表创建失败！")
    elif choice == '2':
        date_str = input("请输入日期 (YYYY-MM-DD，如 2024-01-01): ").strip()
        if date_str:
            print(f"\n📋 从 {date_str} 的stock_info创建简化股票列表...")
            crawler = StockInfoCrawler(DataRepository())
            result = crawler.create_simplified_stock_list(date_str)
            if result:
                print(f"✅ {date_str} 简化股票列表创建完成！")
            else:
                print(f"❌ {date_str} 简化股票列表创建失败！")
        else:
            print("❌ 日期不能为空")
    elif choice == '3':
        date_str = input("请输入日期 (YYYY-MM-DD，留空为今天): ").strip()
        if not date_str:
            date_str = None
        print(f"\n🔍 查看股票列表，日期: {date_str or '今天'}")
        crawler = StockInfoCrawler(DataRepository())
        if hasattr(crawler.data_repo, 'csv_storage') and crawler.data_repo.csv_storage:
            stocks = crawler.data_repo.csv_storage.get_stock_list_by_date(date_str or '2025-11-22')
            if stocks:
                print(f"✅ 找到 {len(stocks)} 条股票记录")
                print("\n前10条记录:")
                print("-" * 60)
                for i, stock in enumerate(stocks[:10], 1):
                    print(f"{i:2d}. {stock.get('symbol', ''):<10} {stock.get('name', ''):<15} "
                          f"更新时间: {stock.get('crawl_time', '')}")
                if len(stocks) > 10:
                    print(f"... 还有 {len(stocks) - 10} 条记录")
            else:
                print(f"❌ 未找到 {date_str or '今天'} 的股票列表")
        else:
            print("❌ 当前不支持数据库模式查看")
    else:
        print("❌ 无效选择")

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
    print("1/5 爬取公司信息...")
    company_crawler = CompanyInfoCrawler(DataRepository())
    company_crawler.crawl_company_info()
    
    # 2. 获取股票信息（完整字段）
    print("2/5 获取股票信息（完整字段）...")
    stock_crawler = StockInfoCrawler(DataRepository())
    stock_crawler.crawl_stock_list()
    
    # 3. 创建股票列表（简化字段）
    print("3/5 创建股票列表（简化字段）...")
    stock_crawler.create_simplified_stock_list()
    
    # 4. K线数据
    print("4/5 爬取K线数据...")
    kline_crawler = KlineCrawler(DataRepository())
    kline_crawler.crawl_kline_data('after')
    
    # 5. 财务数据
    print("5/5 爬取财务数据...")
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
            get_stock_info()
        elif choice == '3':
            create_stock_list()
        elif choice == '4':
            crawl_kline_data()
        elif choice == '5':
            crawl_financial_data()
        elif choice == '6':
            crawl_all_data()
        else:
            print("❌ 无效选择，请重新输入！")

if __name__ == "__main__":
    main()