"""
支付服务
实现订单创建和模拟支付功能
后续可以替换为真实支付（微信支付、支付宝等）
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from server.models import Reward


def generate_order_id() -> str:
    """生成唯一订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = str(uuid.uuid4()).replace("-", "")[:8].upper()
    return f"REWARD{timestamp}{random_str}"


def create_order(
    db: Session,
    amount: float,
    message: Optional[str] = None,
    contact: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建打赏订单
    
    Args:
        db: 数据库会话
        amount: 打赏金额
        message: 留言
        contact: 联系方式
    
    Returns:
        订单信息字典
    """
    try:
        # 验证金额
        if amount <= 0:
            raise ValueError("打赏金额必须大于0")
        if amount > 10000:
            raise ValueError("单次打赏金额不能超过10000元")
        
        # 生成订单号
        order_id = generate_order_id()
        
        # 创建订单记录
        reward = Reward(
            order_id=order_id,
            amount=Decimal(str(amount)),
            message=message,
            contact=contact,
            payment_status="pending",
            payment_method=None
        )
        
        db.add(reward)
        db.commit()
        db.refresh(reward)
        
        print(f"[支付服务] 订单创建成功: order_id={order_id}, amount={amount}")
        
        return {
            "success": True,
            "order_id": order_id,
            "amount": float(reward.amount),
            "status": reward.payment_status,
            "created_at": reward.created_at.isoformat() if reward.created_at else None
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"[支付服务] 订单创建失败: {error_msg}")
        raise Exception(f"创建订单失败: {error_msg}")


def simulate_payment(
    db: Session,
    order_id: str
) -> Dict[str, Any]:
    """
    模拟支付（当前实现）
    后续可以替换为真实支付逻辑
    
    Args:
        db: 数据库会话
        order_id: 订单号
    
    Returns:
        支付结果字典
    """
    try:
        # 查询订单
        reward = db.query(Reward).filter(Reward.order_id == order_id).first()
        if not reward:
            raise ValueError(f"订单不存在: {order_id}")
        
        # 检查订单状态
        if reward.payment_status == "paid":
            return {
                "success": True,
                "order_id": order_id,
                "status": "paid",
                "message": "订单已支付"
            }
        
        if reward.payment_status != "pending":
            raise ValueError(f"订单状态不允许支付: {reward.payment_status}")
        
        # 模拟支付（直接设置为已支付）
        reward.payment_status = "paid"
        reward.payment_method = "simulate"  # 模拟支付
        reward.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(reward)
        
        print(f"[支付服务] 模拟支付成功: order_id={order_id}, amount={reward.amount}")
        
        return {
            "success": True,
            "order_id": order_id,
            "status": "paid",
            "payment_method": "simulate",
            "paid_at": reward.paid_at.isoformat() if reward.paid_at else None,
            "message": "支付成功（模拟）"
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"[支付服务] 模拟支付失败: {error_msg}")
        raise Exception(f"支付失败: {error_msg}")


def verify_payment(
    db: Session,
    order_id: str
) -> Dict[str, Any]:
    """
    验证支付状态（预留接口，用于真实支付）
    
    Args:
        db: 数据库会话
        order_id: 订单号
    
    Returns:
        支付状态字典
    """
    try:
        reward = db.query(Reward).filter(Reward.order_id == order_id).first()
        if not reward:
            raise ValueError(f"订单不存在: {order_id}")
        
        return {
            "success": True,
            "order_id": order_id,
            "status": reward.payment_status,
            "payment_method": reward.payment_method,
            "paid_at": reward.paid_at.isoformat() if reward.paid_at else None
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"[支付服务] 验证支付失败: {error_msg}")
        raise Exception(f"验证支付失败: {error_msg}")


def get_order_status(
    db: Session,
    order_id: str
) -> Optional[Reward]:
    """
    获取订单状态
    
    Args:
        db: 数据库会话
        order_id: 订单号
    
    Returns:
        订单对象，如果不存在返回None
    """
    return db.query(Reward).filter(Reward.order_id == order_id).first()

