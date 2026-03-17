"""
大宗商品策略回测Agent
对生成的策略进行历史回测
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.backtest_engine import create_backtest_engine


def strategy_backtest_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    策略回测节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[策略回测] 开始策略回测")
    
    strategy_signals = state.get("strategy_signals", [])
    raw_evidence = state.get("raw_evidence")
    enable_backtest = state.get("enable_backtest", True)
    
    if not enable_backtest:
        print("[策略回测] 回测已禁用")
        state["backtest_results"] = []
        return state
    
    if not strategy_signals:
        print("[策略回测] 没有策略信号，跳过回测")
        state["backtest_results"] = []
        return state
    
    if not raw_evidence or not raw_evidence.get("prices"):
        print("[策略回测] 警告: 没有价格数据")
        state["backtest_results"] = []
        return state
    
    prices = raw_evidence.get("prices", [])
    
    if len(prices) < 60:
        print(f"[策略回测] 警告: 价格数据不足（{len(prices)}条），需要至少60条")
        state["backtest_results"] = []
        return state
    
    try:
        engine = create_backtest_engine(
            initial_capital=1000000.0,
            commission_rate=0.0001
        )
        
        price_data = []
        for p in prices:
            price_data.append({
                "date": p["as_of_date"],
                "close": p["value"],
                "high": p.get("high", p["value"]),
                "low": p.get("low", p["value"])
            })
        
        backtest_results = []
        
        for strategy in strategy_signals:
            try:
                result = engine.backtest(
                    strategy_signals=[strategy],
                    price_data=price_data
                )
                result["strategy_id"] = f"{strategy.get('commodity_id')}_{strategy.get('direction')}_{strategy.get('generated_at')}"
                backtest_results.append(result)
                
                print(f"[策略回测] 策略回测完成")
                print(f"[策略回测] 总收益率: {result['total_return']:.2f}%")
                print(f"[策略回测] 夏普比率: {result['sharpe_ratio']:.2f}")
                print(f"[策略回测] 最大回撤: {result['max_drawdown']:.2f}%")
                print(f"[策略回测] 胜率: {result['win_rate']:.2f}%")
                
            except Exception as e:
                print(f"[策略回测] 策略回测失败: {str(e)}")
                continue
        
        state["backtest_results"] = backtest_results
        
        print(f"[策略回测] 所有策略回测完成，共 {len(backtest_results)} 个结果")
        
    except Exception as e:
        error_msg = f"策略回测失败: {str(e)}"
        print(f"[策略回测] {error_msg}")
        state["backtest_results"] = []
    
    return state
