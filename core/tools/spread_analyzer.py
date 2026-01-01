"""
价差分析工具
提供跨期、跨品种价差分析和套利机会识别
"""
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np


def calculate_spread(
    price1: pd.Series,
    price2: pd.Series
) -> pd.Series:
    """
    计算价差（price1 - price2）
    
    Args:
        price1: 第一个价格序列
        price2: 第二个价格序列
    
    Returns:
        价差序列
    """
    return price1 - price2


def calculate_spread_ratio(
    price1: pd.Series,
    price2: pd.Series
) -> pd.Series:
    """
    计算价差比（price1 / price2）
    
    Args:
        price1: 第一个价格序列
        price2: 第二个价格序列
    
    Returns:
        价差比序列
    """
    return price1 / price2


def analyze_calendar_spread(
    near_month_data: pd.DataFrame,
    far_month_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    分析跨期价差
    
    Args:
        near_month_data: 近月合约数据
        far_month_data: 远月合约数据
    
    Returns:
        {
            'spread_mean': float,  # 价差均值
            'spread_std': float,  # 价差标准差
            'spread_min': float,  # 价差最小值
            'spread_max': float,  # 价差最大值
            'current_spread': float,  # 当前价差
            'spread_percentile': float,  # 当前价差在历史中的分位数
            'trend': str,  # 价差趋势：'widening'/'narrowing'/'stable'
        }
    """
    # 对齐数据
    if '日期' in near_month_data.columns and '日期' in far_month_data.columns:
        merged = pd.merge(
            near_month_data[['日期', '收盘']],
            far_month_data[['日期', '收盘']],
            on='日期',
            suffixes=('_near', '_far')
        )
        near_prices = merged['收盘_near']
        far_prices = merged['收盘_far']
    else:
        # 如果没有日期列，直接按索引对齐
        min_len = min(len(near_month_data), len(far_month_data))
        near_prices = near_month_data['收盘'].iloc[-min_len:]
        far_prices = far_month_data['收盘'].iloc[-min_len:]
    
    # 计算价差
    spread = calculate_spread(near_prices, far_prices)
    
    if spread.empty:
        return {
            'spread_mean': 0.0,
            'spread_std': 0.0,
            'spread_min': 0.0,
            'spread_max': 0.0,
            'current_spread': 0.0,
            'spread_percentile': 50.0,
            'trend': 'unknown'
        }
    
    spread_mean = float(spread.mean())
    spread_std = float(spread.std())
    spread_min = float(spread.min())
    spread_max = float(spread.max())
    current_spread = float(spread.iloc[-1])
    
    # 计算分位数
    spread_percentile = float((spread < current_spread).sum() / len(spread) * 100)
    
    # 判断趋势（最近20天的价差变化）
    if len(spread) >= 20:
        recent_spread = spread.iloc[-20:]
        if recent_spread.iloc[-1] > recent_spread.iloc[0]:
            trend = 'widening'
        elif recent_spread.iloc[-1] < recent_spread.iloc[0]:
            trend = 'narrowing'
        else:
            trend = 'stable'
    else:
        trend = 'unknown'
    
    return {
        'spread_mean': spread_mean,
        'spread_std': spread_std,
        'spread_min': spread_min,
        'spread_max': spread_max,
        'current_spread': current_spread,
        'spread_percentile': spread_percentile,
        'trend': trend
    }


def analyze_inter_commodity_spread(
    commodity1_data: pd.DataFrame,
    commodity2_data: pd.DataFrame
) -> Dict[str, Any]:
    """
    分析跨品种价差
    
    Args:
        commodity1_data: 品种1的数据
        commodity2_data: 品种2的数据
    
    Returns:
        类似跨期价差的分析结果
    """
    return analyze_calendar_spread(commodity1_data, commodity2_data)


def identify_arbitrage_opportunity(
    spread_analysis: Dict[str, Any],
    transaction_cost: float = 0.0,
    threshold_std: float = 2.0
) -> Dict[str, Any]:
    """
    识别套利机会
    
    Args:
        spread_analysis: 价差分析结果
        transaction_cost: 交易成本
        threshold_std: 阈值标准差倍数
    
    Returns:
        {
            'has_opportunity': bool,
            'opportunity_type': str,  # 'buy_spread'/'sell_spread'
            'expected_profit': float,
            'confidence': float,  # 0-1
        }
    """
    spread_mean = spread_analysis.get('spread_mean', 0)
    spread_std = spread_analysis.get('spread_std', 0)
    current_spread = spread_analysis.get('current_spread', 0)
    
    if spread_std == 0:
        return {
            'has_opportunity': False,
            'opportunity_type': None,
            'expected_profit': 0.0,
            'confidence': 0.0
        }
    
    # 计算偏离度（标准差倍数）
    deviation = (current_spread - spread_mean) / spread_std
    
    # 如果价差偏离均值超过阈值，可能存在套利机会
    has_opportunity = abs(deviation) > threshold_std
    
    if not has_opportunity:
        return {
            'has_opportunity': False,
            'opportunity_type': None,
            'expected_profit': 0.0,
            'confidence': min(abs(deviation) / threshold_std, 1.0)
        }
    
    # 判断套利方向
    if deviation > threshold_std:
        # 价差过大，预期回归，卖出价差（卖近买远）
        opportunity_type = 'sell_spread'
        expected_profit = abs(deviation) * spread_std - transaction_cost
    else:
        # 价差过小，预期扩大，买入价差（买近卖远）
        opportunity_type = 'buy_spread'
        expected_profit = abs(deviation) * spread_std - transaction_cost
    
    # 置信度基于偏离程度
    confidence = min(abs(deviation) / (threshold_std * 2), 1.0)
    
    return {
        'has_opportunity': True,
        'opportunity_type': opportunity_type,
        'expected_profit': float(expected_profit),
        'confidence': float(confidence)
    }


def calculate_spread_correlation(
    spread1: pd.Series,
    spread2: pd.Series
) -> float:
    """
    计算两个价差序列的相关性
    
    Args:
        spread1: 价差序列1
        spread2: 价差序列2
    
    Returns:
        相关系数
    """
    # 对齐长度
    min_len = min(len(spread1), len(spread2))
    s1 = spread1.iloc[-min_len:]
    s2 = spread2.iloc[-min_len:]
    
    if len(s1) < 2:
        return 0.0
    
    correlation = s1.corr(s2)
    return float(correlation) if not pd.isna(correlation) else 0.0

