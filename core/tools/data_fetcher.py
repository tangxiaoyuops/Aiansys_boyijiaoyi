"""
数据获取工具

- 主数据源：东方财富日线 ak.stock_zh_a_hist
- 提供 fetch_stock_data / get_stock_name 给分析流程使用
"""

from datetime import datetime
from typing import Optional
import time

import akshare as ak
import pandas as pd


def fetch_stock_data(stock_code: str, days: int = 180, max_retries: int = 3) -> pd.DataFrame:
    """
    获取股票日线数据（前复权），带简单重试与清洗。

    Args:
        stock_code: 6 位股票代码
        days: 需要的最近交易日数量（最终返回长度）

    Returns:
        DataFrame，列包含：
        [日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率]
    """
    last_error: Optional[Exception] = None

    # 方法1: 使用新浪财经API（最稳定）
    print(f"[数据获取] 方法1: 使用新浪财经API获取 {stock_code} 数据...")
    try:
        import requests
        
        # 判断市场：6开头是沪市，其他是深市
        if stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"
        
        url = 'https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData'
        params = {
            'symbol': symbol,
            'scale': '240',  # 日线
            'ma': 'no',
            'datalen': str(days + 30),  # 多取一些
        }
        
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            import json
            data = json.loads(resp.text)
            if data and isinstance(data, list):
                df = pd.DataFrame(data)
                # 转换列名
                df = df.rename(columns={
                    'day': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'volume': '成交量'
                })
                print(f"[数据获取] 新浪财经API成功，获取 {len(df)} 条记录")
                return _process_stock_data(df, stock_code, days)
    except Exception as e:
        print(f"[数据获取] 新浪财经API失败: {str(e)[:100]}")
        last_error = e

    # 方法2: 使用 akshare stock_zh_a_hist (东方财富)
    for attempt in range(max_retries):
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            # 只获取需要的数据范围，避免请求过多数据导致连接问题
            # 多取30天作为缓冲，确保数据充足
            start_date_calc = datetime.now() - pd.Timedelta(days=days + 50)
            start_date = start_date_calc.strftime("%Y%m%d")
            
            print(f"[数据获取] 方法2: 尝试获取 {stock_code} 数据，时间范围: {start_date} - {end_date}")

            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )
            
            if df is not None and not df.empty:
                return _process_stock_data(df, stock_code, days)
                
        except Exception as e:
            last_error = e
            msg = str(e).lower()
            # 网络相关错误简单重试（包括连接中断、远程断开等）
            network_keywords = ["connection", "timeout", "proxy", "network", "retries", 
                               "aborted", "disconnected", "reset", "broken", "closed"]
            if any(k in msg for k in network_keywords):
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 3  # 增加等待时间
                    print(f"东方财富数据源网络异常，{wait} 秒后重试 ({attempt + 1}/{max_retries})...")
                    print(f"错误信息: {str(e)[:100]}")
                    time.sleep(wait)
                    continue
            break
    
    # 方法3: 使用 stock_zh_a_hist_tx (腾讯数据源)
    print(f"[数据获取] 方法2失败，尝试方法3: 腾讯数据源...")
    try:
        import time as time_module
        time_module.sleep(2)  # 短暂延迟
        
        # 腾讯数据源接口
        df = ak.stock_zh_a_hist_tx(symbol=stock_code, adjust="qfq")
        if df is not None and not df.empty:
            # 处理腾讯数据格式
            print(f"[数据获取] 腾讯数据源成功，获取 {len(df)} 条记录")
            return _process_stock_data(df, stock_code, days)
    except Exception as e:
        print(f"[数据获取] 腾讯数据源也失败: {str(e)[:100]}")
        last_error = e
    
    # 方法4: 使用分钟数据聚合（最后备选）
    print(f"[数据获取] 方法3失败，尝试方法4: 分钟数据聚合...")
    try:
        import time as time_module
        time_module.sleep(2)  # 短暂延迟
        
        # 获取分钟数据
        df_min = ak.stock_zh_a_hist_min_em(symbol=stock_code, period="daily", adjust="qfq")
        if df_min is not None and not df_min.empty:
            print(f"[数据获取] 分钟数据源成功，获取 {len(df_min)} 条记录")
            # 分钟数据转换为日线（按日期聚合）
            if '时间' in df_min.columns or 'time' in df_min.columns:
                time_col = '时间' if '时间' in df_min.columns else 'time'
                df_min['日期'] = pd.to_datetime(df_min[time_col]).dt.date
                df = df_min.groupby('日期').agg({
                    '开盘': 'first',
                    '收盘': 'last',
                    '最高': 'max',
                    '最低': 'min',
                    '成交量': 'sum'
                }).reset_index()
                return _process_stock_data(df, stock_code, days)
    except Exception as e:
        print(f"[数据获取] 分钟数据源也失败: {str(e)[:100]}")
        last_error = e

    raise Exception(f"获取股票数据失败（所有数据源都失败）: {last_error}")


def _process_stock_data(df: pd.DataFrame, stock_code: str, days: int) -> pd.DataFrame:
    """处理股票数据"""
    if df is None or df.empty:
        raise ValueError(f"无法获取股票 {stock_code} 的日线数据，返回为空")

    # 打印akshare返回的实际列名，用于调试
    original_cols = list(df.columns)
    print(f"[数据获取] {stock_code} akshare返回的原始列名: {original_cols}")
    
    # 使用列名匹配而非位置索引来识别列
    # akshare可能返回的列名有多种可能
    column_mapping = {}
    target_columns = {
        "日期": ["日期", "date", "交易日期", "时间"],
        "开盘": ["开盘", "open", "开盘价", "今开"],
        "收盘": ["收盘", "close", "收盘价", "今收"],
        "最高": ["最高", "high", "最高价", "今高"],
        "最低": ["最低", "low", "最低价", "今低"],
        "成交量": ["成交量", "volume", "成交额（手）", "成交手数", "vol"],
        "成交额": ["成交额", "amount", "成交金额"],
        "振幅": ["振幅", "amplitude", "振幅%"],
        "涨跌幅": ["涨跌幅", "pct_chg", "涨跌幅%", "涨跌%"],
        "涨跌额": ["涨跌额", "change", "涨跌"],
        "换手率": ["换手率", "turnover", "换手率%", "turn"]
    }
    
    # 遍历所有列，尝试匹配
    for col in df.columns:
        col_str = str(col).strip()
        col_lower = col_str.lower()
        # 跳过股票代码列（通常包含代码本身）
        if col_str == stock_code or col_lower == 'symbol' or col_lower == '代码':
            print(f"[数据获取] 跳过股票代码列: {col_str}")
            continue
            
        # 尝试匹配目标列
        matched = False
        for target_col, possible_names in target_columns.items():
            if target_col not in column_mapping:
                for name in possible_names:
                    if name.lower() == col_lower or col_lower in name.lower() or name.lower() in col_lower:
                        column_mapping[target_col] = col_str
                        print(f"[数据获取] 列映射: {col_str} -> {target_col}")
                        matched = True
                        break
            if matched:
                break
    
    # 检查必要的列是否都已找到
    required_cols = ["日期", "开盘", "收盘", "最高", "最低"]
    missing_cols = [col for col in required_cols if col not in column_mapping]
    if missing_cols:
        raise ValueError(f"无法识别必要的列: {missing_cols}。原始列名: {original_cols}，已匹配: {list(column_mapping.keys())}")
    
    # 只保留已匹配的列，并重命名
    df_result = pd.DataFrame()
    for target_col in ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]:
        if target_col in column_mapping:
            df_result[target_col] = df[column_mapping[target_col]]
        elif target_col in ["成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]:
            # 这些列是可选的，如果没有则设为0或NaN
            if target_col == "成交量":
                df_result[target_col] = 0
            else:
                df_result[target_col] = 0.0
    
    df = df_result

    # 调试：打印原始价格列，帮助排查"开盘价固定不变"的情况
    try:
        print(f"[数据获取] {stock_code} 映射后的价格示例（最近10条，未清洗）：")
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
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 先清洗数据：过滤掉无效的OHLC数据
    original_len = len(df)
    ohlc_cols = ["开盘", "收盘", "最高", "最低"]
    
    # 过滤掉任何OHLC列 <= 0 或 NaN 的行
    valid_mask = pd.Series([True] * len(df), index=df.index)
    for col in ohlc_cols:
        if col in df.columns:
            valid_mask = valid_mask & (df[col] > 0) & df[col].notna()
    
    # 过滤掉OHLC逻辑关系错误的数据（最高 < 最低等）
    if all(col in df.columns for col in ohlc_cols):
        valid_mask = valid_mask & (
            (df["最高"] >= df["最低"]) &
            (df["最高"] >= df["开盘"]) &
            (df["最高"] >= df["收盘"]) &
            (df["最低"] <= df["开盘"]) &
            (df["最低"] <= df["收盘"])
        )
    
    df = df[valid_mask].copy()
    filtered_count = original_len - len(df)
    
    if filtered_count > 0:
        print(f"[数据获取] 过滤掉 {filtered_count} 条无效数据（原始{original_len}条，剩余{len(df)}条）")
    
    # 数据验证：确保清洗后数据质量
    validation_errors = []
    
    # 检查清洗后数据是否足够
    if len(df) < original_len * 0.5:  # 如果过滤后数据少于50%，可能有问题
        validation_errors.append(f"过滤后数据过少（原始{original_len}条，剩余{len(df)}条，过滤比例{filtered_count/original_len:.1%}）")
    
    # 检查是否包含过多NaN值
    for col in ohlc_cols:
        if col in df.columns:
            non_numeric = df[col].isna().sum()
            if non_numeric > len(df) * 0.1:  # 如果超过10%的值是NaN，报错
                validation_errors.append(f"{col}列包含过多无效值（{non_numeric}/{len(df)}）")
    
    # 检查开盘价是否几乎都是同一个值（可能是列错位）
    if "开盘" in df.columns and len(df) > 0:
        if df["开盘"].nunique() <= 3 and len(df) > 10:
            unique_vals = df["开盘"].value_counts().head(5)
            # 如果最大值占比例很高，可能是列错位
            max_ratio = unique_vals.iloc[0] / len(df) if len(unique_vals) > 0 else 0
            if max_ratio > 0.8:
                validation_errors.append(f"开盘价几乎都是同一个值（{unique_vals.index[0]}，占比{max_ratio:.1%}），可能存在列错位")
    
    # 如果检测到严重错误，抛出异常
    if validation_errors:
        error_msg = f"数据验证失败（股票{stock_code}）：\n" + "\n".join(f"  - {err}" for err in validation_errors)
        error_msg += f"\n原始列名: {original_cols}"
        error_msg += f"\n已匹配列: {list(column_mapping.keys())}"
        print(f"[数据获取][错误] {error_msg}")
        raise ValueError(error_msg)
    
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df = df.dropna(subset=["日期", "收盘"]).sort_values("日期").reset_index(drop=True)
    
    # 最终验证：确保至少有一些数据
    if len(df) == 0:
        raise ValueError(f"数据清洗后为空（股票{stock_code}）")

    # 最终只返回最近 days 天
    if days and days > 0 and len(df) > days:
        df = df.tail(days).reset_index(drop=True)

    return df


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
