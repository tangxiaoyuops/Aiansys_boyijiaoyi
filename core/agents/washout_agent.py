"""
洗盘分析Agent
分析洗盘类型和强度
"""
from core.models.state import AnalysisState
from core.tools.pattern_recognizer import identify_washout_type
from core.tools.calculator import calculate_washout_effect
from core.tools.technical_analyzer import calculate_washout_indicators
import pandas as pd


def washout_analysis_node(state: AnalysisState) -> AnalysisState:
    """洗盘分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    # 确保必需列存在且为数值
    required_cols = ['收盘', '开盘', '最高', '最低', '成交量', '涨跌幅']
    for col in required_cols:
        if col not in stock_data.columns:
            state['washout_result'] = {
                'is_washout': False,
                'washout_type': 'unknown',
                'washout_type_confidence': 0,
                'washout_score': 0,
                'fear_level': 0,
                'anxiety_level': 0,
                'retail_ratio': 1,
                'indicators': {},
                'details': {'error': f'缺少必要列: {col}'}
            }
            return state

    df = stock_data.copy()
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['收盘'])
    if df.empty:
        state['washout_result'] = {
            'is_washout': False,
            'washout_type': 'unknown',
            'washout_type_confidence': 0,
            'washout_score': 0,
            'fear_level': 0,
            'anxiety_level': 0,
            'retail_ratio': 1,
            'indicators': {},
            'details': {'error': '数据无有效收盘价'}
        }
        return state

    # 识别洗盘类型
    washout_type_result = identify_washout_type(df)

    # 计算洗盘效果
    washout_effect = calculate_washout_effect(df, washout_period=30)

    # 获取洗盘指标
    washout_indicators = calculate_washout_indicators(df, lookback_days=30)

    # 综合判断是否处于洗盘状态
    is_washout = (
        washout_type_result.get('type') != 'unknown' or
        washout_effect.get('washout_score', 0) > 0.3
    )
    
    washout_result = {
        'is_washout': is_washout,
        'washout_type': washout_type_result.get('type', 'unknown'),
        'washout_type_confidence': washout_type_result.get('confidence', 0),
        'washout_score': washout_effect.get('washout_score', 0),
        'fear_level': washout_effect.get('fear_level', 0),
        'anxiety_level': washout_effect.get('anxiety_level', 0),
        'retail_ratio': washout_effect.get('retail_ratio', 1),
        'indicators': washout_indicators,
        'details': {
            **washout_type_result,
            **washout_effect
        }
    }
    
    # 更新状态
    state['washout_result'] = washout_result
    
    return state


