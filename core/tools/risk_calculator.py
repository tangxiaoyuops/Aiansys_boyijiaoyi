"""
风险管理计算工具
提供期货交易的风险管理相关计算
"""
from typing import Dict, Any, Optional, List
import pandas as pd


def calculate_margin(
    price: float,
    contract_multiplier: int,
    margin_rate: float,
    position: int = 1
) -> float:
    """
    计算保证金
    
    Args:
        price: 当前价格
        contract_multiplier: 合约乘数
        margin_rate: 保证金率（如0.10表示10%）
        position: 持仓手数
    
    Returns:
        所需保证金
    """
    contract_value = price * contract_multiplier
    margin_per_contract = contract_value * margin_rate
    total_margin = margin_per_contract * position
    return total_margin


def calculate_leverage(
    price: float,
    contract_multiplier: int,
    margin_rate: float
) -> float:
    """
    计算杠杆倍数
    
    Args:
        price: 当前价格
        contract_multiplier: 合约乘数
        margin_rate: 保证金率
    
    Returns:
        杠杆倍数
    """
    if margin_rate == 0:
        return 0
    return 1.0 / margin_rate


def calculate_position_risk(
    entry_price: float,
    current_price: float,
    contract_multiplier: int,
    position: int,
    direction: str = 'long'  # 'long' or 'short'
) -> Dict[str, float]:
    """
    计算持仓风险
    
    Args:
        entry_price: 开仓价格
        current_price: 当前价格
        contract_multiplier: 合约乘数
        position: 持仓手数
        direction: 方向，'long'多头或'short'空头
    
    Returns:
        {
            'unrealized_pnl': float,  # 未实现盈亏
            'unrealized_pnl_pct': float,  # 未实现盈亏百分比
            'risk_exposure': float,  # 风险敞口
        }
    """
    price_change = current_price - entry_price
    if direction == 'short':
        price_change = -price_change
    
    contract_value = entry_price * contract_multiplier
    total_contract_value = contract_value * position
    
    unrealized_pnl = price_change * contract_multiplier * position
    unrealized_pnl_pct = (price_change / entry_price * 100) if entry_price != 0 else 0.0
    risk_exposure = total_contract_value
    
    return {
        'unrealized_pnl': unrealized_pnl,
        'unrealized_pnl_pct': unrealized_pnl_pct,
        'risk_exposure': risk_exposure
    }


def calculate_stop_loss(
    entry_price: float,
    stop_loss_pct: float,
    direction: str = 'long'
) -> float:
    """
    计算止损价格
    
    Args:
        entry_price: 开仓价格
        stop_loss_pct: 止损百分比（如-5表示5%）
        direction: 方向，'long'多头或'short'空头
    
    Returns:
        止损价格
    """
    if direction == 'long':
        stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
    else:  # short
        stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
    
    return stop_loss_price


def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float,
    contract_multiplier: int,
    margin_rate: float
) -> Dict[str, Any]:
    """
    根据风险计算合适的仓位大小
    
    Args:
        account_balance: 账户余额
        risk_per_trade: 每笔交易愿意承担的风险金额
        entry_price: 开仓价格
        stop_loss_price: 止损价格
        contract_multiplier: 合约乘数
        margin_rate: 保证金率
    
    Returns:
        {
            'position_size': int,  # 建议持仓手数
            'required_margin': float,  # 所需保证金
            'risk_amount': float,  # 实际风险金额
            'margin_usage_rate': float,  # 保证金使用率
        }
    """
    price_risk = abs(entry_price - stop_loss_price)
    risk_per_contract = price_risk * contract_multiplier
    
    if risk_per_contract == 0:
        return {
            'position_size': 0,
            'required_margin': 0.0,
            'risk_amount': 0.0,
            'margin_usage_rate': 0.0
        }
    
    # 根据风险计算手数
    position_size = int(risk_per_trade / risk_per_contract)
    position_size = max(1, position_size)  # 至少1手
    
    # 计算所需保证金
    required_margin = calculate_margin(entry_price, contract_multiplier, margin_rate, position_size)
    
    # 如果保证金超过账户余额，调整手数
    if required_margin > account_balance:
        max_position = int(account_balance / (entry_price * contract_multiplier * margin_rate))
        position_size = max(1, max_position)
        required_margin = calculate_margin(entry_price, contract_multiplier, margin_rate, position_size)
    
    # 实际风险金额
    actual_risk = price_risk * contract_multiplier * position_size
    
    # 保证金使用率
    margin_usage_rate = (required_margin / account_balance * 100) if account_balance > 0 else 0.0
    
    return {
        'position_size': position_size,
        'required_margin': required_margin,
        'risk_amount': actual_risk,
        'margin_usage_rate': margin_usage_rate
    }


def assess_portfolio_risk(
    positions: List[Dict[str, Any]],
    account_balance: float
) -> Dict[str, Any]:
    """
    评估投资组合风险
    
    Args:
        positions: 持仓列表，每个元素包含 {price, contract_multiplier, position, direction, margin_rate}
        account_balance: 账户余额
    
    Returns:
        {
            'total_margin': float,  # 总保证金
            'total_exposure': float,  # 总风险敞口
            'margin_usage_rate': float,  # 保证金使用率
            'unrealized_pnl': float,  # 总未实现盈亏
            'risk_level': str,  # 风险等级：'low'/'medium'/'high'
        }
    """
    total_margin = 0.0
    total_exposure = 0.0
    total_unrealized_pnl = 0.0
    
    for pos in positions:
        price = pos.get('price', 0)
        multiplier = pos.get('contract_multiplier', 1)
        position = pos.get('position', 0)
        margin_rate = pos.get('margin_rate', 0.1)
        
        margin = calculate_margin(price, multiplier, margin_rate, position)
        total_margin += margin
        
        exposure = price * multiplier * position
        total_exposure += exposure
    
    margin_usage_rate = (total_margin / account_balance * 100) if account_balance > 0 else 0.0
    
    # 评估风险等级
    if margin_usage_rate < 30:
        risk_level = 'low'
    elif margin_usage_rate < 70:
        risk_level = 'medium'
    else:
        risk_level = 'high'
    
    return {
        'total_margin': total_margin,
        'total_exposure': total_exposure,
        'margin_usage_rate': margin_usage_rate,
        'unrealized_pnl': total_unrealized_pnl,
        'risk_level': risk_level
    }

