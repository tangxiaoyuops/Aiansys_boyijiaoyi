"""
O点识别Agent
识别原始低点（O点）
"""
from core.models.state import AnalysisState
from core.tools.technical_analyzer import find_o_point
import pandas as pd


def o_point_analysis_node(state: AnalysisState) -> AnalysisState:
    """O点分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    # 确保关键列存在且为数值
    required_cols = ['收盘', '最低']
    for col in required_cols:
        if col not in stock_data.columns:
            state['o_point_result'] = {
                'o_point_price': None,
                'o_point_date': None,
                'current_price': None,
                'relative_gain': 0,
                'days_from_o': 0,
                'error': f'缺少必要列: {col}'
            }
            return state

    df = stock_data.copy()
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['收盘', '最低'])
    if df.empty:
        state['o_point_result'] = {
            'o_point_price': None,
            'o_point_date': None,
            'current_price': None,
            'relative_gain': 0,
            'days_from_o': 0,
            'error': '数据无有效收盘/最低价'
        }
        return state

    # 识别O点
    o_point_result = find_o_point(df, lookback_days=250)

    if o_point_result is None:
        o_point_result = {
            'o_point_price': None,
            'o_point_date': None,
            'current_price': df.iloc[-1]['收盘'],
            'relative_gain': 0,
            'days_from_o': 0,
            'error': '无法识别O点，数据不足'
        }
    
    # 更新状态
    state['o_point_result'] = o_point_result
    
    return state


