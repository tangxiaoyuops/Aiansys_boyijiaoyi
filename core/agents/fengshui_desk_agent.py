"""
风水工位摆放Agent
根据命卦和职业类型分析办公桌最佳摆放位置
"""
from typing import Dict, Any, List, Optional
import logging

from core.tools.fengshui_calculator import (
    calculate_desk_position,
    BAZHAI_JI_FANGWEI,
    BAZHAI_XIONG_FANGWEI,
    BAGUA_FANGWEI,
    FANGWEI_WUXING,
    OCCUPATION_WUXING,
)

logger = logging.getLogger(__name__)


def fengshui_desk_analysis(
    room_direction: str,
    mingua: str,
    occupation_type: str,
    room_size: Optional[Dict] = None,
    existing_furniture: Optional[List] = None,
    include_direction_detail: bool = True,
) -> Dict[str, Any]:
    """
    工位/办公桌摆放优化
    
    Args:
        room_direction: 房间朝向（二十四山）
        mingua: 命卦
        occupation_type: 职业类型（管理/技术/销售/创意/教育/金融/医疗/法律/艺术/餐饮）
        room_size: 房间尺寸 {'width': float, 'length': float}
        existing_furniture: 现有家具位置列表
        include_direction_detail: 是否包含详细朝向分析
    
    Returns:
        {
            'success': bool,
            'desk_position': Dict,     # 最佳桌位位置
            'desk_direction': str,     # 桌面朝向
            'avoid_directions': List,  # 需避开朝向
            'enhancement_items': List, # 增运物品建议
        }
    """
    try:
        logger.info(f"开始工位分析: 朝向{room_direction}, 命卦{mingua}, 职业{occupation_type}")
        
        result = {
            'success': True,
            'room_direction': room_direction,
            'mingua': mingua,
            'occupation_type': occupation_type,
        }
        
        desk_result = calculate_desk_position(
            room_direction, mingua, occupation_type, room_size, existing_furniture
        )
        if desk_result.get('success'):
            result['desk_position'] = desk_result['desk_position']
            result['desk_direction'] = desk_result['desk_direction']
            result['face_direction'] = desk_result.get('face_direction', '')
            result['avoid_directions'] = desk_result['avoid_directions']
            result['enhancement_items'] = desk_result['enhancement_items']
        else:
            result['desk_position'] = {}
            result['desk_direction'] = ''
            result['avoid_directions'] = []
            result['enhancement_items'] = []
        
        occupation_wuxing = OCCUPATION_WUXING.get(occupation_type, '土')
        result['occupation_wuxing'] = occupation_wuxing
        result['occupation_analysis'] = _analyze_occupation(occupation_type, occupation_wuxing)
        
        if include_direction_detail:
            result['direction_analysis'] = _analyze_desk_direction(
                room_direction, mingua, occupation_type
            )
        
        result['layout_suggestions'] = _generate_desk_suggestions(
            result, room_size, existing_furniture
        )
        
        result['taboos'] = _get_desk_taboos(occupation_type)
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"工位分析失败: {error_msg}", exc_info=True)
        return {
            'success': False,
            'error': error_msg,
        }


def _analyze_occupation(occupation_type: str, wuxing: str) -> Dict[str, Any]:
    """
    分析职业特点与五行关系
    """
    occupation_info = {
        '管理': {
            'wuxing': '土',
            'traits': ['稳重', '统筹', '决策'],
            'suitable_direction': ['西南', '东北'],
            'suitable_color': ['黄色', '棕色'],
            'suitable_shape': '方形',
            'enhance_tip': '适合在土位办公，使用方形办公桌',
        },
        '技术': {
            'wuxing': '金',
            'traits': ['精确', '逻辑', '创新'],
            'suitable_direction': ['西', '西北'],
            'suitable_color': ['白色', '金色', '银色'],
            'suitable_shape': '圆形',
            'enhance_tip': '适合在金位办公，保持环境整洁',
        },
        '销售': {
            'wuxing': '水',
            'traits': ['灵活', '沟通', '流动'],
            'suitable_direction': ['北'],
            'suitable_color': ['黑色', '蓝色'],
            'suitable_shape': '波浪形',
            'enhance_tip': '适合在水位办公，放置流水摆件',
        },
        '创意': {
            'wuxing': '木',
            'traits': ['创新', '灵感', '成长'],
            'suitable_direction': ['东', '东南'],
            'suitable_color': ['绿色', '青色'],
            'suitable_shape': '长方形',
            'enhance_tip': '适合在木位办公，放置绿植',
        },
        '教育': {
            'wuxing': '木',
            'traits': ['培养', '引导', '传播'],
            'suitable_direction': ['东', '东南'],
            'suitable_color': ['绿色', '蓝色'],
            'suitable_shape': '长方形',
            'enhance_tip': '适合在文昌位办公，放置书籍',
        },
        '金融': {
            'wuxing': '金',
            'traits': ['精确', '保守', '积累'],
            'suitable_direction': ['西', '西北'],
            'suitable_color': ['金色', '白色'],
            'suitable_shape': '圆形',
            'enhance_tip': '适合在财位办公，放置招财物',
        },
        '医疗': {
            'wuxing': '水',
            'traits': ['治愈', '关怀', '流动'],
            'suitable_direction': ['北'],
            'suitable_color': ['白色', '蓝色'],
            'suitable_shape': '波浪形',
            'enhance_tip': '适合在水位办公，保持环境清洁',
        },
        '法律': {
            'wuxing': '金',
            'traits': ['公正', '严谨', '权威'],
            'suitable_direction': ['西', '西北'],
            'suitable_color': ['白色', '银色'],
            'suitable_shape': '方形',
            'enhance_tip': '适合在金位办公，摆放金属装饰',
        },
        '艺术': {
            'wuxing': '火',
            'traits': ['创造', '热情', '表达'],
            'suitable_direction': ['南'],
            'suitable_color': ['红色', '紫色'],
            'suitable_shape': '三角形',
            'enhance_tip': '适合在火位办公，保持光线充足',
        },
        '餐饮': {
            'wuxing': '火',
            'traits': ['热情', '服务', '创造'],
            'suitable_direction': ['南'],
            'suitable_color': ['红色', '橙色'],
            'suitable_shape': '三角形',
            'enhance_tip': '适合在火位办公，注意通风',
        },
    }
    
    return occupation_info.get(occupation_type, occupation_info['管理'])


def _analyze_desk_direction(
    room_direction: str,
    mingua: str,
    occupation_type: str,
) -> Dict[str, Any]:
    """
    分析办公桌朝向
    """
    from core.tools.fengshui_calculator import shan_to_gua
    
    room_gua = shan_to_gua(room_direction)
    ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
    
    best_face_directions = []
    for ji_name, gua in ji_fangwei.items():
        fangwei = BAGUA_FANGWEI.get(gua, '')
        best_face_directions.append({
            'direction': fangwei,
            'gua': gua,
            'type': ji_name,
            'score': 100 if ji_name == '生气' else (80 if ji_name == '天医' else 60),
        })
    
    best_face_directions.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'room_direction': room_direction,
        'room_gua': room_gua,
        'best_face_directions': best_face_directions[:3],
        'recommended_face': best_face_directions[0] if best_face_directions else None,
    }


def _generate_desk_suggestions(
    result: Dict,
    room_size: Optional[Dict],
    existing_furniture: Optional[List],
) -> List[str]:
    """
    生成办公桌摆放建议
    """
    suggestions = []
    
    desk_position = result.get('desk_position', {})
    if desk_position.get('area'):
        suggestions.append(f"建议将办公桌放置在房间的{desk_position['area']}方位")
    
    if result.get('desk_direction'):
        suggestions.append(f"办公桌面朝向建议为{result['desk_direction']}方向")
    
    avoid_directions = result.get('avoid_directions', [])
    for avoid in avoid_directions[:2]:
        suggestions.append(f"避免面向{avoid['direction']}方向（{avoid['reason']}）")
    
    enhancement_items = result.get('enhancement_items', [])
    if enhancement_items:
        item_names = [item['item'] for item in enhancement_items[:2]]
        suggestions.append(f"建议在办公桌上摆放：{', '.join(item_names)}")
    
    if room_size:
        width = room_size.get('width', 0)
        length = room_size.get('length', 0)
        if width and length:
            suggestions.append(f"房间尺寸{width}x{length}米，建议办公桌靠墙摆放以增加活动空间")
    
    if existing_furniture and len(existing_furniture) > 3:
        suggestions.append("房间家具较多，建议保持办公区域通透，避免杂物堆积")
    
    return suggestions


def _get_desk_taboos(occupation_type: str) -> List[str]:
    """
    获取办公桌摆放禁忌
    """
    common_taboos = [
        '办公桌不宜正对门口，易受冲煞',
        '办公桌不宜背对窗户，不利事业稳定',
        '办公桌上方不宜有横梁压顶',
        '办公桌不宜正对卫生间方向',
        '办公桌不宜摆在走道尽头',
    ]
    
    occupation_taboos = {
        '管理': ['办公桌不宜过小，影响威严', '背后宜有靠山（墙或柜）'],
        '技术': ['办公桌不宜靠近嘈杂区域', '保持桌面整洁有序'],
        '销售': ['办公桌不宜背对门', '可面向门口或窗户'],
        '创意': ['办公桌不宜过于规整', '可增加创意装饰元素'],
        '教育': ['办公桌宜靠近书架', '避免面对镜子'],
        '金融': ['办公桌宜稳重，不宜过多装饰', '背后必须有实墙'],
        '医疗': ['办公桌宜保持清洁', '避免杂物堆积'],
        '法律': ['办公桌宜庄重', '文件摆放要有条理'],
        '艺术': ['办公桌可富有个性', '保持光线充足'],
        '餐饮': ['办公桌宜远离油烟区', '保持通风'],
    }
    
    return common_taboos + occupation_taboos.get(occupation_type, [])
