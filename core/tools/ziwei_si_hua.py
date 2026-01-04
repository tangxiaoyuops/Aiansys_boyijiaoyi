"""
紫微斗数四化星计算模块
基于 iztro 逻辑的完整实现

四化星：化禄、化权、化科、化忌
根据年干确定哪些星会四化
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ==================== 四化星查表 ====================

# 年干四化表：根据年干确定哪些星会四化
# 格式：年干 -> {化禄: 星名, 化权: 星名, 化科: 星名, 化忌: 星名}
SI_HUA_TABLE = {
    '甲': {
        '化禄': '廉贞',
        '化权': '破军',
        '化科': '武曲',
        '化忌': '太阳',
    },
    '乙': {
        '化禄': '天机',
        '化权': '天梁',
        '化科': '紫微',
        '化忌': '太阴',
    },
    '丙': {
        '化禄': '天同',
        '化权': '天机',
        '化科': '文昌',
        '化忌': '廉贞',
    },
    '丁': {
        '化禄': '太阴',
        '化权': '天同',
        '化科': '天机',
        '化忌': '巨门',
    },
    '戊': {
        '化禄': '贪狼',
        '化权': '太阴',
        '化科': '右弼',
        '化忌': '天机',
    },
    '己': {
        '化禄': '武曲',
        '化权': '贪狼',
        '化科': '天梁',
        '化忌': '文曲',
    },
    '庚': {
        '化禄': '太阳',
        '化权': '武曲',
        '化科': '太阴',
        '化忌': '天同',
    },
    '辛': {
        '化禄': '巨门',
        '化权': '太阳',
        '化科': '文曲',
        '化忌': '文昌',
    },
    '壬': {
        '化禄': '天梁',
        '化权': '紫微',
        '化科': '左辅',
        '化忌': '武曲',
    },
    '癸': {
        '化禄': '破军',
        '化权': '巨门',
        '化科': '太阴',
        '化忌': '贪狼',
    },
}

# 四化星类型
SI_HUA_TYPES = ['化禄', '化权', '化科', '化忌']

# 四化星含义
SI_HUA_MEANINGS = {
    '化禄': '财运、福气、收获',
    '化权': '权力、地位、掌控',
    '化科': '名声、学问、贵人',
    '化忌': '阻碍、损失、困扰',
}

# ==================== 四化星计算函数 ====================

def get_si_hua_stars(year_gan: str) -> Dict[str, str]:
    """
    根据年干获取四化星配置

    Args:
        year_gan: 年干（甲、乙、丙...）

    Returns:
        四化星配置字典：{化禄: 星名, 化权: 星名, 化科: 星名, 化忌: 星名}
    """
    if year_gan not in SI_HUA_TABLE:
        logger.warning(f"未找到年干 {year_gan} 的四化配置，使用默认值")
        return {
            '化禄': '',
            '化权': '',
            '化科': '',
            '化忌': '',
        }

    si_hua = SI_HUA_TABLE[year_gan].copy()
    logger.debug(f"年干 {year_gan} 的四化配置: {si_hua}")
    return si_hua

def apply_si_hua_to_pan(pan_data: Dict, year_gan: str) -> Dict:
    """
    将四化星应用到命盘数据中

    Args:
        pan_data: 命盘数据（来自 create_pan 函数）
        year_gan: 年干

    Returns:
        更新后的命盘数据，包含四化星信息
    """
    # 获取四化星配置
    si_hua_config = get_si_hua_stars(year_gan)

    # 构建星名到四化类型的映射
    star_to_si_hua = {}
    for si_hua_type, star_name in si_hua_config.items():
        if star_name:
            star_to_si_hua[star_name] = si_hua_type

    # 初始化四化星数据
    si_hua_data = {
        '化禄': [],
        '化权': [],
        '化科': [],
        '化忌': [],
    }

    # 遍历所有宫位，标记四化星
    for palace in pan_data.get('palaces', []):
        palace_si_hua = []

        # 检查主星是否有四化
        for star in palace.get('main_stars', []):
            if star in star_to_si_hua:
                si_hua_type = star_to_si_hua[star]
                palace_si_hua.append(si_hua_type)
                si_hua_data[si_hua_type].append({
                    'palace': palace['name'],
                    'star': star,
                })

        # 检查辅星是否有四化
        for star in palace.get('auxiliary_stars', []):
            if star in star_to_si_hua:
                si_hua_type = star_to_si_hua[star]
                palace_si_hua.append(si_hua_type)
                si_hua_data[si_hua_type].append({
                    'palace': palace['name'],
                    'star': star,
                })

        # 将四化信息添加到宫位数据中
        palace['si_hua'] = palace_si_hua

    # 将四化数据添加到命盘数据中
    pan_data['si_hua'] = {
        'config': si_hua_config,
        'data': si_hua_data,
        'star_to_si_hua': star_to_si_hua,
    }

    logger.info(f"四化星已应用到命盘: {len(si_hua_data['化禄'])}个化禄, "
                f"{len(si_hua_data['化权'])}个化权, "
                f"{len(si_hua_data['化科'])}个化科, "
                f"{len(si_hua_data['化忌'])}个化忌")

    return pan_data

# ==================== 四化星影响分析 ====================

def analyze_si_hua_impact(pan_data: Dict) -> Dict[str, any]:
    """
    分析四化星对命盘的影响

    Args:
        pan_data: 包含四化星信息的命盘数据

    Returns:
        四化星影响分析结果
    """
    if 'si_hua' not in pan_data:
        logger.warning("命盘数据中未找到四化星信息")
        return {}

    si_hua_data = pan_data['si_hua']['data']
    palaces = pan_data.get('palaces', [])
    ming_gong_index = pan_data.get('ming_gong', 0)

    # 分析各宫位的四化情况
    palace_analysis = []
    for palace in palaces:
        palace_si_hua = palace.get('si_hua', [])
        if palace_si_hua:
            analysis = {
                'palace': palace['name'],
                'si_hua': palace_si_hua,
                'impact': _analyze_palace_si_hua(palace, palace_si_hua, ming_gong_index),
            }
            palace_analysis.append(analysis)

    # 统计四化星分布
    statistics = {
        '化禄_count': len(si_hua_data['化禄']),
        '化权_count': len(si_hua_data['化权']),
        '化科_count': len(si_hua_data['化科']),
        '化忌_count': len(si_hua_data['化忌']),
    }

    # 重点分析：化忌位置（需要特别注意）
    hua_ji_analysis = _analyze_hua_ji(si_hua_data['化忌'], palaces, ming_gong_index)

    # 重点分析：化禄位置（财运相关）
    hua_lu_analysis = _analyze_hua_lu(si_hua_data['化禄'], palaces, ming_gong_index)

    result = {
        'statistics': statistics,
        'palace_analysis': palace_analysis,
        'hua_ji_analysis': hua_ji_analysis,
        'hua_lu_analysis': hua_lu_analysis,
        'summary': _generate_si_hua_summary(statistics, hua_ji_analysis, hua_lu_analysis),
    }

    logger.info("四化星影响分析完成")
    return result

def _analyze_palace_si_hua(palace: Dict, si_hua_list: List[str], ming_gong_index: int) -> str:
    """分析单个宫位的四化影响"""
    impacts = []

    is_ming_gong = palace.get('is_ming_gong', False)

    for si_hua_type in si_hua_list:
        meaning = SI_HUA_MEANINGS.get(si_hua_type, '')
        if si_hua_type == '化禄':
            impacts.append(f"该宫位有财运和福气（{meaning}）")
        elif si_hua_type == '化权':
            impacts.append(f"该宫位有权力和掌控力（{meaning}）")
        elif si_hua_type == '化科':
            impacts.append(f"该宫位有名声和贵人（{meaning}）")
        elif si_hua_type == '化忌':
            impacts.append(f"该宫位需要注意阻碍和困扰（{meaning}）")

    if is_ming_gong and '化忌' in si_hua_list:
        impacts.append("⚠️ 命宫有化忌，需要特别注意")

    return "；".join(impacts) if impacts else "无特殊四化影响"

def _analyze_hua_ji(hua_ji_list: List[Dict], palaces: List[Dict], ming_gong_index: int) -> Dict:
    """分析化忌的影响"""
    if not hua_ji_list:
        return {'message': '无化忌，整体较为顺利'}

    analysis = {
        'count': len(hua_ji_list),
        'locations': [],
        'warnings': [],
    }

    for item in hua_ji_list:
        palace_name = item['palace']
        star_name = item['star']

        # 找到对应的宫位
        palace = next((p for p in palaces if p['name'] == palace_name), None)
        is_ming_gong = palace and palace.get('is_ming_gong', False)

        location_info = {
            'palace': palace_name,
            'star': star_name,
            'is_ming_gong': is_ming_gong,
        }
        analysis['locations'].append(location_info)

        if is_ming_gong:
            analysis['warnings'].append(f"⚠️ 命宫有{star_name}化忌，需要特别注意自身发展和健康")
        else:
            analysis['warnings'].append(f"⚠️ {palace_name}有{star_name}化忌，该方面需要谨慎")

    return analysis

def _analyze_hua_lu(hua_lu_list: List[Dict], palaces: List[Dict], ming_gong_index: int) -> Dict:
    """分析化禄的影响"""
    if not hua_lu_list:
        return {'message': '无化禄'}

    analysis = {
        'count': len(hua_lu_list),
        'locations': [],
        'opportunities': [],
    }

    for item in hua_lu_list:
        palace_name = item['palace']
        star_name = item['star']

        palace = next((p for p in palaces if p['name'] == palace_name), None)
        is_ming_gong = palace and palace.get('is_ming_gong', False)

        location_info = {
            'palace': palace_name,
            'star': star_name,
            'is_ming_gong': is_ming_gong,
        }
        analysis['locations'].append(location_info)

        if is_ming_gong:
            analysis['opportunities'].append(f"✨ 命宫有{star_name}化禄，自身财运和福气较好")
        else:
            analysis['opportunities'].append(f"✨ {palace_name}有{star_name}化禄，该方面有财运机会")

    return analysis

def _generate_si_hua_summary(statistics: Dict, hua_ji_analysis: Dict, hua_lu_analysis: Dict) -> str:
    """生成四化星分析总结"""
    summary_parts = []

    # 化禄总结
    if statistics['化禄_count'] > 0:
        summary_parts.append(f"命盘中有{statistics['化禄_count']}个化禄，财运和福气较好")

    # 化权总结
    if statistics['化权_count'] > 0:
        summary_parts.append(f"有{statistics['化权_count']}个化权，权力和掌控力较强")

    # 化科总结
    if statistics['化科_count'] > 0:
        summary_parts.append(f"有{statistics['化科_count']}个化科，名声和贵人运不错")

    # 化忌总结
    if statistics['化忌_count'] > 0:
        summary_parts.append(f"⚠️ 有{statistics['化忌_count']}个化忌，需要特别注意相关宫位")

    return "；".join(summary_parts) if summary_parts else "四化星分布较为均衡"

