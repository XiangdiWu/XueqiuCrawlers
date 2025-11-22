"""
爬虫服务层
"""
from crawlers.stock_info_crawler import StockInfoCrawler
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
        self.stock_crawler = StockInfoCrawler(self.data_repo)
        self.financial_crawler = FinancialCrawler(self.data_repo)
        self.kline_crawler = KlineCrawler(self.data_repo)
        self.stock_list_crawler = StockListCrawler(self.data_repo)
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
        self.stock_crawler = StockInfoCrawler(self.data_repo)
        self.financial_crawler = FinancialCrawler(self.data_repo)
        self.kline_crawler = KlineCrawler(self.data_repo)
        self.stock_list_crawler = StockListCrawler(self.data_repo)
        
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
    
    def run_company_info_crawl(self, symbols=None):
        """只爬取公司信息"""
        self.logger.info("爬取公司信息...")
        result = self.stock_crawler.crawl_company_info(symbols)
        self.logger.info(f"公司信息爬取完成 - 成功: {result['success']}, 失败: {result['error']}")
        return result
    
    def crawl_company_info_by_symbol(self, symbol: str):
        """按证券代码爬取公司信息"""
        self.logger.info(f"爬取公司信息: {symbol}")
        return self.stock_crawler.crawl_company_info_by_code(symbol)
    
    def get_company_info_by_symbol(self, symbol: str):
        """获取指定公司的信息"""
        return self.data_repo.get_company_info_by_symbol(symbol)
    
    def update_company_info_by_symbol(self, symbol: str):
        """更新指定公司的信息"""
        self.logger.info(f"更新公司信息: {symbol}")
        return self.stock_crawler.update_company_info_by_symbol(symbol)
    
    def crawl_company_info_batch(self, symbols: list, batch_size: int = 50):
        """批量爬取公司信息"""
        self.logger.info(f"批量爬取公司信息，共{len(symbols)}支股票")
        return self.stock_crawler.crawl_company_info_batch(symbols, batch_size)
    
    def export_company_info_to_csv(self, output_path=None, symbols=None):
        """导出公司信息到CSV"""
        return self.stock_crawler.export_company_info_to_csv(output_path, symbols)
    
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
    
    # 股票列表相关方法
    def run_stock_list_crawl_by_date(self, date_str: str = None, 
                                     max_pages: int = 10, page_size: int = 100,
                                     stock_type: str = '11,12'):
        """按日期爬取股票列表"""
        self.logger.info(f"爬取股票列表，日期: {date_str or '今天'}")
        result = self.stock_list_crawler.crawl_stock_list_by_date(
            date_str, max_pages, page_size, stock_type
        )
        if result:
            self.logger.info("股票列表爬取完成")
        else:
            self.logger.error("股票列表爬取失败")
        return result
    
    def get_stock_list_by_date(self, date_str: str = None):
        """获取指定日期的股票列表"""
        return self.stock_list_crawler.get_stock_list_by_date(date_str)
    
    def get_stock_symbols_by_date(self, date_str: str = None):
        """获取指定日期的股票代码列表"""
        return self.stock_list_crawler.get_stock_symbols_by_date(date_str)
    
    def get_stock_by_symbol(self, symbol: str, date_str: str = None):
        """获取指定股票在指定日期的数据"""
        return self.stock_list_crawler.get_stock_by_symbol(symbol, date_str)
    
    def update_stock_list(self, date_str: str = None):
        """更新指定日期的股票列表"""
        return self.stock_list_crawler.update_stock_list(date_str)
    
    def get_crawl_dates(self):
        """获取已爬取的日期列表"""
        return self.stock_list_crawler.get_crawl_dates()
    
    def create_simplified_stock_list(self, date_str: str = None):
        """从stock_info创建简化的stock_list"""
        self.logger.info(f"创建简化股票列表，日期: {date_str or '今天'}")
        return self.stock_list_crawler.create_simplified_stock_list(date_str)
    
    def run_stock_info_crawl(self):
        """爬取股票信息到stock_info目录"""
        self.logger.info("爬取股票信息到stock_info...")
        self.stock_crawler.crawl_stock_list()
        self.logger.info("股票信息爬取完成")