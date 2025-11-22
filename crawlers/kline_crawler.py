"""
K线数据爬虫
"""
import json
from crawlers.base_crawler import BaseCrawler
from engine.logger import logger


class KlineCrawler(BaseCrawler):
    """K线数据爬虫"""
    
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.stock_base_url = self.config['stock_base_url']
    
    def crawl_kline_data(self, adjust_type='after'):
        """
        爬取K线数据
        
        Args:
            adjust_type: 复权类型 ('before'前复权, 'after'后复权, 'none'不复权)
        """
        self.logger.info(f"开始爬取K线数据，复权类型: {adjust_type}...")
        
        stock_symbols = self.data_repo.get_unprocessed_kline_stocks()
        total = len(stock_symbols)
        
        for i, symbol in enumerate(stock_symbols, 1):
            self.logger.info(f"处理第{i}/{total}支股票K线数据: {symbol}")
            
            try:
                kline_data_list = self._fetch_kline_data(symbol, adjust_type)
                
                # 批量保存K线数据（按日期存储）
                if kline_data_list:
                    self.data_repo.save_kline_data_batch(kline_data_list)
                
                # 记录处理日志
                self.data_repo.log_kline_processing(symbol)
                self.logger.info(f"K线数据保存成功: {symbol}，共{len(kline_data_list)}条")
                
            except Exception as e:
                self.logger.error(f"获取K线数据失败 {symbol}: {e}")
            
            self.delay()
        
        self.logger.info("K线数据爬取完成")
    
    def crawl_kline_data_after_adjust(self):
        """爬取后复权K线数据（便捷方法）"""
        return self.crawl_kline_data('after')
    
    def crawl_kline_data_before_adjust(self):
        """爬取前复权K线数据（便捷方法）"""
        return self.crawl_kline_data('before')
    
    def crawl_kline_data_no_adjust(self):
        """爬取不复权K线数据（便捷方法）"""
        return self.crawl_kline_data('none')
    
    def _fetch_kline_data(self, symbol, adjust_type='after'):
        """
        获取K线数据
        
        Args:
            symbol: 股票代码
            adjust_type: 复权类型 ('before'前复权, 'after'后复权, 'none'不复权)
            
        Returns:
            List[Dict]: K线数据列表
        """
        url = (
            f"{self.stock_base_url}/v5/stock/chart/kline.json"
            f"?symbol={symbol}&begin=600000000000&end={self.get_timestamp()}"
            f"&period=day&type={adjust_type}&indicator=kline"
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
                'type': adjust_type # 复权类型
            }
            kline_list.append(kline_data_item)
        
        return kline_list