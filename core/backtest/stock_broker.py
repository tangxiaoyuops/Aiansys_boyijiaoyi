"""
股票模拟券商模块
处理订单执行、滑点、手续费等（全款买入，无需保证金）
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

from .portfolio import Portfolio


@dataclass
class StockBrokerConfig:
    """股票券商配置"""
    commission_rate: float = 0.0003  # 手续费率（万3）
    slippage: float = 0.0002  # 滑点（万2）
    min_commission: float = 5.0  # 最小手续费（通常为5元）
    stamp_tax_rate: float = 0.001  # 印花税（卖出时收取，0.1%）


class StockBroker:
    """股票模拟券商"""
    
    def __init__(self, config: StockBrokerConfig):
        """
        初始化券商
        
        Args:
            config: 券商配置
        """
        self.config = config
    
    def calculate_commission(self, size: int, price: float, is_buy: bool = True) -> float:
        """
        计算手续费（买入和卖出都收手续费，卖出还收印花税）
        
        Args:
            size: 交易数量（股数）
            price: 价格
            is_buy: 是否买入（买入时只收手续费，卖出时收手续费+印花税）
            
        Returns:
            手续费金额
        """
        # 基础手续费
        commission = abs(size) * price * self.config.commission_rate
        commission = max(commission, self.config.min_commission)
        
        # 卖出时加印花税
        if not is_buy:
            commission += abs(size) * price * self.config.stamp_tax_rate
        
        return commission
    
    def calculate_slippage_cost(self, size: int, price: float) -> float:
        """
        计算滑点成本
        
        Args:
            size: 交易数量
            price: 价格
            
        Returns:
            滑点成本金额
        """
        return abs(size) * price * self.config.slippage
    
    def execute_order(
        self,
        signal: Dict[str, Any],
        current_bar: Dict[str, Any],
        portfolio: Portfolio
    ) -> Optional[Dict[str, Any]]:
        """
        执行订单（仅支持做多，不支持做空）
        
        Args:
            signal: 交易信号 {
                'action': 'OPEN_LONG' | 'CLOSE_LONG' | 'CLOSE_ALL',
                'size': 交易数量（股数）,
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
        
        # 股票不支持做空，拒绝做空信号
        if action in ['OPEN_SHORT', 'CLOSE_SHORT']:
            print(f"[股票经纪人] 拒绝做空信号: {action}，股票交易不支持做空")
            return None
        
        # 获取当前价格（使用收盘价）
        current_price = current_bar.get('close', 0)
        if current_price <= 0:
            # 尝试其他可能的列名
            current_price = current_bar.get('收盘', current_bar.get('settle', 0))
        if current_price <= 0 or pd.isna(current_price):
            return None
        
        current_price = float(current_price)
        
        # 确定交易方向（股票只有做多）
        direction = 0
        if action == 'OPEN_LONG':
            direction = 1
        elif action in ['CLOSE_LONG', 'CLOSE_ALL']:
            # 只能平掉多头持仓
            if portfolio.position.size <= 0:
                print(f"[股票经纪人] 无持仓可平，忽略信号: {action}")
                return None
            direction = -1  # 平仓方向为负（减少持仓）
        
        # 计算手续费和滑点
        is_buy = (action == 'OPEN_LONG')
        commission = self.calculate_commission(size, current_price, is_buy)
        slippage_cost = self.calculate_slippage_cost(size, current_price)
        
        # 检查资金是否充足（开仓时，需要全款买入）
        if action == 'OPEN_LONG':
            # 买入需要：股数 * 价格 + 手续费 + 滑点
            trade_cost = size * current_price + commission + slippage_cost
            
            if portfolio.cash < trade_cost:
                # 资金不足，拒绝交易
                print(f"[股票经纪人] 资金不足，拒绝买入：需要{trade_cost:.2f}，可用{portfolio.cash:.2f}")
                return None
        
        # 检查持仓是否充足（平仓时）
        if action in ['CLOSE_LONG', 'CLOSE_ALL']:
            # 平仓数量不能超过持仓
            if size > portfolio.position.size:
                size = portfolio.position.size
                if size <= 0:
                    return None
        
        # 执行交易
        trade = portfolio.record_trade(
            action=action,
            direction=direction,
            size=size if action == 'OPEN_LONG' else size,  # 买入为正，平仓为正（减少持仓）
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
        检查是否可以开仓（买入）
        
        Args:
            size: 开仓数量（股数）
            price: 价格
            portfolio: 投资组合
            
        Returns:
            是否可以开仓
        """
        commission = self.calculate_commission(size, price, is_buy=True)
        slippage_cost = self.calculate_slippage_cost(size, price)
        trade_cost = size * price + commission + slippage_cost
        
        return portfolio.cash >= trade_cost







