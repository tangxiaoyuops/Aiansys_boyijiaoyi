"""
八字工具选择器
支持可扩展的工具注册机制，根据意图选择合适的工具执行
"""
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BaziContext:
    """八字上下文数据"""
    sizhu: Dict[str, Any] = field(default_factory=dict)           # 四柱数据
    wuxing_analysis: Optional[Dict] = None                        # 五行分析
    shishen_analysis: Optional[Dict] = None                       # 十神分析
    dayun_analysis: Optional[Dict] = None                         # 大运分析
    liunian_analysis: Optional[Dict] = None                       # 流年分析
    shensha_analysis: Optional[Dict] = None                       # 神煞分析
    llm_analysis: Optional[str] = None                            # LLM分析文本
    analysis_style: str = 'classic'                               # 分析风格
    gender: str = '男'                                            # 性别
    birth_info: Dict[str, Any] = field(default_factory=dict)     # 出生信息


class BaziTool(ABC):
    """
    八字工具基类
    所有自定义工具需要继承此类并实现execute方法
    """
    
    # 工具元信息（子类必须覆盖）
    name: str = "base_tool"
    description: str = "基础工具"
    intent_types: List[str] = []  # 该工具支持的意图类型
    priority: int = 0             # 优先级
    
    @abstractmethod
    def execute(self, context: BaziContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        """
        执行工具逻辑
        
        Args:
            context: 八字上下文
            user_message: 用户消息
            extracted_info: 从意图识别中提取的信息
        
        Returns:
            工具执行结果文本
        """
        pass
    
    def can_handle(self, intent_type: str) -> bool:
        """检查工具是否能处理该意图"""
        return intent_type in self.intent_types
    
    def get_prompt_context(self, context: BaziContext) -> str:
        """获取工具可用的上下文信息，用于构建prompt"""
        parts = []
        
        if context.sizhu:
            parts.append(self._format_sizhu(context.sizhu))
        
        if context.wuxing_analysis:
            parts.append(self._format_wuxing(context.wuxing_analysis))
        
        if context.shishen_analysis:
            parts.append(self._format_shishen(context.shishen_analysis))
        
        if context.dayun_analysis:
            parts.append(self._format_dayun(context.dayun_analysis))
        
        if context.shensha_analysis:
            parts.append(self._format_shensha(context.shensha_analysis))
        
        return "\n\n".join(parts)
    
    def _format_sizhu(self, sizhu: Dict) -> str:
        """格式化四柱信息"""
        lines = ["【四柱八字】"]
        zhu_names = {
            'nian_zhu': '年柱',
            'yue_zhu': '月柱', 
            'ri_zhu': '日柱',
            'shi_zhu': '时柱'
        }
        for key, name in zhu_names.items():
            zhu = sizhu.get(key, {})
            if zhu:
                lines.append(f"{name}: {zhu.get('tian_gan', '?')}{zhu.get('di_zhi', '?')}")
        
        if sizhu.get('lunar_year'):
            lines.append(f"农历: {sizhu.get('lunar_year')}年{sizhu.get('lunar_month')}月{sizhu.get('lunar_day')}日")
        
        return "\n".join(lines)
    
    def _format_wuxing(self, wuxing: Dict) -> str:
        """格式化五行信息"""
        data = wuxing.get('wuxing_data', {})
        if not data:
            return ""
        
        lines = ["【五行分析】"]
        wuxing_names = {
            'jin': '金', 'mu': '木', 'shui': '水', 'huo': '火', 'tu': '土'
        }
        for key, name in wuxing_names.items():
            count = data.get(key, 0)
            lines.append(f"{name}: {count}")
        
        if data.get('rizhu_wuxing'):
            lines.append(f"日主五行: {data.get('rizhu_wuxing')}")
        
        return "\n".join(lines)
    
    def _format_shishen(self, shishen: Dict) -> str:
        """格式化十神信息"""
        data = shishen.get('shishen_data', {})
        if not data:
            return ""
        
        lines = ["【十神分析】"]
        zhu_names = {
            'nian_zhu': '年柱', 'yue_zhu': '月柱',
            'ri_zhu': '日柱', 'shi_zhu': '时柱'
        }
        for key, name in zhu_names.items():
            zhu_data = data.get(key, {})
            if zhu_data:
                gan = zhu_data.get('gan_shishen', '')
                zhi = zhu_data.get('zhi_shishen', '')
                lines.append(f"{name}: 天干{gan}, 地支{zhi}")
        
        return "\n".join(lines)
    
    def _format_dayun(self, dayun: Dict) -> str:
        """格式化大运信息"""
        dayun_list = dayun.get('dayun_list', [])
        if not dayun_list:
            return ""
        
        lines = ["【大运分析】"]
        for i, dy in enumerate(dayun_list[:8]):  # 最多显示8步大运
            lines.append(f"第{i+1}步: {dy.get('gan', '?')}{dy.get('zhi', '?')} ({dy.get('start_age', '?')}-{dy.get('end_age', '?')}岁)")
        
        return "\n".join(lines)
    
    def _format_shensha(self, shensha: Dict) -> str:
        """格式化神煞信息"""
        shensha_list = shensha.get('shensha_data', {}).get('shensha_list', [])
        if not shensha_list:
            return ""
        
        lines = ["【神煞分析】"]
        for ss in shensha_list:
            pos = ss.get('position', '')
            name = ss.get('name', '')
            ss_type = ss.get('type', '')
            lines.append(f"{name} ({pos}) - {ss_type}")
        
        return "\n".join(lines)


class ToolRegistry:
    """
    工具注册表 - 可扩展架构核心
    支持动态注册新的工具
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, BaziTool] = {}
        return cls._instance
    
    def register(self, tool: BaziTool):
        """注册工具"""
        self._tools[tool.name] = tool
        logger.debug(f"注册工具: {tool.name} - {tool.description}")
    
    def unregister(self, tool_name: str) -> bool:
        """注销工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaziTool]:
        """获取工具"""
        return self._tools.get(tool_name)
    
    def get_tools_for_intent(self, intent_type: str) -> List[BaziTool]:
        """获取能处理指定意图的所有工具，按优先级排序"""
        tools = [t for t in self._tools.values() if t.can_handle(intent_type)]
        return sorted(tools, key=lambda x: -x.priority)
    
    def list_tools(self) -> List[BaziTool]:
        """列出所有工具"""
        return list(self._tools.values())


class ToolSelector:
    """
    工具选择器
    根据意图选择最合适的工具执行
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
    
    def select_and_execute(
        self, 
        intent_type: str, 
        context: BaziContext, 
        user_message: str,
        extracted_info: Dict,
        **kwargs
    ) -> Dict[str, Any]:
        """
        选择并执行工具
        
        Args:
            intent_type: 意图类型
            context: 八字上下文
            user_message: 用户消息
            extracted_info: 提取的信息
        
        Returns:
            {
                'tool_name': str,
                'success': bool,
                'result': str,
                'error': Optional[str]
            }
        """
        tools = self.registry.get_tools_for_intent(intent_type)
        
        if not tools:
            logger.warning(f"没有找到处理意图 '{intent_type}' 的工具")
            return {
                'tool_name': None,
                'success': False,
                'result': '',
                'error': f'没有可用的工具处理意图: {intent_type}'
            }
        
        # 选择优先级最高的工具
        selected_tool = tools[0]
        logger.info(f"选择工具: {selected_tool.name} 处理意图: {intent_type}")
        
        try:
            result = selected_tool.execute(context, user_message, extracted_info, **kwargs)
            return {
                'tool_name': selected_tool.name,
                'success': True,
                'result': result,
                'error': None
            }
        except Exception as e:
            logger.error(f"工具执行失败: {selected_tool.name} - {e}")
            return {
                'tool_name': selected_tool.name,
                'success': False,
                'result': '',
                'error': str(e)
            }
    
    def execute_all_for_intent(
        self,
        intent_type: str,
        context: BaziContext,
        user_message: str,
        extracted_info: Dict,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行所有能处理该意图的工具（用于聚合多个工具结果）
        """
        tools = self.registry.get_tools_for_intent(intent_type)
        results = []
        
        for tool in tools:
            try:
                result = tool.execute(context, user_message, extracted_info, **kwargs)
                results.append({
                    'tool_name': tool.name,
                    'success': True,
                    'result': result,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'tool_name': tool.name,
                    'success': False,
                    'result': '',
                    'error': str(e)
                })
        
        return results


def register_bazi_tool(tool_class: Type[BaziTool]) -> Type[BaziTool]:
    """
    工具注册装饰器
    
    用法:
        @register_bazi_tool
        class MyCustomTool(BaziTool):
            ...
    """
    tool = tool_class()
    ToolRegistry().register(tool)
    return tool_class


# 导出便捷函数
def get_tool_selector() -> ToolSelector:
    """获取工具选择器实例"""
    return ToolSelector()