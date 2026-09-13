"""
工作流工具实现
"""
from typing import Dict, Any, Optional
import time
from .base import BaseTool, ToolMetadata


class WorkflowTool(BaseTool):
    """工作流工具 - 包装LangGraph工作流"""
    
    def __init__(
        self, 
        workflow_config_path: str, 
        metadata: ToolMetadata,
        workflow_engine: Optional[Any] = None
    ):
        """
        初始化工作流工具
        
        Args:
            workflow_config_path: 工作流配置文件路径
            metadata: 工具元数据
            workflow_engine: 工作流引擎实例(可选,可以后续注入)
        """
        super().__init__(metadata)
        self.workflow_config_path = workflow_config_path
        self.workflow_engine = workflow_engine
    
    def set_workflow_engine(self, engine: Any):
        """设置工作流引擎"""
        self.workflow_engine = engine
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流工具
        
        Args:
            parameters: 工作流输入参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        if not self.workflow_engine:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": "工作流引擎未设置",
                "error_type": "ConfigurationError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
        
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 加载工作流
            workflow = self.workflow_engine.load_workflow(self.workflow_config_path)
            
            # 合并参数和上下文
            input_data = {
                **parameters,
                **context,
                "user_question": parameters.get("task", ""),
            }
            
            # 执行工作流
            result = self.workflow_engine.execute_workflow(workflow, input_data)
            
            # 记录执行时间
            execution_time = time.time() - start_time
            self._record_execution(execution_time)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "tool_name": self.metadata.name,
                "tool_type": "workflow",
                "workflow_path": self.workflow_config_path
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
