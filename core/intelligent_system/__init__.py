"""
博弈交易法智能分析系统 - 核心模块

该模块实现了基于博弈理论的智能股票分析系统，
包括Agent驱动的分析引擎、数据采集、决策系统等核心功能。
"""

__version__ = "1.0.0"
__author__ = "博弈交易法团队"

# 核心组件导入 - 延迟导入，避免循环依赖
# from core.database.db_manager import DatabaseManager
# from core.data_collection.stock_collector import StockDataCollector
# from core.agents.phase_analyzer import PhaseAnalysisAgent
# from core.agents.knowledge_base import BoyiKnowledgeBase
# from core.scheduler.task_scheduler import TaskScheduler

__all__ = [
    "DatabaseManager",
    "StockDataCollector",
    "PhaseAnalysisAgent",
    "BoyiKnowledgeBase",
    "TaskScheduler",
]
