"""
计算工具
实现洗盘公式、情绪比例关系等计算
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_washout_effect(data: pd.DataFrame, washout_period: int = 30) -> Dict[str, Any]:
    """
    计算洗盘效果
    洗盘效果 = 恐惧程度 × 焦虑程度 × (1 - 场内散户数量比例)
    
    Args:
        data: 股票数据
        washout_period: 洗盘周期天数
    
    Returns:
        洗盘效果评分
    """
    if len(data) < washout_period:
        return {'washout_score': 0, 'fear_level': 0, 'anxiety_level': 0, 'retail_ratio': 1}
    
    recent = data.tail(washout_period)
    
    # 1. 恐惧程度：股票走势的难看程度
    # 计算波动率、最大回撤、下跌天数
    volatility = recent['涨跌幅'].std()
    max_drawdown = ((recent['最高'].max() - recent['最低'].min()) / recent['最高'].max()) * 100
    down_days = (recent['涨跌幅'] < 0).sum()
    down_ratio = down_days / len(recent)
    
    # 恐惧程度评分（0-1）
    fear_level = min(1.0, (volatility / 5 + max_drawdown / 20 + down_ratio) / 3)
    
    # 2. 焦虑程度：持有股票的时间越长，焦虑程度越大
    # 计算横盘或下跌的持续时间
    current_price = recent.iloc[-1]['收盘']
    high_price = recent['最高'].max()
    price_ratio = current_price / high_price
    
    # 如果价格从高点下跌超过10%，开始计算焦虑
    if price_ratio < 0.9:
        anxiety_days = 0
        for i in range(len(recent) - 1, -1, -1):
            if recent.iloc[i]['收盘'] < high_price * 0.9:
                anxiety_days += 1
            else:
                break
        anxiety_level = min(1.0, anxiety_days / washout_period)
    else:
        anxiety_level = 0
    
    # 3. 场内散户数量：通过成交量变化估算
    # 成交量萎缩表示散户离场
    early_volume = recent.head(10)['成交量'].mean()
    recent_volume = recent.tail(10)['成交量'].mean()
    volume_ratio = recent_volume / early_volume if early_volume > 0 else 1
    
    # 成交量萎缩表示散户减少
    retail_ratio = min(1.0, volume_ratio)
    
    # 洗盘效果评分
    washout_score = fear_level * anxiety_level * (1 - retail_ratio * 0.5)
    
    return {
        'washout_score': float(washout_score),
        'fear_level': float(fear_level),
        'anxiety_level': float(anxiety_level),
        'retail_ratio': float(retail_ratio),
        'volatility': float(volatility),
        'max_drawdown': float(max_drawdown),
        'down_days': int(down_days),
        'volume_ratio': float(volume_ratio)
    }


def calculate_emotion_ratio(data: pd.DataFrame, lookback: int = 60) -> Dict[str, Any]:
    """
    计算情绪比例关系
    较为好看的出货 + 非常难看的洗盘 = 看涨
    较为难看的洗盘 + 非常好看的出货 = 看跌
    
    Args:
        data: 股票数据
        lookback: 回看天数
    
    Returns:
        情绪比例关系分析
    """
    if len(data) < lookback:
        return {'direction': 'neutral', 'confidence': 0}
    
    recent = data.tail(lookback)
    
    # 将数据分为两段：前半段（可能的出货）和后半段（可能的洗盘）
    mid_point = len(recent) // 2
    first_half = recent.head(mid_point)
    second_half = recent.tail(len(recent) - mid_point)
    
    # 分析前半段（出货形态）
    # "好看"的出货：上涨流畅、阳线多、波动小
    first_gain = ((first_half.iloc[-1]['收盘'] - first_half.iloc[0]['收盘']) / first_half.iloc[0]['收盘']) * 100
    first_yang_ratio = (first_half['收盘'] > first_half['开盘']).sum() / len(first_half)
    first_volatility = first_half['涨跌幅'].std()
    
    # 出货"好看程度"（0-1，越高越好看）
    distribution_beauty = min(1.0, (max(0, first_gain) / 20 + first_yang_ratio + (1 - min(1, first_volatility / 5))) / 3)
    
    # 分析后半段（洗盘形态）
    # "难看"的洗盘：下跌、阴线多、波动大
    second_gain = ((second_half.iloc[-1]['收盘'] - second_half.iloc[0]['收盘']) / second_half.iloc[0]['收盘']) * 100
    second_yin_ratio = (second_half['收盘'] < second_half['开盘']).sum() / len(second_half)
    second_volatility = second_half['涨跌幅'].std()
    
    # 洗盘"难看程度"（0-1，越高越难看）
    washout_ugliness = min(1.0, (max(0, -second_gain) / 20 + second_yin_ratio + min(1, second_volatility / 5)) / 3)
    
    # 判断方向
    # 较为好看的出货（>0.5） + 非常难看的洗盘（>0.7） = 看涨
    # 较为难看的洗盘（>0.5） + 非常好看的出货（>0.7） = 看跌
    if distribution_beauty > 0.5 and washout_ugliness > 0.7:
        direction = 'bullish'
        confidence = min(0.9, (distribution_beauty + washout_ugliness) / 2)
    elif washout_ugliness > 0.5 and distribution_beauty > 0.7:
        direction = 'bearish'
        confidence = min(0.9, (washout_ugliness + distribution_beauty) / 2)
    else:
        direction = 'neutral'
        confidence = 0.5
    
    return {
        'direction': direction,
        'confidence': float(confidence),
        'distribution_beauty': float(distribution_beauty),
        'washout_ugliness': float(washout_ugliness),
        'first_half_gain': float(first_gain),
        'second_half_gain': float(second_gain)
    }


