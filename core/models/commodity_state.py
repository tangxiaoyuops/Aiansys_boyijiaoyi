"""
大宗商品分析状态定义
定义LangGraph工作流中使用的状态结构
"""
from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime
from core.models.commodity_models import RawEvidence
from core.models.strategy_models import StrategySignal, BacktestResult, TechnicalIndicators, RiskMetrics


class CommodityAnalysisState(TypedDict):
    """大宗商品分析状态定义"""
    
    # 输入
    commodity_or_chain: str  # 品种或产业链名称
    time_range: Optional[dict]  # 时间范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    user_question: Optional[str]  # 用户追问或关注点
    strategy_type: Optional[str]  # 策略类型：trend/arbitrage/hedge/event_driven
    
    # 采集结果
    raw_evidence: Optional[RawEvidence]  # 原始证据包
    fetch_error: Optional[str]  # 采集错误信息
    
    # 分析结果
    structured_analysis: Optional[Dict[str, Any]]  # 结构化分析（摘要、分类、驱动、置信度）
    judgment: Optional[Dict[str, Any]]  # 自动判定（缺口、矛盾、关键驱动、建议搜索）
    
    # 自动搜索
    search_queries: Optional[List[str]]  # 本轮要执行的查询
    search_results: Optional[List[Dict[str, Any]]]  # 本轮搜索结果
    round_index: int  # 当前轮次
    
    # 技术指标
    technical_indicators: Optional[TechnicalIndicators]  # 各类技术指标值
    market_state: Optional[str]  # 市场状态：trend/range/reversal
    
    # 策略生成
    strategy_signals: Optional[List[StrategySignal]]  # 生成的策略信号列表
    strategy_confidence: Optional[float]  # 策略置信度
    
    # 回测评估
    backtest_results: Optional[List[BacktestResult]]  # 回测结果
    risk_metrics: Optional[RiskMetrics]  # 风险指标
    
    # 最终输出
    final_report: Optional[str]  # 最终报告
    structured_output: Optional[Dict[str, Any]]  # 结构化输出（JSON）
    
    # 配置
    max_rounds: int  # 最大轮次
    enable_backtest: bool  # 是否启用回测
    timeout: int  # 超时时间（秒）
    
    # 会话管理
    conversation_id: Optional[str]  # 会话ID
    chat_history: Optional[List[Dict[str, str]]]  # 聊天历史
    
    # 元数据
    start_time: float  # 开始时间戳
    end_time: Optional[float]  # 结束时间戳
    total_duration: Optional[float]  # 总耗时（秒）
