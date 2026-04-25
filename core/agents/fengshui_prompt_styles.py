"""
风水分析LLM提示词模板
提供多种风格的风水解读提示词
"""
from typing import Dict, Any, Tuple


def get_fengshui_prompt(analysis_result: Dict[str, Any], style: str = 'classic') -> Tuple[str, str]:
    """
    获取风水分析提示词
    
    Args:
        analysis_result: 风水分析结果
        style: 分析风格
            - classic: 传统风格，专业详尽
            - simple: 简洁风格，通俗易懂
            - business: 商业风格，注重财运事业
            - health: 健康风格，注重身心健康
            - comprehensive: 综合风格，全面分析
    
    Returns:
        (system_prompt, user_prompt)
    """
    style_prompts = {
        'classic': _get_classic_prompt,
        'simple': _get_simple_prompt,
        'business': _get_business_prompt,
        'health': _get_health_prompt,
        'comprehensive': _get_comprehensive_prompt,
    }
    
    prompt_func = style_prompts.get(style, _get_classic_prompt)
    return prompt_func(analysis_result)


def _get_classic_prompt(result: Dict[str, Any]) -> Tuple[str, str]:
    """传统专业风格"""
    system_prompt = """你是一位精通八宅风水、玄空飞星的风水大师，具有深厚的传统文化功底。
请用专业但易懂的语言，对风水布局进行深入分析，结合传统风水理论给出专业建议。

分析要点：
1. 命卦与东四/西四命的含义
2. 四吉四凶方位的具体影响
3. 房屋朝向与命卦的匹配程度
4. 房间布局的合理性
5. 工位摆放的专业建议
6. 改善方案与注意事项

请用专业术语但解释清楚，体现传统文化智慧。"""

    user_prompt = _build_user_prompt(result)
    return system_prompt, user_prompt


def _get_simple_prompt(result: Dict[str, Any]) -> Tuple[str, str]:
    """简洁通俗风格"""
    system_prompt = """你是一位亲切的风水顾问，擅长用简单易懂的语言解释风水知识。
请用日常语言，避免专业术语，给出实用的居家风水建议。

分析要点：
1. 用大白话解释命卦是什么
2. 哪些方位好，哪些方位不好
3. 房间应该怎么布置
4. 办公桌应该放哪里
5. 简单有效的改善方法

语气亲切自然，像朋友聊天一样。"""

    user_prompt = _build_user_prompt(result, simple=True)
    return system_prompt, user_prompt


def _get_business_prompt(result: Dict[str, Any]) -> Tuple[str, str]:
    """商业事业风格"""
    system_prompt = """你是一位专注于商业风水的顾问，擅长分析办公环境对事业发展的影响。
请重点分析风水布局对事业、财运、人际关系的帮助。

分析要点：
1. 办公环境与事业发展的关系
2. 财位的选择与布置
3. 办公桌最佳位置
4. 提升事业运的具体方法
5. 商业谈判、决策的风水建议

注重实用性，给出可操作的建议。"""

    user_prompt = _build_user_prompt(result, focus='business')
    return system_prompt, user_prompt


def _get_health_prompt(result: Dict[str, Any]) -> Tuple[str, str]:
    """健康风格"""
    system_prompt = """你是一位注重健康养生的风水顾问，擅长分析居住环境对身心健康的影响。
请重点分析风水布局与健康、睡眠、家庭和谐的关系。

分析要点：
1. 卧室位置与睡眠质量
2. 健康方位的选择
3. 居家环境与身心健康
4. 化解不利因素的方法
5. 提升家庭和谐的建议

语气温和关怀，注重身心健康。"""

    user_prompt = _build_user_prompt(result, focus='health')
    return system_prompt, user_prompt


def _get_comprehensive_prompt(result: Dict[str, Any]) -> Tuple[str, str]:
    """综合全面风格"""
    system_prompt = """你是一位全面的风水大师，精通八宅、玄空、形势等多派风水理论。
请从多个角度全面分析风水布局，给出综合性的专业建议。

分析要点：
1. 命卦分析与人生运势
2. 房屋格局与气场流通
3. 各房间功能定位
4. 工位与事业财运
5. 流年运势与风水调整
6. 综合改善方案

请全面深入，兼顾传统与现代。"""

    user_prompt = _build_user_prompt(result, comprehensive=True)
    return system_prompt, user_prompt


def _build_user_prompt(
    result: Dict[str, Any],
    simple: bool = False,
    focus: str = None,
    comprehensive: bool = False,
) -> str:
    """
    构建用户提示词
    """
    lines = []
    
    lines.append("【基本信息】")
    
    if 'mingua' in result:
        mingua = result['mingua']
        lines.append(f"- 命卦：{mingua.get('mingua', '')}")
        lines.append(f"- 命卦类型：{mingua.get('dong_si_xi_si', '')}")
        lines.append(f"- 命卦五行：{mingua.get('mingua_wuxing', '')}")
    
    if 'house_info' in result:
        house_info = result['house_info']
        lines.append(f"- 房屋形状：{house_info.get('house_shape', '矩形')}")
        lines.append(f"- 房屋朝向：{house_info.get('house_direction', '')}")
    
    lines.append("")
    
    if 'orientation_analysis' in result:
        orientation = result['orientation_analysis']
        lines.append("【朝向分析】")
        lines.append(f"- 朝向评分：{orientation.get('orientation_score', 0)}分")
        lines.append(f"- 适配等级：{orientation.get('orientation_level', '')}")
        
        if 'ji_fangwei' in orientation:
            lines.append("- 四吉方位：")
            for name, info in orientation['ji_fangwei'].items():
                lines.append(f"  · {name}：{info.get('fangwei', '')}（{info.get('gua', '')}宫）")
        
        if 'xiong_fangwei' in orientation:
            lines.append("- 四凶方位：")
            for name, info in orientation['xiong_fangwei'].items():
                lines.append(f"  · {name}：{info.get('fangwei', '')}（{info.get('gua', '')}宫）")
        lines.append("")
    
    if 'layout_analysis' in result:
        layout = result['layout_analysis']
        lines.append("【格局分析】")
        lines.append(f"- 格局评分：{layout.get('layout_score', 0)}分")
        lines.append(f"- 房屋形状：{layout.get('house_shape', '')}")
        
        shape_analysis = layout.get('shape_analysis', {})
        if shape_analysis.get('description'):
            lines.append(f"- 形状描述：{shape_analysis['description']}")
        
        defects = layout.get('defects', [])
        if defects:
            lines.append(f"- 缺角问题：{len(defects)}处")
        lines.append("")
    
    if 'room_analysis' in result:
        room = result['room_analysis']
        lines.append("【房间定位】")
        
        room_positions = room.get('room_positions', {})
        for room_type, pos_info in room_positions.items():
            if pos_info.get('best_position'):
                lines.append(f"- {room_type}：建议设置在{pos_info['best_position']}方位")
        lines.append("")
    
    if 'desk_analysis' in result:
        desk = result['desk_analysis']
        lines.append("【工位分析】")
        
        desk_pos = desk.get('desk_position', {})
        if desk_pos.get('area'):
            lines.append(f"- 最佳位置：房间{desk_pos['area']}侧")
        
        if desk.get('desk_direction'):
            lines.append(f"- 面向方向：{desk['desk_direction']}")
        
        enhancement = desk.get('enhancement_items', [])
        if enhancement:
            items = [item['item'] for item in enhancement[:3]]
            lines.append(f"- 增运物品：{', '.join(items)}")
        lines.append("")
    
    lines.append("【综合评价】")
    lines.append(f"- 综合评分：{result.get('overall_score', 0)}分")
    
    summary = result.get('summary', {})
    if summary.get('overall_level'):
        lines.append(f"- 总体评级：{summary['overall_level']}")
    
    if focus == 'business':
        lines.append("")
        lines.append("请重点分析此风水布局对事业发展、财运、人际关系的影响，并给出专业建议。")
    elif focus == 'health':
        lines.append("")
        lines.append("请重点分析此风水布局对健康、睡眠、家庭和谐的影响，并给出改善建议。")
    elif comprehensive:
        lines.append("")
        lines.append("请从事业、财运、健康、家庭等多个角度进行全面分析，并给出综合改善方案。")
    
    return "\n".join(lines)
