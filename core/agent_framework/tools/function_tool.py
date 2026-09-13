"""
函数工具实现
"""
from typing import Dict, Any, Callable
import time
from .base import BaseTool, ToolMetadata


class FunctionTool(BaseTool):
    """函数工具 - 包装Python函数"""
    
    def __init__(self, func: Callable, metadata: ToolMetadata):
        """
        初始化函数工具
        
        Args:
            func: Python函数
            metadata: 工具元数据
        """
        super().__init__(metadata)
        self.func = func
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行函数工具
        
        Args:
            parameters: 函数参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 执行函数
            result = self.func(**parameters)
            
            # 记录执行时间
            execution_time = time.time() - start_time
            self._record_execution(execution_time)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "tool_name": self.metadata.name,
                "tool_type": "function"
            }
            
        except ValueError as e:
            # 参数验证错误
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": f"参数验证失败: {str(e)}",
                "error_type": "ValidationError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
            
        except Exception as e:
            # 执行错误
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
