"""
期货风险管理Agent
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.risk_calculator import (
    calculate_margin,
    calculate_leverage,
    calculate_position_risk,
    calculate_stop_loss,
    calculate_position_size
)
from core.tools.futures_analyzer import compute_futures_volatility


def futures_risk_analysis_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货风险管理分析节点"""
    futures_code = state.get('futures_code', '')
    futures_data = state.get('futures_data')
    
    print(f"[期货风险管理] 开始分析: {futures_code}")
    
    if futures_data is None or futures_data.empty:
        print(f"[期货风险管理] 错误: 缺少期货数据")
        state['risk_analysis_result'] = {
            'error': '缺少期货数据，请先运行futures_data_fetch_node'
        }
        return state
    
    try:
        current_price = float(futures_data.iloc[-1]['收盘'])
        margin_rate = state.get('margin_rate', 0.10)
        contract_multiplier = state.get('contract_multiplier', 10)
        
        print(f"[期货风险管理] 当前价格: {current_price:.2f}, 保证金率: {margin_rate:.1%}, 合约乘数: {contract_multiplier}")
        
        # 计算杠杆
        leverage = calculate_leverage(current_price, contract_multiplier, margin_rate)
        print(f"[期货风险管理] 杠杆倍数: {leverage:.1f}倍")
        
        # 计算波动率（用于风险评估）
        print(f"[期货风险管理] 正在计算波动率...")
        volatility_20 = compute_futures_volatility(futures_data, 20)
        volatility_60 = compute_futures_volatility(futures_data, 60)
        print(f"[期货风险管理] 20日波动率: {volatility_20:.2f}%, 60日波动率: {volatility_60:.2f}%")
        
        # 计算最大回撤
        from core.tools.futures_analyzer import compute_futures_max_drawdown
        max_drawdown_60 = compute_futures_max_drawdown(futures_data, 60)
        print(f"[期货风险管理] 60日最大回撤: {max_drawdown_60:.2f}%")
        
        # 风险评估
        risk_level = 'medium'
        if volatility_20 and volatility_20 > 5:
            risk_level = 'high'
        elif volatility_20 and volatility_20 < 2:
            risk_level = 'low'
        print(f"[期货风险管理] 风险等级评估: {risk_level}")
        
        # 生成风险管理建议
        print(f"[期货风险管理] 正在生成风险管理建议...")
        risk_recommendations = []
        
        # 止损建议
        if volatility_20:
            stop_loss_pct = -volatility_20 * 1.5  # 止损幅度为1.5倍波动率
            stop_loss_price = calculate_stop_loss(current_price, stop_loss_pct, 'long')
            risk_recommendations.append({
                'type': 'stop_loss',
                'price': stop_loss_price,
                'percentage': stop_loss_pct,
                'reason': f'基于20日波动率({volatility_20:.2f}%)，建议止损幅度为{abs(stop_loss_pct):.2f}%'
            })
            print(f"[期货风险管理] 止损建议: 价格={stop_loss_price:.2f}, 幅度={abs(stop_loss_pct):.2f}%")
        
        # 仓位建议
        risk_recommendations.append({
            'type': 'position',
            'suggestion': '建议单笔交易风险不超过账户资金的2-5%',
            'reason': f'当前杠杆倍数{leverage:.1f}倍，风险较高，需要严格控制仓位'
        })
        
        # 保证金使用建议
        risk_recommendations.append({
            'type': 'margin',
            'suggestion': '建议保证金使用率不超过50%',
            'reason': '保留足够的保证金缓冲，应对价格波动'
        })
        
        result = {
            'current_price': current_price,
            'leverage': float(leverage),
            'margin_rate': margin_rate,
            'contract_multiplier': contract_multiplier,
            'volatility_20': volatility_20,
            'volatility_60': volatility_60,
            'max_drawdown_60': max_drawdown_60,
            'risk_level': risk_level,
            'recommendations': risk_recommendations
        }
        
        state['risk_analysis_result'] = result
        print(f"[期货风险管理] 风险管理分析完成，共生成 {len(risk_recommendations)} 条建议")
        
    except Exception as e:
        print(f"[期货风险管理] 分析失败: {e}")
        import traceback
        print(f"[期货风险管理] 错误堆栈: {traceback.format_exc()}")
        state['risk_analysis_result'] = {
            'error': f'分析失败: {str(e)}'
        }
    
    return state

