"""
风水工具选择器
支持可扩展的工具注册机制，根据意图选择合适的工具执行
"""
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class FengshuiContext:
    """风水上下文数据"""
    mingua: str = ''
    dong_si_xi_si: str = ''
    house_shape: str = '矩形'
    house_direction: str = '子'
    construction_year: Optional[int] = None
    room_layout: Dict[str, Any] = field(default_factory=dict)
    room_types: List[str] = field(default_factory=list)
    occupation_type: str = '管理'
    orientation_data: Optional[Dict] = None
    layout_data: Optional[Dict] = None
    room_data: Optional[Dict] = None
    desk_data: Optional[Dict] = None
    birth_year: Optional[int] = None
    gender: str = '男'


class FengshuiTool(ABC):
    """
    风水工具基类
    所有自定义工具需要继承此类并实现execute方法
    """
    
    name: str = "base_tool"
    description: str = "基础工具"
    intent_types: List[str] = []
    priority: int = 0
    
    @abstractmethod
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        """
        执行工具逻辑
        
        Args:
            context: 风水上下文
            user_message: 用户消息
            extracted_info: 从意图识别中提取的信息
        
        Returns:
            工具执行结果文本
        """
        pass
    
    def can_handle(self, intent_type: str) -> bool:
        """检查工具是否能处理该意图"""
        return intent_type in self.intent_types
    
    def get_prompt_context(self, context: FengshuiContext) -> str:
        """获取工具可用的上下文信息"""
        parts = []
        
        if context.mingua:
            parts.append(f"【命卦信息】\n命卦: {context.mingua}\n类型: {context.dong_si_xi_si}")
        
        if context.house_shape:
            parts.append(f"【房屋信息】\n形状: {context.house_shape}\n朝向: {context.house_direction}")
        
        if context.orientation_data:
            parts.append(self._format_orientation(context.orientation_data))
        
        if context.layout_data:
            parts.append(self._format_layout(context.layout_data))
        
        if context.room_data:
            parts.append(self._format_room(context.room_data))
        
        if context.desk_data:
            parts.append(self._format_desk(context.desk_data))
        
        return "\n\n".join(parts)
    
    def _format_orientation(self, data: Dict) -> str:
        """格式化朝向信息"""
        lines = ["【朝向分析】"]
        if data.get('orientation_score'):
            lines.append(f"朝向评分: {data['orientation_score']}分")
        if data.get('orientation_level'):
            lines.append(f"适配等级: {data['orientation_level']}")
        return "\n".join(lines)
    
    def _format_layout(self, data: Dict) -> str:
        """格式化格局信息"""
        lines = ["【格局分析】"]
        if data.get('layout_score'):
            lines.append(f"格局评分: {data['layout_score']}分")
        if data.get('house_shape'):
            lines.append(f"房屋形状: {data['house_shape']}")
        return "\n".join(lines)
    
    def _format_room(self, data: Dict) -> str:
        """格式化房间信息"""
        lines = ["【房间定位】"]
        room_positions = data.get('room_positions', {})
        for room_type, pos_info in room_positions.items():
            if pos_info.get('best_position'):
                lines.append(f"{room_type}: {pos_info['best_position']}")
        return "\n".join(lines)
    
    def _format_desk(self, data: Dict) -> str:
        """格式化工位信息"""
        lines = ["【工位分析】"]
        desk_pos = data.get('desk_position', {})
        if desk_pos.get('area'):
            lines.append(f"最佳位置: {desk_pos['area']}")
        if data.get('desk_direction'):
            lines.append(f"面朝方向: {data['desk_direction']}")
        return "\n".join(lines)


class FengshuiToolRegistry:
    """
    风水工具注册表 - 可扩展架构核心
    支持动态注册新的工具
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, FengshuiTool] = {}
        return cls._instance
    
    def register(self, tool: FengshuiTool):
        """注册工具"""
        self._tools[tool.name] = tool
        logger.debug(f"注册风水工具: {tool.name} - {tool.description}")
    
    def unregister(self, tool_name: str) -> bool:
        """注销工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[FengshuiTool]:
        """获取工具"""
        return self._tools.get(tool_name)
    
    def get_tools_for_intent(self, intent_type: str) -> List[FengshuiTool]:
        """获取能处理指定意图的所有工具，按优先级排序"""
        tools = [t for t in self._tools.values() if t.can_handle(intent_type)]
        return sorted(tools, key=lambda x: -x.priority)
    
    def list_tools(self) -> List[FengshuiTool]:
        """列出所有工具"""
        return list(self._tools.values())


class FengshuiToolSelector:
    """
    风水工具选择器
    根据意图选择最合适的工具执行
    """
    
    def __init__(self):
        self.registry = FengshuiToolRegistry()
    
    def select_and_execute(
        self,
        intent_type: str,
        context: FengshuiContext,
        user_message: str,
        extracted_info: Dict,
        **kwargs
    ) -> Dict[str, Any]:
        """
        选择并执行工具
        
        Args:
            intent_type: 意图类型
            context: 风水上下文
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


# ==================== 内置工具实现 ====================

@register_fengshui_tool
class OrientationQueryTool(FengshuiTool):
    """朝向查询工具"""
    
    name = "orientation_query"
    description = "查询房屋朝向与命卦匹配度"
    intent_types = ["orientation_query", "朝向查询", "命卦查询"]
    priority = 10
    
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        from core.tools.fengshui_calculator import calculate_orientation_score, BAZHAI_JI_FANGWEI, BAZHAI_XIONG_FANGWEI, BAGUA_FANGWEI
        
        if not context.mingua:
            return "请先提供出生年份和性别，以便计算命卦。"
        
        house_direction = extracted_info.get('house_direction', context.house_direction)
        
        result = calculate_orientation_score(house_direction, context.mingua, context.birth_year)
        
        if not result.get('success'):
            return f"朝向分析失败: {result.get('error', '未知错误')}"
        
        response = f"【朝向分析结果】\n"
        response += f"您的命卦: {context.mingua}（{context.dong_si_xi_si}）\n"
        response += f"房屋朝向: {house_direction}\n"
        response += f"朝向评分: {result['score']}分\n"
        response += f"适配等级: {result['level']}\n"
        
        analysis = result.get('analysis', {})
        if analysis.get('position_type') == '吉':
            response += f"\n此朝向属于{analysis.get('position_name', '')}位，是大吉之选！"
        elif analysis.get('position_type') == '凶':
            response += f"\n此朝向属于{analysis.get('position_name', '')}位，需要化解。"
        
        suggestions = result.get('suggestions', [])
        if suggestions:
            response += "\n\n建议：\n" + "\n".join(f"• {s}" for s in suggestions[:3])
        
        return response


@register_fengshui_tool
class RoomPositionTool(FengshuiTool):
    """房间定位工具"""
    
    name = "room_position"
    description = "分析房间最佳位置"
    intent_types = ["room_position", "房间定位", "房间布局"]
    priority = 10
    
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        from core.tools.fengshui_calculator import calculate_room_position
        
        if not context.mingua:
            return "请先提供出生年份和性别，以便计算命卦。"
        
        room_types = extracted_info.get('room_types', context.room_types)
        if not room_types:
            room_types = ['主卧', '书房', '客厅', '厨房', '卫生间']
        
        result = calculate_room_position(context.mingua, context.room_layout, room_types)
        
        if not result.get('success'):
            return f"房间定位失败: {result.get('error', '未知错误')}"
        
        response = f"【房间定位分析】\n"
        response += f"命卦: {context.mingua}（{context.dong_si_xi_si}）\n\n"
        
        room_positions = result.get('room_positions', {})
        for room_type, pos_info in room_positions.items():
            response += f"• {room_type}：建议设置在{pos_info.get('best_position', '待定')}方位"
            if pos_info.get('reason'):
                response += f"（{pos_info['reason']}）"
            response += "\n"
        
        avoid_positions = result.get('avoid_positions', [])
        if avoid_positions:
            response += "\n需避开的方位：\n"
            for avoid in avoid_positions[:3]:
                response += f"• {avoid.get('position', '')}（{avoid.get('type', '')}位）\n"
        
        return response


@register_fengshui_tool
class DeskPositionTool(FengshuiTool):
    """工位分析工具"""
    
    name = "desk_position"
    description = "分析办公桌最佳摆放位置"
    intent_types = ["desk_position", "工位分析", "办公桌摆放"]
    priority = 10
    
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        from core.tools.fengshui_calculator import calculate_desk_position
        
        if not context.mingua:
            return "请先提供出生年份和性别，以便计算命卦。"
        
        occupation_type = extracted_info.get('occupation_type', context.occupation_type)
        room_direction = extracted_info.get('room_direction', context.house_direction)
        
        result = calculate_desk_position(room_direction, context.mingua, occupation_type)
        
        if not result.get('success'):
            return f"工位分析失败: {result.get('error', '未知错误')}"
        
        response = f"【工位分析结果】\n"
        response += f"命卦: {context.mingua}\n"
        response += f"职业类型: {occupation_type}\n\n"
        
        desk_pos = result.get('desk_position', {})
        if desk_pos.get('area'):
            response += f"最佳位置：房间{desk_pos['area']}侧\n"
        if desk_pos.get('reason'):
            response += f"原因：{desk_pos['reason']}\n"
        if result.get('desk_direction'):
            response += f"面朝方向：{result['desk_direction']}\n"
        
        avoid_directions = result.get('avoid_directions', [])
        if avoid_directions:
            response += "\n需避开的方位：\n"
            for avoid in avoid_directions[:2]:
                response += f"• {avoid.get('direction', '')}（{avoid.get('reason', '')}）\n"
        
        enhancement_items = result.get('enhancement_items', [])
        if enhancement_items:
            response += "\n增运物品建议：\n"
            for item in enhancement_items[:3]:
                response += f"• {item['item']}：{item['reason']}\n"
        
        return response


@register_fengshui_tool
class LayoutAnalysisTool(FengshuiTool):
    """格局分析工具"""
    
    name = "layout_analysis"
    description = "分析房屋格局优劣"
    intent_types = ["layout_analysis", "格局分析", "房屋格局"]
    priority = 10
    
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        from core.tools.fengshui_calculator import detect_house_defects
        
        house_shape = extracted_info.get('house_shape', context.house_shape)
        
        result = detect_house_defects(house_shape)
        
        if not result.get('success'):
            return f"格局分析失败: {result.get('error', '未知错误')}"
        
        response = f"【格局分析结果】\n"
        response += f"房屋形状: {house_shape}\n"
        response += f"格局评分: {result.get('layout_score', 0)}分\n\n"
        
        defects = result.get('defects', [])
        if defects:
            response += "格局问题：\n"
            for defect in defects:
                response += f"• {defect.get('position', '')}: {defect.get('impact', '')}\n"
                if defect.get('suggestion'):
                    response += f"  建议: {defect['suggestion']}\n"
        else:
            response += "房屋格局方正，无明显缺陷。\n"
        
        analysis = result.get('analysis', {})
        if analysis.get('is_regular'):
            response += "\n方正格局，气场流通顺畅，是理想的选择。"
        
        return response


@register_fengshui_tool
class GeneralFengshuiTool(FengshuiTool):
    """通用风水咨询工具"""
    
    name = "general_fengshui"
    description = "通用风水咨询"
    intent_types = ["general", "风水咨询", "风水问题"]
    priority = 5
    
    def execute(self, context: FengshuiContext, user_message: str, extracted_info: Dict, **kwargs) -> str:
        if context.mingua:
            response = f"根据您的命卦{context.mingua}（{context.dong_si_xi_si}），我来为您分析：\n\n"
        else:
            response = "请提供您的出生年份和性别，以便进行精确的风水分析。\n\n"
        
        response += "我可以帮您分析：\n"
        response += "• 房屋朝向与命卦的匹配度\n"
        response += "• 各房间的最佳位置\n"
        response += "• 办公桌的最佳摆放\n"
        response += "• 房屋格局的优劣\n\n"
        response += "请告诉我您想了解哪方面的内容？"
        
        return response


def register_fengshui_tool(tool_class: Type[FengshuiTool]) -> Type[FengshuiTool]:
    """
    工具注册装饰器
    
    用法:
        @register_fengshui_tool
        class MyCustomTool(FengshuiTool):
            ...
    """
    tool = tool_class()
    FengshuiToolRegistry().register(tool)
    return tool_class


def get_fengshui_tool_selector() -> FengshuiToolSelector:
    """获取风水工具选择器实例"""
    return FengshuiToolSelector()
