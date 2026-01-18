"""
趋势跟踪策略模板
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
import pandas as pd
import numpy as np

from ..base import Strategy

if TYPE_CHECKING:
    from ...backtest.portfolio import Portfolio


class DualMAStrategy(Strategy):
    """双均线策略"""
    
    def __init__(self):
        super().__init__("双均线策略")
        self.fast_period = 5
        self.slow_period = 20
        self.position_size = 1  # 每次开仓手数
    
    def _on_initialize(self):
        """初始化参数"""
        self.fast_period = self.get_parameter('fast_period', 5)
        self.slow_period = self.get_parameter('slow_period', 20)
        self.position_size = self.get_parameter('position_size', 1)
    
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        策略逻辑：
        - 快速均线上穿慢速均线：买入
        - 快速均线下穿慢速均线：卖出
        """
        if len(data) < self.slow_period:
            return None
        
        # 获取收盘价
        close = data['close'] if 'close' in data.columns else data['收盘']
        
        # 计算均线
        fast_ma = close.rolling(self.fast_period).mean()
        slow_ma = close.rolling(self.slow_period).mean()
        
        if len(fast_ma) < 2:
            return None
        
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        prev_fast = fast_ma.iloc[-2]
        prev_slow = slow_ma.iloc[-2]
        
        # 金叉：快速均线上穿慢速均线
        if prev_fast <= prev_slow and current_fast > current_slow:
            if portfolio.position.size <= 0:  # 空仓或持空
                return {
                    'action': 'OPEN_LONG',
                    'size': self.position_size,
                    'reason': f'金叉：MA{self.fast_period}({current_fast:.2f}) > MA{self.slow_period}({current_slow:.2f})'
                }
        
        # 死叉：快速均线下穿慢速均线
        elif prev_fast >= prev_slow and current_fast < current_slow:
            if portfolio.position.size >= 0:  # 空仓或持多
                if portfolio.position.size > 0:
                    return {
                        'action': 'CLOSE_ALL',
                        'size': portfolio.position.size,
                        'reason': f'死叉：MA{self.fast_period}({current_fast:.2f}) < MA{self.slow_period}({current_slow:.2f})'
                    }
                else:
                    return {
                        'action': 'OPEN_SHORT',
                        'size': self.position_size,
                        'reason': f'死叉：MA{self.fast_period}({current_fast:.2f}) < MA{self.slow_period}({current_slow:.2f})'
                    }
        
        return None


class TripleMAStrategy(Strategy):
    """三均线策略"""
    
    def __init__(self):
        super().__init__("三均线策略")
        self.fast_period = 5
        self.mid_period = 20
        self.slow_period = 60
        self.position_size = 1
    
    def _on_initialize(self):
        """初始化参数"""
        self.fast_period = self.get_parameter('fast_period', 5)
        self.mid_period = self.get_parameter('mid_period', 20)
        self.slow_period = self.get_parameter('slow_period', 60)
        self.position_size = self.get_parameter('position_size', 1)
    
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        策略逻辑：
        - 三均线多头排列（快>中>慢）：买入
        - 三均线空头排列（快<中<慢）：卖出
        """
        if len(data) < self.slow_period:
            return None
        
        close = data['close'] if 'close' in data.columns else data['收盘']
        
        fast_ma = close.rolling(self.fast_period).mean()
        mid_ma = close.rolling(self.mid_period).mean()
        slow_ma = close.rolling(self.slow_period).mean()
        
        if len(fast_ma) < 1:
            return None
        
        current_fast = fast_ma.iloc[-1]
        current_mid = mid_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        
        # 多头排列
        if current_fast > current_mid > current_slow:
            if portfolio.position.size <= 0:
                return {
                    'action': 'OPEN_LONG',
                    'size': self.position_size,
                    'reason': f'多头排列：MA{self.fast_period} > MA{self.mid_period} > MA{self.slow_period}'
                }
        
        # 空头排列
        elif current_fast < current_mid < current_slow:
            if portfolio.position.size >= 0:
                if portfolio.position.size > 0:
                    return {
                        'action': 'CLOSE_ALL',
                        'size': portfolio.position.size,
                        'reason': f'空头排列：MA{self.fast_period} < MA{self.mid_period} < MA{self.slow_period}'
                    }
                else:
                    return {
                        'action': 'OPEN_SHORT',
                        'size': self.position_size,
                        'reason': f'空头排列：MA{self.fast_period} < MA{self.mid_period} < MA{self.slow_period}'
                    }
        
        return None


