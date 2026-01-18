"""
均值回归策略模板
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
import pandas as pd
import numpy as np

from ..base import Strategy

if TYPE_CHECKING:
    from ...backtest.portfolio import Portfolio


class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self):
        super().__init__("布林带策略")
        self.period = 20
        self.std_dev = 2.0
        self.position_size = 1
    
    def _on_initialize(self):
        """初始化参数"""
        self.period = self.get_parameter('period', 20)
        self.std_dev = self.get_parameter('std_dev', 2.0)
        self.position_size = self.get_parameter('position_size', 1)
    
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        策略逻辑：
        - 价格触及下轨：买入
        - 价格触及上轨：卖出
        """
        if len(data) < self.period:
            return None
        
        close = data['close'] if 'close' in data.columns else data['收盘']
        
        # 计算布林带
        ma = close.rolling(self.period).mean()
        std = close.rolling(self.period).std()
        upper_band = ma + self.std_dev * std
        lower_band = ma - self.std_dev * std
        
        if len(close) < 1:
            return None
        
        current_price = close.iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        # 价格触及下轨，买入
        if current_price <= current_lower:
            if portfolio.position.size <= 0:
                return {
                    'action': 'OPEN_LONG',
                    'size': self.position_size,
                    'reason': f'价格触及下轨：{current_price:.2f} <= {current_lower:.2f}'
                }
        
        # 价格触及上轨，卖出
        elif current_price >= current_upper:
            if portfolio.position.size >= 0:
                if portfolio.position.size > 0:
                    return {
                        'action': 'CLOSE_ALL',
                        'size': portfolio.position.size,
                        'reason': f'价格触及上轨：{current_price:.2f} >= {current_upper:.2f}'
                    }
        
        return None


class RSIStrategy(Strategy):
    """RSI策略"""
    
    def __init__(self):
        super().__init__("RSI策略")
        self.period = 14
        self.overbought = 70
        self.oversold = 30
        self.position_size = 1
    
    def _on_initialize(self):
        """初始化参数"""
        self.period = self.get_parameter('rsi_period', 14)
        self.overbought = self.get_parameter('rsi_overbought', 70)
        self.oversold = self.get_parameter('rsi_oversold', 30)
        self.position_size = self.get_parameter('position_size', 1)
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        策略逻辑：
        - RSI < 超卖线：买入
        - RSI > 超买线：卖出
        """
        if len(data) < self.period + 1:
            return None
        
        close = data['close'] if 'close' in data.columns else data['收盘']
        
        # 计算RSI
        rsi = self._calculate_rsi(close, self.period)
        
        if len(rsi) < 1 or pd.isna(rsi.iloc[-1]):
            return None
        
        current_rsi = rsi.iloc[-1]
        
        # RSI超卖，买入
        if current_rsi < self.oversold:
            if portfolio.position.size <= 0:
                return {
                    'action': 'OPEN_LONG',
                    'size': self.position_size,
                    'reason': f'RSI超卖：{current_rsi:.2f} < {self.oversold}'
                }
        
        # RSI超买，卖出
        elif current_rsi > self.overbought:
            if portfolio.position.size >= 0:
                if portfolio.position.size > 0:
                    return {
                        'action': 'CLOSE_ALL',
                        'size': portfolio.position.size,
                        'reason': f'RSI超买：{current_rsi:.2f} > {self.overbought}'
                    }
        
        return None


