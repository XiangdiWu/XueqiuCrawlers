"""
股票数据爬虫
"""
import json
from crawlers.base_crawler import BaseCrawler
from engine.logger import logger


class StockInfoCrawler(BaseCrawler):
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
            "?page={page}&size={page_size}"
            "&order=asc&exchange=CN&stockType={stock_type}"
            "&column=symbol%2Cname%2Ccurrent%2Cchg%2Cpercent%2Clast_close"
            "%2Copen%2Chigh%2Clow%2Cvolume%2Camount%2Cmarket_capital"
            "%2Cpe_ttm%2Chigh52w%2Clow52w%2Chasexist&orderBy=symbol&_={timestamp}"
        )
        
        # 获取第一页确定总页数
        first_page_url = url_template.format(
            page=1, 
            page_size=self.crawler_config['page_size'],
            stock_type=stock_type,
            timestamp=self.get_timestamp()
        )
        response = self.make_request(first_page_url)
        
        # 处理响应，将null替换为0防止解析错误
        response_text = response.text.replace('null', '0')
        data = response.json()
        
        total_count = int(data.get('count', 0))
        max_page = total_count // self.crawler_config['page_size'] + 1
        
        self.logger.info(f"{stock_type}共{total_count}支股票，{max_page}页")
        
        # 爬取所有页面
        stock_count = 0
        for page in range(1, max_page + 1):
            url = url_template.format(
                page=page, 
                page_size=self.crawler_config['page_size'],
                stock_type=stock_type,
                timestamp=self.get_timestamp()
            )
            response = self.make_request(url)
            
            # 处理响应，将null替换为0防止解析错误
            response_text = response.text.replace('null', '0')
            data = response.json()
            
            # 处理股票数据 - 使用原始数据结构（数组形式）
            stock_list = data.get('data', [])
            for stock_item in stock_list:
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
            'current': stock_item[2] if len(stock_item) > 2 else 0,
            'percent': stock_item[4] if len(stock_item) > 4 else 0,
            'high52w': stock_item[13] if len(stock_item) > 13 else 0,
            'low52w': stock_item[14] if len(stock_item) > 14 else 0,
            'marketcapital': stock_item[11] if len(stock_item) > 11 else 0,
            'amount': stock_item[10] if len(stock_item) > 10 else 0,
            'volume': stock_item[9] if len(stock_item) > 9 else 0,
            'pe_ttm': stock_item[12] if len(stock_item) > 12 else 0
        }