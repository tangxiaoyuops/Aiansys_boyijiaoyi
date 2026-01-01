"""
阶段分析Agent
分析股票当前处于哪个阶段（一至五阶段）
"""
from typing import Dict, Any
from core.models.state import AnalysisState
from core.tools.technical_analyzer import (
    identify_stage_indicators,
    calculate_ma,
    calculate_macd,
    calculate_rsi,
    compute_gains,
    compute_max_drawdown,
    compute_volatility,
    compute_days_from_high,
    detect_capitulation,
    detect_base,
    detect_breakout,
    detect_box,
    compute_three_stage_features,
    detect_watershed_top,
)
import pandas as pd


def analyze_stage_with_llm(data: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用LLM分析阶段（这里先用规则判断，后续可以集成LLM）
    
    根据文档中的阶段特征进行判断
    """
    # 安全兜底：指标为空直接返回未知阶段，避免 KeyError
    if not indicators:
        return {
            'stage': 0,
            'stage_name': '未知',
            'description': '指标不足，无法判定阶段',
            'confidence': 0.3,
            'indicators': indicators
        }

    current_price = indicators['current_price']
    ma20 = indicators.get('ma20', current_price)
    ma60 = indicators.get('ma60', current_price)
    recent_gain = indicators['recent_gain_20d']
    rsi = indicators['rsi']
    macd_positive = indicators['macd_positive']
    
    # 一阶段特征：缓慢上涨，偶有大阳线后猛跌
    # 二阶段特征：快速上涨，高位运行
    # 三阶段特征：疯狂上涨，持续时间短
    # 四阶段特征：猛烈下跌
    # 五阶段特征：长期阴跌
    
    # 简单规则判断（后续可以用LLM优化）
    volatility = indicators.get('volatility', 0)
    if recent_gain < -20:
        # 大幅下跌，可能是四阶段或五阶段
        if volatility > 3:
            stage = 4  # 四阶段：猛烈下跌
            description = "猛烈下跌阶段，下跌速度快且幅度大"
        else:
            stage = 5  # 五阶段：长期阴跌
            description = "长期阴跌阶段，消磨投资者意志"
    elif recent_gain > 30:
        # 大幅上涨
        if indicators.get('washout_days', 0) < 5:
            stage = 3  # 三阶段：疯狂阶段
            description = "疯狂上涨阶段，持续时间短，需及时止盈"
        else:
            stage = 2  # 二阶段：快速上涨
            description = "快速上涨阶段，上涨幅度最大，伴随持续洗盘"
    elif recent_gain > 0 and current_price > ma20:
        # 缓慢上涨
        stage = 1  # 一阶段：趋势形成初期
        description = "趋势形成初期，缓慢且隐蔽的上涨，杀跌入场"
    else:
        # 不确定
        stage = 0
        description = "阶段不明确，需要更多信息判断"
    
    return {
        'stage': stage,
        'stage_name': ['未知', '一阶段', '二阶段', '三阶段', '四阶段', '五阶段'][stage] if 0 <= stage <= 5 else '未知',
        'description': description,
        'confidence': 0.7,
        'indicators': indicators
    }


def stage_analysis_node(state: AnalysisState) -> AnalysisState:
    """阶段分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")
    if len(stock_data) < 60:
        state['stage_result'] = {
            'stage': 0,
            'stage_name': '未知',
            'description': '数据不足，少于60日',
            'confidence': 0.2,
            'indicators': {}
        }
        return state
    
    # 计算技术指标
    df = calculate_ma(stock_data)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    
    # 获取阶段指标
    indicators = identify_stage_indicators(df)
    if not indicators:
        # 指标不足，直接返回“未知阶段”，避免后续 KeyError
        stage_result = {
            'stage': 0,
            'stage_name': '未知',
            'description': '指标不足，无法判定阶段',
            'confidence': 0.3,
            'indicators': {}
        }
        state['stage_result'] = stage_result
        return state
    
    # 添加波动率信息
    if len(df) >= 20:
        indicators['volatility'] = df.tail(20)['涨跌幅'].std()
        # 计算洗盘天数
        recent_prices = df.tail(30)['收盘'].values
        high_price = recent_prices.max()
        washout_days = 0
        for i in range(len(recent_prices) - 1, -1, -1):
            if recent_prices[i] < high_price * 0.95:
                washout_days += 1
            else:
                break
        indicators['washout_days'] = washout_days
    
    # 分析阶段
    # 计算扩展指标
    gains = compute_gains(df, (20, 60, 120, 180))
    mdd60 = compute_max_drawdown(df, 60)
    mdd120 = compute_max_drawdown(df, 120)
    mdd180 = compute_max_drawdown(df, 180)
    vol20 = compute_volatility(df, 20)
    vol60 = compute_volatility(df, 60)
    days_from_high, high_gap = compute_days_from_high(df, 180)
    cap = detect_capitulation(df, window=40, vol_ratio=1.8)
    base = detect_base(df, cap.get('cap_price'), tol=0.15, min_days=60) if cap.get('has_capitulation') else {'has_base': False}
    breakout = detect_breakout(df, base.get('base_high'), look_forward=10, gain_thresh=0.3, vol_ratio=1.5) if base.get('has_base') else {'has_breakout': False}
    box = detect_box(df, window=120, max_range_pct=40.0, min_days=30)
    three_feat = compute_three_stage_features(df, window=40)
    watershed = detect_watershed_top(df, {
        **indicators,
        **{k: v for k, v in gains.items()},
        'max_drawdown_60': mdd60,
        'max_drawdown_120': mdd120,
        'max_drawdown_180': mdd180,
        'vol20': vol20,
        'vol60': vol60,
        'days_from_high': days_from_high,
        'high_gap_pct': high_gap,
        'events': {}
    })

    indicators.update({
        **{k: v for k, v in gains.items()},
        'max_drawdown_60': mdd60,
        'max_drawdown_120': mdd120,
        'max_drawdown_180': mdd180,
        'vol20': vol20,
        'vol60': vol60,
        'days_from_high': days_from_high,
        'high_gap_pct': high_gap,
        'events': {
            **cap,
            **base,
            **breakout,
            **box,
            **three_feat,
        },
        'risk_flags': {
            'watershed_top': watershed
        }
    })

    # 阶段判定（规则优先级：3>4>5>2>1>未知）
    def rule_three(ind):
        """
        三阶段（疯狂阶段）判定：
        1. 高位 & 大涨 & 回撤不深 & 距高点不远
        2. 形态和量能满足：上影线多 / 象征性洗盘 / 高位大阳放量 / 阳线多于阴线
        """
        gain60 = ind.get('gain60')
        gain120 = ind.get('gain120')
        mdd60_val = ind.get('max_drawdown_60')
        days_from_high = ind.get('days_from_high', 999)
        high_gap_pct = ind.get('high_gap_pct', 0)

        # 1）粗筛：高位 & 大涨 & 回撤不深 & 靠近高点
        high_and_gain = (
            (gain60 is not None and gain60 > 40) or
            (gain120 is not None and gain120 > 80)
        )
        shallow_dd = mdd60_val is not None and mdd60_val > -20
        near_high = days_from_high <= 30 and high_gap_pct < 25
        if not (high_and_gain and shallow_dd and near_high):
            return False

        # 2）形态 + 量能特征
        events = ind.get('events', {}) or {}
        upper_shadow_ratio = events.get('upper_shadow_ratio')
        mild_pullback_runs = events.get('mild_pullback_runs')
        big_bull_count = events.get('big_bull_count')
        vol_ratio_recent = events.get('vol_ratio_recent')
        bull_vs_bear = events.get('bull_vs_bear')

        score = 0

        # 初期：上影线多，涨得不“稳”
        if upper_shadow_ratio is not None and upper_shadow_ratio > 0.3:
            score += 1

        # 中段：象征性洗盘——有至少1段连续4天以上的小跌
        if mild_pullback_runs is not None and mild_pullback_runs >= 1:
            score += 1

        # 末段：高位大阳放量 + 散户涌入
        if big_bull_count is not None and big_bull_count >= 2:
            score += 1
        if vol_ratio_recent is not None and vol_ratio_recent > 1.5:
            score += 1
        if bull_vs_bear is not None and bull_vs_bear > 1.2:
            score += 1

        return score >= 2

    def rule_four(ind):
        return (
            (ind.get('gain20') is not None and ind['gain20'] < -15) or
            (ind.get('gain60') is not None and ind['gain60'] < -25)
        ) or (ind.get('max_drawdown_60') is not None and ind['max_drawdown_60'] < -20)

    def rule_five(ind):
        return (
            (ind.get('gain120') is not None and ind['gain120'] < 0) and
            (ind.get('gain180') is not None and ind['gain180'] < 0)
        ) and (ind.get('vol60') is None or ind['vol60'] < 5)

    def rule_two(ind):
        fast_gain = (ind.get('gain60') and ind['gain60'] > 30) or (ind.get('gain120') and ind['gain120'] > 60)
        shallow_mdd = ind.get('max_drawdown_120') is not None and ind['max_drawdown_120'] > -20
        high_stay = ind.get('days_from_high', 999) > 10 and ind.get('high_gap_pct', 0) < 25
        return fast_gain and shallow_mdd and high_stay

    def rule_one(ind):
        mild_gain = (ind.get('gain60') is not None and 0 <= ind['gain60'] <= 30) and (ind.get('gain120') is not None and 0 <= ind['gain120'] <= 50)
        low_vol = ind.get('vol60') is None or ind['vol60'] < 8
        return mild_gain and low_vol

    stage = 0
    reason = '指标不足或未匹配阶段'
    confidence = 0.3

    if rule_three(indicators):
        stage = 3
        reason = '高位冲顶：近60日涨幅大且回撤小，距离高点<=30日'
        confidence = 0.7
    elif rule_four(indicators):
        stage = 4
        reason = '快速下跌：近20/60日跌幅或回撤显著'
        confidence = 0.7
    elif rule_five(indicators):
        stage = 5
        reason = '长期阴跌：120/180日整体下行，波动不高'
        confidence = 0.6
    elif breakout.get('has_breakout') or box.get('has_box') or rule_two(indicators):
        stage = 2
        reason = '二阶段：出现底部突破/高位箱体，或快速上行且回撤不深'
        confidence = 0.65
    elif base.get('has_base') or rule_one(indicators):
        stage = 1
        reason = '一阶段：底部横盘吸筹或缓慢上行'
        confidence = 0.55

    stage_names = ['未知', '一阶段', '二阶段', '三阶段', '四阶段', '五阶段']
    stage_result = {
        'stage': stage,
        'stage_name': stage_names[stage] if 0 <= stage < len(stage_names) else '未知',
        'description': reason,
        'confidence': confidence,
        'indicators': indicators
    }
    
    # 更新状态
    state['stage_result'] = stage_result
    
    return state

