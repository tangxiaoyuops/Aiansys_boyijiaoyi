"""
数据获取工具

支持多种数据源：
1. vnPy（优先，如果可用）- 本地数据库，数据质量好，速度快
2. akshare（备选）- 东方财富接口，实时获取

提供 fetch_stock_data / get_stock_name 给分析流程使用
"""

from datetime import datetime, timedelta
from typing import Optional
import time

import pandas as pd

# 尝试导入vnPy
try:
    from core.tools.vnpy_integration import (
        fetch_stock_data_from_vnpy,
        get_stock_info_from_vnpy,
        get_vnpy_status
    )
    VNPY_AVAILABLE = True
except ImportError:
    VNPY_AVAILABLE = False

# 尝试导入akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


def fetch_stock_data(stock_code: str, days: int = 180, max_retries: int = 3) -> pd.DataFrame:
    """
    获取股票日线数据（前复权），支持多数据源：
    1. 优先使用 vnPy（本地数据库，速度快，数据质量好）
    2. 备选 akshare（实时获取，但可能受网络影响）

    Args:
        stock_code: 6 位股票代码
        days: 需要的最近交易日数量（最终返回长度）
        max_retries: 最大重试次数

    Returns:
        DataFrame，列包含：
        [日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率]
    """
    last_error: Optional[Exception] = None
    
    # 优先使用vnPy（如果可用）
    if VNPY_AVAILABLE:
        try:
            print(f"[数据获取] 尝试使用vnPy获取股票数据: {stock_code}")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=max(days * 2, 365))  # 多获取一些，确保有足够数据
            
            df_vnpy = fetch_stock_data_from_vnpy(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
                interval="d"
            )
            
            if df_vnpy is not None and not df_vnpy.empty:
                print(f"[数据获取] vnPy数据获取成功: {len(df_vnpy)} 条记录")
                
                # 转换为标准格式
                df = df_vnpy.copy()
                df.columns = ['日期', '开盘', '最高', '最低', '收盘', '成交量']
                
                # 添加缺失的列（vnPy可能没有这些字段）
                df['成交额'] = df['成交量'] * df['收盘']  # 估算成交额
                df['振幅'] = ((df['最高'] - df['最低']) / df['收盘'].shift(1)) * 100
                df['涨跌幅'] = df['收盘'].pct_change() * 100
                df['涨跌额'] = df['收盘'].diff()
                df['换手率'] = 0.0  # vnPy可能没有换手率数据
                
                # 确保日期列格式正确
                if '日期' in df.columns:
                    df['日期'] = pd.to_datetime(df['日期'], errors="coerce")
                elif 'datetime' in df.columns:
                    df['日期'] = pd.to_datetime(df['datetime'], errors="coerce")
                    df = df.drop(columns=['datetime'])
                
                # 排序并截取最近days天
                df = df.dropna(subset=["日期", "收盘"]).sort_values("日期").reset_index(drop=True)
                if days and days > 0 and len(df) > days:
                    df = df.tail(days).reset_index(drop=True)
                
                # 重新排列列顺序
                df = df[["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]]
                
                print(f"[数据获取] vnPy数据转换完成，返回 {len(df)} 条记录")
                return df
            else:
                print(f"[数据获取] vnPy返回空数据，尝试使用akshare")
        except Exception as e:
            print(f"[数据获取] vnPy获取失败，尝试使用akshare: {e}")
            import traceback
            print(f"[数据获取] vnPy错误详情: {traceback.format_exc()}")
    
    # 使用akshare作为备选
    if not AKSHARE_AVAILABLE:
        error_msg = "无法获取股票数据："
        if not VNPY_AVAILABLE and not AKSHARE_AVAILABLE:
            error_msg += "vnPy和akshare都未安装，请安装至少一个数据源。"
        elif not VNPY_AVAILABLE:
            error_msg += "vnPy未安装，akshare也不可用。建议安装vnPy: pip install vnpy"
        else:
            error_msg += "akshare未安装，vnPy不可用。建议安装akshare: pip install akshare"
        raise Exception(error_msg)
    
    # 使用akshare获取数据
    for attempt in range(max_retries):
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            # 尽量拿全历史，再在末尾按 days 截断
            start_date = "20000101"

            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )

            if df is None or df.empty:
                raise ValueError(f"无法获取股票 {stock_code} 的日线数据，返回为空")

            cols = list(df.columns)
            print(f"[数据获取] akshare返回的原始列名: {cols}")
            
            if len(cols) < 11:
                raise ValueError(f"东方财富返回的列数不足，列: {cols}")

            # 智能列映射：根据实际列名匹配，而不是假设顺序
            column_mapping = {}
            for i, col in enumerate(cols):
                col_str = str(col).strip()
                col_lower = col_str.lower()
                
                # 日期列
                if 'date' in col_lower or '日期' in col_str or 'time' in col_lower or i == 0:
                    if '日期' not in column_mapping.values():
                        column_mapping[col] = '日期'
                # 开盘
                elif 'open' in col_lower or '开盘' in col_str:
                    if '开盘' not in column_mapping.values():
                        column_mapping[col] = '开盘'
                # 收盘
                elif 'close' in col_lower or '收盘' in col_str:
                    if '收盘' not in column_mapping.values():
                        column_mapping[col] = '收盘'
                # 最高
                elif 'high' in col_lower or '最高' in col_str:
                    if '最高' not in column_mapping.values():
                        column_mapping[col] = '最高'
                # 最低
                elif 'low' in col_lower or '最低' in col_str:
                    if '最低' not in column_mapping.values():
                        column_mapping[col] = '最低'
                # 成交量
                elif 'volume' in col_lower or '成交量' in col_str or 'vol' in col_lower:
                    if '成交量' not in column_mapping.values():
                        column_mapping[col] = '成交量'
                # 成交额
                elif 'amount' in col_lower or '成交额' in col_str or 'turnover' in col_lower:
                    if '成交额' not in column_mapping.values():
                        column_mapping[col] = '成交额'
                # 振幅
                elif '振幅' in col_str or 'amplitude' in col_lower:
                    if '振幅' not in column_mapping.values():
                        column_mapping[col] = '振幅'
                # 涨跌幅
                elif '涨跌幅' in col_str or 'pct' in col_lower or 'change' in col_lower:
                    if '涨跌幅' not in column_mapping.values():
                        column_mapping[col] = '涨跌幅'
                # 涨跌额
                elif '涨跌额' in col_str or 'change_amount' in col_lower:
                    if '涨跌额' not in column_mapping.values():
                        column_mapping[col] = '涨跌额'
                # 换手率
                elif '换手' in col_str or 'turnover_rate' in col_lower:
                    if '换手率' not in column_mapping.values():
                        column_mapping[col] = '换手率'
            
            # 如果智能映射失败，使用默认顺序（兼容旧版本）
            required_cols = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            if len(column_mapping) < len(required_cols):
                print(f"[数据获取] 警告：智能映射不完整，使用默认顺序。已映射: {list(column_mapping.values())}")
                # 使用默认顺序
                df = df.iloc[:, :11].copy()
                df.columns = required_cols
            else:
                # 使用智能映射
                df = df.rename(columns=column_mapping)
                # 只保留需要的列
                df = df[required_cols].copy()
            
            print(f"[数据获取] 列映射完成，最终列名: {list(df.columns)}")

            # 调试：打印原始价格列，帮助排查"开盘价固定不变"的情况
            try:
                print(f"[数据获取] {stock_code} 原始价格示例（最近10条，映射后但未清洗）：")
                print(df[["日期", "开盘", "最高", "最低", "收盘"]].tail(10))
                # 简单统计：看开盘价是否几乎是常数
                if df["开盘"].nunique() <= 3:
                    print(f"[数据获取][警告] {stock_code} 开盘价唯一值个数很少（{df['开盘'].nunique()}），可能存在数据源异常：")
                    print(df["开盘"].value_counts().head(5))
            except Exception as _:
                # 打印失败不影响主流程
                pass

            # 数值列转为 float
            numeric_cols = [
                "开盘",
                "收盘",
                "最高",
                "最低",
                "成交量",
                "成交额",
                "振幅",
                "涨跌幅",
                "涨跌额",
                "换手率",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
            df = df.dropna(subset=["日期", "收盘"]).sort_values("日期").reset_index(drop=True)
            
            # 数据清洗和验证
            if not df.empty:
                # 确保最高 >= 最低
                invalid_high_low = df['最高'] < df['最低']
                if invalid_high_low.any():
                    print(f"[数据获取] 警告：发现 {invalid_high_low.sum()} 条数据最高 < 最低，正在修复...")
                    # 交换最高和最低
                    df.loc[invalid_high_low, ['最高', '最低']] = df.loc[invalid_high_low, ['最低', '最高']].values
                
                # 确保收盘在最高和最低之间
                invalid_close = (df['收盘'] > df['最高']) | (df['收盘'] < df['最低'])
                if invalid_close.any():
                    print(f"[数据获取] 警告：发现 {invalid_close.sum()} 条数据收盘不在最高最低之间，正在修复...")
                    # 将收盘价限制在最高和最低之间
                    df.loc[invalid_close, '收盘'] = df.loc[invalid_close, ['最高', '最低', '收盘']].apply(
                        lambda x: max(min(x['收盘'], x['最高']), x['最低']), axis=1
                    )
                
                # 确保开盘在最高和最低之间
                invalid_open = (df['开盘'] > df['最高']) | (df['开盘'] < df['最低'])
                if invalid_open.any():
                    print(f"[数据获取] 警告：发现 {invalid_open.sum()} 条数据开盘不在最高最低之间，正在修复...")
                    # 将开盘价限制在最高和最低之间
                    df.loc[invalid_open, '开盘'] = df.loc[invalid_open, ['最高', '最低', '开盘']].apply(
                        lambda x: max(min(x['开盘'], x['最高']), x['最低']), axis=1
                    )
                
                # 移除明显异常的数据（价格 <= 0）
                invalid_price = (df['收盘'] <= 0) | (df['开盘'] <= 0) | (df['最高'] <= 0) | (df['最低'] <= 0)
                if invalid_price.any():
                    print(f"[数据获取] 警告：发现 {invalid_price.sum()} 条数据价格 <= 0，正在移除...")
                    df = df[~invalid_price].copy()
                
                # 重新计算涨跌幅和涨跌额（基于清洗后的数据）
                if len(df) > 1:
                    df['涨跌幅'] = df['收盘'].pct_change() * 100
                    df['涨跌额'] = df['收盘'].diff()
                
                # 重新计算振幅（基于清洗后的数据）
                df['振幅'] = ((df['最高'] - df['最低']) / df['收盘'].shift(1).fillna(df['收盘'])) * 100
                
                # 重新计算成交额（如果缺失或异常）
                if '成交额' in df.columns:
                    invalid_amount = (df['成交额'] <= 0) | df['成交额'].isna()
                    if invalid_amount.any():
                        print(f"[数据获取] 警告：发现 {invalid_amount.sum()} 条数据成交额异常，正在估算...")
                        df.loc[invalid_amount, '成交额'] = df.loc[invalid_amount, '成交量'] * df.loc[invalid_amount, '收盘']
                
                df = df.reset_index(drop=True)

            # 最终只返回最近 days 天
            if days and days > 0 and len(df) > days:
                df = df.tail(days).reset_index(drop=True)

            print(f"[数据获取] akshare数据获取成功: {len(df)} 条记录")
            return df
        except Exception as e:
            last_error = e
            msg = str(e).lower()
            # 网络相关错误简单重试
            if any(k in msg for k in ["connection", "timeout", "proxy", "network", "retries"]):
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 2
                    print(f"东方财富数据源网络异常，{wait} 秒后重试 ({attempt + 1}/{max_retries})...")
                    time.sleep(wait)
                    continue
            break

    raise Exception(f"获取股票数据失败（akshare）: {last_error}")


def get_stock_name(stock_code: str, max_retries: int = 2) -> str:
    """获取股票名称；失败时回退为代码本身。"""
    for attempt in range(max_retries):
        try:
            info = ak.stock_individual_info_em(symbol=stock_code)
            if not info.empty:
                name_row = info[info["item"] == "股票简称"]
                if not name_row.empty:
                    return str(name_row.iloc[0]["value"])
            return stock_code
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return stock_code
    return stock_code
