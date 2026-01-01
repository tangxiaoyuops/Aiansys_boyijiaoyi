"""
分析结果总结Agent
综合所有分析结果，生成总结报告
"""
from core.models.state import AnalysisState
from typing import Dict, Any


def generate_summary(state: AnalysisState) -> Dict[str, Any]:
    """生成分析总结（基于LLM分析结果）"""
    summary_parts = []
    
    # LLM 阶段分析结果
    llm_stage_result = state.get('llm_stage_result') or {}
    if llm_stage_result and 'error' not in llm_stage_result:
        stage_name = llm_stage_result.get('stage_name', '未知')
        reasoning = llm_stage_result.get('reasoning', '')
        confidence = llm_stage_result.get('confidence', 0.0)
        summary_parts.append(f"**阶段分析**：{stage_name}（信心度：{confidence:.0%}）")
        if reasoning:
            summary_parts.append(f"  {reasoning}")
        
        # O点信息
        o_point = llm_stage_result.get('o_point', {})
        if o_point.get('has_o_point'):
            o_date = o_point.get('date', '')
            o_price = o_point.get('price', 0)
            o_desc = o_point.get('description', '')
            summary_parts.append(f"**O点分析**：{o_desc}")
            if o_date and o_price:
                summary_parts.append(f"  O点位置：{o_date}，价格 {o_price:.2f}")
        
        # 洗盘结构
        washout = llm_stage_result.get('washout_structure', {})
        if washout.get('has_washout'):
            washout_type = washout.get('washout_type', '')
            washout_desc = washout.get('description', '')
            summary_parts.append(f"**洗盘分析**：{washout_desc}")
            if washout_type:
                summary_parts.append(f"  洗盘类型：{washout_type}")
    else:
        # 回退到旧结果（兼容性）
        stage_result = state.get('stage_result') or {}
        if stage_result:
            stage_name = stage_result.get('stage_name', '未知')
            stage_desc = stage_result.get('description', '')
            summary_parts.append(f"**阶段分析**：{stage_name} - {stage_desc}")
    
    # LLM 出货分析结果
    llm_distribution_result = state.get('llm_distribution_result') or {}
    if llm_distribution_result and 'error' not in llm_distribution_result:
        overall_scale = llm_distribution_result.get('overall_scale', 'none')
        scale_map = {
            'large': '大规模',
            'medium': '中等规模',
            'small': '小规模',
            'none': '无明显',
            'unknown': '未知'
        }
        scale_text = scale_map.get(overall_scale, overall_scale)
        
        latest_cycle = llm_distribution_result.get('latest_cycle_analysis', {})
        detailed_analysis = llm_distribution_result.get('detailed_analysis', '')
        risk_warning = llm_distribution_result.get('risk_warning', '')
        
        summary_parts.append(f"**出货分析**：{scale_text}出货")
        if latest_cycle:
            start_date = latest_cycle.get('start_date', '')
            end_date = latest_cycle.get('end_date', '')
            reasoning = latest_cycle.get('reasoning', '')
            if start_date and end_date:
                summary_parts.append(f"  最近出货周期：{start_date} ~ {end_date}")
            if reasoning:
                summary_parts.append(f"  {reasoning}")
        if detailed_analysis:
            summary_parts.append(f"  {detailed_analysis}")
        if risk_warning:
            summary_parts.append(f"**出货风险**：{risk_warning}")
    else:
        # 回退到旧结果（兼容性）
        distribution_result = state.get('distribution_result') or {}
        if distribution_result:
            scale = distribution_result.get('scale', 'unknown')
            scale_map = {
                'large': '大规模',
                'medium': '中等规模',
                'small': '小规模',
                'none': '无明显',
                'unknown': '未知'
            }
            scale_text = scale_map.get(scale, scale)
            summary_parts.append(f"**出货分析**：{scale_text}出货")
    
    # LLM 情绪分析结果
    llm_emotion_result = state.get('llm_emotion_result') or {}
    if llm_emotion_result and 'error' not in llm_emotion_result:
        emotion_ratio = llm_emotion_result.get('emotion_ratio', {})
        
        if emotion_ratio:
            direction = emotion_ratio.get('direction', 'neutral')
            direction_map = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
            explanation = emotion_ratio.get('explanation', '')
            summary_parts.append(f"**情绪比例关系**：{direction_map.get(direction, direction)}")
            if explanation:
                summary_parts.append(f"  {explanation}")
        
        anchor = llm_emotion_result.get('anchor', {})
        if anchor:
            anchor_type = anchor.get('type', 'neutral')
            anchor_type_map = {'bullish': '多方锚定', 'bearish': '空方锚定', 'neutral': '无锚定'}
            anchor_desc = anchor.get('description', '')
            summary_parts.append(f"**锚定分析**：{anchor_type_map.get(anchor_type, anchor_type)}")
            if anchor_desc:
                summary_parts.append(f"  {anchor_desc}")
        
        reasoning = llm_emotion_result.get('reasoning', '')
        if reasoning:
            summary_parts.append(f"**情绪分析理由**：{reasoning}")
    else:
        # 回退到旧结果（兼容性）
        emotion_result = state.get('emotion_ratio_result') or {}
        if emotion_result:
            direction = emotion_result.get('future_direction', '中性')
            explanation = emotion_result.get('explanation', '')
            summary_parts.append(f"**情绪比例关系**：{direction} - {explanation}")
    
    # LLM 买卖点分析结果
    llm_trading_points_result = state.get('llm_trading_points_result') or {}
    if llm_trading_points_result and 'error' not in llm_trading_points_result:
        buy_signals = llm_trading_points_result.get('buy_signals', [])
        sell_signals = llm_trading_points_result.get('sell_signals', [])
        position_suggestion = llm_trading_points_result.get('position_suggestion', {})
        trading_summary = llm_trading_points_result.get('trading_summary', '')
        
        if buy_signals:
            summary_parts.append(f"**买入信号（恐慌点）**：检测到 {len(buy_signals)} 个买入信号")
            for i, signal in enumerate(buy_signals[:5], 1):  # 最多显示5个
                signal_date = signal.get('date', '未知日期')
                signal_price = signal.get('price', 0)
                signal_type = signal.get('type', 'unknown')
                signal_type_map = {
                    'stage5_panic': '5阶段恐慌点',
                    'stage1_panic': '1阶段恐慌点',
                    'washout_panic': '洗盘恐慌点',
                    'uptrend_panic': '上涨趋势恐慌点'
                }
                type_text = signal_type_map.get(signal_type, signal_type)
                meets_time = signal.get('meets_time_requirement', False)
                meets_count = signal.get('meets_panic_count_requirement', False)
                summary_parts.append(
                    f"  {i}. {signal_date}（{type_text}），价格 {signal_price:.2f}，"
                    f"时间要求：{'满足' if meets_time else '不满足'}，"
                    f"数量要求：{'满足' if meets_count else '不满足'}"
                )
        
        if sell_signals:
            summary_parts.append(f"**卖出信号（分水岭）**：检测到 {len(sell_signals)} 个卖出信号")
            for i, signal in enumerate(sell_signals[:3], 1):  # 最多显示3个
                signal_date = signal.get('date', '未知日期')
                signal_price = signal.get('price', 0)
                signal_type = signal.get('type', 'unknown')
                summary_parts.append(f"  {i}. {signal_date}（{signal_type}），价格 {signal_price:.2f}")
        
        if position_suggestion:
            can_buy = position_suggestion.get('can_buy', False)
            buy_reason = position_suggestion.get('buy_reason', '')
            suggested_position = position_suggestion.get('suggested_position', '0%')
            position_reasoning = position_suggestion.get('position_reasoning', '')
            
            summary_parts.append(f"**仓位建议**：{'可以买入' if can_buy else '不建议买入'}")
            if buy_reason:
                summary_parts.append(f"  {buy_reason}")
            if suggested_position:
                summary_parts.append(f"  建议仓位：{suggested_position}")
            if position_reasoning:
                summary_parts.append(f"  {position_reasoning}")
        
        if trading_summary:
            summary_parts.append(f"**买卖点分析总结**：{trading_summary}")
    
    summary_text = "\n\n".join(summary_parts) if summary_parts else "分析完成，但未生成详细总结"
    
    return {
        'summary': summary_text,
        'parts': summary_parts,
        'analysis_complete': True
    }


def summary_node(state: AnalysisState) -> AnalysisState:
    """分析结果总结节点"""
    summary_result = generate_summary(state)
    
    # 更新状态
    state['summary_result'] = summary_result
    
    return state


