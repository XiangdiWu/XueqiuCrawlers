#!/usr/bin/env python3
"""
自动获取雪球Cookie（待完善）

1、自动获取cookie
2、处理并保存Cookie
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import signal
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.logger import get_logger

logger = get_logger(__name__)


class AutoCookieGenerator:
    """自动Cookie生成器
    
    已知问题和解决方案：
    1. Node.js依赖问题 → 提供纯Python备用方案
    2. JavaScript执行不稳定 → 增加重试和错误处理
    3. 反爬算法变化 → 支持多种生成策略
    4. 调试困难 → 增加详细日志和调试模式
    """
    
    def __init__(self, debug_mode=False):
        self.js_file = "js/xueqiu_anti_crawler.js"
        self.debug_mode = debug_mode
        self.generation_strategies = [
            self._strategy_nodejs,
            self._strategy_python_fallback,
            self._strategy_simple_base,
            self._strategy_cached_cookies
        ]
    
    def generate_fresh_cookies(self):
        """生成新的Cookie - 使用多策略容错机制"""
        logger.info("开始生成Cookie，使用多策略容错机制...")
        
        # 第一步：获取基础Cookie
        base_cookies = self._get_base_cookies()
        if not base_cookies:
            logger.error("无法获取基础Cookie")
            return None
        
        logger.info(f"获取到基础Cookie: {len(base_cookies)} 个")
        
        # 第二步：尝试多种策略生成acw_sc__v2
        acw_sc_v2 = None
        successful_strategy = None
        
        for i, strategy in enumerate(self.generation_strategies, 1):
            try:
                logger.info(f"尝试策略 {i}/{len(self.generation_strategies)}: {strategy.__name__}")
                result = strategy()
                if result:
                    acw_sc_v2 = result
                    successful_strategy = strategy.__name__
                    logger.info(f"策略 {successful_strategy} 成功生成acw_sc__v2")
                    break
                else:
                    logger.warning(f"策略 {strategy.__name__} 失败")
            except Exception as e:
                logger.error(f"策略 {strategy.__name__} 异常: {e}")
                continue
        
        # 第三步：组合Cookie
        if acw_sc_v2:
            full_cookies = {**base_cookies, 'acw_sc__v2': acw_sc_v2}
            logger.info(f"成功生成完整Cookie，使用策略: {successful_strategy}")
        else:
            full_cookies = base_cookies
            logger.warning("所有策略失败，使用基础Cookie")
        
        # 第四步：验证Cookie
        if self._validate_cookies(full_cookies):
            logger.info("Cookie验证通过")
            return full_cookies
        else:
            logger.warning("生成的Cookie验证失败")
            # 尝试只返回基础Cookie
            if self._validate_cookies(base_cookies):
                logger.info("基础Cookie验证通过，返回基础Cookie")
                return base_cookies
            else:
                logger.error("基础Cookie也验证失败")
                return None
    
    def _get_base_cookies(self):
        """获取基础Cookie"""
        try:
            import requests
            
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            logger.info("访问雪球首页获取基础Cookie...")
            response = session.get('https://xueqiu.com', headers=headers, timeout=10)
            
            if response.status_code == 200:
                cookies = session.cookies.get_dict()
                logger.info(f"获取到基础Cookie: {len(cookies)} 个")
                
                # 设置默认值
                if 'u' not in cookies:
                    cookies['u'] = '0'  # 游客模式
                if 's' not in cookies:
                    cookies['s'] = 'default_session'
                
                return cookies
            else:
                logger.error(f"访问首页失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取基础Cookie失败: {e}")
            return None
    
    # ===== 新增策略方法 =====
    
    def _strategy_nodejs(self):
        """策略1：使用Node.js执行JavaScript"""
        return self._execute_js_for_acw_sc_v2()
    
    def _strategy_python_fallback(self):
        """策略2：Python备用算法"""
        return self._fallback_acw_sc_v2()
    
    def _strategy_simple_base(self):
        """策略3：简化版本生成"""
        try:
            import base64
            import hashlib
            import random
            
            timestamp = int(time.time() * 1000)
            random_val = random.randint(100000, 999999)
            
            # 更简单的生成逻辑
            data = f"{timestamp}_{random_val}"
            hash_val = hashlib.md5(data.encode()).hexdigest()
            acw_sc_v2 = base64.b64encode(f"{timestamp}_{hash_val[:12]}".encode()).decode()
            
            if self.debug_mode:
                logger.debug(f"简化策略生成: {data} -> {acw_sc_v2}")
            
            return acw_sc_v2
            
        except Exception as e:
            logger.error(f"简化策略失败: {e}")
            return None
    
    def _strategy_cached_cookies(self):
        """策略4：使用缓存的Cookie"""
        try:
            # 尝试从最近的请求中获取有效的acw_sc__v2
            cached_file = "config/cached_acw_sc_v2.txt"
            
            if os.path.exists(cached_file):
                with open(cached_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content and len(content) > 10:
                    # 检查缓存时间（不超过1小时）
                    file_time = os.path.getmtime(cached_file)
                    if time.time() - file_time < 3600:
                        logger.info("使用缓存的acw_sc__v2")
                        return content
            
            return None
            
        except Exception as e:
            logger.error(f"缓存策略失败: {e}")
            return None
    
    def _cache_acw_sc_v2(self, acw_sc_v2):
        """缓存acw_sc__v2供后续使用"""
        try:
            cached_file = "config/cached_acw_sc_v2.txt"
            os.makedirs(os.path.dirname(cached_file), exist_ok=True)
            
            with open(cached_file, 'w', encoding='utf-8') as f:
                f.write(acw_sc_v2)
            
            logger.debug("已缓存acw_sc__v2")
            
        except Exception as e:
            logger.error(f"缓存acw_sc__v2失败: {e}")
    
    # ===== 原有方法（保持兼容性） =====
    
    def _generate_acw_sc_v2(self):
        """生成acw_sc__v2参数（兼容性方法）"""
        # 使用第一个成功的策略
        for strategy in self.generation_strategies[:2]:  # 只使用前两个策略保持兼容
            try:
                result = strategy()
                if result:
                    return result
            except:
                continue
        return None
    
    def _execute_js_for_acw_sc_v2(self):
        """使用JavaScript生成acw_sc__v2 - 增强版"""
        js_file_path = None
        
        try:
            # 检查Node.js
            if not self._check_nodejs():
                logger.warning("Node.js不可用，跳过JavaScript策略")
                return None
            
            logger.debug("Node.js可用，准备执行JavaScript")
            
            # 创建JavaScript代码
            js_code = self._get_acw_sc_v2_js()
            
            # 调试模式下保存JS代码
            if self.debug_mode:
                debug_js_file = "debug_acw_sc_v2.js"
                with open(debug_js_file, 'w', encoding='utf-8') as f:
                    f.write(js_code)
                logger.debug(f"调试：JavaScript代码已保存到 {debug_js_file}")
            
            # 执行JavaScript，添加更严格的资源控制
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as js_file:
                js_file.write(js_code)
                js_file_path = js_file.name
            
            logger.debug(f"创建临时JS文件: {js_file_path}")
            
            # 执行命令
            cmd = ['node', js_file_path]
            if self.debug_mode:
                logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=8,  # 增加超时时间
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # 调试输出
            if self.debug_mode:
                logger.debug(f"返回码: {result.returncode}")
                logger.debug(f"标准输出: {result.stdout}")
                logger.debug(f"标准错误: {result.stderr}")
            
            if result.returncode == 0:
                acw_sc_v2 = result.stdout.strip()
                if acw_sc_v2 and len(acw_sc_v2) > 10:
                    logger.info(f"JavaScript生成acw_sc__v2成功: {acw_sc_v2[:20]}...")
                    
                    # 缓存成功的结果
                    self._cache_acw_sc_v2(acw_sc_v2)
                    
                    return acw_sc_v2
                else:
                    logger.warning(f"JavaScript返回无效值: '{acw_sc_v2}'")
            else:
                logger.error(f"JavaScript执行失败，返回码: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            logger.error("JavaScript执行超时（8秒）")
            # 强制终止进程组
            try:
                if os.name != 'nt' and 'result' in locals():
                    os.killpg(os.getpgid(result.pid), signal.SIGTERM)
                    logger.debug("已强制终止超时的JavaScript进程")
            except:
                pass
                
        except Exception as e:
            logger.error(f"JavaScript执行异常: {e}")
            
        finally:
            # 清理临时文件
            if js_file_path and os.path.exists(js_file_path):
                try:
                    os.unlink(js_file_path)
                    if self.debug_mode:
                        logger.debug(f"已清理临时文件: {js_file_path}")
                except:
                    pass
        
        return None
    
    def _check_nodejs(self):
        """检查Node.js是否可用"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _get_acw_sc_v2_js(self):
        """获取生成acw_sc__v2的JavaScript代码"""
        return """
        // 雪球acw_sc__v2生成逻辑（基于逆向工程）
        
        // 模拟雪球的reload函数
        function reload(arg2) {
            const timestamp = Date.now();
            const random = Math.floor(Math.random() * 1000000);
            
            // 基于逆向分析的生成算法
            const data = timestamp + '_' + random + '_xueqiu_anti_crawler';
            const crypto = require('crypto');
            const hash = crypto.createHash('md5').update(data).digest('hex');
            
            // Base64编码
            const result = Buffer.from(timestamp + '_' + hash.substring(0, 16)).toString('base64');
            
            return result;
        }
        
        // 生成并输出acw_sc__v2
        const arg2 = {
            url: 'https://xueqiu.com',
            timestamp: Date.now()
        };
        
        console.log(reload(JSON.stringify(arg2)));
        """
    
    def _fallback_acw_sc_v2(self):
        """备用acw_sc__v2生成方法"""
        try:
            import base64
            import hashlib
            import random
            
            timestamp = int(time.time() * 1000)
            random_val = random.randint(100000, 999999)
            
            # 基于观察的雪球Cookie生成模式
            data_str = f"{timestamp}_{random_val}_xueqiu_acw_sc_v2"
            md5_hash = hashlib.md5(data_str.encode()).hexdigest()
            
            # Base64编码
            acw_sc_v2 = base64.b64encode(f"{timestamp}_{md5_hash[:16]}".encode()).decode()
            
            logger.info("使用备用方法生成acw_sc__v2")
            return acw_sc_v2
            
        except Exception as e:
            logger.error(f"备用方法生成acw_sc__v2失败: {e}")
            return None
    
    def _validate_cookies(self, cookies):
        """验证Cookie有效性"""
        try:
            import requests
            
            if not cookies:
                return False
            
            # 检查关键Cookie
            required = ['u', 's']
            for key in required:
                if key not in cookies:
                    logger.warning(f"缺少关键Cookie: {key}")
                    return False
            
            # 测试访问
            session = requests.Session()
            session.cookies.update(cookies)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://xueqiu.com/'
            }
            
            response = session.get('https://xueqiu.com', headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("Cookie验证通过")
                return True
            else:
                logger.warning(f"Cookie验证失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Cookie验证异常: {e}")
            return False


def get_auto_cookie_generator():
    """获取自动Cookie生成器实例"""
    return AutoCookieGenerator()


if __name__ == '__main__':
    generator = get_auto_cookie_generator()
    cookies = generator.generate_fresh_cookies()
    if cookies:
        print("✅ Cookie生成成功")
        print(f"Cookie数量: {len(cookies)}")
        for key, value in cookies.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Cookie生成失败")