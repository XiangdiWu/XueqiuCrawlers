#!/usr/bin/env python3
"""
Cookie诊断工具
帮助诊断和解决Cookie相关问题
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.logger import get_logger
from engine.xueqiu_auth import get_auth
from todo.auto_cookie import get_auto_cookie_generator

logger = get_logger(__name__)


class CookieDiagnostic:
    """Cookie诊断工具"""
    
    def __init__(self):
        self.auth = get_auth()
        self.auto_generator = get_auto_cookie_generator()
    
    def run_full_diagnosis(self):
        """运行完整诊断"""
        print("🔍 雪球Cookie完整诊断")
        print("=" * 50)
        
        # 1. 检查文件存在性
        self._check_files()
        
        # 2. 检查Node.js环境
        self._check_nodejs()
        
        # 3. 检查网络连接
        self._check_network()
        
        # 4. 测试手动Cookie
        self._test_manual_cookies()
        
        # 5. 测试自动生成
        self._test_auto_generation()
        
        # 6. 测试认证状态
        self._test_authentication()
        
        # 7. 提供解决方案
        self._provide_solutions()
    
    def _check_files(self):
        """检查相关文件"""
        print("\n📁 检查相关文件")
        print("-" * 30)
        
        files_to_check = [
            "config/xueqiu_cookies.json",
            "cookie_input.txt",
            "engine/xueqiu_deobfuscator.js",
            "engine/auto_cookie.py"
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"✅ {file_path} (大小: {size} bytes, 修改时间: {mtime})")
                
                # 检查Cookie文件内容
                if file_path.endswith('.json'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        cookies = data.get('cookies', {})
                        print(f"   🍪 包含 {len(cookies)} 个Cookie")
                        
                        # 检查关键Cookie
                        key_cookies = ['u', 's', 'acw_sc__v2']
                        for key in key_cookies:
                            status = "✅" if key in cookies else "❌"
                            print(f"     {status} {key}")
                    except Exception as e:
                        print(f"   ❌ 文件格式错误: {e}")
            else:
                print(f"❌ {file_path} (文件不存在)")
    
    def _check_nodejs(self):
        """检查Node.js环境"""
        print("\n🟢 检查Node.js环境")
        print("-" * 30)
        
        try:
            import subprocess
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Node.js版本: {version}")
                
                # 测试npm
                try:
                    npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                    if npm_result.returncode == 0:
                        npm_version = npm_result.stdout.strip()
                        print(f"✅ npm版本: {npm_version}")
                    else:
                        print("⚠️  npm不可用")
                except:
                    print("⚠️  npm不可用")
            else:
                print(f"❌ Node.js执行失败: {result.stderr}")
        except FileNotFoundError:
            print("❌ Node.js未安装")
        except Exception as e:
            print(f"❌ Node.js检查异常: {e}")
    
    def _check_network(self):
        """检查网络连接"""
        print("\n🌐 检查网络连接")
        print("-" * 30)
        
        urls_to_test = [
            "https://xueqiu.com",
            "https://stock.xueqiu.com",
            "https://xueqiu.com/v5/stock/quote.json?symbol=SZ000001"
        ]
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        for url in urls_to_test:
            try:
                start_time = time.time()
                response = session.get(url, timeout=10)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ {url} (状态: {response.status_code}, 耗时: {elapsed:.2f}s)")
                    
                    # 检查响应内容
                    if '雪球' in response.text or 'xueqiu' in response.text.lower():
                        print("   📄 内容验证通过")
                    else:
                        print("   ⚠️  内容可能异常")
                else:
                    print(f"❌ {url} (状态: {response.status_code})")
                    
            except requests.Timeout:
                print(f"⏰ {url} (超时)")
            except Exception as e:
                print(f"❌ {url} (异常: {e})")
    
    def _test_manual_cookies(self):
        """测试手动Cookie"""
        print("\n🖊️  测试手动Cookie")
        print("-" * 30)
        
        # 检查是否有手动Cookie
        cookie_file = "cookie_input.txt"
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content and not content.startswith('#'):
                    print(f"📝 发现手动Cookie: {content[:50]}...")
                    
                    # 解析并测试
                    cookies = {}
                    for item in content.split(';'):
                        if '=' in item:
                            key, value = item.strip().split('=', 1)
                            cookies[key] = value
                    
                    if self._test_cookies_validity(cookies, "手动Cookie"):
                        return True
                    
            except Exception as e:
                print(f"❌ 读取手动Cookie失败: {e}")
        else:
            print("❌ 未找到手动Cookie文件")
        
        return False
    
    def _test_auto_generation(self):
        """测试自动生成"""
        print("\n🤖 测试自动生成")
        print("-" * 30)
        
        try:
            # 测试自动Cookie生成器
            generator = get_auto_cookie_generator()
            
            # 启用调试模式
            generator.debug_mode = True
            
            cookies = generator.generate_fresh_cookies()
            
            if cookies:
                print(f"✅ 自动生成成功，获得 {len(cookies)} 个Cookie")
                
                # 显示关键Cookie
                key_cookies = ['u', 's', 'acw_sc__v2']
                for key in key_cookies:
                    status = "✅" if key in cookies else "❌"
                    value = cookies.get(key, 'N/A')
                    display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
                    print(f"   {status} {key}: {display_value}")
                
                # 测试有效性
                if self._test_cookies_validity(cookies, "自动生成Cookie"):
                    return True
            else:
                print("❌ 自动生成失败")
                
        except Exception as e:
            print(f"❌ 自动生成异常: {e}")
        
        return False
    
    def _test_authentication(self):
        """测试认证状态"""
        print("\n🔐 测试认证状态")
        print("-" * 30)
        
        try:
            status_info = self.auth.get_auth_status()
            print(f"📊 认证状态: {status_info['message']}")
            print(f"🔑 登录状态: {'已登录' if status_info['is_logged_in'] else '未登录'}")
            
            if status_info['user_id']:
                print(f"👤 用户ID: {status_info['user_id']}")
            
            # 测试session
            session = self.auth.get_session()
            response = session.get('https://xueqiu.com', timeout=10)
            
            if response.status_code == 200:
                print("✅ Session访问成功")
                return True
            else:
                print(f"❌ Session访问失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 认证测试异常: {e}")
        
        return False
    
    def _test_cookies_validity(self, cookies, cookie_type):
        """测试Cookie有效性"""
        try:
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
                print(f"✅ {cookie_type}验证通过")
                return True
            else:
                print(f"❌ {cookie_type}验证失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {cookie_type}验证异常: {e}")
            return False
    
    def _provide_solutions(self):
        """提供解决方案"""
        print("\n💡 解决方案建议")
        print("-" * 30)
        
        print("🔧 常见问题解决方案：")
        print()
        
        print("1️⃣  Node.js相关问题：")
        print("   • 安装Node.js: https://nodejs.org/")
        print("   • 检查环境变量PATH")
        print("   • 重启终端/IDE")
        print()
        
        print("2️⃣  Cookie失效问题：")
        print("   • 重新获取Cookie: python get_cookie.py")
        print("   • 确保雪球账号已登录")
        print("   • 检查Cookie格式是否正确")
        print()
        
        print("3️⃣  网络连接问题：")
        print("   • 检查网络连接")
        print("   • 尝试使用VPN")
        print("   • 检查防火墙设置")
        print()
        
        print("4️⃣  反爬虫问题：")
        print("   • 降低请求频率")
        print("   • 使用不同的User-Agent")
        print("   • 清除浏览器缓存后重新获取Cookie")
        print()
        
        print("5️⃣  调试模式：")
        print("   • 启用调试: AutoCookieGenerator(debug_mode=True)")
        print("   • 查看日志文件: logs/")
        print("   • 检查临时文件是否清理")


def main():
    """主函数"""
    diagnostic = CookieDiagnostic()
    diagnostic.run_full_diagnosis()


if __name__ == '__main__':
    main()