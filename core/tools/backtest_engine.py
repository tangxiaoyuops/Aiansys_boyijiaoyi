"""
大宗商品策略回测引擎
实现历史数据回测、风险指标计算
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from core.models.strategy_models import BacktestResult, RiskMetrics, StrategySignal


class Trade:
    """交易记录"""
    def __init__(
        self,
        entry_time: str,
        exit_time: str,
        direction: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        pnl: float,
        commission: float
    ):
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.position_size = position_size
        self.pnl = pnl
        self.commission = commission
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "position_size": self.position_size,
            "pnl": self.pnl,
            "commission": self.commission
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self,
        initial_capital: float = 1000000.0,
        commission_rate: float = 0.0001,
        slippage: float = 0.0
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
    
    def backtest(
        self,
        strategy_signals: List[StrategySignal],
        price_data: List[Dict[str, Any]],
        high_data: Optional[List[float]] = None,
        low_data: Optional[List[float]] = None
    ) -> BacktestResult:
        """
        执行回测
        
        Args:
            strategy_signals: 策略信号列表
            price_data: 价格数据 [{"date": "YYYY-MM-DD", "close": 100.0}]
            high_data: 最高价数据（可选）
            low_data: 最低价数据（可选）
        
        Returns:
            BacktestResult: 回测结果
        """
        print(f"[回测引擎] 开始回测，策略数量: {len(strategy_signals)}")
        
        if not price_data:
            raise ValueError("价格数据不能为空")
        
        capital = self.initial_capital
        position = 0.0
        trades = []
        equity_curve = [capital]
        drawdown_curve = [0.0]
        peak_equity = capital
        
        current_trade = None
        entry_date = None
        
        for i, price_point in enumerate(price_data):
            date = price_point["date"]
            close = price_point["close"]
            high = price_point.get("high", close)
            low = price_point.get("low", close)
            
            if current_trade:
                current_trade["duration"] += 1
                
                pnl = 0.0
                should_close = False
                
                if current_trade["direction"] == "long":
                    if low <= current_trade["stop_loss"]:
                        pnl = (current_trade["stop_loss"] - current_trade["entry_price"]) * current_trade["position_size"]
                        should_close = True
                    elif high >= current_trade["target_price"]:
                        pnl = (current_trade["target_price"] - current_trade["entry_price"]) * current_trade["position_size"]
                        should_close = True
                    else:
                        pnl = (close - current_trade["entry_price"]) * current_trade["position_size"]
                else:
                    if high >= current_trade["stop_loss"]:
                        pnl = (current_trade["entry_price"] - current_trade["stop_loss"]) * current_trade["position_size"]
                        should_close = True
                    elif low <= current_trade["target_price"]:
                        pnl = (current_trade["entry_price"] - current_trade["target_price"]) * current_trade["position_size"]
                        should_close = True
                    else:
                        pnl = (current_trade["entry_price"] - close) * current_trade["position_size"]
                
                commission = abs(pnl) * self.commission_rate
                net_pnl = pnl - commission
                
                capital += net_pnl
                
                if should_close or i == len(price_data) - 1:
                    trade = Trade(
                        entry_time=entry_date,
                        exit_time=date,
                        direction=current_trade["direction"],
                        entry_price=current_trade["entry_price"],
                        exit_price=current_trade["stop_loss"] if should_close and (current_trade["direction"] == "long" and low <= current_trade["stop_loss"]) or (current_trade["direction"] == "short" and high >= current_trade["stop_loss"]) else (current_trade["target_price"] if should_close else close),
                        position_size=current_trade["position_size"],
                        pnl=net_pnl,
                        commission=commission
                    )
                    trades.append(trade)
                    current_trade = None
            
            for signal in strategy_signals:
                if current_trade is None and self._should_execute_signal(signal, date):
                    position_size = self._calculate_position_size(
                        capital, close, signal["stop_loss"], signal["direction"]
                    )
                    
                    current_trade = {
                        "direction": signal["direction"],
                        "entry_price": close,
                        "stop_loss": signal["stop_loss"],
                        "target_price": signal["target_price"],
                        "position_size": position_size,
                        "duration": 0
                    }
                    entry_date = date
                    break
            
            equity_curve.append(capital)
            
            if capital > peak_equity:
                peak_equity = capital
            
            drawdown = (peak_equity - capital) / peak_equity * 100
            drawdown_curve.append(drawdown)
        
        if current_trade:
            trade = Trade(
                entry_time=entry_date,
                exit_time=price_data[-1]["date"],
                direction=current_trade["direction"],
                entry_price=current_trade["entry_price"],
                exit_price=price_data[-1]["close"],
                position_size=current_trade["position_size"],
                pnl=0.0,
                commission=0.0
            )
            trades.append(trade)
        
        result = self._calculate_backtest_metrics(
            trades, equity_curve, drawdown_curve, price_data
        )
        
        print(f"[回测引擎] 回测完成，总收益率: {result['total_return']:.2f}%")
        return result
    
    def _should_execute_signal(self, signal: StrategySignal, current_date: str) -> bool:
        """判断是否应该执行信号"""
        signal_date = signal.get("generated_at", "")
        if not signal_date:
            return False
        
        signal_datetime = datetime.fromisoformat(signal_date.replace("Z", "+00:00"))
        current_datetime = datetime.fromisoformat(current_date)
        
        return signal_datetime <= current_datetime
    
    def _calculate_position_size(
        self,
        capital: float,
        current_price: float,
        stop_loss: float,
        direction: str
    ) -> float:
        """
        计算仓位大小
        
        Args:
            capital: 当前资金
            current_price: 当前价格
            stop_loss: 止损价格
            direction: 方向
        
        Returns:
            仓位大小
        """
        risk_ratio = 0.02  # 单笔风险2%
        
        if direction == "long":
            risk_per_unit = abs(current_price - stop_loss)
        else:
            risk_per_unit = abs(stop_loss - current_price)
        
        if risk_per_unit == 0:
            return 0.0
        
        risk_amount = capital * risk_ratio
        position_size = risk_amount / risk_per_unit
        
        return position_size
    
    def _calculate_backtest_metrics(
        self,
        trades: List[Trade],
        equity_curve: List[float],
        drawdown_curve: List[float],
        price_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算回测指标
        
        Args:
            trades: 交易列表
            equity_curve: 净值曲线
            drawdown_curve: 回撤曲线
            price_data: 价格数据
        
        Returns:
            回测指标字典
        """
        if not trades:
            return {
                "total_return": 0.0,
                "annual_return": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "trade_count": 0
            }
        
        final_capital = equity_curve[-1]
        total_return = (final_capital - self.initial_capital) / self.initial_capital * 100
        
        days = len(price_data)
        annual_return = (final_capital / self.initial_capital) ** (365.0 / days) - 1
        
        max_drawdown = max(drawdown_curve)
        
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i - 1] > 0:
                returns.append((equity_curve[i] - equity_curve[i - 1]) / equity_curve[i - 1])
        
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        trade_durations = [t.duration for t in trades]
        avg_trade_duration = np.mean(trade_durations) if trade_durations else 0
        
        best_trade = max((t.pnl for t in trades)) if trades else 0
        worst_trade = min((t.pnl for t in trades)) if trades else 0
        
        return {
            "strategy_id": "",
            "start_date": price_data[0]["date"],
            "end_date": price_data[-1]["date"],
            "initial_capital": self.initial_capital,
            "final_capital": final_capital,
            "total_return": total_return,
            "annual_return": annual_return * 100,
            "volatility": std_return * 100 if returns else 0,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sharpe_ratio * 0.9,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "trade_count": len(trades),
            "avg_trade_duration": avg_trade_duration,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "equity_curve": equity_curve,
            "drawdown_curve": drawdown_curve,
            "trades": [t.to_dict() for t in trades]
        }
    
    def calculate_risk_metrics(
        self,
        returns: List[float],
        confidence_level: float = 0.95
    ) -> RiskMetrics:
        """
        计算风险指标
        
        Args:
            returns: 收益率列表
            confidence_level: 置信水平
        
        Returns:
            RiskMetrics: 风险指标
        """
        if not returns:
            return RiskMetrics(
                var_95=0.0,
                var_99=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                volatility=0.0,
                beta=None,
                alpha=None,
                information_ratio=None
            )
        
        returns_array = np.array(returns)
        
        var_95 = np.percentile(returns_array, (1 - confidence_level) * 100)
        var_99 = np.percentile(returns_array, (1 - 0.99) * 100)
        
        volatility = np.std(returns_array)
        
        avg_return = np.mean(returns_array)
        sharpe_ratio = avg_return / volatility * np.sqrt(252) if volatility > 0 else 0
        
        downside_returns = returns_array[returns_array < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino_ratio = avg_return / downside_std * np.sqrt(252) if downside_std > 0 else 0
        
        max_drawdown = 0.0
        peak = 0.0
        cumulative = 0.0
        for r in returns:
            cumulative += r
            if cumulative > peak:
                peak = cumulative
            drawdown = (peak - cumulative) / peak * 100 if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        calmar_ratio = avg_return * 252 / max_drawdown if max_drawdown > 0 else 0
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            volatility=volatility,
            beta=None,
            alpha=None,
            information_ratio=None
        )


def create_backtest_engine(
    initial_capital: float = 1000000.0,
    commission_rate: float = 0.0001
) -> BacktestEngine:
    """创建回测引擎实例"""
    return BacktestEngine(initial_capital, commission_rate)
