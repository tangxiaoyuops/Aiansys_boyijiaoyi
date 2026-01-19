"""
每日恐慌点扫描脚本

- 数据源：复用 core.tools.data_fetcher.fetch_stock_data（东方财富日线，前复权）
- 核心逻辑：core.tools.technical_analyzer.detect_panic_points / identify_stage_indicators
- 目标：扫描指定股票池（沪深300 + 自定义池），找到最近若干天内的恐慌点候选，输出到本地文件
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from core.tools.data_fetcher import fetch_stock_data, get_stock_name
from core.tools.technical_analyzer import detect_panic_points, identify_stage_indicators


def get_hs300_codes() -> List[str]:
    """
    获取沪深300成分股代码列表。

    优先使用 akshare 的指数成分接口。如果获取失败，返回空列表，主流程会继续用自定义股票池。
    """
    try:
        import akshare as ak

        df = ak.index_stock_cons(symbol="000300")
        if df is None or df.empty:
            print("[HS300] 未获取到成分股数据，返回空列表")
            return []

        # 常见列名兼容
        code_col: Optional[str] = None
        for col in df.columns:
            col_str = str(col)
            if col_str in ("品种代码", "代码", "index_code", "股票代码", "证券代码"):
                code_col = col_str
                break

        if code_col is None:
            print(f"[HS300] 未找到代码列，列名: {list(df.columns)}，返回空列表")
            return []

        codes = df[code_col].astype(str).str.zfill(6).tolist()
        print(f"[HS300] 成分股数量: {len(codes)}")
        return codes
    except Exception as e:  # noqa: BLE001
        print(f"[HS300] 获取成分股失败: {e}")
        return []


def get_custom_pool() -> List[str]:
    """
    自定义股票池。

    TODO: 如需要，可改为从配置文件 / 数据库 / 前端输入中加载。
    """
    return [
        "600000",
        "600519",
        "000001",
        # 在这里添加你特别关注的标的
    ]


def get_universe() -> List[str]:
    """
    最终监控股票池 = 沪深300 + 自选（去重后排序）。
    """
    hs300 = get_hs300_codes()
    custom = get_custom_pool()
    universe = sorted(set(hs300) | set(custom))
    print(f"[Universe] 股票池总数: {len(universe)}")
    return universe


def _normalize_date(value: Any) -> Optional[pd.Timestamp]:
    """将传入的日期字段统一转换为 pandas.Timestamp。"""
    if isinstance(value, pd.Timestamp):
        return value
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return None
        return ts
    except Exception:  # noqa: BLE001
        return None


def scan_single_stock(
    code: str,
    days: int = 250,
    panic_window: int = 60,
    recent_days: int = 5,
) -> List[Dict[str, Any]]:
    """
    扫描单只股票，返回“近 recent_days 日内的恐慌点候选列表”。
    """
    try:
        df = fetch_stock_data(code, days=days)
    except Exception as e:  # noqa: BLE001
        print(f"[Scan] 获取 {code} 数据失败: {e}")
        return []

    if df is None or df.empty:
        return []

    # 恐慌点检测
    panic_points = detect_panic_points(df, window=panic_window)
    if not panic_points:
        return []

    # 阶段 / 趋势指标
    stage_indicators = identify_stage_indicators(df)

    # 只保留最近 N 天内的恐慌点
    last_date = _normalize_date(df["日期"].max())
    if last_date is None:
        return []
    cutoff_date = last_date - timedelta(days=recent_days)

    results: List[Dict[str, Any]] = []
    name = get_stock_name(code)

    for p in panic_points:
        p_date_raw = p.get("date")
        p_date = _normalize_date(p_date_raw)
        if p_date is None:
            continue

        if p_date < cutoff_date:
            continue

        current_price = stage_indicators.get("current_price")
        ma60 = stage_indicators.get("ma60")

        over_ma60_ratio: Optional[float] = None
        if current_price and ma60:
            try:
                over_ma60_ratio = (current_price - ma60) / ma60 * 100
            except ZeroDivisionError:
                over_ma60_ratio = None

        # 简单高位过滤：距离 60 日线涨幅过高的票先剔除，避免明显三阶段高位
        if over_ma60_ratio is not None and over_ma60_ratio > 50:
            continue

        drop_pct = float(p.get("drop_pct", 0.0) or 0.0)
        vol_ratio = float(p.get("vol_ratio", 0.0) or 0.0)

        # 简单评分：跌幅越大（越负）+ 放量越大，分数越高
        score = (-drop_pct) * 0.7 + vol_ratio * 0.3

        results.append(
            {
                "code": code,
                "name": name,
                "panic_date": p_date.strftime("%Y-%m-%d"),
                "panic_type": p.get("type"),
                "panic_desc": p.get("description", ""),
                "drop_pct": drop_pct,
                "vol_ratio": vol_ratio,
                "score": score,
                "current_price": current_price,
                "ma60": ma60,
                "over_ma60_pct": over_ma60_ratio,
                "recent_gain_20d": stage_indicators.get("recent_gain_20d"),
            }
        )

    return results


def run_daily_scan(
    output_dir: str = "output",
    days: int = 300,
    panic_window: int = 60,
    recent_days: int = 5,
    top_k: int = 50,
) -> Dict[str, str]:
    """
    扫描整个股票池，输出当日恐慌点候选列表到 CSV/JSON。

    Returns:
        包含输出文件路径的字典，例如:
        {"csv": ".../daily_panic_candidates_YYYYMMDD.csv", "json": ".../daily_panic_candidates_YYYYMMDD.json"}
    """
    os.makedirs(output_dir, exist_ok=True)

    universe = get_universe()
    if not universe:
        print("[Scan] 股票池为空，直接返回")
        return {}

    all_records: List[Dict[str, Any]] = []

    total = len(universe)
    for idx, code in enumerate(universe, start=1):
        print(f"[Scan] ({idx}/{total}) 扫描 {code} ...")
        records = scan_single_stock(
            code=code,
            days=days,
            panic_window=panic_window,
            recent_days=recent_days,
        )
        all_records.extend(records)

    if not all_records:
        print("[Scan] 今日未发现任何恐慌点候选股票")
        return {}

    df_res = pd.DataFrame(all_records)
    df_res = df_res.sort_values("score", ascending=False).reset_index(drop=True)

    if top_k and len(df_res) > top_k:
        df_res = df_res.head(top_k)

    today_str = datetime.now().strftime("%Y%m%d")

    csv_path = os.path.join(output_dir, f"daily_panic_candidates_{today_str}.csv")
    json_path = os.path.join(output_dir, f"daily_panic_candidates_{today_str}.json")

    df_res.to_csv(csv_path, index=False, encoding="utf-8-sig")
    # 使用 orient="records" 方便前端或其他程序直接读取
    df_res.to_json(json_path, orient="records", force_ascii=False)

    print(f"[Scan] 已输出 {len(df_res)} 条候选至: {csv_path}")
    print(f"[Scan] JSON 输出: {json_path}")

    return {"csv": csv_path, "json": json_path}


def main() -> None:
    """
    CLI 入口，支持命令行参数。
    """
    import argparse

    parser = argparse.ArgumentParser(description="每日恐慌点扫描脚本")
    parser.add_argument("--output-dir", type=str, default="output", help="输出目录")
    parser.add_argument("--days", type=int, default=300, help="回看交易日数量")
    parser.add_argument("--panic-window", type=int, default=60, help="恐慌点检测窗口")
    parser.add_argument("--recent-days", type=int, default=5, help="只看最近N天内的恐慌点")
    parser.add_argument("--top-k", type=int, default=50, help="每日最多推荐数量")

    args = parser.parse_args()

    run_daily_scan(
        output_dir=args.output_dir,
        days=args.days,
        panic_window=args.panic_window,
        recent_days=args.recent_days,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()


