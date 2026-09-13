"""
工作流节点基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """节点基类"""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """
        初始化节点
        
        Args:
            node_id: 节点ID
            config: 节点配置
        """
        import os
        self.node_id = node_id
        self.config = config
        # 使用环境变量中的模型,如果没有则使用配置中的模型,最后才用默认值
        self.model = os.getenv('QWEN_MODEL') or config.get('model', 'GLM-5')
        self.timeout = config.get('timeout', 30)
        self.retry_times = config.get('retry_times', 2)
        self.node_type = self.__class__.__name__
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行节点逻辑（抽象方法，子类必须实现）
        
        Args:
            input_data: 输入数据
        
        Returns:
            执行结果
        """
        pass
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行节点（包含错误处理和重试机制）
        
        Args:
            input_data: 输入数据
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        # 验证输入
        if not self.validate_input(input_data):
            return self.handle_error(ValueError("输入数据验证失败"))
        
        # 重试机制
        for attempt in range(self.retry_times + 1):
            try:
                logger.info(f"[{self.node_id}] 开始执行，尝试 {attempt + 1}/{self.retry_times + 1}")
                
                result = self.execute(input_data)
                
                # 添加元数据
                result['node_id'] = self.node_id
                result['node_type'] = self.node_type
                result['status'] = 'success'
                result['timestamp'] = time.time()
                result['elapsed_time'] = time.time() - start_time
                
                logger.info(f"[{self.node_id}] 执行成功，耗时 {result['elapsed_time']:.2f}秒")
                
                return result
            
            except Exception as e:
                logger.error(f"[{self.node_id}] 执行失败，尝试 {attempt + 1}/{self.retry_times + 1}: {str(e)}")
                
                if attempt == self.retry_times:
                    # 最后一次重试也失败了
                    return self.handle_error(e)
                
                # 等待一段时间后重试
                time.sleep(2 ** attempt)  # 指数退避
        
        return self.handle_error(Exception("未知错误"))
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
        
        Returns:
            是否验证通过
        """
        if not isinstance(input_data, dict):
            logger.error(f"[{self.node_id}] 输入数据必须是字典类型")
            return False
        
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        错误处理
        
        Args:
            error: 异常对象
        
        Returns:
            错误结果
        """
        logger.error(f"[{self.node_id}] 错误: {str(error)}", exc_info=True)
        
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "status": "error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time()
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def __repr__(self) -> str:
        return f"<{self.node_type} node_id={self.node_id}>"
