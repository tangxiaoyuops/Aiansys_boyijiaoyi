"""
LangGraph工作流定义
实现博弈交易法分析的多Agent工作流
"""
from langgraph.graph import StateGraph, END
from core.models.state import AnalysisState
from core.agents.intent_agent import intent_recognition_node
from core.agents.data_agent import data_fetch_node
from core.agents.structured_data_agent import structured_data_node
from core.agents.llm_stage_agent import llm_stage_analysis_node
from core.agents.llm_distribution_agent import llm_distribution_analysis_node
from core.agents.llm_emotion_agent import llm_emotion_analysis_node
from core.agents.llm_trading_points_agent import llm_trading_points_analysis_node
from core.agents.llm_dialogue_agent import llm_dialogue_node
from core.agents.summary_agent import summary_node
from core.agents.strategy_agent import strategy_recommendation_node
from core.agents.regular_analysis_agent import regular_analysis_node
from core.agents.backtest_agent import backtest_node

# 保留旧节点（兼容性）
from core.agents.stage_analysis_agent import stage_analysis_node
from core.agents.o_point_agent import o_point_analysis_node
from core.agents.washout_agent import washout_analysis_node
from core.agents.distribution_agent import distribution_analysis_node
from core.agents.emotion_ratio_agent import emotion_ratio_node
from core.agents.anchor_agent import anchor_analysis_node


def route_analysis_node(state: AnalysisState) -> AnalysisState:
    """路由节点：根据分析类型决定走哪个分支，直接返回状态"""
    return state


def route_analysis(state: AnalysisState) -> str:
    """路由函数：根据分析类型决定走哪个分支"""
    analysis_type = state.get('analysis_type', 'regular')
    dialogue_mode = state.get('dialogue_mode', False)

    # 如果识别为对话/追问，则走对话分支，直接和LLM聊天
    if dialogue_mode:
        return 'dialogue'

    if analysis_type == 'game_theory':
        return 'game_theory_analysis'
    else:
        return 'regular_analysis'


def should_backtest(state: AnalysisState) -> str:
    """判断是否进行回测"""
    run_backtest = state.get('run_backtest', False)
    if run_backtest:
        return 'backtest'
    else:
        return 'end'


def generate_final_report(state: AnalysisState) -> AnalysisState:
    """生成最终报告节点"""
    analysis_type = state.get('analysis_type', 'regular')
    report_parts = []

    if analysis_type == 'game_theory':
        # 博弈分析报告
        summary_result = state.get('summary_result', {})
        strategy = state.get('strategy_recommendation', {})
        backtest = state.get('backtest_result', {})

        if summary_result:
            report_parts.append("## 博弈交易法分析报告\n")
            report_parts.append(summary_result.get('summary', ''))

        if strategy:
            report_parts.append("\n## 交易策略推荐\n")
            report_parts.append(f"**操作建议**：{strategy.get('operation', '观望')}")
            report_parts.append(f"**理由**：{strategy.get('reason', '')}")
            report_parts.append(f"**仓位建议**：{strategy.get('position_suggestion', '0%')}")
            if strategy.get('strategy_details'):
                report_parts.append("\n**操作策略**：")
                for detail in strategy.get('strategy_details', []):
                    report_parts.append(f"- {detail}")
            if strategy.get('stop_loss_advice'):
                report_parts.append("\n**止损建议**：")
                for advice in strategy.get('stop_loss_advice', []):
                    report_parts.append(f"- {advice}")

        if backtest and not backtest.get('skipped'):
            report_parts.append("\n## 回溯测试结果\n")
            if backtest.get('error'):
                report_parts.append(f"回测失败：{backtest.get('error')}")
            else:
                report_parts.append(
                    f"**初始资金**：{backtest.get('initial_capital', 0):.2f}，"
                    f"**期末权益**：{backtest.get('final_equity', 0):.2f}"
                )
                report_parts.append(f"**总收益率**：{backtest.get('total_return', 0):.2f}%")
                report_parts.append(f"**最大回撤**：{backtest.get('max_drawdown', 0):.2f}%")
                report_parts.append(f"**交易次数**：{backtest.get('trades', 0)}")
                report_parts.append(f"**持股天数**：{backtest.get('holding_days', 0)}")

                # 只展示实际有交易的记录（trade_shares != 0），避免每天一行太长
                full_log = backtest.get('trade_log') or []
                trade_log = [
                    row for row in full_log
                    if row and isinstance(row, dict) and row.get('trade_shares')
                ]
                if trade_log:
                    report_parts.append("\n**回测交易明细（仅实际交易）**：")
                    report_parts.append("| 序号 | 日期 | 收盘价 | 操作 | 仓位比例 | 持股数量 | 权益 | 当日成交股数 |")
                    report_parts.append("| --- | ---- | ------ | ---- | -------- | -------- | ---- | ------------ |")
                    max_rows = 50
                    for idx, row in enumerate(trade_log[:max_rows], start=1):
                        report_parts.append(
                            f"| {idx} | {row.get('date', '')} | "
                            f"{row.get('close', 0):.2f} | {row.get('operation', '')} | "
                            f"{row.get('position_ratio', 0) * 100:.1f}% | {row.get('shares', 0)} | "
                            f"{row.get('equity', 0):.2f} | {row.get('trade_shares', 0)} |"
                        )
                    if len(trade_log) > max_rows:
                        report_parts.append(f"\n（共 {len(trade_log)} 笔交易，以上仅展示前 {max_rows} 笔）")
    else:
        # 常规分析报告
        regular_result = state.get('regular_analysis_result', {})
        if regular_result:
            report_parts.append("## 常规技术分析报告\n")
            indicators = regular_result.get('indicators', {})
            report_parts.append(f"**当前价格**：{regular_result.get('current_price', 0):.2f}")
            report_parts.append(f"**MA5**：{indicators.get('MA5', 0):.2f}")
            report_parts.append(f"**MA20**：{indicators.get('MA20', 0):.2f}")
            report_parts.append(f"**RSI**：{indicators.get('RSI', 50):.2f}")
            report_parts.append(f"**MACD**：{indicators.get('MACD', 0):.4f}")
            report_parts.append(f"\n**交易建议**：{regular_result.get('suggestion', '观望')}")
            report_parts.append(f"**信心度**：{regular_result.get('confidence', '低')}")

    state['final_report'] = "\n".join(report_parts) if report_parts else "分析完成"
    return state


def create_analysis_graph() -> StateGraph:
    """创建分析工作流图（基于LLM的新框架）"""
    # 创建状态图
    workflow = StateGraph(AnalysisState)

    # 添加节点
    workflow.add_node("intent_recognition", intent_recognition_node)
    workflow.add_node("data_fetch", data_fetch_node)
    workflow.add_node("route", route_analysis_node)  # 路由节点（条件判断）
    
    # 新框架：结构化数据 + LLM分析
    workflow.add_node("structured_data", structured_data_node)
    workflow.add_node("llm_stage_analysis", llm_stage_analysis_node)
    workflow.add_node("llm_distribution_analysis", llm_distribution_analysis_node)
    workflow.add_node("llm_emotion_analysis", llm_emotion_analysis_node)
    workflow.add_node("llm_trading_points_analysis", llm_trading_points_analysis_node)
    
    # 对话节点（用于常规对话 / 追问）
    workflow.add_node("dialogue", llm_dialogue_node)

    # 总结和策略
    workflow.add_node("summary", summary_node)
    workflow.add_node("strategy_recommendation", strategy_recommendation_node)
    
    # 常规分析（保留）
    workflow.add_node("regular_analysis", regular_analysis_node)
    
    # 回测和最终报告
    workflow.add_node("backtest", backtest_node)
    workflow.add_node("final_report", generate_final_report)

    # 设置入口点
    workflow.set_entry_point("intent_recognition")

    # 添加边
    workflow.add_edge("intent_recognition", "data_fetch")
    workflow.add_edge("data_fetch", "route")

    # 条件分支：根据分析类型路由
    workflow.add_conditional_edges(
        "route",
        route_analysis,
        {
            "game_theory_analysis": "structured_data",  # 博弈分析走新框架
            "regular_analysis": "regular_analysis",     # 常规分析走旧路径
            "dialogue": "dialogue",                     # 常规对话/追问走对话节点
        },
    )

    # 新框架：博弈分析链（顺序执行）
    # 注意：出货分析在阶段分析之前，因为阶段分析需要出货分析的结果
    workflow.add_edge("structured_data", "llm_distribution_analysis")
    workflow.add_edge("llm_distribution_analysis", "llm_stage_analysis")
    workflow.add_edge("llm_stage_analysis", "llm_emotion_analysis")
    workflow.add_edge("llm_emotion_analysis", "llm_trading_points_analysis")
    workflow.add_edge("llm_trading_points_analysis", "summary")
    workflow.add_edge("summary", "strategy_recommendation")

    # 常规分析路径
    workflow.add_edge("regular_analysis", "strategy_recommendation")

    # 策略推荐后，根据配置决定是否先回测
    workflow.add_conditional_edges(
        "strategy_recommendation",
        should_backtest,
        {
            "backtest": "backtest",      # 先回测，再生成最终报告
            "end": "final_report",       # 不回测则直接生成最终报告
        },
    )

    # 回测结束后生成最终报告
    workflow.add_edge("backtest", "final_report")

    # 对话分支：直接结束（final_report 已由 llm_dialogue_node 写入）
    workflow.add_edge("dialogue", END)

    # 最终报告后结束
    workflow.add_edge("final_report", END)

    return workflow


# 创建图实例
analysis_graph = create_analysis_graph()

# 编译图
compiled_graph = analysis_graph.compile()

