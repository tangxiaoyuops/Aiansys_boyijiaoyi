"""
绩效指标计算
收益类指标
"""
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime


class PerformanceMetrics:
    """绩效指标计算器"""
    
    def __init__(self, equity_curve: np.ndarray, initial_capital: float):
        """
        初始化
        
        Args:
            equity_curve: 权益曲线
            initial_capital: 初始资金
        """
        self.equity_curve = equity_curve
        self.initial_capital = initial_capital
        
        # 计算收益率序列
        if len(equity_curve) > 1:
            self.returns = np.diff(equity_curve) / equity_curve[:-1]
        else:
            self.returns = np.array([])
    
    def total_return(self) -> float:
        """
        计算总收益率
        
        Returns:
            总收益率（百分比）
        """
        if len(self.equity_curve) == 0:
            return 0.0
        
        total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital
        return float(total_return * 100)
    
    def annual_return(self, periods_per_year: int = 252) -> float:
        """
        计算年化收益率
        
        Args:
            periods_per_year: 每年交易周期数（日线252，小时线252*4）
            
        Returns:
            年化收益率（百分比）
        """
        if len(self.equity_curve) < 2:
            return 0.0
        
        total_return = self.equity_curve[-1] / self.initial_capital
        num_periods = len(self.equity_curve) - 1
        
        if num_periods == 0:
            return 0.0
        
        # 年化收益率 = (1 + 总收益率)^(252/交易天数) - 1
        years = num_periods / periods_per_year
        annual_return = (total_return ** (1 / years) - 1) if years > 0 else 0.0
        
        return float(annual_return * 100)
    
    def monthly_returns(self) -> List[Dict[str, Any]]:
        """
        计算月度收益率
        
        Returns:
            月度收益率列表
        """
        if len(self.equity_curve) < 2:
            return []
        
        # 这里简化处理，假设equity_curve是按日期顺序的
        # 实际应该根据日期分组计算月度收益
        # 为了简化，我们按固定间隔计算
        
        monthly_returns = []
        period_length = max(1, len(self.equity_curve) // 12)  # 大约每月的数据点数
        
        for i in range(0, len(self.equity_curve) - 1, period_length):
            if i + period_length < len(self.equity_curve):
                start_equity = self.equity_curve[i]
                end_equity = self.equity_curve[min(i + period_length, len(self.equity_curve) - 1)]
                monthly_return = (end_equity - start_equity) / start_equity if start_equity > 0 else 0.0
                
                monthly_returns.append({
                    'period': i // period_length + 1,
                    'return': float(monthly_return * 100)
                })
        
        return monthly_returns
    
    def sharpe_ratio(self, volatility: float, risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率
        
        Args:
            volatility: 年化波动率（百分比）
            risk_free_rate: 无风险利率（年化，默认3%）
            
        Returns:
            夏普比率
        """
        if volatility == 0:
            return 0.0
        
        annual_return = self.annual_return()
        sharpe = (annual_return - risk_free_rate * 100) / volatility
        
        return float(sharpe)
    
    def sortino_ratio(self, downside_deviation: float, target_return: float = 0.0) -> float:
        """
        计算索提诺比率
        
        Args:
            downside_deviation: 下行偏差（百分比）
            target_return: 目标收益率（年化，百分比）
            
        Returns:
            索提诺比率
        """
        if downside_deviation == 0:
            return 0.0
        
        annual_return = self.annual_return()
        sortino = (annual_return - target_return) / downside_deviation
        
        return float(sortino)
    
    def calmar_ratio(self, max_drawdown: float) -> float:
        """
        计算卡玛比率
        
        Args:
            max_drawdown: 最大回撤（百分比）
            
        Returns:
            卡玛比率
        """
        if max_drawdown == 0:
            return 0.0
        
        annual_return = self.annual_return()
        calmar = annual_return / abs(max_drawdown)
        
        return float(calmar)
    
    def information_ratio(self, benchmark_returns: np.ndarray) -> float:
        """
        计算信息比率
        
        Args:
            benchmark_returns: 基准收益率序列
            
        Returns:
            信息比率
        """
        if len(self.returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        min_len = min(len(self.returns), len(benchmark_returns))
        excess_returns = self.returns[:min_len] - benchmark_returns[:min_len]
        
        if len(excess_returns) == 0:
            return 0.0
        
        mean_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns)
        
        if std_excess == 0:
            return 0.0
        
        # 年化
        information_ratio = mean_excess / std_excess * np.sqrt(252)
        
        return float(information_ratio)













