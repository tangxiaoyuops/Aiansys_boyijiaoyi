"""
出货分析Agent
分析出货规模（大规模/中等规模/小规模）
优先使用高级时间轴分析，失败时回退到简单规则
"""
from core.models.state import AnalysisState
from core.tools.pattern_recognizer import identify_distribution_scale
from core.tools.advanced_distribution_analyzer import analyze_distribution_advanced
import pandas as pd


def distribution_analysis_node(state: AnalysisState) -> AnalysisState:
    """出货分析节点"""
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")

    required_cols = ['最高', '涨跌幅', '成交量', '日期', '开盘', '收盘', '最低']
    for col in required_cols:
        if col not in stock_data.columns:
            state['distribution_result'] = {'scale': 'unknown', 'confidence': 0, 'error': f'缺少必要列: {col}'}
            return state

    df = stock_data.copy()
    for col in ['最高', '涨跌幅', '成交量', '开盘', '收盘', '最低']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期', '最高', '收盘'])
    df = df.sort_values('日期').reset_index(drop=True)
    if df.empty:
        state['distribution_result'] = {'scale': 'unknown', 'confidence': 0, 'error': '数据无有效高点'}
        return state

    # 优先使用高级时间轴分析
    try:
        advanced_result = analyze_distribution_advanced(df)
        latest_cycle = advanced_result.get('latest_cycle')
        
        if latest_cycle:
            # 使用高级分析结果
            distribution_result = {
                'scale': latest_cycle.scale,
                'confidence': 0.7 if latest_cycle.total_watershed_count > 0 else 0.5,
                'high_price': latest_cycle.max_price,
                'high_date': latest_cycle.end_date,
                'zone_days': latest_cycle.cycle_days,
                'volume_ratio': sum(s.volume_ratio for s in latest_cycle.segments) / len(latest_cycle.segments) if latest_cycle.segments else 1.0,
                'big_up_days': latest_cycle.total_watershed_count,
                'post_drop_pct': latest_cycle.post_cycle_drop_pct,
                'days_from_high': (df.iloc[-1]['日期'] - latest_cycle.end_date).days if isinstance(latest_cycle.end_date, pd.Timestamp) else 0,
                'from_advanced_analyzer': True,
                'watershed_count': latest_cycle.total_watershed_count,
                'cycle_start': latest_cycle.start_date,
                'cycle_end': latest_cycle.end_date,
                'summary': advanced_result.get('summary', '')
            }
        else:
            # 高级分析未找到周期，回退到简单规则
            distribution_result = identify_distribution_scale(df)
            distribution_result['from_advanced_analyzer'] = False
    except Exception as e:
        # 高级分析出错，回退到简单规则
        import traceback
        print(f"[出货分析] 高级分析失败，回退到简单规则: {e}")
        print(traceback.format_exc())
        distribution_result = identify_distribution_scale(df)
        distribution_result['from_advanced_analyzer'] = False

    # 如果阶段分析里检测到了高位分水岭形态，则至少应视为“有出货”
    # - 若原本规模为 none/unknown，则提升为 small，并注明由分水岭触发
    # - 若已有 small/medium/large，则保持规模不变，只是后续在总结/策略中叠加风险解释
    stage_result = state.get('stage_result') or {}
    indicators = stage_result.get('indicators') or {}
    risk_flags = indicators.get('risk_flags') or {}
    watershed = risk_flags.get('watershed_top') or {}
    if watershed.get('has_watershed_top'):
        scale = distribution_result.get('scale', 'unknown')
        if scale in ['none', 'unknown', None]:
            distribution_result['scale'] = 'small'
            distribution_result['confidence'] = max(
                float(distribution_result.get('confidence', 0.5)), 0.6
            )
            distribution_result['from_watershed'] = True
        else:
            distribution_result['from_watershed'] = True

    # 添加操作建议
    scale = distribution_result.get('scale', 'unknown')
    days_from_high = distribution_result.get('days_from_high', 0)
    
    if scale == 'large':
        operation_advice = "大规模出货，一年内不建议做中线和长线投资，仅做短线操作"
    elif scale == 'medium':
        operation_advice = "中等规模出货，洗盘三个月后直接上涨，可入场5%资金作为底仓"
    elif scale == 'small':
        operation_advice = "小规模出货，在洗盘过程中逐步买入，持续加仓"
    else:
        operation_advice = "未识别到明显出货，继续观察"
    
    distribution_result['operation_advice'] = operation_advice
    
    # 更新状态
    state['distribution_result'] = distribution_result
    
    return state


