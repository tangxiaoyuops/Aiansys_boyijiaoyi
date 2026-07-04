"""
选股策略API路由
提供选股、回测、报告等接口
复用已有的GameTheoryStrategy
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/selection", tags=["选股策略"])


# === 请求模型 ===
class SelectionRequest(BaseModel):
    """选股请求"""
    codes: List[str]  # 股票代码列表
    strategy_params: Optional[Dict[str, Any]] = None  # 博弈策略参数


class BacktestRequest(BaseModel):
    """回测请求"""
    codes: List[str]
    start_date: str
    end_date: str
    rebalance_freq: str = "weekly"
    strategy_params: Optional[Dict[str, Any]] = None


class SingleStockRequest(BaseModel):
    """单只股票分析请求"""
    code: str
    days: int = 250


# === 响应模型 ===
class SelectionResponse(BaseModel):
    """选股响应"""
    success: bool
    message: str
    scan_time: str
    total_candidates: int
    qualified_candidates: int
    top_candidates: List[Dict[str, Any]]
    errors: List[Dict[str, str]]


class BacktestResponse(BaseModel):
    """回测响应"""
    success: bool
    message: str
    performance: Dict[str, Any]
    trades: List[Dict[str, Any]]


class AnalysisResponse(BaseModel):
    """分析响应"""
    success: bool
    code: str
    name: str
    buy_signals: List[Dict[str, Any]]
    stage: int
    stage_name: str
    kline_data: Optional[List[Dict[str, Any]]] = None


# === API接口 ===
@router.post("/select", response_model=SelectionResponse)
async def select_stocks(request: SelectionRequest):
    """
    执行选股 - 使用GameTheoryStrategy
    
    Args:
        request: 选股请求参数
    
    Returns:
        选股结果
    """
    try:
        from core.selection import StockSelectionStrategy
        
        logger.info(f"[选股API] 开始选股: {len(request.codes)}只股票")
        
        # 提取策略参数
        strategy_params = request.strategy_params or {}
        
        # 添加默认参数
        default_params = {
            'max_stocks': 10,
            'max_position_per_stock': 0.2,
            'initial_capital': 1000000,
            'data_days': 250,
            # 博弈策略参数
            'panic_drop_threshold': -3.0,
            'panic_vol_ratio': 1.5,
            'panic_window': 60,
            'stage_window': 60,
        }
        
        # 合并参数（用户参数优先）
        for key, value in default_params.items():
            if key not in strategy_params:
                strategy_params[key] = value
        
        # 创建选股策略（内部使用GameTheoryStrategy）
        strategy = StockSelectionStrategy(strategy_params)
        
        # 执行选股
        result = strategy.select_stocks_sync(request.codes)
        
        logger.info(f"[选股API] 选股完成: 合格{result.qualified_candidates}只, 推荐{len(result.top_candidates)}只")
        
        return SelectionResponse(
            success=True,
            message="选股完成",
            scan_time=result.scan_time,
            total_candidates=result.total_candidates,
            qualified_candidates=result.qualified_candidates,
            top_candidates=[c.to_dict() for c in result.top_candidates],
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"[选股API] 选股失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    运行回测 - 使用GameTheoryStrategy
    
    Args:
        request: 回测请求参数
    
    Returns:
        回测结果
    """
    try:
        from core.selection import SelectionBacktester
        
        logger.info(f"[回测API] 开始回测: {request.start_date} 至 {request.end_date}")
        
        strategy_params = request.strategy_params or {}
        
        # 创建回测器
        backtester = SelectionBacktester(strategy_params)
        
        # 运行回测
        result = backtester.run_backtest(
            codes=request.codes,
            start_date=request.start_date,
            end_date=request.end_date,
            rebalance_freq=request.rebalance_freq
        )
        
        logger.info(f"[回测API] 回测完成: 收益率{result.performance.total_return:.2f}%")
        
        return BacktestResponse(
            success=True,
            message="回测完成",
            performance=result.performance.to_dict(),
            trades=[t.to_dict() for t in result.trades]
        )
        
    except Exception as e:
        logger.error(f"[回测API] 回测失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_single_stock(request: SingleStockRequest):
    """
    分析单只股票 - 使用GameTheoryStrategy
    
    Args:
        request: 单只股票分析请求
    
    Returns:
        分析结果(包含K线数据)
    """
    try:
        from core.strategy.templates.game_theory import GameTheoryStrategy
        from core.backtest.portfolio import Portfolio
        from core.tools.data_fetcher import fetch_stock_data, get_stock_name
        
        logger.info(f"[分析API] 分析股票: {request.code}")
        
        # 获取数据
        df = fetch_stock_data(request.code, days=request.days)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="无法获取股票数据")
        
        # 获取股票名称
        name = get_stock_name(request.code)
        
        # 创建博弈策略实例
        strategy = GameTheoryStrategy()
        strategy.initialize({})
        
        # 创建模拟组合
        portfolio = Portfolio(initial_capital=1000000)
        
        # 收集买入信号
        buy_signals = []
        
        # 遍历历史数据，找出所有买入信号
        for i in range(120, len(df)):
            historical_data = df.iloc[:i+1].copy()
            signal = strategy.generate_signal(historical_data, portfolio)
            
            if signal and signal.get('action') in ['OPEN_LONG', 'OPEN_SHORT']:
                buy_signals.append({
                    'buy_type': 'panic_point' if '恐慌' in signal.get('reason', '') else 'buy_signal',
                    'date': str(df.iloc[i]['日期'])[:10] if '日期' in df.columns else str(i),
                    'price': float(df.iloc[i]['收盘']) if '收盘' in df.columns else 0,
                    'score': 75.0,
                    'confidence': 0.7,
                    'reasoning': signal.get('reason', '')
                })
        
        # 判断阶段
        stage = strategy._detect_stage_simple(df)
        stage_name = {
            1: "一阶段(趋势形成)",
            2: "二阶段(快速上涨)",
            3: "三阶段(疯狂阶段)",
            4: "四阶段(猛烈下跌)",
            5: "五阶段(漫长阴跌)"
        }.get(stage, "未知阶段")
        
        # 准备K线数据
        kline_data = []
        for idx, row in df.iterrows():
            kline_data.append({
                "date": str(row['日期'])[:10] if '日期' in row else str(idx),
                "open": float(row['开盘']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "close": float(row['收盘']),
                "volume": float(row['成交量']) if '成交量' in row else 0
            })
        
        logger.info(f"[分析API] 分析完成: 检测到{len(buy_signals)}个买点, K线数据{len(kline_data)}条")
        
        return AnalysisResponse(
            success=True,
            code=request.code,
            name=name,
            buy_signals=buy_signals,
            stage=stage,
            stage_name=stage_name,
            kline_data=kline_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[分析API] 分析失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/default")
async def get_default_config():
    """获取默认配置"""
    return {
        "success": True,
        "config": {
            "max_stocks": 10,
            "max_position_per_stock": 0.2,
            "initial_capital": 1000000,
            "data_days": 250,
            "panic_drop_threshold": -3.0,
            "panic_vol_ratio": 1.5,
            "panic_window": 60,
            "stage_window": 60
        }
    }


@router.get("/config/types")
async def get_config_types():
    """获取可用的配置类型"""
    return {
        "success": True,
        "types": [
            {
                "name": "standard",
                "label": "标准配置",
                "description": "平衡风险和收益",
                "params": {
                    "max_stocks": 10,
                    "max_position_per_stock": 0.2
                }
            },
            {
                "name": "conservative",
                "label": "保守型配置",
                "description": "更低风险,更少持仓",
                "params": {
                    "max_stocks": 5,
                    "max_position_per_stock": 0.15
                }
            },
            {
                "name": "aggressive",
                "label": "激进型配置",
                "description": "更高风险,更多持仓",
                "params": {
                    "max_stocks": 15,
                    "max_position_per_stock": 0.25
                }
            }
        ]
    }


@router.post("/report/save")
async def save_selection_report(request: SelectionRequest):
    """
    生成并保存选股报告
    
    Args:
        request: 选股请求参数
    
    Returns:
        报告保存路径
    """
    try:
        from core.selection import StockSelectionStrategy, SelectionReporter
        
        logger.info(f"[报告API] 生成选股报告")
        
        strategy_params = request.strategy_params or {}
        strategy_params.setdefault('max_stocks', 10)
        
        # 执行选股
        strategy = StockSelectionStrategy(strategy_params)
        result = strategy.select_stocks_sync(request.codes)
        
        # 生成报告
        reporter = SelectionReporter()
        report = reporter.generate_selection_report(result, "markdown")
        
        # 保存报告
        import os
        os.makedirs("output", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"output/selection_report_{timestamp}.md"
        
        reporter.save_report(report, filepath)
        
        logger.info(f"[报告API] 报告已保存: {filepath}")
        
        return {
            "success": True,
            "message": "报告已保存",
            "filepath": filepath
        }
        
    except Exception as e:
        logger.error(f"[报告API] 保存报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
