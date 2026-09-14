"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """系统配置"""
    
    # 应用配置
    APP_NAME: str = "博弈交易法智能分析系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://boyi:password@localhost:5432/boyi"
    TIMESCALEDB_URL: str = "postgresql://boyi:password@localhost:5433/boyi_ts"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 数据源配置
    TUSHARE_TOKEN: Optional[str] = None
    
    # AI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    
    # 向量数据库配置
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # 任务调度配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 监控配置
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()
