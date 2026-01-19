"""
风险指标计算
风险类指标
"""
from typing import Dict, Any
import numpy as np


class RiskMetrics:
    """风险指标计算器"""
    
    def __init__(self, equity_curve: np.ndarray):
        """
        初始化
        
        Args:
            equity_curve: 权益曲线
        """
        self.equity_curve = equity_curve
        
        # 计算收益率序列
        if len(equity_curve) > 1:
            self.returns = np.diff(equity_curve) / equity_curve[:-1]
        else:
            self.returns = np.array([])
    
    def max_drawdown(self) -> Dict[str, float]:
        """
        计算最大回撤及相关指标
        
        Returns:
            {
                'max_drawdown': 最大回撤百分比,
                'max_drawdown_duration': 最大回撤持续天数,
                'current_drawdown': 当前回撤,
                'drawdown_series': 回撤序列
            }
        """
        if len(self.equity_curve) == 0:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_duration': 0,
                'current_drawdown': 0.0,
                'drawdown_series': []
            }
        
        cumulative = np.maximum.accumulate(self.equity_curve)
        drawdown = (self.equity_curve - cumulative) / cumulative
        
        max_dd = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)
        
        # 计算回撤持续时间
        peak_idx = np.argmax(self.equity_curve[:max_dd_idx+1])
        dd_duration = max_dd_idx - peak_idx
        
        # 当前回撤
        current_dd = drawdown[-1]
        
        return {
            'max_drawdown': float(max_dd * 100),  # 百分比
            'max_drawdown_duration': int(dd_duration),
            'current_drawdown': float(current_dd * 100),
            'drawdown_series': drawdown.tolist()
        }
    
    def volatility(self, annualize: bool = True, periods_per_year: int = 252) -> float:
        """
        计算波动率
        
        Args:
            annualize: 是否年化
            periods_per_year: 每年交易周期数
            
        Returns:
            波动率（百分比）
        """
        if len(self.returns) == 0:
            return 0.0
        
        vol = np.std(self.returns)
        if annualize:
            vol = vol * np.sqrt(periods_per_year)
        
        return float(vol * 100)
    
    def downside_deviation(self, target_return: float = 0.0, annualize: bool = True, periods_per_year: int = 252) -> float:
        """
        计算下行偏差（用于Sortino比率）
        
        Args:
            target_return: 目标收益率
            annualize: 是否年化
            periods_per_year: 每年交易周期数
            
        Returns:
            下行偏差（百分比）
        """
        if len(self.returns) == 0:
            return 0.0
        
        downside_returns = self.returns[self.returns < target_return]
        if len(downside_returns) == 0:
            return 0.0
        
        dd = np.std(downside_returns)
        if annualize:
            dd = dd * np.sqrt(periods_per_year)
        
        return float(dd * 100)
    
    def value_at_risk(self, confidence: float = 0.95) -> float:
        """
        计算VaR（Value at Risk）
        
        Args:
            confidence: 置信水平（如0.95表示95%置信度）
            
        Returns:
            VaR值（百分比）
        """
        if len(self.returns) == 0:
            return 0.0
        
        var = np.percentile(self.returns, (1 - confidence) * 100)
        return float(var * 100)
    
    def conditional_var(self, confidence: float = 0.95) -> float:
        """
        计算CVaR（条件风险价值，期望损失）
        
        Args:
            confidence: 置信水平
            
        Returns:
            CVaR值（百分比）
        """
        if len(self.returns) == 0:
            return 0.0
        
        var = np.percentile(self.returns, (1 - confidence) * 100)
        cvar = self.returns[self.returns <= var].mean()
        
        return float(cvar * 100)
    
    def ulcer_index(self) -> float:
        """
        计算溃疡指数（Ulcer Index）
        衡量回撤的深度和持续时间
        
        Returns:
            溃疡指数
        """
        if len(self.equity_curve) == 0:
            return 0.0
        
        cumulative = np.maximum.accumulate(self.equity_curve)
        drawdown = (self.equity_curve - cumulative) / cumulative
        return float(np.sqrt(np.mean(drawdown ** 2)) * 100)








