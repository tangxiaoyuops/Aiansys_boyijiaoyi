"""
期货价差分析Agent
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.spread_analyzer import (
    analyze_calendar_spread,
    analyze_inter_commodity_spread,
    identify_arbitrage_opportunity
)
from core.tools.futures_data_fetcher import fetch_futures_data


def futures_spread_analysis_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货价差分析节点"""
    futures_code = state.get('futures_code', '')
    futures_data = state.get('futures_data')
    
    print(f"[期货价差分析] 开始分析: {futures_code}")
    
    if futures_data is None or futures_data.empty:
        print(f"[期货价差分析] 错误: 缺少期货数据")
        state['spread_analysis_result'] = {
            'error': '缺少期货数据，请先运行futures_data_fetch_node'
        }
        return state
    
    try:
        product_code = state.get('product_code', '')
        contract_month = state.get('contract_month', '')
        
        result = {
            'calendar_spread': None,
            'inter_commodity_spread': None,
            'arbitrage_opportunities': []
        }
        
        # 跨期价差分析（需要获取相关月份合约数据）
        if contract_month and len(contract_month) >= 4:
            try:
                # 尝试获取相邻月份合约
                year = int(contract_month[:2])
                month = int(contract_month[2:])
                
                # 计算下一个月
                next_month = month + 1
                next_year = year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                
                next_month_code = f"{product_code}{next_year:02d}{next_month:02d}"
                print(f"[期货价差分析] 准备分析跨期价差: {futures_code} vs {next_month_code}")
                
                # 尝试获取下月合约数据
                try:
                    print(f"[期货价差分析] 正在获取下月合约数据: {next_month_code}")
                    next_month_data = fetch_futures_data(next_month_code, state.get('days', 180))
                    print(f"[期货价差分析] 下月合约数据获取成功: {len(next_month_data)} 条记录")
                    
                    # 分析跨期价差
                    print(f"[期货价差分析] 正在分析跨期价差...")
                    calendar_analysis = analyze_calendar_spread(futures_data, next_month_data)
                    print(f"[期货价差分析] 当前价差: {calendar_analysis.get('current_spread', 0):.2f}, 趋势: {calendar_analysis.get('trend', 'unknown')}")
                    
                    # 识别套利机会
                    arbitrage = identify_arbitrage_opportunity(calendar_analysis)
                    if arbitrage.get('has_opportunity'):
                        print(f"[期货价差分析] 发现套利机会: {arbitrage.get('opportunity_type')}, 预期收益: {arbitrage.get('expected_profit', 0):.2f}")
                    else:
                        print(f"[期货价差分析] 未发现明显的套利机会")
                    
                    result['calendar_spread'] = {
                        'near_month': futures_code,
                        'far_month': next_month_code,
                        'analysis': calendar_analysis,
                        'arbitrage': arbitrage
                    }
                    
                    if arbitrage.get('has_opportunity'):
                        result['arbitrage_opportunities'].append({
                            'type': 'calendar',
                            'description': f'{futures_code}与{next_month_code}的跨期套利机会',
                            'opportunity': arbitrage
                        })
                except Exception as e:
                    print(f"[期货价差分析] 无法获取下月合约数据: {e}")
            except Exception as e:
                print(f"[期货价差分析] 跨期价差分析失败: {e}")
                import traceback
                print(f"[期货价差分析] 错误堆栈: {traceback.format_exc()}")
        
        # 跨品种价差分析（需要根据实际需求配置相关品种）
        # 这里暂时跳过，后续可以根据需要扩展
        
        state['spread_analysis_result'] = result
        print(f"[期货价差分析] 价差分析完成，发现 {len(result['arbitrage_opportunities'])} 个套利机会")
        
    except Exception as e:
        print(f"[期货价差分析] 分析失败: {e}")
        import traceback
        print(f"[期货价差分析] 错误堆栈: {traceback.format_exc()}")
        state['spread_analysis_result'] = {
            'error': f'分析失败: {str(e)}'
        }
    
    return state

