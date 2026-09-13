"""
通用自主规划Agent框架
支持ReAct循环、工具调用、嵌套Agent
"""

from .tools.base import BaseTool, ToolMetadata
from .tools.function_tool import FunctionTool
from .tools.agent_tool import AgentTool
from .tools.workflow_tool import WorkflowTool
from .tools.api_tool import APITool
from .registry import ToolRegistry
from .agents.base import BaseAgent, AgentState
from .agents.react_agent import ReActAgent
from .engine import ExecutionEngine

__version__ = "1.0.0"
__all__ = [
    # Tools
    "BaseTool",
    "ToolMetadata",
    "FunctionTool",
    "AgentTool",
    "WorkflowTool",
    "APITool",
    # Registry
    "ToolRegistry",
    # Agents
    "BaseAgent",
    "AgentState",
    "ReActAgent",
    # Engine
    "ExecutionEngine",
]
