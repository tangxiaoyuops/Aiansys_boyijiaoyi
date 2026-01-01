"""
期货技术分析工具
提供期货专用的技术指标计算和形态识别
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List


def calculate_ma_futures(df: pd.DataFrame, periods: Tuple[int, ...] = (5, 10, 20, 60)) -> Dict[str, pd.Series]:
    """
    计算期货移动平均线
    
    Args:
        df: 包含'收盘'列的DataFrame
        periods: 均线周期
    
    Returns:
        {f'ma{period}': Series, ...}
    """
    result = {}
    for period in periods:
        if len(df) >= period:
            result[f'ma{period}'] = df['收盘'].rolling(window=period).mean()
        else:
            result[f'ma{period}'] = pd.Series([np.nan] * len(df))
    return result


def calculate_macd_futures(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Dict[str, pd.Series]:
    """
    计算期货MACD指标
    
    Args:
        df: 包含'收盘'列的DataFrame
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
    
    Returns:
        {'macd': Series, 'signal': Series, 'hist': Series}
    """
    close = df['收盘']
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    
    return {
        'macd': macd,
        'signal': signal_line,
        'hist': hist
    }


def calculate_rsi_futures(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    计算期货RSI指标
    
    Args:
        df: 包含'收盘'列的DataFrame
        period: RSI周期
    
    Returns:
        RSI Series
    """
    close = df['收盘']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def compute_futures_gains(df: pd.DataFrame, windows: Tuple[int, ...] = (20, 60, 120)) -> Dict[str, float]:
    """计算期货多窗口涨跌幅（%）"""
    res = {}
    for w in windows:
        if len(df) >= w + 1:
            start = df.iloc[-(w + 1)]['收盘']
            end = df.iloc[-1]['收盘']
            if start and not pd.isna(start) and start != 0:
                res[f'gain{w}'] = float((end - start) / start * 100)
            else:
                res[f'gain{w}'] = 0.0
        else:
            res[f'gain{w}'] = None
    return res


def compute_futures_max_drawdown(df: pd.DataFrame, window: int = 180) -> float:
    """计算期货近window日最大回撤（%）"""
    if df.empty:
        return None
    recent = df.tail(window) if len(df) > window else df
    highs = recent['收盘'].cummax()
    drawdown = (recent['收盘'] - highs) / highs
    return float(drawdown.min() * 100)


def compute_futures_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """计算期货近window日波动率（收盘收益率标准差，%）"""
    if len(df) < window + 1:
        return None
    recent = df.tail(window + 1)['收盘'].pct_change().dropna()
    return float(recent.std() * 100)


def analyze_open_interest_trend(df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
    """
    分析持仓量趋势
    
    Args:
        df: 包含'持仓量'列的DataFrame
        window: 分析窗口
    
    Returns:
        {
            'trend': str,  # 'increasing'/'decreasing'/'stable'
            'change_pct': float,  # 持仓量变化百分比
            'avg_oi': float,  # 平均持仓量
        }
    """
    if '持仓量' not in df.columns or df.empty:
        return {
            'trend': 'unknown',
            'change_pct': 0.0,
            'avg_oi': 0.0
        }
    
    recent = df.tail(window) if len(df) > window else df
    oi = recent['持仓量'].dropna()
    
    if len(oi) < 2:
        return {
            'trend': 'unknown',
            'change_pct': 0.0,
            'avg_oi': float(oi.mean()) if not oi.empty else 0.0
        }
    
    start_oi = oi.iloc[0]
    end_oi = oi.iloc[-1]
    change_pct = ((end_oi - start_oi) / start_oi * 100) if start_oi != 0 else 0.0
    
    # 判断趋势
    if change_pct > 5:
        trend = 'increasing'
    elif change_pct < -5:
        trend = 'decreasing'
    else:
        trend = 'stable'
    
    return {
        'trend': trend,
        'change_pct': float(change_pct),
        'avg_oi': float(oi.mean())
    }


def detect_futures_stage_candidates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    识别期货阶段候选区间（类似股票的五阶段分析）
    
    Args:
        df: K线数据
    
    Returns:
        阶段候选区间列表
    """
    candidates = []
    
    if df.empty or len(df) < 60:
        return candidates
    
    # 识别恐慌低点（类似股票的O点）
    recent = df.tail(180) if len(df) > 180 else df
    vol_avg = recent['成交量'].mean()
    
    # 寻找放量下跌的低点
    for i in range(10, len(recent) - 5):
        row = recent.iloc[i]
        prev_rows = recent.iloc[max(0, i-10):i]
        next_rows = recent.iloc[i+1:min(len(recent), i+6)]
        
        # 条件：放量、低点、后续有反弹
        if (row['成交量'] > vol_avg * 1.5 and
            row['收盘'] < prev_rows['收盘'].min() * 0.95 and
            next_rows['收盘'].max() > row['收盘'] * 1.05):
            
            candidates.append({
                'type': 'panic_low',
                'date': row['日期'] if '日期' in recent.columns else i,
                'price': float(row['收盘']),
                'description': '恐慌性低点'
            })
    
    return candidates


def compute_futures_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    计算期货技术指标综合结果
    
    Args:
        df: K线数据
    
    Returns:
        技术指标字典
    """
    if df.empty:
        return {}
    
    indicators = {}
    
    # 计算均线
    ma_result = calculate_ma_futures(df)
    for key, value in ma_result.items():
        indicators[key] = float(value.iloc[-1]) if not value.isna().iloc[-1] else None
    
    # 计算MACD
    macd_result = calculate_macd_futures(df)
    indicators['macd'] = float(macd_result['macd'].iloc[-1]) if not macd_result['macd'].isna().iloc[-1] else None
    indicators['macd_signal'] = float(macd_result['signal'].iloc[-1]) if not macd_result['signal'].isna().iloc[-1] else None
    indicators['macd_hist'] = float(macd_result['hist'].iloc[-1]) if not macd_result['hist'].isna().iloc[-1] else None
    
    # 计算RSI
    rsi = calculate_rsi_futures(df)
    indicators['rsi'] = float(rsi.iloc[-1]) if not rsi.isna().iloc[-1] else None
    
    # 计算涨跌幅
    gains = compute_futures_gains(df)
    indicators.update(gains)
    
    # 计算最大回撤
    indicators['max_drawdown_60'] = compute_futures_max_drawdown(df, 60)
    indicators['max_drawdown_120'] = compute_futures_max_drawdown(df, 120)
    
    # 计算波动率
    indicators['volatility_20'] = compute_futures_volatility(df, 20)
    indicators['volatility_60'] = compute_futures_volatility(df, 60)
    
    # 当前价格
    indicators['current_price'] = float(df.iloc[-1]['收盘'])
    
    # 持仓量趋势
    if '持仓量' in df.columns:
        oi_trend = analyze_open_interest_trend(df)
        indicators['open_interest_trend'] = oi_trend
    
    return indicators

