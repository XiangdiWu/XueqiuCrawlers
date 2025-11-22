"""
基础爬虫类
"""
import time
import requests
from engine.logger import logger
from engine.settings import Config
from engine.xueqiu_auth import get_authenticated_session


class BaseCrawler:
    """基础爬虫类"""
    
    def __init__(self, data_repository=None):
        self.config = Config.XUEQIU_CONFIG
        self.crawler_config = Config.CRAWLER_CONFIG
        self.logger = logger
        self.data_repo = data_repository
        
        # 使用新的认证系统获取会话
        self.session = get_authenticated_session()
        
        # 更新请求头
        self.session.headers.update(self.config['headers'])
        
        # 检查认证状态
        cookies = self.session.cookies.get_dict()
        user_id = cookies.get('u', '0')
        if user_id == '0':
            self.logger.info("使用游客模式Cookie")
        else:
            self.logger.info(f"使用登录Cookie (用户ID: {user_id})")
        
        self.logger.info(f"当前Cookie数量: {len(cookies)}")
        
        # 检查关键反爬Cookie
        anti_crawler_cookies = ['acw_sc__v2', 'ACW-TC', 'ACWSCVI']
        for cookie in anti_crawler_cookies:
            if cookie in cookies:
                self.logger.info(f"反爬Cookie {cookie}: {cookies[cookie][:20]}...")
            else:
                self.logger.warning(f"缺少反爬Cookie: {cookie}")
    
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
    
    def _get_xueqiu_anti_crawler_cookies(self):
        """获取雪球反爬虫Cookie"""
        try:
            from utils.xueqiu_cookie_generator import XueqiuCookieGenerator
            
            generator = XueqiuCookieGenerator()
            cookies = generator.get_anti_crawler_cookies()
            
            if cookies:
                # 将获取到的Cookie设置到session
                for key, value in cookies.items():
                    if key in ['ACW-TC', 'ACWSCVI']:
                        self.session.cookies.set(key, value, domain='.xueqiu.com')
                
                self.logger.info("成功获取并设置雪球反爬虫Cookie")
            else:
                self.logger.warning("未能获取雪球反爬虫Cookie")
            
        except Exception as e:
            self.logger.warning(f"获取雪球反爬虫Cookie失败: {e}")
            # 继续执行，使用默认Cookie