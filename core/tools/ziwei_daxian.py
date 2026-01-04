"""
紫微斗数大限计算模块
基于 iztro 逻辑的完整实现

大限：每10年一个大限，从命宫开始，根据性别和年干阴阳决定顺逆
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ==================== 大限基础定义 ====================

# 天干阴阳属性
TIAN_GAN_YIN_YANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
    '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
    '壬': '阳', '癸': '阴',
}

# 大限年龄范围（每个大限10年）
DAXIAN_AGE_RANGES = [
    (0, 9),    # 第1大限：0-9岁
    (10, 19),  # 第2大限：10-19岁
    (20, 29),  # 第3大限：20-29岁
    (30, 39),  # 第4大限：30-39岁
    (40, 49),  # 第5大限：40-49岁
    (50, 59),  # 第6大限：50-59岁
    (60, 69),  # 第7大限：60-69岁
    (70, 79),  # 第8大限：70-79岁
    (80, 89),  # 第9大限：80-89岁
    (90, 99),  # 第10大限：90-99岁
]

# ==================== 大限计算函数 ====================

def get_tian_gan_yin_yang(year_gan: str) -> str:
    """
    获取天干的阴阳属性
    
    Args:
        year_gan: 年干
    
    Returns:
        '阳' 或 '阴'
    """
    return TIAN_GAN_YIN_YANG.get(year_gan, '阳')

def determine_daxian_direction(year_gan: str, gender: str) -> str:
    """
    确定大限的顺逆方向
    
    规则：
    - 阳男阴女：顺行（顺时针）
    - 阴男阳女：逆行（逆时针）
    
    Args:
        year_gan: 年干
        gender: 性别（'男' 或 '女'）
    
    Returns:
        '顺' 或 '逆'
    """
    yin_yang = get_tian_gan_yin_yang(year_gan)
    is_male = gender == '男'
    
    # 阳男阴女：顺行
    # 阴男阳女：逆行
    if (yin_yang == '阳' and is_male) or (yin_yang == '阴' and not is_male):
        direction = '顺'
    else:
        direction = '逆'
    
    logger.debug(f"大限方向: 年干={year_gan}({yin_yang}), 性别={gender}, 方向={direction}")
    return direction

def calculate_daxian_start_age(birth_year: int, current_year: int) -> int:
    """
    计算当前年龄对应的起始大限年龄
    
    大限从出生年份开始，每10年一个大限
    
    Args:
        birth_year: 出生年份
        current_year: 当前年份（或查询年份）
    
    Returns:
        当前大限的起始年龄
    """
    age = current_year - birth_year
    # 计算是第几个大限（从0开始）
    daxian_index = age // 10
    # 该大限的起始年龄
    start_age = daxian_index * 10
    
    logger.debug(f"年龄={age}, 大限索引={daxian_index}, 起始年龄={start_age}")
    return start_age

def calculate_daxian_palace(ming_gong: int, daxian_index: int, direction: str) -> int:
    """
    计算指定大限对应的宫位
    
    大限从命宫开始，根据顺逆方向依次排布
    
    Args:
        ming_gong: 命宫索引
        daxian_index: 大限索引（0-9，0表示第1大限）
        direction: 方向（'顺' 或 '逆'）
    
    Returns:
        大限所在宫位索引
    """
    if direction == '顺':
        # 顺时针：命宫 + 大限索引
        palace = (ming_gong + daxian_index) % 12
    else:
        # 逆时针：命宫 - 大限索引
        palace = (ming_gong - daxian_index) % 12
    
    logger.debug(f"大限{daxian_index+1}: 命宫={ming_gong}, 方向={direction}, 宫位={palace}")
    return palace

def calculate_all_daxian(ming_gong: int, direction: str) -> List[Dict]:
    """
    计算所有大限的排布
    
    Args:
        ming_gong: 命宫索引
        direction: 方向（'顺' 或 '逆'）
    
    Returns:
        所有大限的列表，每个大限包含：索引、年龄范围、宫位索引
    """
    all_daxian = []
    
    for i in range(len(DAXIAN_AGE_RANGES)):
        age_range = DAXIAN_AGE_RANGES[i]
        palace = calculate_daxian_palace(ming_gong, i, direction)
        
        daxian_info = {
            'index': i,
            'number': i + 1,  # 第几大限（从1开始）
            'start_age': age_range[0],
            'end_age': age_range[1],
            'palace': palace,
            'direction': direction,
        }
        all_daxian.append(daxian_info)
    
    logger.debug(f"计算完成，共{len(all_daxian)}个大限")
    return all_daxian

def get_current_daxian(birth_year: int, current_year: int, ming_gong: int, direction: str) -> Dict:
    """
    获取当前大限信息
    
    Args:
        birth_year: 出生年份
        current_year: 当前年份（或查询年份）
        ming_gong: 命宫索引
        direction: 方向（'顺' 或 '逆'）
    
    Returns:
        当前大限的详细信息
    """
    age = current_year - birth_year
    
    # 计算当前是第几个大限（从0开始）
    daxian_index = age // 10
    if daxian_index >= len(DAXIAN_AGE_RANGES):
        daxian_index = len(DAXIAN_AGE_RANGES) - 1  # 限制在最后一个大限
    
    age_range = DAXIAN_AGE_RANGES[daxian_index]
    palace = calculate_daxian_palace(ming_gong, daxian_index, direction)
    
    current_daxian = {
        'index': daxian_index,
        'number': daxian_index + 1,
        'start_age': age_range[0],
        'end_age': age_range[1],
        'current_age': age,
        'palace': palace,
        'direction': direction,
        'years_remaining': age_range[1] - age,  # 该大限剩余年数
    }
    
    logger.info(f"当前大限: 第{current_daxian['number']}大限, "
                f"年龄={age}岁, 宫位={palace}, "
                f"剩余{current_daxian['years_remaining']}年")
    
    return current_daxian

# ==================== 大限影响分析 ====================

def analyze_daxian_impact(pan_data: Dict, current_daxian: Dict) -> Dict:
    """
    分析大限对命盘的影响
    
    Args:
        pan_data: 命盘数据
        current_daxian: 当前大限信息
    
    Returns:
        大限影响分析结果
    """
    palaces = pan_data.get('palaces', [])
    daxian_palace_index = current_daxian['palace']
    
    # 找到大限所在宫位
    daxian_palace = next((p for p in palaces if p['index'] == daxian_palace_index), None)
    
    if not daxian_palace:
        logger.warning(f"未找到大限宫位: {daxian_palace_index}")
        return {}
    
    # 分析大限宫位的星曜
    main_stars = daxian_palace.get('main_stars', [])
    auxiliary_stars = daxian_palace.get('auxiliary_stars', [])
    si_hua = daxian_palace.get('si_hua', [])
    
    # 分析主星影响
    main_star_analysis = _analyze_main_stars_in_daxian(main_stars)
    
    # 分析辅星影响
    auxiliary_star_analysis = _analyze_auxiliary_stars_in_daxian(auxiliary_stars)
    
    # 分析四化影响
    si_hua_analysis = _analyze_si_hua_in_daxian(si_hua)
    
    # 生成总结
    summary = _generate_daxian_summary(
        current_daxian,
        daxian_palace,
        main_star_analysis,
        auxiliary_star_analysis,
        si_hua_analysis
    )
    
    result = {
        'current_daxian': current_daxian,
        'palace': {
            'name': daxian_palace['name'],
            'index': daxian_palace_index,
            'main_stars': main_stars,
            'auxiliary_stars': auxiliary_stars,
            'si_hua': si_hua,
        },
        'analysis': {
            'main_stars': main_star_analysis,
            'auxiliary_stars': auxiliary_star_analysis,
            'si_hua': si_hua_analysis,
        },
        'summary': summary,
    }
    
    logger.info("大限影响分析完成")
    return result

def _analyze_main_stars_in_daxian(main_stars: List[str]) -> Dict:
    """分析大限宫位的主星影响"""
    if not main_stars:
        return {'message': '大限宫位无主星，影响较为平淡'}
    
    # 重要主星的影响
    important_stars = ['紫微', '天府', '太阳', '太阴', '武曲', '天同']
    
    analysis = {
        'stars': main_stars,
        'has_important_stars': any(star in important_stars for star in main_stars),
        'impact': f"大限宫位有{len(main_stars)}个主星：{', '.join(main_stars)}",
    }
    
    return analysis

def _analyze_auxiliary_stars_in_daxian(auxiliary_stars: List[str]) -> Dict:
    """分析大限宫位的辅星影响"""
    if not auxiliary_stars:
        return {'message': '大限宫位无辅星'}
    
    # 区分吉星和煞星
    lucky_stars = ['左辅', '右弼', '文曲', '文昌', '天魁', '天钺']
    evil_stars = ['擎羊', '陀罗', '火星', '铃星', '地空', '地劫']
    
    lucky_count = sum(1 for star in auxiliary_stars if star in lucky_stars)
    evil_count = sum(1 for star in auxiliary_stars if star in evil_stars)
    
    analysis = {
        'stars': auxiliary_stars,
        'lucky_count': lucky_count,
        'evil_count': evil_count,
        'impact': f"大限宫位有{len(auxiliary_stars)}个辅星（{lucky_count}个吉星，{evil_count}个煞星）",
    }
    
    return analysis

def _analyze_si_hua_in_daxian(si_hua: List[str]) -> Dict:
    """分析大限宫位的四化影响"""
    if not si_hua:
        return {'message': '大限宫位无四化'}
    
    analysis = {
        'si_hua': si_hua,
        'has_hua_lu': '化禄' in si_hua,
        'has_hua_quan': '化权' in si_hua,
        'has_hua_ke': '化科' in si_hua,
        'has_hua_ji': '化忌' in si_hua,
        'impact': f"大限宫位有四化：{', '.join(si_hua)}",
    }
    
    if '化忌' in si_hua:
        analysis['warning'] = '⚠️ 大限宫位有化忌，需要特别注意'
    
    return analysis

def _generate_daxian_summary(
    current_daxian: Dict,
    daxian_palace: Dict,
    main_star_analysis: Dict,
    auxiliary_star_analysis: Dict,
    si_hua_analysis: Dict
) -> str:
    """生成大限分析总结"""
    summary_parts = []
    
    # 基本信息
    summary_parts.append(
        f"当前处于第{current_daxian['number']}大限"
        f"（{current_daxian['start_age']}-{current_daxian['end_age']}岁），"
        f"大限在{daxian_palace['name']}"
    )
    
    # 主星影响
    if main_star_analysis.get('stars'):
        summary_parts.append(f"大限宫位有主星：{', '.join(main_star_analysis['stars'])}")
    
    # 辅星影响
    if auxiliary_star_analysis.get('stars'):
        lucky = auxiliary_star_analysis.get('lucky_count', 0)
        evil = auxiliary_star_analysis.get('evil_count', 0)
        if lucky > 0:
            summary_parts.append(f"有{lucky}个吉星助力")
        if evil > 0:
            summary_parts.append(f"有{evil}个煞星需要注意")
    
    # 四化影响
    if si_hua_analysis.get('si_hua'):
        summary_parts.append(f"四化：{', '.join(si_hua_analysis['si_hua'])}")
        if si_hua_analysis.get('has_hua_ji'):
            summary_parts.append("⚠️ 特别注意化忌的影响")
    
    return "；".join(summary_parts)

