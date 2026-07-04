"""
选股策略核心模块 - 重构版
复用已有的GameTheoryStrategy，实现股票池扫描选股
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.strategy.templates.game_theory import GameTheoryStrategy
from core.backtest.portfolio import Portfolio

logger = logging.getLogger(__name__)


@dataclass
class StockCandidate:
    """股票候选"""
    code: str
    name: str
    buy_signals: List[Dict[str, Any]]  # 买入信号列表
    best_signal: Dict[str, Any]  # 最佳买入信号
    overall_score: float  # 综合评分
    stage: int
    stage_name: str
    current_price: float
    
    # 仓位建议
    suggested_position_pct: float
    suggested_shares: int
    suggested_amount: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "buy_signals": self.buy_signals,
            "best_signal": self.best_signal,
            "overall_score": self.overall_score,
            "stage": self.stage,
            "stage_name": self.stage_name,
            "current_price": self.current_price,
            "suggested_position_pct": self.suggested_position_pct,
            "suggested_shares": self.suggested_shares,
            "suggested_amount": self.suggested_amount
        }


@dataclass
class SelectionResult:
    """选股结果"""
    scan_time: str
    total_candidates: int
    qualified_candidates: int
    top_candidates: List[StockCandidate]
    all_candidates: List[StockCandidate]
    errors: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_time": self.scan_time,
            "total_candidates": self.total_candidates,
            "qualified_candidates": self.qualified_candidates,
            "top_candidates": [c.to_dict() for c in self.top_candidates],
            "all_candidates": [c.to_dict() for c in self.all_candidates],
            "errors": self.errors
        }


class StockSelectionStrategy:
    """选股策略核心 - 复用GameTheoryStrategy"""
    
    def __init__(self, strategy_params: Optional[Dict[str, Any]] = None):
        """
        初始化选股策略
        
        Args:
            strategy_params: 博弈交易策略参数
        """
        self.strategy_params = strategy_params or {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # 创建博弈交易策略实例
        self.game_strategy = GameTheoryStrategy()
        self.game_strategy.initialize(self.strategy_params)
    
    async def select_stocks(
        self,
        codes: List[str],
        progress_callback: Optional[callable] = None
    ) -> SelectionResult:
        """异步选股"""
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        all_candidates: List[StockCandidate] = []
        errors: List[Dict[str, str]] = []
        
        loop = asyncio.get_event_loop()
        
        for idx, code in enumerate(codes):
            try:
                candidate = await loop.run_in_executor(
                    self.executor,
                    self._select_single_stock,
                    code
                )
                
                if candidate:
                    all_candidates.append(candidate)
                
                if progress_callback:
                    await progress_callback(
                        current=idx + 1,
                        total=len(codes),
                        code=code,
                        found=candidate is not None
                    )
                
            except Exception as e:
                errors.append({"code": code, "error": str(e)})
                logger.error(f"[StockSelectionStrategy] 选股 {code} 异常: {e}")
        
        # 过滤和排序
        qualified_candidates = [
            c for c in all_candidates 
            if c.buy_signals and len(c.buy_signals) > 0
        ]
        
        # 按综合评分排序
        qualified_candidates.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 获取顶级候选
        max_stocks = self.strategy_params.get('max_stocks', 10)
        top_candidates = qualified_candidates[:max_stocks]
        
        # 计算仓位分配
        self._allocate_positions(top_candidates)
        
        logger.info(
            f"[StockSelectionStrategy] 选股完成: "
            f"候选{len(all_candidates)}只, "
            f"合格{len(qualified_candidates)}只, "
            f"推荐{len(top_candidates)}只"
        )
        
        return SelectionResult(
            scan_time=scan_time,
            total_candidates=len(all_candidates),
            qualified_candidates=len(qualified_candidates),
            top_candidates=top_candidates,
            all_candidates=all_candidates,
            errors=errors
        )
    
    def select_stocks_sync(self, codes: List[str]) -> SelectionResult:
        """同步选股"""
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        all_candidates: List[StockCandidate] = []
        errors: List[Dict[str, str]] = []
        
        for idx, code in enumerate(codes):
            try:
                candidate = self._select_single_stock(code)
                if candidate:
                    all_candidates.append(candidate)
                
                if (idx + 1) % 10 == 0:
                    logger.info(f"[StockSelectionStrategy] 进度: {idx + 1}/{len(codes)}")
                
            except Exception as e:
                errors.append({"code": code, "error": str(e)})
        
        qualified_candidates = [
            c for c in all_candidates 
            if c.buy_signals and len(c.buy_signals) > 0
        ]
        
        qualified_candidates.sort(key=lambda x: x.overall_score, reverse=True)
        
        max_stocks = self.strategy_params.get('max_stocks', 10)
        top_candidates = qualified_candidates[:max_stocks]
        
        self._allocate_positions(top_candidates)
        
        return SelectionResult(
            scan_time=scan_time,
            total_candidates=len(all_candidates),
            qualified_candidates=len(qualified_candidates),
            top_candidates=top_candidates,
            all_candidates=all_candidates,
            errors=errors
        )
    
    def _select_single_stock(self, code: str) -> Optional[StockCandidate]:
        """对单只股票进行选股分析 - 使用GameTheoryStrategy"""
        try:
            from core.tools.data_fetcher import fetch_stock_data, get_stock_name
            
            # 获取数据
            days = self.strategy_params.get('data_days', 250)
            df = fetch_stock_data(code, days=days)
            
            if df is None or len(df) < 120:
                logger.warning(f"[StockSelectionStrategy] {code} 数据不足")
                return None
            
            name = get_stock_name(code)
            
            # 创建模拟的组合对象（用于策略信号生成）
            portfolio = Portfolio(initial_capital=self.strategy_params.get('initial_capital', 1000000))
            
            # 使用博弈交易策略生成信号
            buy_signals = []
            current_stage = 0
            stage_name = "未知"
            
            # 遍历历史数据，找出所有买入信号
            for i in range(120, len(df)):
                historical_data = df.iloc[:i+1].copy()
                
                # 生成信号
                signal = self.game_strategy.generate_signal(historical_data, portfolio)
                
                if signal and signal.get('action') in ['OPEN_LONG', 'OPEN_SHORT']:
                    # 记录买入信号
                    buy_signals.append({
                        'date': str(df.iloc[i]['日期'])[:10] if '日期' in df.columns else str(i),
                        'price': float(df.iloc[i]['收盘']) if '收盘' in df.columns else 0,
                        'action': signal['action'],
                        'reason': signal.get('reason', ''),
                        'size': signal.get('size', 100)
                    })
            
            # 判断当前阶段
            current_stage = self.game_strategy._detect_stage_simple(df)
            stage_name = self._get_stage_name(current_stage)
            
            # 当前价格
            current_price = float(df.iloc[-1]['收盘']) if '收盘' in df.columns else 0
            
            # 如果没有买入信号，返回None
            if not buy_signals:
                return None
            
            # 找到最佳买入信号（最近的一个）
            best_signal = buy_signals[-1] if buy_signals else None
            
            # 计算综合评分
            overall_score = self._calculate_score(current_stage, len(buy_signals), current_price, df)
            
            return StockCandidate(
                code=code,
                name=name,
                buy_signals=buy_signals,
                best_signal=best_signal,
                overall_score=overall_score,
                stage=current_stage,
                stage_name=stage_name,
                current_price=current_price,
                suggested_position_pct=0.0,
                suggested_shares=0,
                suggested_amount=0.0
            )
            
        except Exception as e:
            logger.error(f"[StockSelectionStrategy] 分析 {code} 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_stage_name(self, stage: int) -> str:
        """获取阶段名称"""
        names = {
            1: "一阶段(趋势形成)",
            2: "二阶段(快速上涨)",
            3: "三阶段(疯狂阶段)",
            4: "四阶段(猛烈下跌)",
            5: "五阶段(漫长阴跌)"
        }
        return names.get(stage, "未知阶段")
    
    def _calculate_score(self, stage: int, signal_count: int, price: float, df: pd.DataFrame) -> float:
        """计算综合评分"""
        # 阶段评分
        stage_scores = {1: 90, 2: 100, 5: 60, 0: 30, 3: 10, 4: 0}
        stage_score = stage_scores.get(stage, 0)
        
        # 信号数量评分（信号越多越好）
        signal_score = min(signal_count * 10, 30)
        
        # 趋势强度评分
        if len(df) >= 60:
            ma60 = df['收盘'].rolling(window=60).mean().iloc[-1]
            if ma60 > 0:
                trend_strength = (price - ma60) / ma60 * 100
                trend_score = min(max(trend_strength, 0), 20)
            else:
                trend_score = 0
        else:
            trend_score = 0
        
        return stage_score + signal_score + trend_score
    
    def _allocate_positions(self, candidates: List[StockCandidate]) -> None:
        """分配仓位"""
        if not candidates:
            return
        
        initial_capital = self.strategy_params.get('initial_capital', 1000000)
        max_position_per_stock = self.strategy_params.get('max_position_per_stock', 0.2)
        
        # 计算总评分
        total_score = sum(c.overall_score for c in candidates)
        
        if total_score == 0:
            equal_position = max_position_per_stock
            for candidate in candidates:
                candidate.suggested_position_pct = equal_position
        else:
            for candidate in candidates:
                score_ratio = candidate.overall_score / total_score
                position_pct = score_ratio * len(candidates) * max_position_per_stock
                position_pct = min(position_pct, max_position_per_stock)
                candidate.suggested_position_pct = position_pct
        
        # 计算具体买入股数和金额
        for candidate in candidates:
            suggested_amount = initial_capital * candidate.suggested_position_pct
            suggested_shares = int(suggested_amount / candidate.current_price)
            suggested_shares = (suggested_shares // 100) * 100
            suggested_shares = max(suggested_shares, 100)
            
            candidate.suggested_shares = suggested_shares
            candidate.suggested_amount = suggested_shares * candidate.current_price
    
    def __del__(self):
        """清理线程池"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)
