"""
风险管理模块
检查保证金率、强平条件等
"""
from typing import Dict, Any
from dataclasses import dataclass

from .portfolio import Portfolio


@dataclass
class RiskConfig:
    """风险配置"""
    max_margin_rate: float = 0.8  # 最大保证金率（80%）
    max_position_size: int = 10  # 最大持仓量（手数）
    max_drawdown: float = 0.5  # 最大回撤限制（50%）
    stop_loss_ratio: float = 0.05  # 止损比例（5%）
    take_profit_ratio: float = 0.10  # 止盈比例（10%）
    force_liquidation_margin_rate: float = 0.9  # 强平保证金率（90%）


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: RiskConfig):
        """
        初始化风险管理器
        
        Args:
            config: 风险配置
        """
        self.config = config
    
    def check_risk(self, portfolio: Portfolio) -> Dict[str, Any]:
        """
        检查风险
        
        Args:
            portfolio: 投资组合
            
        Returns:
            {
                'passed': bool,  # 是否通过检查
                'warnings': List[str],  # 警告信息
                'should_force_liquidation': bool,  # 是否应该强平
            }
        """
        warnings = []
        should_force_liquidation = False
        
        # 检查保证金率
        if portfolio.total_equity > 0:
            margin_rate = portfolio.margin_used / portfolio.total_equity
            
            if margin_rate > self.config.force_liquidation_margin_rate:
                should_force_liquidation = True
                warnings.append(f"保证金率过高({margin_rate:.2%})，触发强平")
            elif margin_rate > self.config.max_margin_rate:
                warnings.append(f"保证金率过高({margin_rate:.2%})，接近限制")
        
        # 检查持仓量
        if abs(portfolio.position.size) > self.config.max_position_size:
            warnings.append(f"持仓量({abs(portfolio.position.size)})超过限制({self.config.max_position_size})")
        
        # 检查回撤
        if len(portfolio.equity_history) > 1:
            max_equity = max(portfolio.equity_history)
            current_equity = portfolio.total_equity
            drawdown = (max_equity - current_equity) / max_equity if max_equity > 0 else 0
            
            if drawdown > self.config.max_drawdown:
                warnings.append(f"回撤({drawdown:.2%})超过限制({self.config.max_drawdown:.2%})")
        
        # 检查止损止盈
        if not portfolio.position.is_empty:
            pnl_ratio = portfolio.position.unrealized_pnl_ratio
            
            if pnl_ratio <= -self.config.stop_loss_ratio:
                warnings.append(f"触发止损({pnl_ratio:.2%})")
            elif pnl_ratio >= self.config.take_profit_ratio:
                warnings.append(f"触发止盈({pnl_ratio:.2%})")
        
        passed = not should_force_liquidation and len(warnings) == 0
        
        return {
            'passed': passed,
            'warnings': warnings,
            'should_force_liquidation': should_force_liquidation
        }
    
    def should_stop_loss(self, portfolio: Portfolio) -> bool:
        """检查是否应该止损"""
        if portfolio.position.is_empty:
            return False
        
        pnl_ratio = portfolio.position.unrealized_pnl_ratio
        return pnl_ratio <= -self.config.stop_loss_ratio
    
    def should_take_profit(self, portfolio: Portfolio) -> bool:
        """检查是否应该止盈"""
        if portfolio.position.is_empty:
            return False
        
        pnl_ratio = portfolio.position.unrealized_pnl_ratio
        return pnl_ratio >= self.config.take_profit_ratio
    
    def get_force_liquidation_signal(self, portfolio: Portfolio) -> Dict[str, Any]:
        """
        获取强平信号
        
        Args:
            portfolio: 投资组合
            
        Returns:
            强平信号或None
        """
        risk_check = self.check_risk(portfolio)
        
        if risk_check['should_force_liquidation'] and not portfolio.position.is_empty:
            return {
                'action': 'CLOSE_ALL',
                'size': abs(portfolio.position.size),
                'reason': '强平：保证金率过高'
            }
        
        return None









