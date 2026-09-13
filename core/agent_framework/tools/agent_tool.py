"""
Agent工具实现 - 支持嵌套Agent
"""
from typing import Dict, Any
import time
from .base import BaseTool, ToolMetadata


class AgentTool(BaseTool):
    """Agent工具 - 包装子Agent"""
    
    def __init__(self, agent_instance, metadata: ToolMetadata):
        """
        初始化Agent工具
        
        Args:
            agent_instance: Agent实例(必须是BaseAgent的实例)
            metadata: 工具元数据
        """
        super().__init__(metadata)
        self.agent = agent_instance
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent工具
        
        Args:
            parameters: Agent输入参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 准备Agent输入
            user_input = {
                "task": parameters.get("task", ""),
                **parameters
            }
            
            # 调用子Agent
            result = self.agent.run(
                user_input=user_input,
                context=context
            )
            
            # 记录执行时间
            execution_time = time.time() - start_time
            self._record_execution(execution_time)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "tool_name": self.metadata.name,
                "tool_type": "agent",
                "sub_agent_name": self.agent.name if hasattr(self.agent, 'name') else "unknown",
                "sub_agent_iterations": result.get("iterations", 0) if isinstance(result, dict) else 0,
                "sub_agent_trace": result.get("execution_trace", []) if isinstance(result, dict) else []
            }
            
        except ValueError as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": f"参数验证失败: {str(e)}",
                "error_type": "ValidationError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
