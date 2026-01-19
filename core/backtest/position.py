"""
仓位管理模块
管理期货持仓状态
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Position:
    """期货持仓"""
    
    direction: int  # 1=多头, -1=空头, 0=空仓
    size: int  # 持仓数量（手数）
    entry_price: float  # 开仓价格
    entry_time: datetime  # 开仓时间
    current_price: float  # 当前价格
    
    def __init__(
        self,
        direction: int = 0,
        size: int = 0,
        entry_price: float = 0.0,
        entry_time: Optional[datetime] = None,
        current_price: float = 0.0
    ):
        self.direction = direction
        self.size = size
        self.entry_price = entry_price
        self.entry_time = entry_time or datetime.now()
        self.current_price = current_price
    
    @property
    def is_long(self) -> bool:
        """是否持有多头"""
        return self.direction > 0 and self.size > 0
    
    @property
    def is_short(self) -> bool:
        """是否持有空头"""
        return self.direction < 0 and self.size > 0
    
    @property
    def is_empty(self) -> bool:
        """是否空仓"""
        return self.size == 0
    
    @property
    def market_value(self) -> float:
        """持仓市值"""
        return abs(self.size) * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        if self.size == 0:
            return 0.0
        
        if self.direction > 0:  # 多头
            return (self.current_price - self.entry_price) * self.size
        else:  # 空头
            return (self.entry_price - self.current_price) * abs(self.size)
    
    @property
    def unrealized_pnl_ratio(self) -> float:
        """未实现盈亏比例"""
        if self.entry_price == 0:
            return 0.0
        return self.unrealized_pnl / (self.entry_price * abs(self.size))
    
    def update_price(self, price: float):
        """更新当前价格"""
        self.current_price = price
    
    def add_position(
        self,
        direction: int,
        size: int,
        price: float,
        time: Optional[datetime] = None
    ):
        """增加持仓"""
        if self.size == 0:
            # 空仓，直接开仓
            self.direction = direction
            self.size = size
            self.entry_price = price
            self.entry_time = time or datetime.now()
            self.current_price = price
        elif self.direction == direction:
            # 同向加仓，计算加权平均开仓价
            total_cost = self.entry_price * abs(self.size) + price * size
            self.size += size if direction > 0 else -size
            self.entry_price = total_cost / abs(self.size) if self.size != 0 else 0.0
            self.current_price = price
        else:
            # 反向开仓，先平仓再开仓
            if abs(size) >= abs(self.size):
                # 完全反向，平掉所有持仓并开新仓
                self.direction = direction
                self.size = size - abs(self.size) if direction > 0 else -(abs(self.size) - size)
                self.entry_price = price
                self.entry_time = time or datetime.now()
                self.current_price = price
            else:
                # 部分反向，减少持仓
                self.size += size if direction > 0 else -size
                self.current_price = price
    
    def reduce_position(self, size: int, price: float):
        """减少持仓"""
        if self.size == 0:
            return
        
        reduce_size = min(abs(self.size), size)
        if self.direction > 0:
            self.size -= reduce_size
        else:
            self.size += reduce_size
        
        self.current_price = price
        
        if self.size == 0:
            self.direction = 0
            self.entry_price = 0.0
    
    def close_position(self, price: float):
        """平仓"""
        pnl = self.unrealized_pnl
        self.direction = 0
        self.size = 0
        self.entry_price = 0.0
        self.current_price = price
        return pnl
    
    def __repr__(self) -> str:
        direction_str = "多头" if self.is_long else ("空头" if self.is_short else "空仓")
        return f"Position({direction_str}, {abs(self.size)}手, 开仓价={self.entry_price:.2f}, 当前价={self.current_price:.2f}, 盈亏={self.unrealized_pnl:.2f})"








