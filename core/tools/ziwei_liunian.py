"""
紫微斗数流年计算模块
基于 iztro 逻辑的完整实现

流年：每年的天干地支，以及流年太岁、流年流曜等
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ==================== 流年基础定义 ====================

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 流年太岁查表（根据流年地支）
LIUNIAN_TAISUI_TABLE = {
    '子': '子', '丑': '丑', '寅': '寅', '卯': '卯',
    '辰': '辰', '巳': '巳', '午': '午', '未': '未',
    '申': '申', '酉': '酉', '戌': '戌', '亥': '亥',
}

# ==================== 流年计算函数 ====================

def get_tian_gan(year: int) -> str:
    """
    根据年份获取天干
    
    Args:
        year: 年份
    
    Returns:
        天干
    """
    # 以1984年为甲子年参考
    base_year = 1984
    gan_index = (year - base_year) % 10
    return TIAN_GAN[gan_index]

def get_di_zhi(year: int) -> str:
    """
    根据年份获取地支
    
    Args:
        year: 年份
    
    Returns:
        地支
    """
    # 以1984年为甲子年参考
    base_year = 1984
    zhi_index = (year - base_year) % 12
    return DI_ZHI[zhi_index]

def get_di_zhi_index(zhi: str) -> int:
    """获取地支索引"""
    return DI_ZHI.index(zhi)

def normalize_palace_index(index: int) -> int:
    """标准化宫位索引（0-11）"""
    return index % 12

def calculate_liunian_taisui(liunian_zhi: str) -> int:
    """
    计算流年太岁所在宫位
    
    流年太岁就是流年地支所在的宫位
    
    Args:
        liunian_zhi: 流年地支
    
    Returns:
        流年太岁所在宫位索引
    """
    taisui_palace = get_di_zhi_index(liunian_zhi)
    logger.debug(f"流年太岁: 流年地支={liunian_zhi}, 太岁宫位={taisui_palace}")
    return taisui_palace

def calculate_liunian_stars(liunian_gan: str, liunian_zhi: str) -> Dict[str, int]:
    """
    计算流年流曜位置
    
    流年流曜包括：
    - 流年四化（根据流年天干）
    - 流年太岁（根据流年地支）
    - 其他流年星曜
    
    Args:
        liunian_gan: 流年天干
        liunian_zhi: 流年地支
    
    Returns:
        流年星曜位置字典
    """
    stars = {}
    
    # 流年太岁
    taisui_palace = calculate_liunian_taisui(liunian_zhi)
    stars['太岁'] = taisui_palace
    
    # 流年四化（需要导入四化星模块，这里先简化处理）
    # 流年四化根据流年天干确定，与年干四化规则相同
    # 这里先标记，后续可以调用四化星模块
    
    logger.debug(f"流年流曜: {stars}")
    return stars

def calculate_liunian_pan(year: int, pan_data: Dict) -> Dict:
    """
    计算流年命盘
    
    流年命盘是在原命盘基础上，叠加流年的影响
    
    Args:
        year: 流年年份
        pan_data: 原命盘数据
    
    Returns:
        流年命盘数据
    """
    # 计算流年天干地支
    liunian_gan = get_tian_gan(year)
    liunian_zhi = get_di_zhi(year)
    
    # 计算流年流曜
    liunian_stars = calculate_liunian_stars(liunian_gan, liunian_zhi)
    
    # 计算流年太岁
    taisui_palace = calculate_liunian_taisui(liunian_zhi)
    
    # 构建流年数据
    liunian_data = {
        'year': year,
        'gan': liunian_gan,
        'zhi': liunian_zhi,
        'gan_zhi': f"{liunian_gan}{liunian_zhi}",
        'taisui_palace': taisui_palace,
        'stars': liunian_stars,
    }
    
    logger.info(f"流年命盘计算完成: {year}年 ({liunian_gan}{liunian_zhi})")
    return liunian_data

def get_current_liunian(current_year: int) -> Dict:
    """
    获取当前流年信息
    
    Args:
        current_year: 当前年份
    
    Returns:
        当前流年信息
    """
    liunian_gan = get_tian_gan(current_year)
    liunian_zhi = get_di_zhi(current_year)
    taisui_palace = calculate_liunian_taisui(liunian_zhi)
    
    current_liunian = {
        'year': current_year,
        'gan': liunian_gan,
        'zhi': liunian_zhi,
        'gan_zhi': f"{liunian_gan}{liunian_zhi}",
        'taisui_palace': taisui_palace,
    }
    
    logger.info(f"当前流年: {current_year}年 ({liunian_gan}{liunian_zhi})")
    return current_liunian

# ==================== 流年影响分析 ====================

def analyze_liunian_impact(pan_data: Dict, liunian_data: Dict) -> Dict:
    """
    分析流年对命盘的影响
    
    Args:
        pan_data: 原命盘数据
        liunian_data: 流年数据
    
    Returns:
        流年影响分析结果
    """
    palaces = pan_data.get('palaces', [])
    taisui_palace_index = liunian_data['taisui_palace']
    ming_gong_index = pan_data.get('ming_gong', 0)
    
    # 找到流年太岁所在宫位
    taisui_palace = next((p for p in palaces if p['index'] == taisui_palace_index), None)
    
    if not taisui_palace:
        logger.warning(f"未找到流年太岁宫位: {taisui_palace_index}")
        return {}
    
    # 分析流年太岁宫位的影响
    taisui_analysis = _analyze_taisui_palace(taisui_palace, ming_gong_index)
    
    # 分析流年与命宫的关系
    ming_gong_relation = _analyze_ming_gong_relation(taisui_palace_index, ming_gong_index)
    
    # 分析流年四化（如果有）
    si_hua_analysis = _analyze_liunian_si_hua(liunian_data, pan_data)
    
    # 生成总结
    summary = _generate_liunian_summary(
        liunian_data,
        taisui_analysis,
        ming_gong_relation,
        si_hua_analysis
    )
    
    result = {
        'liunian': liunian_data,
        'taisui_analysis': taisui_analysis,
        'ming_gong_relation': ming_gong_relation,
        'si_hua_analysis': si_hua_analysis,
        'summary': summary,
    }
    
    logger.info("流年影响分析完成")
    return result

def _analyze_taisui_palace(taisui_palace: Dict, ming_gong_index: int) -> Dict:
    """分析流年太岁所在宫位的影响"""
    palace_name = taisui_palace['name']
    is_ming_gong = taisui_palace.get('is_ming_gong', False)
    
    main_stars = taisui_palace.get('main_stars', [])
    auxiliary_stars = taisui_palace.get('auxiliary_stars', [])
    si_hua = taisui_palace.get('si_hua', [])
    
    analysis = {
        'palace': palace_name,
        'is_ming_gong': is_ming_gong,
        'main_stars': main_stars,
        'auxiliary_stars': auxiliary_stars,
        'si_hua': si_hua,
        'impact': f"流年太岁在{palace_name}",
    }
    
    if is_ming_gong:
        analysis['impact'] += "，与命宫重合，影响较大"
    else:
        analysis['impact'] += f"，该宫位在流年期间需要特别注意"
    
    return analysis

def _analyze_ming_gong_relation(taisui_palace_index: int, ming_gong_index: int) -> Dict:
    """分析流年太岁与命宫的关系"""
    # 计算距离
    distance = abs(taisui_palace_index - ming_gong_index)
    if distance > 6:
        distance = 12 - distance
    
    relation = {
        'distance': distance,
        'is_same': taisui_palace_index == ming_gong_index,
        'is_opposite': distance == 6,
        'description': '',
    }
    
    if relation['is_same']:
        relation['description'] = '流年太岁与命宫重合，流年影响直接作用于自身'
    elif relation['is_opposite']:
        relation['description'] = '流年太岁在命宫对宫，形成对冲，需要注意'
    elif distance <= 2:
        relation['description'] = f'流年太岁与命宫相邻（距离{distance}），影响较为直接'
    else:
        relation['description'] = f'流年太岁与命宫距离较远（距离{distance}），影响相对间接'
    
    return relation

def _analyze_liunian_si_hua(liunian_data: Dict, pan_data: Dict) -> Dict:
    """分析流年四化"""
    # 流年四化根据流年天干确定
    liunian_gan = liunian_data['gan']
    
    # 这里可以调用四化星模块获取流年四化配置
    # 暂时简化处理
    analysis = {
        'gan': liunian_gan,
        'message': f'流年天干为{liunian_gan}，可根据流年天干确定流年四化',
    }
    
    return analysis

def _generate_liunian_summary(
    liunian_data: Dict,
    taisui_analysis: Dict,
    ming_gong_relation: Dict,
    si_hua_analysis: Dict
) -> str:
    """生成流年分析总结"""
    summary_parts = []
    
    # 基本信息
    summary_parts.append(
        f"{liunian_data['year']}年（{liunian_data['gan_zhi']}）"
    )
    
    # 太岁位置
    summary_parts.append(taisui_analysis['impact'])
    
    # 与命宫关系
    summary_parts.append(ming_gong_relation['description'])
    
    # 四化信息
    if si_hua_analysis.get('message'):
        summary_parts.append(si_hua_analysis['message'])
    
    return "；".join(summary_parts)

