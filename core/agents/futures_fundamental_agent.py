"""
期货基本面分析Agent
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.futures_analyzer import analyze_open_interest_trend


def futures_fundamental_analysis_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货基本面分析节点"""
    futures_code = state.get('futures_code', '')
    futures_data = state.get('futures_data')
    
    print(f"[期货基本面分析] 开始分析: {futures_code}")
    
    if futures_data is None or futures_data.empty:
        print(f"[期货基本面分析] 错误: 缺少期货数据")
        state['fundamental_analysis_result'] = {
            'error': '缺少期货数据，请先运行futures_data_fetch_node'
        }
        return state
    
    try:
        result = {}
        
        # 持仓量分析
        if '持仓量' in futures_data.columns:
            print(f"[期货基本面分析] 正在分析持仓量趋势...")
            oi_trend = analyze_open_interest_trend(futures_data)
            result['open_interest'] = {
                'trend': oi_trend.get('trend', 'unknown'),
                'change_pct': oi_trend.get('change_pct', 0),
                'avg_oi': oi_trend.get('avg_oi', 0),
                'current_oi': float(futures_data.iloc[-1]['持仓量']) if '持仓量' in futures_data.columns else 0,
                'analysis': _analyze_open_interest_meaning(oi_trend)
            }
            print(f"[期货基本面分析] 持仓量趋势: {oi_trend.get('trend')}, 变化: {oi_trend.get('change_pct', 0):.2f}%, 当前持仓量: {result['open_interest']['current_oi']:.0f}")
        
        # 成交量分析
        if '成交量' in futures_data.columns:
            print(f"[期货基本面分析] 正在分析成交量...")
            volume_analysis = _analyze_volume(futures_data)
            result['volume'] = volume_analysis
            print(f"[期货基本面分析] 成交量分析完成: {volume_analysis.get('analysis', '')}")
        
        # 价格与持仓量关系分析
        if '持仓量' in futures_data.columns and '收盘' in futures_data.columns:
            print(f"[期货基本面分析] 正在分析价量关系...")
            price_oi_analysis = _analyze_price_oi_relationship(futures_data)
            result['price_oi_relationship'] = price_oi_analysis
            print(f"[期货基本面分析] 价量关系: {price_oi_analysis.get('relationship', '')}")
        
        # 基差分析（如果有基差数据）
        basis_data = state.get('basis_data')
        if basis_data is not None and not basis_data.empty:
            print(f"[期货基本面分析] 发现基差数据，正在分析...")
            result['basis'] = {
                'current_basis': float(basis_data.iloc[-1]['basis']) if 'basis' in basis_data.columns else None,
                'analysis': '基差数据可用，但详细分析需要更多信息'
            }
        
        # 基本面总结
        result['summary'] = _generate_fundamental_summary(result)
        print(f"[期货基本面分析] 基本面总结: {result['summary']}")
        
        state['fundamental_analysis_result'] = result
        print(f"[期货基本面分析] 基本面分析完成")
        
    except Exception as e:
        print(f"[期货基本面分析] 分析失败: {e}")
        import traceback
        print(f"[期货基本面分析] 错误堆栈: {traceback.format_exc()}")
        state['fundamental_analysis_result'] = {
            'error': f'分析失败: {str(e)}'
        }
    
    return state


def _analyze_open_interest_meaning(oi_trend: dict) -> str:
    """分析持仓量变化的含义"""
    trend = oi_trend.get('trend', 'unknown')
    change_pct = oi_trend.get('change_pct', 0)
    
    if trend == 'increasing':
        if change_pct > 10:
            return "持仓量大幅增加，表明资金大量流入，市场情绪积极"
        else:
            return "持仓量小幅增加，市场情绪温和向好"
    elif trend == 'decreasing':
        if change_pct < -10:
            return "持仓量大幅减少，表明资金流出，市场情绪谨慎"
        else:
            return "持仓量小幅减少，市场情绪趋于谨慎"
    else:
        return "持仓量相对稳定，市场情绪中性"


def _analyze_volume(futures_data) -> dict:
    """分析成交量"""
    if '成交量' not in futures_data.columns:
        return {}
    
    recent_20 = futures_data.tail(20)['成交量']
    recent_60 = futures_data.tail(60)['成交量'] if len(futures_data) >= 60 else recent_20
    
    avg_volume_20 = float(recent_20.mean())
    avg_volume_60 = float(recent_60.mean())
    current_volume = float(futures_data.iloc[-1]['成交量'])
    
    volume_ratio = (avg_volume_20 / avg_volume_60) if avg_volume_60 > 0 else 1.0
    current_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 1.0
    
    return {
        'avg_volume_20': avg_volume_20,
        'avg_volume_60': avg_volume_60,
        'current_volume': current_volume,
        'volume_ratio': volume_ratio,
        'current_ratio': current_ratio,
        'analysis': f'近期成交量{"放大" if volume_ratio > 1.2 else "缩小" if volume_ratio < 0.8 else "稳定"}，当前成交量{"放大" if current_ratio > 1.5 else "正常" if current_ratio > 0.5 else "萎缩"}'
    }


def _analyze_price_oi_relationship(futures_data) -> dict:
    """分析价格与持仓量的关系"""
    if '持仓量' not in futures_data.columns or '收盘' not in futures_data.columns:
        return {}
    
    recent = futures_data.tail(20)
    price_change = (recent.iloc[-1]['收盘'] - recent.iloc[0]['收盘']) / recent.iloc[0]['收盘'] * 100
    oi_change = (recent.iloc[-1]['持仓量'] - recent.iloc[0]['持仓量']) / recent.iloc[0]['持仓量'] * 100 if recent.iloc[0]['持仓量'] > 0 else 0
    
    # 判断价格与持仓量的关系
    if price_change > 0 and oi_change > 0:
        relationship = "价格上涨 + 持仓量增加 = 资金流入，看涨信号"
    elif price_change > 0 and oi_change < 0:
        relationship = "价格上涨 + 持仓量减少 = 获利了结，可能见顶"
    elif price_change < 0 and oi_change < 0:
        relationship = "价格下跌 + 持仓量减少 = 止损离场，看跌信号"
    elif price_change < 0 and oi_change > 0:
        relationship = "价格下跌 + 持仓量增加 = 资金抄底，可能见底"
    else:
        relationship = "价格与持仓量变化不明显"
    
    return {
        'price_change_pct': float(price_change),
        'oi_change_pct': float(oi_change),
        'relationship': relationship
    }


def _generate_fundamental_summary(analysis_result: dict) -> str:
    """生成基本面分析总结"""
    summary_parts = []
    
    if 'open_interest' in analysis_result:
        oi = analysis_result['open_interest']
        summary_parts.append(f"持仓量趋势：{oi.get('analysis', '')}")
    
    if 'volume' in analysis_result:
        vol = analysis_result['volume']
        summary_parts.append(f"成交量：{vol.get('analysis', '')}")
    
    if 'price_oi_relationship' in analysis_result:
        poi = analysis_result['price_oi_relationship']
        summary_parts.append(f"价量关系：{poi.get('relationship', '')}")
    
    if not summary_parts:
        return "基本面数据不足，无法进行详细分析"
    
    return "；".join(summary_parts)

