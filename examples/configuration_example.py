"""
配置使用示例
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from config.settings import Config
from utils.logger import get_logger


def example_database_config():
    """数据库配置示例"""
    print("=== 数据库配置示例 ===")
    
    # 获取数据库配置
    db_config = Config.DATABASE_CONFIG
    print("数据库配置:")
    for key, value in db_config.items():
        if key == 'password':
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    # 修改配置（运行时）
    print("\n修改数据库配置...")
    original_host = db_config['host']
    db_config['host'] = 'new_host'
    print(f"主机修改为: {db_config['host']}")
    
    # 恢复原始配置
    db_config['host'] = original_host
    print(f"恢复原始主机: {db_config['host']}")


def example_xueqiu_config():
    """雪球配置示例"""
    print("=== 雪球配置示例 ===")
    
    # 获取雪球配置
    xueqiu_config = Config.XUEQIU_CONFIG
    print("雪球API配置:")
    print(f"  基础URL: {xueqiu_config['base_url']}")
    print(f"  股票基础URL: {xueqiu_config['stock_base_url']}")
    
    # 显示请求头
    print("\n请求头配置:")
    for key, value in xueqiu_config['headers'].items():
        print(f"  {key}: {value}")


def example_crawler_config():
    """爬虫配置示例"""
    print("=== 爬虫配置示例 ===")
    
    # 获取爬虫配置
    crawler_config = Config.CRAWLER_CONFIG
    print("爬虫配置:")
    for key, value in crawler_config.items():
        print(f"  {key}: {value}")
    
    # 修改配置
    print("\n修改爬虫配置...")
    original_delay = crawler_config['request_delay']
    crawler_config['request_delay'] = 1.0
    print(f"请求延迟修改为: {crawler_config['request_delay']} 秒")
    
    # 恢复原始配置
    crawler_config['request_delay'] = original_delay
    print(f"恢复原始延迟: {crawler_config['request_delay']} 秒")


def example_log_config():
    """日志配置示例"""
    print("=== 日志配置示例 ===")
    
    # 获取日志配置
    log_config = Config.LOG_CONFIG
    print("日志配置:")
    for key, value in log_config.items():
        print(f"  {key}: {value}")


def example_custom_config():
    """自定义配置示例"""
    print("=== 自定义配置示例 ===")
    
    # 创建自定义配置类
    class CustomConfig:
        # API配置
        API_CONFIG = {
            'timeout': 30,
            'max_retries': 3,
            'api_key': 'your_api_key_here',
            'base_url': 'https://api.example.com'
        }
        
        # 业务配置
        BUSINESS_CONFIG = {
            'max_stocks_per_batch': 100,
            'enable_real_time': True,
            'data_retention_days': 365
        }
    
    # 使用自定义配置
    custom_config = CustomConfig()
    
    print("自定义API配置:")
    for key, value in custom_config.API_CONFIG.items():
        if key == 'api_key':
            print(f"  {key}: {'*' * 10}")
        else:
            print(f"  {key}: {value}")
    
    print("\n自定义业务配置:")
    for key, value in custom_config.BUSINESS_CONFIG.items():
        print(f"  {key}: {value}")


def example_environment_config():
    """环境配置示例"""
    print("=== 环境配置示例 ===")
    
    import os
    
    # 从环境变量读取配置
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3311')
    api_timeout = os.getenv('API_TIMEOUT', '30')
    
    print("环境变量配置:")
    print(f"  DB_HOST: {db_host}")
    print(f"  DB_PORT: {db_port}")
    print(f"  API_TIMEOUT: {api_timeout}")
    
    # 设置环境变量（示例）
    os.environ['CUSTOM_CONFIG'] = 'custom_value'
    print(f"\n设置环境变量: CUSTOM_CONFIG = {os.getenv('CUSTOM_CONFIG')}")


def example_config_validation():
    """配置验证示例"""
    print("=== 配置验证示例 ===")
    
    def validate_database_config(config):
        """验证数据库配置"""
        required_fields = ['host', 'user', 'password', 'db', 'port']
        errors = []
        
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
            elif not config[field]:
                errors.append(f"字段不能为空: {field}")
        
        # 验证端口号
        if 'port' in config:
            try:
                port = int(config['port'])
                if port < 1 or port > 65535:
                    errors.append(f"端口号无效: {port}")
            except ValueError:
                errors.append(f"端口号必须是数字: {config['port']}")
        
        return errors
    
    # 验证当前配置
    db_config = Config.DATABASE_CONFIG
    errors = validate_database_config(db_config)
    
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("数据库配置验证通过！")
    
    # 测试无效配置
    invalid_config = {
        'host': '',
        'user': 'test',
        'port': 'invalid_port'
    }
    
    errors = validate_database_config(invalid_config)
    print("\n测试无效配置:")
    for error in errors:
        print(f"  - {error}")


def main():
    """主函数"""
    logger = get_logger('example_config')
    
    try:
        # 示例1: 数据库配置
        example_database_config()
        
        # 示例2: 雪球配置
        example_xueqiu_config()
        
        # 示例3: 爬虫配置
        example_crawler_config()
        
        # 示例4: 日志配置
        example_log_config()
        
        # 示例5: 自定义配置
        example_custom_config()
        
        # 示例6: 环境配置
        example_environment_config()
        
        # 示例7: 配置验证
        example_config_validation()
        
        print("配置使用示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"错误: {e}")


if __name__ == '__main__':
    main()