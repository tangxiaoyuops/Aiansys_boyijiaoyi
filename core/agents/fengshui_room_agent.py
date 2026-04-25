"""
风水房间功能定位Agent
根据命卦和飞星盘分析各房间的最佳位置
"""
from typing import Dict, Any, List, Optional
import logging

from core.tools.fengshui_calculator import (
    calculate_room_position,
    BAZHAI_JI_FANGWEI,
    BAZHAI_XIONG_FANGWEI,
    BAGUA_FANGWEI,
    ROOM_BAGUA_MAP,
)

logger = logging.getLogger(__name__)


def fengshui_room_analysis(
    house_layout: Dict,
    mingua: str,
    room_types: List[str],
    include_feixing: bool = True,
    feixing_pan: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    房间功能定位分析
    
    Args:
        house_layout: 房屋布局信息
        mingua: 命卦
        room_types: 需定位的房间类型列表
        include_feixing: 是否结合飞星分析
        feixing_pan: 飞星盘数据（可选）
    
    Returns:
        {
            'success': bool,
            'room_positions': Dict,    # 各房间建议位置
            'priority_order': List,    # 房间优先级排序
            'avoid_positions': List,   # 需避开的位置
            'detailed_analysis': Dict, # 详细分析
        }
    """
    try:
        logger.info(f"开始房间定位分析: 命卦{mingua}, 房间类型{room_types}")
        
        result = {
            'success': True,
            'mingua': mingua,
            'room_types': room_types,
        }
        
        room_result = calculate_room_position(mingua, house_layout, room_types)
        if room_result.get('success'):
            result['room_positions'] = room_result['room_positions']
            result['priority_order'] = room_result['priority_order']
            result['avoid_positions'] = room_result['avoid_positions']
        else:
            result['room_positions'] = {}
            result['priority_order'] = room_types
            result['avoid_positions'] = []
        
        result['ji_fangwei'] = BAZHAI_JI_FANGWEI.get(mingua, {})
        result['xiong_fangwei'] = BAZHAI_XIONG_FANGWEI.get(mingua, {})
        
        result['detailed_analysis'] = _generate_detailed_analysis(
            mingua, room_types, result.get('room_positions', {}), feixing_pan
        )
        
        result['room_recommendations'] = _generate_room_recommendations(
            mingua, room_types, result.get('room_positions', {})
        )
        
        result['bagua_room_map'] = _get_bagua_room_suitability(mingua)
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"房间定位分析失败: {error_msg}", exc_info=True)
        return {
            'success': False,
            'error': error_msg,
        }


def _generate_detailed_analysis(
    mingua: str,
    room_types: List[str],
    room_positions: Dict,
    feixing_pan: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    生成详细的房间分析
    """
    analysis = {}
    
    room_requirements = {
        '主卧': {
            'requirements': ['安静', '私密', '采光好', '通风'],
            'suitable_gua': ['生气', '天医', '延年', '伏位'],
            'avoid_gua': ['绝命', '五鬼'],
            'description': '主卧室需要安静私密，适合位于吉位',
        },
        '书房': {
            'requirements': ['安静', '采光好', '文昌位'],
            'suitable_gua': ['生气', '伏位', '文昌'],
            'avoid_gua': ['绝命', '六煞'],
            'description': '书房需要安静，利于学习和工作',
        },
        '客厅': {
            'requirements': ['明亮', '宽敞', '通风好'],
            'suitable_gua': ['生气', '延年', '天医'],
            'avoid_gua': ['祸害'],
            'description': '客厅是家庭活动中心，需要明亮宽敞',
        },
        '厨房': {
            'requirements': ['通风', '水源', '火位'],
            'suitable_gua': ['延年', '天医'],
            'avoid_gua': ['生气'],
            'description': '厨房五行属火，需注意火位选择',
        },
        '卫生间': {
            'requirements': ['通风', '隐蔽', '排水'],
            'suitable_gua': ['祸害', '六煞'],
            'avoid_gua': ['生气', '天医', '延年'],
            'description': '卫生间宜设在凶位，压凶化吉',
        },
        '餐厅': {
            'requirements': ['明亮', '通风', '近厨房'],
            'suitable_gua': ['生气', '延年'],
            'avoid_gua': ['绝命'],
            'description': '餐厅需要温馨明亮，促进家庭和谐',
        },
        '儿童房': {
            'requirements': ['安静', '安全', '文昌'],
            'suitable_gua': ['生气', '天医'],
            'avoid_gua': ['绝命', '五鬼'],
            'description': '儿童房需要安全，利于成长学习',
        },
        '老人房': {
            'requirements': ['安静', '采光', '近卫生间'],
            'suitable_gua': ['天医', '延年', '伏位'],
            'avoid_gua': ['绝命'],
            'description': '老人房需要安静祥和，利于健康',
        },
    }
    
    for room_type in room_types:
        room_info = room_requirements.get(room_type, {})
        position_info = room_positions.get(room_type, {})
        
        analysis[room_type] = {
            'requirements': room_info.get('requirements', []),
            'suitable_gua': room_info.get('suitable_gua', []),
            'avoid_gua': room_info.get('avoid_gua', []),
            'description': room_info.get('description', ''),
            'recommended_position': position_info.get('best_position', '待定'),
            'recommended_gua': position_info.get('gua', ''),
            'reason': position_info.get('reason', ''),
        }
    
    return analysis


def _generate_room_recommendations(
    mingua: str,
    room_types: List[str],
    room_positions: Dict,
) -> List[str]:
    """
    生成房间布局建议
    """
    recommendations = []
    
    ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
    
    if '主卧' in room_types:
        pos_info = room_positions.get('主卧', {})
        recommendations.append(f"主卧室建议设置在{pos_info.get('best_position', '吉位')}方位")
    
    if '书房' in room_types:
        pos_info = room_positions.get('书房', {})
        recommendations.append(f"书房建议设置在{pos_info.get('best_position', '文昌位')}方位，利于学业事业")
    
    if '厨房' in room_types:
        recommendations.append("厨房宜设置在延年或天医位，避免设在生气位")
    
    if '卫生间' in room_types:
        recommendations.append("卫生间宜设置在凶位（祸害、六煞），可压凶化吉")
    
    if '客厅' in room_types:
        pos_info = room_positions.get('客厅', {})
        recommendations.append(f"客厅建议设置在{pos_info.get('best_position', '生气位')}方位，明亮宽敞")
    
    return recommendations


def _get_bagua_room_suitability(mingua: str) -> Dict[str, List[str]]:
    """
    获取各卦位的房间适宜性
    """
    ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
    xiong_fangwei = BAZHAI_XIONG_FANGWEI.get(mingua, {})
    
    bagua_map = {}
    
    for gua in ['坎', '离', '震', '巽', '乾', '坤', '艮', '兑']:
        suitable = []
        avoid = []
        
        for ji_name, ji_gua in ji_fangwei.items():
            if ji_gua == gua:
                if ji_name == '生气':
                    suitable.extend(['主卧', '书房', '客厅', '办公室'])
                elif ji_name == '天医':
                    suitable.extend(['主卧', '老人房', '餐厅'])
                elif ji_name == '延年':
                    suitable.extend(['客厅', '餐厅', '主卧'])
                elif ji_name == '伏位':
                    suitable.extend(['书房', '卧室', '储藏室'])
        
        for xiong_name, xiong_gua in xiong_fangwei.items():
            if xiong_gua == gua:
                if xiong_name in ['绝命', '五鬼']:
                    avoid.extend(['主卧', '书房', '儿童房'])
                    suitable.extend(['卫生间', '储藏室'])
                elif xiong_name in ['六煞', '祸害']:
                    avoid.extend(['主卧'])
                    suitable.extend(['卫生间', '厨房'])
        
        bagua_map[gua] = {
            'suitable': list(set(suitable)),
            'avoid': list(set(avoid)),
            'fangwei': BAGUA_FANGWEI.get(gua, ''),
        }
    
    return bagua_map
