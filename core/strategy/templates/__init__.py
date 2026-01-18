"""
策略模板库
预置常用策略
"""
from .trend_following import DualMAStrategy, TripleMAStrategy
from .mean_reversion import BollingerBandsStrategy, RSIStrategy
from .game_theory import GameTheoryStrategy

__all__ = [
    'DualMAStrategy',
    'TripleMAStrategy',
    'BollingerBandsStrategy',
    'RSIStrategy',
    'GameTheoryStrategy',
]

# 策略注册表
STRATEGY_REGISTRY = {
    'dual_ma': DualMAStrategy,
    'triple_ma': TripleMAStrategy,
    'bollinger_bands': BollingerBandsStrategy,
    'rsi': RSIStrategy,
    'game_theory': GameTheoryStrategy,
    '博弈分析': GameTheoryStrategy,  # 中文名称支持
}


def get_strategy(strategy_name: str):
    """
    根据名称获取策略类
    
    Args:
        strategy_name: 策略名称
        
    Returns:
        策略类
    """
    return STRATEGY_REGISTRY.get(strategy_name.lower())


