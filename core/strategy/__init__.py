"""
策略管理模块
提供策略基类、模板和组合优化功能
"""
from .base import Strategy

# 导入策略模板
from .templates.trend_following import DualMAStrategy, TripleMAStrategy
from .templates.game_theory import GameTheoryStrategy

__all__ = [
    'Strategy',
    'DualMAStrategy',
    'TripleMAStrategy',
    'GameTheoryStrategy'
]


