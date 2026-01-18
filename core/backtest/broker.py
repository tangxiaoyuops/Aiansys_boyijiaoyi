"""
模拟券商模块
处理订单执行、滑点、手续费等
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

from .portfolio import Portfolio


@dataclass
class BrokerConfig:
    """券商配置"""
    commission_rate: float = 0.0003  # 手续费率（万3）
    slippage: float = 0.0002  # 滑点（万2）
    margin_rate: float = 0.15  # 保证金率（15%）
    contract_multiplier: int = 10  # 合约乘数
    min_commission: float = 0.0  # 最小手续费


class FuturesBroker:
    """期货模拟券商"""
    
    def __init__(self, config: BrokerConfig):
        """
        初始化券商
        
        Args:
            config: 券商配置
        """
        self.config = config
    
    def calculate_commission(self, size: int, price: float) -> float:
        """
        计算手续费
        
        Args:
            size: 交易数量（手数）
            price: 价格
            
        Returns:
            手续费金额
        """
        commission = abs(size) * price * self.config.contract_multiplier * self.config.commission_rate
        return max(commission, self.config.min_commission)
    
    def calculate_slippage_cost(self, size: int, price: float) -> float:
        """
        计算滑点成本
        
        Args:
            size: 交易数量
            price: 价格
            
        Returns:
            滑点成本金额
        """
        return abs(size) * price * self.config.contract_multiplier * self.config.slippage
    
    def calculate_margin_required(self, size: int, price: float) -> float:
        """
        计算所需保证金
        
        Args:
            size: 持仓数量
            price: 价格
            
        Returns:
            所需保证金
        """
        return abs(size) * price * self.config.contract_multiplier * self.config.margin_rate
    
    def execute_order(
        self,
        signal: Dict[str, Any],
        current_bar: Dict[str, Any],
        portfolio: Portfolio
    ) -> Optional[Dict[str, Any]]:
        """
        执行订单
        
        Args:
            signal: 交易信号 {
                'action': 'OPEN_LONG' | 'OPEN_SHORT' | 'CLOSE_LONG' | 'CLOSE_SHORT' | 'CLOSE_ALL',
                'size': 交易数量,
                'reason': 交易原因
            }
            current_bar: 当前K线数据 {'open', 'high', 'low', 'close', ...}
            portfolio: 投资组合
            
        Returns:
            交易结果或None（如果无法执行）
        """
        action = signal.get('action')
        size = signal.get('size', 0)
        reason = signal.get('reason', '')
        
        if size <= 0:
            return None
        
        # 获取当前价格（使用收盘价）
        current_price = current_bar.get('close', 0)
        if current_price <= 0:
            # 尝试其他可能的列名
            current_price = current_bar.get('收盘', current_bar.get('settle', 0))
        if current_price <= 0 or pd.isna(current_price):
            return None
        
        current_price = float(current_price)
        
        # 确定交易方向
        direction = 0
        if action in ['OPEN_LONG', 'CLOSE_SHORT']:
            direction = 1
        elif action in ['OPEN_SHORT', 'CLOSE_LONG']:
            direction = -1
        elif action == 'CLOSE_ALL':
            direction = portfolio.position.direction
        
        # 计算手续费和滑点
        commission = self.calculate_commission(size, current_price)
        slippage_cost = self.calculate_slippage_cost(size, current_price)
        
        # 检查资金是否充足（开仓时）
        if action in ['OPEN_LONG', 'OPEN_SHORT']:
            margin_required = self.calculate_margin_required(size, current_price)
            trade_cost = size * current_price * self.config.contract_multiplier + commission + slippage_cost
            
            if portfolio.cash < trade_cost:
                # 资金不足
                return None
        
        # 执行交易
        trade = portfolio.record_trade(
            action=action,
            direction=direction,
            size=size,
            price=current_price,
            commission=commission,
            slippage=self.config.slippage,
            reason=reason,
            time=current_bar.get('date', datetime.now())
        )
        
        return {
            'success': True,
            'trade': trade,
            'action': action,
            'size': size,
            'price': current_price,
            'commission': commission,
            'slippage': slippage_cost
        }
    
    def can_open_position(
        self,
        size: int,
        price: float,
        portfolio: Portfolio
    ) -> bool:
        """
        检查是否可以开仓
        
        Args:
            size: 开仓数量
            price: 价格
            portfolio: 投资组合
            
        Returns:
            是否可以开仓
        """
        margin_required = self.calculate_margin_required(size, price)
        commission = self.calculate_commission(size, price)
        trade_cost = size * price * self.config.contract_multiplier + commission
        
        return portfolio.cash >= trade_cost


