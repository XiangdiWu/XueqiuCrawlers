"""
股票数据爬虫 - 使用与stock_list_crawler相同的API和字段结构
"""
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from crawlers.base_crawler import BaseCrawler
from engine.logger import get_logger
from engine.database import DataRepository
from engine.xueqiu_auth import XueqiuAuth

logger = get_logger(__name__)


class StockInfoCrawler(BaseCrawler):
    """股票信息爬虫 - 使用stock_list API获取完整字段数据"""
    
    def __init__(self, data_repo: DataRepository = None):
        self.data_repo = data_repo or DataRepository()
        self.auth = XueqiuAuth()
        self.session = self.auth.get_session()
        
        # 股票列表API - 与stock_list_crawler相同
        self.stock_list_url = "https://xueqiu.com/stock/cata/stocklist.json"
        
        # 股票类型映射
        self.stock_types = {
            '11': 'A股',
            '12': 'B股', 
            '13': '港股',
            '14': '美股',
            '15': '指数',
            '16': '基金',
            '17': '债券',
            '18': '期货',
            '19': '外汇'
        }
        
        logger.info("股票信息爬虫初始化完成")
    
    def get_stock_list(self, page: int = 1, size: int = 100, 
                      order: str = 'desc', orderby: str = 'percent',
                      stock_type: str = '11,12') -> Optional[Dict[str, Any]]:
        """
        获取股票列表数据 - 与stock_list_crawler相同的API
        
        Args:
            page: 页码
            size: 每页数量
            order: 排序方向 (asc/desc)
            orderby: 排序字段 (percent/current/volume等)
            stock_type: 股票类型，默认11,12(A股B股)
            
        Returns:
            Dict: 股票列表数据
        """
        try:
            timestamp = int(time.time() * 1000)
            
            params = {
                'page': page,
                'size': size,
                'order': order,
                'orderby': orderby,
                'type': stock_type,
                '_': timestamp
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://xueqiu.com/hq',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(
                self.stock_list_url, 
                params=params, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # 雪球API响应结构可能是 data.list 或直接是 stocks
                stock_list = data.get('data', {}).get('list', []) or data.get('stocks', [])
                logger.info(f"成功获取第{page}页股票列表，共{len(stock_list)}条记录")
                return data
            else:
                logger.error(f"获取股票列表失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取股票列表异常: {e}")
            return None
    
    def parse_stock_data(self, stock_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析股票数据 - 与stock_list_crawler完全相同的字段结构
        
        Args:
            stock_item: 原始股票数据
            
        Returns:
            Dict: 解析后的股票数据
        """
        try:
            # 基础字段映射 - 与stock_list_crawler保持一致
            parsed_data = {
                'symbol': stock_item.get('symbol', ''),
                'name': stock_item.get('name', ''),
                'current': stock_item.get('current', 0.0),
                'percent': stock_item.get('percent', 0.0),
                'chg': stock_item.get('chg', 0.0),
                'volume': stock_item.get('volume', 0),
                'amount': stock_item.get('amount', 0.0),
                'turnoverrate': stock_item.get('turnoverrate', 0.0),
                'pe_ttm': stock_item.get('pe_ttm', 0.0),
                'pb': stock_item.get('pb', 0.0),
                'market_capital': stock_item.get('market_capital', 0.0),
                'float_market_capital': stock_item.get('float_market_capital', 0.0),
                'high_52w': stock_item.get('high_52w', 0.0),
                'low_52w': stock_item.get('low_52w', 0.0),
                'amplitude': stock_item.get('amplitude', 0.0),
                'current_year_percent': stock_item.get('current_year_percent', 0.0),
                'type': stock_item.get('type', ''),
                'hasexist': stock_item.get('hasexist', ''),
                'is_delist': stock_item.get('is_delist', ''),
                'is_suspended': stock_item.get('is_suspended', ''),
                'stock_type': self.stock_types.get(stock_item.get('type', ''), '未知'),
                'crawl_date': datetime.now().strftime('%Y-%m-%d'),
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': int(time.time())
            }
            
            # 添加更多字段 - 与stock_list_crawler保持一致
            if 'quote' in stock_item:
                quote = stock_item['quote']
                parsed_data.update({
                    'open': quote.get('open', 0.0),
                    'high': quote.get('high', 0.0),
                    'low': quote.get('low', 0.0),
                    'preclose': quote.get('preclose', 0.0),
                    'y_close': quote.get('y_close', 0.0),
                    'lot_size': quote.get('lot_size', 0),
                    'tick_size': quote.get('tick_size', 0.0),
                    'per_share': quote.get('per_share', 0.0),
                    'profit': quote.get('profit', 0.0),
                    'profit_four': quote.get('profit_four', 0.0),
                    'eps': quote.get('eps', 0.0),
                    'eps_ttm': quote.get('eps_ttm', 0.0),
                    'navps': quote.get('navps', 0.0),
                    'roe': quote.get('roe', 0.0),
                    'roa': quote.get('roa', 0.0),
                    'update_time': quote.get('update_time', ''),
                    'timestamp': quote.get('timestamp', 0)
                })
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"解析股票数据失败: {e}")
            return {}
    
    def crawl_all_pages(self, max_pages: int = 10, page_size: int = 100,
                       stock_type: str = '11,12') -> List[Dict[str, Any]]:
        """
        爬取所有页面的股票列表 - 与stock_list_crawler保持一致
        
        Args:
            max_pages: 最大页数
            page_size: 每页数量
            stock_type: 股票类型
            
        Returns:
            List[Dict]: 所有股票数据
        """
        all_stocks = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"正在爬取第 {page} 页股票列表...")
            
            data = self.get_stock_list(
                page=page, 
                size=page_size,
                stock_type=stock_type
            )
            
            if not data:
                logger.warning(f"第 {page} 页数据获取失败，停止爬取")
                break
            
            # 雪球API响应结构可能是 data.list 或直接是 stocks
            stock_list = data.get('data', {}).get('list', []) or data.get('stocks', [])
            
            if not stock_list:
                logger.info(f"第 {page} 页没有数据，停止爬取")
                break
            
            # 解析股票数据
            for stock_item in stock_list:
                parsed_stock = self.parse_stock_data(stock_item)
                if parsed_stock:
                    all_stocks.append(parsed_stock)
            
            # 检查是否还有更多数据
            count = data.get('data', {}).get('count', 0) or data.get('count', 0)
            try:
                count = int(count) if count else 0
            except (ValueError, TypeError):
                count = 0
                
            if page * page_size >= count and count > 0:
                logger.info(f"已爬取所有数据，总共 {count} 条记录")
                break
            
            # 避免请求过快
            time.sleep(0.5)
        
        logger.info(f"股票列表爬取完成，共获取 {len(all_stocks)} 条记录")
        return all_stocks
    
    def crawl_stock_list(self):
        """爬取股票实时行情到stock_info目录"""
        logger.info("开始爬取股票信息到stock_info...")
        
        # 爬取所有页面数据
        all_stocks = self.crawl_all_pages(max_pages=10, page_size=100, stock_type='11,12')
        
        if all_stocks:
            # 按日期保存到stock_info目录
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                # CSV模式，按日期保存到stock_info目录
                success = self.data_repo.csv_storage.save_stock_info_by_date(all_stocks, date_str)
            else:
                # 数据库模式，使用原有方法
                success = True
                for stock_data in all_stocks:
                    if not self.data_repo.save_stock_basic_info(stock_data):
                        success = False
                        break
            
            if success:
                logger.info(f"成功保存 {len(all_stocks)} 条股票信息到stock_info")
            else:
                logger.error("保存股票信息失败")
        else:
            logger.error("没有获取到股票数据")
        
        logger.info("股票信息爬取完成")
    
    def create_simplified_stock_list(self, date_str: str = None) -> bool:
        """
        从stock_info读取数据，创建简化的stock_list（只包含symbol、code、name、crawl_time）
        
        Args:
            date_str: 日期字符串，格式YYYY-MM-DD，默认为今天
            
        Returns:
            bool: 是否成功
        """
        try:
            if date_str is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"从stock_info创建{date_str}的简化股票列表...")
            
            # 从stock_info读取指定日期的数据
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                stock_info_data = self.data_repo.csv_storage.get_stock_info_by_date(date_str)
            else:
                # 从数据库查询
                query = f"SELECT * FROM stock_info WHERE DATE(crawl_time) = '{date_str}'"
                stock_info_data = self.data_repo.database.execute_query(query)
            
            if not stock_info_data:
                logger.warning(f"没有找到{date_str}的stock_info数据")
                return False
            
            # 创建简化的股票数据
            simplified_stocks = []
            for stock in stock_info_data:
                # 从symbol中提取code（去掉SZ/SH等后缀）
                symbol = stock.get('symbol', '')
                code = symbol
                if len(symbol) > 6:
                    code = symbol[:-6] if symbol[-6:].isdigit() else symbol
                
                simplified_stock = {
                    'symbol': symbol,
                    'code': code,
                    'name': stock.get('name', ''),
                    'crawl_time': stock.get('crawl_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'crawl_date': date_str
                }
                simplified_stocks.append(simplified_stock)
            
            # 保存简化版本到stock_list目录
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                success = self.data_repo.csv_storage.save_stock_list_by_date(simplified_stocks, date_str)
            else:
                # 数据库模式
                success = True
                for stock_data in simplified_stocks:
                    if not self.data_repo.save_stock_list([stock_data]):
                        success = False
                        break
            
            if success:
                logger.info(f"成功创建简化股票列表，共{len(simplified_stocks)}条记录")
            else:
                logger.error(f"创建简化股票列表失败")
            
            return success
            
        except Exception as e:
            logger.error(f"创建简化股票列表异常: {e}")
            return False
    
