"""
回溯测试Agent
根据博弈分析+策略推荐进行逐日历史回测
"""
from typing import Dict, Any, List

import pandas as pd

# 新框架：使用LLM分析链
from core.agents.structured_data_agent import structured_data_node
from core.agents.llm_distribution_agent import llm_distribution_analysis_node
from core.agents.llm_stage_agent import llm_stage_analysis_node
from core.agents.llm_emotion_agent import llm_emotion_analysis_node
from core.agents.llm_trading_points_agent import llm_trading_points_analysis_node
from core.agents.summary_agent import summary_node
from core.agents.strategy_agent import strategy_recommendation_node

# 保留旧框架（兼容性）
from core.agents.anchor_agent import anchor_analysis_node
from core.agents.distribution_agent import distribution_analysis_node
from core.agents.emotion_ratio_agent import emotion_ratio_node
from core.agents.o_point_agent import o_point_analysis_node
from core.agents.stage_analysis_agent import stage_analysis_node
from core.agents.washout_agent import washout_analysis_node
from core.models.state import AnalysisState


def _compute_max_drawdown(equity_curve: List[float]) -> float:
    """根据权益曲线计算最大回撤（百分比）"""
    if not equity_curve:
        return 0.0
    series = pd.Series(equity_curve, dtype="float64")
    running_max = series.cummax()
    drawdown = (series - running_max) / running_max
    return float(drawdown.min() * 100)


def _decide_target_pos_ratio(operation: str, position_suggestion: str, current_ratio: float) -> float:
    """根据操作+文字仓位建议，决定目标仓位比例（0~1）"""
    op = operation or ""
    suggest = position_suggestion or ""

    # 强制清仓类
    sell_keywords = ["卖出", "止盈", "止损"]
    if any(k in op for k in sell_keywords) or "0%" in suggest:
        return 0.0

    # 观望类（无仓或尽量轻仓）
    if "观望" in op and "仓" not in suggest:
        return 0.0

    # 一阶段：最多1/3仓位 -> 目标至少 1/3
    if "1/3" in suggest or "三分之一" in suggest:
        return max(current_ratio, 1.0 / 3.0)

    # 逐步加仓至满仓 / 买入加仓
    if "逐步加仓至满仓" in suggest or "加仓" in op:
        return min(current_ratio + 0.33, 1.0)

    # 满仓/重仓提示
    if "满仓" in suggest:
        return 1.0

    # 持有 / 保持现有仓位
    if "持有" in op or "保持现有仓位" in suggest:
        return current_ratio

    # 买入但无明确仓位建议 -> 目标至 1/2 仓
    if "买入" in op:
        return max(current_ratio, 0.5)

    # 默认不变
    return current_ratio


def _run_game_theory_backtest(
    data: pd.DataFrame,
    stock_code: str,
    initial_capital: float = 100000.0,
) -> Dict[str, Any]:
    """基于博弈分析链条的逐日回测"""
    print(f"[Backtest] start _run_game_theory_backtest stock={stock_code}, rows={len(data)}, initial_capital={initial_capital}")

    if data is None or data.empty:
        return {
            "total_return": 0,
            "max_drawdown": 0,
            "trades": 0,
            "holding_days": 0,
            "initial_capital": float(initial_capital),
            "final_equity": float(initial_capital),
            "error": "股票数据为空，无法回测",
        }

    if len(data) < 60:
        return {
            "total_return": 0,
            "max_drawdown": 0,
            "trades": 0,
            "holding_days": 0,
            "initial_capital": float(initial_capital),
            "final_equity": float(initial_capital),
            "error": "数据不足（少于60日），无法回测",
        }

    df = data.reset_index(drop=True).copy()
    date_col = "日期" if "日期" in df.columns else None

    total_len = len(df)
    start_index = max(60, total_len // 2)
    total_days = total_len - start_index
    print(f"[Backtest] using start_index={start_index} of total_len={total_len}, 将回测 {total_days} 天")

    cash = float(initial_capital)
    position = 0
    equity_curve: List[float] = []
    trade_log: List[Dict[str, Any]] = []
    
    # 缓存机制：避免重复分析相同的数据
    analysis_cache: Dict[int, Dict[str, Any]] = {}
    last_analysis_index = -1
    analysis_interval = 5  # 每5天重新分析一次（可以根据需要调整）

    for i in range(start_index, total_len):
        # 进度日志：每20天打印一次
        if (i - start_index) % 20 == 0:
            progress = ((i - start_index) / total_days * 100) if total_days > 0 else 0
            print(f"[Backtest] 进度: {i - start_index}/{total_days} 天 ({progress:.1f}%)")
        visible = df.iloc[: i + 1].copy()
        today = df.iloc[i]

        price = float(today.get("收盘", today.iloc[-1]))
        if price <= 0:
            equity = cash + position * price
            equity_curve.append(equity)
            trade_log.append(
                {
                    "index": int(i),
                    "date": str(today[date_col]) if date_col else str(i),
                    "close": price,
                    "operation": "观望",
                    "position_ratio": float(
                        (position * price) / (equity if equity != 0 else 1.0)
                    )
                    if equity > 0
                    else 0.0,
                    "shares": int(position),
                    "equity": float(equity),
                    "trade_shares": 0,
                }
            )
            continue

        equity_before = cash + position * price
        current_ratio = (
            (position * price) / equity_before if equity_before > 0 else 0.0
        )

        # 缓存机制：只在需要时重新分析（每N天或数据变化时）
        need_reanalysis = (
            (i - last_analysis_index) >= analysis_interval or
            i not in analysis_cache
        )
        
        if need_reanalysis:
            state: AnalysisState = {
                "user_message": "回测博弈分析",
                "stock_code": stock_code,
                "analysis_type": "game_theory",
                "stock_data": visible,
                "stock_name": None,  # 回测时可能没有股票名称
                # 新框架字段
                "structured_data": None,
                "llm_stage_result": None,
                "llm_distribution_result": None,
                "llm_emotion_result": None,
                "llm_trading_points_result": None,
                # 旧框架字段（兼容性）
                "stage_result": None,
                "o_point_result": None,
                "washout_result": None,
                "distribution_result": None,
                "emotion_ratio_result": None,
                "anchor_result": None,
                "summary_result": None,
                "strategy_recommendation": None,
                "backtest_result": None,
                "regular_analysis_result": None,
                "final_report": None,
                "run_backtest": True,  # 标记为回测模式，减少日志输出
                "days": len(visible),
            }

            # 使用新的LLM分析链（与主工作流一致）
            try:
                state = structured_data_node(state)
                state = llm_distribution_analysis_node(state)
                state = llm_stage_analysis_node(state)
                state = llm_emotion_analysis_node(state)
                state = llm_trading_points_analysis_node(state)
                state = summary_node(state)
                state = strategy_recommendation_node(state)
                
                # 缓存分析结果
                analysis_cache[i] = {
                    'strategy_recommendation': state.get("strategy_recommendation"),
                    'llm_trading_points_result': state.get("llm_trading_points_result"),
                }
                last_analysis_index = i
            except Exception as e:
                # 如果新框架失败，回退到旧框架
                print(f"[Backtest] LLM分析链失败，回退到旧框架: {e}")
                try:
                    state = stage_analysis_node(state)
                    state = o_point_analysis_node(state)
                    state = washout_analysis_node(state)
                    state = distribution_analysis_node(state)
                    state = emotion_ratio_node(state)
                    state = anchor_analysis_node(state)
                    state = summary_node(state)
                    state = strategy_recommendation_node(state)
                    
                    # 缓存分析结果
                    analysis_cache[i] = {
                        'strategy_recommendation': state.get("strategy_recommendation"),
                        'llm_trading_points_result': state.get("llm_trading_points_result"),
                    }
                    last_analysis_index = i
                except Exception as e2:
                    print(f"[Backtest] 旧框架也失败: {e2}")
                    # 使用默认策略
                    analysis_cache[i] = {
                        'strategy_recommendation': {"operation": "观望", "position_suggestion": ""},
                    }
                    last_analysis_index = i
        else:
            # 使用缓存的结果
            cached = analysis_cache.get(last_analysis_index, {})
            strategy = cached.get('strategy_recommendation', {"operation": "观望", "position_suggestion": ""})
        
        # 确保strategy已定义
        if need_reanalysis and 'state' in locals():
            strategy = state.get("strategy_recommendation") or strategy
        
        operation = str(strategy.get("operation", "观望"))
        pos_suggestion = str(strategy.get("position_suggestion", ""))

        target_ratio = _decide_target_pos_ratio(
            operation=operation,
            position_suggestion=pos_suggestion,
            current_ratio=current_ratio,
        )
        target_ratio = max(0.0, min(1.0, target_ratio))

        target_value = equity_before * target_ratio
        current_value = position * price
        delta_value = target_value - current_value
        trade_shares = int(delta_value / price)

        if trade_shares < 0 and abs(trade_shares) > position:
            trade_shares = -position

        trade_amount = trade_shares * price

        cash -= trade_amount
        position += trade_shares

        equity_after = cash + position * price
        equity_curve.append(equity_after)

        position_ratio_after = (
            (position * price) / equity_after if equity_after > 0 else 0.0
        )

        # 如果发生了真实买卖动作，记录当时的博弈分析结论，便于前端点击查看
        analysis_payload: Dict[str, Any] | None = None
        if trade_shares != 0:
            # 优先使用LLM分析结果
            llm_stage_result = state.get("llm_stage_result") or {}
            llm_distribution_result = state.get("llm_distribution_result") or {}
            llm_trading_points_result = state.get("llm_trading_points_result") or {}
            summary_result = state.get("summary_result") or {}
            
            summary_text = (
                summary_result.get("summary")
                if isinstance(summary_result, dict)
                else None
            )
            
            # 获取阶段信息（优先LLM结果）
            if llm_stage_result and "error" not in llm_stage_result:
                stage = llm_stage_result.get("stage", 0)
                stage_name = llm_stage_result.get("stage_name", "未知")
                stage_description = llm_stage_result.get("reasoning", "")
            else:
                # 回退到旧结果
                stage_result = state.get("stage_result") or {}
                stage = stage_result.get("stage", 0)
                stage_name = stage_result.get("stage_name", "未知")
                stage_description = stage_result.get("description", "")
            
            analysis_payload = {
                "stage": stage,
                "stage_name": stage_name,
                "stage_description": stage_description,
                "strategy_operation": strategy.get("operation"),
                "strategy_reason": strategy.get("reason"),
                "strategy_position": strategy.get("position_suggestion"),
                "summary": summary_text,
                # 添加LLM分析结果标识
                "using_llm_analysis": bool(llm_stage_result and "error" not in llm_stage_result),
            }

        trade_log.append(
            {
                "index": int(i),
                "date": str(today[date_col]) if date_col else str(i),
                "close": price,
                "operation": operation,
                "position_ratio": float(position_ratio_after),
                "shares": int(position),
                "equity": float(equity_after),
                "trade_shares": int(trade_shares),
                "analysis": analysis_payload,
            }
        )

    if not equity_curve:
        return {
            "total_return": 0,
            "max_drawdown": 0,
            "trades": 0,
            "holding_days": 0,
            "initial_capital": float(initial_capital),
            "final_equity": float(initial_capital),
            "error": "未能生成有效权益曲线",
        }

    final_equity = equity_curve[-1]
    total_return = (final_equity - initial_capital) / initial_capital * 100.0
    max_drawdown = _compute_max_drawdown(equity_curve)
    holding_days = sum(1 for t in trade_log if t["shares"] > 0)
    trade_count = sum(1 for t in trade_log if t["trade_shares"] != 0)

    print(
        f"[Backtest] done stock={stock_code}, total_return={total_return:.2f}%, "
        f"max_drawdown={max_drawdown:.2f}%, trades={trade_count}, holding_days={holding_days}"
    )

    # 准备用于前端绘制K线图的基础数据（日期、开高低收、成交量）
    kline_records: List[Dict[str, Any]] = []
    base_cols = ["日期", "开盘", "最高", "最低", "收盘", "成交量"]
    for _, row in df.iterrows():
        rec: Dict[str, Any] = {}
        for col in base_cols:
            if col not in df.columns:
                continue
            val = row[col]
            if col == "日期":
                # 转成字符串，便于前端作为类目轴
                rec[col] = str(val)
            else:
                # 转成普通 float/int，避免 numpy 类型在 JSON 序列化时报错
                try:
                    rec[col] = float(val)
                except Exception:
                    rec[col] = None
        if rec:
            kline_records.append(rec)

    return {
        "total_return": float(total_return),
        "max_drawdown": float(max_drawdown),
        "trades": int(trade_count),
        "holding_days": int(holding_days),
        "initial_capital": float(initial_capital),
        "final_equity": float(final_equity),
        "equity_curve": equity_curve,
        "trade_log": trade_log,
        "kline": kline_records,
    }


def backtest_node(state: AnalysisState) -> AnalysisState:
    """回溯测试节点：基于博弈分析的逐日回测"""
    stock_data = state.get("stock_data")
    run_backtest = state.get("run_backtest", False)
    stock_code = state.get("stock_code", "")

    print(
        f"[BacktestNode] enter stock={stock_code}, run_backtest={run_backtest}, "
        f"stock_data_len={len(stock_data) if stock_data is not None else 0}"
    )

    if not run_backtest or stock_data is None:
        state["backtest_result"] = {"skipped": True}
        print("[BacktestNode] skipped")
        return state

    try:
        initial_capital = float(state.get("initial_capital", 100000.0))
        backtest_result = _run_game_theory_backtest(
            data=stock_data,
            stock_code=stock_code,
            initial_capital=initial_capital,
        )
        state["backtest_result"] = backtest_result
        print(
            f"[BacktestNode] finished stock={stock_code}, "
            f"total_return={backtest_result.get('total_return')}, "
            f"error={backtest_result.get('error')}"
        )
    except Exception as e:
        print(f"[BacktestNode] error stock={stock_code}: {e}")
        state["backtest_result"] = {"error": str(e)}

    return state


