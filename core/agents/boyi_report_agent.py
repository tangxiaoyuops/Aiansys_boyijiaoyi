"""
博弈交易法专业报告生成Agent
按照博弈交易法的方法论生成结构化、逻辑清晰的分析报告
"""
from core.models.state import AnalysisState
from typing import Dict, Any, List
import json


def generate_boyi_report(state: AnalysisState) -> Dict[str, Any]:
    """
    生成博弈交易法专业分析报告
    
    Args:
        state: 包含所有分析结果的状态字典
        
    Returns:
        报告字典，包含完整的结构化报告
    """
    report_parts = []
    
    # 获取各模块分析结果
    stock_data = state.get('stock_data', {})
    llm_stage_result = state.get('llm_stage_result', {})
    llm_distribution_result = state.get('llm_distribution_result', {})
    llm_emotion_result = state.get('llm_emotion_result', {})
    llm_trading_points_result = state.get('llm_trading_points_result', {})
    strategy = state.get('strategy_recommendation', {})
    
    # 股票基本信息
    stock_code = state.get('stock_code', '')
    stock_name = state.get('stock_name', '')
    
    # ========== 一、执行过程总结 ==========
    report_parts.append("# " + stock_code + "博弈分析报告")
    report_parts.append("\n## 一、执行过程总结")
    
    execution_summary = []
    if state.get('stock_data') is not None:
        execution_summary.append(f"成功获取{len(state.get('stock_data', []))}日K线数据")
    if llm_stage_result:
        execution_summary.append("完成阶段分析、O点判断")
    if llm_distribution_result:
        execution_summary.append("出货识别")
    if llm_emotion_result:
        execution_summary.append("情绪比例及锚定状态分析")
    if llm_trading_points_result:
        execution_summary.append("买卖点识别")
    
    # 检查是否有工具报错
    errors = []
    if llm_stage_result.get('error'):
        errors.append(f"阶段分析: {llm_stage_result.get('error')}")
    if llm_distribution_result.get('error'):
        errors.append(f"出货分析: {llm_distribution_result.get('error')}")
    if llm_emotion_result.get('error'):
        errors.append(f"情绪分析: {llm_emotion_result.get('error')}")
    if llm_trading_points_result.get('error'):
        errors.append(f"买卖点分析: {llm_trading_points_result.get('error')}")
    
    if execution_summary:
        report_parts.append(", ".join(execution_summary) + "。")
    if errors:
        report_parts.append("\n**注意**：" + "、".join(errors) + "，但不影响核心结论输出。")
    
    # ========== 二、核心分析结论 ==========
    report_parts.append("\n## 二、核心分析结论")
    
    # 1. 阶段分析
    if llm_stage_result and not llm_stage_result.get('error'):
        stage = llm_stage_result.get('stage', 0)
        stage_name = llm_stage_result.get('stage_name', '未知')
        confidence = llm_stage_result.get('confidence', 0.0)
        reasoning = llm_stage_result.get('reasoning', '')
        
        report_parts.append(f"\n### 1. 趋势定位：{stage_name}（信心度：{confidence:.0%}）")
        
        # 阶段详细描述
        if reasoning:
            # 格式化推理过程
            reasoning_lines = reasoning.split('\n')
            for line in reasoning_lines:
                if line.strip():
                    report_parts.append(line.strip())
        
        # O点分析
        o_point = llm_stage_result.get('o_point', {})
        if o_point.get('has_o_point'):
            o_date = o_point.get('date', '')
            o_price = o_point.get('price', 0)
            o_desc = o_point.get('description', '')
            
            report_parts.append(f"\n**O点分析**：{o_desc}")
            if o_date and o_price:
                report_parts.append(f"\nO点位置：{o_date}，价格 {o_price:.2f}")
        
        # 洗盘分析
        washout = llm_stage_result.get('washout_structure', {})
        if washout.get('has_washout'):
            washout_type = washout.get('washout_type', '')
            washout_desc = washout.get('description', '')
            
            report_parts.append(f"\n**洗盘分析**：{washout_desc}")
            if washout_type:
                report_parts.append(f"\n洗盘类型：{washout_type}")
    
    # 2. 出货分析
    if llm_distribution_result and not llm_distribution_result.get('error'):
        overall_scale = llm_distribution_result.get('overall_scale', 'none')
        scale_map = {
            'large': '大规模',
            'medium': '中等规模',
            'small': '小规模',
            'none': '无明显',
            'unknown': '未知'
        }
        scale_text = scale_map.get(overall_scale, overall_scale)
        
        report_parts.append(f"\n### 2. 出货分析：{scale_text}出货")
        
        latest_cycle = llm_distribution_result.get('latest_cycle_analysis', {})
        if latest_cycle:
            dist_scale = latest_cycle.get('scale', 'none')
            dist_scale_text = scale_map.get(dist_scale, dist_scale)
            start_date = latest_cycle.get('start_date', '')
            end_date = latest_cycle.get('end_date', '')
            reasoning = latest_cycle.get('reasoning', '')
            
            if start_date and end_date:
                report_parts.append(f"\n**最近出货周期**：{start_date} ~ {end_date}")
            
            if reasoning:
                report_parts.append(f"\n{reasoning}")
        
        detailed_analysis = llm_distribution_result.get('detailed_analysis', '')
        if detailed_analysis:
            report_parts.append(f"\n{detailed_analysis}")
        
        risk_warning = llm_distribution_result.get('risk_warning', '')
        if risk_warning:
            report_parts.append(f"\n**出货风险**：{risk_warning}")
    
    # 3. 情绪比例关系
    if llm_emotion_result and not llm_emotion_result.get('error'):
        emotion_ratio = llm_emotion_result.get('emotion_ratio', {})
        anchor = llm_emotion_result.get('anchor', {})
        
        if emotion_ratio:
            direction = emotion_ratio.get('direction', 'neutral')
            direction_map = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
            explanation = emotion_ratio.get('explanation', '')
            
            report_parts.append(f"\n### 3. 情绪比例关系：{direction_map.get(direction, direction)}")
            if explanation:
                report_parts.append(f"\n{explanation}")
        
        if anchor:
            anchor_type = anchor.get('type', 'neutral')
            anchor_type_map = {'bullish': '多方锚定', 'bearish': '空方锚定', 'neutral': '无锚定'}
            anchor_desc = anchor.get('description', '')
            
            report_parts.append(f"\n### 4. 锚定分析：{anchor_type_map.get(anchor_type, anchor_type)}")
            if anchor_desc:
                report_parts.append(f"\n{anchor_desc}")
        
        reasoning = llm_emotion_result.get('reasoning', '')
        if reasoning:
            report_parts.append(f"\n**情绪分析理由**：{reasoning}")
    
    # 4. 买入信号（恐慌点）
    if llm_trading_points_result and not llm_trading_points_result.get('error'):
        buy_signals = llm_trading_points_result.get('buy_signals', [])
        sell_signals = llm_trading_points_result.get('sell_signals', [])
        position_suggestion = llm_trading_points_result.get('position_suggestion', {})
        
        if buy_signals:
            report_parts.append(f"\n### 5. 买入信号（恐慌点）：检测到 {len(buy_signals)} 个买入信号")
            
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
                
                report_parts.append(
                    f"\n{i}. {signal_date}（{type_text}），价格 {signal_price:.2f}，"
                    f"时间要求：{'满足' if meets_time else '不满足'}，"
                    f"数量要求：{'满足' if meets_count else '不满足'}"
                )
        else:
            report_parts.append("\n### 5. 买入信号（恐慌点）：暂未检测到明确的买入信号")
        
        if sell_signals:
            report_parts.append(f"\n### 6. 卖出信号（分水岭）：检测到 {len(sell_signals)} 个卖出信号")
            
            for i, signal in enumerate(sell_signals[:3], 1):  # 最多显示3个
                signal_date = signal.get('date', '未知日期')
                signal_price = signal.get('price', 0)
                signal_type = signal.get('type', 'unknown')
                
                report_parts.append(f"\n{i}. {signal_date}（{signal_type}），价格 {signal_price:.2f}")
        
        # 仓位建议
        if position_suggestion:
            can_buy = position_suggestion.get('can_buy', False)
            buy_reason = position_suggestion.get('buy_reason', '')
            suggested_position = position_suggestion.get('suggested_position', '0%')
            position_reasoning = position_suggestion.get('position_reasoning', '')
            
            report_parts.append(f"\n**仓位建议**：{'可以买入' if can_buy else '不建议买入'}")
            if buy_reason:
                report_parts.append(f"\n{buy_reason}")
            if suggested_position:
                report_parts.append(f"\n建议仓位：{suggested_position}")
            if position_reasoning:
                report_parts.append(f"\n{position_reasoning}")
        
        trading_summary = llm_trading_points_result.get('trading_summary', '')
        if trading_summary:
            report_parts.append(f"\n**买卖点分析总结**：{trading_summary}")
    
    # ========== 三、交易策略推荐 ==========
    if strategy:
        report_parts.append("\n## 三、交易策略推荐")
        
        operation = strategy.get('operation', '观望')
        reason = strategy.get('reason', '')
        position_suggestion = strategy.get('position_suggestion', '0%')
        
        report_parts.append(f"\n**操作建议**：{operation}")
        if reason:
            report_parts.append(f"\n**理由**：{reason}")
        report_parts.append(f"\n**仓位建议**：{position_suggestion}")
        
        strategy_details = strategy.get('strategy_details', [])
        if strategy_details:
            report_parts.append("\n**操作策略**：")
            for detail in strategy_details:
                report_parts.append(f"\n- {detail}")
        
        stop_loss_advice = strategy.get('stop_loss_advice', [])
        if stop_loss_advice:
            report_parts.append("\n**止损建议**：")
            for advice in stop_loss_advice:
                report_parts.append(f"\n- {advice}")
        
        warnings = strategy.get('warnings', [])
        if warnings:
            report_parts.append("\n**风险提示**：")
            for warning in warnings:
                report_parts.append(f"\n- ⚠️ {warning}")
    
    # 汇总报告
    report_text = "\n".join(report_parts)
    
    return {
        'report': report_text,
        'report_parts': report_parts,
        'analysis_complete': True
    }


def boyi_report_node(state: AnalysisState) -> AnalysisState:
    """博弈交易法报告生成节点"""
    report_result = generate_boyi_report(state)
    
    # 更新状态
    state['boyi_report_result'] = report_result
    # 同时更新final_report以保持兼容性
    state['final_report'] = report_result.get('report', '分析完成')
    
    return state
