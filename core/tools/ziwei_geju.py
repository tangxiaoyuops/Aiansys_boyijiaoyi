"""
紫微斗数格局分析模块
基于 iztro 逻辑的完整实现

格局：三方四正分析、经典格局判断（紫微朝垣、杀破狼等）
"""
from typing import Dict, List, Optional, Tuple, Set
import logging

logger = logging.getLogger(__name__)

# ==================== 格局基础定义 ====================

# 主星列表
MAIN_STARS = [
    '紫微', '天机', '太阳', '武曲', '天同', '廉贞',
    '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
    '七杀', '破军'
]

# 三方四正关系
# 每个宫位的三方：本宫、对宫、以及相邻的特定宫位
TRIANGULAR_RELATIONS = {
    0: [0, 6, 4],   # 命宫的三方：命宫、迁移、财帛
    1: [1, 7, 5],   # 兄弟的三方：兄弟、官禄、疾厄
    2: [2, 8, 6],   # 夫妻的三方：夫妻、田宅、迁移
    3: [3, 9, 7],   # 子女的三方：子女、福德、官禄
    4: [4, 10, 0],  # 财帛的三方：财帛、父母、命宫
    5: [5, 11, 1],  # 疾厄的三方：疾厄、兄弟、兄弟
    6: [6, 0, 2],   # 迁移的三方：迁移、命宫、夫妻
    7: [7, 1, 3],   # 官禄的三方：官禄、兄弟、子女
    8: [8, 2, 4],   # 田宅的三方：田宅、夫妻、财帛
    9: [9, 3, 5],   # 福德的三方：福德、子女、疾厄
    10: [10, 4, 6], # 父母的三方：父母、财帛、迁移
    11: [11, 5, 7], # 父母的三方：父母、疾厄、官禄
}

# 四正关系（本宫、对宫、左右相邻宫）
FOUR_CORNERS_RELATIONS = {
    0: [0, 6, 11, 1],  # 命宫的四正：命宫、迁移、父母、兄弟
    1: [1, 7, 0, 2],   # 兄弟的四正：兄弟、官禄、命宫、夫妻
    2: [2, 8, 1, 3],   # 夫妻的四正：夫妻、田宅、兄弟、子女
    3: [3, 9, 2, 4],   # 子女的四正：子女、福德、夫妻、财帛
    4: [4, 10, 3, 5],  # 财帛的四正：财帛、父母、子女、疾厄
    5: [5, 11, 4, 6],  # 疾厄的四正：疾厄、父母、财帛、迁移
    6: [6, 0, 5, 7],   # 迁移的四正：迁移、命宫、疾厄、官禄
    7: [7, 1, 6, 8],   # 官禄的四正：官禄、兄弟、迁移、田宅
    8: [8, 2, 7, 9],   # 田宅的四正：田宅、夫妻、官禄、福德
    9: [9, 3, 8, 10],  # 福德的四正：福德、子女、田宅、父母
    10: [10, 4, 9, 11], # 父母的四正：父母、财帛、福德、父母
    11: [11, 5, 10, 0], # 父母的四正：父母、疾厄、父母、命宫
}

# 经典格局定义
CLASSIC_GEJU = {
    '紫微朝垣': {
        'description': '紫微星在命宫，且三方四正有吉星拱照',
        'main_stars': ['紫微'],
        'required_palace': 0,  # 命宫
    },
    '杀破狼': {
        'description': '七杀、破军、贪狼三星会聚',
        'main_stars': ['七杀', '破军', '贪狼'],
    },
    '日月同宫': {
        'description': '太阳和太阴同在一个宫位',
        'main_stars': ['太阳', '太阴'],
        'same_palace': True,
    },
    '紫府同宫': {
        'description': '紫微和天府同在一个宫位',
        'main_stars': ['紫微', '天府'],
        'same_palace': True,
    },
}

# ==================== 工具函数 ====================

def normalize_palace_index(index: int) -> int:
    """标准化宫位索引（0-11）"""
    return index % 12

def get_triangular_palaces(palace_index: int) -> List[int]:
    """获取三方宫位"""
    return TRIANGULAR_RELATIONS.get(palace_index, [palace_index])

def get_four_corners_palaces(palace_index: int) -> List[int]:
    """获取四正宫位"""
    return FOUR_CORNERS_RELATIONS.get(palace_index, [palace_index])

# ==================== 三方四正分析 ====================

def analyze_triangular_palaces(pan_data: Dict, palace_index: int) -> Dict:
    """
    分析指定宫位的三方情况
    
    Args:
        pan_data: 命盘数据
        palace_index: 宫位索引
    
    Returns:
        三方分析结果
    """
    palaces = pan_data.get('palaces', [])
    triangular_indices = get_triangular_palaces(palace_index)
    
    # 收集三方宫位的主星和辅星
    main_stars = []
    auxiliary_stars = []
    si_hua_list = []
    
    for idx in triangular_indices:
        palace = next((p for p in palaces if p['index'] == idx), None)
        if palace:
            main_stars.extend(palace.get('main_stars', []))
            auxiliary_stars.extend(palace.get('auxiliary_stars', []))
            si_hua_list.extend(palace.get('si_hua', []))
    
    # 统计
    analysis = {
        'palace_index': palace_index,
        'triangular_palaces': triangular_indices,
        'main_stars': list(set(main_stars)),  # 去重
        'auxiliary_stars': list(set(auxiliary_stars)),  # 去重
        'si_hua': list(set(si_hua_list)),  # 去重
        'main_star_count': len(set(main_stars)),
        'auxiliary_star_count': len(set(auxiliary_stars)),
    }
    
    logger.debug(f"三方分析: 宫位={palace_index}, 主星数={analysis['main_star_count']}")
    return analysis

def analyze_four_corners_palaces(pan_data: Dict, palace_index: int) -> Dict:
    """
    分析指定宫位的四正情况
    
    Args:
        pan_data: 命盘数据
        palace_index: 宫位索引
    
    Returns:
        四正分析结果
    """
    palaces = pan_data.get('palaces', [])
    four_corners_indices = get_four_corners_palaces(palace_index)
    
    # 收集四正宫位的主星和辅星
    main_stars = []
    auxiliary_stars = []
    si_hua_list = []
    
    for idx in four_corners_indices:
        palace = next((p for p in palaces if p['index'] == idx), None)
        if palace:
            main_stars.extend(palace.get('main_stars', []))
            auxiliary_stars.extend(palace.get('auxiliary_stars', []))
            si_hua_list.extend(palace.get('si_hua', []))
    
    # 统计
    analysis = {
        'palace_index': palace_index,
        'four_corners_palaces': four_corners_indices,
        'main_stars': list(set(main_stars)),  # 去重
        'auxiliary_stars': list(set(auxiliary_stars)),  # 去重
        'si_hua': list(set(si_hua_list)),  # 去重
        'main_star_count': len(set(main_stars)),
        'auxiliary_star_count': len(set(auxiliary_stars)),
    }
    
    logger.debug(f"四正分析: 宫位={palace_index}, 主星数={analysis['main_star_count']}")
    return analysis

# ==================== 经典格局判断 ====================

def check_classic_geju(pan_data: Dict) -> Dict[str, Dict]:
    """
    检查命盘中是否存在经典格局
    
    Args:
        pan_data: 命盘数据
    
    Returns:
        检测到的格局字典，格式：{格局名称: 格局详情}
    """
    detected_geju = {}
    main_stars_pos = pan_data.get('main_stars', {})
    palaces = pan_data.get('palaces', [])
    
    # 检查每个经典格局
    for geju_name, geju_config in CLASSIC_GEJU.items():
        result = _check_single_geju(pan_data, geju_name, geju_config, main_stars_pos, palaces)
        if result['detected']:
            detected_geju[geju_name] = result
    
    logger.info(f"检测到{len(detected_geju)}个经典格局: {list(detected_geju.keys())}")
    return detected_geju

def _check_single_geju(
    pan_data: Dict,
    geju_name: str,
    geju_config: Dict,
    main_stars_pos: Dict,
    palaces: List[Dict]
) -> Dict:
    """检查单个格局"""
    required_stars = geju_config.get('main_stars', [])
    same_palace = geju_config.get('same_palace', False)
    required_palace = geju_config.get('required_palace')
    
    result = {
        'detected': False,
        'geju_name': geju_name,
        'description': geju_config.get('description', ''),
        'details': {},
    }
    
    if same_palace:
        # 检查是否同宫
        for palace in palaces:
            palace_stars = set(palace.get('main_stars', []))
            required_stars_set = set(required_stars)
            if required_stars_set.issubset(palace_stars):
                result['detected'] = True
                result['details'] = {
                    'palace': palace['name'],
                    'palace_index': palace['index'],
                    'stars': list(required_stars_set),
                }
                break
    elif required_palace is not None:
        # 检查是否在指定宫位
        target_palace = next((p for p in palaces if p['index'] == required_palace), None)
        if target_palace:
            palace_stars = set(target_palace.get('main_stars', []))
            required_stars_set = set(required_stars)
            if required_stars_set.issubset(palace_stars):
                result['detected'] = True
                result['details'] = {
                    'palace': target_palace['name'],
                    'palace_index': required_palace,
                    'stars': list(required_stars_set),
                }
    else:
        # 检查是否在命盘中存在（不要求同宫）
        found_stars = []
        for star in required_stars:
            if star in main_stars_pos:
                found_stars.append(star)
        
        if len(found_stars) == len(required_stars):
            result['detected'] = True
            result['details'] = {
                'stars': found_stars,
                'positions': {star: main_stars_pos[star] for star in found_stars},
            }
    
    return result

# ==================== 格局影响分析 ====================

def analyze_geju_impact(pan_data: Dict) -> Dict:
    """
    分析格局对命盘的影响
    
    Args:
        pan_data: 命盘数据
    
    Returns:
        格局影响分析结果
    """
    # 检测经典格局
    detected_geju = check_classic_geju(pan_data)
    
    # 分析命宫的三方四正
    ming_gong_index = pan_data.get('ming_gong', 0)
    triangular_analysis = analyze_triangular_palaces(pan_data, ming_gong_index)
    four_corners_analysis = analyze_four_corners_palaces(pan_data, ming_gong_index)
    
    # 分析每个检测到的格局
    geju_analysis = {}
    for geju_name, geju_info in detected_geju.items():
        geju_analysis[geju_name] = _analyze_single_geju_impact(geju_name, geju_info)
    
    # 生成总结
    summary = _generate_geju_summary(detected_geju, geju_analysis, triangular_analysis)
    
    result = {
        'detected_geju': detected_geju,
        'geju_analysis': geju_analysis,
        'ming_gong_triangular': triangular_analysis,
        'ming_gong_four_corners': four_corners_analysis,
        'summary': summary,
    }
    
    logger.info("格局影响分析完成")
    return result

def _analyze_single_geju_impact(geju_name: str, geju_info: Dict) -> Dict:
    """分析单个格局的影响"""
    impact_map = {
        '紫微朝垣': '命宫有紫微星，且三方四正有吉星拱照，主贵显，有领导才能和权威',
        '杀破狼': '七杀、破军、贪狼三星会聚，主变动、开创，性格刚强，适合创业和变革',
        '日月同宫': '太阳和太阴同宫，主阴阳调和，性格平衡，有智慧和包容力',
        '紫府同宫': '紫微和天府同宫，主富贵双全，有领导才能和财富运势',
    }
    
    impact = impact_map.get(geju_name, f'{geju_name}格局，需要进一步分析')
    
    analysis = {
        'geju_name': geju_name,
        'description': geju_info.get('description', ''),
        'impact': impact,
        'details': geju_info.get('details', {}),
    }
    
    return analysis

def _generate_geju_summary(
    detected_geju: Dict,
    geju_analysis: Dict,
    triangular_analysis: Dict
) -> str:
    """生成格局分析总结"""
    summary_parts = []
    
    # 经典格局
    if detected_geju:
        geju_names = list(detected_geju.keys())
        summary_parts.append(f"检测到{len(geju_names)}个经典格局：{', '.join(geju_names)}")
        
        for geju_name in geju_names:
            if geju_name in geju_analysis:
                summary_parts.append(geju_analysis[geju_name]['impact'])
    else:
        summary_parts.append("未检测到经典格局")
    
    # 命宫三方四正
    if triangular_analysis:
        main_star_count = triangular_analysis.get('main_star_count', 0)
        summary_parts.append(f"命宫三方有{main_star_count}个主星")
    
    return "；".join(summary_parts) if summary_parts else "格局分析完成"

