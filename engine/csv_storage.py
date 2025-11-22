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
        # 创建子目录
        subdirs = ['stocks', 'companies', 'financial', 'kline']
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
        # 根据表名确定子目录
        if table_name in ['stock_list', 'stock_info']:
            subdir = 'stocks'
        elif table_name == 'company_profile':
            subdir = 'companies'
        elif table_name in ['financial_data', 'financial_summary']:
            subdir = 'financial'
        elif table_name == 'kline_data':
            subdir = 'kline'
        else:
            subdir = ''
        
        if subdir:
            return os.path.join(self.csv_path, subdir, filename)
        return os.path.join(self.csv_path, filename)
    
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
                    mode: str = 'a', suffix: str = '') -> bool:
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的数据
            table_name: 表名
            mode: 写入模式 ('a'追加, 'w'覆盖)
            suffix: 文件名后缀
        
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
    
    def read_from_csv(self, table_name: str, suffix: str = '') -> List[Dict[str, Any]]:
        """
        从CSV文件读取数据
        
        Args:
            table_name: 表名
            suffix: 文件名后缀
        
        Returns:
            List[Dict]: 数据列表
        """
        try:
            filepath = self._get_filepath(table_name, suffix)
            
            if not os.path.exists(filepath):
                logger.warning(f"CSV文件不存在: {filepath}")
                return []
            
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