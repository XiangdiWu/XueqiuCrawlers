"""
数据库连接和操作模块
"""
import pymysql
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config.settings import Config
from engine.logger import get_logger
import threading
import time

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器 - 支持连接池"""
    
    def __init__(self, pool_size=5):
        self.config = Config.DATABASE_CONFIG
        self.pool_size = pool_size
        self._pool = []
        self._lock = threading.Lock()
        self._created_connections = 0
        self._max_connections = pool_size * 2  # 最大连接数
    
    def _create_connection(self):
        """创建新连接"""
        try:
            conn = pymysql.connect(**self.config)
            self._created_connections += 1
            logger.debug(f"创建新数据库连接，当前连接数: {self._created_connections}")
            return conn
        except Exception as e:
            logger.error(f"创建数据库连接失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器 - 支持连接池"""
        connection = None
        try:
            # 尝试从连接池获取连接
            with self._lock:
                if self._pool:
                    connection = self._pool.pop()
                    logger.debug(f"从连接池获取连接，剩余: {len(self._pool)}")
                elif self._created_connections < self._max_connections:
                    connection = self._create_connection()
                else:
                    # 等待可用连接
                    logger.warning("连接池已满，等待可用连接...")
                    time.sleep(0.1)
                    # 递归调用获取连接
                    with self.get_connection() as conn:
                        yield conn
                        return
            
            # 检查连接是否有效
            if not self._is_connection_valid(connection):
                connection.close()
                connection = self._create_connection()
            
            yield connection
            
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                # 将连接放回连接池
                with self._lock:
                    if len(self._pool) < self.pool_size and self._is_connection_valid(connection):
                        self._pool.append(connection)
                        logger.debug(f"连接放回池中，当前池大小: {len(self._pool)}")
                    else:
                        connection.close()
                        self._created_connections -= 1
                        logger.debug(f"关闭连接，当前连接数: {self._created_connections}")
    
    def _is_connection_valid(self, connection):
        """检查连接是否有效"""
        try:
            connection.ping(reconnect=False)
            return True
        except:
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def close_all_connections(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._pool:
                try:
                    conn.close()
                except:
                    pass
            self._pool.clear()
            self._created_connections = 0
            logger.info("所有数据库连接已关闭")
    
    def execute_query(self, sql, params=None):
        """执行查询语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
    
    def execute_update(self, sql, params=None):
        """执行更新语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            cursor.close()
    
    def execute_batch_update(self, sql_list):
        """批量执行更新语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for sql, params in sql_list:
                    cursor.execute(sql, params or ())
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()


class StockRepository:
    """股票数据仓库"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_stock_symbols(self):
        """获取所有股票代码"""
        sql = "SELECT symbol FROM stocks ORDER BY symbol ASC"
        result = self.db.execute_query(sql)
        return [item['symbol'] for item in result]
    
    def get_unprocessed_finmain_stocks(self):
        """获取未处理财务数据的股票"""
        sql = """
        SELECT a.symbol FROM stocks a 
        LEFT JOIN finmain_log b ON a.symbol = b.compcode 
        WHERE b.compcode IS NULL 
        ORDER BY a.symbol ASC
        """
        result = self.db.execute_query(sql)
        return [item['symbol'] for item in result]
    
    def get_unprocessed_kline_stocks(self):
        """获取未处理K线数据的股票"""
        sql = """
        SELECT a.symbol FROM stocks a 
        LEFT JOIN kline_log b ON a.symbol = b.symbol 
        WHERE b.symbol IS NULL 
        ORDER BY a.symbol ASC
        """
        result = self.db.execute_query(sql)
        return [item['symbol'] for item in result]
    
    def upsert_stock_basic_info(self, stock_data):
        """插入或更新股票基本信息"""
        sql = """
        INSERT INTO stocks (symbol, compcode, compsname, current, percent, 
                           high52w, low52w, marketcapital, amount, volume, pe_ttm)
        VALUES (%(symbol)s, %(code)s, %(name)s, %(current)s, %(percent)s,
                %(high52w)s, %(low52w)s, %(marketcapital)s, %(amount)s, 
                %(volume)s, %(pe_ttm)s)
        ON DUPLICATE KEY UPDATE 
        current = %(current)s, percent = %(percent)s, high52w = %(high52w)s,
        low52w = %(low52w)s, marketcapital = %(marketcapital)s, 
        amount = %(amount)s, volume = %(volume)s, pe_ttm = %(pe_ttm)s,
        timestamp = CURRENT_TIMESTAMP
        """
        self.db.execute_update(sql, stock_data)
    
    def upsert_company_info(self, company_data):
        """插入或更新公司信息"""
        sql = """
        INSERT INTO comp (compname, engname, founddate, regcapital, chairman,
                        manager, leconstant, accfirm, regaddr, officeaddr,
                        compintro, bizscope, majorbiz, compcode, compsname, region)
        VALUES (%(compname)s, %(engname)s, %(founddate)s, %(regcapital)s,
                %(chairman)s, %(manager)s, %(leconstant)s, %(accfirm)s,
                %(regaddr)s, %(officeaddr)s, %(compintro)s, %(bizscope)s,
                %(majorbiz)s, %(compcode)s, %(compsname)s, %(region)s)
        ON DUPLICATE KEY UPDATE
        compname = %(compname)s, engname = %(engname)s, regcapital = %(regcapital)s,
        chairman = %(chairman)s, manager = %(manager)s, leconstant = %(leconstant)s,
        accfirm = %(accfirm)s, regaddr = %(regaddr)s, officeaddr = %(officeaddr)s,
        compintro = %(compintro)s, bizscope = %(bizscope)s, majorbiz = %(majorbiz)s,
        compsname = %(compsname)s, region = %(region)s, timestamp = CURRENT_TIMESTAMP
        """
        self.db.execute_update(sql, company_data)
    
    def upsert_finmain_data(self, finmain_data):
        """插入或更新主要财务数据"""
        sql = """
        INSERT INTO finmain (compcode, reportdate, basiceps, epsdiluted, epsweighted,
                           naps, opercashpershare, peropecashpershare, netassgrowrate,
                           dilutedroe, weightedroe, mainbusincgrowrate, netincgrowrate,
                           totassgrowrate, salegrossprofitrto, mainbusiincome,
                           mainbusiprofit, totprofit, netprofit, totalassets,
                           totalliab, totsharequi, operrevenue, invnetcashflow,
                           finnetcflow, chgexchgchgs, cashnetr, cashequfinbal)
        VALUES (%(compcode)s, %(reportdate)s, %(basiceps)s, %(epsdiluted)s,
                %(epsweighted)s, %(naps)s, %(opercashpershare)s, %(peropecashpershare)s,
                %(netassgrowrate)s, %(dilutedroe)s, %(weightedroe)s,
                %(mainbusincgrowrate)s, %(netincgrowrate)s, %(totassgrowrate)s,
                %(salegrossprofitrto)s, %(mainbusiincome)s, %(mainbusiprofit)s,
                %(totprofit)s, %(netprofit)s, %(totalassets)s, %(totalliab)s,
                %(totsharequi)s, %(operrevenue)s, %(invnetcashflow)s,
                %(finnetcflow)s, %(chgexchgchgs)s, %(cashnetr)s, %(cashequfinbal)s)
        ON DUPLICATE KEY UPDATE
        basiceps = %(basiceps)s, epsdiluted = %(epsdiluted)s, epsweighted = %(epsweighted)s,
        naps = %(naps)s, opercashpershare = %(opercashpershare)s, peropecashpershare = %(peropecashpershare)s,
        netassgrowrate = %(netassgrowrate)s, dilutedroe = %(dilutedroe)s, weightedroe = %(weightedroe)s,
        mainbusincgrowrate = %(mainbusincgrowrate)s, netincgrowrate = %(netincgrowrate)s,
        totassgrowrate = %(totassgrowrate)s, salegrossprofitrto = %(salegrossprofitrto)s,
        mainbusiincome = %(mainbusiincome)s, mainbusiprofit = %(mainbusiprofit)s,
        totprofit = %(totprofit)s, netprofit = %(netprofit)s, totalassets = %(totalassets)s,
        totalliab = %(totalliab)s, totsharequi = %(totsharequi)s, operrevenue = %(operrevenue)s,
        invnetcashflow = %(invnetcashflow)s, finnetcflow = %(finnetcflow)s,
        chgexchgchgs = %(chgexchgchgs)s, cashnetr = %(cashnetr)s, cashequfinbal = %(cashequfinbal)s
        """
        self.db.execute_update(sql, finmain_data)
    
    def upsert_kline_data(self, kline_data):
        """插入或更新K线数据"""
        sql = """
        INSERT INTO kline (symbol, timestamp, volume, open, high, low, close,
                          chg, percent, turnoverrate, period, type)
        VALUES (%(symbol)s, FROM_UNIXTIME(%(timestamp)s), %(volume)s, %(open)s,
                %(high)s, %(low)s, %(close)s, %(chg)s, %(percent)s,
                %(turnoverrate)s, %(period)s, %(type)s)
        ON DUPLICATE KEY UPDATE
        volume = %(volume)s, open = %(open)s, high = %(high)s, low = %(low)s,
        close = %(close)s, chg = %(chg)s, percent = %(percent)s,
        turnoverrate = %(turnoverrate)s, period = %(period)s, type = %(type)s
        """
        self.db.execute_update(sql, kline_data)
    
    def log_finmain_processing(self, compcode, reportdate):
        """记录财务数据处理日志"""
        sql = """
        INSERT INTO finmain_log (compcode, reportdate, timestamp)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        """
        self.db.execute_update(sql, (compcode, reportdate))
    
    def log_kline_processing(self, symbol):
        """记录K线数据处理日志"""
        sql = """
        INSERT INTO kline_log (symbol, timestamp)
        VALUES (%s, CURRENT_TIMESTAMP)
        """
        self.db.execute_update(sql, (symbol,))


class DataRepository:
    """统一数据仓库接口，支持数据库和CSV存储"""
    
    def __init__(self, storage_type: str = None):
        from config.settings import Config
        
        # 确定存储类型
        if storage_type is None:
            storage_type = Config.STORAGE_CONFIG.get('type', 'database')
        
        self.storage_type = storage_type
        
        if storage_type == 'database':
            self.db_manager = DatabaseManager()
            self.stock_repo = StockRepository(self.db_manager)
            self.csv_storage = None
        elif storage_type == 'csv':
            from .csv_storage import CSVStorage
            csv_config = Config.STORAGE_CONFIG
            self.csv_storage = CSVStorage(
                csv_path=csv_config.get('csv_path', 'data/csv'),
                encoding=csv_config.get('csv_encoding', 'utf-8-sig')
            )
            self.db_manager = None
            self.stock_repo = None
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")
        
        logger.info(f"初始化数据仓库，存储类型: {storage_type}")
    
    def get_stock_symbols(self) -> List[str]:
        """获取所有股票代码"""
        if self.storage_type == 'database':
            return self.stock_repo.get_stock_symbols()
        else:
            data = self.csv_storage.read_from_csv('stock_list')
            return [item.get('symbol', '') for item in data if item.get('symbol')]
    
    def get_unprocessed_finmain_stocks(self) -> List[str]:
        """获取未处理财务数据的股票"""
        if self.storage_type == 'database':
            return self.stock_repo.get_unprocessed_finmain_stocks()
        else:
            # CSV模式下，获取所有股票代码
            stock_symbols = self.get_stock_symbols()
            # 获取已处理财务数据的股票
            processed_data = self.csv_storage.read_from_csv('finmain_log')
            processed_symbols = set(item.get('compcode', '') for item in processed_data)
            # 返回未处理的股票
            return [symbol for symbol in stock_symbols if symbol not in processed_symbols]
    
    def get_unprocessed_kline_stocks(self) -> List[str]:
        """获取未处理K线数据的股票"""
        if self.storage_type == 'database':
            return self.stock_repo.get_unprocessed_kline_stocks()
        else:
            # CSV模式下，获取所有股票代码
            stock_symbols = self.get_stock_symbols()
            # 获取已处理K线数据的股票
            processed_data = self.csv_storage.read_from_csv('kline_log')
            processed_symbols = set(item.get('symbol', '') for item in processed_data)
            # 返回未处理的股票
            return [symbol for symbol in stock_symbols if symbol not in processed_symbols]
    
    def save_stock_basic_info(self, stock_data: Dict[str, Any]) -> bool:
        """保存股票基本信息"""
        try:
            if self.storage_type == 'database':
                self.stock_repo.upsert_stock_basic_info(stock_data)
            else:
                # CSV模式，追加数据到stock_info目录
                success = self.csv_storage.append_data([stock_data], 'stock_info', 'symbol')
            return True
        except Exception as e:
            logger.error(f"保存股票基本信息失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def save_company_info(self, company_data: Dict[str, Any]) -> bool:
        """保存公司信息"""
        try:
            if self.storage_type == 'database':
                self.stock_repo.upsert_company_info(company_data)
            else:
                # CSV模式 - 按证券代码单独存储
                symbol = company_data.get('compcode', '')
                if symbol:
                    self.csv_storage.save_company_info_by_symbol(company_data, symbol)
                else:
                    # 兼容旧模式，保存到company_profile.csv
                    self.csv_storage.save_company_profile([company_data])
            return True
        except Exception as e:
            logger.error(f"保存公司信息失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def get_company_info_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        根据证券代码获取公司信息
        
        Args:
            symbol: 证券代码
            
        Returns:
            Dict: 公司信息数据
        """
        try:
            if self.storage_type == 'database':
                sql = "SELECT * FROM comp WHERE compcode = %s"
                result = self.db_manager.execute_query(sql, (symbol,))
                return result[0] if result else {}
            else:
                return self.csv_storage.get_company_info_by_symbol(symbol)
        except Exception as e:
            logger.error(f"获取公司信息失败 {symbol}: {e}")
            return {}
    
    def save_finmain_data(self, finmain_data: Dict[str, Any]) -> bool:
        """保存主要财务数据"""
        try:
            if self.storage_type == 'database':
                self.stock_repo.upsert_finmain_data(finmain_data)
                # 记录处理日志
                self.stock_repo.log_finmain_processing(
                    finmain_data['compcode'], 
                    finmain_data['reportdate']
                )
            else:
                # 保存财务数据到financial目录
                self.csv_storage.save_to_csv([finmain_data], 'financial_data', mode='a')
                # 记录处理日志
                import pandas as pd
                log_data = {
                    'compcode': finmain_data['compcode'],
                    'reportdate': finmain_data['reportdate'],
                    'timestamp': str(pd.Timestamp.now())
                }
                self.csv_storage.save_to_csv([log_data], 'finmain_log', mode='a')
            return True
        except Exception as e:
            logger.error(f"保存财务数据失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def save_kline_data(self, kline_data: Dict[str, Any]) -> bool:
        """保存K线数据"""
        try:
            if self.storage_type == 'database':
                self.stock_repo.upsert_kline_data(kline_data)
            else:
                # 保存K线数据（按日期存储）
                self.csv_storage.save_kline_data_by_date([kline_data])
            return True
        except Exception as e:
            logger.error(f"保存K线数据失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def save_kline_data_batch(self, kline_data_list: List[Dict[str, Any]], date_str: str = None) -> bool:
        """
        批量保存K线数据（按日期存储）
        
        Args:
            kline_data_list: K线数据列表
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            bool: 是否成功
        """
        try:
            if self.storage_type == 'database':
                # 数据库模式，逐条保存
                for kline_data in kline_data_list:
                    self.stock_repo.upsert_kline_data(kline_data)
            else:
                # CSV模式，按日期批量保存
                self.csv_storage.save_kline_data_by_date(kline_data_list, date_str)
            return True
        except Exception as e:
            logger.error(f"批量保存K线数据失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def log_kline_processing(self, symbol: str) -> bool:
        """记录K线数据处理日志"""
        try:
            if self.storage_type == 'database':
                self.stock_repo.log_kline_processing(symbol)
            else:
                import pandas as pd
                log_data = {
                    'symbol': symbol,
                    'timestamp': str(pd.Timestamp.now())
                }
                self.csv_storage.append_data([log_data], 'kline_log', 'symbol')
            return True
        except Exception as e:
            logger.error(f"记录K线处理日志失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def batch_save_stock_data(self, stock_data_list: List[Dict[str, Any]]) -> bool:
        """批量保存股票数据"""
        try:
            if self.storage_type == 'database':
                # 数据库批量操作
                sql_list = []
                for stock_data in stock_data_list:
                    sql = """
                    INSERT INTO stocks (symbol, compcode, compsname, current, percent, 
                                       high52w, low52w, marketcapital, amount, volume, pe_ttm)
                    VALUES (%(symbol)s, %(code)s, %(name)s, %(current)s, %(percent)s,
                            %(high52w)s, %(low52w)s, %(marketcapital)s, %(amount)s, 
                            %(volume)s, %(pe_ttm)s)
                    ON DUPLICATE KEY UPDATE 
                    current = %(current)s, percent = %(percent)s, high52w = %(high52w)s,
                    low52w = %(low52w)s, marketcapital = %(marketcapital)s, 
                    amount = %(amount)s, volume = %(volume)s, pe_ttm = %(pe_ttm)s,
                    timestamp = CURRENT_TIMESTAMP
                    """
                    sql_list.append((sql, stock_data))
                
                self.db_manager.execute_batch_update(sql_list)
            else:
                # CSV批量操作
                self.csv_storage.append_data(stock_data_list, 'stock_list', 'symbol')
                self.csv_storage.append_data(stock_data_list, 'stock_info', 'symbol')
            return True
        except Exception as e:
            logger.error(f"批量保存股票数据失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        if self.storage_type == 'database':
            try:
                # 获取数据库表信息
                tables_info = {}
                tables = ['stocks', 'comp', 'finmain', 'kline']
                for table in tables:
                    result = self.db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                    tables_info[table] = result[0]['count'] if result else 0
                
                return {
                    'type': 'database',
                    'tables': tables_info,
                    'config': self.db_manager.config
                }
            except Exception as e:
                return {'type': 'database', 'error': str(e)}
        else:
            try:
                # 获取CSV文件信息
                files_info = {}
                tables = ['stock_list', 'company_profile', 'financial_data', 'kline_data']
                for table in tables:
                    files_info[table] = self.csv_storage.get_file_info(table)
                
                return {
                    'type': 'csv',
                    'files': files_info,
                    'config': {
                        'csv_path': self.csv_storage.csv_path,
                        'encoding': self.csv_storage.encoding
                    }
                }
            except Exception as e:
                return {'type': 'csv', 'error': str(e)}
    
    def create_backup(self) -> bool:
        """创建备份"""
        try:
            if self.storage_type == 'database':
                # 数据库备份（这里可以扩展为实际的数据库备份逻辑）
                logger.info("数据库备份功能待实现")
                return True
            else:
                # CSV备份
                tables = ['stock_list', 'company_profile', 'financial_data', 'kline_data']
                for table in tables:
                    self.csv_storage.create_backup(table)
                return True
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def save_financial_statement_data(self, symbol: str, statement_type: str, data: Dict[str, Any]) -> bool:
        """
        保存财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型 ('income', 'balance', 'cash')
            data: 财务报表数据
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建字段名和值
                fields = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key not in ['statement_type']:  # 排除statement_type，它作为表名的一部分
                        fields.append(key)
                        values.append(value)
                        placeholders.append('%s')
                
                # 构建SQL
                field_str = ', '.join(fields)
                placeholder_str = ', '.join(placeholders)
                
                # 使用INSERT IGNORE避免重复数据
                sql = f"""
                INSERT IGNORE INTO {table_name} ({field_str}) 
                VALUES ({placeholder_str})
                """
                
                cursor.execute(sql, values)
                
                # 记录处理日志
                report_date = data.get('reportdate', data.get('report_date', ''))
                log_sql = """
                INSERT IGNORE INTO financial_statements_log (symbol, statement_type, report_date, timestamp) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                cursor.execute(log_sql, (symbol, statement_type, report_date))
                
                conn.commit()
                logger.debug(f"保存{symbol}的{statement_type}报表数据成功")
                return True
                
        except Exception as e:
            logger.error(f"保存财务报表数据失败: {e}")
            return False
    
    def get_financial_statement_data(self, symbol: str, statement_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 证券代码
            statement_type: 报表类型
            limit: 限制返回条数
            
        Returns:
            List[Dict]: 财务报表数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建表名
                table_name = f"financial_{statement_type}"
                
                # 构建SQL
                sql = f"SELECT * FROM {table_name} WHERE symbol = %s ORDER BY reportdate DESC"
                
                if limit:
                    sql += f" LIMIT {limit}"
                
                cursor.execute(sql, (symbol,))
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表数据失败: {e}")
            return []
    
    def get_financial_statement_logs(self) -> List[Dict[str, Any]]:
        """
        获取财务报表处理日志
        
        Returns:
            List[Dict]: 日志数据列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                sql = """
                SELECT * FROM financial_statements_log 
                ORDER BY timestamp DESC 
                LIMIT 1000
                """
                
                cursor.execute(sql)
                result = cursor.fetchall()
                
                return result
                
        except Exception as e:
            logger.error(f"获取财务报表日志失败: {e}")
            return []