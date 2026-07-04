"""
买点识别器
基于博弈交易理论识别买入信号
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BuyPoint:
    """买点信号"""
    code: str
    name: str
    buy_type: str  # panic_point, o_point, washout_end, lowest_after_panic
    date: str
    price: float
    stage: int
    stage_name: str
    confidence: float
    score: float  # 综合评分
    reasoning: str
    
    # 详细特征
    drop_pct: Optional[float] = None
    vol_ratio: Optional[float] = None
    trend_strength: Optional[float] = None
    emotion_score: Optional[float] = None
    washout_days: Optional[int] = None
    
    # 技术指标
    rsi: Optional[float] = None
    ma_distance: Optional[float] = None  # 距离均线距离(%)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "buy_type": self.buy_type,
            "date": self.date,
            "price": self.price,
            "stage": self.stage,
            "stage_name": self.stage_name,
            "confidence": self.confidence,
            "score": self.score,
            "reasoning": self.reasoning,
            "drop_pct": self.drop_pct,
            "vol_ratio": self.vol_ratio,
            "trend_strength": self.trend_strength,
            "emotion_score": self.emotion_score,
            "washout_days": self.washout_days,
            "rsi": self.rsi,
            "ma_distance": self.ma_distance
        }


class BuyPointDetector:
    """买点识别器"""
    
    def __init__(self, config: Any):
        """
        初始化买点识别器
        
        Args:
            config: SelectionConfig配置对象
        """
        self.config = config
    
    def detect_buy_points(
        self,
        code: str,
        data: pd.DataFrame,
        scan_date: Optional[datetime] = None
    ) -> List[BuyPoint]:
        """
        检测买点信号
        
        Args:
            code: 股票代码
            data: 股票历史数据
            scan_date: 扫描日期(默认今天)
        
        Returns:
            买点信号列表
        """
        if data is None or len(data) < self.config.min_data_days:
            logger.warning(f"[BuyPointDetector] {code} 数据不足")
            return []
        
        buy_points = []
        scan_date = scan_date or datetime.now()
        
        # 标准化数据
        df = self._normalize_data(data)
        
        # 判断阶段
        stage = self._detect_stage(df)
        stage_name = self._get_stage_name(stage)
        
        # 如果不在允许买入的阶段,直接返回
        if stage not in self.config.allowed_stages:
            return []
        
        # 1. 检测恐慌点买入
        panic_points = self._detect_panic_points(df, code, stage, stage_name)
        buy_points.extend(panic_points)
        
        # 2. 检测恐慌点后的最低价买入
        lowest_points = self._detect_lowest_after_panic(df, code, stage, stage_name, panic_points)
        buy_points.extend(lowest_points)
        
        # 3. 检测O点买入(一阶段)
        if stage == 1:
            o_points = self._detect_o_point(df, code, stage, stage_name)
            buy_points.extend(o_points)
        
        # 4. 检测洗盘结束买入(二阶段)
        if stage == 2:
            washout_points = self._detect_washout_end(df, code, stage, stage_name)
            buy_points.extend(washout_points)
        
        # 5. 过滤:只保留最近N天的买点
        recent_days = 5
        cutoff_date = scan_date - pd.Timedelta(days=recent_days)
        buy_points = [
            bp for bp in buy_points 
            if pd.to_datetime(bp.date) >= cutoff_date
        ]
        
        # 按评分排序
        buy_points.sort(key=lambda x: x.score, reverse=True)
        
        return buy_points
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化数据列名"""
        df = data.copy()
        
        # 列名映射
        column_mapping = {
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '日期': 'date'
        }
        
        # 重命名列
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]
        
        # 确保必要的列存在
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                chinese_map = {
                    'open': '开盘',
                    'close': '收盘',
                    'high': '最高',
                    'low': '最低'
                }
                if chinese_map[col] in df.columns:
                    df[col] = df[chinese_map[col]]
        
        # 如果没有volume,添加默认值
        if 'volume' not in df.columns:
            if '成交量' in df.columns:
                df['volume'] = df['成交量']
            else:
                df['volume'] = 0
        
        # 如果没有date列,使用索引
        if 'date' not in df.columns:
            if '日期' in df.columns:
                df['date'] = df['日期']
            elif isinstance(df.index, pd.DatetimeIndex):
                df['date'] = df.index
            else:
                df['date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='D')
        
        return df
    
    def _detect_stage(self, df: pd.DataFrame) -> int:
        """判断股票所处阶段"""
        if len(df) < self.config.ma_long:
            return 0
        
        # 计算均线
        df['ma20'] = df['close'].rolling(window=self.config.ma_medium).mean()
        df['ma60'] = df['close'].rolling(window=self.config.ma_long).mean()
        
        # 计算RSI
        rsi = self._calculate_rsi(df['close'])
        
        current_price = df.iloc[-1]['close']
        ma20 = df.iloc[-1]['ma20']
        ma60 = df.iloc[-1]['ma60']
        
        # 计算20日和60日涨幅
        if len(df) >= 60:
            price_20d_ago = df.iloc[-20]['close']
            price_60d_ago = df.iloc[0]['close']
            gain_20d = (current_price - price_20d_ago) / price_20d_ago * 100
            gain_60d = (current_price - price_60d_ago) / price_60d_ago * 100
        else:
            gain_20d = 0
            gain_60d = 0
        
        # 阶段判断逻辑
        # 五阶段:长期阴跌,近60日跌幅<-15%,RSI<30
        if gain_60d < -15 and rsi < 30:
            return 5
        
        # 四阶段:猛烈下跌,近20日跌幅<-10%
        if gain_20d < -10:
            return 4
        
        # 三阶段:疯狂上涨,近20日涨幅>15%,RSI>70
        if gain_20d > 15 and rsi > 70:
            return 3
        
        # 二阶段:快速上涨,近30日涨幅>10%,RSI 40-70
        if len(df) >= 30:
            price_30d_ago = df.iloc[-30]['close']
            gain_30d = (current_price - price_30d_ago) / price_30d_ago * 100
            if gain_30d > 10 and 40 <= rsi <= 70:
                return 2
        
        # 一阶段:长期下跌后企稳,近60日涨幅<5%,RSI<40
        if gain_60d < 5 and rsi < 40:
            return 1
        
        return 0
    
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
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """计算RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _detect_panic_points(
        self,
        df: pd.DataFrame,
        code: str,
        stage: int,
        stage_name: str
    ) -> List[BuyPoint]:
        """检测恐慌点买入信号"""
        buy_points = []
        
        if len(df) < self.config.panic_window:
            return buy_points
        
        # 计算成交量均线
        df['vol_ma'] = df['volume'].rolling(window=self.config.panic_window).mean()
        
        # 检测最近N天的恐慌点
        for i in range(max(0, len(df) - 5), len(df)):
            row = df.iloc[i]
            
            # 计算跌幅
            drop_pct = (row['close'] - row['open']) / row['open'] * 100
            
            # 计算放量倍数
            vol_ma = df.iloc[i]['vol_ma']
            vol_ratio = row['volume'] / vol_ma if vol_ma > 0 else 0
            
            # 恐慌点条件:大阴线+放量
            if (drop_pct <= self.config.panic_drop_threshold and 
                vol_ratio >= self.config.panic_vol_ratio):
                
                # 计算综合评分
                score = self._calculate_panic_score(drop_pct, vol_ratio, stage)
                
                # 计算置信度
                confidence = self._calculate_confidence('panic_point', stage, drop_pct, vol_ratio)
                
                buy_point = BuyPoint(
                    code=code,
                    name=self._get_stock_name(code),
                    buy_type='panic_point',
                    date=str(row['date'])[:10] if 'date' in row else str(i),
                    price=float(row['close']),
                    stage=stage,
                    stage_name=stage_name,
                    confidence=confidence,
                    score=score,
                    reasoning=f"恐慌点买入:跌幅{drop_pct:.2f}%,放量{vol_ratio:.2f}倍,阶段{stage}",
                    drop_pct=drop_pct,
                    vol_ratio=vol_ratio,
                    stage_score=self._get_stage_score(stage),
                    trend_strength=self._calculate_trend_strength(df),
                    emotion_score=self._calculate_emotion_score(df)
                )
                
                buy_points.append(buy_point)
        
        return buy_points
    
    def _detect_lowest_after_panic(
        self,
        df: pd.DataFrame,
        code: str,
        stage: int,
        stage_name: str,
        panic_points: List[BuyPoint]
    ) -> List[BuyPoint]:
        """检测恐慌点后的最低价买入"""
        buy_points = []
        
        if not panic_points or len(df) < 30:
            return buy_points
        
        # 找到最近的恐慌点
        latest_panic = panic_points[-1]
        panic_date = pd.to_datetime(latest_panic.date)
        
        # 检查恐慌点是否在最近30天内
        recent_30 = df.tail(30)
        panic_in_recent = False
        panic_idx = None
        
        for idx, row in recent_30.iterrows():
            row_date = pd.to_datetime(row['date']) if 'date' in row else idx
            if row_date == panic_date:
                panic_in_recent = True
                panic_idx = recent_30.index.get_loc(idx)
                break
        
        if not panic_in_recent:
            return buy_points
        
        # 恐慌点后的数据
        after_panic = recent_30.iloc[panic_idx+1:] if panic_idx < len(recent_30) - 1 else pd.DataFrame()
        
        if len(after_panic) == 0:
            return buy_points
        
        # 找到恐慌点后的最低价
        after_panic_low = after_panic['low'].min()
        
        # 当前价格
        current_low = float(df.iloc[-1]['low'])
        current_close = float(df.iloc[-1]['close'])
        
        # 如果当前价格接近或等于恐慌点后的最低价(允许0.5%误差)
        if current_low <= after_panic_low * 1.005 and current_low >= after_panic_low * 0.995:
            score = self._calculate_panic_score(latest_panic.drop_pct, latest_panic.vol_ratio, stage)
            confidence = self._calculate_confidence('lowest_after_panic', stage)
            
            buy_point = BuyPoint(
                code=code,
                name=self._get_stock_name(code),
                buy_type='lowest_after_panic',
                date=str(df.iloc[-1]['date'])[:10] if 'date' in df.iloc[-1] else str(len(df)-1),
                price=current_close,
                stage=stage,
                stage_name=stage_name,
                confidence=confidence,
                score=score * 0.9,  # 略低于恐慌点本身的评分
                reasoning=f"恐慌点后最低价买入:恐慌点{latest_panic.date},当前价格{current_close:.2f}",
                drop_pct=latest_panic.drop_pct,
                vol_ratio=latest_panic.vol_ratio,
                trend_strength=self._calculate_trend_strength(df),
                emotion_score=self._calculate_emotion_score(df)
            )
            
            buy_points.append(buy_point)
        
        return buy_points
    
    def _detect_o_point(
        self,
        df: pd.DataFrame,
        code: str,
        stage: int,
        stage_name: str
    ) -> List[BuyPoint]:
        """检测O点买入信号(一阶段)"""
        buy_points = []
        
        if len(df) < self.config.o_point_lookback:
            return buy_points
        
        # 获取回看期数据
        lookback_data = df.tail(self.config.o_point_lookback)
        
        # 找到最低点
        min_idx = lookback_data['low'].idxmin()
        min_price = lookback_data.loc[min_idx, 'low']
        min_volume = lookback_data.loc[min_idx, 'volume']
        
        # 计算平均成交量
        avg_volume = lookback_data['volume'].mean()
        
        # O点条件:最低价+成交量明显萎缩(地量)
        vol_shrink = min_volume / avg_volume if avg_volume > 0 else 0
        
        if vol_shrink <= self.config.o_point_vol_shrink:
            # 检查是否不再创新低
            after_min = lookback_data.loc[min_idx:]
            if len(after_min) > 5:
                # 最近5天没有创新低
                if after_min['low'].iloc[-5:].min() >= min_price * 0.98:
                    score = self._calculate_o_point_score(vol_shrink)
                    confidence = self._calculate_confidence('o_point', stage)
                    
                    buy_point = BuyPoint(
                        code=code,
                        name=self._get_stock_name(code),
                        buy_type='o_point',
                        date=str(lookback_data.iloc[-1]['date'])[:10] if 'date' in lookback_data.iloc[-1] else str(len(lookback_data)-1),
                        price=float(lookback_data.iloc[-1]['close']),
                        stage=stage,
                        stage_name=stage_name,
                        confidence=confidence,
                        score=score,
                        reasoning=f"O点买入:地量确认,成交量萎缩{vol_shrink:.2f},不再创新低",
                        trend_strength=self._calculate_trend_strength(df),
                        emotion_score=self._calculate_emotion_score(df)
                    )
                    
                    buy_points.append(buy_point)
        
        return buy_points
    
    def _detect_washout_end(
        self,
        df: pd.DataFrame,
        code: str,
        stage: int,
        stage_name: str
    ) -> List[BuyPoint]:
        """检测洗盘结束买入信号(二阶段)"""
        buy_points = []
        
        if len(df) < self.config.washout_days + 20:
            return buy_points
        
        # 检测洗盘特征
        recent = df.tail(self.config.washout_days)
        
        # 洗盘条件:
        # 1. 跌幅达到阈值
        # 2. 成交量萎缩
        # 3. 形态难看(多根阴线)
        
        high_price = recent['high'].max()
        current_price = recent.iloc[-1]['close']
        drop_pct = (current_price - high_price) / high_price * 100
        
        # 成交量萎缩
        recent_vol = recent['volume'].mean()
        before_vol = df.iloc[-self.config.washout_days-20:-self.config.washout_days]['volume'].mean()
        vol_shrink = recent_vol / before_vol if before_vol > 0 else 0
        
        # 阴线数量
        yin_lines = (recent['close'] < recent['open']).sum()
        yin_ratio = yin_lines / len(recent)
        
        # 洗盘结束条件
        if (abs(drop_pct) >= abs(self.config.washout_drop_threshold) and 
            vol_shrink <= self.config.washout_vol_shrink and
            yin_ratio >= 0.5):
            
            score = self._calculate_washout_score(drop_pct, vol_shrink, yin_ratio)
            confidence = self._calculate_confidence('washout_end', stage)
            
            buy_point = BuyPoint(
                code=code,
                name=self._get_stock_name(code),
                buy_type='washout_end',
                date=str(recent.iloc[-1]['date'])[:10] if 'date' in recent.iloc[-1] else str(len(recent)-1),
                price=float(current_price),
                stage=stage,
                stage_name=stage_name,
                confidence=confidence,
                score=score,
                reasoning=f"洗盘结束买入:跌幅{drop_pct:.2f}%,成交量萎缩{vol_shrink:.2f},阴线比例{yin_ratio:.2f}",
                drop_pct=drop_pct,
                vol_ratio=1/vol_shrink if vol_shrink > 0 else 0,
                washout_days=self.config.washout_days,
                trend_strength=self._calculate_trend_strength(df),
                emotion_score=self._calculate_emotion_score(df)
            )
            
            buy_points.append(buy_point)
        
        return buy_points
    
    def _calculate_panic_score(self, drop_pct: float, vol_ratio: float, stage: int) -> float:
        """计算恐慌点评分"""
        # 基础分:跌幅和放量
        drop_score = min(abs(drop_pct) / 10, 1.0) * 50  # 最高50分
        vol_score = min(vol_ratio / 3, 1.0) * 30  # 最高30分
        
        # 阶段加分
        stage_score = self._get_stage_score(stage) * 20  # 最高20分
        
        return drop_score + vol_score + stage_score
    
    def _calculate_o_point_score(self, vol_shrink: float) -> float:
        """计算O点评分"""
        # 成交量萎缩越明显,评分越高
        shrink_score = min((1 - vol_shrink) / 0.7, 1.0) * 60  # 最高60分
        stage_score = 20  # 一阶段固定20分
        trend_score = 20  # 趋势起点固定20分
        
        return shrink_score + stage_score + trend_score
    
    def _calculate_washout_score(self, drop_pct: float, vol_shrink: float, yin_ratio: float) -> float:
        """计算洗盘结束评分"""
        drop_score = min(abs(drop_pct) / 10, 1.0) * 30  # 最高30分
        shrink_score = min((1 - vol_shrink) / 0.5, 1.0) * 30  # 最高30分
        yin_score = yin_ratio * 20  # 最高20分
        stage_score = 20  # 二阶段固定20分
        
        return drop_score + shrink_score + yin_score + stage_score
    
    def _calculate_confidence(
        self,
        buy_type: str,
        stage: int,
        drop_pct: float = 0,
        vol_ratio: float = 0
    ) -> float:
        """计算置信度"""
        base_confidence = {
            'panic_point': 0.7,
            'lowest_after_panic': 0.8,
            'o_point': 0.6,
            'washout_end': 0.75
        }
        
        confidence = base_confidence.get(buy_type, 0.5)
        
        # 根据阶段调整
        if stage in self.config.preferred_stages:
            confidence += 0.1
        
        # 根据信号强度调整
        if buy_type == 'panic_point':
            if abs(drop_pct) > 5 and vol_ratio > 2:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_stage_score(self, stage: int) -> float:
        """获取阶段评分(0-1)"""
        scores = {
            1: 0.9,  # 一阶段最优先
            2: 1.0,  # 二阶段最优先
            5: 0.6,  # 五阶段次优
            0: 0.3,  # 未知
            3: 0.1,  # 三阶段不建议
            4: 0.0   # 四阶段不建议
        }
        return scores.get(stage, 0.0)
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """计算趋势强度"""
        if len(df) < 60:
            return 0.0
        
        # 计算MA20和MA60
        ma20 = df['close'].rolling(window=20).mean()
        ma60 = df['close'].rolling(window=60).mean()
        
        # 当前价格相对于MA60的位置
        current_price = df.iloc[-1]['close']
        ma60_current = ma60.iloc[-1]
        
        if ma60_current > 0:
            distance = (current_price - ma60_current) / ma60_current
            # 归一化到0-1
            return min(max(distance / 0.5, 0), 1.0)
        
        return 0.0
    
    def _calculate_emotion_score(self, df: pd.DataFrame) -> float:
        """计算情绪比例评分"""
        # 简化版:基于最近涨跌形态
        if len(df) < 20:
            return 0.0
        
        recent = df.tail(20)
        
        # 计算阴线比例(洗盘难看程度)
        yin_ratio = (recent['close'] < recent['open']).sum() / len(recent)
        
        # 计算上影线比例(出货好看程度)
        upper_shadow = (recent['high'] - recent[['open', 'close']].max(axis=1)) / recent['close']
        long_upper_ratio = (upper_shadow > 0.02).sum() / len(recent)
        
        # 情绪比例:难看洗盘+好看出货 = 看涨
        emotion_score = yin_ratio * 0.6 + (1 - long_upper_ratio) * 0.4
        
        return emotion_score
    
    def _get_stock_name(self, code: str) -> str:
        """获取股票名称"""
        try:
            from core.tools.data_fetcher import get_stock_name
            return get_stock_name(code)
        except:
            return code
