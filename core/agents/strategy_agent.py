"""
策略推荐Agent
基于分析结果生成交易策略
"""
from core.models.state import AnalysisState
from typing import Dict, Any


def generate_strategy(state: AnalysisState) -> Dict[str, Any]:
    """生成交易策略（基于LLM分析结果）"""
    # 优先使用LLM分析结果
    llm_stage_result = state.get('llm_stage_result') or {}
    llm_distribution_result = state.get('llm_distribution_result') or {}
    llm_emotion_result = state.get('llm_emotion_result') or {}
    llm_trading_points_result = state.get('llm_trading_points_result') or {}
    
    # 回退到旧结果（兼容性）
    stage_result = state.get('stage_result') or {}
    washout_result = state.get('washout_result') or {}
    emotion_result = state.get('emotion_ratio_result') or {}
    anchor_result = state.get('anchor_result') or {}
    o_point_result = state.get('o_point_result') or {}
    distribution_result = state.get('distribution_result') or {}
    
    # 获取阶段信息（优先LLM结果）
    if llm_stage_result and 'error' not in llm_stage_result:
        stage = llm_stage_result.get('stage', 0)
        stage_name = llm_stage_result.get('stage_name', '未知')
        o_point = llm_stage_result.get('o_point', {})
    else:
        stage = stage_result.get('stage', 0)
        stage_name = stage_result.get('stage_name', '未知')
        o_point = {}
    
    # 获取出货信息（优先LLM结果）
    if llm_distribution_result and 'error' not in llm_distribution_result:
        overall_scale = llm_distribution_result.get('overall_scale', 'none')
        latest_cycle = llm_distribution_result.get('latest_cycle_analysis', {})
        risk_warning = llm_distribution_result.get('risk_warning', '')
    else:
        overall_scale = distribution_result.get('scale', 'none')
        latest_cycle = {}
        risk_warning = ''
    
    # 获取情绪信息（优先LLM结果）
    if llm_emotion_result and 'error' not in llm_emotion_result:
        emotion_ratio = llm_emotion_result.get('emotion_ratio', {})
        anchor = llm_emotion_result.get('anchor', {})
        emotion_direction = emotion_ratio.get('direction', 'neutral')
        anchor_type = anchor.get('type', 'none')
    else:
        emotion_direction = emotion_result.get('direction', 'neutral')
        anchor_type = anchor_result.get('anchor_type', 'none')
    
    # 初始化策略
    operation = '观望'
    reason = ''
    position_suggestion = '0%'
    strategy_details = []
    
    # 根据阶段生成策略
    if stage == 1:  # 一阶段
        operation = '买入'
        reason = '一阶段趋势形成初期，适合杀跌入场'
        position_suggestion = '最多1/3仓位'
        strategy_details.append('杀跌入场，谨防破位，严禁追高')
        strategy_details.append('分仓操作，最多买入三分之一仓位')
        strategy_details.append('长期持有，一阶段结束时加仓')
        
        # 检查O点（优先LLM结果）
        if o_point and o_point.get('has_o_point'):
            o_price = o_point.get('price', 0)
            o_desc = o_point.get('description', '')
            strategy_details.append(f'O点已识别：{o_desc}')
        elif o_point_result and o_point_result.get('relative_gain', 0) < 20:
            strategy_details.append('当前相对O点涨幅较小，适合建仓')
    
    elif stage == 2:  # 二阶段
        is_washout = washout_result.get('is_washout', False)
        if is_washout:
            operation = '买入/加仓'
            reason = '二阶段快速上涨，当前处于洗盘状态，适合入场'
            position_suggestion = '逐步加仓至满仓'
            strategy_details.append('在洗盘时入场')
            strategy_details.append('上涨-洗盘-再上涨-再洗盘的循环模式')
        else:
            operation = '持有'
            reason = '二阶段快速上涨中，持有待涨'
            position_suggestion = '保持现有仓位'
    
    elif stage == 3:  # 三阶段
        operation = '卖出/止盈'
        reason = '三阶段疯狂阶段，持续时间短，需及时止盈离场'
        position_suggestion = '逐步减仓至清仓'
        strategy_details.append('及时止盈离场，避免深套')
        strategy_details.append('三阶段必须借助大盘，关注大盘走势')

        # 若检测到高位分水岭风险，强化卖出建议（检查LLM结果中的分水岭）
        structured_data = state.get('structured_data') or {}
        watershed_events = structured_data.get('watershed_events', [])
        if watershed_events:
            latest_watershed = watershed_events[-1]
            ws_price = latest_watershed.get('price', 0)
            ws_date = latest_watershed.get('date', '')
            strategy_details.append(
                f'检测到分水岭事件（{ws_date}，价格约 {ws_price:.2f}），'
                '主力疑似边拉边出货，建议按照1-3成仓位分批减仓，直至清仓。'
            )
    
    elif stage == 4:  # 四阶段
        operation = '观望/止损'
        reason = '四阶段猛烈下跌，避免抄底'
        position_suggestion = '0%'
        strategy_details.append('猛烈下跌阶段，不要轻易入场')
    
    elif stage == 5:  # 五阶段
        operation = '观望'
        reason = '五阶段长期阴跌，消磨意志'
        position_suggestion = '0%'
        strategy_details.append('长期阴跌阶段，等待机会')
    
    # 考虑情绪比例关系
    if emotion_direction == 'bullish' and operation == '观望':
        operation = '买入'
        reason += '；情绪比例关系看涨'
    elif emotion_direction == 'bearish' and operation == '买入':
        operation = '谨慎买入'
        reason += '；情绪比例关系看跌，需谨慎'
    
    # 考虑锚定
    if anchor_type == 'bullish':
        if operation == '买入':
            strategy_details.append('多方锚定形成，买入信号确认')
    elif anchor_type == 'bearish':
        strategy_details.append('空方锚定形成，上涨行情中保持空头思维')
    
    # 止损建议
    stop_loss_advice = []
    if stage in [1, 2]:
        stop_loss_advice.append('有趋势的股票不止损')
        stop_loss_advice.append('正在洗盘行情中的股票不止损')
    else:
        stop_loss_advice.append('看不准的股票必须止损')
        stop_loss_advice.append('让自己受到惊吓的股票必须止损')

    # 结合买卖点分析结果（优先LLM结果）
    if llm_trading_points_result and 'error' not in llm_trading_points_result:
        buy_signals = llm_trading_points_result.get('buy_signals', [])
        sell_signals = llm_trading_points_result.get('sell_signals', [])
        position_suggestion_tp = llm_trading_points_result.get('position_suggestion', {})
        
        # 如果有明确的买卖点建议，优先使用
        if position_suggestion_tp:
            can_buy = position_suggestion_tp.get('can_buy', False)
            buy_reason_tp = position_suggestion_tp.get('buy_reason', '')
            suggested_position_tp = position_suggestion_tp.get('suggested_position', '')
            position_reasoning_tp = position_suggestion_tp.get('position_reasoning', '')
            
            if can_buy and buy_signals:
                # 有买入信号且满足条件
                valid_buy_signals = [
                    s for s in buy_signals
                    if s.get('meets_time_requirement', False) and s.get('meets_panic_count_requirement', False)
                ]
                if valid_buy_signals:
                    operation = '买入'
                    reason = buy_reason_tp if buy_reason_tp else reason
                    if suggested_position_tp:
                        position_suggestion = suggested_position_tp
                    strategy_details.append(f"买卖点分析：{position_reasoning_tp if position_reasoning_tp else '检测到有效买入信号'}")
                    # 列出有效的买入信号
                    for signal in valid_buy_signals[:3]:  # 最多列出3个
                        signal_date = signal.get('date', '')
                        signal_price = signal.get('price', 0)
                        signal_type = signal.get('type', '')
                        strategy_details.append(f"  买入信号：{signal_date}，价格 {signal_price:.2f}（{signal_type}）")
            
            elif not can_buy and buy_reason_tp:
                # 不可以买入，说明原因
                operation = '观望'
                reason = buy_reason_tp
                position_suggestion = '0%'
        
        # 如果有卖出信号（分水岭），强化卖出建议
        if sell_signals:
            for signal in sell_signals:
                signal_date = signal.get('date', '')
                signal_price = signal.get('price', 0)
                signal_type = signal.get('type', '')
                if operation in ['持有', '买入']:
                    operation = '卖出/减仓'
                    reason = f'检测到卖出信号（{signal_type}），建议减仓或清仓'
                strategy_details.append(
                    f"卖出信号：{signal_date}，价格 {signal_price:.2f}（{signal_type}），"
                    "主力疑似边拉边出货，建议按照1-3成仓位分批减仓，直至清仓。"
                )
    
    # 结合上一次出货规模，进一步调整风险与仓位（优先LLM结果）
    dist_scale = overall_scale if overall_scale != 'none' else distribution_result.get('scale', 'none')
    if dist_scale in ['large', 'medium']:
        # 大/中规模出货后，整体建议更保守
        if stage in [1, 2]:
            # 即便阶段显示一二阶段，也要提醒上方有重压
            scale_text = '大' if dist_scale == 'large' else '中等'
            strategy_details.append(
                f"历史上存在{scale_text}规模高位出货，"
                "上方套牢盘较多，本轮上攻接近前高时需明显减仓。"
            )
            if risk_warning:
                strategy_details.append(f"风险提示：{risk_warning}")
            if '仓位' in position_suggestion or '%' in position_suggestion:
                position_suggestion = '不超过1/2仓位，接近前高逐步减仓'
        elif stage == 3:
            # 三阶段 + 曾经大出货风险更高
            scale_text = '大' if dist_scale == 'large' else '中等'
            strategy_details.append(
                f"当前处于三阶段，同时历史曾发生{scale_text}规模出货，"
                "一旦出现高位放量冲高回落，应快速减仓或清仓。"
            )
            if risk_warning:
                strategy_details.append(f"风险提示：{risk_warning}")
    elif dist_scale == 'small':
        strategy_details.append(
            "历史上曾有小规模出货，主力可能边拉边试探，"
            "若本轮再接近前高附近放量冲高回落，同样需考虑减仓。"
        )
    
    return {
        'operation': operation,
        'reason': reason,
        'position_suggestion': position_suggestion,
        'strategy_details': strategy_details,
        'stop_loss_advice': stop_loss_advice,
        'stage': stage,
        'stage_name': stage_name,
        'confidence': 0.7
    }


def strategy_recommendation_node(state: AnalysisState) -> AnalysisState:
    """策略推荐节点"""
    strategy = generate_strategy(state)
    
    # 更新状态
    state['strategy_recommendation'] = strategy
    
    return state


