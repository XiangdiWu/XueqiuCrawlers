import json
import os
from datetime import datetime
from crawlers.base_crawler import BaseCrawler
from engine.logger import logger

class CompanyInfoCrawler(BaseCrawler):
    """公司基本信息爬虫"""
    
    def __init__(self, data_repository=None):
        super().__init__(data_repository)
        self.base_url = self.config['base_url']
        self.processed_symbols = set()  # 记录已处理的股票代码
        
    def _fetch_company_info(self, symbol):
        """获取公司信息"""
        url = (
            f"{self.base_url}/stock/f10/compinfo.json"
            f"?symbol={symbol}&page=1&size=4&_={self.get_timestamp()}"
        )
        
        try:
            response = self.make_request(url)
            data = response.json()
            
            compinfo = data.get('tqCompInfo', {})
            if not compinfo:
                self.logger.warning(f"未获取到公司信息: {symbol}")
                return None
            
            # 数据清洗和格式化
            company_data = {
                'compcode': symbol,
                'compname': self._clean_text(compinfo.get('compname', '')),
                'engname': self._clean_text(compinfo.get('engname', '')),
                'founddate': self._clean_date(compinfo.get('founddate', '')),
                'regcapital': self._clean_capital(compinfo.get('regcapital', '')),
                'chairman': self._clean_text(compinfo.get('chairman', '')),
                'manager': self._clean_text(compinfo.get('manager', '')),
                'leconstant': self._clean_text(compinfo.get('leconstant', '')),
                'accfirm': self._clean_text(compinfo.get('accfirm', '')),
                'regaddr': self._clean_text(compinfo.get('regaddr', '')),
                'officeaddr': self._clean_text(compinfo.get('officeaddr', '')),
                'compintro': self._clean_long_text(compinfo.get('compintro', '')),
                'bizscope': self._clean_long_text(compinfo.get('bizscope', '')),
                'majorbiz': self._clean_long_text(compinfo.get('majorbiz', '')),
                'compsname': self._clean_text(compinfo.get('compsname', '')),
                'region': self._clean_text(compinfo.get('region', '')),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return company_data
            
        except Exception as e:
            self.logger.error(f"解析公司信息失败 {symbol}: {e}")
            return None
    
    def _clean_text(self, text):
        """清洗文本数据"""
        if not text:
            return ''
        return str(text).replace('"', ' ').replace("'", ' ').strip()
    
    def _clean_long_text(self, text):
        """清洗长文本数据"""
        if not text:
            return ''
        # 移除引号和多余空白，保留换行
        cleaned = str(text).replace('"', ' ').replace("'", ' ')
        # 移除连续空白字符
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _clean_date(self, date_str):
        """清洗日期数据"""
        if not date_str:
            return ''
        # 移除引号和空白
        return str(date_str).replace('"', '').strip()
    
    def _clean_capital(self, capital_str):
        """清洗注册资本数据"""
        if not capital_str:
            return ''
        # 移除引号和空白，保留数字和单位
        return str(capital_str).replace('"', '').strip()
    
    def crawl_company_info(self, symbols=None):
        """爬取公司基本信息
        
        Args:
            symbols: 指定股票代码列表，为None则获取所有股票
        """
        self.logger.info("开始爬取公司基本信息...")
        
        if symbols is None:
            stock_symbols = self.data_repo.get_stock_symbols()
        else:
            stock_symbols = symbols
        
        total = len(stock_symbols)
        success_count = 0
        error_count = 0
        
        for i, symbol in enumerate(stock_symbols, 1):
            # 跳过已处理的股票
            if symbol in self.processed_symbols:
                self.logger.debug(f"跳过已处理的股票: {symbol}")
                continue
            
            self.logger.info(f"处理第{i}/{total}支股票: {symbol}")
            
            try:
                company_data = self._fetch_company_info(symbol)
                if company_data:
                    # 保存到数据仓库
                    success = self.data_repo.save_company_info(company_data)
                    if success:
                        success_count += 1
                        self.processed_symbols.add(symbol)
                        self.logger.info(f"✅ 公司信息保存成功: {symbol} {company_data.get('compsname', '')}")
                    else:
                        error_count += 1
                        self.logger.error(f"❌ 公司信息保存失败: {symbol}")
                else:
                    error_count += 1
                    self.logger.warning(f"⚠️ 未获取到公司信息: {symbol}")
                    
            except Exception as e:
                error_count += 1
                self.logger.error(f"❌ 获取公司信息失败 {symbol}: {e}")
            
            self.delay()
        
        self.logger.info(f"公司基本信息爬取完成 - 成功: {success_count}, 失败: {error_count}")
        return {
            'total': total,
            'success': success_count,
            'error': error_count
        }
    
    def crawl_company_info_by_code(self, symbol):
        """按证券代码获取单个公司信息"""
        self.logger.info(f"获取公司信息: {symbol}")
        
        try:
            company_data = self._fetch_company_info(symbol)
            if company_data:
                success = self.data_repo.save_company_info(company_data)
                if success:
                    self.logger.info(f"✅ 公司信息保存成功: {symbol} {company_data.get('compsname', '')}")
                    return company_data
                else:
                    self.logger.error(f"❌ 公司信息保存失败: {symbol}")
                    return None
            else:
                self.logger.warning(f"⚠️ 未获取到公司信息: {symbol}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ 获取公司信息失败 {symbol}: {e}")
            return None
    
    def crawl_company_info_batch(self, symbols, batch_size=50):
        """批量爬取公司信息
        
        Args:
            symbols: 股票代码列表
            batch_size: 批次大小
        """
        self.logger.info(f"批量爬取公司信息，共{len(symbols)}支股票，批次大小: {batch_size}")
        
        total_success = 0
        total_error = 0
        
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            self.logger.info(f"处理第{batch_num}/{total_batches}批次，{len(batch_symbols)}支股票")
            
            result = self.crawl_company_info(batch_symbols)
            total_success += result['success']
            total_error += result['error']
            
            # 批次间休息
            if i + batch_size < len(symbols):
                self.logger.info("批次间休息5秒...")
                import time
                time.sleep(5)
        
        self.logger.info(f"批量爬取完成 - 总成功: {total_success}, 总失败: {total_error}")
        return {
            'total': len(symbols),
            'success': total_success,
            'error': total_error
        }
    
    def get_company_info_by_symbol(self, symbol):
        """从存储中获取指定公司的信息"""
        try:
            if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                # CSV模式
                data = self.data_repo.csv_storage.read_from_csv('company_profile')
                for item in data:
                    if item.get('compcode') == symbol:
                        return item
                return None
            else:
                # 数据库模式
                sql = "SELECT * FROM comp WHERE compcode = %s"
                result = self.data_repo.db_manager.execute_query(sql, (symbol,))
                return result[0] if result else None
        except Exception as e:
            self.logger.error(f"查询公司信息失败 {symbol}: {e}")
            return None
    
    def update_company_info_by_symbol(self, symbol):
        """更新指定公司的信息"""
        self.logger.info(f"更新公司信息: {symbol}")
        return self.crawl_company_info_by_code(symbol)
    
    def export_company_info_to_csv(self, output_path=None, symbols=None):
        """导出公司信息到CSV文件
        
        Args:
            output_path: 输出文件路径，为None则使用默认路径
            symbols: 指定股票代码列表，为None则导出所有
        """
        try:
            import pandas as pd
            
            if symbols is None:
                # 获取所有公司信息
                if hasattr(self.data_repo, 'csv_storage') and self.data_repo.csv_storage:
                    data = self.data_repo.csv_storage.read_from_csv('company_profile')
                else:
                    # 数据库模式
                    sql = "SELECT * FROM comp ORDER BY compcode"
                    data = self.data_repo.db_manager.execute_query(sql)
            else:
                # 获取指定公司信息
                data = []
                for symbol in symbols:
                    info = self.get_company_info_by_symbol(symbol)
                    if info:
                        data.append(info)
            
            if not data:
                self.logger.warning("没有找到公司信息数据")
                return False
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 设置输出路径
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"data/company_info_export_{timestamp}.csv"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 导出到CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"✅ 公司信息导出成功: {output_path} ({len(data)}条记录)")
            return True
            
        except Exception as e:
            self.logger.error(f"导出公司信息失败: {e}")
            return False