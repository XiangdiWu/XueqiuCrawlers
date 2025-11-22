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
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.logger import get_logger
from todo.auto_cookie import get_auto_cookie_generator

logger = get_logger(__name__)


class XueqiuAuth:
    """雪球认证管理器"""
    
    def __init__(self):
        self.cookie_file = "config/xueqiu_cookies.json"
        self.session = None
        self.session_created_time = None
        self.session_max_age = 3600  # 1小时后重新创建session
    
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
            # 使用自动Cookie生成器
            generator = get_auto_cookie_generator()
            cookies = generator.generate_fresh_cookies()
            
            if cookies:
                logger.info("自动生成Cookie成功")
                return cookies
            else:
                logger.error("自动生成Cookie失败")
                return None
                
        except Exception as e:
            logger.error(f"生成Cookie失败: {e}")
            return None
    
    def get_auth_status(self):
        """获取认证状态"""
        cookies = self.get_cookies()
        
        if not cookies:
            return {
                'status': 'no_cookies',
                'message': '无Cookie',
                'is_logged_in': False,
                'user_id': None
            }
        
        # 检查用户ID
        user_id = cookies.get('u', '0')
        
        if user_id == '0':
            return {
                'status': 'guest_mode',
                'message': '游客状态',
                'is_logged_in': False,
                'user_id': '0'
            }
        else:
            return {
                'status': 'logged_in',
                'message': f'已登录 (用户ID: {user_id})',
                'is_logged_in': True,
                'user_id': user_id
            }
    
    def get_session(self):
        """获取带有认证Cookie的会话 - 支持会话过期管理"""
        import requests
        import time
        
        current_time = time.time()
        
        # 检查是否需要重新创建session
        if (self.session is None or 
            self.session_created_time is None or 
            current_time - self.session_created_time > self.session_max_age):
            
            # 清理旧session
            if self.session is not None:
                try:
                    self.session.close()
                    logger.debug("关闭旧session")
                except:
                    pass
            
            # 创建新session
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
            
            self.session_created_time = current_time
            logger.info("创建新的认证session")
        
        return self.session
    
    def cleanup_session(self):
        """清理session资源"""
        if self.session is not None:
            try:
                self.session.close()
                logger.info("session已清理")
            except:
                pass
            finally:
                self.session = None
                self.session_created_time = None
    

    
    def test_auth(self):
        """测试认证状态"""
        print("🧪 测试认证状态")
        print("=" * 30)
        
        status_info = self.get_auth_status()
        
        print(f"📊 认证状态: {status_info['message']}")
        print(f"🔑 登录状态: {'已登录' if status_info['is_logged_in'] else '未登录'}")
        
        if status_info['user_id']:
            print(f"👤 用户ID: {status_info['user_id']}")
        
        # 获取Cookie详情
        cookies = self.get_cookies()
        if cookies:
            print(f"🍪 Cookie数量: {len(cookies)}")
            
            # 显示关键Cookie
            key_cookies = ['u', 's', 'xq_a_token', 'xq_id_token', 'acw_sc__v2']
            for key in key_cookies:
                status = "✅" if key in cookies else "❌"
                value = cookies.get(key, 'N/A')
                display_value = str(value)[:20] + "..." if len(str(value)) > 20 else value
                print(f"   {status} {key}: {display_value}")
        
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
    """设置认证 - 重定向到get_cookie.py"""
    print("🔐 Cookie设置")
    print("=" * 30)
    print("请运行以下命令获取Cookie:")
    print("   python get_cookie.py")
    print()
    print("该命令将提供详细的Cookie获取引导")
    return False


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
    parser.add_argument('--status', action='store_true', help='查看认证状态')
    
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
    elif args.status:
        auth = get_auth()
        status = auth.get_auth_status()
        print(f"认证状态: {status['message']}")
        print(f"登录状态: {'已登录' if status['is_logged_in'] else '未登录'}")
        if status['user_id']:
            print(f"用户ID: {status['user_id']}")
    else:
        # 默认测试
        test_auth()