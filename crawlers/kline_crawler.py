"""
K线数据爬虫 - 借鉴recycling/kline.py的鲁棒性设计
"""
import json
import time
import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from crawlers.base_crawler import BaseCrawler
from engine.logger import get_logger

logger = get_logger(__name__)


class KlineCrawler(BaseCrawler):
    """K线数据爬虫 - 具备重试机制和错误处理"""
    
    def __init__(self, data_repository=None, max_retries: int = 3):
        super().__init__(data_repository)
        self.stock_base_url = self.config['stock_base_url']
        self.max_retries = max_retries
        self.processed_count = 0
        self.failed_symbols = []
        
        # 如果传入的是CSVStorage对象，确保正确访问
        if data_repository and hasattr(data_repository, 'csv_path'):
            # 这是一个CSVStorage对象，直接使用
            self.csv_storage = data_repository
        elif hasattr(data_repository, 'csv_storage') and data_repository.csv_storage:
            # 这是一个DataRepository对象，使用其csv_storage属性
            self.csv_storage = data_repository.csv_storage
        else:
            self.csv_storage = None
        
        logger.info("K线爬虫初始化完成")
    
    def crawl_market_daily_data(self, target_date: str = None, adjust_type: str = 'after', max_stocks: Optional[int] = None):
        """
        爬取全市场股票在某一个交易日的数据
        
        Args:
            target_date: 目标日期，格式 'YYYY-MM-DD'，None表示最新交易日
            adjust_type: 复权类型 ('before'前复权, 'after'后复权, 'none'不复权)
            max_stocks: 最大处理股票数量，None表示处理所有
        """
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"开始爬取全市场股票 {target_date} 的日频数据，复权类型: {adjust_type}...")
        
        # 获取所有股票列表
        stock_symbols = self._get_unprocessed_stocks()
        
        if max_stocks:
            stock_symbols = stock_symbols[:max_stocks]
            logger.info(f"限制处理数量: {max_stocks}")
        
        total = len(stock_symbols)
        self.processed_count = 0
        self.failed_symbols = []
        
        if total == 0:
            logger.info("没有找到股票列表")
            return
        
        # 将目标日期转换为时间戳
        target_timestamp = self._date_to_timestamp(target_date)
        next_day_timestamp = target_timestamp + 24 * 60 * 60 * 1000  # 第二天
        
        for i, symbol in enumerate(stock_symbols, 1):
            logger.info(f'第{i}/{total}支，{symbol}-获取{target_date}日频数据中...')
            
            try:
                # 获取指定日期的K线数据
                kline_data_list = self._fetch_single_day_kline_data(symbol, target_timestamp, next_day_timestamp, adjust_type)
                
                if kline_data_list:
                    # 保存单日数据
                    success = self._save_single_day_data(kline_data_list, target_date)
                    if success:
                        self.processed_count += 1
                        logger.info(f"保存成功: {symbol} {target_date} 数据")
                    else:
                        self.failed_symbols.append(symbol)
                        logger.error(f"保存失败: {symbol}")
                else:
                    self.failed_symbols.append(symbol)
                    logger.warning(f"没有获取到数据: {symbol} {target_date}")
                
            except Exception as e:
                self.failed_symbols.append(symbol)
                logger.error(f"获取数据异常 {symbol}: {e}")
            
            # 降低请求频率
            time.sleep(0.3)
        
        # 输出统计信息
        self._log_statistics()
        logger.info(f"全市场股票 {target_date} 日频数据爬取完成")

    def crawl_kline_data(self, adjust_type='after', max_stocks: Optional[int] = None):
        """
        爬取K线数据 - 借鉴重试机制和批量处理
        
        Args:
            adjust_type: 复权类型 ('before'前复权, 'after'后复权, 'none'不复权)
            max_stocks: 最大处理股票数量，None表示处理所有
        """
        logger.info(f"开始爬取K线数据，复权类型: {adjust_type}...")
        
        # 获取待处理的股票列表
        stock_symbols = self._get_unprocessed_stocks()
        
        if max_stocks:
            stock_symbols = stock_symbols[:max_stocks]
            logger.info(f"限制处理数量: {max_stocks}")
        
        total = len(stock_symbols)
        self.processed_count = 0
        self.failed_symbols = []
        
        if total == 0:
            logger.info("没有待处理的股票")
            return
        
        for i, symbol in enumerate(stock_symbols, 1):
            logger.info(f'第{i}/{total}支，{symbol}-获取日线数据中...')
            
            try:
                # 使用重试机制获取K线数据
                kline_data_list = self._fetch_kline_data_with_retry(symbol, adjust_type)
                
                if kline_data_list:
                    # 批量保存K线数据（按日期存储）
                    success = self._save_kline_data_batch(kline_data_list)
                    if success:
                        # 记录处理日志
                        self._log_kline_processing(symbol)
                        self.processed_count += 1
                        logger.info(f"K线数据保存成功: {symbol}，共{len(kline_data_list)}条")
                    else:
                        self.failed_symbols.append(symbol)
                        logger.error(f"K线数据保存失败: {symbol}")
                else:
                    self.failed_symbols.append(symbol)
                    logger.warning(f"没有获取到K线数据: {symbol}")
                
            except Exception as e:
                self.failed_symbols.append(symbol)
                logger.error(f"获取K线数据异常 {symbol}: {e}")
            
            # 降低请求频率
            time.sleep(0.3)
        
        # 输出统计信息
        self._log_statistics()
        logger.info("K线数据爬取完成")
    
    def crawl_kline_data_after_adjust(self):
        """爬取后复权K线数据（便捷方法）"""
        return self.crawl_kline_data('after')
    
    def crawl_kline_data_before_adjust(self, max_stocks: Optional[int] = None):
        """爬取前复权K线数据（便捷方法）"""
        return self.crawl_kline_data('before', max_stocks)
    
    def crawl_kline_data_no_adjust(self, max_stocks: Optional[int] = None):
        """爬取不复权K线数据（便捷方法）"""
        return self.crawl_kline_data('none', max_stocks)
    
    def crawl_single_stock_kline(self, symbol: str, adjust_type: str = 'after') -> List[Dict[str, Any]]:
        """
        爬取单只股票的K线数据
        
        Args:
            symbol: 股票代码
            adjust_type: 复权类型
            
        Returns:
            List[Dict]: K线数据列表
        """
        logger.info(f"获取股票 {symbol} 的K线数据，复权类型: {adjust_type}")
        
        try:
            return self._fetch_kline_data_with_retry(symbol, adjust_type)
        except Exception as e:
            logger.error(f"获取股票 {symbol} K线数据失败: {e}")
            return []
    
    def get_kline_log_filepath(self) -> str:
        """获取K线处理日志文件路径"""
        if self.csv_storage:
            return self.csv_storage.get_kline_log_filepath()
        return 'kline_log.csv'
    
    def get_processed_symbols(self) -> List[str]:
        """
        获取已处理的股票列表
        
        Returns:
            List[str]: 已处理的股票代码列表
        """
        try:
            log_filepath = self.get_kline_log_filepath()
            
            if not os.path.exists(log_filepath):
                return []
            
            processed_symbols = []
            with open(log_filepath, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    symbol = row.get('symbol', '')
                    if symbol and symbol not in processed_symbols:
                        processed_symbols.append(symbol)
            
            logger.info(f"已处理股票数量: {len(processed_symbols)}")
            return processed_symbols
            
        except Exception as e:
            logger.error(f"获取已处理股票列表失败: {e}")
            return []
    
    def resume_crawl(self, adjust_type: str = 'after', max_stocks: Optional[int] = None):
        """
        恢复爬取 - 只处理未完成的股票
        
        Args:
            adjust_type: 复权类型
            max_stocks: 最大处理数量
        """
        logger.info("开始恢复K线数据爬取...")
        
        # 获取所有股票和已处理股票
        all_symbols = self._get_unprocessed_stocks()
        processed_symbols = self.get_processed_symbols()
        
        # 过滤出未处理的股票
        unprocessed_symbols = [symbol for symbol in all_symbols if symbol not in processed_symbols]
        
        if max_stocks:
            unprocessed_symbols = unprocessed_symbols[:max_stocks]
        
        logger.info(f"未处理股票数量: {len(unprocessed_symbols)}")
        
        if not unprocessed_symbols:
            logger.info("所有股票都已处理完成")
            return
        
        total = len(unprocessed_symbols)
        self.processed_count = 0
        self.failed_symbols = []
        
        for i, symbol in enumerate(unprocessed_symbols, 1):
            logger.info(f'恢复处理第{i}/{total}支，{symbol}-获取日线数据中...')
            
            try:
                kline_data_list = self._fetch_kline_data_with_retry(symbol, adjust_type)
                
                if kline_data_list:
                    success = self._save_kline_data_batch(kline_data_list)
                    if success:
                        self._log_kline_processing(symbol)
                        self.processed_count += 1
                        logger.info(f"K线数据保存成功: {symbol}，共{len(kline_data_list)}条")
                    else:
                        self.failed_symbols.append(symbol)
                        logger.error(f"K线数据保存失败: {symbol}")
                else:
                    self.failed_symbols.append(symbol)
                    logger.warning(f"没有获取到K线数据: {symbol}")
                
            except Exception as e:
                self.failed_symbols.append(symbol)
                logger.error(f"获取K线数据异常 {symbol}: {e}")
            
            time.sleep(0.3)
        
        self._log_statistics()
        logger.info("恢复K线数据爬取完成")
    
    def _fetch_kline_data_with_retry(self, symbol: str, adjust_type: str = 'after') -> List[Dict[str, Any]]:
        """
        获取K线数据 - 带重试机制
        
        Args:
            symbol: 股票代码
            adjust_type: 复权类型 ('before'前复权, 'after'后复权, 'none'不复权)
            
        Returns:
            List[Dict]: K线数据列表
        """
        for attempt in range(self.max_retries):
            try:
                # 动态生成时间戳
                timestamp = int(time.time() * 1000)
                url = (
                    f"{self.stock_base_url}/v5/stock/chart/kline.json"
                    f"?symbol={symbol}&begin=600000000000&end={timestamp}"
                    f"&period=day&type={adjust_type}&indicator=kline"
                )
                
                # 为stock.xueqiu.com使用专门的headers
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'cache-control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Host': 'stock.xueqiu.com',
                    'Referer': 'https://xueqiu.com/S',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                # 使用专门的headers发送请求
                response = self.session.get(url, headers=headers, timeout=self.crawler_config['timeout'])
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    raise Exception(f"HTTP错误: {response.status_code}")
                
                data = response.json()
                
                # 检查API错误码
                error_code = data.get('error_code')
                error_description = data.get('error_description', '')
                
                if error_code != 0:
                    raise Exception(f"API错误: {error_description} (错误码: {error_code})")
                
                # 解析K线数据
                kline_data = data.get('data', {})
                items = kline_data.get('item', [])
                
                if not items:
                    logger.warning(f"股票 {symbol} 没有K线数据")
                    return []
                
                # 转换数据格式
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
                        'turnoverrate': round(item[8], 2) if len(item) > 8 else 0.0,  # 换手率
                        'period': 'day',    # 日线
                        'type': adjust_type, # 复权类型
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'crawl_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    kline_list.append(kline_data_item)
                
                logger.debug(f"成功获取 {symbol} 的K线数据，共 {len(kline_list)} 条记录")
                return kline_list
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"第{attempt + 1}次尝试失败 {symbol}: {e}，等待重试...")
                    time.sleep(1)  # 等待1秒后重试
                else:
                    logger.error(f"重试{self.max_retries}次后仍然失败 {symbol}: {e}")
                    raise
        
        return []
    
    def _fetch_single_day_kline_data(self, symbol: str, begin_timestamp: int, end_timestamp: int, adjust_type: str = 'after') -> List[Dict[str, Any]]:
        """
        获取指定日期的K线数据
        
        Args:
            symbol: 股票代码
            begin_timestamp: 开始时间戳（毫秒）
            end_timestamp: 结束时间戳（毫秒）
            adjust_type: 复权类型
            
        Returns:
            List[Dict]: K线数据列表
        """
        for attempt in range(self.max_retries):
            try:
                url = (
                    f"{self.stock_base_url}/v5/stock/chart/kline.json"
                    f"?symbol={symbol}&begin={begin_timestamp}&end={end_timestamp}"
                    f"&period=day&type={adjust_type}&indicator=kline"
                )
                
                # 为stock.xueqiu.com使用专门的headers
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'cache-control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Host': 'stock.xueqiu.com',
                    'Referer': 'https://xueqiu.com/S',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                response = self.session.get(url, headers=headers, timeout=self.crawler_config['timeout'])
                
                if response.status_code != 200:
                    raise Exception(f"HTTP错误: {response.status_code}")
                
                data = response.json()
                
                error_code = data.get('error_code')
                error_description = data.get('error_description', '')
                
                if error_code != 0:
                    raise Exception(f"API错误: {error_description} (错误码: {error_code})")
                
                kline_data = data.get('data', {})
                items = kline_data.get('item', [])
                
                if not items:
                    logger.debug(f"股票 {symbol} 在指定日期没有数据")
                    return []
                
                # 转换数据格式
                kline_list = []
                for item in items:
                    kline_data_item = {
                        'symbol': symbol,
                        'timestamp': item[0] / 1000,
                        'volume': item[1],
                        'open': round(item[2], 2),
                        'high': round(item[3], 2),
                        'low': round(item[4], 2),
                        'close': round(item[5], 2),
                        'chg': round(item[6], 2),
                        'percent': round(item[7], 2),
                        'turnoverrate': round(item[8], 2) if len(item) > 8 else 0.0,
                        'period': 'day',
                        'type': adjust_type,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'crawl_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    kline_list.append(kline_data_item)
                
                logger.debug(f"成功获取 {symbol} 指定日期的K线数据，共 {len(kline_list)} 条记录")
                return kline_list
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"第{attempt + 1}次尝试失败 {symbol}: {e}，等待重试...")
                    time.sleep(1)
                else:
                    logger.error(f"重试{self.max_retries}次后仍然失败 {symbol}: {e}")
                    raise
        
        return []
    
    def _date_to_timestamp(self, date_str: str) -> int:
        """
        将日期字符串转换为时间戳（毫秒）
        
        Args:
            date_str: 日期字符串，格式 'YYYY-MM-DD'
            
        Returns:
            int: 时间戳（毫秒）
        """
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return int(dt.timestamp() * 1000)
        except Exception as e:
            logger.error(f"日期转换失败 {date_str}: {e}")
            return int(time.time() * 1000)
    
    def _save_single_day_data(self, kline_data_list: List[Dict[str, Any]], target_date: str) -> bool:
        """
        保存单日数据到指定日期的文件
        
        Args:
            kline_data_list: K线数据列表
            target_date: 目标日期
            
        Returns:
            bool: 是否成功
        """
        try:
            if not kline_data_list:
                return False
            
            # CSV存储模式
            if self.csv_storage:
                return self.csv_storage.save_kline_data_by_date(kline_data_list, target_date)
            
            # 数据库存储模式
            elif hasattr(self.data_repo, 'save_kline_data_batch'):
                return self.data_repo.save_kline_data_batch(kline_data_list)
            
            logger.warning("未找到合适的保存方法")
            return False
            
        except Exception as e:
            logger.error(f"保存单日数据失败: {e}")
            return False
    
    def _get_unprocessed_stocks(self) -> List[str]:
        """
        获取待处理的股票列表 - 从stock_info或stock_list中获取
        
        Returns:
            List[str]: 股票代码列表
        """
        try:
            # 使用CSV存储获取
            if self.csv_storage:
                # 获取最新的股票信息
                stock_info_data = self.csv_storage.get_latest_stock_info()
                if stock_info_data:
                    symbols = [stock['symbol'] for stock in stock_info_data if stock.get('symbol')]
                    logger.info(f"从最新stock_info获取到 {len(symbols)} 只股票")
                    return symbols
                
                # 如果没有stock_info，尝试获取stock_list
                stock_list_data = self.csv_storage.get_latest_stock_list()
                if stock_list_data:
                    symbols = [stock['symbol'] for stock in stock_list_data if stock.get('symbol')]
                    logger.info(f"从最新stock_list获取到 {len(symbols)} 只股票")
                    return symbols
            
            # 从数据库获取（原有逻辑）
            if hasattr(self.data_repo, 'get_unprocessed_kline_stocks'):
                return self.data_repo.get_unprocessed_kline_stocks()
            
            logger.warning("无法获取股票列表，请检查数据源")
            return []
            
        except Exception as e:
            logger.error(f"获取待处理股票列表失败: {e}")
            return []
    
    def _save_kline_data_batch(self, kline_data_list: List[Dict[str, Any]]) -> bool:
        """
        批量保存K线数据 - 支持CSV和数据库存储
        
        Args:
            kline_data_list: K线数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            if not kline_data_list:
                return False
            
            # CSV存储模式
            if self.csv_storage:
                # 按日期分组保存
                date_groups = {}
                for kline_data in kline_data_list:
                    date_str = kline_data.get('crawl_date', datetime.now().strftime('%Y-%m-%d'))
                    if date_str not in date_groups:
                        date_groups[date_str] = []
                    date_groups[date_str].append(kline_data)
                
                # 按日期保存
                success = True
                for date_str, data_list in date_groups.items():
                    if not self.csv_storage.save_kline_data_by_date(data_list, date_str):
                        success = False
                        break
                
                return success
            
            # 数据库存储模式
            elif hasattr(self.data_repo, 'save_kline_data_batch'):
                return self.data_repo.save_kline_data_batch(kline_data_list)
            
            logger.warning("未找到合适的保存方法")
            return False
            
        except Exception as e:
            logger.error(f"批量保存K线数据失败: {e}")
            return False
    
    def _log_kline_processing(self, symbol: str):
        """
        记录K线处理日志
        
        Args:
            symbol: 股票代码
        """
        try:
            log_data = {
                'symbol': symbol,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'crawl_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            # CSV存储模式
            if self.csv_storage:
                # 使用CSV存储的日志方法
                self.csv_storage.save_kline_log(log_data)
            
            # 数据库存储模式
            elif hasattr(self.data_repo, 'log_kline_processing'):
                self.data_repo.log_kline_processing(symbol)
                
        except Exception as e:
            logger.error(f"记录K线处理日志失败 {symbol}: {e}")
    
    def _log_statistics(self):
        """输出统计信息"""
        logger.info("=" * 50)
        logger.info("K线数据爬取统计")
        logger.info(f"成功处理: {self.processed_count} 支股票")
        logger.info(f"失败数量: {len(self.failed_symbols)} 支股票")
        
        if self.failed_symbols:
            logger.warning("失败的股票代码:")
            for symbol in self.failed_symbols:
                logger.warning(f"  - {symbol}")
        
        logger.info("=" * 50)