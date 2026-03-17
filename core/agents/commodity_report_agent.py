"""
大宗商品报告生成Agent
生成最终分析报告
"""
from typing import Dict, Any
from datetime import datetime
from core.models.commodity_state import CommodityAnalysisState
from core.tools.llm_client import call_llm


def commodity_report_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    报告生成节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[报告生成] 开始生成最终报告")
    
    structured_analysis = state.get("structured_analysis")
    strategy_signals = state.get("strategy_signals", [])
    backtest_results = state.get("backtest_results", [])
    risk_metrics = state.get("risk_metrics")
    raw_evidence = state.get("raw_evidence")
    market_state = state.get("market_state")
    technical_indicators = state.get("technical_indicators")
    
    print(f"[报告生成] raw_evidence: {raw_evidence}")
    print(f"[报告生成] state中的commodity_or_chain: {state.get('commodity_or_chain')}")
    
    # 安全获取 raw_evidence 中的数据
    commodity_or_chain = raw_evidence.get('commodity_or_chain', '未知') if raw_evidence else state.get('commodity_or_chain', '未知')
    time_range_str = raw_evidence.get('time_range', '未指定') if raw_evidence else '未指定'
    
    print(f"[报告生成] 最终使用的品种: {commodity_or_chain}")
    
    # 获取当前时间
    current_date = datetime.now().strftime("%Y年%m月%d日")
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    system_prompt = f"""你是一个大宗商品市场分析报告专家。请基于提供的分析结果生成一份完整的分析报告。

**重要时间信息**：
- 当前日期：{current_date}
- 分析报告中的所有时间节点必须基于当前日期（{current_date}）
- 未来预测和建议的时间节点必须相对于当前日期计算
- 例如：如果当前是{current_year}年{current_month}月，那么"下个月"指的是{current_year}年{current_month+1}月

报告应包含以下部分：
1. 市场概况：品种、时间范围、市场状态
2. 基本面分析：供给链、价格走势、驱动因子
3. 技术面分析：技术指标、市场状态识别
4. 买卖策略：策略信号、入场点位、止损止盈
5. 风险评估：风险指标、风险建议
6. 回测结果：策略历史表现
7. 结论与建议：综合判断、操作建议

请以Markdown格式生成报告，使用清晰的标题和格式。"""
    
    user_prompt = f"""请生成大宗商品分析报告：

品种/产业链：{commodity_or_chain}
时间范围：{time_range_str}
市场状态：{market_state}

**重要提示**：以下所有数据均为真实采集的数据，请在报告中准确使用这些数据，不要编造或修改任何数值。

基本面分析："""
    
    if structured_analysis:
        user_prompt += f"""
- 摘要: {structured_analysis.get('summary')}
- 市场分类: {structured_analysis.get('classification')}
- 驱动因子: {structured_analysis.get('key_drivers')}
- 供给链摘要: {structured_analysis.get('supply_chain_summary')}
- 价格摘要: {structured_analysis.get('price_summary')}
- 置信度: {structured_analysis.get('confidence')}
"""
    else:
        user_prompt += "\n- 暂无基本面分析数据"
    
    user_prompt += f"""
技术指标（真实计算结果，请准确使用）："""
    
    if technical_indicators:
        user_prompt += f"""
- MA短期(5日): {technical_indicators.get('ma_short')}
- MA中期(20日): {technical_indicators.get('ma_medium')}
- MA长期(60日): {technical_indicators.get('ma_long')}
- MACD柱: {technical_indicators.get('macd_bar')}
- MACD DIF: {technical_indicators.get('macd_dif')}
- MACD DEA: {technical_indicators.get('macd_dea')}
- RSI(14): {technical_indicators.get('rsi')}
- 布林带上轨: {technical_indicators.get('bollinger_upper')}
- 布林带中轨: {technical_indicators.get('bollinger_middle')}
- 布林带下轨: {technical_indicators.get('bollinger_lower')}
- ATR(14): {technical_indicators.get('atr')}
- KDJ K: {technical_indicators.get('kdj_k')}
- KDJ D: {technical_indicators.get('kdj_d')}
- KDJ J: {technical_indicators.get('kdj_j')}
- CCI: {technical_indicators.get('cci')}
"""
    else:
        user_prompt += "\n- 暂无技术指标数据"
    
    user_prompt += f"""
买卖策略（{len(strategy_signals)}个）："""
    
    for i, strategy in enumerate(strategy_signals):
        user_prompt += f"""
策略{i+1}:
- 类型: {strategy.get('strategy_type')}
- 方向: {strategy.get('direction')}
- 入场价: {strategy.get('entry_price')}
- 目标价: {strategy.get('target_price')}
- 止损价: {strategy.get('stop_loss')}
- 仓位: {strategy.get('position_size')}
- 风险收益比: {strategy.get('risk_reward_ratio')}
- 置信度: {strategy.get('confidence')}
- 逻辑: {strategy.get('reasoning')}
"""
    
    if risk_metrics:
        user_prompt += f"""
风险评估：
- 整体风险: {risk_metrics.get('risk_assessment')}
- VaR(95%): {risk_metrics.get('var_95')}
- 最大回撤: {risk_metrics.get('max_drawdown')}
- 夏普比率: {risk_metrics.get('sharpe_ratio')}
- 风险建议: {risk_metrics.get('risk_recommendations')}
"""
    else:
        user_prompt += "\n- 暂无风险评估数据"
    
    if backtest_results:
        user_prompt += f"""
回测结果（{len(backtest_results)}个）："""
        for i, result in enumerate(backtest_results):
            user_prompt += f"""
策略{i+1}回测：
- 总收益率: {result['total_return']:.2f}%
- 年化收益率: {result['annual_return']:.2f}%
- 夏普比率: {result['sharpe_ratio']:.2f}
- 最大回撤: {result['max_drawdown']:.2f}%
- 胜率: {result['win_rate']:.2f}%
- 盈亏比: {result['profit_factor']:.2f}
- 交易次数: {result['trade_count']}
"""
    else:
        user_prompt += "\n- 暂无回测数据"
    
    user_prompt += """
请基于以上信息生成一份完整的大宗商品分析报告，包括市场概况、基本面分析、技术面分析、买卖策略、风险评估、回测结果和结论建议。"""

    try:
        report = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.5
        )
        
        state["final_report"] = report
        
        # 安全构建 structured_output
        structured_output = {}
        
        if raw_evidence:
            structured_output["commodity_or_chain"] = raw_evidence.get("commodity_or_chain")
            structured_output["time_range"] = raw_evidence.get("time_range")
        
        if market_state:
            structured_output["market_state"] = market_state
        
        if structured_analysis:
            structured_output["structured_analysis"] = structured_analysis
        
        if technical_indicators:
            structured_output["technical_indicators"] = {
                "ma_short": technical_indicators.get("ma_short"),
                "ma_medium": technical_indicators.get("ma_medium"),
                "ma_long": technical_indicators.get("ma_long"),
                "rsi": technical_indicators.get("rsi"),
                "macd_bar": technical_indicators.get("macd_bar")
            }
        
        structured_output["strategy_signals"] = strategy_signals
        
        if risk_metrics:
            structured_output["risk_metrics"] = risk_metrics
        
        if backtest_results:
            structured_output["backtest_results"] = [
                {
                    "strategy_id": r.get("strategy_id"),
                    "total_return": r.get("total_return"),
                    "sharpe_ratio": r.get("sharpe_ratio"),
                    "max_drawdown": r.get("max_drawdown"),
                    "win_rate": r.get("win_rate")
                }
                for r in backtest_results
            ]
        
        state["structured_output"] = structured_output
        
        import time
        state["end_time"] = time.time()
        state["total_duration"] = state["end_time"] - state.get("start_time", state["end_time"])
        
        print(f"[报告生成] 报告生成完成")
        print(f"[报告生成] 总耗时: {state['total_duration']:.2f}秒")
        
    except Exception as e:
        error_msg = f"报告生成失败: {str(e)}"
        print(f"[报告生成] {error_msg}")
        state["final_report"] = f"报告生成失败: {error_msg}"
        state["structured_output"] = None
    
    return state
