"""
数据库操作示例
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import DataRepository
from utils.logger import get_logger


def example_data_repository():
    """数据仓库使用示例"""
    print("=== 数据仓库示例 ===")
    
    # 创建数据仓库
    data_repo = DataRepository()
    
    # 获取股票列表
    print("获取股票列表...")
    try:
        symbols = data_repo.get_stock_symbols()
        print(f"获取到 {len(symbols)} 支股票")
        if symbols:
            print(f"前5支: {symbols[:5]}")
            
    except Exception as e:
        print(f"获取股票列表失败: {e}")
    
    # 获取存储信息
    print("获取存储信息...")
    try:
        storage_info = data_repo.get_storage_info()
        print(f"存储类型: {storage_info['type']}")
        print("存储信息获取成功")
        
    except Exception as e:
        print(f"获取存储信息失败: {e}")


def example_stock_operations():
    """股票操作示例"""
    print("=== 股票操作示例 ===")
    
    # 创建数据仓库
    data_repo = DataRepository()
    
    # 获取股票代码列表
    print("获取股票代码列表...")
    try:
        symbols = data_repo.get_stock_symbols()
        print(f"共 {len(symbols)} 支股票")
        print(f"前10支: {symbols[:10]}")
        
    except Exception as e:
        print(f"获取股票代码失败: {e}")
    
    # 获取未处理财务数据的股票
    print("获取未处理财务数据的股票...")
    try:
        unprocessed_stocks = data_repo.get_unprocessed_finmain_stocks()
        print(f"未处理财务数据的股票: {len(unprocessed_stocks)} 支")
        if unprocessed_stocks:
            print(f"前5支: {unprocessed_stocks[:5]}")
            
    except Exception as e:
        print(f"获取未处理股票失败: {e}")
    
    # 获取未处理K线数据的股票
    print("获取未处理K线数据的股票...")
    try:
        unprocessed_kline = data_repo.get_unprocessed_kline_stocks()
        print(f"未处理K线数据的股票: {len(unprocessed_kline)} 支")
        if unprocessed_kline:
            print(f"前5支: {unprocessed_kline[:5]}")
            
    except Exception as e:
        print(f"获取未处理K线股票失败: {e}")


def example_data_insertion():
    """数据插入示例"""
    print("=== 数据插入示例 ===")
    
    data_repo = DataRepository()
    
    # 插入股票基本信息示例
    print("插入股票基本信息示例...")
    stock_data = {
        'symbol': 'EXAMPLE001',
        'code': 'EXAMPLE001',
        'name': '示例股票',
        'current': 10.50,
        'percent': 2.5,
        'high52w': 15.00,
        'low52w': 8.00,
        'marketcapital': 1000000000,
        'amount': 50000000,
        'volume': 5000000,
        'pe_ttm': 20.5
    }
    
    try:
        success = data_repo.save_stock_basic_info(stock_data)
        print(f"股票基本信息插入结果: {success}")
    except Exception as e:
        print(f"插入股票信息失败: {e}")
    
    # 插入公司信息示例
    print("插入公司信息示例...")
    company_data = {
        'compcode': 'EXAMPLE001',
        'compname': '示例股份有限公司',
        'engname': 'Example Co., Ltd.',
        'founddate': '2010-01-01',
        'regcapital': '1000000000',
        'chairman': '张三',
        'manager': '李四',
        'leconstant': '',
        'accfirm': '某某会计师事务所',
        'regaddr': '北京市朝阳区',
        'officeaddr': '北京市朝阳区',
        'compintro': '这是一家示例公司',
        'bizscope': '软件开发、技术服务',
        'majorbiz': '软件开发',
        'compsname': '示例股份',
        'region': '北京'
    }
    
    try:
        success = data_repo.save_company_info(company_data)
        print(f"公司信息插入结果: {success}")
    except Exception as e:
        print(f"插入公司信息失败: {e}")


def main():
    """主函数"""
    logger = get_logger('example_database')
    
    try:
        # 示例1: 数据仓库
        example_data_repository()
        
        # 示例2: 股票操作
        example_stock_operations()
        
        # 示例3: 数据插入
        example_data_insertion()
        
        print("数据库操作示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()