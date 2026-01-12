"""
数据库模型定义
用于需求、问题、打赏等功能的持久化存储
"""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, DECIMAL, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel as PydanticBaseModel

# 数据库文件路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(project_root, "data")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "app.db")
DATABASE_URL = f"sqlite:///{db_path}"

# SQLAlchemy 设置
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLAlchemy 模型
class Requirement(Base):
    """需求提交表"""
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    contact = Column(String(100))
    status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())


class Issue(Base):
    """问题报告表"""
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    contact = Column(String(100))
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="open")  # open, in_progress, resolved, closed
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())


class Reward(Base):
    """打赏记录表"""
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    message = Column(Text)
    contact = Column(String(100))
    payment_status = Column(String(20), default="pending")  # pending, paid, failed, cancelled
    payment_method = Column(String(50))  # 支付方式（如：wechat, alipay, simulate）
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)


# Pydantic 模型（用于 API 请求/响应）
class RequirementCreate(PydanticBaseModel):
    """创建需求请求模型"""
    title: str
    content: str
    contact: Optional[str] = None


class RequirementResponse(PydanticBaseModel):
    """需求响应模型"""
    id: int
    title: str
    content: str
    contact: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class IssueCreate(PydanticBaseModel):
    """创建问题请求模型"""
    title: str
    content: str
    contact: Optional[str] = None
    severity: Optional[str] = "medium"  # low, medium, high, critical


class IssueResponse(PydanticBaseModel):
    """问题响应模型"""
    id: int
    title: str
    content: str
    contact: Optional[str]
    severity: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RewardCreate(PydanticBaseModel):
    """创建打赏订单请求模型"""
    amount: float
    message: Optional[str] = None
    contact: Optional[str] = None


class RewardResponse(PydanticBaseModel):
    """打赏订单响应模型"""
    id: int
    order_id: str
    amount: float
    message: Optional[str]
    contact: Optional[str]
    payment_status: str
    payment_method: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print(f"[数据库] 数据库表已创建/检查: {db_path}")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

