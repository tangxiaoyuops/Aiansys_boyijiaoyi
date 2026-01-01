"""
状态定义模块
定义LangGraph工作流中使用的状态结构
"""
from typing import TypedDict, Optional, Dict, Any, List
import pandas as pd


class AnalysisState(TypedDict):
    """分析状态定义"""
    # 用户输入
    user_message: str
    stock_code: str
    analysis_type: Optional[str]  # regular/game_theory
    
    # 数据
    stock_data: Optional[pd.DataFrame]
    stock_name: Optional[str]  # 股票名称
    
    # 结构化数据（新框架）
    structured_data: Optional[Dict[str, Any]]  # 结构化数据（分水岭、出货周期、阶段候选等）
    
    # LLM分析结果（新框架）
    llm_stage_result: Optional[Dict[str, Any]]  # LLM阶段分析结果
    llm_distribution_result: Optional[Dict[str, Any]]  # LLM出货分析结果
    llm_emotion_result: Optional[Dict[str, Any]]  # LLM情绪分析结果
    llm_trading_points_result: Optional[Dict[str, Any]]  # LLM买卖点分析结果
    
    # 分析结果（旧框架，保留兼容性）
    stage_result: Optional[Dict[str, Any]]  # 阶段分析结果
    o_point_result: Optional[Dict[str, Any]]  # O点识别结果
    washout_result: Optional[Dict[str, Any]]  # 洗盘分析结果
    distribution_result: Optional[Dict[str, Any]]  # 出货分析结果
    emotion_ratio_result: Optional[Dict[str, Any]]  # 情绪比例关系结果
    anchor_result: Optional[Dict[str, Any]]  # 锚定分析结果
    summary_result: Optional[Dict[str, Any]]  # 分析总结
    strategy_recommendation: Optional[Dict[str, Any]]  # 策略推荐
    backtest_result: Optional[Dict[str, Any]]  # 回测结果（原有简单回测）
    vnpy_backtest_result: Optional[Dict[str, Any]]  # vnpy 回测结果（专业回测引擎）
    regular_analysis_result: Optional[Dict[str, Any]]  # 常规分析结果
    
    # 最终输出
    final_report: Optional[str]
    
    # 配置
    run_backtest: bool
    days: int

    # 会话管理（多轮对话）
    conversation_id: Optional[str]                # 会话ID
    chat_history: Optional[List[Dict[str, str]]]  # [{'role': 'user'/'assistant', 'content': '...'}]

    # 对话模式标记 & 对话结果
    dialogue_mode: Optional[bool]                 # 是否为常规对话/对历史结论的追问
    dialogue_result: Optional[Dict[str, Any]]     # 纯对话LLM的结果（如果走对话分支）

    # 场景定向分析（只重跑某一类分析）
    # 可选值示例：'stage'（阶段）、'distribution'（出货）、'emotion'（情绪）、'trading'（买卖点）
    scene_type: Optional[str]
