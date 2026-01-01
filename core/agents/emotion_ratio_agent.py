"""
情绪比例关系Agent
分析情绪比例关系，判断后市方向
"""
from core.models.state import AnalysisState
from core.tools.calculator import calculate_emotion_ratio
import pandas as pd


def emotion_ratio_node(state: AnalysisState) -> AnalysisState:
    """情绪比例关系分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    required_cols = ['收盘', '开盘', '涨跌幅']
    for col in required_cols:
        if col not in stock_data.columns:
            state['emotion_ratio_result'] = {'direction': 'neutral', 'confidence': 0, 'error': f'缺少必要列: {col}'}
            return state

    df = stock_data.copy()
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['收盘', '开盘'])
    if df.empty or len(df) < 10:
        state['emotion_ratio_result'] = {'direction': 'neutral', 'confidence': 0, 'error': '数据不足'}
        return state

    # 计算情绪比例关系
    emotion_result = calculate_emotion_ratio(df, lookback=60)

    # 添加详细说明
    direction = emotion_result.get('direction', 'neutral')
    confidence = emotion_result.get('confidence', 0)
    distribution_beauty = emotion_result.get('distribution_beauty', 0)
    washout_ugliness = emotion_result.get('washout_ugliness', 0)
    
    if direction == 'bullish':
        explanation = f"较为好看的出货（{distribution_beauty:.2f}）+ 非常难看的洗盘（{washout_ugliness:.2f}），后市看涨"
    elif direction == 'bearish':
        explanation = f"较为难看的洗盘（{washout_ugliness:.2f}）+ 非常好看的出货（{distribution_beauty:.2f}），后市看跌"
    else:
        explanation = "情绪比例关系不明确，需要继续观察"
    
    emotion_result['explanation'] = explanation
    emotion_result['future_direction'] = '看涨' if direction == 'bullish' else ('看跌' if direction == 'bearish' else '中性')
    
    # 更新状态
    state['emotion_ratio_result'] = emotion_result
    
    return state


