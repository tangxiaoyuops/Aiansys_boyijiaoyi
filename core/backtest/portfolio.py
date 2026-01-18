"""
组合管理模块
管理回测过程中的资金、持仓和权益
"""
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

if TYPE_CHECKING:
    from datetime import datetime as dt

from .position import Position


@dataclass
class Trade:
    """交易记录"""
    time: datetime
    action: str  # 'OPEN_LONG', 'OPEN_SHORT', 'CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL'
    direction: int  # 1=多头, -1=空头
    size: int  # 交易数量
    price: float  # 成交价格
    commission: float  # 手续费
    slippage: float  # 滑点成本
    reason: str  # 交易原因
    equity_before: float  # 交易前权益
    equity_after: float  # 交易后权益


class Portfolio:
    """投资组合"""
    
    def __init__(self, initial_capital: float):
        """
        初始化组合
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital  # 可用资金
        self.position = Position()  # 持仓
        self.trade_log: List[Trade] = []  # 交易记录
        self.equity_history: List[float] = [initial_capital]  # 权益历史
        self.daily_stats: List[Dict[str, Any]] = []  # 每日统计
        
    @property
    def total_equity(self) -> float:
        """
        总权益 = 账户余额 + 持仓市值
        
        账户余额（cash）：剩余可用现金
        持仓市值（market_value）：持仓数量 × 当前价格
        
        注意：持仓市值已经包含了持仓成本，未实现盈亏已经体现在市值变化中
        """
        return self.cash + self.position.market_value
    
    @property
    def margin_used(self) -> float:
        """已用保证金"""
        if self.position.size == 0:
            return 0.0
        # 假设保证金率在外部配置中，这里只返回持仓市值
        return self.position.market_value
    
    @property
    def available_cash(self) -> float:
        """可用资金"""
        return self.cash
    
    def update_position_price(self, price: float):
        """更新持仓价格"""
        self.position.update_price(price)
    
    def get_total_equity(self, current_price: float) -> float:
        """获取总权益（使用指定价格）"""
        self.update_position_price(current_price)
        return self.total_equity
    
    def record_trade(
        self,
        action: str,
        direction: int,
        size: int,
        price: float,
        commission: float,
        slippage: float,
        reason: str,
        time: Optional[Any] = None  # 可以是datetime或pandas Timestamp
    ):
        """
        记录交易
        
        Args:
            action: 交易动作
            direction: 方向（1=多头, -1=空头）
            size: 数量
            price: 价格
            commission: 手续费
            slippage: 滑点成本
            reason: 交易原因
            time: 交易时间
        """
        equity_before = self.total_equity
        
        # 计算实际成交价格（考虑滑点）
        if direction > 0:  # 买入
            actual_price = price * (1 + slippage)
        else:  # 卖出
            actual_price = price * (1 - slippage)
        
        # 计算交易成本
        trade_cost = size * actual_price + commission
        
        # 更新持仓
        if action in ['OPEN_LONG', 'OPEN_SHORT']:
            self.position.add_position(direction, size, actual_price, time)
            self.cash -= trade_cost
        elif action in ['CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL']:
            # 平仓时：获得卖出现金，减去平仓手续费
            # 注意：close_position返回的是价格差异的盈亏，但我们需要的是卖出获得的现金
            position_size = abs(self.position.size) if self.position.size != 0 else size
            realized_pnl = self.position.close_position(actual_price)
            # 平仓时获得卖出现金：size * actual_price
            # 盈亏已经体现在价格差异中，但我们需要把卖出现金加入cash
            # 计算：卖出现金 = 持仓成本 + 价格差异盈亏
            # 但我们直接用卖出现金更简单
            sell_cash = position_size * actual_price
            self.cash += sell_cash
            self.cash -= commission  # 平仓手续费（印花税已包含在commission中）
        
        equity_after = self.total_equity
        
        # 处理时间（可能是pandas Timestamp）
        trade_time = time
        if trade_time is None:
            trade_time = datetime.now()
        elif hasattr(trade_time, 'to_pydatetime'):
            trade_time = trade_time.to_pydatetime()
        elif not isinstance(trade_time, datetime):
            trade_time = datetime.now()
        
        # 记录交易
        trade = Trade(
            time=trade_time,
            action=action,
            direction=direction,
            size=size,
            price=actual_price,
            commission=commission,
            slippage=slippage,
            reason=reason,
            equity_before=equity_before,
            equity_after=equity_after
        )
        self.trade_log.append(trade)
        
        return trade
    
    def record_daily_stat(self, date: Any, current_price: float):
        """记录每日统计"""
        self.update_position_price(current_price)
        
        # 处理日期（可能是pandas Timestamp）
        stat_date = date
        if hasattr(stat_date, 'to_pydatetime'):
            stat_date = stat_date.to_pydatetime()
        elif not isinstance(stat_date, datetime):
            stat_date = datetime.now()
        
        stat = {
            'date': stat_date,
            'equity': self.total_equity,
            'cash': self.cash,
            'position': self.position.size,
            'position_direction': self.position.direction,
            'entry_price': self.position.entry_price,
            'current_price': current_price,
            'unrealized_pnl': self.position.unrealized_pnl,
            'margin_used': self.margin_used,
            'margin_rate': self.margin_used / self.total_equity if self.total_equity > 0 else 0.0
        }
        self.daily_stats.append(stat)
        self.equity_history.append(self.total_equity)
        
        return stat
    
    def get_trade_log_df(self) -> pd.DataFrame:
        """获取交易记录DataFrame"""
        if not self.trade_log:
            return pd.DataFrame()
        
        data = []
        for trade in self.trade_log:
            data.append({
                'time': trade.time,
                'action': trade.action,
                'direction': trade.direction,
                'size': trade.size,
                'price': trade.price,
                'commission': trade.commission,
                'slippage': trade.slippage,
                'reason': trade.reason,
                'equity_before': trade.equity_before,
                'equity_after': trade.equity_after
            })
        
        return pd.DataFrame(data)
    
    def get_daily_stats_df(self) -> pd.DataFrame:
        """获取每日统计DataFrame"""
        if not self.daily_stats:
            return pd.DataFrame()
        
        return pd.DataFrame(self.daily_stats)
    
    def __repr__(self) -> str:
        return f"Portfolio(初始资金={self.initial_capital:.2f}, 现金={self.cash:.2f}, 权益={self.total_equity:.2f}, 持仓={self.position})"


