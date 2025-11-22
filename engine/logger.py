"""
日志配置模块
"""
import logging
import os
from config.settings import Config


def setup_logger(name, log_file=None):
    """
    设置日志记录器
    
    Args:
        name (str): 日志记录器名称
        log_file (str): 日志文件路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_CONFIG['level']))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(Config.LOG_CONFIG['format'])
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name=None):
    """
    获取日志记录器
    
    Args:
        name (str): 日志记录器名称，默认使用项目名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    if name is None:
        name = 'xueqiu_crawler'
    
    return setup_logger(name, Config.LOG_CONFIG.get('filename'))


# 创建默认日志记录器
logger = get_logger()