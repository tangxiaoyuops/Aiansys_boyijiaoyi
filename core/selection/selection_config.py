"""
选股策略配置
定义选股参数、筛选条件、风险控制等配置
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SelectionConfig:
    """选股策略配置"""
    
    # === 基础参数 ===
    initial_capital: float = 1000000.0  # 初始资金
    max_stocks: int = 10  # 最大持仓股票数量
    max_position_per_stock: float = 0.2  # 单只股票最大仓位比例
    
    # === 买点识别参数 ===
    # 恐慌点参数
    panic_drop_threshold: float = -3.0  # 恐慌点跌幅阈值(%)
    panic_vol_ratio: float = 1.5  # 恐慌点放量倍数
    panic_window: int = 60  # 恐慌点检测窗口(天)
    
    # 洗盘参数
    washout_drop_threshold: float = -5.0  # 洗盘跌幅阈值(%)
    washout_days: int = 20  # 洗盘持续时间(天)
    washout_vol_shrink: float = 0.5  # 洗盘成交量萎缩比例
    
    # O点识别参数
    o_point_lookback: int = 120  # O点识别回看期(天)
    o_point_vol_shrink: float = 0.3  # O点成交量萎缩比例(地量)
    
    # === 阶段过滤参数 ===
    preferred_stages: List[int] = field(default_factory=lambda: [1, 2])  # 优先阶段
    allowed_stages: List[int] = field(default_factory=lambda: [1, 2, 5])  # 允许买入的阶段
    
    # === 技术指标参数 ===
    ma_short: int = 5  # 短期均线
    ma_medium: int = 20  # 中期均线
    ma_long: int = 60  # 长期均线
    
    rsi_oversold: float = 30.0  # RSI超卖
    rsi_overbought: float = 70.0  # RSI超买
    
    # === 情绪比例关系参数 ===
    # 看涨信号: 难看的洗盘 + 好看的出货
    ugly_washout_score: float = 0.7  # 难看洗盘评分阈值
    beautiful_sell_score: float = 0.7  # 好看出货评分阈值
    
    # === 出货规模参数 ===
    # 大规模出货: 洗盘时间>1年,不做中长线
    large_scale_washout_days: int = 365
    # 中等规模出货: 洗盘3-6个月,轻仓试探
    medium_scale_washout_min: int = 90
    medium_scale_washout_max: int = 180
    # 小规模出货: 洗盘<3个月,可重仓
    small_scale_washout_days: int = 90
    
    # === 筛选条件权重 ===
    stage_weight: float = 0.3  # 阶段权重
    trend_weight: float = 0.25  # 趋势权重
    pattern_weight: float = 0.25  # 形态权重(洗盘/出货)
    emotion_weight: float = 0.2  # 情绪比例权重
    
    # === 风险控制参数 ===
    stop_loss_ratio: float = 0.08  # 止损比例(8%)
    take_profit_ratio: float = 0.15  # 止盈比例(15%)
    max_drawdown: float = 0.2  # 最大回撤控制(20%)
    
    # === 数据参数 ===
    data_days: int = 250  # 获取历史数据天数
    min_data_days: int = 120  # 最少数据天数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "initial_capital": self.initial_capital,
            "max_stocks": self.max_stocks,
            "max_position_per_stock": self.max_position_per_stock,
            "panic_drop_threshold": self.panic_drop_threshold,
            "panic_vol_ratio": self.panic_vol_ratio,
            "panic_window": self.panic_window,
            "washout_drop_threshold": self.washout_drop_threshold,
            "washout_days": self.washout_days,
            "washout_vol_shrink": self.washout_vol_shrink,
            "o_point_lookback": self.o_point_lookback,
            "o_point_vol_shrink": self.o_point_vol_shrink,
            "preferred_stages": self.preferred_stages,
            "allowed_stages": self.allowed_stages,
            "ma_short": self.ma_short,
            "ma_medium": self.ma_medium,
            "ma_long": self.ma_long,
            "rsi_oversold": self.rsi_oversold,
            "rsi_overbought": self.rsi_overbought,
            "ugly_washout_score": self.ugly_washout_score,
            "beautiful_sell_score": self.beautiful_sell_score,
            "stage_weight": self.stage_weight,
            "trend_weight": self.trend_weight,
            "pattern_weight": self.pattern_weight,
            "emotion_weight": self.emotion_weight,
            "stop_loss_ratio": self.stop_loss_ratio,
            "take_profit_ratio": self.take_profit_ratio,
            "max_drawdown": self.max_drawdown,
            "data_days": self.data_days,
            "min_data_days": self.min_data_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelectionConfig":
        """从字典创建"""
        return cls(**data)
    
    @classmethod
    def conservative(cls) -> "SelectionConfig":
        """保守型配置"""
        return cls(
            max_stocks=5,
            max_position_per_stock=0.15,
            panic_drop_threshold=-5.0,
            panic_vol_ratio=2.0,
            preferred_stages=[1, 2],
            allowed_stages=[1, 2],
            stop_loss_ratio=0.05,
            take_profit_ratio=0.12
        )
    
    @classmethod
    def aggressive(cls) -> "SelectionConfig":
        """激进型配置"""
        return cls(
            max_stocks=15,
            max_position_per_stock=0.25,
            panic_drop_threshold=-2.5,
            panic_vol_ratio=1.2,
            preferred_stages=[1, 2, 5],
            allowed_stages=[1, 2, 5],
            stop_loss_ratio=0.1,
            take_profit_ratio=0.2
        )
