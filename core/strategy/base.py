"""
策略基类
所有策略都需要继承此类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class Strategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str = "Base Strategy"):
        """
        初始化策略
        
        Args:
            name: 策略名称
        """
        self.name = name
        self.parameters = {}
        self.initialized = False
        
    def initialize(self, parameters: Dict[str, Any]):
        """
        初始化策略参数
        
        Args:
            parameters: 策略参数字典
        """
        self.parameters = parameters
        self.initialized = True
        self._on_initialize()
    
    @abstractmethod
    def _on_initialize(self):
        """子类实现：初始化逻辑"""
        pass
    
    @abstractmethod
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any  # Portfolio类型，避免循环导入
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        Args:
            data: 历史数据（包含OHLCV等）
            portfolio: 当前组合状态
            
        Returns:
            信号字典 {
                'action': 'OPEN_LONG' | 'OPEN_SHORT' | 'CLOSE_LONG' | 'CLOSE_SHORT' | 'CLOSE_ALL',
                'size': 交易数量（手数）,
                'reason': 交易原因
            }
            或 None（无信号）
        """
        pass
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(key, default)
    
    def __repr__(self) -> str:
        return f"Strategy(name={self.name}, initialized={self.initialized})"









