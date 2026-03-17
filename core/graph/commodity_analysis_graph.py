"""
大宗商品分析工作流图
使用LangGraph构建完整的工作流
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END
from core.models.commodity_state import CommodityAnalysisState
from core.agents import (
    commodity_intent_agent,
    commodity_fetch_agent,
    commodity_analysis_agent,
    commodity_judgment_agent,
    commodity_search_agent,
    technical_indicators_agent,
    strategy_generation_agent,
    strategy_risk_agent,
    strategy_backtest_agent,
    commodity_report_agent
)


def should_continue_search(state: CommodityAnalysisState) -> str:
    """
    判断是否需要继续搜索
    
    Args:
        state: 当前状态
    
    Returns:
        "continue" 或 "proceed"
    """
    search_queries = state.get("search_queries", [])
    round_index = state.get("round_index", 0)
    max_rounds = state.get("max_rounds", 2)
    
    if search_queries and round_index < max_rounds:
        print(f"[工作流] 需要继续搜索，当前轮次: {round_index}, 最大轮次: {max_rounds}")
        return "continue"
    else:
        print(f"[工作流] 不需要继续搜索，进入策略生成")
        return "proceed"


def create_commodity_analysis_graph():
    """
    创建大宗商品分析工作流图
    
    Returns:
        编译后的工作流图
    """
    print("[工作流] 创建大宗商品分析工作流图")
    
    workflow = StateGraph(CommodityAnalysisState)
    
    workflow.add_node("intent", commodity_intent_agent.commodity_intent_node)
    workflow.add_node("fetch", commodity_fetch_agent.commodity_fetch_node)
    workflow.add_node("structured_analysis", commodity_analysis_agent.commodity_structured_analysis_node)
    workflow.add_node("judgment", commodity_judgment_agent.commodity_judgment_node)
    workflow.add_node("search", commodity_search_agent.commodity_search_node)
    workflow.add_node("technical_indicators", technical_indicators_agent.technical_indicators_node)
    workflow.add_node("strategy_generation", strategy_generation_agent.strategy_generation_node)
    workflow.add_node("strategy_risk", strategy_risk_agent.strategy_risk_node)
    workflow.add_node("strategy_backtest", strategy_backtest_agent.strategy_backtest_node)
    workflow.add_node("report", commodity_report_agent.commodity_report_node)
    
    workflow.set_entry_point("intent")
    
    workflow.add_edge("intent", "fetch")
    workflow.add_edge("fetch", "structured_analysis")
    workflow.add_edge("structured_analysis", "judgment")
    
    workflow.add_conditional_edges(
        "judgment",
        should_continue_search,
        {
            "continue": "search",
            "proceed": "technical_indicators"
        }
    )
    
    workflow.add_edge("search", "structured_analysis")
    workflow.add_edge("technical_indicators", "strategy_generation")
    workflow.add_edge("strategy_generation", "strategy_risk")
    workflow.add_edge("strategy_risk", "strategy_backtest")
    workflow.add_edge("strategy_backtest", "report")
    workflow.add_edge("report", END)
    
    compiled_graph = workflow.compile()
    
    print("[工作流] 工作流图创建完成")
    print("[工作流] 节点顺序: intent -> fetch -> structured_analysis -> judgment -> (search -> structured_analysis) | technical_indicators -> strategy_generation -> strategy_risk -> strategy_backtest -> report -> END")
    
    return compiled_graph


def run_commodity_analysis(
    commodity_or_chain: str,
    time_range: dict = None,
    user_question: str = None,
    strategy_type: str = "trend",
    max_rounds: int = 2,
    enable_backtest: bool = True
) -> dict:
    """
    运行大宗商品分析
    
    Args:
        commodity_or_chain: 品种或产业链名称
        time_range: 时间范围
        user_question: 用户问题
        strategy_type: 策略类型
        max_rounds: 最大轮次
        enable_backtest: 是否启用回测
    
    Returns:
        分析结果字典
    """
    print(f"[工作流] 开始运行大宗商品分析")
    print(f"[工作流] 品种/产业链: {commodity_or_chain}")
    print(f"[工作流] 策略类型: {strategy_type}")
    
    initial_state = {
        "commodity_or_chain": commodity_or_chain,
        "time_range": time_range,
        "user_question": user_question,
        "strategy_type": strategy_type,
        "max_rounds": max_rounds,
        "enable_backtest": enable_backtest,
        "round_index": 0,
        "raw_evidence": None,
        "structured_analysis": None,
        "judgment": None,
        "search_queries": None,
        "search_results": None,
        "technical_indicators": None,
        "market_state": None,
        "strategy_signals": None,
        "strategy_confidence": None,
        "backtest_results": None,
        "risk_metrics": None,
        "final_report": None,
        "structured_output": None,
        "start_time": None,
        "end_time": None,
        "total_duration": None
    }
    
    try:
        graph = create_commodity_analysis_graph()
        result = graph.invoke(initial_state)
        
        print(f"[工作流] 分析完成")
        print(f"[工作流] 总耗时: {result.get('total_duration', 0):.2f}秒")
        
        return {
            "success": True,
            "data": {
                "report": result.get("final_report"),
                "structured": result.get("structured_output"),
                "strategies": result.get("strategy_signals", []),
                "backtest_results": result.get("backtest_results", []),
                "rounds_used": result.get("round_index", 0),
                "total_duration": result.get("total_duration", 0)
            }
        }
        
    except Exception as e:
        error_msg = f"分析执行失败: {str(e)}"
        print(f"[工作流] {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "data": None
        }
