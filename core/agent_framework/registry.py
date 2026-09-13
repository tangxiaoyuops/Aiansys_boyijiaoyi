"""
工具注册中心
统一管理所有工具
"""
from typing import Dict, List, Optional
from .tools.base import BaseTool


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        """初始化工具注册中心"""
        self.tools: Dict[str, BaseTool] = {}
        self.capabilities_index: Dict[str, List[str]] = {}  # 能力索引
        self.type_index: Dict[str, List[str]] = {}  # 类型索引
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        注册工具
        
        Args:
            tool: 工具实例
        
        Raises:
            ValueError: 工具已存在
        """
        tool_name = tool.metadata.name
        
        if tool_name in self.tools:
            raise ValueError(f"工具已存在: {tool_name}")
        
        # 注册工具
        self.tools[tool_name] = tool
        
        # 更新能力索引
        for capability in tool.metadata.capabilities:
            if capability not in self.capabilities_index:
                self.capabilities_index[capability] = []
            self.capabilities_index[capability].append(tool_name)
        
        # 更新类型索引
        tool_type = tool.metadata.tool_type
        if tool_type not in self.type_index:
            self.type_index[tool_type] = []
        self.type_index[tool_type].append(tool_name)
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            是否注销成功
        """
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        
        # 从能力索引中移除
        for capability in tool.metadata.capabilities:
            if capability in self.capabilities_index:
                if tool_name in self.capabilities_index[capability]:
                    self.capabilities_index[capability].remove(tool_name)
        
        # 从类型索引中移除
        tool_type = tool.metadata.tool_type
        if tool_type in self.type_index:
            if tool_name in self.type_index[tool_type]:
                self.type_index[tool_type].remove(tool_name)
        
        # 删除工具
        del self.tools[tool_name]
        
        return True
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """
        获取工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具实例
        
        Raises:
            ValueError: 工具不存在
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")
        return self.tools[tool_name]
    
    def has_tool(self, tool_name: str) -> bool:
        """检查工具是否存在"""
        return tool_name in self.tools
    
    def list_tools(
        self, 
        tool_type: Optional[str] = None, 
        capability: Optional[str] = None
    ) -> List[BaseTool]:
        """
        列出工具
        
        Args:
            tool_type: 工具类型过滤(function/workflow/agent/api)
            capability: 能力标签过滤
        
        Returns:
            工具列表
        """
        # 先根据类型过滤
        if tool_type:
            tool_names = self.type_index.get(tool_type, [])
        else:
            tool_names = list(self.tools.keys())
        
        # 再根据能力过滤
        if capability:
            capability_tool_names = set(self.capabilities_index.get(capability, []))
            tool_names = [name for name in tool_names if name in capability_tool_names]
        
        # 返回工具实例列表
        return [self.tools[name] for name in tool_names]
    
    def get_tools_description(self, tool_names: Optional[List[str]] = None) -> str:
        """
        生成工具描述(给Agent看)
        
        Args:
            tool_names: 指定工具名称列表,如果为None则返回所有工具
        
        Returns:
            工具描述文本
        """
        if tool_names is None:
            tools = list(self.tools.values())
        else:
            tools = [self.tools[name] for name in tool_names if name in self.tools]
        
        if not tools:
            return "没有可用的工具"
        
        descriptions = []
        for i, tool in enumerate(tools, 1):
            descriptions.append(f"【工具{i}】\n{tool.get_description_for_agent()}")
        
        return "\n\n" + "="*50 + "\n\n".join(descriptions)
    
    def search_tools_by_capability(self, required_capabilities: List[str]) -> List[BaseTool]:
        """
        根据能力搜索工具(匹配度排序)
        
        Args:
            required_capabilities: 需要的能力列表
        
        Returns:
            匹配的工具列表(按匹配度降序)
        """
        tool_score: Dict[str, int] = {}
        
        for capability in required_capabilities:
            tool_names = self.capabilities_index.get(capability, [])
            for name in tool_names:
                tool_score[name] = tool_score.get(name, 0) + 1
        
        # 按匹配度排序
        sorted_tools = sorted(
            tool_score.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [self.tools[name] for name, _ in sorted_tools]
    
    def get_all_capabilities(self) -> List[str]:
        """获取所有能力标签"""
        return list(self.capabilities_index.keys())
    
    def get_all_tool_types(self) -> List[str]:
        """获取所有工具类型"""
        return list(self.type_index.keys())
    
    def get_registry_stats(self) -> Dict:
        """
        获取注册中心统计信息
        
        Returns:
            统计数据
        """
        stats = {
            "total_tools": len(self.tools),
            "tools_by_type": {},
            "tools_by_capability": {},
            "tool_names": list(self.tools.keys())
        }
        
        # 按类型统计
        for tool_type, names in self.type_index.items():
            stats["tools_by_type"][tool_type] = len(names)
        
        # 按能力统计
        for capability, names in self.capabilities_index.items():
            stats["tools_by_capability"][capability] = len(names)
        
        return stats
    
    def clear(self):
        """清空所有注册的工具"""
        self.tools.clear()
        self.capabilities_index.clear()
        self.type_index.clear()
    
    def __len__(self) -> int:
        """返回注册的工具数量"""
        return len(self.tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """检查工具是否存在"""
        return tool_name in self.tools
    
    def __iter__(self):
        """迭代所有工具"""
        return iter(self.tools.values())
