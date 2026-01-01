"""
常规分析Agent
进行常规技术分析
"""
from core.models.state import AnalysisState
from core.tools.technical_analyzer import calculate_ma, calculate_macd, calculate_rsi
import pandas as pd


def regular_analysis_node(state: AnalysisState) -> AnalysisState:
    """常规分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    # 确保关键列存在且为数值
    required_cols = ['收盘', '开盘', '最高', '最低', '成交量']
    for col in required_cols:
        if col not in stock_data.columns:
            raise ValueError(f"缺少必要列: {col}")
    df = stock_data.copy()
    numeric_cols = ['收盘', '开盘', '最高', '最低', '成交量']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['收盘'])
    if df.empty:
        raise ValueError("股票数据无有效收盘价")

    # 计算技术指标
    df = calculate_ma(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)

    # 获取最新指标值
    latest = df.iloc[-1]

    # 生成分析结果
    analysis_result = {
        'indicators': {
            'MA5': float(latest.get('MA5', 0)),
            'MA10': float(latest.get('MA10', 0)),
            'MA20': float(latest.get('MA20', 0)),
            'MA60': float(latest.get('MA60', 0)) if not pd.isna(latest.get('MA60')) else None,
            'MACD': float(latest.get('MACD', 0)),
            'MACD_Signal': float(latest.get('MACD_Signal', 0)),
            'MACD_Hist': float(latest.get('MACD_Hist', 0)),
            'RSI': float(latest.get('RSI', 50))
        },
        'current_price': float(latest.get('收盘', 0)),
        'analysis': '常规技术分析完成'
    }

    # 简单交易建议
    current_price = latest.get('收盘', 0)
    ma20 = latest.get('MA20', current_price)
    rsi = latest.get('RSI', 50)
    macd_hist = latest.get('MACD_Hist', 0)

    if current_price > ma20 and rsi < 70 and macd_hist > 0:
        analysis_result['suggestion'] = '买入'
        analysis_result['confidence'] = '中'
    elif current_price < ma20 or rsi > 70:
        analysis_result['suggestion'] = '卖出'
        analysis_result['confidence'] = '中'
    else:
        analysis_result['suggestion'] = '观望'
        analysis_result['confidence'] = '低'

    # 更新状态
    state['regular_analysis_result'] = analysis_result

    return state


