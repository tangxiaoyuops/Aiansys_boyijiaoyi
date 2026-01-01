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
            if len(cols) < 11:
                raise ValueError(f"东方财富返回的列数不足，列: {cols}")

            # 只保留前 11 列，并重命名为标准列
            df = df.iloc[:, :11].copy()
            df.columns = [
                "日期",
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

            # 调试：打印原始价格列，帮助排查“开盘价固定不变”的情况
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
