"""
形态识别工具
识别K线形态、洗盘形态、出货形态等
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def recognize_kline_pattern(data: pd.DataFrame, lookback: int = 10) -> Dict[str, Any]:
    """
    识别K线形态
    
    Args:
        data: 股票数据
        lookback: 回看K线数量
    
    Returns:
        形态识别结果
    """
    if len(data) < lookback:
        return {}
    
    recent = data.tail(lookback)
    
    # 识别大阳线
    big_yang = recent['收盘'] > recent['开盘'] * 1.03
    big_yang_count = big_yang.sum()
    
    # 识别大阴线
    big_yin = recent['收盘'] < recent['开盘'] * 0.97
    big_yin_count = big_yin.sum()
    
    # 识别上影线
    upper_shadow = (recent['最高'] - recent[['开盘', '收盘']].max(axis=1)) / recent['收盘']
    long_upper_shadow = (upper_shadow > 0.02).sum()
    
    # 识别下影线
    lower_shadow = (recent[['开盘', '收盘']].min(axis=1) - recent['最低']) / recent['收盘']
    long_lower_shadow = (lower_shadow > 0.02).sum()
    
    # 识别连续上涨/下跌
    consecutive_up = 0
    consecutive_down = 0
    for i in range(len(recent) - 1, 0, -1):
        if recent.iloc[i]['收盘'] > recent.iloc[i-1]['收盘']:
            consecutive_up += 1
            consecutive_down = 0
        elif recent.iloc[i]['收盘'] < recent.iloc[i-1]['收盘']:
            consecutive_down += 1
            consecutive_up = 0
        else:
            break
    
    return {
        'big_yang_count': int(big_yang_count),
        'big_yin_count': int(big_yin_count),
        'long_upper_shadow_count': int(long_upper_shadow),
        'long_lower_shadow_count': int(long_lower_shadow),
        'consecutive_up': int(consecutive_up),
        'consecutive_down': int(consecutive_down),
        'recent_trend': 'up' if consecutive_up > consecutive_down else 'down'
    }


def identify_washout_type(data: pd.DataFrame) -> Dict[str, Any]:
    """
    识别洗盘类型（K线洗盘 vs 波段洗盘）
    
    Returns:
        洗盘类型和特征
    """
    if len(data) < 20:
        return {'type': 'unknown', 'confidence': 0}
    
    recent = data.tail(30)
    
    # K线洗盘特征：几根K线组合打破上涨形态
    # 波段洗盘特征：一段时间的下跌，没有分水岭高点
    
    # 计算高点
    highs = recent['最高'].values
    # 寻找最近的高点
    recent_high_idx = len(highs) - 1
    for i in range(len(highs) - 2, -1, -1):
        if highs[i] > highs[recent_high_idx]:
            recent_high_idx = i
    
    # 计算从高点后的跌幅
    high_price = highs[recent_high_idx]
    current_price = recent.iloc[-1]['收盘']
    drawdown = ((high_price - current_price) / high_price) * 100
    
    # 计算下跌天数
    down_days = 0
    for i in range(len(recent) - 1, recent_high_idx, -1):
        if recent.iloc[i]['收盘'] < recent.iloc[i-1]['收盘']:
            down_days += 1
        else:
            break
    
    # 判断类型
    if down_days <= 5 and drawdown > 3:
        # 短期快速下跌，可能是K线洗盘
        washout_type = 'kline'
        confidence = min(0.8, drawdown / 10)
    elif down_days > 5:
        # 较长时间的下跌，可能是波段洗盘
        washout_type = 'wave'
        confidence = min(0.8, down_days / 20)
    else:
        washout_type = 'unknown'
        confidence = 0.3
    
    return {
        'type': washout_type,
        'confidence': float(confidence),
        'drawdown': float(drawdown),
        'down_days': int(down_days),
        'high_price': float(high_price),
        'current_price': float(current_price)
    }


def identify_distribution_scale(data: pd.DataFrame) -> Dict[str, Any]:
    """
    识别最近一轮出货规模（large / medium / small / none）
    回溯原则：
      - 使用最近最多 3 年左右数据（约 750 根K线）
      - 高位出货区间的持续时间与放量程度、K线形态一起决定规模：
        small  ~ 3-6 个月
        medium ~ 1 年
        large  ~ 1 年以上 / 多次高调出货
    """
    if len(data) < 80:
        return {"scale": "unknown", "confidence": 0}

    # 1. 取最近约 3 年的数据上限（750 根K线）
    MAX_WINDOW = 750
    recent = data.tail(MAX_WINDOW).copy()

    # 2. 找最高点（最近一轮出货的“顶”）
    max_idx = recent["最高"].idxmax()
    max_price = float(recent.loc[max_idx, "最高"])
    max_date = recent.loc[max_idx, "日期"]

    # 3. 向前回溯，找到高位出货区间：
    #    收盘价在 max_price * 0.8 以上的这段视为“高位区间”
    close = recent["收盘"]
    zone_indices: List[int] = []
    started = False
    threshold = max_price * 0.8  # 高位下沿，可微调成 0.75~0.85

    for idx in recent.index:
        if idx > max_idx:
            break
        price = close.loc[idx]
        if price >= threshold:
            zone_indices.append(idx)
            started = True
        else:
            if started:
                break

    days_from_high = len(recent) - (recent.index.get_loc(max_idx) if max_idx in recent.index else 0)

    if not zone_indices:
        return {
            "scale": "none",
            "confidence": 0.3,
            "days_from_high": int(days_from_high),
            "high_price": max_price,
            "high_date": max_date,
        }

    zone = recent.loc[zone_indices[0] : zone_indices[-1]]
    zone_days = len(zone)
    zone_low = float(zone["收盘"].min())
    zone_high = float(zone["收盘"].max())
    zone_range_pct = (zone_high - zone_low) / zone_low * 100 if zone_low > 0 else 0.0

    # 4. 放量倍数：高位区间 vs 高位前一段（用约1年作为对比基准）
    zone_vol_avg = zone["成交量"].mean()
    pre_window = recent[recent.index < zone_indices[0]].tail(250)
    pre_vol_avg = pre_window["成交量"].mean() if not pre_window.empty else None
    # 高位区间整体的放量倍数（对比前段）
    if pre_vol_avg and pre_vol_avg > 0:
        volume_ratio = zone_vol_avg / pre_vol_avg
    else:
        volume_ratio = 1.0

    # 5. 高位大阳/涨停 & 高位剧烈波动天数
    body = (zone["收盘"] - zone["开盘"]) / zone["开盘"]
    big_up = body > 0.05  # >5% 视为大阳/涨停尝试
    # 对“出货大阳”来说，放量应当相对于高位前一段，而不是区间内部的平均
    # 这里适当降低放量门槛到 ~1.5 倍，让典型但不极端的出货形态也能被识别出来
    vol_baseline = pre_vol_avg if pre_vol_avg and pre_vol_avg > 0 else zone_vol_avg
    vol_big = zone["成交量"] > (vol_baseline * 1.5 if vol_baseline else 0)

    # 计算高位区间开始前一段的“前高”，用于判断是否为突破前高的大阳/涨停
    pre_segment = recent[recent.index < zone_indices[0]]
    if not pre_segment.empty:
        prev_high = float(pre_segment["收盘"].max())
    else:
        prev_high = zone_low  # 若无前段，则退化为区间低点

    close_zone = zone["收盘"]
    near_or_break_prev_high = close_zone >= prev_high * 0.97  # 接近或突破前高

    # 只有突破/接近前高的大阳+放量才算出货K线
    big_up_mask = big_up & vol_big & near_or_break_prev_high
    big_up_days = int(big_up_mask.sum())

    upper_shadow = (zone["最高"] - zone[["开盘", "收盘"]].max(axis=1)) / zone["收盘"]
    lower_shadow = (zone[["开盘", "收盘"]].min(axis=1) - zone["最低"]) / zone["收盘"]
    choppy = (
        (body.abs() < 0.03)
        & ((upper_shadow > 0.03) | (lower_shadow > 0.03))
        & vol_big
    )
    choppy_days = int(choppy.sum())

    # 6. 高位之后的最大跌幅（辅助判断“小规模快速出货”）
    after_high = recent[recent.index > max_idx].head(60)
    post_drop = 0.0
    if not after_high.empty:
        post_low = float(after_high["收盘"].min())
        post_drop = (max_price - post_low) / max_price * 100

    # 7. 根据 zone_days + 量价特征划分规模
    scale = "none"
    confidence = 0.3

    # 小规模（约 3-6 个月 / <60 交易日），时间相对较短、放量明显、有 1-4 根高位大阳，随后快速下跌
    if (
        zone_days <= 60
        and volume_ratio > 1.3
        and 1 <= big_up_days <= 4
        and post_drop > 20
    ):
        scale = "small"
        confidence = 0.6
    # 特例：区间时间很短（<=10天），整体明显放量且随后大跌，
    # 即使统计不到“突破前高大阳”的天数，也直接视为小规模出货
    elif (
        zone_days <= 10
        and volume_ratio > 1.5
        and post_drop > 30
    ):
        scale = "small"
        confidence = 0.6

    # 中等规模（约 1 年 / 60-250 日），高位震荡时间中等，放量更明显
    if (
        60 < zone_days <= 250
        and volume_ratio > 1.7
        and big_up_days >= 3
        and choppy_days >= 2
    ):
        scale = "medium"
        confidence = 0.7

    # 大规模（>1 年），高位长期震荡放量，多次高调突破
    if (
        zone_days > 250
        and volume_ratio >= 2.0
        and big_up_days >= 5
        and choppy_days >= 3
    ):
        scale = "large"
        confidence = 0.8

    return {
        "scale": scale,
        "confidence": float(confidence),
        "days_from_high": int(days_from_high),
        "high_price": float(max_price),
        "high_date": max_date,
        "zone_days": int(zone_days),
        "zone_low": zone_low,
        "zone_high": zone_high,
        "zone_range_pct": float(zone_range_pct),
        "volume_ratio": float(volume_ratio),
        "big_up_days": big_up_days,
        "choppy_days": choppy_days,
        "post_drop_pct": float(post_drop),
    }


