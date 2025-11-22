"""
CSV存储管理器
"""
import os
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from engine.logger import get_logger

logger = get_logger(__name__)


class CSVStorage:
    """CSV存储管理器"""
    
    def __init__(self, csv_path: str = 'data/csv', encoding: str = 'utf-8-sig'):
        self.csv_path = csv_path
        self.encoding = encoding
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        os.makedirs(self.csv_path, exist_ok=True)
        # 创建子目录 - 匹配实际的文件夹结构
        subdirs = ['company_info', 'financial', 'kline', 'stock_info', 'stock_list']
        for subdir in subdirs:
            os.makedirs(os.path.join(self.csv_path, subdir), exist_ok=True)
    
    def _get_filename(self, table_name: str, suffix: str = '') -> str:
        """获取文件名"""
        if suffix:
            return f"{table_name}_{suffix}.csv"
        return f"{table_name}.csv"
    
    def _get_filepath(self, table_name: str, suffix: str = '') -> str:
        """获取完整文件路径"""
        filename = self._get_filename(table_name, suffix)
        # 根据表名确定子目录 - 匹配实际的文件夹结构
        if table_name == 'stock_list':
            subdir = 'stock_list'
        elif table_name in ['stock_info']:
            subdir = 'stock_info'
        elif table_name == 'company_profile':
            subdir = 'company_info'
        elif table_name in ['financial_data', 'financial_summary']:
            subdir = 'financial'
        elif table_name == 'kline_data':
            subdir = 'kline'
        else:
            subdir = ''
        
        if subdir:
            return os.path.join(self.csv_path, subdir, filename)
        return os.path.join(self.csv_path, filename)
    
    def get_stock_list_filepath_by_date(self, date_str: str = None) -> str:
        """
        根据日期获取股票列表文件路径 - stock_list/YYYY-MM-DD.csv格式
        
        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            str: 股票列表文件路径
        """
        if date_str is None:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 创建stock_list目录
        stock_list_dir = os.path.join(self.csv_path, 'stock_list')
        os.makedirs(stock_list_dir, exist_ok=True)
        
        filename = f"{date_str}.csv"
        return os.path.join(stock_list_dir, filename)
    
    def save_stock_list_by_date(self, data: List[Dict[str, Any]], date_str: str = None) -> bool:
        """
        按日期保存股票列表 - 使用stock_list/YYYY-MM-DD.csv格式
        
        Args:
            data: 股票数据列表
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning("没有股票数据需要保存")
            return False
        
        try:
            if date_str is None:
                from datetime import datetime
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            filepath = self.get_stock_list_filepath_by_date(date_str)
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条股票数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存股票列表失败: {e}")
            return False
    
    def get_stock_list_by_date(self, date_str: str = None) -> List[Dict[str, Any]]:
        """
        获取指定日期的股票列表 - 从stock_list/YYYY-MM-DD.csv读取
        
        Args:
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            
        Returns:
            List[Dict]: 股票数据列表
        """
        try:
            if date_str is None:
                from datetime import datetime
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            filepath = self.get_stock_list_filepath_by_date(date_str)
            
            if not os.path.exists(filepath):
                logger.warning(f"股票列表文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条股票数据")
            return data
            
        except Exception as e:
            logger.error(f"读取股票列表失败: {e}")
            return []
    
    def get_company_filepath_by_symbol(self, symbol: str) -> str:
        """
        根据证券代码获取公司信息文件路径
        
        Args:
            symbol: 证券代码
            
        Returns:
            str: 公司信息文件路径
        """
        filename = f"company_{symbol}.csv"
        return os.path.join(self.csv_path, 'company_info', filename)
    
    def save_company_info_by_symbol(self, data: Dict[str, Any], symbol: str) -> bool:
        """
        按证券代码保存公司信息
        
        Args:
            data: 公司信息数据
            symbol: 证券代码
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning(f"没有公司信息要保存: {symbol}")
            return False
        
        try:
            filepath = self.get_company_filepath_by_symbol(symbol)
            
            # 获取字段名
            fieldnames = list(data.keys())
            
            with open(filepath, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
            
            logger.info(f"成功保存公司信息到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存公司信息失败 {symbol}: {e}")
            return False
    
    def get_company_info_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        根据证券代码获取公司信息
        
        Args:
            symbol: 证券代码
            
        Returns:
            Dict: 公司信息数据
        """
        try:
            filepath = self.get_company_filepath_by_symbol(symbol)
            
            if not os.path.exists(filepath):
                logger.warning(f"公司信息文件不存在: {filepath}")
                return {}
            
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    return dict(row)
            
            return {}
            
        except Exception as e:
            logger.error(f"读取公司信息失败 {symbol}: {e}")
            return {}
    
    def get_stock_info_filepath_by_date(self, date_str: str = None, suffix: str = '') -> str:
        """
        根据日期获取股票信息文件路径
        
        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            suffix: 文件名后缀
            
        Returns:
            str: 股票信息文件路径
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        if suffix:
            filename = f"{date_str}_{suffix}.csv"
        else:
            filename = f"{date_str}.csv"
        
        return os.path.join(self.csv_path, 'stock_info', filename)
    
    def save_stock_info_by_date(self, data: List[Dict[str, Any]], date_str: str = None, suffix: str = '') -> bool:
        """
        按日期保存股票信息
        
        Args:
            data: 股票信息数据列表
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            suffix: 文件名后缀
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning("没有股票信息需要保存")
            return False
        
        try:
            if date_str is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            filepath = self.get_stock_info_filepath_by_date(date_str, suffix)
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条股票信息到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存股票信息失败: {e}")
            return False
    
    def get_stock_info_by_date(self, date_str: str = None, suffix: str = '') -> List[Dict[str, Any]]:
        """
        获取指定日期的股票信息
        
        Args:
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            suffix: 文件名后缀
            
        Returns:
            List[Dict]: 股票信息数据列表
        """
        try:
            if date_str is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            filepath = self.get_stock_info_filepath_by_date(date_str, suffix)
            
            if not os.path.exists(filepath):
                logger.warning(f"股票信息文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条股票信息")
            return data
            
        except Exception as e:
            logger.error(f"读取股票信息失败: {e}")
            return []
    
    def get_company_profile_filepath(self) -> str:
        """
        获取公司概况文件路径
        
        Returns:
            str: 公司概况文件路径
        """
        return os.path.join(self.csv_path, 'company_info', 'company_profile.csv')
    
    def save_company_profile(self, data: List[Dict[str, Any]]) -> bool:
        """
        保存公司概况数据
        
        Args:
            data: 公司概况数据列表
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning("没有公司概况数据需要保存")
            return False
        
        try:
            filepath = self.get_company_profile_filepath()
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条公司概况数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存公司概况数据失败: {e}")
            return False
    
    def get_company_profile(self) -> List[Dict[str, Any]]:
        """
        获取公司概况数据
        
        Returns:
            List[Dict]: 公司概况数据列表
        """
        try:
            filepath = self.get_company_profile_filepath()
            
            if not os.path.exists(filepath):
                logger.warning(f"公司概况文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条公司概况数据")
            return data
            
        except Exception as e:
            logger.error(f"读取公司概况数据失败: {e}")
            return []
    
    def get_kline_filepath_by_date(self, date_str: str = None) -> str:
        """
        根据日期获取K线数据文件路径
        
        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            str: K线数据文件路径
        """
        if date_str is None:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        filename = f"{date_str}.csv"
        return os.path.join(self.csv_path, 'kline', filename)
    
    def save_kline_data_by_date(self, data: List[Dict[str, Any]], date_str: str = None) -> bool:
        """
        按日期保存K线数据
        
        Args:
            data: K线数据列表
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning("没有K线数据要保存")
            return False
        
        try:
            filepath = self.get_kline_filepath_by_date(date_str)
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条K线数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存K线数据失败: {e}")
            return False
    
    def save_to_csv(self, data: List[Dict[str, Any]], table_name: str, 
                    mode: str = 'a', suffix: str = '', chunk_size: int = 10000) -> bool:
        """
        保存数据到CSV文件 - 支持分块处理大数据
        
        Args:
            data: 要保存的数据
            table_name: 表名
            mode: 写入模式 ('a'追加, 'w'覆盖)
            suffix: 文件名后缀
            chunk_size: 分块大小，大数据时使用
        
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning(f"没有数据要保存到 {table_name}")
            return False
        
        try:
            filepath = self._get_filepath(table_name, suffix)
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            # 大数据分块处理
            if len(data) > chunk_size:
                logger.info(f"大数据量 {len(data)} 条，分块处理 (块大小: {chunk_size})")
                return self._save_chunked_data(data, filepath, fieldnames, mode, file_exists, chunk_size)
            
            # 小数据直接处理
            with open(filepath, mode, newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在或覆盖模式，写入表头
                if not file_exists or mode == 'w':
                    writer.writeheader()
                
                # 写入数据
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")
            return False
    
    def _save_chunked_data(self, data, filepath, fieldnames, mode, file_exists, chunk_size):
        """分块保存大数据"""
        try:
            with open(filepath, mode, newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在或覆盖模式，写入表头
                if not file_exists or mode == 'w':
                    writer.writeheader()
                
                # 分块写入
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]
                    writer.writerows(chunk)
                    logger.debug(f"写入第 {i//chunk_size + 1} 块，{len(chunk)} 条数据")
                    
                    # 定期刷新缓冲区
                    csvfile.flush()
            
            logger.info(f"分块保存完成，共 {len(data)} 条数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"分块保存失败: {e}")
            return False
    
    def read_from_csv(self, table_name: str, suffix: str = '', chunk_size: int = 50000) -> List[Dict[str, Any]]:
        """
        从CSV文件读取数据 - 支持分块读取大文件
        
        Args:
            table_name: 表名
            suffix: 文件名后缀
            chunk_size: 分块大小，大文件时使用
        
        Returns:
            List[Dict]: 数据列表
        """
        try:
            filepath = self._get_filepath(table_name, suffix)
            
            if not os.path.exists(filepath):
                logger.warning(f"CSV文件不存在: {filepath}")
                return []
            
            # 检查文件大小，决定是否分块处理
            file_size = os.path.getsize(filepath)
            if file_size > 50 * 1024 * 1024:  # 50MB以上使用分块
                logger.info(f"大文件检测 ({file_size/1024/1024:.1f}MB)，使用分块读取")
                return self._read_chunked_data(filepath, chunk_size)
            
            # 小文件直接读取
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条数据")
            return data
            
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            return []
    
    def _read_chunked_data(self, filepath, chunk_size):
        """分块读取大文件"""
        data = []
        try:
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                chunk_count = 0
                
                while True:
                    chunk = []
                    for _ in range(chunk_size):
                        try:
                            row = next(reader)
                            chunk.append(dict(row))
                        except StopIteration:
                            break
                    
                    if not chunk:
                        break
                    
                    data.extend(chunk)
                    chunk_count += 1
                    logger.debug(f"读取第 {chunk_count} 块，{len(chunk)} 条数据")
                    
                    # 内存管理：如果数据量太大，可以考虑流式处理
                    if len(data) > 1000000:  # 100万条数据警告
                        logger.warning("数据量过大，建议使用流式处理")
            
            logger.info(f"分块读取完成，共 {len(data)} 条数据")
            return data
            
        except Exception as e:
            logger.error(f"分块读取失败: {e}")
            return []
    
    def append_data(self, data: List[Dict[str, Any]], table_name: str, 
                    unique_key: str = None, suffix: str = '') -> bool:
        """
        追加数据，避免重复
        
        Args:
            data: 要追加的数据
            table_name: 表名
            unique_key: 唯一键字段名
            suffix: 文件名后缀
        
        Returns:
            bool: 是否成功
        """
        if not data:
            return False
        
        try:
            # 读取现有数据
            existing_data = self.read_from_csv(table_name, suffix)
            
            if existing_data and unique_key:
                # 获取现有数据的唯一键集合
                existing_keys = {item[unique_key] for item in existing_data}
                # 过滤掉重复数据
                new_data = [item for item in data if item.get(unique_key) not in existing_keys]
                
                if not new_data:
                    logger.info(f"没有新数据需要追加到 {table_name}")
                    return True
                
                logger.info(f"过滤掉 {len(data) - len(new_data)} 条重复数据")
            else:
                new_data = data
            
            # 追加新数据
            return self.save_to_csv(new_data, table_name, mode='a', suffix=suffix)
            
        except Exception as e:
            logger.error(f"追加数据失败: {e}")
            return False
    
    def create_backup(self, table_name: str, suffix: str = '') -> bool:
        """
        创建备份文件
        
        Args:
            table_name: 表名
            suffix: 文件名后缀
        
        Returns:
            bool: 是否成功
        """
        try:
            from config.settings import Config
            backup_config = Config.STORAGE_CONFIG
            backup_path = backup_config.get('backup_path', 'data/backup')
            
            os.makedirs(backup_path, exist_ok=True)
            
            # 生成带时间戳的备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_suffix = f"{suffix}_{timestamp}" if suffix else timestamp
            
            source_file = self._get_filepath(table_name, suffix)
            if not os.path.exists(source_file):
                logger.warning(f"源文件不存在，无法备份: {source_file}")
                return False
            
            # 复制文件到备份目录
            import shutil
            backup_filename = self._get_filename(table_name, backup_suffix)
            backup_filepath = os.path.join(backup_path, backup_filename)
            shutil.copy2(source_file, backup_filepath)
            
            logger.info(f"成功创建备份: {backup_filepath}")
            return True
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def get_file_info(self, table_name: str, suffix: str = '') -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            table_name: 表名
            suffix: 文件名后缀
        
        Returns:
            Dict: 文件信息
        """
        try:
            filepath = self._get_filepath(table_name, suffix)
            
            if not os.path.exists(filepath):
                return {'exists': False}
            
            stat = os.stat(filepath)
            data = self.read_from_csv(table_name, suffix)
            
            return {
                'exists': True,
                'filepath': filepath,
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'record_count': len(data),
                'field_count': len(data[0].keys()) if data else 0
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return {'exists': False, 'error': str(e)}
    
    def export_to_excel(self, table_names: List[str], output_file: str = None) -> bool:
        """
        导出多个CSV文件到Excel
        
        Args:
            table_names: 表名列表
            output_file: 输出文件路径
        
        Returns:
            bool: 是否成功
        """
        try:
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.csv_path, f'export_{timestamp}.xlsx')
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for table_name in table_names:
                    data = self.read_from_csv(table_name)
                    if data:
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=table_name, index=False)
                        logger.info(f"导出 {table_name} 到Excel: {len(data)} 条记录")
            
            logger.info(f"成功导出Excel文件: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            return False
    
    def clean_old_files(self, days: int = 30) -> bool:
        """
        清理旧文件
        
        Args:
            days: 保留天数
        
        Returns:
            bool: 是否成功
        """
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            deleted_count = 0
            for root, dirs, files in os.walk(self.csv_path):
                for file in files:
                    if file.endswith('.csv'):
                        filepath = os.path.join(root, file)
                        if os.path.getmtime(filepath) < cutoff_time:
                            os.remove(filepath)
                            deleted_count += 1
                            logger.info(f"删除旧文件: {filepath}")
            
            logger.info(f"清理完成，删除了 {deleted_count} 个旧文件")
            return True
            
        except Exception as e:
            logger.error(f"清理旧文件失败: {e}")
            return False
    
    # ==================== 财务数据相关方法 ====================
    
    def get_financial_filepath_by_symbol(self, symbol: str) -> str:
        """
        根据证券代码获取财务数据文件路径
        
        Args:
            symbol: 证券代码
            
        Returns:
            str: 财务数据文件路径
        """
        filename = f"{symbol}.csv"
        return os.path.join(self.csv_path, 'financial', filename)
    
    def save_financial_data_by_symbol(self, symbol: str, data: List[Dict[str, Any]]) -> bool:
        """
        按证券代码保存财务数据
        
        Args:
            symbol: 证券代码
            data: 财务数据列表
            
        Returns:
            bool: 是否成功
        """
        if not data:
            logger.warning(f"没有财务数据要保存: {symbol}")
            return False
        
        try:
            filepath = self.get_financial_filepath_by_symbol(symbol)
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerows(data)
            
            logger.info(f"成功保存 {len(data)} 条财务数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存财务数据失败 {symbol}: {e}")
            return False
    
    def get_financial_data_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """
        根据证券代码获取财务数据
        
        Args:
            symbol: 证券代码
            
        Returns:
            List[Dict]: 财务数据列表
        """
        try:
            filepath = self.get_financial_filepath_by_symbol(symbol)
            
            if not os.path.exists(filepath):
                logger.warning(f"财务数据文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条财务数据")
            return data
            
        except Exception as e:
            logger.error(f"读取财务数据失败: {e}")
            return []
    
    def get_financial_log_filepath(self) -> str:
        """
        获取财务数据处理日志文件路径
        
        Returns:
            str: 日志文件路径
        """
        return os.path.join(self.csv_path, 'financial', 'financial_log.csv')
    
    def save_financial_log(self, log_data: Dict[str, Any]) -> bool:
        """
        保存财务数据处理日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            bool: 是否成功
        """
        try:
            filepath = self.get_financial_log_filepath()
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = ['compcode', 'reportdate', 'timestamp']
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerow(log_data)
            
            return True
            
        except Exception as e:
            logger.error(f"保存财务日志失败: {e}")
            return False
    
    def get_financial_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务数据处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            filepath = self.get_financial_log_filepath()
            
            if not os.path.exists(filepath):
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            return data
            
        except Exception as e:
            logger.error(f"读取财务日志失败: {e}")
            return []
    
    def get_latest_stock_info(self) -> List[Dict[str, Any]]:
        """
        获取最新的股票信息列表
        
        Returns:
            List[Dict]: 股票信息列表
        """
        try:
            # 获取最新的stock_info文件
            stock_info_dir = os.path.join(self.csv_path, 'stock_info')
            if not os.path.exists(stock_info_dir):
                return []
            
            # 按修改时间排序，获取最新文件
            files = []
            for filename in os.listdir(stock_info_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(stock_info_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    files.append((mtime, filepath))
            
            if not files:
                return []
            
            # 获取最新文件
            latest_file = max(files, key=lambda x: x[0])[1]
            
            data = []
            with open(latest_file, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从最新文件 {os.path.basename(latest_file)} 读取了 {len(data)} 条股票信息")
            return data
            
        except Exception as e:
            logger.error(f"读取最新股票信息失败: {e}")
            return []
    
    # ==================== K线数据相关方法 ====================
    
    def get_kline_log_filepath(self) -> str:
        """
        获取K线数据处理日志文件路径
        
        Returns:
            str: 日志文件路径
        """
        return os.path.join(self.csv_path, 'kline', 'kline_log.csv')
    
    def save_kline_log(self, log_data: Dict[str, Any]) -> bool:
        """
        保存K线数据处理日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            bool: 是否成功
        """
        try:
            filepath = self.get_kline_log_filepath()
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = ['symbol', 'timestamp', 'crawl_date']
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerow(log_data)
            
            return True
            
        except Exception as e:
            logger.error(f"保存K线日志失败: {e}")
            return False
    
    def get_kline_logs(self) -> List[Dict[str, Any]]:
        """
        获取K线数据处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            filepath = self.get_kline_log_filepath()
            
            if not os.path.exists(filepath):
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            return data
            
        except Exception as e:
            logger.error(f"读取K线日志失败: {e}")
            return []
    
    def get_kline_data_by_symbol_and_date(self, symbol: str, date_str: str) -> List[Dict[str, Any]]:
        """
        根据股票代码和日期获取K线数据
        
        Args:
            symbol: 股票代码
            date_str: 日期字符串，格式YYYY-MM-DD
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            filepath = self.get_kline_filepath_by_date(date_str)
            
            if not os.path.exists(filepath):
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('symbol') == symbol:
                        data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条 {symbol} 的K线数据")
            return data
            
        except Exception as e:
            logger.error(f"读取K线数据失败 {symbol} {date_str}: {e}")
            return []
    
    def get_kline_data_by_symbol(self, symbol: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        根据股票代码获取K线数据（支持日期范围）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            kline_dir = os.path.join(self.csv_path, 'kline')
            if not os.path.exists(kline_dir):
                return []
            
            # 获取所有K线数据文件
            files = []
            for filename in os.listdir(kline_dir):
                if filename.endswith('.csv') and filename != 'kline_log.csv':
                    # 提取日期
                    date_str = filename.replace('.csv', '')
                    if start_date and date_str < start_date:
                        continue
                    if end_date and date_str > end_date:
                        continue
                    files.append(date_str)
            
            # 按日期排序
            files.sort()
            
            all_data = []
            for date_str in files:
                data = self.get_kline_data_by_symbol_and_date(symbol, date_str)
                all_data.extend(data)
            
            logger.info(f"获取到 {symbol} 的K线数据，共 {len(all_data)} 条记录")
            return all_data
            
        except Exception as e:
            logger.error(f"获取K线数据失败 {symbol}: {e}")
            return []
    
    def get_latest_stock_list(self) -> List[Dict[str, Any]]:
        """
        获取最新的股票列表
        
        Returns:
            List[Dict]: 股票列表数据
        """
        try:
            # 获取最新的stock_list文件
            stock_list_dir = os.path.join(self.csv_path, 'stock_list')
            if not os.path.exists(stock_list_dir):
                return []
            
            # 按修改时间排序，获取最新文件
            files = []
            for filename in os.listdir(stock_list_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(stock_list_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    files.append((mtime, filepath))
            
            if not files:
                return []
            
            # 获取最新文件
            latest_file = max(files, key=lambda x: x[0])[1]
            
            data = []
            with open(latest_file, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从最新文件 {os.path.basename(latest_file)} 读取了 {len(data)} 条股票列表")
            return data
            
        except Exception as e:
            logger.error(f"读取最新股票列表失败: {e}")
            return []
    
    def get_kline_data_by_date(self, date_str: str = None) -> List[Dict[str, Any]]:
        """
        根据日期获取K线数据
        
        Args:
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            
        Returns:
            List[Dict]: K线数据列表
        """
        try:
            if date_str is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            filepath = self.get_kline_filepath_by_date(date_str)
            
            if not os.path.exists(filepath):
                logger.warning(f"K线数据文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条K线数据")
            return data
            
        except Exception as e:
            logger.error(f"读取K线数据失败: {e}")
            return []
    
    def get_financial_statement_filepath(self, symbol: str, statement_type: str) -> str:
        """
        获取财务报表文件路径
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            
        Returns:
            str: 文件路径
        """
        # 确保目录存在
        statements_dir = os.path.join(self.csv_path, 'financial_statements')
        os.makedirs(statements_dir, exist_ok=True)
        
        # 构建文件名
        filename = f"{symbol}_{statement_type}.csv"
        return os.path.join(statements_dir, filename)
    
    def save_financial_statement(self, symbol: str, statement_type: str, statement_data: List[Dict[str, Any]]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            statement_data: 财务报表数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            if not statement_data:
                logger.warning(f"没有{symbol}的{statement_type}报表数据需要保存")
                return False
            
            filepath = self.get_financial_statement_filepath(symbol, statement_type)
            
            # 检查文件是否存在
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = list(statement_data[0].keys())
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerows(statement_data)
            
            logger.info(f"成功保存 {len(statement_data)} 条{statement_type}报表数据到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存财务报表失败 {symbol} {statement_type}: {e}")
            return False
    
    def get_financial_statement_log_filepath(self) -> str:
        """获取财务报表日志文件路径"""
        log_dir = os.path.join(self.csv_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'financial_statements_log.csv')
    
    def save_financial_statement_log(self, log_data: Dict[str, Any]) -> bool:
        """
        保存财务报表处理日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            bool: 是否成功
        """
        try:
            filepath = self.get_financial_statement_log_filepath()
            
            # 检查文件是否存在
            file_exists = os.path.exists(filepath)
            
            # 获取字段名
            fieldnames = ['symbol', 'statement_type', 'report_date', 'timestamp']
            
            with open(filepath, 'a', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据
                writer.writerow(log_data)
            
            return True
            
        except Exception as e:
            logger.error(f"保存财务报表日志失败: {e}")
            return False
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            filepath = self.get_financial_statement_log_filepath()
            
            if not os.path.exists(filepath):
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            return data
            
        except Exception as e:
            logger.error(f"读取财务报表日志失败: {e}")
            return []
    
    def get_financial_statement_data(self, symbol: str, statement_type: str) -> List[Dict[str, Any]]:
        """
        获取指定股票的财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            filepath = self.get_financial_statement_filepath(symbol, statement_type)
            
            if not os.path.exists(filepath):
                logger.warning(f"财务报表文件不存在: {filepath}")
                return []
            
            data = []
            with open(filepath, 'r', encoding=self.encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(dict(row))
            
            logger.info(f"从 {filepath} 读取了 {len(data)} 条{statement_type}报表数据")
            return data
            
        except Exception as e:
            logger.error(f"读取财务报表数据失败: {e}")
            return []
    
    def get_all_financial_statements(self, symbol: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取股票的所有财务报表数据
        
        Args:
            symbol: 证券代码
            
        Returns:
            Dict[str, List[Dict]]]: 包含三张报表数据的字典
        """
        statements = {}
        statement_types = ['income', 'balance', 'cash']
        
        for stmt_type in statement_types:
            data = self.get_financial_statement_data(symbol, stmt_type)
            if data:
                statements[stmt_type] = data
        
        return statements