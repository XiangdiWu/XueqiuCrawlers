"""
K线数据爬虫
"""
import json
from crawlers.base_crawler import BaseCrawler
from utils.logger import logger


class KlineCrawler(BaseCrawler):
    """K线数据爬虫"""
    
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.stock_base_url = self.config['stock_base_url']
    
    def crawl_kline_data(self):
        """爬取K线数据"""
        self.logger.info("开始爬取K线数据...")
        
        stock_symbols = self.data_repo.get_unprocessed_kline_stocks()
        total = len(stock_symbols)
        
        for i, symbol in enumerate(stock_symbols, 1):
            self.logger.info(f"处理第{i}/{total}支股票K线数据: {symbol}")
            
            try:
                kline_data_list = self._fetch_kline_data(symbol)
                
                # 批量保存K线数据
                for kline_data in kline_data_list:
                    self.data_repo.save_kline_data(kline_data)
                
                # 记录处理日志
                self.data_repo.log_kline_processing(symbol)
                self.logger.info(f"K线数据保存成功: {symbol}")
                
            except Exception as e:
                self.logger.error(f"获取K线数据失败 {symbol}: {e}")
            
            self.delay()
        
        self.logger.info("K线数据爬取完成")
    
    def _fetch_kline_data(self, symbol):
        """获取K线数据"""
        url = (
            f"{self.stock_base_url}/v5/stock/chart/kline.json"
            f"?symbol={symbol}&begin=600000000000&end={self.get_timestamp()}"
            "&period=day&type=before&indicator=kline"
        )
        
        response = self.make_request(url)
        data = response.json()
        
        # 检查错误
        if data.get('error_code') != 0:
            error_desc = data.get('error_description', '未知错误')
            raise Exception(f"API错误: {error_desc}")
        
        kline_data = data.get('data', {})
        items = kline_data.get('item', [])
        
        kline_list = []
        for item in items:
            kline_data_item = {
                'symbol': symbol,
                'timestamp': item[0] / 1000,  # 转换为秒
                'volume': item[1],
                'open': round(item[2], 2),
                'high': round(item[3], 2),
                'low': round(item[4], 2),
                'close': round(item[5], 2),
                'chg': round(item[6], 2),
                'percent': round(item[7], 2),
                'turnoverrate': round(item[8], 2),
                'period': 'day',    # 日线
                'type': 'before'    # 前复权
            }
            kline_list.append(kline_data_item)
        
        return kline_list