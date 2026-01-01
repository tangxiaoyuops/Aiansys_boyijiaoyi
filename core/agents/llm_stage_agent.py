"""
LLM 阶段分析 Agent
使用大模型分析股票阶段、O点、洗盘结构
"""
from core.models.state import AnalysisState
from core.tools.llm_client import call_llm
from typing import Dict, Any
import json


def build_stage_analysis_prompt(structured_data: Dict[str, Any], distribution_result: Dict[str, Any] = None) -> str:
    """构建阶段分析的提示词"""
    stock_code = structured_data.get('stock_code', '')
    stock_name = structured_data.get('stock_name', '')
    recent_bars = structured_data.get('recent_bars', [])
    stage_candidates = structured_data.get('stage_candidates', [])
    technical_indicators = structured_data.get('technical_indicators', {})
    distribution_cycles = structured_data.get('distribution_cycles', [])
    
    # 构建技术指标文本
    indicators_text = "【技术指标（辅助判断）】\n"
    if technical_indicators:
        # 涨跌幅
        gains_info = []
        for period in [20, 60, 120, 180]:
            gain_key = f'gain{period}'
            if gain_key in technical_indicators and technical_indicators[gain_key] is not None:
                gains_info.append(f"近{period}日涨跌幅：{technical_indicators[gain_key]:.2f}%")
        if gains_info:
            indicators_text += "涨跌幅：\n  " + "\n  ".join(gains_info) + "\n"
        
        # 回撤
        mdd_info = []
        for period in [60, 120, 180]:
            mdd_key = f'max_drawdown_{period}'
            if mdd_key in technical_indicators and technical_indicators[mdd_key] is not None:
                mdd_info.append(f"近{period}日最大回撤：{technical_indicators[mdd_key]:.2f}%")
        if mdd_info:
            indicators_text += "最大回撤：\n  " + "\n  ".join(mdd_info) + "\n"
        
        # 波动率
        if 'volatility_20' in technical_indicators and technical_indicators['volatility_20'] is not None:
            indicators_text += f"波动率：近20日 {technical_indicators['volatility_20']:.2f}%，"
        if 'volatility_60' in technical_indicators and technical_indicators['volatility_60'] is not None:
            indicators_text += f"近60日 {technical_indicators['volatility_60']:.2f}%\n"
        
        # 距离高点
        if 'days_from_high' in technical_indicators:
            indicators_text += f"距离高点：{technical_indicators['days_from_high']}天，"
        if 'high_gap_pct' in technical_indicators:
            indicators_text += f"当前价相对高点：{technical_indicators['high_gap_pct']:.2f}%\n"
        
        # 均线
        if 'current_price' in technical_indicators:
            indicators_text += f"当前价格：{technical_indicators['current_price']:.2f}\n"
        ma_info = []
        for ma in ['ma5', 'ma20', 'ma60']:
            if ma in technical_indicators and technical_indicators[ma] is not None:
                ma_info.append(f"{ma.upper()}：{technical_indicators[ma]:.2f}")
        if ma_info:
            indicators_text += "均线：\n  " + "，".join(ma_info) + "\n"
        
        # 洗盘指标
        if 'washout' in technical_indicators and technical_indicators['washout']:
            washout = technical_indicators['washout']
            indicators_text += "洗盘特征：\n"
            if 'volatility' in washout:
                indicators_text += f"  波动率：{washout['volatility']:.2f}\n"
            if 'down_ratio' in washout:
                indicators_text += f"  下跌天数比例：{washout['down_ratio']:.2%}\n"
            if 'max_drawdown' in washout:
                indicators_text += f"  最大回撤：{washout['max_drawdown']:.2f}%\n"
        
        # O点信息
        if 'o_point' in technical_indicators and technical_indicators['o_point']:
            o_point = technical_indicators['o_point']
            indicators_text += f"O点：{o_point.get('o_point_date', '')}，价格 {o_point.get('o_point_price', 0):.2f}，"
            indicators_text += f"当前相对O点涨幅：{o_point.get('relative_gain', 0):.2f}%\n"
    else:
        indicators_text += "技术指标数据不足\n"
    
    # 构建最近K线数据文本
    recent_bars_text = "【最近K线数据（时间顺序，越往下越新）】\n"
    recent_bars_text += "格式：日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅(%) | 成交量(万手)\n"
    for bar in recent_bars[-180:]:  # 只取最近180天
        recent_bars_text += (
            f"{bar['date']} | {bar['open']:.2f} | {bar['high']:.2f} | "
            f"{bar['low']:.2f} | {bar['close']:.2f} | {bar['change_pct']:.2f} | "
            f"{bar['volume']:.2f}\n"
        )
    
    # 构建阶段候选区间文本
    candidates_text = "【阶段候选区间】\n"
    if stage_candidates:
        for cand in stage_candidates:
            candidates_text += f"- {cand.get('name', '')}：{cand.get('description', '')}\n"
            if 'date' in cand:
                candidates_text += f"  时间：{cand['date']}，价格：{cand.get('price', 0):.2f}\n"
            elif 'start_date' in cand:
                candidates_text += (
                    f"  时间范围：{cand['start_date']} ~ {cand['end_date']}，"
                    f"价格区间：{cand.get('low_price', 0):.2f} ~ {cand.get('high_price', 0):.2f}\n"
                )
    else:
        candidates_text += "未识别到明显的阶段候选区间\n"
    
    # 构建出货分析结果信息（优先使用LLM分析结果，如果没有则使用结构化数据）
    distribution_info_text = "【出货分析结果（用于判断五阶段是否结束）】\n"
    
    if distribution_result and not distribution_result.get('error'):
        # 使用LLM出货分析的结果
        overall_scale = distribution_result.get('overall_scale', 'none')
        latest_cycle_analysis = distribution_result.get('latest_cycle_analysis', {})
        historical_cycles = distribution_result.get('historical_cycles', [])
        
        scale_map = {'small': '小规模', 'medium': '中等规模', 'large': '大规模', 'none': '无明显出货'}
        scale_text = scale_map.get(overall_scale, overall_scale)
        
        distribution_info_text += f"最近一轮出货规模：{scale_text}\n"
        
        if latest_cycle_analysis:
            dist_scale = latest_cycle_analysis.get('scale', 'none')
            dist_scale_text = scale_map.get(dist_scale, dist_scale)
            distribution_info_text += (
                f"最近一轮出货周期：{dist_scale_text}出货\n"
                f"  出货开始日期：{latest_cycle_analysis.get('start_date', '未知')}\n"
                f"  出货结束日期：{latest_cycle_analysis.get('end_date', '未知')}\n"
                f"  出货起始信号日期：{latest_cycle_analysis.get('start_signal_date', '未知')}\n"
            )
            reasoning = latest_cycle_analysis.get('reasoning', '')
            if reasoning:
                distribution_info_text += f"  判断理由：{reasoning}\n"
        
        if historical_cycles:
            distribution_info_text += "\n历史出货周期（往前3年）：\n"
            for i, cycle in enumerate(historical_cycles, 1):
                cycle_scale = cycle.get('scale', 'unknown')
                cycle_scale_text = scale_map.get(cycle_scale, cycle_scale)
                distribution_info_text += (
                    f"  周期{i}：{cycle_scale_text}出货"
                )
                if cycle.get('start_date'):
                    distribution_info_text += f"，时间：{cycle.get('start_date')} ~ {cycle.get('end_date', '未知')}"
                distribution_info_text += "\n"
                cycle_reasoning = cycle.get('reasoning', '')
                if cycle_reasoning:
                    distribution_info_text += f"    理由：{cycle_reasoning}\n"
        
        distribution_info_text += (
            "\n判断五阶段是否结束的参考：\n"
            f"- 小规模出货后至少需要3个月（约90天）\n"
            f"- 中等规模出货后至少需要6个月（约180天）\n"
            f"- 大规模出货后至少需要1年（约250个交易日）\n"
            f"- 当前距离最近一次出货结束的时间需要结合K线数据计算\n"
        )
        
        risk_warning = distribution_result.get('risk_warning', '')
        if risk_warning:
            distribution_info_text += f"\n风险提示：{risk_warning}\n"
    elif distribution_cycles:
        # 如果没有LLM结果，使用结构化数据中的周期信息
        latest_cycle = distribution_cycles[-1] if distribution_cycles else None
        if latest_cycle:
            scale_map = {'small': '小规模', 'medium': '中等规模', 'large': '大规模'}
            scale_text = scale_map.get(latest_cycle.get('scale', 'unknown'), latest_cycle.get('scale', 'unknown'))
            distribution_info_text += (
                f"最近一次出货：{scale_text}出货\n"
                f"  出货结束日期：{latest_cycle.get('end_date', '未知')}\n"
                f"  出货规模：{scale_text}\n"
                f"  出货周期天数：{latest_cycle.get('cycle_days', 0)}天\n"
            )
            distribution_info_text += (
                "\n判断五阶段是否结束的参考：\n"
                f"- 小规模出货后至少需要3个月（约90天）\n"
                f"- 中等规模出货后至少需要6个月（约180天）\n"
                f"- 大规模出货后至少需要1年（约250个交易日）\n"
                f"- 当前距离最近一次出货结束的时间需要结合K线数据计算\n"
            )
    else:
        distribution_info_text += "未检测到明显的出货周期\n"
    
    prompt = f"""你是一名擅长博弈交易法分析的资深交易员。现在请你分析股票 {stock_code}（{stock_name}）的当前阶段。

【阶段定义（博弈交易法）】

一阶段（趋势形成初期）：
- 特征：缓慢且隐蔽的上涨，承接上一轮五阶段下跌后的底部
- 始于O点（恐慌低点后的反弹起点）
- 可以偶有大阳线或涨停，但出现后必须立刻掉头猛跌
- 作用：消磨散户持股意志，产生极度悲观情绪
- 持续时间：因人而异，可能1个月到2年

二阶段（快速上涨阶段）：
- 特征：快速上涨并在高位长期维持，期间伴随持续洗盘
- 上涨幅度最大的阶段，通常涨幅超过三阶段
- 高位运行，趋势结束前不会再现低位价格
- 识别重点：洗盘出货比例关系（牛股结构）
- 持续时间：通常按月计算，可能数月或数年

三阶段（疯狂上涨阶段）：
- 特征：利用散户贪婪和冲动情绪，使其在高位追高被套
- 持续时间短，通常不超过3个月
- 象征性洗盘（浮皮潦草，只持续1天或半天）， 阳多阴少
- 必须借助大盘的上攻走势
- 通常出现在牛市的大高点上
- 判断要点：
  * 高位 & 大涨（近60日涨幅>40%或近120日涨幅>80%）
  * 回撤不深（近60日最大回撤>-20%）
  * 距离高点不远（距离高点<=30天，当前价相对高点<25%）
  * 形态特征：上影线多、象征性洗盘、高位大阳放量、阳线多于阴线

四阶段（猛烈下跌阶段）：
- 特征：猛烈下跌，下跌速度快且幅度大，但是却夹杂着小幅反弹，下引线，反弹后继续下跌，阳线和阴线交叉，阴线多于阳线。
- 散户账面浮亏最多的阶段，高位入场散户，会被反弹，下影线误导，以为还有反弹上涨希望，舍不得给肉。
- 可能先缓慢下跌，然后猛烈下跌，

五阶段（长期阴跌阶段）：
- 特征：漫长的阴跌，消磨投资者意志
- 极少出现大幅升跌后立即反转的形态
- 使散户群体一致看跌，不敢轻易入场做反弹
- 判断五阶段结束方式：
  * 距离上一个出货区域足够远
  * 小规模出货：至少3个月
  * 中等规模出货：至少6个月
  * 大规模出货：至少1年以上
  * 规模越大，距离上一个出货区域越远，五阶段结束的可能性越大
  * 结合技术指标：长期整体下行（近120/180日涨跌幅<0），波动率低（vol60<5%），距离高点很远

【当前股票的结构化信息】

{indicators_text}

{distribution_info_text}

{candidates_text}

{recent_bars_text}

【分析要点】

1. 优先使用技术指标辅助判断：
   - 涨跌幅：判断是否处于上涨/下跌阶段
   - 最大回撤：判断回撤深度（三阶段回撤不深，四阶段回撤大）
   - 距离高点：判断是否在高位（三阶段靠近高点，五阶段远离高点）
   - 波动率：判断波动特征（五阶段波动率低，四阶段波动率大）
   - 洗盘特征：判断是否有洗盘（二阶段有持续洗盘，三阶段象征性洗盘）

2. 结合阶段候选区间：
   - 如果有恐慌低点，可能是4/5阶段末尾或一阶段起点
   - 如果有底部，可能是一阶段
   - 如果有突破点，可能是一阶段到二阶段的转折
   - 如果有箱体，可能是二阶段高位运行

3. 观察K线形态：
   - 三阶段：阳多阴少，上影线多，象征性洗盘
   - 四阶段：阴多阳少，有反弹和下影线，但继续下跌
   - 五阶段：长期阴跌，波动小

4. 判断五阶段是否结束：
   - 需要结合出货规模信息（如果有）
   - 小规模出货后至少3个月，中等规模至少6个月，大规模至少1年
   - 距离上一个出货区域越远，五阶段结束可能性越大

【请输出JSON格式的分析结果】

请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
    "stage": 1-5的整数（0表示未知）,
    "stage_name": "一阶段/二阶段/三阶段/四阶段/五阶段/未知",
    "o_point": {{
        "has_o_point": true/false,
        "date": "日期字符串（如果有）",
        "price": 价格（如果有）,
        "description": "O点描述"
    }},
    "washout_structure": {{
        "has_washout": true/false,
        "washout_type": "洗盘类型（如果有）",
        "description": "洗盘结构描述"
    }},
    "stage_five_ending_analysis": {{
        "is_ending": true/false,
        "days_from_last_distribution": "距离上一个出货区域的天数（如果有）",
        "reasoning": "五阶段是否结束的判断理由"
    }},
    "confidence": 0.0-1.0的浮点数,
    "reasoning": "你的分析理由（详细说明为什么判断是这个阶段，结合技术指标、K线形态、阶段候选区间等信息）"
}}
"""
    return prompt


def llm_stage_analysis_node(state: AnalysisState) -> AnalysisState:
    """LLM阶段分析节点"""
    structured_data = state.get('structured_data')
    if not structured_data:
        state['llm_stage_result'] = {
            'error': '缺少结构化数据，请先运行structured_data_node'
        }
        return state
    
    # 从出货分析结果中读取规模和时间节点信息
    llm_distribution_result = state.get('llm_distribution_result', {})
    
    # 构建提示词（传入出货分析结果）
    user_prompt = build_stage_analysis_prompt(structured_data, llm_distribution_result)
    system_prompt = "你是一名擅长博弈交易法分析的资深交易员，严格按照用户给出的阶段定义进行判断，并以JSON格式输出结果。"
    
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
        if 'stage' not in result:
            result['stage'] = 0
        if 'stage_name' not in result:
            stage_names = ['未知', '一阶段', '二阶段', '三阶段', '四阶段', '五阶段']
            result['stage_name'] = stage_names[result.get('stage', 0)] if 0 <= result.get('stage', 0) <= 5 else '未知'
        
        state['llm_stage_result'] = result
    except Exception as e:
        print(f"[LLM阶段分析] JSON解析失败: {e}")
        print(f"LLM原始返回: {llm_response}")
        state['llm_stage_result'] = {
            'stage': 0,
            'stage_name': '未知',
            'error': f'LLM返回解析失败: {str(e)}',
            'raw_response': llm_response
        }
    
    return state

