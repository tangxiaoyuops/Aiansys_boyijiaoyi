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
            
            # 目标列名（标准输出格式）
            target_columns = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]
            
            # 智能列映射：通过列名匹配，而不是依赖固定位置
            # 这样可以适应akshare API的变化（列顺序变化、新增列等）
            column_mapping = {}
            
            # 定义列名匹配规则（支持多种可能的列名，不区分大小写）
            column_patterns = {
                "日期": ["日期", "date", "时间", "time", "交易日期", "交易时间"],
                "开盘": ["开盘", "open", "开盘价", "open_price"],
                "收盘": ["收盘", "close", "收盘价", "close_price"],
                "最高": ["最高", "high", "最高价", "high_price"],
                "最低": ["最低", "low", "最低价", "low_price"],
                "成交量": ["成交量", "volume", "vol", "成交手数", "volume_手"],
                "成交额": ["成交额", "amount", "成交金额", "turnover", "成交额_元"],
                "振幅": ["振幅", "amplitude", "振幅%", "amplitude_pct"],
                "涨跌幅": ["涨跌幅", "change_pct", "涨跌%", "涨跌幅%", "pct_chg", "涨跌幅_%"],
                "涨跌额": ["涨跌额", "change", "涨跌", "net_change", "涨跌额_元"],
                "换手率": ["换手率", "turnover_rate", "换手", "turnover%", "换手率_%"]
            }
            
            # 遍历所有列，找到匹配的列（跳过股票代码列）
            for col in cols:
                col_str = str(col).strip().lower()
                
                # 明确跳过股票代码列（但保留日期相关的列）
                if any(keyword in col_str for keyword in ["股票代码", "symbol", "code"]):
                    if "日期" not in col_str and "date" not in col_str:
                        continue  # 跳过股票代码列
                
                # 匹配目标列
                for target_col, patterns in column_patterns.items():
                    if any(pattern.lower() in col_str for pattern in patterns):
                        if target_col not in column_mapping:  # 避免重复匹配
                            column_mapping[target_col] = col
                            break
            
            # 验证是否找到了所有必需的列
            missing_cols = [col for col in target_columns if col not in column_mapping]
            if missing_cols:
                print(f"[数据获取][警告] 通过列名匹配未找到以下列: {missing_cols}")
                print(f"[数据获取] 已匹配的列: {column_mapping}")
                
                # 回退方案1：如果缺少的列不多，尝试位置映射（兼容旧版本）
                if len(missing_cols) <= 2 and "日期" in column_mapping and "收盘" in column_mapping:
                    print(f"[数据获取] 尝试回退方案：使用位置映射")
                    has_code_col = any('股票代码' in str(col) or ('代码' in str(col) and '日期' not in str(col)) for col in cols)
                    if has_code_col and len(cols) >= 12:
                        # 有股票代码列，跳过第2列
                        df = df.iloc[:, [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]].copy()
                        df.columns = target_columns
                        print(f"[数据获取] 回退方案：跳过股票代码列（位置映射）")
                    elif len(cols) >= 11:
                        # 没有股票代码列
                        df = df.iloc[:, :11].copy()
                        df.columns = target_columns
                        print(f"[数据获取] 回退方案：使用前11列（位置映射）")
                    else:
                        raise ValueError(f"列数不足且无法匹配，原始列: {cols}")
                else:
                    # 如果缺少关键列，抛出错误
                    raise ValueError(
                        f"缺少关键列（{missing_cols}），无法继续。\n"
                        f"原始列名: {cols}\n"
                        f"已匹配列: {column_mapping}\n"
                        f"这可能是akshare API发生了变化，请检查或更新代码。"
                    )
            else:
                # 使用列名映射（最健壮的方式）
                df = df.rename(columns=column_mapping)
                # 只保留我们需要的列，并按目标顺序排列
                df = df[target_columns].copy()
                print(f"[数据获取] 智能列映射成功（通过列名匹配），最终列名: {list(df.columns)}")

            # 数据验证：在转换为数值类型前进行验证
            try:
                print(f"[数据获取] {stock_code} 数据示例（映射后但未清洗）：")
                print(df[["日期", "开盘", "最高", "最低", "收盘"]].tail(10))
                
                # 关键验证：检查开盘价是否合理
                if "开盘" in df.columns:
                    # 检查开盘价是否等于股票代码（列映射错误的典型症状）
                    sample_open = str(df["开盘"].iloc[0]) if len(df) > 0 else ""
                    if sample_open == stock_code or sample_open.strip() == stock_code:
                        raise ValueError(
                            f"数据异常：开盘价列的值是股票代码（{stock_code}），列映射错误！\n"
                            f"这通常是因为akshare返回的列结构发生了变化。\n"
                            f"原始列名: {cols}\n"
                            f"请检查列映射逻辑或联系开发者更新代码。"
                        )
                    
                    # 检查开盘价是否为数值类型（字符串类型的股票代码无法转换为数值）
                    try:
                        test_convert = pd.to_numeric(df["开盘"].iloc[0], errors='raise')
                        if not isinstance(test_convert, (int, float)) or test_convert <= 0:
                            raise ValueError(f"开盘价不是有效的正数: {test_convert}")
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"数据异常：开盘价无法转换为数值类型，可能是列映射错误。\n"
                            f"样本值: {sample_open}\n"
                            f"原始列名: {cols}"
                        )
                    
                    # 转换为数值后检查唯一值数量
                    open_prices = pd.to_numeric(df["开盘"], errors='coerce')
                    unique_count = open_prices.nunique()
                    if unique_count <= 3:
                        print(f"[数据获取][警告] {stock_code} 开盘价唯一值个数很少（{unique_count}），可能存在数据源异常：")
                        print(df["开盘"].value_counts().head(5))
                
                # 验证价格数据的逻辑关系（在转换为数值前先检查类型）
                if all(col in df.columns for col in ["开盘", "收盘", "最高", "最低"]):
                    # 先转换为数值类型
                    for col in ["开盘", "收盘", "最高", "最低"]:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 检查数据合理性
                    invalid_count = len(df[
                        (df["最高"] < df["最低"]) | 
                        (df["收盘"] > df["最高"]) | 
                        (df["收盘"] < df["最低"]) |
                        (df["开盘"] > df["最高"]) |
                        (df["开盘"] < df["最低"])
                    ])
                    if invalid_count > len(df) * 0.1:  # 如果超过10%的数据异常
                        print(f"[数据获取][严重警告] {stock_code} 发现 {invalid_count} 行数据异常（价格超出范围），可能存在列映射错误")
                        print(df[["日期", "开盘", "最高", "最低", "收盘"]].head(10))
            except ValueError as ve:
                # 如果是我们主动抛出的ValueError，直接抛出
                raise
            except Exception as e:
                # 其他错误只记录，不影响主流程
                print(f"[数据获取][调试] 数据验证时出错: {e}")
                import traceback
                traceback.print_exc()

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

            df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
            df = df.dropna(subset=["日期", "收盘"]).sort_values("日期").reset_index(drop=True)

            # 最终只返回最近 days 天
            if days and days > 0 and len(df) > days:
                df = df.tail(days).reset_index(drop=True)

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

    raise Exception(f"获取股票数据失败（东方财富）: {last_error}")


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
