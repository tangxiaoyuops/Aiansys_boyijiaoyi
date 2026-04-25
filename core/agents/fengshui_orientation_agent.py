"""
风水朝向定位Agent
实现八宅命卦计算、朝向评分、玄空飞星等功能
"""
from typing import Dict, Any, Optional
import logging

from core.tools.fengshui_calculator import (
    calculate_bazhai_mingua,
    calculate_orientation_score,
    calculate_xuankong_feixing,
    calculate_yearly_feixing,
    shan_to_gua,
    BAGUA_FANGWEI,
)

logger = logging.getLogger(__name__)


def fengshui_orientation_analysis(
    birth_year: int,
    gender: str,
    house_direction: str,
    include_bazhai: bool = True,
    include_xuankong: bool = True,
    construction_year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    朝向与坐山立向分析
    
    Args:
        birth_year: 出生年份（公历）
        gender: 性别（'男' 或 '女'）
        house_direction: 房屋朝向（二十四山）
        include_bazhai: 是否包含八宅分析
        include_xuankong: 是否包含玄空飞星
        construction_year: 建造年份（用于飞星计算）
    
    Returns:
        {
            'success': bool,
            'mingua': str,              # 命卦
            'dong_si_xi_si': str,       # 东四/西四命
            'ji_fangwei': Dict,         # 四吉方位
            'xiong_fangwei': Dict,      # 四凶方位
            'orientation_score': float, # 朝向适配评分
            'feixing_pan': Dict,        # 飞星盘（可选）
        }
    """
    try:
        logger.info(f"开始朝向分析: 出生{birth_year}年, 性别{gender}, 朝向{house_direction}")
        
        result = {
            'success': True,
            'birth_year': birth_year,
            'gender': gender,
            'house_direction': house_direction,
        }
        
        if include_bazhai:
            mingua_result = calculate_bazhai_mingua(birth_year, gender)
            if mingua_result.get('success'):
                result['mingua'] = mingua_result['mingua']
                result['mingua_number'] = mingua_result['mingua_number']
                result['dong_si_xi_si'] = mingua_result['dong_si_xi_si']
                result['ji_fangwei'] = mingua_result['ji_fangwei']
                result['xiong_fangwei'] = mingua_result['xiong_fangwei']
                result['mingua_wuxing'] = mingua_result['wuxing']
                
                orientation_result = calculate_orientation_score(house_direction, mingua_result['mingua'])
                if orientation_result.get('success'):
                    result['orientation_score'] = orientation_result['score']
                    result['orientation_level'] = orientation_result['level']
                    result['orientation_analysis'] = orientation_result['analysis']
                    result['orientation_suggestions'] = orientation_result['suggestions']
            else:
                result['mingua_error'] = mingua_result.get('error', '命卦计算失败')
        
        house_gua = shan_to_gua(house_direction)
        result['house_gua'] = house_gua
        result['house_fangwei'] = BAGUA_FANGWEI.get(house_gua, '')
        
        if include_xuankong and construction_year:
            zuo_shan = _get_opposite_shan(house_direction)
            feixing_result = calculate_xuankong_feixing(construction_year, zuo_shan, house_direction)
            if feixing_result.get('success'):
                result['feixing_pan'] = feixing_result
        
        import datetime
        current_year = datetime.datetime.now().year
        yearly_feixing = calculate_yearly_feixing(current_year)
        if yearly_feixing.get('success'):
            result['yearly_feixing'] = yearly_feixing
        
        result['orientation_tips'] = _generate_orientation_tips(result)
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"朝向分析失败: {error_msg}", exc_info=True)
        return {
            'success': False,
            'error': error_msg,
        }


def _get_opposite_shan(shan: str) -> str:
    """获取对向山"""
    opposite_map = {
        '壬': '丙', '子': '午', '癸': '丁',
        '丑': '未', '艮': '坤', '寅': '申',
        '甲': '庚', '卯': '酉', '乙': '辛',
        '辰': '戌', '巽': '乾', '巳': '亥',
        '丙': '壬', '午': '子', '丁': '癸',
        '未': '丑', '坤': '艮', '申': '寅',
        '庚': '甲', '酉': '卯', '辛': '乙',
        '戌': '辰', '乾': '巽', '亥': '巳',
    }
    return opposite_map.get(shan, '子')


def _generate_orientation_tips(result: Dict) -> Dict[str, Any]:
    """
    生成朝向提示信息
    """
    tips = {
        'best_directions': [],
        'avoid_directions': [],
        'general_advice': [],
    }
    
    if 'ji_fangwei' in result:
        for name, info in result['ji_fangwei'].items():
            if info.get('gua'):
                tips['best_directions'].append({
                    'name': name,
                    'direction': info.get('fangwei', ''),
                    'gua': info.get('gua', ''),
                })
    
    if 'xiong_fangwei' in result:
        for name, info in result['xiong_fangwei'].items():
            if info.get('gua'):
                tips['avoid_directions'].append({
                    'name': name,
                    'direction': info.get('fangwei', ''),
                    'gua': info.get('gua', ''),
                })
    
    if 'orientation_level' in result:
        level = result['orientation_level']
        if level in ['优秀', '良好']:
            tips['general_advice'].append("当前朝向与命卦配合良好，可安心居住")
            tips['general_advice'].append("建议在吉位布置重要活动区域")
        elif level == '一般':
            tips['general_advice'].append("朝向适中，可通过室内布局优化")
            tips['general_advice'].append("建议重点利用吉方位，避开凶方位")
        else:
            tips['general_advice'].append("朝向与命卦存在冲克，需要化解")
            tips['general_advice'].append("建议在凶位放置化解物品")
    
    return tips
