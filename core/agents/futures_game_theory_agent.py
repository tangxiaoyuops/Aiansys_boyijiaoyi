"""
期货博弈分析Agent
基于股票博弈分析逻辑，适配期货特性
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.futures_analyzer import (
    compute_futures_technical_indicators,
    detect_futures_stage_candidates,
    analyze_open_interest_trend
)
from core.tools.llm_client import call_llm
from typing import Dict, Any
import json


def build_futures_stage_analysis_prompt(
    structured_data: Dict[str, Any],
    futures_data: Any
) -> str:
    """构建期货阶段分析的提示词"""
    futures_code = structured_data.get('futures_code', '')
    futures_name = structured_data.get('futures_name', '')
    technical_indicators = structured_data.get('technical_indicators', {})
    open_interest_trend = structured_data.get('open_interest_trend', {})
    
    # 构建技术指标文本
    indicators_text = "【技术指标】\n"
    if technical_indicators:
        indicators_text += f"当前价格：{technical_indicators.get('current_price', 0):.2f}\n"
        
        # 均线
        ma_info = []
        for ma in ['ma5', 'ma20', 'ma60']:
            if ma in technical_indicators and technical_indicators[ma] is not None:
                ma_info.append(f"{ma.upper()}：{technical_indicators[ma]:.2f}")
        if ma_info:
            indicators_text += "均线：" + "，".join(ma_info) + "\n"
        
        # RSI
        if 'rsi' in technical_indicators and technical_indicators['rsi'] is not None:
            indicators_text += f"RSI：{technical_indicators['rsi']:.2f}\n"
        
        # MACD
        if 'macd' in technical_indicators and technical_indicators['macd'] is not None:
            indicators_text += f"MACD：{technical_indicators['macd']:.4f}\n"
        
        # 涨跌幅
        gains_info = []
        for period in [20, 60, 120]:
            gain_key = f'gain{period}'
            if gain_key in technical_indicators and technical_indicators[gain_key] is not None:
                gains_info.append(f"近{period}日涨跌幅：{technical_indicators[gain_key]:.2f}%")
        if gains_info:
            indicators_text += "涨跌幅：\n  " + "\n  ".join(gains_info) + "\n"
        
        # 波动率
        if 'volatility_20' in technical_indicators and technical_indicators['volatility_20'] is not None:
            indicators_text += f"波动率：近20日 {technical_indicators['volatility_20']:.2f}%\n"
    
    # 持仓量趋势
    oi_text = "【持仓量分析】\n"
    if open_interest_trend:
        trend_map = {
            'increasing': '上升',
            'decreasing': '下降',
            'stable': '稳定',
            'unknown': '未知'
        }
        trend = trend_map.get(open_interest_trend.get('trend', 'unknown'), '未知')
        change_pct = open_interest_trend.get('change_pct', 0)
        oi_text += f"持仓量趋势：{trend}，变化：{change_pct:.2f}%\n"
        oi_text += f"平均持仓量：{open_interest_trend.get('avg_oi', 0):.0f}\n"
    else:
        oi_text += "持仓量数据不足\n"
    
    prompt = f"""你是一名擅长期货博弈交易法分析的资深交易员。现在请你分析期货合约 {futures_code}（{futures_name}）的当前阶段。

【期货特性说明】
- 期货具有杠杆效应，风险放大
- 持仓量变化反映市场情绪和资金流向
- 需要考虑合约到期的影响
- 保证金交易，需要严格控制仓位

【阶段定义（博弈交易法，适配期货）】

一阶段（趋势形成初期）：
- 特征：缓慢且隐蔽的上涨，承接上一轮五阶段下跌后的底部
- 持仓量可能逐步增加，但幅度不大
- 可以偶有大阳线，但出现后必须立刻掉头猛跌
- 作用：消磨散户持仓意志，产生极度悲观情绪

二阶段（快速上涨阶段）：
- 特征：快速上涨并在高位长期维持，期间伴随持续洗盘
- 持仓量显著增加，反映资金流入
- 上涨幅度最大的阶段
- 高位运行，趋势结束前不会再现低位价格

三阶段（疯狂上涨阶段）：
- 特征：利用散户贪婪情绪，使其在高位追高被套
- 持仓量可能达到峰值后开始下降（获利了结）
- 持续时间短，通常不超过3个月
- 象征性洗盘，阳多阴少

四阶段（猛烈下跌阶段）：
- 特征：猛烈下跌，下跌速度快且幅度大
- 持仓量快速下降（止损离场）
- 散户账面浮亏最多的阶段
- 阴线多于阳线

五阶段（长期阴跌阶段）：
- 特征：漫长的阴跌，消磨投资者意志
- 持仓量处于低位
- 使散户群体一致看跌，不敢轻易入场

【当前期货的结构化信息】

{indicators_text}

{oi_text}

【分析要点】

1. 结合持仓量变化：
   - 持仓量增加 + 价格上涨 = 资金流入，可能是一/二阶段
   - 持仓量减少 + 价格上涨 = 获利了结，可能是三阶段
   - 持仓量减少 + 价格下跌 = 止损离场，可能是四阶段
   - 持仓量低位 + 价格阴跌 = 五阶段

2. 考虑杠杆风险：
   - 期货杠杆放大风险，阶段判断需要更谨慎
   - 三阶段追高风险极大，需要严格控制仓位

3. 技术指标辅助：
   - 涨跌幅：判断是否处于上涨/下跌阶段
   - 波动率：判断波动特征
   - RSI、MACD：判断超买超卖

【请输出JSON格式的分析结果】

请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
    "stage": 1-5的整数（0表示未知）,
    "stage_name": "一阶段/二阶段/三阶段/四阶段/五阶段/未知",
    "confidence": 0.0-1.0的浮点数,
    "open_interest_analysis": {{
        "trend": "持仓量趋势描述",
        "impact": "持仓量变化对阶段判断的影响"
    }},
    "leverage_risk": {{
        "risk_level": "风险等级（low/medium/high）",
        "warning": "杠杆风险提示"
    }},
    "reasoning": "你的分析理由（详细说明为什么判断是这个阶段，结合技术指标、持仓量变化等信息）"
}}
"""
    return prompt


def futures_game_theory_analysis_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货博弈分析节点"""
    futures_code = state.get('futures_code', '')
    futures_data = state.get('futures_data')
    
    print(f"[期货博弈分析] 开始分析: {futures_code}")
    
    if futures_data is None or futures_data.empty:
        print(f"[期货博弈分析] 错误: 缺少期货数据")
        state['game_theory_result'] = {
            'error': '缺少期货数据，请先运行futures_data_fetch_node'
        }
        return state
    
    try:
        # 计算技术指标
        print(f"[期货博弈分析] 正在计算技术指标...")
        technical_indicators = compute_futures_technical_indicators(futures_data)
        print(f"[期货博弈分析] 技术指标计算完成")
        if technical_indicators.get('current_price'):
            print(f"[期货博弈分析] 当前价格: {technical_indicators.get('current_price'):.2f}")
        if technical_indicators.get('rsi'):
            print(f"[期货博弈分析] RSI: {technical_indicators.get('rsi'):.2f}")
        
        # 分析持仓量趋势
        open_interest_trend = {}
        if '持仓量' in futures_data.columns:
            print(f"[期货博弈分析] 正在分析持仓量趋势...")
            from core.tools.futures_analyzer import analyze_open_interest_trend
            open_interest_trend = analyze_open_interest_trend(futures_data)
            print(f"[期货博弈分析] 持仓量趋势: {open_interest_trend.get('trend', 'unknown')}, 变化: {open_interest_trend.get('change_pct', 0):.2f}%")
        
        # 识别阶段候选
        print(f"[期货博弈分析] 正在识别阶段候选区间...")
        stage_candidates = detect_futures_stage_candidates(futures_data)
        print(f"[期货博弈分析] 识别到 {len(stage_candidates)} 个阶段候选区间")
        
        # 构建结构化数据
        structured_data = {
            'futures_code': state.get('futures_code', ''),
            'futures_name': state.get('futures_name', ''),
            'technical_indicators': technical_indicators,
            'open_interest_trend': open_interest_trend,
            'stage_candidates': stage_candidates
        }
        
        state['structured_data'] = structured_data
        print(f"[期货博弈分析] 结构化数据构建完成，正在调用LLM分析...")
        
        # 构建提示词
        user_prompt = build_futures_stage_analysis_prompt(structured_data, futures_data)
        system_prompt = "你是一名擅长期货博弈交易法分析的资深交易员，严格按照用户给出的阶段定义进行判断，并以JSON格式输出结果。"
        
        # 调用LLM
        print(f"[期货博弈分析] 正在调用LLM进行阶段分析...")
        llm_response = call_llm(system_prompt, user_prompt, temperature=0.3)
        print(f"[期货博弈分析] LLM响应接收完成，长度: {len(llm_response)} 字符")
        
        # 解析LLM返回的JSON
        try:
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
            
            print(f"[期货博弈分析] 分析结果: {result.get('stage_name', '未知')}, 置信度: {result.get('confidence', 0):.2%}")
            state['game_theory_result'] = result
            print(f"[期货博弈分析] 博弈分析节点完成")
        except Exception as e:
            print(f"[期货博弈分析] JSON解析失败: {e}")
            print(f"[期货博弈分析] LLM原始返回: {llm_response[:500]}...")  # 只打印前500字符
            state['game_theory_result'] = {
                'stage': 0,
                'stage_name': '未知',
                'error': f'LLM返回解析失败: {str(e)}',
                'raw_response': llm_response
            }
        
    except Exception as e:
        print(f"[期货博弈分析] 分析失败: {e}")
        import traceback
        print(f"[期货博弈分析] 错误堆栈: {traceback.format_exc()}")
        state['game_theory_result'] = {
            'error': f'分析失败: {str(e)}'
        }
    
    return state

