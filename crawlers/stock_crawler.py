"""
股票数据爬虫
"""
import json
from crawlers.base_crawler import BaseCrawler
from utils.logger import logger


class StockCrawler(BaseCrawler):
    """股票数据爬虫"""
    
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.base_url = self.config['base_url']
    
    def crawl_stock_list(self):
        """爬取股票列表和实时行情"""
        self.logger.info("开始爬取股票列表...")
        
        # 股票类型：上海A股、深圳A股
        stock_types = ['sha', 'sza']
        
        for stock_type in stock_types:
            self.logger.info(f"爬取{stock_type}股票...")
            self._crawl_stock_by_type(stock_type)
        
        self.logger.info("股票列表爬取完成")
    
    def _crawl_stock_by_type(self, stock_type):
        """按股票类型爬取数据"""
        url_template = (
            f"{self.base_url}/stock/quote_order.json"
            "?page={{page}}&size={self.crawler_config['page_size']}"
            "&order=asc&exchange=CN&stockType={stock_type}"
            "&column=symbol%2Cname%2Ccurrent%2Cchg%2Cpercent%2Clast_close"
            "%2Copen%2Chigh%2Clow%2Cvolume%2Camount%2Cmarket_capital"
            "%2Cpe_ttm%2Chigh52w%2Clow52w%2Chasexist&orderBy=symbol&_={{timestamp}}"
        )
        
        # 获取第一页确定总页数
        first_page_url = url_template.format(page=1, timestamp=self.get_timestamp())
        response = self.make_request(first_page_url)
        data = response.json()
        
        total_count = int(data.get('count', 0))
        max_page = total_count // self.crawler_config['page_size'] + 1
        
        self.logger.info(f"{stock_type}共{total_count}支股票，{max_page}页")
        
        # 爬取所有页面
        stock_count = 0
        for page in range(1, max_page + 1):
            url = url_template.format(page=page, timestamp=self.get_timestamp())
            response = self.make_request(url)
            data = response.json()
            
            # 处理股票数据
            for stock_item in data.get('data', []):
                stock_data = self._parse_stock_data(stock_item, stock_type)
                try:
                    self.data_repo.save_stock_basic_info(stock_data)
                    stock_count += 1
                    self.logger.debug(f"保存股票: {stock_data['symbol']} {stock_data['name']}")
                except Exception as e:
                    self.logger.error(f"保存股票数据失败: {e}")
            
            self.logger.info(f"{stock_type}第{page}页完成，累计{stock_count}支")
            self.delay()
    
    def _parse_stock_data(self, stock_item, stock_type):
        """解析股票数据"""
        return {
            'symbol': stock_item[0],
            'code': stock_item[0],
            'name': stock_item[1],
            'current': stock_item[2] or 0,
            'percent': stock_item[4] or 0,
            'high52w': stock_item[13] or 0,
            'low52w': stock_item[14] or 0,
            'marketcapital': stock_item[11] or 0,
            'amount': stock_item[10] or 0,
            'volume': stock_item[9] or 0,
            'pe_ttm': stock_item[12] or 0
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