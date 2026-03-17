"""
策略相关数据模型
定义策略信号、组合、回测结果等实体
"""
from typing import TypedDict, List, Optional
from datetime import datetime


class StrategySignal(TypedDict):
    """策略信号"""
    strategy_type: str  # 策略类型：trend/arbitrage/hedge/event_driven
    commodity_id: str  # 品种ID
    contract: str  # 合约
    direction: str  # 方向：long/short
    entry_price: float  # 入场价格
    target_price: float  # 目标价格
    stop_loss: float  # 止损价格
    position_size: float  # 仓位规模（手数或金额）
    confidence: float  # 置信度 0-1
    time_horizon: str  # 时间周期：short_term/medium_term/long_term
    reasoning: str  # 策略逻辑说明
    risk_reward_ratio: float  # 风险收益比
    indicators: dict  # 关键技术指标值
    fundamental_factors: List[str]  # 关键基本面因素
    generated_at: str  # 生成时间


class StrategyPortfolio(TypedDict):
    """策略组合"""
    portfolio_id: str  # 组合ID
    strategies: List[StrategySignal]  # 策略列表
    total_exposure: float  # 总敞口
    diversification_score: float  # 分散化评分
    correlation_matrix: dict  # 相关性矩阵
    risk_metrics: dict  # 风险指标
    rebalance_frequency: str  # 再平衡频率


class BacktestResult(TypedDict):
    """回测结果"""
    strategy_id: str  # 策略ID
    start_date: str  # 开始日期
    end_date: str  # 结束日期
    initial_capital: float  # 初始资金
    final_capital: float  # 最终资金
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    volatility: float  # 波动率
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提诺比率
    win_rate: float  # 胜率
    profit_factor: float  # 盈亏比
    trade_count: int  # 交易次数
    avg_trade_duration: float  # 平均持仓时间
    best_trade: float  # 最佳交易
    worst_trade: float  # 最差交易
    equity_curve: List[float]  # 净值曲线
    drawdown_curve: List[float]  # 回撤曲线


class TechnicalIndicators(TypedDict):
    """技术指标"""
    ma_short: Optional[float]  # 短期均线
    ma_medium: Optional[float]  # 中期均线
    ma_long: Optional[float]  # 长期均线
    macd_dif: Optional[float]  # MACD DIF
    macd_dea: Optional[float]  # MACD DEA
    macd_bar: Optional[float]  # MACD 柱状图
    rsi: Optional[float]  # RSI
    bollinger_upper: Optional[float]  # 布林带上轨
    bollinger_middle: Optional[float]  # 布林带中轨
    bollinger_lower: Optional[float]  # 布林带下轨
    atr: Optional[float]  # ATR
    obv: Optional[float]  # OBV
    adx: Optional[float]  # ADX
    cci: Optional[float]  # CCI
    kdj_k: Optional[float]  # KDJ K值
    kdj_d: Optional[float]  # KDJ D值
    kdj_j: Optional[float]  # KDJ J值


class RiskMetrics(TypedDict):
    """风险指标"""
    var_95: float  # 95%置信度VaR
    var_99: float  # 99%置信度VaR
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提诺比率
    calmar_ratio: float  # 卡玛比率
    volatility: float  # 波动率
    beta: Optional[float]  # Beta系数
    alpha: Optional[float]  # Alpha系数
    information_ratio: Optional[float]  # 信息比率
