"""
大宗商品技术指标计算Agent
计算各类技术指标，识别市场状态
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.technical_indicators import create_technical_indicator_calculator


def technical_indicators_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    技术指标计算节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[技术指标] 开始计算技术指标")
    
    raw_evidence = state.get("raw_evidence")
    
    if not raw_evidence or not raw_evidence.get("prices"):
        print("[技术指标] 警告: 没有价格数据")
        state["technical_indicators"] = None
        state["market_state"] = "unknown"
        return state
    
    prices = raw_evidence.get("prices", [])
    
    print(f"[技术指标] 接收到 {len(prices)} 条价格数据")
    if prices:
        latest = prices[-1]
        print(f"[技术指标] 最新价格数据: 日期={latest.get('as_of_date')}, 收盘={latest.get('value')}, 最高={latest.get('high')}, 最低={latest.get('low')}")
    
    if len(prices) < 60:
        print(f"[技术指标] 警告: 价格数据不足（{len(prices)}条），需要至少60条")
        state["technical_indicators"] = None
        state["market_state"] = "insufficient_data"
        return state
    
    try:
        calculator = create_technical_indicator_calculator()
        
        close_prices = [p["value"] for p in prices]
        high_prices = [p.get("high", p["value"]) for p in prices]
        low_prices = [p.get("low", p["value"]) for p in prices]
        
        print(f"[技术指标] 收盘价范围: {min(close_prices):.2f} - {max(close_prices):.2f}")
        print(f"[技术指标] 最新5个收盘价: {close_prices[-5:]}")
        
        technical_indicators = calculator.calculate_all_indicators(
            high=high_prices,
            low=low_prices,
            close=close_prices
        )
        
        state["technical_indicators"] = technical_indicators
        
        market_state = _identify_market_state(technical_indicators)
        state["market_state"] = market_state
        
        print(f"[技术指标] 技术指标计算完成")
        print(f"[技术指标] 市场状态: {market_state}")
        print(f"[技术指标] MA短期: {technical_indicators.get('ma_short')}")
        print(f"[技术指标] MA中期: {technical_indicators.get('ma_medium')}")
        print(f"[技术指标] MA长期: {technical_indicators.get('ma_long')}")
        print(f"[技术指标] RSI: {technical_indicators.get('rsi')}")
        print(f"[技术指标] MACD: {technical_indicators.get('macd_bar')}")
        
    except Exception as e:
        error_msg = f"技术指标计算失败: {str(e)}"
        print(f"[技术指标] {error_msg}")
        state["technical_indicators"] = None
        state["market_state"] = "error"
    
    return state


def _identify_market_state(indicators: dict) -> str:
    """
    识别市场状态
    
    Args:
        indicators: 技术指标
    
    Returns:
        市场状态: trend/range/reversal
    """
    ma_short = indicators.get("ma_short")
    ma_medium = indicators.get("ma_medium")
    ma_long = indicators.get("ma_long")
    macd_bar = indicators.get("macd_bar")
    rsi = indicators.get("rsi")
    
    if None in [ma_short, ma_medium, ma_long]:
        return "unknown"
    
    if ma_short > ma_medium > ma_long:
        if macd_bar and macd_bar > 0:
            return "uptrend"
        else:
            return "uptrend_weak"
    elif ma_short < ma_medium < ma_long:
        if macd_bar and macd_bar < 0:
            return "downtrend"
        else:
            return "downtrend_weak"
    else:
        if rsi:
            if rsi > 70:
                return "overbought"
            elif rsi < 30:
                return "oversold"
        
        return "range"
