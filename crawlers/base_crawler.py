"""
基础爬虫类
"""
import time
import requests
from utils.logger import logger
from config.settings import Config
from utils.cookie_manager import CookieManager
from utils.manual_cookie import ManualCookieManager


class BaseCrawler:
    """基础爬虫类"""
    
    def __init__(self, data_repository=None):
        self.config = Config.XUEQIU_CONFIG
        self.crawler_config = Config.CRAWLER_CONFIG
        self.session = requests.Session()
        self.session.headers.update(self.config['headers'])
        self.logger = logger
        self.data_repo = data_repository
        
        # 设置Cookie - 优先使用手动配置，其次尝试自动获取
        cookies = ManualCookieManager.load_cookies()
        
        if ManualCookieManager.validate_cookies(cookies):
            self.session.cookies.update(cookies)
            user_id = cookies.get('u', '0')
            if user_id == '0':
                self.logger.info("使用手动配置的游客Cookie")
            else:
                self.logger.info(f"使用手动配置的登录Cookie (用户ID: {user_id})")
        else:
            # 尝试从Chrome自动获取
            auto_cookies = CookieManager.get_chrome_cookies()
            if auto_cookies:
                self.session.cookies.update(auto_cookies)
                self.logger.info("成功加载Chrome自动获取的Cookie")
            else:
                self.logger.warning("未能获取任何Cookie，使用默认游客Cookie")
                default_cookies = ManualCookieManager.get_default_cookies()
                self.session.cookies.update(default_cookies)
    
    def make_request(self, url, max_retries=None):
        """
        发送HTTP请求
        
        Args:
            url (str): 请求URL
            max_retries (int): 最大重试次数
            
        Returns:
            requests.Response: 响应对象
        """
        if max_retries is None:
            max_retries = self.crawler_config['max_retries']
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"请求URL: {url}, 尝试次数: {attempt + 1}")
                response = self.session.get(
                    url, 
                    timeout=self.crawler_config['timeout']
                )
                
                if response.status_code == requests.codes.ok:
                    return response
                else:
                    self.logger.warning(f"请求失败，状态码: {response.status_code}")
                    
            except requests.RequestException as e:
                self.logger.error(f"请求异常: {e}")
            
            # 重试前等待
            if attempt < max_retries - 1:
                time.sleep(self.crawler_config['request_delay'])
        
        raise Exception(f"请求失败，已重试{max_retries}次")
    
    def get_timestamp(self):
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)
    
    def delay(self):
        """请求延迟"""
        time.sleep(self.crawler_config['request_delay'])