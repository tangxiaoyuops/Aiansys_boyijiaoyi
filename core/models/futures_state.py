"""
期货分析状态定义模块
定义LangGraph工作流中使用的期货分析状态结构
"""
from typing import TypedDict, Optional, Dict, Any, List
import pandas as pd


class FuturesAnalysisState(TypedDict):
    """期货分析状态定义"""
    # 用户输入
    user_message: str
    futures_code: str
    analysis_type: Optional[str]  # all/game_theory/risk/spread/fundamental
    
    # 期货基本信息
    futures_name: Optional[str]  # 期货名称
    exchange: Optional[str]  # 交易所
    contract_month: Optional[str]  # 合约月份
    product_code: Optional[str]  # 品种代码
    
    # 数据
    futures_data: Optional[pd.DataFrame]  # 期货数据
    open_interest: Optional[pd.DataFrame]  # 持仓量数据
    basis_data: Optional[pd.DataFrame]  # 基差数据
    related_contracts: Optional[Dict[str, Any]]  # 相关合约信息
    spread_data: Optional[pd.DataFrame]  # 价差数据
    
    # 结构化数据
    structured_data: Optional[Dict[str, Any]]  # 结构化数据
    
    # 分析结果
    game_theory_result: Optional[Dict[str, Any]]  # 博弈交易法分析结果
    risk_analysis_result: Optional[Dict[str, Any]]  # 风险管理分析结果
    spread_analysis_result: Optional[Dict[str, Any]]  # 价差分析结果
    fundamental_analysis_result: Optional[Dict[str, Any]]  # 基本面分析结果
    strategy_recommendation: Optional[Dict[str, Any]]  # 策略推荐
    
    # 最终输出
    final_report: Optional[str]
    
    # 配置
    days: int
    
    # 合约信息
    margin_rate: Optional[float]  # 保证金率
    contract_multiplier: Optional[int]  # 合约乘数
    
    # 会话管理（多轮对话）
    conversation_id: Optional[str]  # 会话ID
    chat_history: Optional[List[Dict[str, str]]]  # [{'role': 'user'/'assistant', 'content': '...'}]

