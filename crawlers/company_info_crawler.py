import json
from crawlers.base_crawler import BaseCrawler
from engine.logger import logger

class CompanyInfoCrawler(BaseCrawler):
    """公司基本信息爬虫"""
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.base_url = self.config['base_url']

    def _fetch_company_info(self, symbol):
        """获取公司信息"""
        url = (
            f"{self.base_url}/stock/f10/compinfo.json"
            f"?symbol={symbol}&page=1&size=4&_={self.get_timestamp()}"
        )
        
        response = self.make_request(url)
        data = response.json()
        
        compinfo = data.get('tqCompInfo', {})
        if not compinfo:
            return None
        
        return {
            'compcode': symbol,
            'compname': compinfo.get('compname', ''),
            'engname': compinfo.get('engname', ''),
            'founddate': compinfo.get('founddate', ''),
            'regcapital': compinfo.get('regcapital', ''),
            'chairman': compinfo.get('chairman', ''),
            'manager': compinfo.get('manager', ''),
            'leconstant': compinfo.get('leconstant', ''),
            'accfirm': compinfo.get('accfirm', ''),
            'regaddr': compinfo.get('regaddr', ''),
            'officeaddr': compinfo.get('officeaddr', ''),
            'compintro': compinfo.get('compintro', '').replace('"', ' '),
            'bizscope': compinfo.get('bizscope', '').replace('"', ' '),
            'majorbiz': compinfo.get('majorbiz', '').replace('"', ' '),
            'compsname': compinfo.get('compsname', ''),
            'region': compinfo.get('region', '')
        }

    def crawl_company_info(self):
        """爬取公司基本信息"""
        self.logger.info("开始爬取公司基本信息...")
        
        stock_symbols = self.data_repo.get_stock_symbols()
        total = len(stock_symbols)
        
        for i, symbol in enumerate(stock_symbols, 1):
            self.logger.info(f"处理第{i}/{total}支股票: {symbol}")
            
            try:
                company_data = self._fetch_company_info(symbol)
                if company_data:
                    self.data_repo.save_company_info(company_data)
                    self.logger.info(f"公司信息保存成功: {symbol} {company_data.get('compsname', '')}")
            except Exception as e:
                self.logger.error(f"获取公司信息失败 {symbol}: {e}")
            
            self.delay()
        
        self.logger.info("公司基本信息爬取完成")