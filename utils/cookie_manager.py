"""
Cookie管理模块
"""
import os
import sqlite3
import platform
from utils.logger import get_logger

logger = get_logger(__name__)


class CookieManager:
    """Cookie管理器"""
    
    @staticmethod
    def get_chrome_cookies(host='.xueqiu.com'):
        """
        从Chrome浏览器获取Cookie
        
        Args:
            host (str): 目标域名，默认为雪球
            
        Returns:
            dict: Cookie字典
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                return CookieManager._get_windows_chrome_cookies(host)
            elif system == "Darwin":  # macOS
                return CookieManager._get_mac_chrome_cookies(host)
            elif system == "Linux":
                return CookieManager._get_linux_chrome_cookies(host)
            else:
                logger.warning(f"不支持的操作系统: {system}")
                return {}
                
        except Exception as e:
            logger.error(f"获取Chrome Cookie失败: {e}")
            return {}
    
    @staticmethod
    def _get_windows_chrome_cookies(host):
        """Windows系统获取Chrome Cookie"""
        try:
            import win32crypt
            cookie_path = os.environ['LOCALAPPDATA'] + r"\\Google\\Chrome\\User Data\\Default\\Cookies"
            sql = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key = ?"
            
            with sqlite3.connect(cookie_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (host,))
                cookies = {}
                
                for host_key, name, encrypted_value in cursor.fetchall():
                    try:
                        # 解密Cookie值
                        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value)[1].decode()
                        cookies[name] = decrypted_value
                    except Exception as e:
                        logger.debug(f"解密Cookie失败: {name}, 错误: {e}")
                        continue
                
                return cookies
                
        except ImportError:
            logger.warning("Windows系统需要安装pywin32库来获取Chrome Cookie")
            return {}
        except Exception as e:
            logger.error(f"Windows系统获取Cookie失败: {e}")
            return {}
    
    @staticmethod
    def _get_mac_chrome_cookies(host):
        """macOS系统获取Chrome Cookie"""
        try:
            import keyring
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import PBKDF2
            
            # 动态检测Chrome配置文件路径
            chrome_base = os.path.expanduser("~/Library/Application Support/Google/Chrome")
            cookie_path = CookieManager._find_chrome_cookie_file(chrome_base)
            
            if not cookie_path or not os.path.exists(cookie_path):
                logger.error("Chrome Cookie文件不存在")
                return {}
                
            sql = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key = ?"
            
            # 尝试以只读模式连接数据库，避免锁定问题
            conn = None
            try:
                conn = sqlite3.connect(f"file:{cookie_path}?mode=ro", uri=True)
                cursor = conn.cursor()
                cursor.execute(sql, (host,))
                cookies = {}
                
                for host_key, name, encrypted_value in cursor.fetchall():
                    try:
                        # macOS Chrome Cookie解密
                        decrypted_value = CookieManager._decrypt_mac_cookie(encrypted_value)
                        if decrypted_value:
                            cookies[name] = decrypted_value
                    except Exception as e:
                        logger.debug(f"解密Cookie失败: {name}, 错误: {e}")
                        continue
                
                return cookies
                
            finally:
                if conn:
                    conn.close()
                
        except ImportError:
            logger.warning("macOS系统需要安装keyring和pycryptodome库来获取Chrome Cookie")
            return {}
        except Exception as e:
            logger.error(f"macOS系统获取Cookie失败: {e}")
            return {}
    
    @staticmethod
    def _find_chrome_cookie_file(chrome_base):
        """查找Chrome Cookie文件"""
        # 常见的配置文件名称，按优先级排序
        profiles = ["Default", "Profile 1", "Profile 2", "Profile 3"]
        
        for profile in profiles:
            cookie_path = os.path.join(chrome_base, profile, "Cookies")
            if os.path.exists(cookie_path):
                return cookie_path
        
        # 如果常见配置文件都不存在，尝试查找任何包含Cookies的目录
        try:
            for item in os.listdir(chrome_base):
                item_path = os.path.join(chrome_base, item)
                if os.path.isdir(item_path):
                    cookie_path = os.path.join(item_path, "Cookies")
                    if os.path.exists(cookie_path):
                        return cookie_path
        except (OSError, PermissionError):
            pass
        
        return None
    
    @staticmethod
    def _get_linux_chrome_cookies(host):
        """Linux系统获取Chrome Cookie"""
        try:
            cookie_path = os.path.expanduser("~/.config/google-chrome/Default/Cookies")
            sql = "SELECT host_key, name, value FROM cookies WHERE host_key = ?"
            
            with sqlite3.connect(cookie_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (host,))
                cookies = {}
                
                for host_key, name, value in cursor.fetchall():
                    cookies[name] = value
                
                return cookies
                
        except Exception as e:
            logger.error(f"Linux系统获取Cookie失败: {e}")
            return {}
    
    @staticmethod
    def _decrypt_mac_cookie(encrypted_value):
        """解密macOS Chrome Cookie"""
        try:
            import keyring
            from Crypto.Cipher import AES
            from Crypto.Protocol.KDF import PBKDF2
            
            # 获取Chrome安全密钥
            safe_storage = keyring.get_password('Chrome Safe Storage', 'Chrome')
            if not safe_storage:
                return None
            
            # 使用PBKDF2派生密钥
            salt = b'saltysalt'
            key = PBKDF2(safe_storage, salt, 16, 1003)
            
            # 解密数据
            iv = b' ' * 16
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 移除v10前缀
            if encrypted_value.startswith(b'v10'):
                encrypted_value = encrypted_value[3:]
            
            # 填充处理
            decrypted = cipher.decrypt(encrypted_value)
            # 移除padding
            padding = decrypted[-1]
            if isinstance(padding, str):
                padding = ord(padding)
            decrypted = decrypted[:-padding]
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            logger.debug(f"macOS Cookie解密失败: {e}")
            return None
    
    @staticmethod
    def get_default_cookies():
        """获取默认Cookie（当无法从浏览器获取时）"""
        return {
            'u': '0',  # 用户ID
            'bid': '1',  # 浏览器ID
            's': 'ae8c8c8f8f8f8f8f8f8f8f8f8f8f8f8f'  # 会话ID
        }