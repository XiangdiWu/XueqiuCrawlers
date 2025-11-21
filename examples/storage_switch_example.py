"""
存储切换示例 - 演示如何在数据库和CSV存储之间一键切换
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.crawler_service import CrawlerService
from database.database import DataRepository
from config.settings import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def config_based_switching():
    """基于配置的存储切换"""
    print("=== 基于配置的存储切换 ===")
    
    # 显示当前配置
    current_config = Config.STORAGE_CONFIG
    print(f"当前存储配置:")
    print(f"  类型: {current_config['type']}")
    print(f"  CSV路径: {current_config['csv_path']}")
    print(f"  编码: {current_config['csv_encoding']}")
    
    # 根据配置初始化服务
    print(f"\n根据配置初始化服务...")
    service = CrawlerService()  # 自动使用配置中的存储类型
    print(f"服务使用存储类型: {service.storage_type}")
    
    # 获取存储信息
    info = service.get_storage_info()
    print(f"存储信息: {info}")


def manual_switching():
    """手动存储切换"""
    print("\n=== 手动存储切换 ===")
    
    # 初始化为CSV模式
    print("1. 初始化为CSV模式")
    service = CrawlerService(storage_type='csv')
    print(f"   存储类型: {service.storage_type}")
    
    # 保存一些测试数据
    print("   保存测试数据...")
    test_data = {
        'symbol': 'TEST001',
        'code': 'TEST001',
        'name': '测试股票',
        'current': 10.0,
        'percent': 1.5,
        'high52w': 15.0,
        'low52w': 8.0,
        'marketcapital': 1000000000,
        'amount': 5000000,
        'volume': 500000,
        'pe_ttm': 20.0
    }
    
    success = service.data_repo.save_stock_basic_info(test_data)
    print(f"   保存结果: {success}")
    
    # 切换到数据库模式
    print("\n2. 切换到数据库模式")
    try:
        service.switch_storage('database')
        print(f"   切换成功，存储类型: {service.storage_type}")
        
        # 尝试保存相同的数据到数据库
        print("   保存测试数据到数据库...")
        success = service.data_repo.save_stock_basic_info(test_data)
        print(f"   保存结果: {success}")
        
    except Exception as e:
        print(f"   切换失败: {e}")
    
    # 切换回CSV模式
    print("\n3. 切换回CSV模式")
    service.switch_storage('csv')
    print(f"   切换成功，存储类型: {service.storage_type}")


def data_repository_comparison():
    """数据仓库对比"""
    print("\n=== 数据仓库功能对比 ===")
    
    # CSV模式仓库
    print("CSV模式仓库:")
    csv_repo = DataRepository(storage_type='csv')
    
    # 测试基本功能
    print("  测试基本功能...")
    test_symbols = csv_repo.get_stock_symbols()
    print(f"    获取股票代码: {len(test_symbols)} 个")
    
    unprocessed_fin = csv_repo.get_unprocessed_finmain_stocks()
    print(f"    未处理财务数据股票: {len(unprocessed_fin)} 个")
    
    unprocessed_kline = csv_repo.get_unprocessed_kline_stocks()
    print(f"    未处理K线数据股票: {len(unprocessed_kline)} 个")
    
    # 获取存储信息
    csv_info = csv_repo.get_storage_info()
    print(f"    存储信息: {csv_info['type']}")
    
    # 数据库模式仓库
    print("\n数据库模式仓库:")
    try:
        db_repo = DataRepository(storage_type='database')
        
        # 测试基本功能
        print("  测试基本功能...")
        test_symbols = db_repo.get_stock_symbols()
        print(f"    获取股票代码: {len(test_symbols)} 个")
        
        unprocessed_fin = db_repo.get_unprocessed_finmain_stocks()
        print(f"    未处理财务数据股票: {len(unprocessed_fin)} 个")
        
        unprocessed_kline = db_repo.get_unprocessed_kline_stocks()
        print(f"    未处理K线数据股票: {len(unprocessed_kline)} 个")
        
        # 获取存储信息
        db_info = db_repo.get_storage_info()
        print(f"    存储信息: {db_info['type']}")
        
    except Exception as e:
        print(f"    数据库模式不可用: {e}")


def crawler_with_different_storage():
    """不同存储模式下的爬虫使用"""
    print("\n=== 不同存储模式下的爬虫使用 ===")
    
    # CSV模式爬虫
    print("CSV模式爬虫:")
    csv_service = CrawlerService(storage_type='csv')
    print(f"  存储类型: {csv_service.storage_type}")
    print(f"  爬虫初始化完成")
    
    # 数据库模式爬虫
    print("\n数据库模式爬虫:")
    try:
        db_service = CrawlerService(storage_type='database')
        print(f"  存储类型: {db_service.storage_type}")
        print(f"  爬虫初始化完成")
    except Exception as e:
        print(f"  数据库模式爬虫初始化失败: {e}")


def backup_and_recovery():
    """备份和恢复示例"""
    print("\n=== 备份和恢复示例 ===")
    
    # CSV模式备份
    print("CSV模式备份:")
    csv_service = CrawlerService(storage_type='csv')
    
    # 创建备份
    success = csv_service.create_backup()
    print(f"  备份结果: {success}")
    
    # 数据库模式备份
    print("\n数据库模式备份:")
    try:
        db_service = CrawlerService(storage_type='database')
        success = db_service.create_backup()
        print(f"  备份结果: {success}")
    except Exception as e:
        print(f"  备份失败: {e}")


def performance_comparison():
    """性能对比示例"""
    print("\n=== 性能对比示例 ===")
    
    import time
    
    # 测试数据
    test_data = []
    for i in range(100):
        test_data.append({
            'symbol': f'TEST{i:04d}',
            'code': f'TEST{i:04d}',
            'name': f'测试股票{i}',
            'current': 10.0 + i * 0.1,
            'percent': i * 0.01,
            'high52w': 15.0 + i * 0.1,
            'low52w': 8.0 + i * 0.1,
            'marketcapital': 1000000000 + i * 1000000,
            'amount': 5000000 + i * 50000,
            'volume': 500000 + i * 5000,
            'pe_ttm': 20.0 + i * 0.1
        })
    
    # CSV模式性能测试
    print("CSV模式性能测试:")
    csv_repo = DataRepository(storage_type='csv')
    
    start_time = time.time()
    success = csv_repo.batch_save_stock_data(test_data)
    csv_time = time.time() - start_time
    
    print(f"  保存 {len(test_data)} 条记录")
    print(f"  耗时: {csv_time:.2f} 秒")
    print(f"  平均每条: {csv_time/len(test_data)*1000:.2f} 毫秒")
    
    # 数据库模式性能测试
    print("\n数据库模式性能测试:")
    try:
        db_repo = DataRepository(storage_type='database')
        
        start_time = time.time()
        success = db_repo.batch_save_stock_data(test_data)
        db_time = time.time() - start_time
        
        print(f"  保存 {len(test_data)} 条记录")
        print(f"  耗时: {db_time:.2f} 秒")
        print(f"  平均每条: {db_time/len(test_data)*1000:.2f} 毫秒")
        
        # 性能对比
        print(f"\n性能对比:")
        if csv_time > 0 and db_time > 0:
            ratio = db_time / csv_time
            if ratio > 1:
                print(f"  数据库比CSV慢 {ratio:.2f} 倍")
            else:
                print(f"  数据库比CSV快 {1/ratio:.2f} 倍")
        
    except Exception as e:
        print(f"  数据库模式测试失败: {e}")


def configuration_management():
    """配置管理示例"""
    print("\n=== 配置管理示例 ===")
    
    # 显示所有配置
    print("当前存储配置:")
    storage_config = Config.STORAGE_CONFIG
    for key, value in storage_config.items():
        print(f"  {key}: {value}")
    
    # 修改配置示例（实际修改需要编辑配置文件）
    print("\n配置说明:")
    print("  type: 存储类型 ('database' 或 'csv')")
    print("  csv_path: CSV文件存储路径")
    print("  csv_encoding: CSV文件编码 (推荐 'utf-8-sig' 支持Excel)")
    print("  create_backup: 是否创建备份")
    print("  backup_path: 备份文件路径")
    
    print("\n修改配置方法:")
    print("  1. 编辑 config/settings.py 文件")
    print("  2. 修改 STORAGE_CONFIG 字典中的值")
    print("  3. 重新启动程序即可生效")


def main():
    """主函数"""
    print("存储切换功能演示")
    print("=" * 60)
    
    try:
        config_based_switching()
        manual_switching()
        data_repository_comparison()
        crawler_with_different_storage()
        backup_and_recovery()
        performance_comparison()
        configuration_management()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        
        print("\n使用总结:")
        print("1. 通过修改 config/settings.py 中的 STORAGE_CONFIG.type 可以全局切换存储方式")
        print("2. 也可以在代码中手动指定 storage_type 参数")
        print("3. CSV模式适合小规模数据和无数据库环境")
        print("4. 数据库模式适合大规模数据和高性能需求")
        print("5. 两种模式提供相同的API接口，可以无缝切换")
        
    except Exception as e:
        logger.error(f"执行示例时出错: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()