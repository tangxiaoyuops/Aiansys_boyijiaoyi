"""
大宗商品分析API路由
提供大宗商品分析、策略生成、回测等接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from core.graph.commodity_analysis_graph import run_commodity_analysis

router = APIRouter(prefix="/api/commodity", tags=["大宗商品分析"])


class AnalyzeRequest(BaseModel):
    """分析请求"""
    commodity_or_chain: str
    time_range: Optional[Dict[str, str]] = None
    user_question: Optional[str] = None
    strategy_type: Optional[str] = "trend"
    enable_backtest: Optional[bool] = True
    max_rounds: Optional[int] = 2


class StrategyRequest(BaseModel):
    """策略生成请求"""
    commodity: str
    strategy_type: str
    parameters: Optional[Dict[str, Any]] = None
    time_range: Optional[Dict[str, str]] = None


class BacktestRequest(BaseModel):
    """回测请求"""
    strategy_id: str
    start_date: str
    end_date: str
    initial_capital: Optional[float] = 1000000.0
    commission: Optional[float] = 0.0001


@router.post("/analyze")
async def analyze_commodity(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    大宗商品综合分析
    
    Args:
        request: 分析请求
    
    Returns:
        分析结果
    """
    try:
        print(f"[API] 收到大宗商品分析请求: {request.commodity_or_chain}")
        
        result = run_commodity_analysis(
            commodity_or_chain=request.commodity_or_chain,
            time_range=request.time_range,
            user_question=request.user_question,
            strategy_type=request.strategy_type,
            max_rounds=request.max_rounds,
            enable_backtest=request.enable_backtest
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "分析完成",
                "data": result["data"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "分析失败")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"分析执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post("/strategy")
async def generate_strategy(request: StrategyRequest) -> Dict[str, Any]:
    """
    生成买卖策略
    
    Args:
        request: 策略请求
    
    Returns:
        策略信号
    """
    try:
        print(f"[API] 收到策略生成请求: {request.commodity}")
        
        result = run_commodity_analysis(
            commodity_or_chain=request.commodity,
            time_range=request.time_range,
            strategy_type=request.strategy_type,
            max_rounds=1,
            enable_backtest=False
        )
        
        if result["success"]:
            data = result["data"]
            return {
                "success": True,
                "message": "策略生成完成",
                "data": {
                    "strategies": data.get("strategies", []),
                    "technical_indicators": data.get("structured", {}).get("technical_indicators", {}),
                    "market_state": data.get("structured", {}).get("market_state", "unknown")
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "策略生成失败")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"策略生成异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post("/backtest")
async def backtest_strategy(request: BacktestRequest) -> Dict[str, Any]:
    """
    策略回测
    
    Args:
        request: 回测请求
    
    Returns:
        回测结果
    """
    try:
        print(f"[API] 收到策略回测请求: {request.strategy_id}")
        
        result = run_commodity_analysis(
            commodity_or_chain=request.strategy_id.split("_")[0],
            time_range={
                "start": request.start_date,
                "end": request.end_date
            },
            enable_backtest=True
        )
        
        if result["success"]:
            data = result["data"]
            backtest_results = data.get("backtest_results", [])
            
            if backtest_results:
                return {
                    "success": True,
                    "message": "回测完成",
                    "data": {
                        "backtest_result": backtest_results[0],
                        "equity_curve": backtest_results[0].get("equity_curve", []),
                        "drawdown_curve": backtest_results[0].get("drawdown_curve", []),
                        "trade_list": backtest_results[0].get("trades", [])
                    }
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail="未找到回测结果"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "回测失败")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"回测执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get("/strategies")
async def list_strategies(
    commodity: Optional[str] = None,
    strategy_type: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    获取策略列表
    
    Args:
        commodity: 品种筛选
        strategy_type: 策略类型筛选
        limit: 返回数量限制
    
    Returns:
        策略列表
    """
    try:
        print(f"[API] 收到策略列表请求")
        
        import os
        import json
        from datetime import datetime
        
        strategies_dir = "data/commodity/strategies"
        
        if not os.path.exists(strategies_dir):
            return {
                "success": True,
                "data": {
                    "strategies": [],
                    "total": 0
                }
            }
        
        strategies = []
        
        for filename in os.listdir(strategies_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(strategies_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    strategy_data = json.load(f)
                    
                    if commodity and commodity not in strategy_data.get("commodity_id", ""):
                        continue
                    
                    if strategy_type and strategy_type != strategy_data.get("strategy_type", ""):
                        continue
                    
                    strategies.append(strategy_data)
                    
                    if len(strategies) >= limit:
                        break
        
        return {
            "success": True,
            "data": {
                "strategies": strategies,
                "total": len(strategies)
            }
        }
        
    except Exception as e:
        error_msg = f"获取策略列表异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    健康检查
    """
    return {
        "status": "healthy",
        "service": "commodity_analysis"
    }
