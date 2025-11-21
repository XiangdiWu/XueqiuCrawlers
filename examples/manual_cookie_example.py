"""
手动Cookie配置示例
演示如何使用手动配置的Cookie进行雪球数据爬取
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.base_crawler import BaseCrawler
from utils.manual_cookie import ManualCookieManager
from utils.logger import get_logger

logger = get_logger(__name__)


def example_manual_cookie_usage():
    """手动Cookie使用示例"""
    print("=== 手动Cookie使用示例 ===")
    
    # 检查Cookie状态
    ManualCookieManager.check_cookie_status()
    
    # 创建爬虫实例
    crawler = BaseCrawler()
    
    # 测试请求
    test_urls = [
        "https://xueqiu.com/statuses/hot_timelineV3.json?count=10",
        "https://xueqiu.com/stock/search.json?code=000001",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- 测试请求 {i} ---")
        try:
            response = crawler.make_request(url)
            print(f"✅ 请求成功: {response.status_code}")
            
            # 尝试解析JSON
            try:
                data = response.json()
                print(f"📊 数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"📋 数据键: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"📋 数据长度: {len(data)}")
            except:
                print(f"📄 响应长度: {len(response.text)} 字符")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")


def example_cookie_comparison():
    """Cookie对比示例"""
    print("\n=== Cookie对比示例 ===")
    
    # 加载不同类型的Cookie
    manual_cookies = ManualCookieManager.load_cookies()
    default_cookies = ManualCookieManager.get_default_cookies()
    
    print("手动配置的Cookie:")
    for key, value in manual_cookies.items():
        print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")
    
    print("\n默认Cookie:")
    for key, value in default_cookies.items():
        print(f"  {key}: {value}")
    
    # 验证Cookie
    manual_valid = ManualCookieManager.validate_cookies(manual_cookies)
    default_valid = ManualCookieManager.validate_cookies(default_cookies)
    
    print(f"\n手动Cookie有效性: {'✅' if manual_valid else '❌'}")
    print(f"默认Cookie有效性: {'✅' if default_valid else '❌'}")


def main():
    """主函数"""
    try:
        example_cookie_comparison()
        example_manual_cookie_usage()
        print("\n🎉 手动Cookie示例完成！")
        
    except Exception as e:
        logger.error(f"示例执行失败: {e}")
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    main()