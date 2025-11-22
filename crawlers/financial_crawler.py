"""
财务数据爬虫
"""
import json
from crawlers.base_crawler import BaseCrawler
from engine.logger import logger


class FinancialCrawler(BaseCrawler):
    """财务数据爬虫"""
    
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.base_url = self.config['base_url']
    
    def crawl_financial_data(self):
        """爬取主要财务数据"""
        self.logger.info("开始爬取财务数据...")
        
        stock_symbols = self.data_repo.get_unprocessed_finmain_stocks()
        total = len(stock_symbols)
        
        for i, symbol in enumerate(stock_symbols, 1):
            self.logger.info(f"处理第{i}/{total}支股票财务数据: {symbol}")
            
            try:
                financial_data_list = self._fetch_financial_data(symbol)
                for financial_data in financial_data_list:
                    self.data_repo.save_finmain_data(financial_data)
                
                self.logger.info(f"财务数据保存成功: {symbol}")
            except Exception as e:
                self.logger.error(f"获取财务数据失败 {symbol}: {e}")
            
            self.delay()
        
        self.logger.info("财务数据爬取完成")
    
    def _fetch_financial_data(self, symbol):
        """获取财务数据"""
        url = (
            f"{self.base_url}/stock/f10/finmainindex.json"
            f"?symbol={symbol}&page=1&size=100&_={self.get_timestamp()}"
        )
        
        response = self.make_request(url)
        # 将null替换为0，防止解析错误
        text = response.text.replace('null', '0')
        data = json.loads(text)
        
        financial_list = []
        for item in data.get('list', []):
            # 添加股票代码
            item['compcode'] = symbol
            
            # 确保所有字段都有值，空值设为0
            financial_data = {
                'compcode': symbol,
                'reportdate': item.get('reportdate', ''),
                'basiceps': item.get('basiceps', 0),
                'epsdiluted': item.get('epsdiluted', 0),
                'epsweighted': item.get('epsweighted', 0),
                'naps': item.get('naps', 0),
                'opercashpershare': item.get('opercashpershare', 0),
                'peropecashpershare': item.get('peropecashpershare', 0),
                'netassgrowrate': item.get('netassgrowrate', 0),
                'dilutedroe': item.get('dilutedroe', 0),
                'weightedroe': item.get('weightedroe', 0),
                'mainbusincgrowrate': item.get('mainbusincgrowrate', 0),
                'netincgrowrate': item.get('netincgrowrate', 0),
                'totassgrowrate': item.get('totassgrowrate', 0),
                'salegrossprofitrto': item.get('salegrossprofitrto', 0),
                'mainbusiincome': item.get('mainbusiincome', 0),
                'mainbusiprofit': item.get('mainbusiprofit', 0),
                'totprofit': item.get('totprofit', 0),
                'netprofit': item.get('netprofit', 0),
                'totalassets': item.get('totalassets', 0),
                'totalliab': item.get('totalliab', 0),
                'totsharequi': item.get('totsharequi', 0),
                'operrevenue': item.get('operrevenue', 0),
                'invnetcashflow': item.get('invnetcashflow', 0),
                'finnetcflow': item.get('finnetcflow', 0),
                'chgexchgchgs': item.get('chgexchgchgs', 0),
                'cashnetr': item.get('cashnetr', 0),
                'cashequfinbal': item.get('cashequfinbal', 0)
            }
            financial_list.append(financial_data)
        
        return financial_list