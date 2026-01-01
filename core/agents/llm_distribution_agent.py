"""
LLM 出货分析 Agent
使用大模型分析出货规模、分水岭、历史周期
"""
from core.models.state import AnalysisState
from core.tools.llm_client import call_llm
from typing import Dict, Any
import json


def build_distribution_analysis_prompt(structured_data: Dict[str, Any]) -> str:
    """构建出货分析的提示词（覆盖往前3年的所有出货情况）"""
    stock_code = structured_data.get('stock_code', '')
    stock_name = structured_data.get('stock_name', '')
    recent_bars = structured_data.get('recent_bars', [])
    watershed_events = structured_data.get('watershed_events', [])
    distribution_cycles = structured_data.get('distribution_cycles', [])
    distribution_start_signals = structured_data.get('distribution_start_signals', [])
    
    # 计算往前3年的数据范围（约750个交易日）
    # 确保分析覆盖往前3年的所有出货情况
    
    # 构建出货起始信号文本
    start_signals_text = "【出货起始信号（出货计算起点）】\n"
    if distribution_start_signals:
        start_signals_text += "重要：出货时间的计算应该从这些起始信号开始，而不是从其他时间点开始。\n"
        for i, signal in enumerate(distribution_start_signals, 1):
            start_signals_text += (
                f"{i}. {signal['date']}：收盘价 {signal['price']:.2f}，"
                f"{signal['description']}\n"
            )
    else:
        start_signals_text += "未检测到明确的出货起始信号（连续2-3根放量大阳线突破前高）\n"
    
    # 构建分水岭事件文本
    watershed_text = "【分水岭事件列表】\n"
    if watershed_events:
        for i, event in enumerate(watershed_events, 1):
            watershed_text += (
                f"{i}. {event['date']}：收盘价 {event['price']:.2f}，"
                f"突破前高 {event['breakthrough_price']:.2f}，"
                f"放量倍数 {event['volume_ratio']:.2f}倍，"
                f"{'涨停' if event['is_limit_up'] else '大阳'}，"
                f"后续最大涨幅 {event['post_max_gain']:.1f}%，"
                f"最大跌幅 {event['post_max_drop']:.1f}%\n"
            )
    else:
        watershed_text += "未检测到分水岭事件\n"
    
    # 构建出货周期文本
    cycles_text = "【出货周期列表】\n"
    if distribution_cycles:
        for i, cycle in enumerate(distribution_cycles, 1):
            scale_map = {'small': '小规模', 'medium': '中等规模', 'large': '大规模'}
            cycles_text += (
                f"周期{i}：{scale_map.get(cycle['scale'], cycle['scale'])}出货\n"
                f"  时间范围：{cycle['start_date']} ~ {cycle['end_date']}（{cycle['cycle_days']}天）\n"
                f"  最高价：{cycle['max_price']:.2f}，最低价：{cycle['min_price_in_cycle']:.2f}\n"
                f"  分水岭次数：{cycle['total_watershed_count']}\n"
                f"  周期后最大跌幅：{cycle['post_cycle_drop_pct']:.1f}%（持续{cycle['post_cycle_drop_days']}天）\n"
            )
            if cycle.get('segments'):
                cycles_text += "  内部片段：\n"
                for seg in cycle['segments']:
                    cycles_text += (
                        f"    - {seg['start_date']} ~ {seg['end_date']}："
                        f"价格区间 {seg['low_price']:.2f} ~ {seg['high_price']:.2f}，"
                        f"放量倍数 {seg['volume_ratio']:.2f}倍，"
                        f"分水岭 {seg['watershed_count']}次，"
                        f"后续跌幅 {seg['post_drop_pct']:.1f}%\n"
                    )
    else:
        cycles_text += "未检测到明显的出货周期\n"
    
    # 构建最近K线数据文本
    recent_bars_text = "【最近K线数据（时间顺序，越往下越新）】\n"
    recent_bars_text += "格式：日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅(%) | 成交量(万手)\n"
    for bar in recent_bars[-180:]:  # 只取最近180天
        recent_bars_text += (
            f"{bar['date']} | {bar['open']:.2f} | {bar['high']:.2f} | "
            f"{bar['low']:.2f} | {bar['close']:.2f} | {bar['change_pct']:.2f} | "
            f"{bar['volume']:.2f}\n"
        )
    
    prompt = f"""你是一名擅长博弈交易结构分析的资深交易员。现在请你判断股票 {stock_code}（{stock_name}）的出货规模。

**重要**：请分析往前3年（约750个交易日）内的所有出货情况，包括不同规模的出货周期。

【出货规模定义】

1. 小规模出货：
   - 持续时间较短（通常几天到几周）
   - 通常围绕某次高调突破或分水岭附近，放量明显，但总体出货时间不长
   - 后续可能是中短期下跌或震荡，但不一定进入多年大熊

2. 中等规模出货：
   - 出货时间通常在 1~3 个月左右
   - 在同一高位价区附近，可以看到 2 次及以上分水岭结构，或者多次高调突破+放量震荡
   - 出货结束后，往往会有数个月到一年左右的下跌或弱势震荡

3. 大规模出货：
   - 出货周期很长（接近或超过一年），其间多次出现分水岭结构
   - 出货结束后，往往是 1~2 年级别的深跌 + 低位阴跌，等这轮熊市走完才有新行情
   - 典型例子：2019~2020年600536那种：多次分水岭、高位长时间震荡，然后两年大跌

【出货时间计算的起始点（重要）】

出货时间的计算必须从以下起始信号开始：
- **起始信号**：高调放量突破前高
- 这是主力开始出货的标志性起点，出货时间应该从这个位置开始计算
- 不要从其他时间点（如高位震荡开始、分水岭事件等）开始计算出货时间
- 如果检测到多个起始信号，应该分别计算每个出货周期的时间

【当前股票的结构化信息】

{start_signals_text}

{watershed_text}

{cycles_text}

{recent_bars_text}

【请输出JSON格式的分析结果】

请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
    "overall_scale": "small/medium/large/none（最近一轮出货的规模）",
    "latest_cycle_analysis": {{
        "scale": "small/medium/large/none",
        "start_date": "开始日期（必须从出货起始信号开始，即连续2-3根放量大阳线突破前高的日期）",
        "end_date": "结束日期",
        "start_signal_date": "对应的出货起始信号日期（如果有）",
        "reasoning": "为什么判断是这个规模（参考：分水岭次数、出货时长（从起始信号开始计算）、放量特征、出货后下跌幅度和持续时间等）"
    }},
    "historical_cycles": [
        {{
            "cycle_index": 1,
            "scale": "small/medium/large",
            "reasoning": "这个周期的分析理由"
        }}
    ],
    "risk_warning": "最近一轮出货对当前持仓的风险提示（比如：是否仍在大规模出货的阴影之下）",
    "confidence": 0.0-1.0的浮点数,
    "detailed_analysis": "你的详细分析（自然语言，解释整体出货情况）"
}}
"""
    return prompt


def llm_distribution_analysis_node(state: AnalysisState) -> AnalysisState:
    """LLM出货分析节点"""
    structured_data = state.get('structured_data')
    if not structured_data:
        state['llm_distribution_result'] = {
            'error': '缺少结构化数据，请先运行structured_data_node'
        }
        return state
    
    # 构建提示词
    user_prompt = build_distribution_analysis_prompt(structured_data)
    system_prompt = "你是一名擅长博弈交易结构分析的资深交易员，严格按照用户给出的出货规模定义来判断，并以JSON格式输出结果。"
    
    # 调用LLM
    llm_response = call_llm(system_prompt, user_prompt, temperature=0.3)
    
    # 解析LLM返回的JSON
    try:
        # 尝试提取JSON（可能LLM返回了其他文字）
        import re
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(llm_response)
        
        # 验证必要字段
        if 'overall_scale' not in result:
            result['overall_scale'] = 'none'
        
        state['llm_distribution_result'] = result
    except Exception as e:
        print(f"[LLM出货分析] JSON解析失败: {e}")
        print(f"LLM原始返回: {llm_response}")
        state['llm_distribution_result'] = {
            'overall_scale': 'none',
            'error': f'LLM返回解析失败: {str(e)}',
            'raw_response': llm_response
        }
    
    return state

