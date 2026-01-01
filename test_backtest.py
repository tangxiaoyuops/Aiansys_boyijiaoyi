"""简单脚本：直接在后端本地测试回溯逻辑

用法示例：

    python test_backtest.py 600519 400 100000

- 第一个参数：股票代码（必填，如 600519）
- 第二个参数：天数 days（可选，默认 400）
- 第三个参数：初始资金 initial_capital（可选，默认 100000）

脚本会：
1. 用 data_fetcher 取 days 天日线数据
2. 调用 core.agents.backtest_agent._run_game_theory_backtest
3. 在终端打印回测指标 + 前几条交易记录
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import pandas as pd

# 把项目根目录加入 sys.path，方便直接运行该脚本
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.tools.data_fetcher import fetch_stock_data  # noqa: E402
from core.agents.backtest_agent import _run_game_theory_backtest  # noqa: E402


def pretty_print_result(result: Dict[str, Any], max_rows: int = 10) -> None:
    """在终端友好地打印回测结果"""
    if result.get("error"):
        print("回测错误:", result["error"])
        return

    print("=== 回测概要 ===")
    print(f"初始资金:   {result.get('initial_capital', 0):,.2f}")
    print(f"期末权益:   {result.get('final_equity', 0):,.2f}")
    print(f"总收益率:   {result.get('total_return', 0):.2f}%")
    print(f"最大回撤:   {result.get('max_drawdown', 0):.2f}%")
    print(f"交易次数:   {result.get('trades', 0)}")
    print(f"持股天数:   {result.get('holding_days', 0)}")

    trades = result.get("trade_log") or []
    if not trades:
        print("\n无交易记录。")
        return

    print(f"\n=== 前 {min(max_rows, len(trades))} 条交易记录（共 {len(trades)} 条） ===")
    df = pd.DataFrame(trades[:max_rows])
    # 只展示关键列
    cols = [
        "index",
        "date",
        "close",
        "operation",
        "position_ratio",
        "shares",
        "equity",
        "trade_shares",
    ]
    df = df[[c for c in cols if c in df.columns]].copy()
    if "position_ratio" in df.columns:
        df["position_ratio"] = (df["position_ratio"] * 100).round(1)
    print(df.to_string(index=False))


def main() -> None:

    stock_code = "603296"
    days = int(400) if len(sys.argv) >= 3 else 400
    initial_capital = float(100000) if len(sys.argv) >= 4 else 100000.0

    print(f"获取股票 {stock_code} 最近 {days} 天数据...")
    data = fetch_stock_data(stock_code, days)
    print(f"数据行数: {len(data)}")

    print("\n开始回测...")
    result = _run_game_theory_backtest(data=data, stock_code=stock_code, initial_capital=initial_capital)

    pretty_print_result(result)


if __name__ == "__main__":
    main()













