"""
批处理示例
"""
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.crawler_service import CrawlerService
from crawlers.stock_crawler import StockCrawler
from database.database import DataRepository
from utils.logger import get_logger


def example_sequential_processing():
    """顺序处理示例"""
    print("=== 顺序处理示例 ===")
    
    # 模拟股票列表
    symbols = ['SZ000001', 'SZ000002', 'SZ000003', 'SH600000', 'SH600001']
    
    def process_symbol(symbol):
        """处理单个股票"""
        print(f"开始处理: {symbol}")
        time.sleep(1)  # 模拟处理时间
        print(f"完成处理: {symbol}")
        return f"{symbol}_processed"
    
    start_time = time.time()
    results = []
    
    # 顺序处理
    for symbol in symbols:
        try:
            result = process_symbol(symbol)
            results.append(result)
        except Exception as e:
            print(f"处理 {symbol} 失败: {e}")
    
    end_time = time.time()
    
    print(f"顺序处理完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"处理结果: {results}")


def example_batch_processing():
    """批处理示例"""
    print("=== 批处理示例 ===")
    
    # 模拟股票列表
    symbols = ['SZ000001', 'SZ000002', 'SZ000003', 'SH600000', 'SH600001']
    
    def process_batch(batch_symbols):
        """处理一批股票"""
        print(f"开始处理批次: {batch_symbols}")
        time.sleep(2)  # 模拟批次处理时间
        
        batch_results = []
        for symbol in batch_symbols:
            try:
                # 模拟处理
                result = f"{symbol}_processed"
                batch_results.append(result)
            except Exception as e:
                print(f"处理 {symbol} 失败: {e}")
        
        print(f"批次完成: {batch_symbols}")
        return batch_results
    
    # 分批处理
    batch_size = 2
    batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
    
    start_time = time.time()
    all_results = []
    
    for batch in batches:
        batch_results = process_batch(batch)
        all_results.extend(batch_results)
        
        # 批次间延迟
        time.sleep(0.5)
    
    end_time = time.time()
    
    print(f"批处理完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"处理结果: {all_results}")


def example_threaded_processing():
    """多线程处理示例"""
    print("=== 多线程处理示例 ===")
    
    # 模拟股票列表
    symbols = ['SZ000001', 'SZ000002', 'SZ000003', 'SH600000', 'SH600001', 'SH600002']
    
    def process_symbol_threaded(symbol):
        """线程中处理单个股票"""
        print(f"线程处理开始: {symbol}")
        time.sleep(1)  # 模拟处理时间
        print(f"线程处理完成: {symbol}")
        return f"{symbol}_processed"
    
    start_time = time.time()
    results = []
    
    # 使用线程池
    max_workers = 3
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_symbol = {
            executor.submit(process_symbol_threaded, symbol): symbol 
            for symbol in symbols
        }
        
        # 收集结果
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"处理 {symbol} 失败: {e}")
    
    end_time = time.time()
    
    print(f"多线程处理完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"处理结果: {results}")


def example_progress_tracking():
    """进度跟踪示例"""
    print("=== 进度跟踪示例 ===")
    
    import tqdm
    
    # 模拟大量股票
    symbols = [f"SYMBOL{i:06d}" for i in range(1, 101)]
    
    def process_symbol_with_progress(symbol):
        """带进度跟踪的处理"""
        time.sleep(0.1)  # 模拟处理时间
        return f"{symbol}_processed"
    
    start_time = time.time()
    results = []
    
    # 使用tqdm显示进度条
    for symbol in tqdm.tqdm(symbols, desc="处理股票"):
        try:
            result = process_symbol_with_progress(symbol)
            results.append(result)
        except Exception as e:
            print(f"处理 {symbol} 失败: {e}")
    
    end_time = time.time()
    
    print(f"进度跟踪处理完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"成功处理: {len(results)}/{len(symbols)}")


def example_checkpoint_processing():
    """检查点处理示例"""
    print("=== 检查点处理示例 ===")
    
    import json
    
    # 模拟股票列表
    symbols = ['SZ000001', 'SZ000002', 'SZ000003', 'SH600000', 'SH600001']
    checkpoint_file = 'checkpoint.json'
    
    def load_checkpoint():
        """加载检查点"""
        try:
            if os.path.exists(checkpoint_file):
                with open(checkpoint_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载检查点失败: {e}")
        return {}
    
    def save_checkpoint(checkpoint_data):
        """保存检查点"""
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            print(f"保存检查点失败: {e}")
    
    def process_symbol_with_checkpoint(symbol):
        """带检查点的处理"""
        print(f"处理: {symbol}")
        time.sleep(0.5)  # 模拟处理时间
        return f"{symbol}_processed"
    
    # 加载检查点
    checkpoint = load_checkpoint()
    processed_symbols = set(checkpoint.get('processed_symbols', []))
    
    print(f"已处理股票: {len(processed_symbols)}")
    
    results = []
    
    for symbol in symbols:
        # 跳过已处理的股票
        if symbol in processed_symbols:
            print(f"跳过已处理: {symbol}")
            continue
        
        try:
            result = process_symbol_with_checkpoint(symbol)
            results.append(result)
            
            # 更新检查点
            processed_symbols.add(symbol)
            checkpoint['processed_symbols'] = list(processed_symbols)
            save_checkpoint(checkpoint)
            
        except Exception as e:
            print(f"处理 {symbol} 失败: {e}")
    
    print(f"检查点处理完成，结果: {results}")
    
    # 清理检查点文件
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)


def example_error_recovery():
    """错误恢复示例"""
    print("=== 错误恢复示例 ===")
    
    # 模拟股票列表，包含一些会失败的股票
    symbols = ['SZ000001', 'FAIL001', 'SZ000002', 'FAIL002', 'SH600000']
    
    def process_symbol_with_recovery(symbol):
        """带错误恢复的处理"""
        # 模拟某些股票会失败
        if symbol.startswith('FAIL'):
            raise Exception(f"股票 {symbol} 处理失败")
        
        print(f"处理成功: {symbol}")
        time.sleep(0.5)
        return f"{symbol}_processed"
    
    results = []
    failed_symbols = []
    
    for symbol in symbols:
        try:
            result = process_symbol_with_recovery(symbol)
            results.append(result)
            
        except Exception as e:
            print(f"处理失败: {symbol}, 错误: {e}")
            failed_symbols.append(symbol)
            
            # 尝试恢复
            print(f"尝试恢复 {symbol}...")
            time.sleep(1)
            
            try:
                result = process_symbol_with_recovery(symbol)
                results.append(result)
                print(f"恢复成功: {symbol}")
                failed_symbols.remove(symbol)
                
            except Exception as e2:
                print(f"恢复失败: {symbol}, 错误: {e2}")
    
    print(f"处理完成，成功: {len(results)}, 失败: {len(failed_symbols)}")
    print(f"失败的股票: {failed_symbols}")


def example_database_batch_operations():
    """数据仓库批处理操作示例"""
    print("=== 数据仓库批处理操作示例 ===")
    
    data_repo = DataRepository(storage_type='csv')
    
    # 模拟批量插入数据
    stock_data_list = [
        {'symbol': 'TEST001', 'name': '测试股票1', 'current': 10.5},
        {'symbol': 'TEST002', 'name': '测试股票2', 'current': 20.5},
        {'symbol': 'TEST003', 'name': '测试股票3', 'current': 30.5},
    ]
    
    def batch_insert_stocks(stock_list):
        """批量插入股票"""
        try:
            # 批量保存
            success = data_repo.batch_save_stock_data(stock_list)
            if success:
                print(f"批量保存成功: {len(stock_list)} 条记录")
            else:
                print("批量保存失败")
        except Exception as e:
            print(f"批量保存失败: {e}")
    
    # 执行批量保存（示例）
    batch_insert_stocks(stock_data_list)
    print("数据仓库批处理示例完成")


def main():
    """主函数"""
    logger = get_logger('example_batch')
    
    try:
        # 示例1: 顺序处理
        example_sequential_processing()
        
        # 示例2: 批处理
        example_batch_processing()
        
        # 示例3: 多线程处理
        example_threaded_processing()
        
        # 示例4: 进度跟踪
        example_progress_tracking()
        
        # 示例5: 检查点处理
        example_checkpoint_processing()
        
        # 示例6: 错误恢复
        example_error_recovery()
        
        # 示例7: 数据库批处理
        example_database_batch_operations()
        
        print("批处理示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()