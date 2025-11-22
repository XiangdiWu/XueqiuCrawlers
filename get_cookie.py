#!/usr/bin/env python3
"""
获取雪球Cookie

1、cookie_input.txt中手动配置Cookie字符串
2、读取、处理并保存Cookie
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.logger import get_logger

logger = get_logger(__name__)


def process_cookie_file():
    """处理Cookie文件"""
    print("🍪 处理Cookie文件")
    print("=" * 30)
    
    cookie_file = "cookie_input.txt"
    
    if not os.path.exists(cookie_file):
        print(f"❌ 未找到文件: {cookie_file}")
        # 创建文件
        open(cookie_file, 'w', encoding='utf-8')
        print(f"📝 已创建文件: {cookie_file}")
        print("请先编辑该文件，在文件内粘贴Cookie字符串")
        # 询问是否需要手动获取Cookie的引导，并提供引导
        return False
    
    # 读取文件内容
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找Cookie字符串（跳过注释行）
        cookie_string = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                cookie_string = line
                break
        
        if not cookie_string:
            print("❌ 未找到Cookie字符串")
            print(f"请编辑 {cookie_file} 文件，在非注释行添加Cookie字符串")
            return False
        
        print(f"📝 读取到Cookie字符串: {cookie_string[:50]}...")
        
        # 解析Cookie
        cookies = {}
        try:
            for item in cookie_string.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookies[key] = value
        except Exception as e:
            print(f"❌ Cookie解析失败: {e}")
            return False
        
        if not cookies:
            print("❌ 未解析到有效的Cookie")
            return False
        
        print(f"✅ 解析成功，共 {len(cookies)} 个Cookie")
        
        # 显示关键Cookie
        key_cookies = ['u', 's', 'xq_a_token', 'xq_id_token', 'acw_sc__v2']
        print("\n📊 关键Cookie状态:")
        for key in key_cookies:
            status = "✅" if key in cookies else "❌"
            value = cookies.get(key, 'N/A')
            display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
            print(f"   {status} {key}: {display_value}")
        
        # 检查用户ID
        user_id = cookies.get('u', '0')
        if user_id == '0':
            print("\n⚠️  警告: 用户ID为0，可能仍是游客状态")
        else:
            print(f"\n✅ 检测到登录用户ID: {user_id}")
        
        # 验证并保存
        if validate_cookies(cookies):
            print("✅ Cookie验证通过")
        else:
            print("⚠️  Cookie验证失败，但仍将保存")
        
        if save_cookies(cookies):
            print("✅ Cookie保存成功")
            print("\n🎉 处理完成！现在可以使用爬虫了")
            
            # 清空输入文件
            try:
                with open(cookie_file, 'w', encoding='utf-8') as f:
                    f.write("# Cookie已处理，此文件可清空\n")
                print(f"🧹 已清空输入文件: {cookie_file}")
            except:
                pass
            
            return True
        else:
            print("❌ Cookie保存失败")
            return False
            
    except Exception as e:
        print(f"❌ 处理Cookie文件失败: {e}")
        return False


def validate_cookies(cookies):
    """验证Cookie有效性"""
    try:
        import requests
        
        if not cookies:
            return False
        
        # 检查关键Cookie
        required = ['u', 's']
        for key in required:
            if key not in cookies:
                logger.warning(f"缺少关键Cookie: {key}")
                return False
        
        # 测试访问
        session = requests.Session()
        session.cookies.update(cookies)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://xueqiu.com/'
        }
        
        response = session.get('https://xueqiu.com', headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("Cookie验证通过")
            return True
        else:
            logger.warning(f"Cookie验证失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Cookie验证异常: {e}")
        return False


def save_cookies(cookies):
    """保存Cookie"""
    try:
        cookie_file = "config/xueqiu_cookies.json"
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
        
        data = {
            'cookies': cookies,
            'timestamp': time.time(),
            'generated_at': datetime.now().isoformat(),
            'import_method': 'file_import'
        }
        
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Cookie已保存到: {cookie_file}")
        print(f"💾 Cookie已保存到: {cookie_file}")
        return True
    except Exception as e:
        logger.error(f"保存Cookie失败: {e}")
        print(f"❌ 保存Cookie失败: {e}")
        return False


if __name__ == '__main__':
    process_cookie_file()