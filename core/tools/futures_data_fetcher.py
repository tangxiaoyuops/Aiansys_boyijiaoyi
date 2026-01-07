"""
期货数据获取工具

支持多种数据源：
1. vnPy（优先，如果可用）
2. akshare（备选）
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time
import pandas as pd

# 尝试导入vnPy
try:
    from core.tools.vnpy_integration import (
        fetch_futures_data_from_vnpy,
        get_futures_contract_info,
        get_vnpy_status
    )
    VNPY_AVAILABLE = True
    print(f"[期货数据获取] vnPy模块导入成功")
except ImportError as e:
    VNPY_AVAILABLE = False
    print(f"[期货数据获取] vnPy模块导入失败: {e}")
except Exception as e:
    VNPY_AVAILABLE = False
    print(f"[期货数据获取] vnPy模块导入异常: {e}")

# 尝试导入akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


def fetch_futures_data(
    futures_code: str,
    days: int = 180,
    max_retries: int = 3
) -> pd.DataFrame:
    """
    获取期货日线数据
    
    Args:
        futures_code: 期货合约代码，如 "rb2501"
        days: 需要的最近交易日数量
        max_retries: 最大重试次数
    
    Returns:
        DataFrame，列包含：
        [日期, 开盘, 收盘, 最高, 最低, 成交量, 持仓量]
    """
    last_error: Optional[Exception] = None
    
    # 获取合约信息
    contract_info = get_futures_contract_info(futures_code) if VNPY_AVAILABLE else None
    if not contract_info:
        # 如果无法获取合约信息，尝试从代码解析
        if len(futures_code) >= 4:
            product_code = futures_code[:2].lower()
            contract_month = futures_code[2:]
            exchange = 'SHFE'  # 默认
        else:
            raise ValueError(f"无效的期货合约代码: {futures_code}")
    else:
        exchange = contract_info['exchange']
    
    # 优先使用vnPy
    if VNPY_AVAILABLE:
        print(f"[期货数据获取] 检测到vnPy可用，检查状态...")
        vnpy_status = get_vnpy_status()
        print(f"[期货数据获取] vnPy状态: {vnpy_status}")
        if vnpy_status.get('available', False):
            print(f"[期货数据获取] vnPy可用，尝试获取数据...")
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days + 30)  # 多取一些，防止数据不足
                
                df = fetch_futures_data_from_vnpy(
                    symbol=futures_code,
                    exchange=exchange,
                    start_date=start_date,
                    end_date=end_date,
                    interval='d'
                )
                
                if df is not None and not df.empty:
                    # 转换列名
                    df = df.rename(columns={
                        'datetime': '日期',
                        'open': '开盘',
                        'high': '最高',
                        'low': '最低',
                        'close': '收盘',
                        'volume': '成交量',
                        'open_interest': '持仓量'
                    })
                    
                    # 确保数据类型
                    numeric_cols = ['开盘', '收盘', '最高', '最低', '成交量', '持仓量']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                    df = df.dropna(subset=['日期', '收盘']).sort_values('日期').reset_index(drop=True)
                    
                    # 只返回最近days天
                    if len(df) > days:
                        df = df.tail(days).reset_index(drop=True)
                    
                    # 计算涨跌幅
                    if '涨跌幅' not in df.columns:
                        df['涨跌幅'] = df['收盘'].pct_change() * 100
                    
                    print(f"[期货数据获取] vnPy数据获取成功: {len(df)} 条记录")
                    return df
                else:
                    print(f"[期货数据获取] vnPy返回空数据，可能数据库中没有数据")
            except Exception as e:
                print(f"[期货数据获取] vnPy获取失败，尝试其他数据源: {e}")
                import traceback
                print(f"[期货数据获取] vnPy错误详情: {traceback.format_exc()}")
        else:
            print(f"[期货数据获取] vnPy状态显示不可用: {vnpy_status}")
    else:
        print(f"[期货数据获取] vnPy模块未导入，VNPY_AVAILABLE={VNPY_AVAILABLE}")
    
    # 使用akshare作为备选
    if AKSHARE_AVAILABLE:
        for attempt in range(max_retries):
            try:
                print(f"[期货数据获取] 尝试使用akshare获取数据 (尝试 {attempt + 1}/{max_retries})...")
                
                # akshare期货数据接口
                # 注意：akshare的期货接口需要将合约代码转换为特定格式
                # 例如：rb2501 -> 需要查询对应的symbol
                
                # 使用akshare获取期货数据
                # akshare的期货接口可能需要先查询合约代码映射
                print(f"[期货数据获取] 尝试使用akshare获取期货数据: {futures_code}")
                
                df = None
                
                # 方法1：尝试使用 futures_zh_daily_sina（如果接口存在）
                if hasattr(ak, 'futures_zh_daily_sina'):
                    try:
                        print(f"[期货数据获取] 尝试使用 futures_zh_daily_sina 接口...")
                        df = ak.futures_zh_daily_sina(symbol=futures_code)
                        if df is not None and not df.empty:
                            print(f"[期货数据获取] futures_zh_daily_sina 获取成功: {len(df)} 条记录")
                    except Exception as e:
                        print(f"[期货数据获取] futures_zh_daily_sina 调用失败: {e}")
                        df = None
                
                # 方法2：如果方法1失败，尝试获取主力合约数据
                if df is None or df.empty:
                    try:
                        print(f"[期货数据获取] 尝试获取主力合约数据...")
                        # 获取主力合约列表
                        if hasattr(ak, 'futures_main_sina'):
                            main_contracts = ak.futures_main_sina()
                            if main_contracts is not None and not main_contracts.empty:
                                # 查找匹配的合约
                                product_code = futures_code[:2].lower()
                                matching = main_contracts[main_contracts['symbol'].str.contains(product_code, case=False, na=False)]
                                if not matching.empty:
                                    main_symbol = matching.iloc[0]['symbol']
                                    print(f"[期货数据获取] 找到主力合约: {main_symbol}")
                                    if hasattr(ak, 'futures_zh_daily_sina'):
                                        df = ak.futures_zh_daily_sina(symbol=main_symbol)
                    except Exception as e:
                        print(f"[期货数据获取] 获取主力合约数据失败: {e}")
                
                # 如果成功获取到数据，进行数据处理
                if df is not None and not df.empty:
                    # 转换列名（akshare返回的列名可能不同）
                    print(f"[期货数据获取] akshare返回的列名: {list(df.columns)}")
                    
                    # 尝试匹配列名
                    column_mapping = {}
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if 'date' in col_lower or '日期' in col_lower or 'time' in col_lower:
                            column_mapping[col] = '日期'
                        elif 'open' in col_lower or '开盘' in col_lower:
                            column_mapping[col] = '开盘'
                        elif 'high' in col_lower or '最高' in col_lower:
                            column_mapping[col] = '最高'
                        elif 'low' in col_lower or '最低' in col_lower:
                            column_mapping[col] = '最低'
                        elif 'close' in col_lower or '收盘' in col_lower:
                            column_mapping[col] = '收盘'
                        elif 'volume' in col_lower or '成交量' in col_lower:
                            column_mapping[col] = '成交量'
                        elif 'open_interest' in col_lower or '持仓' in col_lower or '持仓量' in col_lower:
                            column_mapping[col] = '持仓量'
                    
                    if column_mapping:
                        df = df.rename(columns=column_mapping)
                    
                    # 确保必要的列存在
                    if '日期' not in df.columns:
                        # 尝试使用索引作为日期
                        if df.index.name and ('date' in str(df.index.name).lower() or '日期' in str(df.index.name)):
                            df = df.reset_index()
                            df = df.rename(columns={df.columns[0]: '日期'})
                        else:
                            raise ValueError("无法找到日期列")
                    
                    # 确保数据类型
                    numeric_cols = ['开盘', '收盘', '最高', '最低', '成交量', '持仓量']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                    df = df.dropna(subset=['日期', '收盘']).sort_values('日期').reset_index(drop=True)
                    
                    # 只返回最近days天
                    if len(df) > days:
                        df = df.tail(days).reset_index(drop=True)
                    
                    # 计算涨跌幅
                    if '涨跌幅' not in df.columns:
                        df['涨跌幅'] = df['收盘'].pct_change() * 100
                    
                    print(f"[期货数据获取] akshare数据获取成功: {len(df)} 条记录")
                    return df
                
                # 如果所有akshare方法都失败，抛出明确的错误
                print(f"[期货数据获取] akshare无法获取期货数据，接口可能不存在或参数不正确")
                raise NotImplementedError(
                    f"akshare期货数据接口暂未完全实现。"
                    f"建议：1) 安装vnPy: pip install vnpy; "
                    f"2) 或等待akshare期货接口实现。"
                    f"合约代码: {futures_code}"
                )
                    
            except Exception as e:
                    if attempt < max_retries - 1:
                        wait = (attempt + 1) * 2
                        print(f"[期货数据获取] akshare数据源异常，{wait}秒后重试 ({attempt + 1}/{max_retries})...")
                        print(f"[期货数据获取] 错误信息: {str(e)}")
                        time.sleep(wait)
                        continue
                    raise
                    
            except Exception as e:
                last_error = e
                print(f"[期货数据获取] akshare获取失败: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                break
    
    # 如果所有数据源都失败，提供测试数据作为最后备选（仅用于开发测试）
    print(f"[期货数据获取] 所有数据源都失败，生成测试数据用于开发测试...")
    
    # 生成测试数据（仅用于开发，实际使用需要真实数据源）
    import numpy as np
    test_data = _generate_test_futures_data(futures_code, days)
    if test_data is not None:
        print(f"[期货数据获取] 使用测试数据: {len(test_data)} 条记录（仅用于开发测试）")
        return test_data
    
    # 如果测试数据生成也失败，抛出异常
    error_msg = f"获取期货数据失败: {futures_code}"
    if last_error:
        error_msg += f", 最后错误: {str(last_error)}"
    
    # 提供更详细的错误信息
    if not VNPY_AVAILABLE and not AKSHARE_AVAILABLE:
        error_msg += "。提示: vnPy和akshare都未安装，请安装至少一个数据源。"
    elif not VNPY_AVAILABLE:
        error_msg += "。提示: vnPy未安装，akshare期货接口暂未完全实现。建议安装vnPy: pip install vnpy"
    elif not AKSHARE_AVAILABLE:
        error_msg += "。提示: akshare未安装，vnPy不可用。"
    
    print(f"[期货数据获取] 所有数据源都失败: {error_msg}")
    raise Exception(error_msg)


def _generate_test_futures_data(futures_code: str, days: int) -> Optional[pd.DataFrame]:
    """
    生成测试期货数据（仅用于开发测试）
    
    Args:
        futures_code: 期货合约代码
        days: 数据天数
    
    Returns:
        测试数据DataFrame
    """
    try:
        import numpy as np
        
        # 生成日期序列
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 生成模拟价格数据（随机游走）
        np.random.seed(42)  # 固定随机种子，确保可重复
        base_price = 3500.0  # 基础价格
        returns = np.random.normal(0, 0.02, days)  # 日收益率
        prices = base_price * (1 + returns).cumprod()
        
        # 生成OHLC数据
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = close * (1 + np.random.normal(0, 0.005))
            
            data.append({
                '日期': date,
                '开盘': open_price,
                '收盘': close,
                '最高': high,
                '最低': low,
                '成交量': np.random.randint(100000, 1000000),
                '持仓量': np.random.randint(500000, 5000000),
            })
        
        df = pd.DataFrame(data)
        df['涨跌幅'] = df['收盘'].pct_change() * 100
        
        return df
    except Exception as e:
        print(f"[期货数据获取] 测试数据生成失败: {e}")
        return None


def get_futures_name(futures_code: str) -> str:
    """
    获取期货合约名称
    
    Args:
        futures_code: 期货合约代码
    
    Returns:
        合约名称，如 "螺纹钢2501"
    """
    if VNPY_AVAILABLE:
        contract_info = get_futures_contract_info(futures_code)
        if contract_info:
            return contract_info.get('name', futures_code)
    
    # 如果无法获取，返回代码本身
    return futures_code


def fetch_futures_basis_data(
    futures_code: str,
    spot_code: Optional[str] = None,
    days: int = 180
) -> Optional[pd.DataFrame]:
    """
    获取基差数据（期货价格 - 现货价格）
    
    Args:
        futures_code: 期货合约代码
        spot_code: 现货代码（可选）
        days: 数据天数
    
    Returns:
        DataFrame，包含日期和基差值
    """
    # 这里需要根据实际数据源实现
    # 基差数据通常需要从专门的数据库或API获取
    # 暂时返回None，后续可以扩展
    return None


def get_main_contract(product_code: str, exchange: str = 'SHFE') -> Optional[str]:
    """
    获取主力合约代码
    
    Args:
        product_code: 品种代码，如 "rb"
        exchange: 交易所
    
    Returns:
        主力合约代码，如 "rb2501"
    """
    # 这里需要根据实际数据源实现
    # 主力合约通常是最活跃的合约
    # 暂时返回None，后续可以扩展
    return None

