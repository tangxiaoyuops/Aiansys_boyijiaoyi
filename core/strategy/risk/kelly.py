"""
凯利公式
用于计算最优仓位比例
"""


def kelly_criterion(win_rate: float, profit_loss_ratio: float) -> float:
    """
    计算凯利比例
    
    Args:
        win_rate: 胜率（0-1之间）
        profit_loss_ratio: 盈亏比（平均盈利/平均亏损）
        
    Returns:
        最优仓位比例（0-1之间）
    """
    if profit_loss_ratio <= 0:
        return 0.0
    
    b = profit_loss_ratio
    p = win_rate
    q = 1 - p
    
    kelly = (b * p - q) / b
    
    # 限制在合理范围内
    return max(0.0, min(kelly, 1.0))


def half_kelly_criterion(win_rate: float, profit_loss_ratio: float) -> float:
    """
    计算半凯利比例（更保守）
    
    Args:
        win_rate: 胜率
        profit_loss_ratio: 盈亏比
        
    Returns:
        半凯利比例
    """
    return kelly_criterion(win_rate, profit_loss_ratio) * 0.5







