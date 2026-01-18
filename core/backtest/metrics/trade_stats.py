"""
交易统计指标
"""
from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta

# Trade类在portfolio模块中定义，这里使用类型提示
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..portfolio import Trade


class TradeStatistics:
    """交易统计计算器"""
    
    def __init__(self, trade_log: List[Any]):
        """
        初始化
        
        Args:
            trade_log: 交易记录列表（Trade对象或字典）
        """
        self.trade_log = trade_log
    
    def _get_closed_trades(self) -> List[Dict[str, Any]]:
        """获取已平仓的交易对（开仓-平仓）"""
        closed_trades = []
        open_trades = {}  # {direction: [trades]}
        
        for trade in self.trade_log:
            # 处理Trade对象或字典
            if isinstance(trade, dict):
                action = trade.get('action', '')
                direction = trade.get('direction', 0)
                time = trade.get('time', datetime.now())
                equity_before = trade.get('equity_before', 0)
                equity_after = trade.get('equity_after', 0)
            else:
                action = trade.action
                direction = trade.direction
                time = trade.time
                equity_before = trade.equity_before
                equity_after = trade.equity_after
            if action in ['OPEN_LONG', 'OPEN_SHORT']:
                if direction not in open_trades:
                    open_trades[direction] = []
                open_trades[direction].append(trade)
            elif action in ['CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL']:
                close_direction = -direction if action == 'CLOSE_ALL' else -direction
                if close_direction in open_trades and open_trades[close_direction]:
                    open_trade = open_trades[close_direction].pop(0)
                    # 获取开仓和平仓交易的权益
                    if isinstance(open_trade, dict):
                        open_equity_after = open_trade.get('equity_after', 0)  # 开仓后的权益
                        open_time = open_trade.get('time', datetime.now())
                    else:
                        open_equity_after = open_trade.equity_after  # 开仓后的权益
                        open_time = open_trade.time
                    
                    # 计算单笔交易盈亏：平仓后权益 - 开仓后权益
                    # 因为平仓时已经将已实现盈亏加到了cash中，所以直接用平仓后权益减去开仓后权益即可
                    trade_pnl = equity_after - open_equity_after
                    
                    closed_trades.append({
                        'open': open_trade,
                        'close': trade,
                        'pnl': trade_pnl,
                        'duration': (time - open_time).total_seconds() / 86400 if isinstance(time, datetime) and isinstance(open_time, datetime) else 0  # 天数
                    })
        
        return closed_trades
    
    def win_rate(self) -> float:
        """
        计算胜率
        
        Returns:
            胜率（百分比）
        """
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        winning_trades = sum(1 for t in closed_trades if t['pnl'] > 0)
        win_rate = winning_trades / len(closed_trades)
        
        return float(win_rate * 100)
    
    def profit_factor(self) -> float:
        """
        计算盈利因子（总盈利 / 总亏损）
        
        Returns:
            盈利因子
        """
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        total_profit = sum(t['pnl'] for t in closed_trades if t['pnl'] > 0)
        total_loss = abs(sum(t['pnl'] for t in closed_trades if t['pnl'] < 0))
        
        if total_loss == 0:
            # 如果没有亏损，返回一个很大的值而不是inf（JSON不支持inf）
            # 使用999.99表示"无限大"的盈利因子
            return 999.99 if total_profit > 0 else 0.0
        
        return float(total_profit / total_loss)
    
    def average_trade(self) -> float:
        """
        计算平均交易盈亏
        
        Returns:
            平均交易盈亏
        """
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        avg_pnl = np.mean([t['pnl'] for t in closed_trades])
        return float(avg_pnl)
    
    def total_trades(self) -> int:
        """
        计算总交易次数
        
        Returns:
            总交易次数
        """
        return len(self._get_closed_trades())
    
    def average_holding_period(self) -> float:
        """
        计算平均持仓周期（天数）
        
        Returns:
            平均持仓周期
        """
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        avg_duration = np.mean([t['duration'] for t in closed_trades])
        return float(avg_duration)
    
    def largest_winning_trade(self) -> float:
        """最大盈利交易"""
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        return float(max((t['pnl'] for t in closed_trades), default=0.0))
    
    def largest_losing_trade(self) -> float:
        """最大亏损交易"""
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        return float(min((t['pnl'] for t in closed_trades), default=0.0))
    
    def profit_loss_ratio(self) -> float:
        """
        计算盈亏比（平均盈利 / 平均亏损）
        
        Returns:
            盈亏比
        """
        closed_trades = self._get_closed_trades()
        if len(closed_trades) == 0:
            return 0.0
        
        winning_trades = [t['pnl'] for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t['pnl'] for t in closed_trades if t['pnl'] < 0]
        
        if len(winning_trades) == 0 or len(losing_trades) == 0:
            return 0.0
        
        avg_win = np.mean(winning_trades)
        avg_loss = abs(np.mean(losing_trades))
        
        if avg_loss == 0:
            return 0.0
        
        return float(avg_win / avg_loss)

