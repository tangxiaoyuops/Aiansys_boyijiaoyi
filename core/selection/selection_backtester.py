"""
选股回测框架
对选股策略进行历史回测验证
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from .selection_config import SelectionConfig
from .stock_selection_strategy import StockSelectionStrategy, SelectionResult

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    """回测交易记录"""
    code: str
    name: str
    buy_date: str
    buy_price: float
    buy_reason: str
    sell_date: Optional[str] = None
    sell_price: Optional[float] = None
    sell_reason: Optional[str] = None
    shares: int = 0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    holding_days: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "buy_date": self.buy_date,
            "buy_price": self.buy_price,
            "buy_reason": self.buy_reason,
            "sell_date": self.sell_date,
            "sell_price": self.sell_price,
            "sell_reason": self.sell_reason,
            "shares": self.shares,
            "pnl": self.pnl,
            "pnl_pct": self.pnl_pct,
            "holding_days": self.holding_days
        }


@dataclass
class BacktestPerformance:
    """回测绩效"""
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_holding_days: float
    avg_profit: float
    avg_loss: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "avg_holding_days": self.avg_holding_days,
            "avg_profit": self.avg_profit,
            "avg_loss": self.avg_loss
        }


@dataclass
class SelectionBacktestResult:
    """选股回测结果"""
    performance: BacktestPerformance
    trades: List[BacktestTrade]
    equity_curve: List[float]
    daily_stats: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "performance": self.performance.to_dict(),
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": self.equity_curve,
            "daily_stats": self.daily_stats
        }


class SelectionBacktester:
    """选股回测框架"""
    
    def __init__(self, config: Optional[SelectionConfig] = None):
        """
        初始化选股回测器
        
        Args:
            config: 选股配置
        """
        self.config = config or SelectionConfig()
        self.selection_strategy = StockSelectionStrategy(self.config)
    
    def run_backtest(
        self,
        codes: List[str],
        start_date: str,
        end_date: str,
        rebalance_freq: str = "weekly"  # weekly, monthly
    ) -> SelectionBacktestResult:
        """
        运行选股回测
        
        Args:
            codes: 股票池代码列表
            start_date: 回测开始日期
            end_date: 回测结束日期
            rebalance_freq: 再平衡频率(weekly/monthly)
        
        Returns:
            回测结果
        """
        logger.info(f"[SelectionBacktester] 开始回测: {start_date} 至 {end_date}")
        
        # 初始化账户
        capital = self.config.initial_capital
        positions: Dict[str, Dict[str, Any]] = {}  # code -> position info
        trades: List[BacktestTrade] = []
        equity_curve: List[float] = [capital]
        daily_stats: List[Dict[str, Any]] = []
        
        # 生成再平衡日期
        rebalance_dates = self._generate_rebalance_dates(
            start_date, 
            end_date, 
            rebalance_freq
        )
        
        # 遍历每个交易日
        current_date = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 更新持仓市值
            capital, positions = self._update_positions(
                capital, 
                positions, 
                date_str
            )
            
            # 检查是否需要再平衡
            if date_str in rebalance_dates:
                logger.info(f"[SelectionBacktester] 再平衡日期: {date_str}")
                
                # 卖出信号检查
                positions, trades = self._check_sell_signals(
                    positions,
                    trades,
                    date_str
                )
                
                # 选股
                selection_result = self._run_selection_on_date(
                    codes,
                    date_str
                )
                
                # 买入新股票
                positions, capital = self._execute_buy_signals(
                    selection_result,
                    positions,
                    capital,
                    date_str
                )
            
            # 记录每日统计
            total_value = capital + sum(
                p['shares'] * p['current_price'] 
                for p in positions.values()
            )
            
            equity_curve.append(total_value)
            
            daily_stats.append({
                "date": date_str,
                "cash": capital,
                "position_value": total_value - capital,
                "total_value": total_value,
                "position_count": len(positions)
            })
            
            # 下一个交易日
            current_date += timedelta(days=1)
            # 跳过周末
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)
        
        # 平仓所有持仓
        positions, trades = self._close_all_positions(
            positions,
            trades,
            end_date
        )
        
        # 计算绩效指标
        performance = self._calculate_performance(
            equity_curve,
            trades,
            start_date,
            end_date
        )
        
        logger.info(
            f"[SelectionBacktester] 回测完成: "
            f"总收益率{performance.total_return:.2f}%, "
            f"最大回撤{performance.max_drawdown:.2f}%, "
            f"交易次数{performance.total_trades}"
        )
        
        return SelectionBacktestResult(
            performance=performance,
            trades=trades,
            equity_curve=equity_curve,
            daily_stats=daily_stats
        )
    
    def _generate_rebalance_dates(
        self,
        start_date: str,
        end_date: str,
        freq: str
    ) -> List[str]:
        """生成再平衡日期"""
        dates = []
        current = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        while current <= end:
            # 只在交易日再平衡
            if current.weekday() < 5:
                dates.append(current.strftime("%Y-%m-%d"))
            
            if freq == "weekly":
                current += timedelta(days=7)
            elif freq == "monthly":
                current += timedelta(days=30)
            else:
                current += timedelta(days=7)
        
        return dates
    
    def _update_positions(
        self,
        capital: float,
        positions: Dict[str, Dict[str, Any]],
        date_str: str
    ) -> Tuple[float, Dict[str, Dict[str, Any]]]:
        """更新持仓市值"""
        from core.tools.data_fetcher import fetch_stock_data
        
        for code, pos in positions.items():
            try:
                # 获取当日价格
                df = fetch_stock_data(code, days=10)
                if df is not None and len(df) > 0:
                    # 找到最近的交易日价格
                    last_date = df.iloc[-1]['date'] if 'date' in df.columns else df.index[-1]
                    if str(last_date)[:10] == date_str:
                        pos['current_price'] = float(df.iloc[-1]['close'])
            except:
                pass
        
        return capital, positions
    
    def _check_sell_signals(
        self,
        positions: Dict[str, Dict[str, Any]],
        trades: List[BacktestTrade],
        date_str: str
    ) -> Tuple[Dict[str, Dict[str, Any]], List[BacktestTrade]]:
        """检查卖出信号"""
        from core.tools.data_fetcher import fetch_stock_data
        from core.tools.technical_analyzer import detect_sell_signals
        
        positions_to_close = []
        
        for code, pos in positions.items():
            try:
                df = fetch_stock_data(code, days=self.config.data_days)
                if df is None:
                    continue
                
                # 检测卖点信号
                sell_signals = detect_sell_signals(
                    df, 
                    window=60, 
                    stage=pos.get('stage', 2)
                )
                
                # 检查是否有最近的卖点信号
                for signal in sell_signals:
                    signal_date = signal.get('date')
                    if signal_date and str(signal_date)[:10] == date_str:
                        # 卖出
                        positions_to_close.append(code)
                        
                        # 记录交易
                        current_price = float(df.iloc[-1]['close'])
                        buy_price = pos['buy_price']
                        shares = pos['shares']
                        
                        pnl = (current_price - buy_price) * shares
                        pnl_pct = (current_price - buy_price) / buy_price * 100
                        holding_days = (pd.to_datetime(date_str) - pd.to_datetime(pos['buy_date'])).days
                        
                        trade = BacktestTrade(
                            code=code,
                            name=pos['name'],
                            buy_date=pos['buy_date'],
                            buy_price=buy_price,
                            buy_reason=pos['buy_reason'],
                            sell_date=date_str,
                            sell_price=current_price,
                            sell_reason=signal.get('description', '卖点信号'),
                            shares=shares,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            holding_days=holding_days
                        )
                        
                        trades.append(trade)
                        break
                
                # 检查止损
                current_price = pos.get('current_price', pos['buy_price'])
                loss_pct = (current_price - pos['buy_price']) / pos['buy_price']
                
                if loss_pct <= -self.config.stop_loss_ratio:
                    positions_to_close.append(code)
                    
                    pnl = (current_price - pos['buy_price']) * pos['shares']
                    pnl_pct = loss_pct * 100
                    holding_days = (pd.to_datetime(date_str) - pd.to_datetime(pos['buy_date'])).days
                    
                    trade = BacktestTrade(
                        code=code,
                        name=pos['name'],
                        buy_date=pos['buy_date'],
                        buy_price=pos['buy_price'],
                        buy_reason=pos['buy_reason'],
                        sell_date=date_str,
                        sell_price=current_price,
                        sell_reason='止损',
                        shares=pos['shares'],
                        pnl=pnl,
                        pnl_pct=pnl_pct,
                        holding_days=holding_days
                    )
                    
                    trades.append(trade)
                
            except Exception as e:
                logger.error(f"[SelectionBacktester] 检查 {code} 卖出信号失败: {e}")
        
        # 移除已平仓的持仓
        for code in positions_to_close:
            if code in positions:
                del positions[code]
        
        return positions, trades
    
    def _run_selection_on_date(
        self,
        codes: List[str],
        date_str: str
    ) -> SelectionResult:
        """在指定日期运行选股"""
        # 注意:这里简化处理,实际应该模拟历史选股
        # 这里使用同步方法
        return self.selection_strategy.select_stocks_sync(codes)
    
    def _execute_buy_signals(
        self,
        selection_result: SelectionResult,
        positions: Dict[str, Dict[str, Any]],
        capital: float,
        date_str: str
    ) -> Tuple[Dict[str, Dict[str, Any]], float]:
        """执行买入信号"""
        for candidate in selection_result.top_candidates:
            # 检查是否已持仓
            if candidate.code in positions:
                continue
            
            # 检查资金是否足够
            if capital < candidate.suggested_amount:
                continue
            
            # 检查持仓数量是否已达上限
            if len(positions) >= self.config.max_stocks:
                break
            
            # 买入
            positions[candidate.code] = {
                'name': candidate.name,
                'buy_date': date_str,
                'buy_price': candidate.best_buy_point.price,
                'buy_reason': candidate.best_buy_point.reasoning,
                'shares': candidate.suggested_shares,
                'current_price': candidate.best_buy_point.price,
                'stage': candidate.stage
            }
            
            capital -= candidate.suggested_amount
            
            logger.info(
                f"[SelectionBacktester] 买入 {candidate.code} {candidate.name}: "
                f"价格{candidate.best_buy_point.price:.2f}, "
                f"股数{candidate.suggested_shares}, "
                f"原因{candidate.best_buy_point.reasoning}"
            )
        
        return positions, capital
    
    def _close_all_positions(
        self,
        positions: Dict[str, Dict[str, Any]],
        trades: List[BacktestTrade],
        end_date: str
    ) -> Tuple[Dict[str, Dict[str, Any]], List[BacktestTrade]]:
        """平仓所有持仓"""
        from core.tools.data_fetcher import fetch_stock_data
        
        for code, pos in positions.items():
            try:
                df = fetch_stock_data(code, days=10)
                if df is not None and len(df) > 0:
                    current_price = float(df.iloc[-1]['close'])
                    
                    pnl = (current_price - pos['buy_price']) * pos['shares']
                    pnl_pct = (current_price - pos['buy_price']) / pos['buy_price'] * 100
                    holding_days = (pd.to_datetime(end_date) - pd.to_datetime(pos['buy_date'])).days
                    
                    trade = BacktestTrade(
                        code=code,
                        name=pos['name'],
                        buy_date=pos['buy_date'],
                        buy_price=pos['buy_price'],
                        buy_reason=pos['buy_reason'],
                        sell_date=end_date,
                        sell_price=current_price,
                        sell_reason='回测结束平仓',
                        shares=pos['shares'],
                        pnl=pnl,
                        pnl_pct=pnl_pct,
                        holding_days=holding_days
                    )
                    
                    trades.append(trade)
            except Exception as e:
                logger.error(f"[SelectionBacktester] 平仓 {code} 失败: {e}")
        
        positions.clear()
        return positions, trades
    
    def _calculate_performance(
        self,
        equity_curve: List[float],
        trades: List[BacktestTrade],
        start_date: str,
        end_date: str
    ) -> BacktestPerformance:
        """计算绩效指标"""
        # 总收益率
        initial_capital = self.config.initial_capital
        final_capital = equity_curve[-1]
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        # 年化收益率
        days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        annual_return = (final_capital / initial_capital) ** (365.0 / days) - 1 if days > 0 else 0
        annual_return *= 100
        
        # 最大回撤
        peak = equity_curve[0]
        max_dd = 0.0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # 夏普比率
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                returns.append((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
        
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 胜率
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        # 盈亏比
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # 平均持仓天数
        avg_holding_days = np.mean([t.holding_days for t in trades]) if trades else 0
        
        # 平均盈利和亏损
        avg_profit = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        return BacktestPerformance(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_holding_days=avg_holding_days,
            avg_profit=avg_profit,
            avg_loss=avg_loss
        )
