"""
爬虫服务层
"""
from crawlers.stock_info_crawler import StockCrawler
from crawlers.financial_crawler import FinancialCrawler
from crawlers.kline_crawler import KlineCrawler
from engine.logger import logger
from engine.database import DataRepository
from config.settings import Config


class CrawlerService:
    """爬虫服务类"""
    
    def __init__(self, storage_type: str = None):
        # 确定存储类型
        if storage_type is None:
            storage_type = Config.STORAGE_CONFIG.get('type', 'database')
        
        self.storage_type = storage_type
        self.data_repo = DataRepository(storage_type)
        
        # 初始化爬虫，传入数据仓库
        self.stock_crawler = StockCrawler(self.data_repo)
        self.financial_crawler = FinancialCrawler(self.data_repo)
        self.kline_crawler = KlineCrawler(self.data_repo)
        self.logger = logger
        
        self.logger.info(f"初始化爬虫服务，存储类型: {storage_type}")
    
    def get_storage_info(self):
        """获取存储信息"""
        return self.data_repo.get_storage_info()
    
    def switch_storage(self, new_storage_type: str):
        """切换存储类型"""
        if new_storage_type not in ['database', 'csv']:
            raise ValueError("存储类型必须是 'database' 或 'csv'")
        
        self.logger.info(f"切换存储类型从 {self.storage_type} 到 {new_storage_type}")
        self.storage_type = new_storage_type
        self.data_repo = DataRepository(new_storage_type)
        
        # 重新初始化爬虫
        self.stock_crawler = StockCrawler(self.data_repo)
        self.financial_crawler = FinancialCrawler(self.data_repo)
        self.kline_crawler = KlineCrawler(self.data_repo)
        
        self.logger.info(f"存储类型切换完成: {new_storage_type}")
    
    def create_backup(self):
        """创建备份"""
        return self.data_repo.create_backup()
    
    def run_full_crawl(self):
        """执行完整爬取流程"""
        try:
            self.logger.info("开始执行完整爬取流程...")
            
            # 1. 爬取股票列表和实时行情
            self.logger.info("步骤1: 爬取股票列表和实时行情")
            self.stock_crawler.crawl_stock_list()
            
            # 2. 爬取公司基本信息
            self.logger.info("步骤2: 爬取公司基本信息")
            self.stock_crawler.crawl_company_info()
            
            # 3. 爬取财务数据
            self.logger.info("步骤3: 爬取财务数据")
            self.financial_crawler.crawl_financial_data()
            
            # 4. 爬取K线数据
            self.logger.info("步骤4: 爬取K线数据")
            self.kline_crawler.crawl_kline_data()
            
            self.logger.info("完整爬取流程执行完成！")
            
        except Exception as e:
            self.logger.error(f"爬取流程执行失败: {e}")
            raise
    
    def run_stock_list_crawl(self):
        """只爬取股票列表"""
        self.logger.info("爬取股票列表...")
        self.stock_crawler.crawl_stock_list()
        self.logger.info("股票列表爬取完成")
    
    def run_company_info_crawl(self):
        """只爬取公司信息"""
        self.logger.info("爬取公司信息...")
        self.stock_crawler.crawl_company_info()
        self.logger.info("公司信息爬取完成")
    
    def run_financial_crawl(self):
        """只爬取财务数据"""
        self.logger.info("爬取财务数据...")
        self.financial_crawler.crawl_financial_data()
        self.logger.info("财务数据爬取完成")
    
    def run_kline_crawl(self):
        """只爬取K线数据"""
        self.logger.info("爬取K线数据...")
        self.kline_crawler.crawl_kline_data()
        self.logger.info("K线数据爬取完成")