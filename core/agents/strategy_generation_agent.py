"""
大宗商品策略生成Agent
综合基本面与技术面，生成买卖策略
"""
from typing import Dict, Any
from datetime import datetime
from core.models.commodity_state import CommodityAnalysisState
from core.tools.llm_client import call_llm


def strategy_generation_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    策略生成节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[策略生成] 开始生成买卖策略")
    
    structured_analysis = state.get("structured_analysis")
    technical_indicators = state.get("technical_indicators")
    market_state = state.get("market_state")
    strategy_type = state.get("strategy_type", "trend")
    raw_evidence = state.get("raw_evidence")
    
    if not structured_analysis or not technical_indicators:
        print("[策略生成] 警告: 缺少分析数据")
        state["strategy_signals"] = []
        state["strategy_confidence"] = 0.0
        return state
    
    # 获取当前时间
    current_date = datetime.now().strftime("%Y年%m月%d日")
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    system_prompt = f"""你是一个大宗商品交易策略专家。请基于提供的基本面和技术面分析，生成买卖策略。

**重要时间信息**：
- 当前日期：{current_date}
- 策略的时间周期和预测必须基于当前日期（{current_date}）
- 例如：短期策略指未来1-7天，中期策略指未来1-4周，长期策略指未来1-3个月

策略类型：{strategy_type}

你需要考虑以下因素：
1. 基本面分析：供给、需求、价格走势、驱动因子
2. 技术面分析：趋势、动量、波动率、支撑阻力
3. 市场状态：{market_state}
4. 风险收益比：确保策略有合理的风险收益比

请以JSON格式返回策略信号，格式如下：
{{
    "strategies": [
        {{
            "strategy_type": "策略类型（trend/arbitrage/hedge/event_driven）",
            "commodity_id": "品种ID",
            "contract": "合约",
            "direction": "方向（long/short）",
            "entry_price": 入场价格,
            "target_price": 目标价格,
            "stop_loss": 止损价格,
            "position_size": 仓位规模（手数）,
            "confidence": 置信度（0-1）,
            "time_horizon": "时间周期（short_term/medium_term/long_term）",
            "reasoning": "策略逻辑说明",
            "risk_reward_ratio": 风险收益比,
            "indicators": {{
                "ma_short": 短期均线,
                "ma_medium": 中期均线,
                "ma_long": 长期均线,
                "rsi": RSI值,
                "macd_bar": MACD柱
            }},
            "fundamental_factors": ["基本面因素1", "基本面因素2"],
            "generated_at": "生成时间"
        }}
    ],
    "overall_confidence": 整体置信度（0-1）
}}

如果没有明确的交易机会，请返回空的strategies数组。"""

    user_prompt = f"""请基于以下分析生成买卖策略：

品种/产业链：{raw_evidence.get('commodity_or_chain', '未知')}
策略类型：{strategy_type}
市场状态：{market_state}

基本面分析：
- 摘要: {structured_analysis.get('summary')}
- 市场分类: {structured_analysis.get('classification')}
- 驱动因子: {structured_analysis.get('key_drivers')}
- 供给链摘要: {structured_analysis.get('supply_chain_summary')}
- 价格摘要: {structured_analysis.get('price_summary')}
- 置信度: {structured_analysis.get('confidence')}

技术指标：
- MA短期: {technical_indicators.get('ma_short')}
- MA中期: {technical_indicators.get('ma_medium')}
- MA长期: {technical_indicators.get('ma_long')}
- MACD柱: {technical_indicators.get('macd_bar')}
- RSI: {technical_indicators.get('rsi')}
- 布林带上轨: {technical_indicators.get('bollinger_upper')}
- 布林带下轨: {technical_indicators.get('bollinger_lower')}
- ATR: {technical_indicators.get('atr')}

请生成买卖策略，包括入场点位、止损止盈、仓位规模等。"""

    try:
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        print(f"[策略生成] LLM返回内容: {result[:500]}...")
        
        import json
        import re
        
        # 尝试提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            json_str = json_match.group(0)
            print(f"[策略生成] 提取的JSON: {json_str[:200]}...")
            strategy_result = json.loads(json_str)
        else:
            print(f"[策略生成] 未找到JSON格式，尝试直接解析")
            strategy_result = json.loads(result)
        
        strategies = strategy_result.get("strategies", [])
        
        for strategy in strategies:
            strategy["generated_at"] = datetime.now().isoformat()
        
        state["strategy_signals"] = strategies
        state["strategy_confidence"] = strategy_result.get("overall_confidence", 0.0)
        
        print(f"[策略生成] 策略生成完成")
        print(f"[策略生成] 生成策略数量: {len(strategies)}")
        print(f"[策略生成] 整体置信度: {state['strategy_confidence']}")
        
        for i, strategy in enumerate(strategies):
            print(f"[策略生成] 策略{i+1}: {strategy.get('direction')} @ {strategy.get('entry_price')}, 目标: {strategy.get('target_price')}, 止损: {strategy.get('stop_loss')}")
        
    except Exception as e:
        error_msg = f"策略生成失败: {str(e)}"
        print(f"[策略生成] {error_msg}")
        print(f"[策略生成] LLM返回内容: {result if 'result' in locals() else '无'}")
        state["strategy_signals"] = []
        state["strategy_confidence"] = 0.0
    
    return state
