"""
配置文件
"""
import os

class Config:
    # 数据库配置
    DATABASE_CONFIG = {
        'host': 'localhost',
        'user': 'test',
        'password': 'test',
        'db': 'stock',
        'port': 3311,
        'charset': 'utf8mb4'
    }
    
    # 雪球API配置
    XUEQIU_CONFIG = {
        'base_url': 'https://xueqiu.com',
        'stock_base_url': 'https://stock.xueqiu.com',
        'headers': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'xueqiu.com',
            'Referer': 'https://xueqiu.com/hq',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
    }
    
    # 爬虫配置
    CRAWLER_CONFIG = {
        'request_delay': 0.3,  # 请求延迟
        'max_retries': 3,      # 最大重试次数
        'timeout': 30,         # 请求超时时间
        'page_size': 90        # 分页大小
    }
    
    # 日志配置
    LOG_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'filename': 'logs/xueqiu_crawler.log'
    }
    
    # 存储配置
    STORAGE_CONFIG = {
        'type': 'csv',  # 'database' 或 'csv'
        'csv_path': 'data/csv',  # CSV文件存储路径
        'csv_encoding': 'utf-8-sig',  # CSV编码，支持Excel
        'create_backup': True,  # 是否创建备份
        'backup_path': 'data/backup'  # 备份路径
    }