"""
仓位管理
"""
from typing import Optional
from .kelly import kelly_criterion, half_kelly_criterion


class PositionSizer:
    """仓位计算器"""
    
    @staticmethod
    def fixed_size(size: int) -> int:
        """固定仓位"""
        return size
    
    @staticmethod
    def percentage_of_equity(equity: float, percentage: float, price: float, contract_multiplier: int = 10) -> int:
        """
        按权益比例计算仓位
        
        Args:
            equity: 总权益
            percentage: 仓位比例（0-1）
            price: 价格
            contract_multiplier: 合约乘数
            
        Returns:
            手数
        """
        if price <= 0:
            return 0
        
        target_value = equity * percentage
        size = int(target_value / (price * contract_multiplier))
        return max(0, size)
    
    @staticmethod
    def kelly_size(
        equity: float,
        win_rate: float,
        profit_loss_ratio: float,
        price: float,
        contract_multiplier: int = 10,
        use_half_kelly: bool = True
    ) -> int:
        """
        使用凯利公式计算仓位
        
        Args:
            equity: 总权益
            win_rate: 胜率
            profit_loss_ratio: 盈亏比
            price: 价格
            contract_multiplier: 合约乘数
            use_half_kelly: 是否使用半凯利（更保守）
            
        Returns:
            手数
        """
        if price <= 0:
            return 0
        
        if use_half_kelly:
            kelly_ratio = half_kelly_criterion(win_rate, profit_loss_ratio)
        else:
            kelly_ratio = kelly_criterion(win_rate, profit_loss_ratio)
        
        # 限制最大仓位比例
        kelly_ratio = min(kelly_ratio, 0.25)  # 最多25%
        
        target_value = equity * kelly_ratio
        size = int(target_value / (price * contract_multiplier))
        return max(0, size)
    
    @staticmethod
    def risk_based_size(
        equity: float,
        risk_per_trade: float,
        stop_loss_pct: float,
        price: float,
        contract_multiplier: int = 10
    ) -> int:
        """
        基于风险计算仓位
        
        Args:
            equity: 总权益
            risk_per_trade: 每笔交易愿意承担的风险金额
            stop_loss_pct: 止损比例（0-1）
            price: 价格
            contract_multiplier: 合约乘数
            
        Returns:
            手数
        """
        if price <= 0 or stop_loss_pct <= 0:
            return 0
        
        risk_per_contract = price * contract_multiplier * stop_loss_pct
        if risk_per_contract <= 0:
            return 0
        
        size = int(risk_per_trade / risk_per_contract)
        return max(0, size)







