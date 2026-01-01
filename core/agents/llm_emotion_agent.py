"""
LLM 情绪分析 Agent
使用大模型分析情绪比例关系和锚定
"""
from core.models.state import AnalysisState
from core.tools.llm_client import call_llm
from typing import Dict, Any
import json


def build_emotion_analysis_prompt(structured_data: Dict[str, Any]) -> str:
    """构建情绪分析的提示词"""
    stock_code = structured_data.get('stock_code', '')
    stock_name = structured_data.get('stock_name', '')
    recent_bars = structured_data.get('recent_bars', [])
    
    # 构建最近K线数据文本（重点关注洗盘和出货的形态）
    recent_bars_text = "【最近K线数据（时间顺序，越往下越新）】\n"
    recent_bars_text += "格式：日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅(%) | 成交量(万手)\n"
    for bar in recent_bars[-120:]:  # 取最近120天
        recent_bars_text += (
            f"{bar['date']} | {bar['open']:.2f} | {bar['high']:.2f} | "
            f"{bar['low']:.2f} | {bar['close']:.2f} | {bar['change_pct']:.2f} | "
            f"{bar['volume']:.2f}\n"
        )
    
    prompt = f"""你是一名擅长博弈交易法分析的资深交易员。现在请你分析股票 {stock_code}（{stock_name}）的情绪比例关系和锚定。

【情绪比例关系定义】

情绪比例关系 = 较为好看的出货 + 非常难看的洗盘

- 较为好看的出货：主力在高位出货时，K线形态相对好看（如大阳线、涨停），让散户觉得还会继续涨，从而在高位接盘
- 非常难看的洗盘：主力在低位洗盘时，K线形态非常难看（如长阴线、连续下跌），让散户感到恐慌，从而在低位割肉

当情绪比例关系成立时，后市看涨（因为散户在低位割肉，在高位接盘，主力完成筹码交换）

【锚定分析定义】

- 多方锚定：散户在上涨行情中保持多头思维，认为还会继续涨，容易在高位追涨
- 空方锚定：散户在下跌行情中保持空头思维，认为还会继续跌，容易在低位割肉
- 中性：没有明显的锚定倾向

【当前股票的K线数据】

{recent_bars_text}

【请输出JSON格式的分析结果】

请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
    "emotion_ratio": {{
        "direction": "bullish/bearish/neutral",
        "distribution_beauty": 0.0-1.0的浮点数（出货形态的好看程度）,
        "washout_ugliness": 0.0-1.0的浮点数（洗盘形态的难看程度）,
        "explanation": "情绪比例关系的详细解释"
    }},
    "anchor": {{
        "type": "bullish/bearish/neutral",
        "description": "锚定类型的描述"
    }},
    "confidence": 0.0-1.0的浮点数,
    "reasoning": "你的分析理由"
}}
"""
    return prompt


def llm_emotion_analysis_node(state: AnalysisState) -> AnalysisState:
    """LLM情绪分析节点"""
    structured_data = state.get('structured_data')
    if not structured_data:
        state['llm_emotion_result'] = {
            'error': '缺少结构化数据，请先运行structured_data_node'
        }
        return state
    
    # 构建提示词
    user_prompt = build_emotion_analysis_prompt(structured_data)
    system_prompt = "你是一名擅长博弈交易法分析的资深交易员，严格按照用户给出的情绪比例关系和锚定定义进行判断，并以JSON格式输出结果。"
    
    # 调用LLM
    llm_response = call_llm(system_prompt, user_prompt, temperature=0.3)
    
    # 解析LLM返回的JSON
    try:
        # 尝试提取JSON（可能LLM返回了其他文字或多余的括号）
        import re
        # 先尝试找到第一个完整的JSON对象
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # 尝试解析，如果失败则尝试清理多余的括号
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                # 如果解析失败，尝试找到最外层的大括号对
                brace_count = 0
                start_idx = -1
                for i, char in enumerate(json_str):
                    if char == '{':
                        if start_idx == -1:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            json_str = json_str[start_idx:i+1]
                            break
                result = json.loads(json_str)
        else:
            result = json.loads(llm_response)
        
        # 验证必要字段
        if 'emotion_ratio' not in result:
            result['emotion_ratio'] = {'direction': 'neutral', 'explanation': '无法判断'}
        if 'anchor' not in result:
            result['anchor'] = {'type': 'neutral', 'description': '无法判断'}
        
        state['llm_emotion_result'] = result
    except Exception as e:
        print(f"[LLM情绪分析] JSON解析失败: {e}")
        print(f"LLM原始返回: {llm_response}")
        # 尝试更宽松的解析方式：找到第一个完整的JSON对象
        try:
            import re
            # 找到第一个 { 到最后一个匹配的 }
            start_idx = llm_response.find('{')
            if start_idx != -1:
                brace_count = 0
                end_idx = -1
                for i in range(start_idx, len(llm_response)):
                    if llm_response[i] == '{':
                        brace_count += 1
                    elif llm_response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i
                            break
                if end_idx != -1:
                    json_str = llm_response[start_idx:end_idx+1]
                    result = json.loads(json_str)
                    if 'emotion_ratio' not in result:
                        result['emotion_ratio'] = {'direction': 'neutral', 'explanation': '无法判断'}
                    if 'anchor' not in result:
                        result['anchor'] = {'type': 'neutral', 'description': '无法判断'}
                    state['llm_emotion_result'] = result
                    return state
        except:
            pass
        state['llm_emotion_result'] = {
            'emotion_ratio': {'direction': 'neutral', 'explanation': f'LLM返回解析失败: {str(e)}'},
            'anchor': {'type': 'neutral', 'description': '无法判断'},
            'error': f'LLM返回解析失败: {str(e)}',
            'raw_response': llm_response
        }
    
    return state
