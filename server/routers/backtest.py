"""
回测相关API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd

from core.backtest.engine import FuturesBacktestEngine, BacktestConfig
from core.backtest.stock_engine import StockBacktestEngine, StockBacktestConfig
from core.strategy.templates import get_strategy

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.get("/strategies")
async def get_strategies():
    """获取所有可用策略列表"""
    from core.strategy.templates import STRATEGY_REGISTRY
    
    strategies = []
    for strategy_key, strategy_class in STRATEGY_REGISTRY.items():
        # 跳过中文别名，只保留英文key
        if strategy_key in ['dual_ma', 'triple_ma', 'bollinger_bands', 'rsi', 'game_theory']:
            try:
                strategy_instance = strategy_class()
                strategies.append({
                    'name': strategy_key,
                    'display_name': strategy_instance.name,
                    'description': getattr(strategy_instance, 'description', '')
                })
            except Exception as e:
                print(f"[策略API] 无法实例化策略 {strategy_key}: {e}")
                continue
    
    return {
        "success": True,
        "strategies": strategies
    }


@router.get("/strategies/{strategy_name}/params")
async def get_strategy_params(strategy_name: str):
    """获取策略参数定义"""
    from core.strategy.templates import get_strategy
    
    strategy_class = get_strategy(strategy_name)
    if strategy_class is None:
        raise HTTPException(status_code=404, detail=f"策略不存在: {strategy_name}")
    
    try:
        strategy_instance = strategy_class()
        # 获取策略的默认参数
        params = {}
        if hasattr(strategy_instance, 'get_parameters'):
            params = strategy_instance.get_parameters()
        elif hasattr(strategy_instance, '_on_initialize'):
            # 尝试从初始化方法中获取参数
            strategy_instance._on_initialize()
            # 这里可以根据策略类的属性来推断参数
            pass
        
        # 返回参数定义（这里可以根据实际策略类来动态生成）
        return {
            "success": True,
            "strategy_name": strategy_name,
            "params": params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略参数失败: {str(e)}")


class BacktestRequest(BaseModel):
    """期货回测请求"""
    futures_code: str
    strategy_name: str
    strategy_params: Dict[str, Any] = {}
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: int = 180
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    slippage: float = 0.0002
    margin_rate: float = 0.15
    contract_multiplier: int = 10
    max_position: int = 10
    max_margin_rate: float = 0.8
    stop_loss_ratio: float = 0.05
    take_profit_ratio: float = 0.10


class StockBacktestRequest(BaseModel):
    """股票回测请求"""
    stock_code: str
    strategy_name: str
    strategy_params: Dict[str, Any] = {}
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: int = 180
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    slippage: float = 0.0002
    stamp_tax_rate: float = 0.001  # 印花税（卖出时，0.1%）
    min_commission: float = 5.0  # 最小手续费（元）
    max_position: int = 10000  # 最大持仓（股数）
    stop_loss_ratio: float = 0.05
    take_profit_ratio: float = 0.10


class OptimizationRequest(BaseModel):
    """参数优化请求"""
    futures_code: str
    strategy_name: str
    param_space: Dict[str, List[Any]]
    days: int = 180
    objective: str = "sharpe_ratio"
    initial_capital: float = 100000.0
    commission_rate: float = 0.0003
    slippage: float = 0.0002
    margin_rate: float = 0.15


@router.post("/stock/run")
async def run_stock_backtest(request: StockBacktestRequest):
    """运行股票回测"""
    import traceback
    try:
        # 获取股票数据
        from core.tools.data_fetcher import fetch_stock_data
        print(f"[股票回测API] 开始获取数据: {request.stock_code}, days={request.days}")
        # fetch_stock_data 需要6位股票代码，如果用户输入的是带后缀的，需要处理
        stock_code = request.stock_code
        # 如果是类似 "000001.SZ" 这样的格式，提取前6位
        if '.' in stock_code:
            stock_code = stock_code.split('.')[0]
        # 确保是6位数字
        stock_code = stock_code.zfill(6)
        data = fetch_stock_data(stock_code, request.days)
        
        if data is None or len(data) == 0:
            raise HTTPException(status_code=400, detail="无法获取股票数据")
        
        print(f"[股票回测API] 数据获取成功: {len(data)} 条记录, 列名: {list(data.columns)}")
        
        # 创建策略实例
        strategy_class = get_strategy(request.strategy_name)
        if strategy_class is None:
            raise HTTPException(status_code=400, detail=f"未知策略: {request.strategy_name}")
        
        print(f"[股票回测API] 创建策略: {request.strategy_name}, 参数: {request.strategy_params}")
        strategy = strategy_class()
        
        # 配置股票回测引擎
        config = StockBacktestConfig(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage=request.slippage,
            stamp_tax_rate=request.stamp_tax_rate,
            min_commission=request.min_commission,
            max_position=request.max_position,
            stop_loss_ratio=request.stop_loss_ratio,
            take_profit_ratio=request.take_profit_ratio
        )
        
        print(f"[股票回测API] 创建回测引擎")
        engine = StockBacktestEngine(config)
        
        # 运行回测
        print(f"[股票回测API] 开始运行回测...")
        results = engine.run_backtest(data, strategy, request.strategy_params)
        print(f"[股票回测API] 回测完成: success={results.get('success')}")
        
        if not results.get('success'):
            error_msg = results.get('error', '回测失败')
            print(f"[股票回测API] 回测失败: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        print(f"[股票回测API] 返回结果")
        return {
            "success": True,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"[股票回测API] 发生异常: {error_msg}")
        print(f"[股票回测API] 错误堆栈:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"股票回测异常: {error_msg}\n{error_trace}")


@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """运行期货回测"""
    import traceback
    try:
        # 获取数据
        from core.tools.futures_data_fetcher import fetch_futures_data
        print(f"[回测API] 开始获取数据: {request.futures_code}, days={request.days}")
        data = fetch_futures_data(request.futures_code, request.days)
        
        if data is None or len(data) == 0:
            raise HTTPException(status_code=400, detail="无法获取期货数据")
        
        print(f"[回测API] 数据获取成功: {len(data)} 条记录, 列名: {list(data.columns)}")
        
        # 创建策略实例
        strategy_class = get_strategy(request.strategy_name)
        if strategy_class is None:
            raise HTTPException(status_code=400, detail=f"未知策略: {request.strategy_name}")
        
        print(f"[回测API] 创建策略: {request.strategy_name}, 参数: {request.strategy_params}")
        strategy = strategy_class()
        
        # 配置回测引擎
        config = BacktestConfig(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage=request.slippage,
            margin_rate=request.margin_rate,
            contract_multiplier=request.contract_multiplier,
            max_position=request.max_position,
            max_margin_rate=request.max_margin_rate,
            stop_loss_ratio=request.stop_loss_ratio,
            take_profit_ratio=request.take_profit_ratio
        )
        
        print(f"[回测API] 创建回测引擎")
        engine = FuturesBacktestEngine(config)
        
        # 运行回测
        print(f"[回测API] 开始运行回测...")
        results = engine.run_backtest(data, strategy, request.strategy_params)
        print(f"[回测API] 回测完成: success={results.get('success')}")
        
        if not results.get('success'):
            error_msg = results.get('error', '回测失败')
            print(f"[回测API] 回测失败: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        print(f"[回测API] 返回结果")
        return {
            "success": True,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"[回测API] 发生异常: {error_msg}")
        print(f"[回测API] 错误堆栈:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"回测异常: {error_msg}\n{error_trace}")


@router.post("/optimize")
async def optimize_parameters(request: OptimizationRequest):
    """优化策略参数"""
    try:
        # 获取数据
        from core.tools.futures_data_fetcher import fetch_futures_data
        data = fetch_futures_data(request.futures_code, request.days)
        
        if data is None or len(data) == 0:
            raise HTTPException(status_code=400, detail="无法获取期货数据")
        
        # 创建策略类
        strategy_class = get_strategy(request.strategy_name)
        if strategy_class is None:
            raise HTTPException(status_code=400, detail=f"未知策略: {request.strategy_name}")
        
        # 配置回测引擎
        config = BacktestConfig(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage=request.slippage,
            margin_rate=request.margin_rate
        )
        
        engine = FuturesBacktestEngine(config)
        
        # 创建优化器
        from core.backtest.optimizer.grid_search import GridSearchOptimizer
        optimizer = GridSearchOptimizer(
            engine=engine,
            strategy_class=strategy_class,
            param_space=request.param_space,
            objective=request.objective
        )
        
        # 运行优化
        optimization_results = optimizer.optimize(data)
        
        if not optimization_results.get('success'):
            raise HTTPException(status_code=500, detail=optimization_results.get('error', '优化失败'))
        
        return {
            "success": True,
            "optimization": optimization_results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_strategies(
    futures_code: str,
    strategies: List[Dict[str, Any]],
    days: int = 180
):
    """对比多个策略"""
    try:
        # 获取数据
        from core.tools.futures_data_fetcher import fetch_futures_data
        data = fetch_futures_data(futures_code, days)
        
        if data is None or len(data) == 0:
            raise HTTPException(status_code=400, detail="无法获取期货数据")
        
        results = []
        
        for strategy_config in strategies:
            strategy_name = strategy_config.get('strategy_name')
            strategy_params = strategy_config.get('strategy_params', {})
            
            # 创建策略
            strategy_class = get_strategy(strategy_name)
            if strategy_class is None:
                continue
            
            strategy = strategy_class()
            
            # 配置回测
            config = BacktestConfig()
            engine = FuturesBacktestEngine(config)
            
            # 运行回测
            result = engine.run_backtest(data, strategy, strategy_params)
            
            if result.get('success'):
                results.append({
                    'strategy_name': strategy_name,
                    'strategy_params': strategy_params,
                    'result': result
                })
        
        # 计算相关性（简化版）
        correlation_matrix = {}
        if len(results) > 1:
            # 这里可以计算策略收益的相关性
            pass
        
        return {
            "success": True,
            "results": results,
            "correlation": correlation_matrix
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

