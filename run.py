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
from crawlers.financial_statements_crawler import FinancialStatementsCrawler
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
    print("6. 爬取财务报表（三表完整数据）")
    print("7. 爬取所有数据")
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
    print("\n📊 K线数据爬取选项")
    print("=" * 40)
    print("1. 爬取所有股票K线数据（后复权）")
    print("2. 爬取所有股票K线数据（前复权）")
    print("3. 爬取所有股票K线数据（不复权）")
    print("4. 爬取指定数量股票K线数据")
    print("5. 爬取单只股票K线数据")
    print("6. 恢复爬取（只处理未完成的股票）")
    print("7. 🆕 爬取全市场股票某日数据")
    print("8. 查看K线数据")
    print("9. 查看处理进度")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (0-9): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        print("\n📊 开始爬取所有股票K线数据（后复权）...")
        crawler = KlineCrawler(DataRepository())
        crawler.crawl_kline_data('after')
        print("✅ K线数据爬取完成！")
    elif choice == '2':
        print("\n📊 开始爬取所有股票K线数据（前复权）...")
        crawler = KlineCrawler(DataRepository())
        crawler.crawl_kline_data('before')
        print("✅ K线数据爬取完成！")
    elif choice == '3':
        print("\n📊 开始爬取所有股票K线数据（不复权）...")
        crawler = KlineCrawler(DataRepository())
        crawler.crawl_kline_data('none')
        print("✅ K线数据爬取完成！")
    elif choice == '4':
        try:
            max_stocks = int(input("请输入要爬取的股票数量: ").strip())
            if max_stocks > 0:
                print(f"\n📊 开始爬取 {max_stocks} 只股票K线数据（后复权）...")
                crawler = KlineCrawler(DataRepository())
                crawler.crawl_kline_data('after', max_stocks)
                print("✅ K线数据爬取完成！")
            else:
                print("❌ 股票数量必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
    elif choice == '5':
        symbol = input("请输入股票代码 (如 SZ000001): ").strip()
        if symbol:
            print(f"\n📊 开始爬取 {symbol} K线数据（后复权）...")
            crawler = KlineCrawler(DataRepository())
            kline_data = crawler.crawl_single_stock_kline(symbol, 'after')
            if kline_data:
                print(f"✅ 成功获取 {len(kline_data)} 条K线数据")
                print("最新5条数据:")
                for data in kline_data[-5:]:
                    date = data.get('crawl_date', '')
                    close = data.get('close', 0)
                    percent = data.get('percent', 0)
                    print(f"  {date}: 收盘价 {close}, 涨跌幅 {percent}%")
            else:
                print(f"❌ 未获取到 {symbol} 的K线数据")
        else:
            print("❌ 股票代码不能为空")
    elif choice == '6':
        print("\n📊 恢复K线数据爬取...")
        crawler = KlineCrawler(DataRepository())
        crawler.resume_crawl('after')
        print("✅ 恢复爬取完成！")
    elif choice == '7':
        # 🆕 爬取全市场股票某日数据
        date_str = input("请输入目标日期 (YYYY-MM-DD，留空为今天): ").strip()
        if not date_str:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        adjust_choice = input("请选择复权类型 (1-前复权, 2-后复权, 3-不复权，默认后复权): ").strip()
        adjust_type = 'after'  # 默认后复权
        if adjust_choice == '1':
            adjust_type = 'before'
        elif adjust_choice == '3':
            adjust_type = 'none'
        
        max_stocks_input = input("限制股票数量 (留空处理全部): ").strip()
        max_stocks = None
        if max_stocks_input and max_stocks_input.isdigit():
            max_stocks = int(max_stocks_input)
        
        print(f"\n📊 开始爬取全市场股票 {date_str} 日频数据（{adjust_type}复权）...")
        crawler = KlineCrawler(DataRepository())
        crawler.crawl_market_daily_data(date_str, adjust_type, max_stocks)
        print("✅ 全市场日频数据爬取完成！")
    elif choice == '8':
        date_str = input("请输入日期 (YYYY-MM-DD，留空为今天): ").strip()
        if not date_str:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🔍 查看 {date_str} 的K线数据...")
        if hasattr(DataRepository(), 'csv_storage'):
            csv_storage = DataRepository().csv_storage
            kline_data = csv_storage.get_kline_data_by_date(date_str)
            if kline_data:
                print(f"✅ 找到 {len(kline_data)} 条K线记录")
                print("\n最新10条记录:")
                print("-" * 80)
                for i, data in enumerate(kline_data[-10:], 1):
                    symbol = data.get('symbol', '')
                    date = data.get('crawl_date', '')
                    close = data.get('close', 0)
                    volume = data.get('volume', 0)
                    percent = data.get('percent', 0)
                    print(f"{i:2d}. {symbol:<10} {date} 收盘:{float(close):>8.2f} "
                          f"涨跌:{float(percent):>6.2f}% 成交量:{int(volume):>10,}")
            else:
                print(f"❌ 未找到 {date_str} 的K线数据")
        else:
            print("❌ 当前不支持数据库模式查看")
    elif choice == '9':
        print("\n📊 查看K线数据处理进度...")
        crawler = KlineCrawler(DataRepository())
        processed_symbols = crawler.get_processed_symbols()
        all_symbols = crawler._get_unprocessed_stocks()
        
        if all_symbols:
            processed_count = len(processed_symbols)
            total_count = len(all_symbols)
            progress = (processed_count / total_count * 100) if total_count > 0 else 0
            
            print(f"✅ 处理进度: {processed_count}/{total_count} ({progress:.1f}%)")
            print(f"📊 已处理股票: {len(processed_symbols)} 只")
            print(f"⏳ 待处理股票: {len(all_symbols) - len(processed_symbols)} 只")
            
            if processed_symbols:
                print(f"\n已处理的股票代码（前10只）:")
                for symbol in processed_symbols[:10]:
                    print(f"  ✅ {symbol}")
                if len(processed_symbols) > 10:
                    print(f"  ... 还有 {len(processed_symbols) - 10} 只")
        else:
            print("❌ 无法获取股票列表，请先获取股票信息")
    else:
        print("❌ 无效选择")

def crawl_financial_data():
    """爬取财务数据（按证券代码存储）"""
    print("\n💰 开始爬取财务数据（按证券代码存储）...")
    crawler = FinancialCrawler(DataRepository())
    crawler.crawl_financial_data()
    print("✅ 财务数据爬取完成！")

def crawl_financial_statements():
    """爬取财务报表（三表完整数据）"""
    print("\n📊 财务报表爬取选项")
    print("=" * 40)
    print("1. 爬取所有股票财务报表")
    print("2. 按证券代码爬取单个股票财务报表")
    print("3. 批量爬取指定股票财务报表")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        print("\n📊 开始爬取所有股票财务报表...")
        crawler = FinancialStatementsCrawler(DataRepository())
        crawler.crawl_financial_statements()
        print("✅ 财务报表爬取完成！")
    elif choice == '2':
        symbol = input("请输入证券代码（如 SH600519）: ").strip().upper()
        if symbol:
            print(f"\n📊 开始爬取 {symbol} 的财务报表...")
            crawler = FinancialStatementsCrawler(DataRepository())
            success = crawler.crawl_single_stock_statements(symbol)
            if success:
                print(f"✅ {symbol} 财务报表爬取完成！")
            else:
                print(f"❌ {symbol} 财务报表爬取失败！")
        else:
            print("❌ 证券代码不能为空")
    elif choice == '3':
        symbols_input = input("请输入证券代码列表，用逗号分隔（如 SH600519,SZ000001）: ").strip().upper()
        if symbols_input:
            symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]
            print(f"\n📊 开始批量爬取财务报表，共 {len(symbols)} 只股票...")
            crawler = FinancialStatementsCrawler(DataRepository())
            success_count = 0
            for i, symbol in enumerate(symbols, 1):
                print(f"\n[{i}/{len(symbols)}] 爬取 {symbol}...")
                try:
                    success = crawler.crawl_single_stock_statements(symbol)
                    if success:
                        success_count += 1
                        print(f"✅ {symbol} 完成")
                    else:
                        print(f"❌ {symbol} 失败")
                except Exception as e:
                    print(f"❌ {symbol} 异常: {e}")
            print(f"\n📊 批量爬取完成，成功: {success_count}/{len(symbols)}")
        else:
            print("❌ 证券代码列表不能为空")
    else:
        print("❌ 无效选择")



def crawl_all_data():
    """爬取所有数据"""
    print("\n🔄 开始爬取所有数据...")
    
    # 1. 公司信息
    print("1/6 爬取公司信息...")
    company_crawler = CompanyInfoCrawler(DataRepository())
    company_crawler.crawl_company_info()
    
    # 2. 获取股票信息（完整字段）
    print("2/6 获取股票信息（完整字段）...")
    stock_crawler = StockInfoCrawler(DataRepository())
    stock_crawler.crawl_stock_list()
    
    # 3. 创建股票列表（简化字段）
    print("3/6 创建股票列表（简化字段）...")
    stock_crawler.create_simplified_stock_list()
    
    # 4. K线数据
    print("4/6 爬取K线数据...")
    kline_crawler = KlineCrawler(DataRepository())
    kline_crawler.crawl_kline_data('after')
    
    # 5. 财务数据
    print("5/6 爬取财务数据...")
    financial_crawler = FinancialCrawler(DataRepository())
    financial_crawler.crawl_financial_data()
    
    # 6. 财务报表
    print("6/6 爬取财务报表...")
    statements_crawler = FinancialStatementsCrawler(DataRepository())
    statements_crawler.crawl_financial_statements()
    
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
        choice = input("请选择功能 (0-7): ").strip()
        
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
            crawl_financial_statements()
        elif choice == '7':
            crawl_all_data()
        else:
            print("❌ 无效选择，请重新输入！")

if __name__ == "__main__":
    main()