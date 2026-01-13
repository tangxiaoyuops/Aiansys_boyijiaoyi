"""
LLM 买卖点分析 Agent
使用大模型识别买入信号（恐慌点）和卖出信号（分水岭）
"""
from core.models.state import AnalysisState
from core.tools.llm_client import call_llm
from core.tools.technical_analyzer import (
    detect_panic_points,
    detect_sell_signals,
    detect_bullish_anchor_pattern
)
from typing import Dict, Any, List
import json
import pandas as pd


def build_trading_points_prompt(
    structured_data: Dict[str, Any],
    stage_result: Dict[str, Any],
    distribution_result: Dict[str, Any],
    panic_points: List[Dict[str, Any]],
    sell_signals: List[Dict[str, Any]] = None,
    bullish_anchor_signals: List[Dict[str, Any]] = None
) -> str:
    """
    构建买卖点分析的提示词
    
    注意：必须严格遵守远离出货位的时间要求和首次建仓的恐慌点数量要求
    """
    if sell_signals is None:
        sell_signals = []
    if bullish_anchor_signals is None:
        bullish_anchor_signals = []
    stock_code = structured_data.get('stock_code', '')
    stock_name = structured_data.get('stock_name', '')
    recent_bars = structured_data.get('recent_bars', [])
    
    # 获取阶段信息
    stage = stage_result.get('stage', 0)
    stage_name = stage_result.get('stage_name', '未知')
    
    # 获取出货信息
    overall_scale = distribution_result.get('overall_scale', 'none')
    latest_cycle_analysis = distribution_result.get('latest_cycle_analysis', {})
    latest_cycle_end_date = latest_cycle_analysis.get('end_date', '')
    
    # 构建恐慌点信息
    panic_points_text = "【检测到的恐慌点（买入信号候选）】\n"
    panic_points_text += "⚠️ 重要提示：如果某个恐慌点出现在涨停后的1-3天内，且跌幅<5%，这通常是正常的技术性调整，不应该被视为真正的恐慌点！\n\n"
    if panic_points:
        for i, point in enumerate(panic_points, 1):
            # 检查前一天是否是涨停（需要从recent_bars中查找）
            prev_day_info = ""
            point_date = point.get('date')
            if point_date and recent_bars:
                # 找到这个恐慌点对应的K线索引
                for j, bar in enumerate(recent_bars[-60:]):
                    if str(bar.get('date')) == str(point_date) and j > 0:
                        # 检查前一天
                        prev_bar = recent_bars[-60:][j-1]
                        prev_open = prev_bar.get('open', 0)
                        prev_close = prev_bar.get('close', 0)
                        if prev_open > 0:
                            prev_body_pct = (prev_close - prev_open) / prev_open
                            if prev_body_pct > 0.095:
                                prev_day_info = f" ⚠️ 前一天是涨停（涨幅{prev_body_pct*100:.2f}%），如果当天跌幅<5%，这是正常调整，不算恐慌点！"
                        break
            
            panic_points_text += (
                f"{i}. {point.get('date', '未知日期')}："
                f"价格 {point.get('price', 0):.2f}，"
                f"类型：{point.get('type', 'unknown')}，"
                f"跌幅 {point.get('drop_pct', 0):.2f}%，"
                f"放量 {point.get('vol_ratio', 0):.2f}倍{prev_day_info}\n"
                f"   描述：{point.get('description', '')}\n"
            )
    else:
        panic_points_text += "未检测到明显的恐慌点\n"
    
    # 构建卖点信号信息
    sell_signals_text = "【检测到的卖点信号（适用于一二阶段，手里有底仓）】\n"
    sell_signals_text += "重要：卖点信号都是指大阳线（收盘价>开盘价，上涨）的情况，不是阴线（下跌）！\n"
    if sell_signals:
        for i, signal in enumerate(sell_signals, 1):
            gain_pct = signal.get('gain_pct', 0)
            body_pct = signal.get('body_pct', 0)  # 当日涨跌幅
            open_price = signal.get('open', 0)
            close_price = signal.get('close', 0)
            gain_label = f"+{gain_pct:.2f}" if gain_pct >= 0 else f"{gain_pct:.2f}"
            body_label = f"+{body_pct:.2f}" if body_pct >= 0 else f"{body_pct:.2f}"
            # 验证：确保是阳线
            kline_type = "阳线" if close_price > open_price else "阴线"
            sell_signals_text += (
                f"{i}. {signal.get('date', '未知日期')}："
                f"价格 {signal.get('price', 0):.2f}，"
                f"类型：{signal.get('type', 'unknown')}，"
                f"K线：{kline_type}（开盘{open_price:.2f}，收盘{close_price:.2f}），"
                f"当日涨跌幅：{body_label}%，"
                f"相对前日涨幅：{gain_label}%，"
                f"放量 {signal.get('vol_ratio', 0):.2f}倍\n"
                f"   描述：{signal.get('description', '')}\n"
            )
    else:
        sell_signals_text += "未检测到明显的卖点信号\n"
    
    # 构建多方锚定信号信息
    anchor_signals_text = "【检测到的多方锚定信号】\n"
    if bullish_anchor_signals:
        for i, signal in enumerate(bullish_anchor_signals, 1):
            anchor_signals_text += (
                f"{i}. {signal.get('date', '未知日期')}："
                f"价格 {signal.get('price', 0):.2f}，"
                f"涨幅 {signal.get('gain_pct', 0):.2f}%，"
                f"放量 {signal.get('vol_ratio', 0):.2f}倍\n"
                f"   描述：{signal.get('description', '')}\n"
            )
    else:
        anchor_signals_text += "未检测到明显的多方锚定信号\n"
    
    # 构建最近K线数据（用于判断）
    recent_bars_text = "【最近K线数据（时间顺序，越往下越新）】\n"
    recent_bars_text += "格式：日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅(%) | 成交量(万手) | K线类型 | 特殊标记\n"
    recent_bars_text += "重要说明：涨跌幅中，正数表示上涨，负数表示下跌。例如：+5.00表示涨5%，-3.50表示跌3.5%\n"
    recent_bars_text += "K线类型：收盘价>开盘价为阳线（上涨），收盘价<开盘价为阴线（下跌）\n"
    recent_bars_text += "特殊标记：涨停（涨幅>9.5%）、跌停（跌幅<-9.5%）、大阳（涨幅>5%）、大阴（跌幅<-5%）\n\n"
    for idx, bar in enumerate(recent_bars[-60:]):  # 只取最近60天用于买卖点判断
        change_pct = bar['change_pct']
        # 明确标注涨跌
        change_label = f"+{change_pct:.2f}" if change_pct >= 0 else f"{change_pct:.2f}"
        # 判断K线类型
        is_yang = bar['close'] > bar['open']
        kline_type = "阳线" if is_yang else "阴线"
        # 数据验证：确保最高>=最低，收盘在最高和最低之间
        open_price = bar['open']
        high_price = bar['high']
        low_price = bar['low']
        close_price = bar['close']
        
        # 计算实体涨幅（用于判断涨停）
        body_pct = (close_price - open_price) / open_price if open_price > 0 else 0
        special_mark = ""
        if body_pct > 0.095:
            special_mark = " [涨停]"
        elif body_pct < -0.095:
            special_mark = " [跌停]"
        elif body_pct > 0.05 and is_yang:
            special_mark = " [大阳]"
        elif body_pct < -0.05 and not is_yang:
            special_mark = " [大阴]"
        
        # 如果数据异常，添加警告标记
        data_warning = ""
        if high_price < low_price:
            data_warning = " [数据异常：最高<最低]"
        if close_price > high_price or close_price < low_price:
            data_warning = " [数据异常：收盘价超出最高/最低范围]"
        recent_bars_text += (
            f"{bar['date']} | {open_price:.2f} | {high_price:.2f} | "
            f"{low_price:.2f} | {close_price:.2f} | {change_label}% | "
            f"{bar['volume']:.2f} | {kline_type}{special_mark}{data_warning}\n"
        )
    
    scale_map = {'small': '小规模', 'medium': '中等规模', 'large': '大规模', 'none': '无明显出货'}
    scale_text = scale_map.get(overall_scale, overall_scale)
    
    prompt = f"""你是一名擅长博弈交易法买卖点识别的资深交易员。现在请你分析股票 {stock_code}（{stock_name}）的买卖点。

【当前股票状态】
- 当前阶段：{stage_name}（{stage}阶段）
- 最近一轮出货规模：{scale_text}
- 最近一轮出货结束日期：{latest_cycle_end_date if latest_cycle_end_date else '未知'}

【买入信号（恐慌点）定义】

1. 5阶段长期阴跌后的恐慌点：
   - 特征：长期阴跌后，由于大盘或行情震荡导致突然急剧下跌且放量
   - 识别要点：前面长期下跌（近20日累计跌幅>10%），突然出现跌幅>3%且放量>1.5倍的阴线

2. 一阶段O点之前的恐慌点：
   - 特征：O点之前的急剧下跌，反弹一小段后又往下跌，出现小短期放量
   - 识别要点：前面有反弹（涨幅>5%），然后出现跌幅>3%且放量的下跌
   - ⚠️ 重要排除条件：如果前一天是涨停，且当天跌幅<5%，这是正常的技术性调整，不应该被视为恐慌点！

3. 1/2阶段洗盘横盘后的恐慌点：
   - 特征：判定为1/2阶段，具有上涨趋势，前面有明显洗盘、长时间横盘，突然出现1-2根大大的放巨量的阴线
   - 识别要点：前面有上涨趋势（近30日涨幅>5%）且横盘（波动率<3%），突然出现放量>2倍的大阴线

4. 小碎步上涨过程中的恐慌点：
   - 特征：小碎步上涨过程中突然的大跌放量阴线
   - 识别要点：前面小碎步上涨（近10日累计涨幅>3%但单日涨幅<3%），突然出现跌幅>3%且放量的阴线
   - ⚠️ 重要排除条件：如果前一天是涨停，且当天跌幅<5%，这是正常的技术性调整，不应该被视为恐慌点！只有跌幅>=5%的才可能是真正的恐慌点
5.空方锚定形态 + 放量大跌恐慌盘：
   - 特征：形态上和前面近期几个月（3-6个月）内的形态很相似，有重复再次下跌的感觉
   - 这是主力操控形态，形成空方锚定
   - 当识别到这种形态，且出现放量的大跌时（涨幅>4%，放量>1.5倍）
   - 操作建议：考虑建仓或者适当加仓
6. **连续下跌，跟随的大阴线跌破前低点、重要均线，导致恐慌盘放量，散户被洗出去（最重要的恐慌点类型）**：
   - **核心原则**：持仓的跌了怕继续跌，外面的不敢进
   - 特征：前面有连续下跌（至少3-5天），跟随的大阴线（跌幅>=4%）跌破前低点或重要均线（20日、30日、60日均线），导致恐慌盘放量（放量>1.5倍）
   - **关键识别要点**：
     * 前面连续下跌至少3天
     * 大阴线跌幅>=4%，且是阴线（收盘<开盘）
     * 收盘价跌破前低点（最近60天内的最低点）或重要均线
     * 放量明显（>1.5倍均量）
     * **后续3-5天继续下跌或横盘**（让外面的人不敢进，这是关键！）
   - **排除条件**：涨停后的调整不算恐慌点（即使跌幅>=5%）
   - 操作建议：考虑建仓或者适当加仓
【买入规则（必须严格遵守）】

⚠️ 重要排除规则：涨停后的调整不是恐慌点！
- 如果某个恐慌点出现在涨停后的1-3天内，且跌幅<5%，这是正常的技术性调整，不应该被视为真正的恐慌点
- 涨停后的正常调整特征：前一天涨停（涨幅>9.5%），第二天或第三天出现小幅下跌（跌幅<5%），即使放量也不算恐慌点
- 只有跌幅>=5%的才可能是真正的恐慌点，需要结合其他条件综合判断

1. 远离出货位的时间要求：
   - 小规模出货：至少3个月（约90个交易日）
   - 中等规模出货：至少6个月（约180个交易日）
   - 大规模出货：至少1年（约250个交易日）
   - 超大规模跌下来的，时间间隔要更长（至少1.5年，约375个交易日）

2. 首次建仓的恐慌点数量要求（必须严格遵守，不能降低标准）：
   - 小规模出货：至少需要1个恐慌点
   - 中等规模出货：至少需要2个恐慌点
   - 大规模出货：至少需要3个恐慌点
   - ⚠️ 重要：如果恐慌点数量不足，绝对不能买入！例如大规模出货只有2个恐慌点，必须设置 can_buy=false，suggested_position="0%"
   - ⚠️ 重要：不能因为"恐慌点质量高"或"时间要求满足"就降低恐慌点数量要求！

3. 仓位计算规则（必须严格遵守）：
   - 如果恐慌点数量不足，can_buy必须为false，suggested_position必须为"0%"
   - 如果恐慌点数量满足要求：
     * 小规模出货：1个恐慌点 → 建议仓位10-20%
     * 中等规模出货：2个恐慌点 → 建议仓位15-25%
     * 大规模出货：3个恐慌点 → 建议仓位20-30%
   - 如果恐慌点数量超过要求，可以适当增加仓位，但不超过30%

4. 加仓规则：
   - 如果恐慌点信号连续出现，可以根据仓位控制加仓
   - 但必须确保满足远离出货位的时间要求

【卖出信号】

1. 大阳线放量，形态特别好看（短线卖点）：
   - 特征：大阳线（涨幅>5%），放量（>1.5倍），上影线短（<2%），下影线短（<1%），形态特别好看
   - 操作建议：根据仓位适当减仓，减仓后等下一个洗盘恐慌点再加回去
   - 注意：一二阶段有上涨趋势的票，要注意保留中长线的底仓

2. 放量突破前高，形态特别好看：
   - 特征：放量突破前高（收盘价>前高*1.01），大阳线，放量（>1.5倍），形态特别好看
   - 操作建议：这是一个卖点，考虑减仓

3. 涨停第二天还是大阳线：
   - 特征：前一天涨停，第二天还是大阳线（涨幅>5%）
   - 逻辑：涨停是为了打广告，散户看到涨停会买进。如果主力想出货，会在第二天给大量筹码。
   - 如果主力想继续拉升，第二天一般会打压（盘中和收盘形态难看）
   - 涨停后第二天如果是涨停（散户买不到）或大阴线（散户不敢买），其余情况都可以看作主力在出货
   - 操作建议：考虑减仓卖出

4. 多方锚定形态 + 放量大涨：
   - 特征：形态上和前面近期几个月（3-6个月）的形态很相似，有重复再次上涨的感觉
   - 这是主力操控形态，形成多方锚定
   - 当识别到这种形态，且出现放量的大涨时（涨幅>5%，放量>1.5倍）
   - 操作建议：考虑大幅度减仓或离场

5. 分水岭形态（三阶段）：
   - 当股票经历三阶段急速拉升以后，在高位置横盘，洗盘阴线不明显
   - 后面有两次大阳线，第二次是涨停，第三次是没封板的涨停
   - 这个形态告诉散户第一次尝试突破前高失败，稍微回调下，第二次再继续往上突破前高
   - 形态上给了散户足够的信心，所以这个形态在快要突破高时会有大批量的散户买进，主力从而达到出货的目的

{panic_points_text}

{sell_signals_text}

{anchor_signals_text}

{recent_bars_text}

【请输出JSON格式的分析结果】

请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
    "buy_signals": [
        {{
            "date": "日期字符串",
            "price": 价格,
            "type": "恐慌点类型（stage5_panic/stage1_panic/washout_panic/uptrend_panic/breakdown_panic）",
            "confidence": 0.0-1.0的浮点数,
            "reasoning": "为什么判断这是买入信号",
            "meets_time_requirement": true/false（是否满足远离出货位的时间要求）,
            "meets_panic_count_requirement": true/false（是否满足首次建仓的恐慌点数量要求）
        }}
    ],
    "sell_signals": [
        {{
            "date": "日期字符串",
            "price": 价格,
            "type": "卖出信号类型（beautiful_big_yang/breakthrough_high/limit_up_next_day/bullish_anchor/watershed）",
            "confidence": 0.0-1.0的浮点数,
            "reasoning": "为什么判断这是卖出信号",
            "suggested_action": "建议操作（适当减仓/减仓/大幅度减仓或离场）",
            "keep_base_position": true/false（是否保留中长线底仓，适用于一二阶段）
        }}
    ],
    "position_suggestion": {{
        "can_buy": true/false（是否可以买入）,
        "buy_reason": "买入理由（如果不可以买入，说明原因）",
        "suggested_position": "建议仓位（0%/10%/20%/30%等）",
        "position_reasoning": "仓位建议的理由",
        "stop_loss_price": 止损价格（如果有）,
        "take_profit_price": 止盈价格（如果有）
    }},
    "trading_summary": "买卖点分析的总结（自然语言）"
}}
"""
    return prompt


def llm_trading_points_analysis_node(state: AnalysisState) -> AnalysisState:
    """LLM买卖点分析节点"""
    structured_data = state.get('structured_data')
    llm_stage_result = state.get('llm_stage_result', {})
    llm_distribution_result = state.get('llm_distribution_result', {})
    stock_data = state.get('stock_data')
    # 兼容旧框架
    stage_result = state.get('stage_result', {})
    
    if not structured_data or stock_data is None or stock_data.empty:
        state['llm_trading_points_result'] = {
            'error': '缺少结构化数据或股票数据'
        }
        return state
    
    # 检测恐慌点
    try:
        df = stock_data.copy()
        for col in ['开盘', '收盘', '最高', '最低', '成交量']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['收盘']).reset_index(drop=True)
        
        panic_points = detect_panic_points(df, window=60, vol_ratio=1.5)
    except Exception as e:
        print(f"[买卖点分析] 检测恐慌点失败: {e}")
        panic_points = []
    
    # 检测卖点信号（需要阶段信息）
    sell_signals_detected = []
    bullish_anchor_signals = []
    try:
        # 获取当前阶段（优先LLM结果）
        current_stage = 0
        if llm_stage_result and 'error' not in llm_stage_result:
            current_stage = llm_stage_result.get('stage', 0)
        elif stage_result:
            current_stage = stage_result.get('stage', 0)
        
        # 检测卖点信号（只在一二阶段）
        if current_stage in [1, 2]:
            sell_signals_detected = detect_sell_signals(df, window=60, stage=current_stage)
        
        # 检测多方锚定形态（所有阶段都可能出现）
        bullish_anchor_signals = detect_bullish_anchor_pattern(df, window=120)
    except Exception as e:
        print(f"[买卖点分析] 检测卖点信号失败: {e}")
        sell_signals_detected = []
        bullish_anchor_signals = []
    
    # 构建提示词
    user_prompt = build_trading_points_prompt(
        structured_data,
        llm_stage_result if llm_stage_result else stage_result,
        llm_distribution_result,
        panic_points,
        sell_signals_detected,
        bullish_anchor_signals
    )
    system_prompt = "你是一名擅长博弈交易法买卖点识别的资深交易员，严格按照用户给出的买入规则进行判断，并以JSON格式输出结果。"
    # 调用LLM
    llm_response = call_llm(system_prompt, user_prompt, temperature=0.3)
    
    # 解析LLM返回的JSON
    try:
        import re
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(llm_response)
        
        # 验证必要字段
        if 'buy_signals' not in result:
            result['buy_signals'] = []
        if 'sell_signals' not in result:
            result['sell_signals'] = []
        if 'position_suggestion' not in result:
            result['position_suggestion'] = {
                'can_buy': False,
                'buy_reason': '未分析'
            }
        
        state['llm_trading_points_result'] = result
    except Exception as e:
        print(f"[LLM买卖点分析] JSON解析失败: {e}")
        print(f"LLM原始返回: {llm_response}")
        state['llm_trading_points_result'] = {
            'buy_signals': [],
            'sell_signals': [],
            'position_suggestion': {
                'can_buy': False,
                'buy_reason': f'LLM返回解析失败: {str(e)}'
            },
            'error': f'LLM返回解析失败: {str(e)}',
            'raw_response': llm_response
        }
    
    return state

