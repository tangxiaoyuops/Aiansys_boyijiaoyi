"""
期货分析工作流定义
基于LangGraph实现期货分析的多Agent工作流
"""
from langgraph.graph import StateGraph, END
from core.models.futures_state import FuturesAnalysisState
from core.agents.futures_data_agent import futures_data_fetch_node
from core.agents.futures_game_theory_agent import futures_game_theory_analysis_node
from core.agents.futures_risk_agent import futures_risk_analysis_node
from core.agents.futures_spread_agent import futures_spread_analysis_node
from core.agents.futures_fundamental_agent import futures_fundamental_analysis_node
from core.agents.futures_strategy_agent import futures_strategy_recommendation_node


def route_futures_analysis(state: FuturesAnalysisState) -> str:
    """路由函数：根据分析类型决定走哪个分支"""
    analysis_type = state.get('analysis_type', 'all')
    print(f"[期货工作流] 路由判断: analysis_type={analysis_type}")
    
    if analysis_type == 'game_theory':
        result = 'game_theory_only'
    elif analysis_type == 'risk':
        result = 'risk_only'
    elif analysis_type == 'spread':
        result = 'spread_only'
    elif analysis_type == 'fundamental':
        result = 'fundamental_only'
    else:
        result = 'all_analysis'
    
    print(f"[期货工作流] 路由结果: {result}")
    return result


def generate_futures_final_report(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """生成期货分析最终报告节点"""
    futures_code = state.get('futures_code', '')
    analysis_type = state.get('analysis_type', 'all')
    
    print(f"[期货最终报告] 开始生成报告: {futures_code}, 分析类型: {analysis_type}")
    
    report_parts = []
    
    # 基本信息
    futures_name = state.get('futures_name', '')
    report_parts.append(f"## 期货分析报告：{futures_code} ({futures_name})\n")
    
    # 博弈分析结果
    if analysis_type in ['all', 'game_theory']:
        game_theory_result = state.get('game_theory_result', {})
        if game_theory_result and not game_theory_result.get('error'):
            report_parts.append("\n### 博弈交易法分析\n")
            report_parts.append(f"**当前阶段**：{game_theory_result.get('stage_name', '未知')}")
            report_parts.append(f"**置信度**：{game_theory_result.get('confidence', 0):.2%}")
            
            oi_analysis = game_theory_result.get('open_interest_analysis', {})
            if oi_analysis:
                report_parts.append(f"**持仓量分析**：{oi_analysis.get('trend', '')}")
                report_parts.append(f"**影响**：{oi_analysis.get('impact', '')}")
            
            leverage_risk = game_theory_result.get('leverage_risk', {})
            if leverage_risk:
                report_parts.append(f"**杠杆风险**：{leverage_risk.get('risk_level', '')}")
                report_parts.append(f"**风险提示**：{leverage_risk.get('warning', '')}")
            
            reasoning = game_theory_result.get('reasoning', '')
            if reasoning:
                report_parts.append(f"\n**分析理由**：{reasoning}")
    
    # 风险管理分析结果
    if analysis_type in ['all', 'risk']:
        risk_result = state.get('risk_analysis_result', {})
        if risk_result and not risk_result.get('error'):
            report_parts.append("\n### 风险管理分析\n")
            report_parts.append(f"**当前价格**：{risk_result.get('current_price', 0):.2f}")
            report_parts.append(f"**杠杆倍数**：{risk_result.get('leverage', 0):.1f}倍")
            report_parts.append(f"**保证金率**：{risk_result.get('margin_rate', 0):.1%}")
            report_parts.append(f"**波动率（20日）**：{risk_result.get('volatility_20', 0):.2f}%")
            report_parts.append(f"**最大回撤（60日）**：{risk_result.get('max_drawdown_60', 0):.2f}%")
            report_parts.append(f"**风险等级**：{risk_result.get('risk_level', 'medium')}")
            
            recommendations = risk_result.get('recommendations', [])
            if recommendations:
                report_parts.append("\n**风险管理建议**：")
                for rec in recommendations:
                    report_parts.append(f"- {rec.get('suggestion', '')}：{rec.get('reason', '')}")
    
    # 价差分析结果
    if analysis_type in ['all', 'spread']:
        spread_result = state.get('spread_analysis_result', {})
        if spread_result and not spread_result.get('error'):
            report_parts.append("\n### 价差分析\n")
            
            calendar_spread = spread_result.get('calendar_spread')
            if calendar_spread:
                analysis = calendar_spread.get('analysis', {})
                report_parts.append(f"**跨期价差**：{calendar_spread.get('near_month', '')} vs {calendar_spread.get('far_month', '')}")
                report_parts.append(f"  - 当前价差：{analysis.get('current_spread', 0):.2f}")
                report_parts.append(f"  - 价差均值：{analysis.get('spread_mean', 0):.2f}")
                report_parts.append(f"  - 价差趋势：{analysis.get('trend', 'unknown')}")
                
                arbitrage = calendar_spread.get('arbitrage', {})
                if arbitrage.get('has_opportunity'):
                    report_parts.append(f"  - **套利机会**：{arbitrage.get('opportunity_type', '')}")
                    report_parts.append(f"  - 预期收益：{arbitrage.get('expected_profit', 0):.2f}")
                    report_parts.append(f"  - 置信度：{arbitrage.get('confidence', 0):.2%}")
            
            arbitrage_opps = spread_result.get('arbitrage_opportunities', [])
            if arbitrage_opps:
                report_parts.append("\n**套利机会列表**：")
                for opp in arbitrage_opps:
                    report_parts.append(f"- {opp.get('description', '')}")
    
    # 基本面分析结果
    if analysis_type in ['all', 'fundamental']:
        fundamental_result = state.get('fundamental_analysis_result', {})
        if fundamental_result and not fundamental_result.get('error'):
            report_parts.append("\n### 基本面分析\n")
            
            oi = fundamental_result.get('open_interest', {})
            if oi:
                report_parts.append(f"**持仓量**：")
                report_parts.append(f"  - 趋势：{oi.get('trend', 'unknown')}")
                report_parts.append(f"  - 变化：{oi.get('change_pct', 0):.2f}%")
                report_parts.append(f"  - 分析：{oi.get('analysis', '')}")
            
            volume = fundamental_result.get('volume', {})
            if volume:
                report_parts.append(f"**成交量**：{volume.get('analysis', '')}")
            
            price_oi = fundamental_result.get('price_oi_relationship', {})
            if price_oi:
                report_parts.append(f"**价量关系**：{price_oi.get('relationship', '')}")
            
            summary = fundamental_result.get('summary', '')
            if summary:
                report_parts.append(f"\n**基本面总结**：{summary}")
    
    # 策略推荐
    strategy = state.get('strategy_recommendation', {})
    if strategy and not strategy.get('error'):
        report_parts.append("\n### 交易策略推荐\n")
        report_parts.append(f"**操作建议**：{strategy.get('operation', '观望')}")
        report_parts.append(f"**理由**：{strategy.get('reason', '')}")
        report_parts.append(f"**仓位建议**：{strategy.get('position_suggestion', '0%')}")
        report_parts.append(f"**风险等级**：{strategy.get('risk_level', 'medium')}")
        
        stop_loss = strategy.get('stop_loss')
        if stop_loss:
            report_parts.append(f"\n**止损建议**：")
            report_parts.append(f"  - 止损价格：{stop_loss.get('price', 0):.2f}")
            report_parts.append(f"  - 止损幅度：{stop_loss.get('percentage', 0):.2f}%")
            report_parts.append(f"  - 理由：{stop_loss.get('reason', '')}")
        
        strategy_details = strategy.get('strategy_details', [])
        if strategy_details:
            report_parts.append("\n**策略详情**：")
            for detail in strategy_details:
                report_parts.append(f"- {detail}")
        
        warnings = strategy.get('warnings', [])
        if warnings:
            report_parts.append("\n**风险提示**：")
            for warning in warnings:
                report_parts.append(f"- ⚠️ {warning}")
    
    state['final_report'] = "\n".join(report_parts) if report_parts else "分析完成"
    print(f"[期货最终报告] 报告生成完成，长度: {len(state['final_report'])} 字符")
    return state


def create_futures_analysis_graph() -> StateGraph:
    """创建期货分析工作流图"""
    # 创建状态图
    workflow = StateGraph(FuturesAnalysisState)
    
    # 添加节点
    workflow.add_node("data_fetch", futures_data_fetch_node)
    workflow.add_node("route", lambda state: state)  # 路由节点
    workflow.add_node("game_theory_analysis", futures_game_theory_analysis_node)
    workflow.add_node("risk_analysis", futures_risk_analysis_node)
    workflow.add_node("spread_analysis", futures_spread_analysis_node)
    workflow.add_node("fundamental_analysis", futures_fundamental_analysis_node)
    workflow.add_node("strategy_recommendation", futures_strategy_recommendation_node)
    workflow.add_node("final_report", generate_futures_final_report)
    
    # 设置入口点
    workflow.set_entry_point("data_fetch")
    
    # 添加边
    workflow.add_edge("data_fetch", "route")
    
    # 条件分支：根据分析类型路由
    workflow.add_conditional_edges(
        "route",
        route_futures_analysis,
        {
            "game_theory_only": "game_theory_analysis",
            "risk_only": "risk_analysis",
            "spread_only": "spread_analysis",
            "fundamental_only": "fundamental_analysis",
            "all_analysis": "game_theory_analysis",  # 全部分析时，先进行博弈分析
        },
    )
    
    # 博弈分析后的路由
    def route_after_game_theory(state: FuturesAnalysisState) -> str:
        analysis_type = state.get('analysis_type', 'all')
        if analysis_type == 'all':
            return 'risk_analysis'
        else:
            return 'strategy_recommendation'
    
    workflow.add_conditional_edges(
        "game_theory_analysis",
        route_after_game_theory,
        {
            "risk_analysis": "risk_analysis",
            "strategy_recommendation": "strategy_recommendation",
        },
    )
    
    # 风险管理分析后的路由
    def route_after_risk(state: FuturesAnalysisState) -> str:
        analysis_type = state.get('analysis_type', 'all')
        if analysis_type == 'all':
            return 'spread_analysis'
        else:
            return 'strategy_recommendation'
    
    workflow.add_conditional_edges(
        "risk_analysis",
        route_after_risk,
        {
            "spread_analysis": "spread_analysis",
            "strategy_recommendation": "strategy_recommendation",
        },
    )
    
    # 价差分析后的路由
    def route_after_spread(state: FuturesAnalysisState) -> str:
        analysis_type = state.get('analysis_type', 'all')
        if analysis_type == 'all':
            return 'fundamental_analysis'
        else:
            return 'strategy_recommendation'
    
    workflow.add_conditional_edges(
        "spread_analysis",
        route_after_spread,
        {
            "fundamental_analysis": "fundamental_analysis",
            "strategy_recommendation": "strategy_recommendation",
        },
    )
    
    # 基本面分析后到策略推荐
    workflow.add_edge("fundamental_analysis", "strategy_recommendation")
    
    # 策略推荐后生成最终报告
    workflow.add_edge("strategy_recommendation", "final_report")
    
    # 最终报告后结束
    workflow.add_edge("final_report", END)
    
    return workflow


# 创建图实例
futures_analysis_graph = create_futures_analysis_graph()

# 编译图
compiled_futures_graph = futures_analysis_graph.compile()

