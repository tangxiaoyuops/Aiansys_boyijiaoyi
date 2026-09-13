"""
工具基类和元数据定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time


class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    tool_type: str = Field(..., description="工具类型: function/workflow/agent/api")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数schema")
    required_parameters: List[str] = Field(default_factory=list, description="必需参数")
    optional_parameters: List[str] = Field(default_factory=list, description="可选参数")
    capabilities: List[str] = Field(default_factory=list, description="工具能力标签")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="使用示例")
    cost_level: str = Field(default="low", description="成本等级: free/low/medium/high")
    estimated_time: str = Field(default="1-5s", description="预估执行时间")
    version: str = Field(default="1.0.0", description="工具版本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "get_stock_data",
                "description": "获取股票实时数据",
                "tool_type": "function",
                "parameters": {
                    "stock_code": {
                        "type": "string",
                        "description": "股票代码"
                    }
                },
                "required_parameters": ["stock_code"],
                "capabilities": ["data_fetch"],
                "cost_level": "low"
            }
        }


class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self, metadata: ToolMetadata):
        """
        初始化工具
        
        Args:
            metadata: 工具元数据
        """
        self.metadata = metadata
        self.execution_count = 0
        self.total_execution_time = 0
        self.last_execution_time = 0
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            parameters: 工具参数
            context: 执行上下文(包含历史结果、用户信息等)
        
        Returns:
            执行结果，格式:
            {
                "status": "success" | "error",
                "result": Any,  # 执行结果
                "error": str,  # 错误信息(如果有)
                "execution_time": float,  # 执行时间(秒)
                "tool_name": str,  # 工具名称
                "metadata": dict  # 其他元数据
            }
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        验证参数
        
        Args:
            parameters: 工具参数
        
        Returns:
            是否验证通过
        
        Raises:
            ValueError: 参数验证失败
        """
        for param in self.metadata.required_parameters:
            if param not in parameters:
                raise ValueError(f"缺少必需参数: {param}")
        return True
    
    def get_description_for_agent(self) -> str:
        """
        生成给Agent看的工具描述
        
        Returns:
            工具描述文本
        """
        desc = f"工具名称: {self.metadata.name}\n"
        desc += f"描述: {self.metadata.description}\n"
        desc += f"类型: {self.metadata.tool_type}\n\n"
        
        if self.metadata.required_parameters:
            desc += "必需参数:\n"
            for param in self.metadata.required_parameters:
                param_info = self.metadata.parameters.get(param, {})
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                desc += f"  - {param}: {param_type}"
                if param_desc:
                    desc += f" - {param_desc}"
                desc += "\n"
        
        if self.metadata.optional_parameters:
            desc += "\n可选参数:\n"
            for param in self.metadata.optional_parameters:
                param_info = self.metadata.parameters.get(param, {})
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                desc += f"  - {param}: {param_type}"
                if param_desc:
                    desc += f" - {param_desc}"
                desc += "\n"
        
        if self.metadata.capabilities:
            desc += f"\n能力标签: {', '.join(self.metadata.capabilities)}\n"
        
        desc += f"预估时间: {self.metadata.estimated_time}\n"
        desc += f"成本等级: {self.metadata.cost_level}\n"
        
        return desc
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取工具执行统计
        
        Returns:
            统计数据
        """
        return {
            "name": self.metadata.name,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": (
                self.total_execution_time / self.execution_count 
                if self.execution_count > 0 else 0
            ),
            "last_execution_time": self.last_execution_time
        }
    
    def _record_execution(self, execution_time: float):
        """记录执行统计"""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.last_execution_time = execution_time
