"""
手动Cookie配置模块
允许用户手动配置雪球网站的Cookie，避免自动获取浏览器Cookie的隐私风险
"""
import json
import os
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ManualCookieManager:
    """手动Cookie管理器"""
    
    # Cookie配置文件路径
    COOKIE_CONFIG_PATH = "config/cookies.json"
    
    # 雪球常用的Cookie名称和说明
    COOKIE_GUIDE = {
        "u": {
            "name": "用户ID",
            "description": "雪球用户唯一标识，登录后会有具体数值",
            "example": "12345678",
            "required": True
        },
        "s": {
            "name": "会话ID", 
            "description": "用户会话标识，登录后生成",
            "example": "ae8c8c8f8f8f8f8f8f8f8f8f8f8f8f8f",
            "required": True
        },
        "bid": {
            "name": "浏览器ID",
            "description": "浏览器唯一标识",
            "example": "1",
            "required": False
        },
        "_ga": {
            "name": "Google Analytics",
            "description": "Google分析Cookie",
            "example": "GA1.2.1234567890.1234567890",
            "required": False
        },
        "_gid": {
            "name": "Google Analytics ID",
            "description": "Google分析会话ID",
            "example": "GA1.2.987654321.987654321",
            "required": False
        }
    }
    
    @classmethod
    def load_cookies(cls) -> Dict[str, str]:
        """
        从配置文件加载Cookie
        
        Returns:
            Dict[str, str]: Cookie字典
        """
        try:
            if os.path.exists(cls.COOKIE_CONFIG_PATH):
                with open(cls.COOKIE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    logger.info(f"成功加载手动配置的Cookie，共{len(cookies)}个")
                    return cookies
            else:
                logger.warning("Cookie配置文件不存在，使用默认Cookie")
                return cls.get_default_cookies()
                
        except Exception as e:
            logger.error(f"加载Cookie配置失败: {e}")
            return cls.get_default_cookies()
    
    @classmethod
    def save_cookies(cls, cookies: Dict[str, str]) -> bool:
        """
        保存Cookie到配置文件
        
        Args:
            cookies (Dict[str, str]): Cookie字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(cls.COOKIE_CONFIG_PATH), exist_ok=True)
            
            with open(cls.COOKIE_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            logger.info(f"成功保存{len(cookies)}个Cookie到配置文件")
            return True
            
        except Exception as e:
            logger.error(f"保存Cookie配置失败: {e}")
            return False
    
    @classmethod
    def get_default_cookies(cls) -> Dict[str, str]:
        """
        获取默认Cookie（游客模式）
        
        Returns:
            Dict[str, str]: 默认Cookie字典
        """
        return {
            'u': '0',  # 游客用户ID
            'bid': '1',  # 默认浏览器ID
            's': 'ae8c8c8f8f8f8f8f8f8f8f8f8f8f8f8f'  # 默认会话ID
        }
    
    @classmethod
    def validate_cookies(cls, cookies: Dict[str, str]) -> bool:
        """
        验证Cookie是否有效
        
        Args:
            cookies (Dict[str, str]): Cookie字典
            
        Returns:
            bool: 是否有效
        """
        required_cookies = ['u', 's']
        
        for cookie_name in required_cookies:
            if cookie_name not in cookies or not cookies[cookie_name]:
                logger.warning(f"缺少必需的Cookie: {cookie_name}")
                return False
        
        # 检查用户ID是否为游客（0表示未登录）
        if cookies.get('u') == '0':
            logger.info("使用游客模式Cookie，功能可能受限")
        
        return True
    
    @classmethod
    def show_cookie_guide(cls) -> None:
        """显示Cookie配置指南"""
        print("=" * 60)
        print("🍪 雪球Cookie手动配置指南")
        print("=" * 60)
        print()
        print("📋 如何获取雪球Cookie：")
        print("1. 在Chrome浏览器中登录雪球网站 (https://xueqiu.com)")
        print("2. 按F12打开开发者工具")
        print("3. 点击 Network（网络）标签")
        print("4. 刷新页面，找到任意一个xueqiu.com的请求")
        print("5. 在请求头中找到 'Cookie' 字段")
        print("6. 复制Cookie值，提取需要的部分")
        print()
        print("🔑 必需的Cookie项：")
        print()
        
        for cookie_key, info in cls.COOKIE_GUIDE.items():
            required_mark = "✅" if info["required"] else "⚪"
            print(f"{required_mark} **{cookie_key}** - {info['name']}")
            print(f"   说明: {info['description']}")
            print(f"   示例: {info['example']}")
            print()
        
        print("⚠️  注意事项：")
        print("- Cookie包含敏感信息，请勿分享给他人")
        print("- Cookie会过期，需要定期更新")
        print("- 建议使用测试账号，避免影响主账号")
        print("- 保存Cookie前请确保格式正确")
        print()
        print("=" * 60)
    
    @classmethod
    def interactive_setup(cls) -> bool:
        """
        交互式Cookie配置
        
        Returns:
            bool: 是否配置成功
        """
        cls.show_cookie_guide()
        
        print("\n🔧 开始配置Cookie（输入 'skip' 跳过该项）：")
        
        cookies = {}
        
        for cookie_key, info in cls.COOKIE_GUIDE.items():
            while True:
                prompt = f"请输入 {cookie_key} ({info['name']}): "
                user_input = input(prompt).strip()
                
                if user_input.lower() == 'skip':
                    if info['required']:
                        print(f"⚠️  {cookie_key} 是必需的，不能跳过")
                        continue
                    else:
                        break
                
                if user_input:
                    cookies[cookie_key] = user_input
                    break
                else:
                    if info['required']:
                        print(f"❌ {cookie_key} 是必需的，请输入有效值")
                    else:
                        break
        
        # 验证Cookie
        if cls.validate_cookies(cookies):
            # 保存Cookie
            if cls.save_cookies(cookies):
                print("✅ Cookie配置保存成功！")
                print(f"📁 配置文件位置: {cls.COOKIE_CONFIG_PATH}")
                return True
            else:
                print("❌ Cookie配置保存失败")
                return False
        else:
            print("❌ Cookie验证失败，请检查必需项")
            return False
    
    @classmethod
    def check_cookie_status(cls) -> None:
        """检查当前Cookie状态"""
        print("=" * 50)
        print("🔍 Cookie状态检查")
        print("=" * 50)
        
        if os.path.exists(cls.COOKIE_CONFIG_PATH):
            cookies = cls.load_cookies()
            print(f"📁 配置文件: {cls.COOKIE_CONFIG_PATH}")
            print(f"🍪 Cookie数量: {len(cookies)}")
            
            if cls.validate_cookies(cookies):
                print("✅ Cookie配置有效")
                
                # 检查登录状态
                user_id = cookies.get('u', '0')
                if user_id == '0':
                    print("👤 当前状态: 游客模式")
                    print("⚠️  功能受限，建议配置登录Cookie")
                else:
                    print(f"👤 当前状态: 已登录 (用户ID: {user_id})")
                    print("✅ 可以访问完整功能")
            else:
                print("❌ Cookie配置无效")
        else:
            print("❌ Cookie配置文件不存在")
            print("💡 请运行以下命令进行配置:")
            print("   python -c \"from utils.manual_cookie import ManualCookieManager; ManualCookieManager.interactive_setup()\"")
        
        print("=" * 50)


# 为了向后兼容，提供简单的接口函数
def get_manual_cookies() -> Dict[str, str]:
    """获取手动配置的Cookie"""
    return ManualCookieManager.load_cookies()


def setup_cookies_interactive() -> bool:
    """交互式配置Cookie"""
    return ManualCookieManager.interactive_setup()


def check_cookies_status() -> None:
    """检查Cookie状态"""
    ManualCookieManager.check_cookie_status()