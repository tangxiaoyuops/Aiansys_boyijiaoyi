"""
股票池扫描分析服务
定时扫描股票池，识别买卖点信号
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass, field, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from core.tools.data_fetcher import fetch_stock_data, get_stock_name
from core.tools.technical_analyzer import (
    detect_panic_points,
    detect_sell_signals,
    identify_stage_indicators
)

logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """交易信号"""
    code: str
    name: str
    signal_type: str  # "buy" | "sell"
    signal_date: str
    price: float
    confidence: float
    reasoning: str
    stage: int
    stage_name: str
    drop_pct: Optional[float] = None
    vol_ratio: Optional[float] = None
    gain_pct: Optional[float] = None
    suggested_action: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    """扫描结果"""
    scan_time: str
    total_stocks: int
    scanned_stocks: int
    signals: List[TradingSignal] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_time": self.scan_time,
            "total_stocks": self.total_stocks,
            "scanned_stocks": self.scanned_stocks,
            "signals": [s.to_dict() for s in self.signals],
            "errors": self.errors
        }
    
    def get_buy_signals(self) -> List[TradingSignal]:
        """获取买入信号"""
        return [s for s in self.signals if s.signal_type == "buy"]
    
    def get_sell_signals(self) -> List[TradingSignal]:
        """获取卖出信号"""
        return [s for s in self.signals if s.signal_type == "sell"]


class PoolScanService:
    """股票池扫描服务"""
    
    def __init__(
        self,
        max_workers: int = 5,
        days: int = 250,
        recent_days: int = 5
    ):
        self.max_workers = max_workers
        self.days = days
        self.recent_days = recent_days
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def scan_single_stock(
        self,
        code: str,
        scan_date: datetime
    ) -> List[TradingSignal]:
        """
        扫描单只股票，识别买卖点信号
        
        基于现有的博弈分析逻辑：
        1. 检测恐慌点（买入信号）
        2. 检测卖点信号
        3. 识别阶段
        """
        signals = []
        
        try:
            # 获取股票数据
            df = fetch_stock_data(code, days=self.days)
            if df is None or df.empty:
                return signals
            
            # 获取股票名称
            name = get_stock_name(code)
            
            # 计算阶段指标
            stage_indicators = identify_stage_indicators(df)
            stage = self._determine_stage(df, stage_indicators)
            stage_name = self._get_stage_name(stage)
            
            # 检测恐慌点（买入信号）
            panic_points = detect_panic_points(df, window=60)
            cutoff_date = scan_date - timedelta(days=self.recent_days)
            
            for p in panic_points:
                p_date = self._parse_date(p.get("date"))
                if p_date and p_date >= cutoff_date:
                    drop_pct = float(p.get("drop_pct", 0))
                    vol_ratio = float(p.get("vol_ratio", 0))
                    
                    signals.append(TradingSignal(
                        code=code,
                        name=name,
                        signal_type="buy",
                        signal_date=p_date.strftime("%Y-%m-%d"),
                        price=float(p.get("price", 0)),
                        confidence=self._calc_buy_confidence(drop_pct, vol_ratio),
                        reasoning=p.get("description", ""),
                        stage=stage,
                        stage_name=stage_name,
                        drop_pct=drop_pct,
                        vol_ratio=vol_ratio,
                        suggested_action="考虑建仓或加仓"
                    ))
            
            # 检测卖点信号（只在一二阶段）
            if stage in [1, 2]:
                sell_signals = detect_sell_signals(df, window=60, stage=stage)
                for s in sell_signals:
                    s_date = self._parse_date(s.get("date"))
                    if s_date and s_date >= cutoff_date:
                        gain_pct = float(s.get("gain_pct", 0))
                        vol_ratio = float(s.get("vol_ratio", 0))
                        
                        signals.append(TradingSignal(
                            code=code,
                            name=name,
                            signal_type="sell",
                            signal_date=s_date.strftime("%Y-%m-%d"),
                            price=float(s.get("price", 0)),
                            confidence=self._calc_sell_confidence(gain_pct, vol_ratio),
                            reasoning=s.get("description", ""),
                            stage=stage,
                            stage_name=stage_name,
                            gain_pct=gain_pct,
                            vol_ratio=vol_ratio,
                            suggested_action="考虑适当减仓"
                        ))
            
        except Exception as e:
            logger.error(f"[PoolScanService] 扫描 {code} 失败: {e}")
        
        return signals
    
    async def scan_pool(
        self,
        codes: List[str],
        progress_callback: Optional[Callable] = None
    ) -> ScanResult:
        """
        扫描整个股票池
        
        Args:
            codes: 股票代码列表
            progress_callback: 进度回调函数 async (current, total, code, signals_count)
        """
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scan_date = datetime.now()
        
        all_signals: List[TradingSignal] = []
        errors: List[Dict[str, str]] = []
        scanned = 0
        
        loop = asyncio.get_event_loop()
        
        for idx, code in enumerate(codes):
            try:
                # 使用线程池执行扫描
                signals = await loop.run_in_executor(
                    self.executor,
                    self.scan_single_stock,
                    code,
                    scan_date
                )
                all_signals.extend(signals)
                scanned += 1
                
                # 进度回调
                if progress_callback:
                    await progress_callback(
                        current=idx + 1,
                        total=len(codes),
                        code=code,
                        signals_count=len(signals)
                    )
                    
            except Exception as e:
                errors.append({"code": code, "error": str(e)})
                logger.error(f"[PoolScanService] 扫描 {code} 异常: {e}")
        
        # 按置信度排序
        all_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(
            f"[PoolScanService] 扫描完成: 共{len(codes)}只股票, "
            f"发现{len(all_signals)}个信号, {len(errors)}个错误"
        )
        
        return ScanResult(
            scan_time=scan_time,
            total_stocks=len(codes),
            scanned_stocks=scanned,
            signals=all_signals,
            errors=errors
        )
    
    def scan_pool_sync(self, codes: List[str]) -> ScanResult:
        """同步版本的扫描方法"""
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scan_date = datetime.now()
        
        all_signals: List[TradingSignal] = []
        errors: List[Dict[str, str]] = []
        scanned = 0
        
        for idx, code in enumerate(codes):
            try:
                signals = self.scan_single_stock(code, scan_date)
                all_signals.extend(signals)
                scanned += 1
                
                if (idx + 1) % 10 == 0:
                    logger.info(f"[PoolScanService] 进度: {idx + 1}/{len(codes)}")
                    
            except Exception as e:
                errors.append({"code": code, "error": str(e)})
        
        all_signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return ScanResult(
            scan_time=scan_time,
            total_stocks=len(codes),
            scanned_stocks=scanned,
            signals=all_signals,
            errors=errors
        )
    
    def _determine_stage(self, df: pd.DataFrame, indicators: Dict) -> int:
        """判断股票所处阶段"""
        current_price = indicators.get("current_price", 0)
        ma20 = indicators.get("ma20", 0)
        ma60 = indicators.get("ma60", 0)
        recent_gain_20d = indicators.get("recent_gain_20d", 0)
        
        # 简化版阶段判断
        if ma60 and current_price:
            over_ma60_pct = (current_price - ma60) / ma60 * 100
            
            # 距离60日线涨幅超过80%，可能是三阶段高位
            if over_ma60_pct > 80:
                return 3
            # 距离60日线涨幅50%-80%，可能是二阶段后期
            elif over_ma60_pct > 50:
                return 2
            # 在60日线下方
            elif over_ma60_pct < -20:
                return 5
        
        # 基于20日涨幅判断
        if recent_gain_20d < -15:
            return 5  # 五阶段：深度下跌
        elif recent_gain_20d < -5:
            return 4  # 四阶段：下跌
        elif indicators.get("price_above_ma20", False):
            return 1  # 一阶段：底部区域
        elif indicators.get("price_above_ma60", False):
            return 2  # 二阶段：上涨趋势
        
        return 4  # 默认四阶段
    
    def _get_stage_name(self, stage: int) -> str:
        """获取阶段名称"""
        names = {
            1: "一阶段（吸筹）",
            2: "二阶段（拉升）",
            3: "三阶段（出货）",
            4: "四阶段（下跌）",
            5: "五阶段（阴跌）"
        }
        return names.get(stage, "未知")
    
    def _parse_date(self, date_val) -> Optional[datetime]:
        """解析日期"""
        if date_val is None:
            return None
        try:
            if isinstance(date_val, datetime):
                return date_val
            if isinstance(date_val, str):
                return pd.to_datetime(date_val)
            return pd.to_datetime(date_val)
        except Exception:
            return None
    
    def _calc_buy_confidence(self, drop_pct: float, vol_ratio: float) -> float:
        """计算买入信号置信度"""
        # 跌幅越大（绝对值），放量越大，置信度越高
        drop_score = min(abs(drop_pct) / 10, 1.0)  # 跌幅评分，最大1.0
        vol_score = min(vol_ratio / 3, 1.0)  # 放量评分，最大1.0
        return round(drop_score * 0.6 + vol_score * 0.4, 2)
    
    def _calc_sell_confidence(self, gain_pct: float, vol_ratio: float) -> float:
        """计算卖出信号置信度"""
        # 涨幅越大，放量越大，置信度越高
        gain_score = min(gain_pct / 8, 1.0)
        vol_score = min(vol_ratio / 3, 1.0)
        return round(gain_score * 0.5 + vol_score * 0.5, 2)
    
    def __del__(self):
        """清理线程池"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)
