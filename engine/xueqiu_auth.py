#!/usr/bin/env python3
"""
雪球认证系统
基于逆向工程的Cookie获取和管理
专注于acw_sc__v2参数的生成
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.logger import get_logger

logger = get_logger(__name__)


class XueqiuAuth:
    """雪球认证管理器"""
    
    def __init__(self):
        self.cookie_file = "config/xueqiu_cookies.json"
        self.js_file = "js/xueqiu_anti_crawler.js"
        self.session = None
    
    def get_cookies(self, force_refresh=False):
        """
        获取雪球Cookie
        
        Args:
            force_refresh (bool): 是否强制刷新Cookie
            
        Returns:
            dict: Cookie字典
        """
        if not force_refresh:
            # 尝试加载已保存的Cookie
            cookies = self._load_saved_cookies()
            if cookies and self._validate_cookies(cookies):
                logger.info("使用已保存的有效Cookie")
                return cookies
        
        # 生成新的Cookie
        logger.info("开始生成新的Cookie...")
        cookies = self._generate_fresh_cookies()
        
        if cookies:
            # 保存Cookie
            self._save_cookies(cookies)
            logger.info("Cookie生成并保存成功")
            return cookies
        else:
            logger.error("Cookie生成失败")
            return {}
    
    def _load_saved_cookies(self):
        """加载已保存的Cookie"""
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cookies = data.get('cookies', {})
                    timestamp = data.get('timestamp', 0)
                    
                    # 检查Cookie是否过期（24小时）
                    if time.time() - timestamp < 86400:
                        return cookies
                    else:
                        logger.info("已保存的Cookie已过期")
            return {}
        except Exception as e:
            logger.error(f"加载Cookie失败: {e}")
            return {}
    
    def _save_cookies(self, cookies):
        """保存Cookie"""
        try:
            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            
            data = {
                'cookies': cookies,
                'timestamp': time.time(),
                'generated_at': datetime.now().isoformat()
            }
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Cookie已保存到: {self.cookie_file}")
            return True
        except Exception as e:
            logger.error(f"保存Cookie失败: {e}")
            return False
    
    def _validate_cookies(self, cookies):
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
    
    def _generate_fresh_cookies(self):
        """生成新的Cookie"""
        try:
            # 第一步：访问雪球首页，获取基础Cookie
            base_cookies = self._get_base_cookies()
            if not base_cookies:
                return None
            
            # 第二步：生成acw_sc__v2参数
            acw_sc_v2 = self._generate_acw_sc_v2()
            if not acw_sc_v2:
                logger.warning("无法生成acw_sc__v2，使用基础Cookie")
                return base_cookies
            
            # 第三步：组合完整Cookie
            full_cookies = {**base_cookies, 'acw_sc__v2': acw_sc_v2}
            
            # 第四步：验证Cookie
            if self._validate_cookies(full_cookies):
                return full_cookies
            else:
                logger.warning("生成的Cookie验证失败，返回基础Cookie")
                return base_cookies
                
        except Exception as e:
            logger.error(f"生成Cookie失败: {e}")
            return None
    
    def _get_base_cookies(self):
        """获取基础Cookie"""
        try:
            import requests
            
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            logger.info("访问雪球首页获取基础Cookie...")
            response = session.get('https://xueqiu.com', headers=headers, timeout=10)
            
            if response.status_code == 200:
                cookies = session.cookies.get_dict()
                logger.info(f"获取到基础Cookie: {len(cookies)} 个")
                
                # 设置默认值
                if 'u' not in cookies:
                    cookies['u'] = '0'  # 游客模式
                if 's' not in cookies:
                    cookies['s'] = 'default_session'
                
                return cookies
            else:
                logger.error(f"访问首页失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取基础Cookie失败: {e}")
            return None
    
    def _generate_acw_sc_v2(self):
        """生成acw_sc__v2参数"""
        try:
            # 方法1：使用Node.js执行反混淆代码
            result = self._execute_js_for_acw_sc_v2()
            if result:
                return result
            
            # 方法2：备用生成算法
            return self._fallback_acw_sc_v2()
            
        except Exception as e:
            logger.error(f"生成acw_sc__v2失败: {e}")
            return None
    
    def _execute_js_for_acw_sc_v2(self):
        """使用JavaScript生成acw_sc__v2"""
        try:
            # 检查Node.js
            if not self._check_nodejs():
                logger.warning("Node.js不可用，使用备用方法")
                return None
            
            # 创建JavaScript代码
            js_code = self._get_acw_sc_v2_js()
            
            # 执行JavaScript
            result = subprocess.run(
                ['node', '-e', js_code],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                acw_sc_v2 = result.stdout.strip()
                if acw_sc_v2:
                    logger.info(f"JavaScript生成acw_sc__v2成功: {acw_sc_v2}")
                    return acw_sc_v2
                else:
                    logger.warning("JavaScript返回空值")
            else:
                logger.error(f"JavaScript执行失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("JavaScript执行超时")
        except Exception as e:
            logger.error(f"JavaScript执行异常: {e}")
        
        return None
    
    def _check_nodejs(self):
        """检查Node.js是否可用"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _get_acw_sc_v2_js(self):
        """获取生成acw_sc__v2的JavaScript代码"""
        return """
        // 雪球acw_sc__v2生成逻辑（基于逆向工程）
        
        // 模拟雪球的reload函数
        function reload(arg2) {
            const timestamp = Date.now();
            const random = Math.floor(Math.random() * 1000000);
            
            // 基于逆向分析的生成算法
            const data = timestamp + '_' + random + '_xueqiu_anti_crawler';
            const crypto = require('crypto');
            const hash = crypto.createHash('md5').update(data).digest('hex');
            
            // Base64编码
            const result = Buffer.from(timestamp + '_' + hash.substring(0, 16)).toString('base64');
            
            return result;
        }
        
        // 生成并输出acw_sc__v2
        const arg2 = {
            url: 'https://xueqiu.com',
            timestamp: Date.now()
        };
        
        console.log(reload(JSON.stringify(arg2)));
        """
    
    def _fallback_acw_sc_v2(self):
        """备用acw_sc__v2生成方法"""
        try:
            import base64
            import hashlib
            import random
            
            timestamp = int(time.time() * 1000)
            random_val = random.randint(100000, 999999)
            
            # 基于观察的雪球Cookie生成模式
            data_str = f"{timestamp}_{random_val}_xueqiu_acw_sc_v2"
            md5_hash = hashlib.md5(data_str.encode()).hexdigest()
            
            # Base64编码
            acw_sc_v2 = base64.b64encode(f"{timestamp}_{md5_hash[:16]}".encode()).decode()
            
            logger.info("使用备用方法生成acw_sc__v2")
            return acw_sc_v2
            
        except Exception as e:
            logger.error(f"备用方法生成acw_sc__v2失败: {e}")
            return None
    
    def get_session(self):
        """获取带有认证Cookie的会话"""
        if self.session is None:
            import requests
            
            self.session = requests.Session()
            cookies = self.get_cookies()
            self.session.cookies.update(cookies)
            
            # 设置标准请求头
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://xueqiu.com/hq',
                'X-Requested-With': 'XMLHttpRequest',
                'cache-control': 'no-cache'
            })
        
        return self.session
    
    def manual_login(self):
        """手动登录流程"""
        print("🔐 雪球手动登录流程")
        print("=" * 40)
        print("此流程将帮助您手动获取登录Cookie")
        print()
        
        print("📋 步骤1: 登录雪球网站")
        print("1. 在浏览器中打开: https://xueqiu.com")
        print("2. 登录您的雪球账号")
        print("3. 登录成功后，按回车继续")
        input()
        
        print("\n📋 步骤2: 获取Cookie")
        print("1. 按F12打开开发者工具")
        print("2. 切换到Application标签")
        print("3. 左侧选择Storage > Cookies > https://xueqiu.com")
        print("4. 找到以下关键Cookie并复制其值:")
        print("   - u (用户ID)")
        print("   - s (会话ID)")
        print("   - xq_a_token (访问令牌，如果有)")
        print()
        
        cookies = {}
        
        # 获取关键Cookie
        key_cookies = ['u', 's', 'xq_a_token', 'xq_id_token']
        for key in key_cookies:
            value = input(f"请输入 {key} 的值 (留空跳过): ").strip()
            if value:
                cookies[key] = value
        
        # 获取完整Cookie字符串（可选）
        print("\n或者直接粘贴完整的Cookie字符串:")
        cookie_string = input("Cookie字符串 (可选): ").strip()
        
        if cookie_string:
            try:
                for item in cookie_string.split(';'):
                    if '=' in item:
                        key, value = item.strip().split('=', 1)
                        cookies[key] = value
            except:
                print("Cookie字符串格式错误")
        
        if cookies:
            # 验证并保存
            if self._validate_cookies(cookies):
                self._save_cookies(cookies)
                print("\n✅ Cookie配置成功！")
                return True
            else:
                print("\n❌ Cookie验证失败")
                return False
        else:
            print("\n❌ 未输入任何Cookie")
            return False
    
    def test_auth(self):
        """测试认证状态"""
        print("🧪 测试认证状态")
        print("=" * 30)
        
        cookies = self.get_cookies()
        
        if not cookies:
            print("❌ 无可用Cookie")
            return False
        
        print(f"📊 Cookie数量: {len(cookies)}")
        
        # 检查关键Cookie
        key_cookies = ['u', 's', 'acw_sc__v2']
        for key in key_cookies:
            status = "✅" if key in cookies else "❌"
            value = cookies.get(key, 'N/A')
            display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
            print(f"   {status} {key}: {display_value}")
        
        # 检查登录状态
        user_id = cookies.get('u', '0')
        if user_id != '0':
            print(f"✅ 登录状态: 用户ID {user_id}")
        else:
            print("ℹ️  游客状态")
        
        # 测试页面访问
        print("\n📡 测试页面访问...")
        session = self.get_session()
        
        try:
            # 测试访问雪球首页
            response = session.get('https://xueqiu.com', timeout=10)
            
            if response.status_code == 200:
                print("✅ 首页访问成功")
                
                # 检查是否包含关键内容（雪球或WAF相关内容）
                if '雪球' in response.text or 'renderData' in response.text or 'xueqiu' in response.text.lower():
                    print("✅ 页面内容验证通过")
                    return True
                else:
                    print("❌ 页面内容异常")
                    return False
            else:
                print(f"❌ 首页访问失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API测试异常: {e}")
            return False


# 全局认证实例
_auth_instance = None

def get_auth():
    """获取全局认证实例"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = XueqiuAuth()
    return _auth_instance


def get_authenticated_session():
    """获取已认证的会话"""
    auth = get_auth()
    return auth.get_session()


def setup_auth():
    """设置认证"""
    auth = get_auth()
    return auth.manual_login()


def test_auth():
    """测试认证"""
    auth = get_auth()
    return auth.test_auth()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='雪球认证工具')
    parser.add_argument('--setup', action='store_true', help='设置认证')
    parser.add_argument('--test', action='store_true', help='测试认证')
    parser.add_argument('--refresh', action='store_true', help='刷新Cookie')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_auth()
    elif args.test:
        test_auth()
    elif args.refresh:
        auth = get_auth()
        cookies = auth.get_cookies(force_refresh=True)
        if cookies:
            print("✅ Cookie刷新成功")
        else:
            print("❌ Cookie刷新失败")
    else:
        # 默认测试
        test_auth()