"""
止损管理
"""
from typing import Optional, Dict, Any


class StopLossManager:
    """止损管理器"""
    
    def __init__(self, stop_loss_ratio: float = 0.05, take_profit_ratio: float = 0.10):
        """
        初始化
        
        Args:
            stop_loss_ratio: 止损比例（默认5%）
            take_profit_ratio: 止盈比例（默认10%）
        """
        self.stop_loss_ratio = stop_loss_ratio
        self.take_profit_ratio = take_profit_ratio
    
    def check_stop_loss(self, entry_price: float, current_price: float, direction: int) -> Optional[Dict[str, Any]]:
        """
        检查是否触发止损
        
        Args:
            entry_price: 开仓价格
            current_price: 当前价格
            direction: 方向（1=多头, -1=空头）
            
        Returns:
            止损信号或None
        """
        if entry_price <= 0:
            return None
        
        if direction > 0:  # 多头
            pnl_ratio = (current_price - entry_price) / entry_price
            if pnl_ratio <= -self.stop_loss_ratio:
                return {
                    'action': 'CLOSE_ALL',
                    'reason': f'止损：亏损{pnl_ratio:.2%}'
                }
        else:  # 空头
            pnl_ratio = (entry_price - current_price) / entry_price
            if pnl_ratio <= -self.stop_loss_ratio:
                return {
                    'action': 'CLOSE_ALL',
                    'reason': f'止损：亏损{pnl_ratio:.2%}'
                }
        
        return None
    
    def check_take_profit(self, entry_price: float, current_price: float, direction: int) -> Optional[Dict[str, Any]]:
        """
        检查是否触发止盈
        
        Args:
            entry_price: 开仓价格
            current_price: 当前价格
            direction: 方向
            
        Returns:
            止盈信号或None
        """
        if entry_price <= 0:
            return None
        
        if direction > 0:  # 多头
            pnl_ratio = (current_price - entry_price) / entry_price
            if pnl_ratio >= self.take_profit_ratio:
                return {
                    'action': 'CLOSE_ALL',
                    'reason': f'止盈：盈利{pnl_ratio:.2%}'
                }
        else:  # 空头
            pnl_ratio = (entry_price - current_price) / entry_price
            if pnl_ratio >= self.take_profit_ratio:
                return {
                    'action': 'CLOSE_ALL',
                    'reason': f'止盈：盈利{pnl_ratio:.2%}'
                }
        
        return None






