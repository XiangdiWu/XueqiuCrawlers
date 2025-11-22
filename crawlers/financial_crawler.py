"""
财务数据爬虫 - 借鉴recycling/finmain.py的健壮性设计
"""
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from crawlers.base_crawler import BaseCrawler
from engine.logger import get_logger
from engine.database import DataRepository
from engine.xueqiu_auth import XueqiuAuth

logger = get_logger(__name__)


class FinancialCrawler(BaseCrawler):
    """财务数据爬虫"""
    
    def __init__(self, data_repo: DataRepository = None):
        self.data_repo = data_repo or DataRepository()
        self.auth = XueqiuAuth()
        self.session = self.auth.get_session()
        
        # 财务数据API
        self.financial_url = "https://xueqiu.com/stock/f10/finmainindex.json"
        
        # 请求头 - 借鉴recycling/finmain.py
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'xueqiu.com',
            'Referer': 'https://xueqiu.com/S',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        logger.info("财务数据爬虫初始化完成")
    
    def get_financial_data(self, symbol: str, max_retries: int = 3) -> Optional[List[Dict[str, Any]]]:
        """
        获取指定股票的财务数据 - 借鉴recycling/finmain.py的重试机制
        
        Args:
            symbol: 股票代码
            max_retries: 最大重试次数
            
        Returns:
            List[Dict]: 财务数据列表
        """
        timestamp = int(time.time() * 1000)
        url = f"{self.financial_url}?symbol={symbol}&page=1&size=100&_={timestamp}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    # 将null替换为0，防止解析错误 - 借鉴recycling/finmain.py
                    text = response.text.replace('null', '0')
                    data = json.loads(text)
                    
                    financial_list = []
                    for item in data.get('list', []):
                        # 用股票代码替换雪球内部编号 - 借鉴recycling/finmain.py
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
                            'cashequfinbal': item.get('cashequfinbal', 0),
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'timestamp': int(time.time())
                        }
                        financial_list.append(financial_data)
                    
                    logger.info(f"成功获取{symbol}财务数据，共{len(financial_list)}条记录")
                    return financial_list
                    
                else:
                    logger.warning(f"获取{symbol}财务数据失败，状态码: {response.status_code}，尝试次数: {attempt + 1}")
                    
            except Exception as e:
                logger.error(f"获取{symbol}财务数据异常: {e}，尝试次数: {attempt + 1}")
            
            # 重试前等待
            if attempt < max_retries - 1:
                time.sleep(0.3)
        
        logger.error(f"获取{symbol}财务数据最终失败")
        return None
    
    def save_financial_data(self, symbol: str, financial_data_list: List[Dict[str, Any]]) -> bool:
        """
        保存财务数据 - 借鉴recycling/finmain.py的日志记录
        
        Args:
            symbol: 股票代码
            financial_data_list: 财务数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            success_count = 0
            error_count = 0
            
            # CSV模式需要批量保存，而不是逐条保存
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                # CSV模式 - 批量保存
                try:
                    success = self.data_repo.csv_storage.save_financial_data_by_symbol(
                        symbol, financial_data_list
                    )
                    if success:
                        success_count += len(financial_data_list)
                        for financial_data in financial_data_list:
                            report_date = financial_data.get('reportdate', '')
                            logger.info(f'{symbol}*{report_date}*财报 爬取成功')
                            # 记录处理日志 - 借鉴recycling/finmain.py
                            self._save_financial_log(symbol, report_date)
                    else:
                        error_count += len(financial_data_list)
                except Exception as e:
                    error_count += len(financial_data_list)
                    logger.error(f'批量保存{symbol}财务数据失败: {e}')
            else:
                # 数据库模式 - 逐条保存
                for financial_data in financial_data_list:
                    try:
                        success = self.data_repo.save_finmain_data(financial_data)
                        
                        if success:
                            success_count += 1
                            report_date = financial_data.get('reportdate', '')
                            logger.info(f'{symbol}*{report_date}*财报 爬取成功')
                            
                            # 记录处理日志 - 借鉴recycling/finmain.py
                            self._save_financial_log(symbol, report_date)
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        logger.error(f'保存{symbol}财务数据失败: {e}')
            
            logger.info(f"{symbol}财务数据处理完成，成功: {success_count}, 失败: {error_count}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"保存{symbol}财务数据异常: {e}")
            return False
    
    def _save_financial_log(self, symbol: str, report_date: str):
        """保存财务数据处理日志 - 借鉴recycling/finmain.py"""
        try:
            log_data = {
                'compcode': symbol,
                'reportdate': report_date,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                # CSV模式 - 保存到日志文件
                self.data_repo.csv_storage.save_financial_log(log_data)
            else:
                # 数据库模式 - 插入日志表
                sql = f'INSERT INTO finmain_log (compcode, reportdate, timestamp) VALUES ("{symbol}", "{report_date}", CURRENT_TIMESTAMP) ON DUPLICATE KEY UPDATE timestamp=CURRENT_TIMESTAMP'
                self.data_repo.database.execute_query(sql)
                
        except Exception as e:
            logger.warning(f"保存财务日志失败: {e}")
    
    def get_unprocessed_stocks(self) -> List[str]:
        """
        获取未处理财务数据的股票列表 - 借鉴recycling/finmain.py的查询逻辑
        
        Returns:
            List[str]: 股票代码列表
        """
        try:
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                # CSV模式 - 从stock_info获取股票列表，排除已处理的
                all_stocks = self.data_repo.csv_storage.get_latest_stock_info()
                processed_logs = self.data_repo.csv_storage.get_financial_logs()
                
                # 构建已处理的股票-报告日期集合
                processed_set = set()
                for log in processed_logs:
                    compcode = log.get('compcode', '')
                    reportdate = log.get('reportdate', '')
                    if compcode and reportdate:
                        processed_set.add(f"{compcode}_{reportdate}")
                
                # 返回未处理的股票
                unprocessed_symbols = []
                for stock in all_stocks:
                    symbol = stock.get('symbol', '')
                    if symbol and symbol not in [log.get('compcode', '') for log in processed_logs]:
                        unprocessed_symbols.append(symbol)
                
                return unprocessed_symbols[:50]  # 限制数量避免过多请求
                
            else:
                # 数据库模式 - 使用SQL查询
                query = '''
                SELECT DISTINCT a.symbol 
                FROM stocks a 
                LEFT JOIN finmain_log b ON a.symbol = b.compcode 
                WHERE b.compcode IS NULL 
                ORDER BY a.symbol ASC 
                LIMIT 50
                '''
                result = self.data_repo.database.execute_query(query)
                return [row.get('symbol', '') for row in result if row.get('symbol')]
                
        except Exception as e:
            logger.error(f"获取未处理股票列表失败: {e}")
            return []
    
    def crawl_financial_data(self):
        """爬取财务数据主函数 - 借鉴recycling/finmain.py的流程"""
        logger.info("开始爬取财务数据...")
        
        # 获取未处理的股票列表
        stock_symbols = self.get_unprocessed_stocks()
        total = len(stock_symbols)
        
        if total == 0:
            logger.info("没有需要处理财务数据的股票")
            return
        
        logger.info(f"找到{total}支股票需要处理财务数据")
        
        success_count = 0
        error_count = 0
        
        for i, symbol in enumerate(stock_symbols, 1):
            logger.info(f'第{i}支股票，{symbol}')
            
            try:
                # 获取财务数据
                financial_data_list = self.get_financial_data(symbol)
                
                if financial_data_list:
                    # 保存财务数据
                    if self.save_financial_data(symbol, financial_data_list):
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1
                    logger.warning(f"未获取到{symbol}的财务数据")
                
            except Exception as e:
                error_count += 1
                logger.error(f'处理{symbol}财务数据异常: {e}')
            
            # 降低爬取速度 - 借鉴recycling/finmain.py
            time.sleep(0.3)
            
            logger.info('-' * 50)
        
        logger.info(f"财务数据爬取完成，总计: {total}, 成功: {success_count}, 失败: {error_count}")
    
    def crawl_single_stock_financial(self, symbol: str) -> bool:
        """
        爬取单只股票的财务数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始爬取{symbol}的财务数据...")
        
        try:
            financial_data_list = self.get_financial_data(symbol)
            
            if financial_data_list:
                return self.save_financial_data(symbol, financial_data_list)
            else:
                logger.warning(f"未获取到{symbol}的财务数据")
                return False
                
        except Exception as e:
            logger.error(f"爬取{symbol}财务数据失败: {e}")
            return False