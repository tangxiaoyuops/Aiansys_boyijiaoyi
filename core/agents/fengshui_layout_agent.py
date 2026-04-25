"""
风水房屋格局分析Agent
实现缺角凸角检测、流线分析、格局评分等功能
"""
from typing import Dict, Any, List, Optional
import logging

from core.tools.fengshui_calculator import (
    detect_house_defects,
    BAGUA_FANGWEI,
    BAGUA_NUMBER,
)

logger = logging.getLogger(__name__)


def fengshui_layout_analysis(
    house_shape: str,
    house_direction: str,
    room_layout: Optional[Dict] = None,
    include_defect_analysis: bool = True,
    include_liuxian: bool = True,
) -> Dict[str, Any]:
    """
    房屋格局分析
    
    Args:
        house_shape: 房屋形状（'矩形', 'L形', 'U形', '不规则'）
        house_direction: 房屋朝向（二十四山）
        room_layout: 房间布局信息
        include_defect_analysis: 是否包含缺角分析
        include_liuxian: 是否包含流线分析
    
    Returns:
        {
            'success': bool,
            'layout_score': float,      # 格局评分
            'defects': List,            # 缺角凸角问题
            'liuxian_analysis': Dict,   # 流线分析
            'suggestions': List,        # 改善建议
        }
    """
    try:
        logger.info(f"开始格局分析: 形状{house_shape}, 朝向{house_direction}")
        
        result = {
            'success': True,
            'house_shape': house_shape,
            'house_direction': house_direction,
        }
        
        if include_defect_analysis:
            defect_result = detect_house_defects(house_shape, room_layout.get('coordinates') if room_layout else None)
            if defect_result.get('success'):
                result['defects'] = defect_result['defects']
                result['protrusions'] = defect_result['protrusions']
                result['layout_score'] = defect_result['layout_score']
                result['defect_analysis'] = defect_result['analysis']
            else:
                result['defects'] = []
                result['protrusions'] = []
                result['layout_score'] = 75.0
        
        if include_liuxian and room_layout:
            liuxian_result = _analyze_liuxian(room_layout, house_direction)
            result['liuxian_analysis'] = liuxian_result
        else:
            result['liuxian_analysis'] = _get_default_liuxian(house_shape)
        
        result['shape_analysis'] = _analyze_shape(house_shape)
        result['direction_analysis'] = _analyze_direction(house_direction)
        result['suggestions'] = _generate_layout_suggestions(result)
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"格局分析失败: {error_msg}", exc_info=True)
        return {
            'success': False,
            'error': error_msg,
        }


def _analyze_liuxian(room_layout: Dict, house_direction: str) -> Dict[str, Any]:
    """
    分析房屋流线（动线）
    """
    liuxian = {
        'main_entrance': None,
        'living_area': None,
        'private_area': None,
        'service_area': None,
        'flow_quality': '中等',
        'issues': [],
        'recommendations': [],
    }
    
    if 'entrance' in room_layout:
        liuxian['main_entrance'] = room_layout['entrance']
    
    if 'living_room' in room_layout:
        liuxian['living_area'] = room_layout['living_room']
    
    if 'bedrooms' in room_layout:
        liuxian['private_area'] = room_layout['bedrooms']
    
    if 'kitchen' in room_layout or 'bathroom' in room_layout:
        liuxian['service_area'] = {
            'kitchen': room_layout.get('kitchen'),
            'bathroom': room_layout.get('bathroom'),
        }
    
    if liuxian['main_entrance'] and liuxian['living_area']:
        liuxian['flow_quality'] = '良好'
        liuxian['recommendations'].append("入口直通客厅，动线流畅")
    
    return liuxian


def _get_default_liuxian(house_shape: str) -> Dict[str, Any]:
    """
    获取默认流线分析
    """
    defaults = {
        '矩形': {
            'flow_quality': '良好',
            'issues': [],
            'recommendations': ['方正格局，动线清晰', '功能分区明确'],
        },
        'L形': {
            'flow_quality': '中等',
            'issues': ['存在转角区域', '部分空间利用率低'],
            'recommendations': ['转角处可设计储物空间', '注意动静分区'],
        },
        'U形': {
            'flow_quality': '中等',
            'issues': ['内部采光可能受影响', '中心区域利用需注意'],
            'recommendations': ['中心区域可作为庭院或天井', '增加采光设计'],
        },
        '不规则': {
            'flow_quality': '需优化',
            'issues': ['格局不规整', '动线可能混乱'],
            'recommendations': ['通过隔断优化空间', '注意功能分区'],
        },
    }
    return defaults.get(house_shape, defaults['矩形'])


def _analyze_shape(house_shape: str) -> Dict[str, Any]:
    """
    分析房屋形状
    """
    shape_info = {
        '矩形': {
            'score': 100,
            'description': '方正格局，四平八稳',
            'advantages': ['气场流通顺畅', '空间利用率高', '装修布置方便'],
            'disadvantages': [],
        },
        'L形': {
            'score': 75,
            'description': 'L形格局，有缺角',
            'advantages': ['空间层次感强'],
            'disadvantages': ['存在缺角', '部分区域采光可能不足'],
        },
        'U形': {
            'score': 70,
            'description': 'U形格局，有凹位',
            'advantages': ['围合感强', '私密性好'],
            'disadvantages': ['中心采光可能不足', '存在缺角'],
        },
        '不规则': {
            'score': 60,
            'description': '不规则格局，气场不稳',
            'advantages': ['独特空间'],
            'disadvantages': ['气场不稳定', '布局困难', '空间利用率低'],
        },
    }
    return shape_info.get(house_shape, shape_info['矩形'])


def _analyze_direction(house_direction: str) -> Dict[str, Any]:
    """
    分析房屋朝向
    """
    from core.tools.fengshui_calculator import shan_to_gua, FANGWEI_WUXING
    
    gua = shan_to_gua(house_direction)
    fangwei = BAGUA_FANGWEI.get(gua, '北')
    wuxing = FANGWEI_WUXING.get(gua, '水')
    
    direction_info = {
        'direction': house_direction,
        'gua': gua,
        'fangwei': fangwei,
        'wuxing': wuxing,
        'sunlight': _get_sunlight_info(fangwei),
        'ventilation': _get_ventilation_info(fangwei),
    }
    
    return direction_info


def _get_sunlight_info(fangwei: str) -> Dict[str, str]:
    """
    获取采光信息
    """
    sunlight_map = {
        '南': {'quality': '优秀', 'description': '全天采光充足，冬暖夏凉'},
        '东南': {'quality': '优秀', 'description': '早晨采光好，温和舒适'},
        '东': {'quality': '良好', 'description': '早晨采光充足，下午稍暗'},
        '西南': {'quality': '良好', 'description': '下午采光好，夏季较热'},
        '西': {'quality': '一般', 'description': '下午西晒，夏季炎热'},
        '西北': {'quality': '一般', 'description': '下午有阳光，冬季较冷'},
        '北': {'quality': '较差', 'description': '全年采光不足，阴凉'},
        '东北': {'quality': '良好', 'description': '早晨有阳光，较为温和'},
    }
    return sunlight_map.get(fangwei, sunlight_map['北'])


def _get_ventilation_info(fangwei: str) -> Dict[str, str]:
    """
    获取通风信息
    """
    ventilation_map = {
        '南': {'quality': '良好', 'description': '夏季南风凉爽'},
        '东南': {'quality': '优秀', 'description': '通风最佳，空气流通好'},
        '东': {'quality': '良好', 'description': '早晨空气清新'},
        '西南': {'quality': '良好', 'description': '夏季通风良好'},
        '西': {'quality': '一般', 'description': '通风一般，夏季热风'},
        '西北': {'quality': '一般', 'description': '冬季风大，需遮挡'},
        '北': {'quality': '一般', 'description': '冬季北风寒冷，需保温'},
        '东北': {'quality': '良好', 'description': '通风适中，较为舒适'},
    }
    return ventilation_map.get(fangwei, ventilation_map['北'])


def _generate_layout_suggestions(result: Dict) -> List[str]:
    """
    生成格局改善建议
    """
    suggestions = []
    
    house_shape = result.get('house_shape', '矩形')
    layout_score = result.get('layout_score', 100)
    
    if house_shape != '矩形':
        suggestions.append(f"房屋{house_shape}格局存在一定缺陷，建议通过装修化解")
    
    defects = result.get('defects', [])
    for defect in defects:
        if 'suggestion' in defect:
            suggestions.append(defect['suggestion'])
    
    if layout_score < 80:
        suggestions.append("格局评分较低，建议重点优化空间布局")
    
    shape_analysis = result.get('shape_analysis', {})
    for disadvantage in shape_analysis.get('disadvantages', []):
        suggestions.append(f"注意：{disadvantage}")
    
    direction_analysis = result.get('direction_analysis', {})
    sunlight = direction_analysis.get('sunlight', {})
    if sunlight.get('quality') in ['较差', '一般']:
        suggestions.append(f"采光建议：{sunlight.get('description', '')}")
    
    if not suggestions:
        suggestions.append("房屋格局良好，建议保持现有布局")
    
    return suggestions
