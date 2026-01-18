"""
vnPy集成模块
提供vnPy数据接口的封装，支持期货数据获取
"""
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta


def get_vnpy_status() -> Dict[str, Any]:
    """
    检查vnPy是否可用
    
    Returns:
        {
            'available': bool,
            'modules': {
                'database': bool,  # 数据库模块是否可用
                'event': bool,    # 事件模块是否可用
                ...
            }
        }
    """
    status = {
        'available': False,
        'modules': {}
    }
    
    try:
        import vnpy
        status['available'] = True
        status['version'] = getattr(vnpy, '__version__', 'unknown')
        
        # 检查常用模块
        modules_to_check = [
            'vnpy.trader.database',
            'vnpy.trader.engine',
            'vnpy.trader.object',
            'vnpy.trader.constant',
        ]
        
        for module_name in modules_to_check:
            try:
                __import__(module_name)
                status['modules'][module_name] = True
            except ImportError:
                status['modules'][module_name] = False
                
    except ImportError:
        status['available'] = False
        status['error'] = 'vnPy未安装'
    
    return status


def fetch_futures_data_from_vnpy(
    symbol: str,
    exchange: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = "d"
) -> Optional[pd.DataFrame]:
    """
    从vnPy数据库获取期货K线数据
    
    Args:
        symbol: 合约代码，如 "rb2501"
        exchange: 交易所，如 "SHFE"
        start_date: 开始日期
        end_date: 结束日期
        interval: K线周期，'d'表示日线，'1m'表示1分钟线
    
    Returns:
        DataFrame，包含：datetime, open, high, low, close, volume, open_interest
        如果vnPy不可用，返回None
    """
    try:
        from vnpy.trader.database import get_database
        from vnpy.trader.object import BarData
        from vnpy.trader.constant import Exchange, Interval
        
        # 获取数据库实例
        try:
            database = get_database()
        except ModuleNotFoundError as db_error:
            if 'vnpy_sqlite' in str(db_error) or 'sqlite' in str(db_error).lower():
                print(f"[vnPy] 数据库驱动缺失: {db_error}")
                print(f"[vnPy] 提示: 需要安装 vnpy_sqlite 模块才能使用vnPy数据库功能")
                print(f"[vnPy] 安装命令: pip install vnpy_sqlite")
                print(f"[vnPy] 或者使用其他数据源（如akshare）")
                return None
            else:
                raise
        
        # 转换交易所字符串为Exchange枚举
        exchange_map = {
            'SHFE': Exchange.SHFE,
            'DCE': Exchange.DCE,
            'CZCE': Exchange.CZCE,
            'CFFEX': Exchange.CFFEX,
            'INE': Exchange.INE,
        }
        exchange_enum = exchange_map.get(exchange.upper(), Exchange.SHFE)
        
        # 转换周期字符串为Interval枚举
        # 不同版本的vnPy可能使用不同的枚举值，需要动态检测
        def get_interval_enum(interval_str: str):
            """安全地获取Interval枚举值"""
            interval_lower = interval_str.lower()
            
            # 尝试不同的可能枚举值名称
            candidates = {
                'd': ['DAILY', 'DAY'],
                '1m': ['MINUTE', 'MIN'],
                '5m': ['MINUTE_5', 'MIN_5', 'FIVE_MINUTE', 'FIVE_MIN'],
                '15m': ['MINUTE_15', 'MIN_15', 'FIFTEEN_MINUTE', 'FIFTEEN_MIN'],
                '30m': ['MINUTE_30', 'MIN_30', 'THIRTY_MINUTE', 'THIRTY_MIN'],
                '1h': ['HOUR', 'H', 'HOURLY'],
            }
            
            # 获取候选枚举名称
            enum_names = candidates.get(interval_lower, ['DAILY', 'DAY'])
            
            # 尝试每个候选名称
            for enum_name in enum_names:
                if hasattr(Interval, enum_name):
                    return getattr(Interval, enum_name)
            
            # 如果都找不到，返回默认的日线
            if hasattr(Interval, 'DAILY'):
                return Interval.DAILY
            elif hasattr(Interval, 'DAY'):
                return Interval.DAY
            else:
                # 打印所有可用的Interval属性以便调试
                available_intervals = [attr for attr in dir(Interval) if not attr.startswith('_') and attr.isupper()]
                print(f"[vnPy] 警告: 无法找到对应的Interval枚举值 '{interval_str}'")
                print(f"[vnPy] 可用的Interval值: {available_intervals}")
                # 尝试使用第一个可用的值
                if available_intervals:
                    return getattr(Interval, available_intervals[0])
                else:
                    raise ValueError(f"无法确定Interval枚举值，interval={interval_str}")
        
        interval_enum = get_interval_enum(interval)
        
        # 设置默认日期范围
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        # 从数据库加载数据
        print(f"[vnPy] 尝试从数据库加载数据: symbol={symbol}, exchange={exchange}, interval={interval}, start={start_date}, end={end_date}")
        bars = database.load_bar_data(
            symbol=symbol,
            exchange=exchange_enum,
            interval=interval_enum,
            start=start_date,
            end=end_date
        )
        
        if not bars:
            print(f"[vnPy] 数据库中没有找到数据，可能数据库为空或需要先导入数据")
            print(f"[vnPy] 提示: vnPy需要先配置数据库并导入历史数据才能使用")
            return None
        
        print(f"[vnPy] 成功从数据库加载 {len(bars)} 条K线数据")
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'close': bar.close_price,
                'volume': bar.volume,
                'open_interest': bar.open_interest,
            })
        
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime').reset_index(drop=True)
        
        return df
        
    except ImportError as e:
        print(f"[vnPy] 导入失败，vnPy可能未正确安装: {e}")
        import traceback
        print(f"[vnPy] 导入错误详情: {traceback.format_exc()}")
        return None
    except Exception as e:
        print(f"[vnPy] 获取期货数据失败: {e}")
        import traceback
        print(f"[vnPy] 错误详情: {traceback.format_exc()}")
        return None


def get_futures_contract_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    获取期货合约信息
    
    Args:
        symbol: 合约代码，如 "rb2501"
    
    Returns:
        {
            'symbol': str,
            'product_code': str,  # 品种代码，如 "rb"
            'contract_month': str,  # 合约月份，如 "2501"
            'exchange': str,  # 交易所
            'name': str,  # 合约名称
            'multiplier': int,  # 合约乘数
            'margin_rate': float,  # 保证金率
        }
    """
    # 期货品种到交易所的映射
    product_exchange_map = {
        'rb': 'SHFE',  # 螺纹钢
        'hc': 'SHFE',  # 热卷
        'cu': 'SHFE',  # 铜
        'al': 'SHFE',  # 铝
        'zn': 'SHFE',  # 锌
        'i': 'DCE',   # 铁矿石
        'j': 'DCE',   # 焦炭
        'jm': 'DCE',  # 焦煤
        'c': 'DCE',   # 玉米
        'cs': 'DCE',  # 玉米淀粉
        'CF': 'CZCE', # 棉花
        'SR': 'CZCE', # 白糖
        'TA': 'CZCE', # PTA
        'IF': 'CFFEX', # 沪深300
        'IC': 'CFFEX', # 中证500
        'IH': 'CFFEX', # 上证50
        'sc': 'INE',  # 原油
    }
    
    # 期货品种到合约乘数的映射（示例，实际需要查询）
    product_multiplier_map = {
        'rb': 10,  # 螺纹钢：10吨/手
        'hc': 10,  # 热卷：10吨/手
        'cu': 5,   # 铜：5吨/手
        'al': 5,   # 铝：5吨/手
        'zn': 5,   # 锌：5吨/手
        'i': 100,  # 铁矿石：100吨/手
        'j': 100,  # 焦炭：100吨/手
        'jm': 60,  # 焦煤：60吨/手
        'c': 10,   # 玉米：10吨/手
        'cs': 10,  # 玉米淀粉：10吨/手
        'CF': 5,   # 棉花：5吨/手
        'SR': 10,  # 白糖：10吨/手
        'TA': 5,   # PTA：5吨/手
        'IF': 300, # 沪深300：300点/手
        'IC': 200, # 中证500：200点/手
        'IH': 300, # 上证50：300点/手
        'sc': 1000, # 原油：1000桶/手
    }
    
    # 解析合约代码
    if len(symbol) < 4:
        return None
    
    # 提取品种代码和月份
    product_code = symbol[:2].lower()
    contract_month = symbol[2:]
    
    # 处理大写品种代码（如CF、SR、TA）
    if symbol[:2].isupper():
        product_code = symbol[:2]
        contract_month = symbol[2:]
    
    exchange = product_exchange_map.get(product_code, 'SHFE')
    multiplier = product_multiplier_map.get(product_code, 10)
    
    # 品种名称映射
    product_name_map = {
        'rb': '螺纹钢',
        'hc': '热卷',
        'cu': '铜',
        'al': '铝',
        'zn': '锌',
        'i': '铁矿石',
        'j': '焦炭',
        'jm': '焦煤',
        'c': '玉米',
        'cs': '玉米淀粉',
        'CF': '棉花',
        'SR': '白糖',
        'TA': 'PTA',
        'IF': '沪深300',
        'IC': '中证500',
        'IH': '上证50',
        'sc': '原油',
    }
    
    product_name = product_name_map.get(product_code, product_code)
    name = f"{product_name}{contract_month}"
    
    return {
        'symbol': symbol,
        'product_code': product_code,
        'contract_month': contract_month,
        'exchange': exchange,
        'name': name,
        'multiplier': multiplier,
        'margin_rate': 0.10,  # 默认10%，实际需要查询
    }

