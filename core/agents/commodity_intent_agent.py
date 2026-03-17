"""
大宗商品意图解析Agent
解析用户输入的品种/产业链/时间/策略类型
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState


def commodity_intent_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    意图解析节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[意图解析] 开始解析用户意图")
    
    commodity_or_chain = state.get("commodity_or_chain", "")
    time_range = state.get("time_range")
    user_question = state.get("user_question")
    strategy_type = state.get("strategy_type")
    
    print(f"[意图解析] 品种/产业链: {commodity_or_chain}")
    print(f"[意图解析] 时间范围: {time_range}")
    print(f"[意图解析] 用户问题: {user_question}")
    print(f"[意图解析] 策略类型: {strategy_type}")
    
    if not commodity_or_chain:
        print("[意图解析] 警告: 未指定品种或产业链")
    
    state["commodity_or_chain"] = commodity_or_chain
    state["time_range"] = time_range
    state["user_question"] = user_question
    state["strategy_type"] = strategy_type or "trend"
    
    if not state.get("max_rounds"):
        state["max_rounds"] = 2
    
    if not state.get("enable_backtest"):
        state["enable_backtest"] = True
    
    if not state.get("timeout"):
        state["timeout"] = 300
    
    if not state.get("round_index"):
        state["round_index"] = 0
    
    if not state.get("start_time"):
        import time
        state["start_time"] = time.time()
    
    print(f"[意图解析] 意图解析完成")
    
    return state
