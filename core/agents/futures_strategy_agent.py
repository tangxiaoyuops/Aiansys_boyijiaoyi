"""
期货策略推荐Agent
综合所有分析结果，生成交易策略
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.risk_calculator import calculate_position_size
from typing import Dict, Any


def futures_strategy_recommendation_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货策略推荐节点"""
    futures_code = state.get('futures_code', '')
    game_theory_result = state.get('game_theory_result', {})
    risk_analysis_result = state.get('risk_analysis_result', {})
    spread_analysis_result = state.get('spread_analysis_result', {})
    fundamental_analysis_result = state.get('fundamental_analysis_result', {})
    
    print(f"[期货策略推荐] 开始生成策略: {futures_code}")
    print(f"[期货策略推荐] 综合以下分析结果:")
    print(f"  - 博弈分析: {'有' if game_theory_result and not game_theory_result.get('error') else '无/错误'}")
    print(f"  - 风险分析: {'有' if risk_analysis_result and not risk_analysis_result.get('error') else '无/错误'}")
    print(f"  - 价差分析: {'有' if spread_analysis_result and not spread_analysis_result.get('error') else '无/错误'}")
    print(f"  - 基本面分析: {'有' if fundamental_analysis_result and not fundamental_analysis_result.get('error') else '无/错误'}")
    
    try:
        # 综合所有分析结果
        strategy = {
            'operation': '观望',  # 买入/卖出/持有/观望
            'reason': '',
            'position_suggestion': '0%',
            'stop_loss': None,
            'take_profit': None,
            'risk_level': 'medium',
            'strategy_details': [],
            'warnings': []
        }
        
        # 基于博弈分析判断操作
        if game_theory_result and not game_theory_result.get('error'):
            stage = game_theory_result.get('stage', 0)
            stage_name = game_theory_result.get('stage_name', '未知')
            print(f"[期货策略推荐] 博弈分析结果: {stage_name} (阶段{stage})")
            
            if stage == 1 or stage == 2:
                strategy['operation'] = '买入'
                strategy['reason'] = f'当前处于{stage_name}，适合建仓'
                strategy['position_suggestion'] = '20-30%'
                print(f"[期货策略推荐] 基于博弈分析，建议: 买入，仓位: 20-30%")
            elif stage == 3:
                strategy['operation'] = '谨慎买入'
                strategy['reason'] = f'当前处于{stage_name}，风险较高，建议小仓位'
                strategy['position_suggestion'] = '10-20%'
                strategy['warnings'].append('三阶段追高风险大，需要严格控制仓位和止损')
                print(f"[期货策略推荐] 基于博弈分析，建议: 谨慎买入，仓位: 10-20%")
            elif stage == 4 or stage == 5:
                strategy['operation'] = '观望'
                strategy['reason'] = f'当前处于{stage_name}，不适合建仓'
                strategy['position_suggestion'] = '0%'
                print(f"[期货策略推荐] 基于博弈分析，建议: 观望")
        
        # 基于风险管理调整策略
        if risk_analysis_result and not risk_analysis_result.get('error'):
            risk_level = risk_analysis_result.get('risk_level', 'medium')
            leverage = risk_analysis_result.get('leverage', 1.0)
            
            strategy['risk_level'] = risk_level
            print(f"[期货策略推荐] 风险等级: {risk_level}, 杠杆倍数: {leverage:.1f}倍")
            
            if risk_level == 'high':
                # 高风险时降低仓位建议
                if strategy['position_suggestion'] != '0%':
                    old_position = strategy['position_suggestion']
                    strategy['position_suggestion'] = '5-10%'
                    print(f"[期货策略推荐] 高风险调整仓位: {old_position} -> {strategy['position_suggestion']}")
                strategy['warnings'].append(f'当前杠杆倍数{leverage:.1f}倍，风险较高，建议降低仓位')
            
            # 止损建议
            recommendations = risk_analysis_result.get('recommendations', [])
            for rec in recommendations:
                if rec.get('type') == 'stop_loss':
                    strategy['stop_loss'] = {
                        'price': rec.get('price'),
                        'percentage': rec.get('percentage'),
                        'reason': rec.get('reason')
                    }
                    print(f"[期货策略推荐] 止损建议: 价格={rec.get('price', 0):.2f}, 幅度={abs(rec.get('percentage', 0)):.2f}%")
        
        # 基于价差分析添加套利策略
        if spread_analysis_result and not spread_analysis_result.get('error'):
            arbitrage_opportunities = spread_analysis_result.get('arbitrage_opportunities', [])
            if arbitrage_opportunities:
                print(f"[期货策略推荐] 发现 {len(arbitrage_opportunities)} 个套利机会")
                strategy['strategy_details'].append('发现套利机会，可以考虑套利策略')
                for opp in arbitrage_opportunities:
                    strategy['strategy_details'].append(f"- {opp.get('description', '')}")
        
        # 基于基本面分析调整策略
        if fundamental_analysis_result and not fundamental_analysis_result.get('error'):
            price_oi = fundamental_analysis_result.get('price_oi_relationship', {})
            relationship = price_oi.get('relationship', '')
            
            if '看涨信号' in relationship:
                if strategy['operation'] == '观望':
                    strategy['operation'] = '买入'
                    strategy['reason'] += '；基本面显示看涨信号'
                    print(f"[期货策略推荐] 基本面看涨信号，调整操作: 观望 -> 买入")
            elif '看跌信号' in relationship:
                if strategy['operation'] == '买入':
                    strategy['operation'] = '观望'
                    strategy['reason'] += '；基本面显示看跌信号'
                    print(f"[期货策略推荐] 基本面看跌信号，调整操作: 买入 -> 观望")
        
        # 生成策略详情
        if not strategy['strategy_details']:
            strategy['strategy_details'] = [
                '严格执行止损，控制单笔交易风险',
                '根据市场变化及时调整仓位',
                '关注持仓量变化，判断资金流向'
            ]
        
        state['strategy_recommendation'] = strategy
        print(f"[期货策略推荐] 策略生成完成:")
        print(f"  - 操作建议: {strategy['operation']}")
        print(f"  - 仓位建议: {strategy['position_suggestion']}")
        print(f"  - 风险等级: {strategy['risk_level']}")
        print(f"  - 警告数量: {len(strategy['warnings'])}")
        print(f"  - 策略详情数量: {len(strategy['strategy_details'])}")
        
    except Exception as e:
        print(f"[期货策略推荐] 生成策略失败: {e}")
        import traceback
        print(f"[期货策略推荐] 错误堆栈: {traceback.format_exc()}")
        state['strategy_recommendation'] = {
            'error': f'生成策略失败: {str(e)}'
        }
    
    return state

