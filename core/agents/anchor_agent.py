"""
锚定分析Agent
分析多方锚定和空方锚定
"""
from core.models.state import AnalysisState
import pandas as pd
import numpy as np


def analyze_anchor(data: pd.DataFrame) -> dict:
    """
    分析多方锚定和空方锚定
    
    多方锚定：散户一致看多，阳线越来越大
    空方锚定：散户一致看空，下跌初期恐怖性下跌
    """
    if len(data) < 30:
        return {'anchor_type': 'none', 'confidence': 0}
    
    recent = data.tail(30)
    
    # 分析多方锚定
    # 特征：阳线个头越来越大，散户越来越愿意买入
    yang_lines = recent[recent['收盘'] > recent['开盘']]
    if len(yang_lines) >= 5:
        yang_sizes = (yang_lines['收盘'] - yang_lines['开盘']) / yang_lines['开盘']
        # 检查阳线是否越来越大
        if len(yang_sizes) >= 3:
            recent_yang_sizes = yang_sizes.tail(3).values
            if np.all(np.diff(recent_yang_sizes) > 0):
                # 阳线越来越大
                return {
                    'anchor_type': 'long',
                    'confidence': 0.7,
                    'status': 'formed',
                    'signal': '买入信号'
                }
    
    # 分析空方锚定
    # 特征：下跌初期恐怖性下跌，持续补空锚
    yin_lines = recent[recent['收盘'] < recent['开盘']]
    if len(yin_lines) >= 3:
        yin_sizes = (yin_lines['开盘'] - yin_lines['收盘']) / yin_lines['开盘']
        # 检查是否有恐怖性下跌
        if yin_sizes.max() > 0.05:  # 单日跌幅超过5%
            # 检查是否持续下跌
            recent_prices = recent['收盘'].values
            if len(recent_prices) >= 5:
                price_decline = (recent_prices[0] - recent_prices[-1]) / recent_prices[0]
                if price_decline > 0.1:  # 累计跌幅超过10%
                    return {
                        'anchor_type': 'short',
                        'confidence': 0.7,
                        'status': 'formed',
                        'signal': '空方锚定形成，上涨行情中保持空头思维'
                    }
    
    return {
        'anchor_type': 'none',
        'confidence': 0.3,
        'status': 'not_formed',
        'signal': '未形成明显锚定'
    }


def anchor_analysis_node(state: AnalysisState) -> AnalysisState:
    """锚定分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    required_cols = ['收盘', '开盘']
    for col in required_cols:
        if col not in stock_data.columns:
            state['anchor_result'] = {'anchor_type': 'none', 'confidence': 0, 'status': 'not_formed', 'signal': f'缺少必要列: {col}'}
            return state

    df = stock_data.copy()
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['收盘', '开盘'])
    if df.empty:
        state['anchor_result'] = {'anchor_type': 'none', 'confidence': 0, 'status': 'not_formed', 'signal': '数据不足'}
        return state

    # 分析锚定
    anchor_result = analyze_anchor(df)

    # 更新状态
    state['anchor_result'] = anchor_result
    
    return state


