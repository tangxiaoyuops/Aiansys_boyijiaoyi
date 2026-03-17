"""
大宗商品策略风险评估Agent
评估策略风险，计算风险指标
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.llm_client import call_llm


def strategy_risk_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    风险评估节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[风险评估] 开始评估策略风险")
    
    strategy_signals = state.get("strategy_signals", [])
    structured_analysis = state.get("structured_analysis")
    technical_indicators = state.get("technical_indicators")
    
    if not strategy_signals:
        print("[风险评估] 没有策略信号，跳过风险评估")
        state["risk_metrics"] = None
        return state
    
    system_prompt = """你是一个大宗商品风险管理专家。请对提供的交易策略进行风险评估。

你需要评估以下内容：
1. 策略风险：每个策略的风险水平
2. 组合风险：多个策略的组合风险
3. 风险指标：VaR、最大回撤、夏普比率等
4. 风险建议：风险控制建议

请以JSON格式返回风险评估结果，格式如下：
{{
    "var_95": 95%置信度VaR,
    "var_99": 99%置信度VaR,
    "max_drawdown": 预期最大回撤,
    "sharpe_ratio": 预期夏普比率,
    "sortino_ratio": 预期索提诺比率,
    "calmar_ratio": 预期卡玛比率,
    "volatility": 预期波动率,
    "beta": Beta系数（可选）,
    "alpha": Alpha系数（可选）,
    "information_ratio": 信息比率（可选）,
    "risk_assessment": "整体风险评估（low/medium/high）",
    "risk_recommendations": ["风险建议1", "风险建议2", ...]
}}"""

    strategies_summary = ""
    for i, strategy in enumerate(strategy_signals):
        strategies_summary += f"""
策略{i+1}:
- 类型: {strategy.get('strategy_type')}
- 方向: {strategy.get('direction')}
- 入场价: {strategy.get('entry_price')}
- 目标价: {strategy.get('target_price')}
- 止损价: {strategy.get('stop_loss')}
- 仓位: {strategy.get('position_size')}
- 风险收益比: {strategy.get('risk_reward_ratio')}
- 置信度: {strategy.get('confidence')}
"""

    user_prompt = f"""请对以下交易策略进行风险评估：

市场状态：{state.get('market_state')}
策略数量：{len(strategy_signals)}

策略详情：
{strategies_summary}

基本面分析：
- 市场分类: {structured_analysis.get('classification')}
- 驱动因子: {structured_analysis.get('key_drivers')}
- 置信度: {structured_analysis.get('confidence')}

技术指标：
- RSI: {technical_indicators.get('rsi')}
- ATR: {technical_indicators.get('atr')}
- 布林带宽度: {technical_indicators.get('bollinger_upper') and technical_indicators.get('bollinger_lower') and technical_indicators.get('bollinger_upper') - technical_indicators.get('bollinger_lower')}

请进行风险评估，计算各项风险指标。"""

    try:
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        import json
        risk_metrics = json.loads(result)
        
        state["risk_metrics"] = risk_metrics
        
        print(f"[风险评估] 风险评估完成")
        print(f"[风险评估] 整体风险: {risk_metrics.get('risk_assessment')}")
        print(f"[风险评估] VaR(95%): {risk_metrics.get('var_95')}")
        print(f"[风险评估] 最大回撤: {risk_metrics.get('max_drawdown')}")
        print(f"[风险评估] 夏普比率: {risk_metrics.get('sharpe_ratio')}")
        
    except Exception as e:
        error_msg = f"风险评估失败: {str(e)}"
        print(f"[风险评估] {error_msg}")
        state["risk_metrics"] = None
    
    return state
