"""
CSV存储使用示例
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.csv_storage import CSVStorage
from database.database import DataRepository
from utils.logger import get_logger

logger = get_logger(__name__)


def basic_csv_usage():
    """基础CSV使用示例"""
    print("=== CSV存储基础使用示例 ===")
    
    # 初始化CSV存储
    csv_storage = CSVStorage(csv_path='data/example_csv')
    
    # 示例数据
    stock_data = [
        {
            'symbol': 'SH600000',
            'name': '浦发银行',
            'current': 10.50,
            'percent': 2.5,
            'volume': 1000000,
            'amount': 10500000
        },
        {
            'symbol': 'SH600001',
            'name': '邯郸钢铁',
            'current': 5.20,
            'percent': -1.2,
            'volume': 800000,
            'amount': 4160000
        }
    ]
    
    # 保存数据
    print("保存股票数据...")
    success = csv_storage.save_to_csv(stock_data, 'stock_list')
    print(f"保存结果: {success}")
    
    # 读取数据
    print("\n读取股票数据...")
    data = csv_storage.read_from_csv('stock_list')
    print(f"读取到 {len(data)} 条记录")
    for item in data:
        print(f"  {item['symbol']}: {item['name']} - {item['current']}")
    
    # 追加数据
    print("\n追加新数据...")
    new_data = [{
        'symbol': 'SH600002',
        'name': '齐鲁石化',
        'current': 8.80,
        'percent': 0.5,
        'volume': 600000,
        'amount': 5280000
    }]
    
    success = csv_storage.append_data(new_data, 'stock_list', 'symbol')
    print(f"追加结果: {success}")
    
    # 再次读取查看结果
    data = csv_storage.read_from_csv('stock_list')
    print(f"追加后共 {len(data)} 条记录")


def csv_file_operations():
    """CSV文件操作示例"""
    print("\n=== CSV文件操作示例 ===")
    
    csv_storage = CSVStorage(csv_path='data/example_csv')
    
    # 获取文件信息
    print("获取文件信息...")
    file_info = csv_storage.get_file_info('stock_list')
    print(f"文件信息: {file_info}")
    
    # 创建备份
    print("\n创建备份...")
    success = csv_storage.create_backup('stock_list')
    print(f"备份结果: {success}")
    
    # 导出到Excel
    print("\n导出到Excel...")
    success = csv_storage.export_to_excel(['stock_list'], 'data/example_csv/stock_export.xlsx')
    print(f"导出结果: {success}")


def data_repository_csv_mode():
    """数据仓库CSV模式示例"""
    print("\n=== 数据仓库CSV模式示例 ===")
    
    # 使用CSV模式初始化数据仓库
    data_repo = DataRepository(storage_type='csv')
    
    # 保存股票数据
    print("保存股票数据...")
    stock_data = {
        'symbol': 'SZ000001',
        'code': 'SZ000001',
        'name': '平安银行',
        'current': 15.60,
        'percent': 1.8,
        'high52w': 20.50,
        'low52w': 12.30,
        'marketcapital': 3000000000,
        'amount': 25000000,
        'volume': 1600000,
        'pe_ttm': 8.5
    }
    
    success = data_repo.save_stock_basic_info(stock_data)
    print(f"保存结果: {success}")
    
    # 保存公司信息
    print("\n保存公司信息...")
    company_data = {
        'compcode': 'SZ000001',
        'compname': '平安银行股份有限公司',
        'engname': 'Ping An Bank Co., Ltd.',
        'founddate': '1987-12-22',
        'regcapital': '19405918198',
        'chairman': '谢永林',
        'manager': '胡跃飞',
        'leconstant': '深圳市',
        'accfirm': '安永华明会计师事务所',
        'regaddr': '广东省深圳市',
        'officeaddr': '广东省深圳市',
        'compintro': '平安银行股份有限公司是一家全国性股份制商业银行',
        'bizscope': '银行业务',
        'majorbiz': '商业银行业务',
        'compsname': '平安银行',
        'region': '深圳'
    }
    
    success = data_repo.save_company_info(company_data)
    print(f"保存结果: {success}")
    
    # 获取存储信息
    print("\n获取存储信息...")
    storage_info = data_repo.get_storage_info()
    print(f"存储类型: {storage_info['type']}")
    print("文件信息:")
    for table, info in storage_info['files'].items():
        if info.get('exists'):
            print(f"  {table}: {info['record_count']} 条记录, {info['size']} 字节")


def csv_vs_database_comparison():
    """CSV与数据库模式对比示例"""
    print("\n=== CSV与数据库模式对比示例 ===")
    
    # CSV模式
    print("CSV模式:")
    csv_repo = DataRepository(storage_type='csv')
    csv_info = csv_repo.get_storage_info()
    print(f"  存储类型: {csv_info['type']}")
    print(f"  配置: {csv_info['config']}")
    
    # 数据库模式（如果配置了数据库）
    print("\n数据库模式:")
    try:
        db_repo = DataRepository(storage_type='database')
        db_info = db_repo.get_storage_info()
        print(f"  存储类型: {db_info['type']}")
        if 'tables' in db_info:
            print("  表信息:")
            for table, count in db_info['tables'].items():
                print(f"    {table}: {count} 条记录")
        elif 'error' in db_info:
            print(f"  错误: {db_info['error']}")
    except Exception as e:
        print(f"  数据库模式不可用: {e}")


def switch_storage_example():
    """存储切换示例"""
    print("\n=== 存储切换示例 ===")
    
    from services.crawler_service import CrawlerService
    
    # 初始化为CSV模式
    print("初始化为CSV模式...")
    service = CrawlerService(storage_type='csv')
    print(f"当前存储类型: {service.storage_type}")
    
    # 获取存储信息
    info = service.get_storage_info()
    print(f"存储信息: {info['type']}")
    
    # 切换到数据库模式
    print("\n切换到数据库模式...")
    try:
        service.switch_storage('database')
        print(f"切换成功，当前存储类型: {service.storage_type}")
    except Exception as e:
        print(f"切换失败: {e}")
    
    # 切换回CSV模式
    print("\n切换回CSV模式...")
    service.switch_storage('csv')
    print(f"当前存储类型: {service.storage_type}")


def advanced_csv_features():
    """高级CSV功能示例"""
    print("\n=== 高级CSV功能示例 ===")
    
    csv_storage = CSVStorage(csv_path='data/example_csv')
    
    # 批量操作
    print("批量保存数据...")
    batch_data = []
    for i in range(10):
        batch_data.append({
            'symbol': f'TEST{i:03d}',
            'name': f'测试股票{i}',
            'current': 10.0 + i,
            'percent': i * 0.1,
            'volume': 100000 * (i + 1),
            'amount': 1000000 * (i + 1)
        })
    
    success = csv_storage.save_to_csv(batch_data, 'test_batch', mode='w')
    print(f"批量保存结果: {success}")
    
    # 使用后缀保存不同版本
    print("\n使用后缀保存不同版本...")
    csv_storage.save_to_csv(batch_data[:5], 'test_batch', suffix='v1')
    csv_storage.save_to_csv(batch_data[5:], 'test_batch', suffix='v2')
    
    # 读取不同版本
    print("读取不同版本:")
    for suffix in ['', 'v1', 'v2']:
        data = csv_storage.read_from_csv('test_batch', suffix)
        print(f"  版本 '{suffix or '默认'}': {len(data)} 条记录")
    
    # 清理旧文件（演示用，实际使用时请谨慎）
    print("\n清理测试文件...")
    # csv_storage.clean_old_files(days=0)  # 清理所有文件
    print("清理完成（演示）")


def main():
    """主函数"""
    print("CSV存储功能演示")
    print("=" * 50)
    
    try:
        basic_csv_usage()
        csv_file_operations()
        data_repository_csv_mode()
        csv_vs_database_comparison()
        switch_storage_example()
        advanced_csv_features()
        
        print("\n" + "=" * 50)
        print("所有示例执行完成！")
        
    except Exception as e:
        logger.error(f"执行示例时出错: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()