"""
风水布局核心计算器
实现八宅命卦、玄空飞星、朝向评分、缺角检测等核心算法
"""
from typing import Dict, List, Optional, Tuple, Any
import logging
import math

logger = logging.getLogger(__name__)

# ==================== 基础常量定义 ====================

# 二十四山（每宫三山，按后天八卦方位）
ERSHISI_SHAN = {
    '坎': ['壬', '子', '癸'],      # 北
    '艮': ['丑', '艮', '寅'],      # 东北
    '震': ['甲', '卯', '乙'],      # 东
    '巽': ['辰', '巽', '巳'],      # 东南
    '离': ['丙', '午', '丁'],      # 南
    '坤': ['未', '坤', '申'],      # 西南
    '兑': ['庚', '酉', '辛'],      # 西
    '乾': ['戌', '乾', '亥'],      # 西北
}

# 二十四山对应度数范围（每山15度）
SHAN_DEGREES = {
    '壬': (337.5, 352.5), '子': (352.5, 7.5), '癸': (7.5, 22.5),
    '丑': (22.5, 37.5), '艮': (37.5, 52.5), '寅': (52.5, 67.5),
    '甲': (67.5, 82.5), '卯': (82.5, 97.5), '乙': (97.5, 112.5),
    '辰': (112.5, 127.5), '巽': (127.5, 142.5), '巳': (142.5, 157.5),
    '丙': (157.5, 172.5), '午': (172.5, 187.5), '丁': (187.5, 202.5),
    '未': (202.5, 217.5), '坤': (217.5, 232.5), '申': (232.5, 247.5),
    '庚': (247.5, 262.5), '酉': (262.5, 277.5), '辛': (277.5, 292.5),
    '戌': (292.5, 307.5), '乾': (307.5, 322.5), '亥': (322.5, 337.5),
}

# 八卦方位
BAGUA_FANGWEI = {
    '坎': '北', '艮': '东北', '震': '东', '巽': '东南',
    '离': '南', '坤': '西南', '兑': '西', '乾': '西北',
}

# 八卦对应数字（后天八卦）
BAGUA_NUMBER = {
    '坎': 1, '坤': 2, '震': 3, '巽': 4,
    '中': 5, '乾': 6, '兑': 7, '艮': 8, '离': 9,
}

# 八宅命卦对照表（根据出生年份计算）
# 男命：100 - (年份后两位) % 9，女命：(年份后两位 - 4) % 9
MINGUA_TABLE = {
    1: '坎', 2: '坤', 3: '震', 4: '巽',
    6: '乾', 7: '兑', 8: '艮', 9: '离',
}

# 东四命与西四命
DONG_SI_MING = ['坎', '离', '震', '巽']  # 东四命
XI_SI_MING = ['乾', '坤', '艮', '兑']    # 西四命

# 八宅四吉方位对照表（命卦 -> 四吉方位）
BAZHAI_JI_FANGWEI = {
    '坎': {'生气': '离', '天医': '震', '延年': '巽', '伏位': '坎'},
    '离': {'生气': '坎', '天医': '巽', '延年': '震', '伏位': '离'},
    '震': {'生气': '巽', '天医': '坎', '延年': '离', '伏位': '震'},
    '巽': {'生气': '震', '天医': '离', '延年': '坎', '伏位': '巽'},
    '乾': {'生气': '兑', '天医': '艮', '延年': '坤', '伏位': '乾'},
    '坤': {'生气': '艮', '天医': '兑', '延年': '乾', '伏位': '坤'},
    '艮': {'生气': '坤', '天医': '乾', '延年': '兑', '伏位': '艮'},
    '兑': {'生气': '乾', '天医': '坤', '延年': '艮', '伏位': '兑'},
}

# 八宅四凶方位对照表（命卦 -> 四凶方位）
BAZHAI_XIONG_FANGWEI = {
    '坎': {'绝命': '坤', '五鬼': '艮', '六煞': '乾', '祸害': '兑'},
    '离': {'绝命': '艮', '五鬼': '坤', '六煞': '兑', '祸害': '乾'},
    '震': {'绝命': '兑', '五鬼': '乾', '六煞': '坤', '祸害': '艮'},
    '巽': {'绝命': '艮', '五鬼': '兑', '六煞': '乾', '祸害': '坤'},
    '乾': {'绝命': '离', '五鬼': '震', '六煞': '坎', '祸害': '巽'},
    '坤': {'绝命': '坎', '五鬼': '离', '六煞': '震', '祸害': '巽'},
    '艮': {'绝命': '巽', '五鬼': '坎', '六煞': '离', '祸害': '震'},
    '兑': {'绝命': '震', '五鬼': '巽', '六煞': '艮', '祸害': '坎'},
}

# 九宫飞星（玄空飞星）
FEIXING = {
    '一白': {'wuxing': '水', 'star': 1, 'name': '贪狼', 'element': '水'},
    '二黑': {'wuxing': '土', 'star': 2, 'name': '巨门', 'element': '土'},
    '三碧': {'wuxing': '木', 'star': 3, 'name': '禄存', 'element': '木'},
    '四绿': {'wuxing': '木', 'star': 4, 'name': '文曲', 'element': '木'},
    '五黄': {'wuxing': '土', 'star': 5, 'name': '廉贞', 'element': '土'},
    '六白': {'wuxing': '金', 'star': 6, 'name': '武曲', 'element': '金'},
    '七赤': {'wuxing': '金', 'star': 7, 'name': '破军', 'element': '金'},
    '八白': {'wuxing': '土', 'star': 8, 'name': '左辅', 'element': '土'},
    '九紫': {'wuxing': '火', 'star': 9, 'name': '右弼', 'element': '火'},
}

# 三元九运周期（每运20年）
SANYUAN_JIUYUN = [
    {'yun': 1, 'start': 1864, 'end': 1883, 'element': '水'},
    {'yun': 2, 'start': 1884, 'end': 1903, 'element': '土'},
    {'yun': 3, 'start': 1904, 'end': 1923, 'element': '木'},
    {'yun': 4, 'start': 1924, 'end': 1943, 'element': '木'},
    {'yun': 5, 'start': 1944, 'end': 1963, 'element': '土'},
    {'yun': 6, 'start': 1964, 'end': 1983, 'element': '金'},
    {'yun': 7, 'start': 1984, 'end': 2003, 'element': '金'},
    {'yun': 8, 'start': 2004, 'end': 2023, 'element': '土'},
    {'yun': 9, 'start': 2024, 'end': 2043, 'element': '火'},
]

# 九宫基础盘（洛书）
LUOSHU = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

# 二十四山所属卦宫
SHAN_TO_GUA = {}
for gua, shan_list in ERSHISI_SHAN.items():
    for shan in shan_list:
        SHAN_TO_GUA[shan] = gua

# 方位五行
FANGWEI_WUXING = {
    '坎': '水', '离': '火', '震': '木', '巽': '木',
    '乾': '金', '兑': '金', '艮': '土', '坤': '土',
}

# 房间功能与八卦对应
ROOM_BAGUA_MAP = {
    '坎': {'suitable': ['卧室', '书房', '储藏室'], 'avoid': ['厨房', '卫生间']},
    '离': {'suitable': ['客厅', '书房', '办公室'], 'avoid': ['储藏室']},
    '震': {'suitable': ['客厅', '餐厅', '卧室'], 'avoid': ['卫生间']},
    '巽': {'suitable': ['书房', '卧室', '阳台'], 'avoid': ['厨房']},
    '乾': {'suitable': ['书房', '办公室', '储藏室'], 'avoid': ['厨房', '卫生间']},
    '坤': {'suitable': ['客厅', '卧室', '餐厅'], 'avoid': ['书房']},
    '艮': {'suitable': ['储藏室', '卧室', '书房'], 'avoid': ['厨房']},
    '兑': {'suitable': ['客厅', '餐厅', '卧室'], 'avoid': ['卫生间']},
}

# 职业类型与五行对应
OCCUPATION_WUXING = {
    '管理': '土',
    '技术': '金',
    '销售': '水',
    '创意': '木',
    '教育': '木',
    '金融': '金',
    '医疗': '水',
    '法律': '金',
    '艺术': '火',
    '餐饮': '火',
}


# ==================== 八宅命卦计算 ====================

def calculate_bazhai_mingua(birth_year: int, gender: str) -> Dict[str, Any]:
    """
    计算八宅命卦
    
    Args:
        birth_year: 出生年份（公历）
        gender: 性别（'男' 或 '女'）
    
    Returns:
        {
            'mingua': str,           # 命卦名
            'mingua_number': int,    # 命数
            'dong_si_xi_si': str,    # 东四命/西四命
            'ji_fangwei': Dict,      # 四吉方位
            'xiong_fangwei': Dict,   # 四凶方位
            'wuxing': str,           # 命卦五行
        }
    """
    try:
        year_last_two = birth_year % 100
        
        if gender == '男':
            num = (100 - year_last_two) % 9
        else:
            num = (year_last_two - 4) % 9
        
        if num == 0:
            num = 9
        
        if num == 5:
            if gender == '男':
                num = 2
            else:
                num = 8
        
        mingua = MINGUA_TABLE.get(num, '坤')
        
        dong_xi = '东四命' if mingua in DONG_SI_MING else '西四命'
        
        ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
        xiong_fangwei = BAZHAI_XIONG_FANGWEI.get(mingua, {})
        
        wuxing = FANGWEI_WUXING.get(mingua, '土')
        
        return {
            'success': True,
            'mingua': mingua,
            'mingua_number': num,
            'dong_si_xi_si': dong_xi,
            'ji_fangwei': {
                '生气': {'gua': ji_fangwei.get('生气', ''), 'fangwei': BAGUA_FANGWEI.get(ji_fangwei.get('生气', ''), '')},
                '天医': {'gua': ji_fangwei.get('天医', ''), 'fangwei': BAGUA_FANGWEI.get(ji_fangwei.get('天医', ''), '')},
                '延年': {'gua': ji_fangwei.get('延年', ''), 'fangwei': BAGUA_FANGWEI.get(ji_fangwei.get('延年', ''), '')},
                '伏位': {'gua': ji_fangwei.get('伏位', ''), 'fangwei': BAGUA_FANGWEI.get(ji_fangwei.get('伏位', ''), '')},
            },
            'xiong_fangwei': {
                '绝命': {'gua': xiong_fangwei.get('绝命', ''), 'fangwei': BAGUA_FANGWEI.get(xiong_fangwei.get('绝命', ''), '')},
                '五鬼': {'gua': xiong_fangwei.get('五鬼', ''), 'fangwei': BAGUA_FANGWEI.get(xiong_fangwei.get('五鬼', ''), '')},
                '六煞': {'gua': xiong_fangwei.get('六煞', ''), 'fangwei': BAGUA_FANGWEI.get(xiong_fangwei.get('六煞', ''), '')},
                '祸害': {'gua': xiong_fangwei.get('祸害', ''), 'fangwei': BAGUA_FANGWEI.get(xiong_fangwei.get('祸害', ''), '')},
            },
            'wuxing': wuxing,
        }
    except Exception as e:
        logger.error(f"计算命卦失败: {e}")
        return {'success': False, 'error': str(e)}


# ==================== 玄空飞星排盘 ====================

def get_current_yun(year: int) -> Dict[str, Any]:
    """
    获取当前运程
    
    Args:
        year: 年份
    
    Returns:
        运程信息
    """
    for yun_info in SANYUAN_JIUYUN:
        if yun_info['start'] <= year <= yun_info['end']:
            return yun_info
    return SANYUAN_JIUYUN[-1]


def degree_to_shan(degree: float) -> str:
    """
    将度数转换为二十四山
    
    Args:
        degree: 度数（0-360）
    
    Returns:
        二十四山名称
    """
    degree = degree % 360
    
    for shan, (start, end) in SHAN_DEGREES.items():
        if start > end:
            if degree >= start or degree < end:
                return shan
        else:
            if start <= degree < end:
                return shan
    
    return '子'


def shan_to_degree(shan: str) -> Tuple[float, float]:
    """
    将二十四山转换为度数范围
    
    Args:
        shan: 二十四山名称
    
    Returns:
        (起始度数, 结束度数)
    """
    return SHAN_DEGREES.get(shan, (0, 15))


def shan_to_gua(shan: str) -> str:
    """
    获取二十四山所属卦宫
    
    Args:
        shan: 二十四山名称
    
    Returns:
        卦名
    """
    return SHAN_TO_GUA.get(shan, '坎')


def calculate_xuankong_feixing(
    construction_year: int,
    zuo_shan: str,
    xiang_shou: str,
) -> Dict[str, Any]:
    """
    计算玄空飞星盘
    
    Args:
        construction_year: 建造年份
        zuo_shan: 坐山（二十四山）
        xiang_shou: 向首（二十四山）
    
    Returns:
        {
            'success': bool,
            'yun': Dict,           # 运程信息
            'shan_pan': List,      # 山盘（九宫）
            'xiang_pan': List,     # 向盘（九宫）
            'yun_pan': List,       # 运盘（九宫）
        }
    """
    try:
        yun_info = get_current_yun(construction_year)
        yun_number = yun_info['yun']
        
        zuo_gua = shan_to_gua(zuo_shan)
        xiang_gua = shan_to_gua(xiang_shou)
        
        zuo_number = BAGUA_NUMBER.get(zuo_gua, 1)
        xiang_number = BAGUA_NUMBER.get(xiang_gua, 9)
        
        shan_pan = _fly_star(zuo_number, yun_number, 'shan')
        xiang_pan = _fly_star(xiang_number, yun_number, 'xiang')
        yun_pan = _fly_star(yun_number, yun_number, 'yun')
        
        return {
            'success': True,
            'yun': yun_info,
            'zuo_shan': zuo_shan,
            'xiang_shou': xiang_shou,
            'zuo_gua': zuo_gua,
            'xiang_gua': xiang_gua,
            'shan_pan': shan_pan,
            'xiang_pan': xiang_pan,
            'yun_pan': yun_pan,
            'combined_pan': _combine_pan(shan_pan, xiang_pan, yun_pan),
        }
    except Exception as e:
        logger.error(f"计算飞星盘失败: {e}")
        return {'success': False, 'error': str(e)}


def _fly_star(center_star: int, yun_star: int, pan_type: str) -> List[List[int]]:
    """
    飞星排盘核心算法
    
    Args:
        center_star: 中心星数
        yun_star: 运星
        pan_type: 盘类型（'shan', 'xiang', 'yun'）
    
    Returns:
        九宫飞星盘
    """
    pan = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    fly_order = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    
    center_idx = fly_order.index(center_star) if center_star in fly_order else 0
    positions = [(1, 1), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)]
    
    for i, pos in enumerate(positions):
        star_idx = (center_idx + i) % 9
        pan[pos[0]][pos[1]] = fly_order[star_idx]
    
    return pan


def _combine_pan(shan_pan: List[List[int]], xiang_pan: List[List[int]], yun_pan: List[List[int]]) -> List[List[Dict]]:
    """
    合并山盘、向盘、运盘
    
    Returns:
        综合九宫盘
    """
    combined = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append({
                'yun_xing': yun_pan[i][j],
                'shan_xing': shan_pan[i][j],
                'xiang_xing': xiang_pan[i][j],
            })
        combined.append(row)
    return combined


# ==================== 朝向评分 ====================

def calculate_orientation_score(
    house_direction: str,
    mingua: str,
    birth_year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    计算房屋朝向与命卦的适配度评分
    
    Args:
        house_direction: 房屋朝向（二十四山）
        mingua: 命卦
        birth_year: 出生年份（可选，用于更详细分析）
    
    Returns:
        {
            'success': bool,
            'score': float,          # 0-100分
            'level': str,            # 优秀/良好/一般/较差/极差
            'analysis': Dict,        # 详细分析
            'suggestions': List,     # 改善建议
        }
    """
    try:
        house_gua = shan_to_gua(house_direction)
        
        ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
        xiong_fangwei = BAZHAI_XIONG_FANGWEI.get(mingua, {})
        
        score = 50
        analysis = {'house_direction': house_direction, 'house_gua': house_gua, 'mingua': mingua, 'position_type': '中性', 'position_name': ''}
        
        for name, gua in ji_fangwei.items():
            if gua == house_gua:
                if name == '生气':
                    score += 40
                elif name == '天医':
                    score += 35
                elif name == '延年':
                    score += 30
                elif name == '伏位':
                    score += 25
                analysis['position_type'] = '吉'
                analysis['position_name'] = name
                break
        
        if analysis['position_type'] == '中性':
            for name, gua in xiong_fangwei.items():
                if gua == house_gua:
                    if name == '绝命':
                        score -= 35
                    elif name == '五鬼':
                        score -= 30
                    elif name == '六煞':
                        score -= 25
                    elif name == '祸害':
                        score -= 20
                    analysis['position_type'] = '凶'
                    analysis['position_name'] = name
                    break
        
        score = max(0, min(100, score))
        
        if score >= 85:
            level = '优秀'
        elif score >= 70:
            level = '良好'
        elif score >= 50:
            level = '一般'
        elif score >= 30:
            level = '较差'
        else:
            level = '极差'
        
        suggestions = _generate_orientation_suggestions(house_gua, mingua, analysis['position_type'])
        
        return {
            'success': True,
            'score': score,
            'level': level,
            'analysis': analysis,
            'suggestions': suggestions,
        }
    except Exception as e:
        logger.error(f"计算朝向评分失败: {e}")
        return {'success': False, 'error': str(e)}


def _generate_orientation_suggestions(house_gua: str, mingua: str, position_type: str) -> List[str]:
    """
    生成朝向改善建议
    """
    suggestions = []
    
    if position_type == '吉':
        suggestions.append(f"房屋朝向属于{house_gua}宫，与您的命卦{mingua}相配，是大吉之选")
        suggestions.append("建议保持现有朝向，可在吉位放置催旺物品")
    elif position_type == '凶':
        ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
        suggestions.append(f"房屋朝向属于{house_gua}宫，与您的命卦{mingua}存在冲克")
        suggestions.append(f"建议在{'生气' if '生气' in ji_fangwei else '天医'}位放置化解物品")
        suggestions.append("可考虑通过室内布局调整来化解不利因素")
    else:
        suggestions.append(f"房屋朝向属于{house_gua}宫，与您的命卦{mingua}关系中性")
        suggestions.append("可通过其他风水布局来提升整体运势")
    
    return suggestions


# ==================== 缺角凸角检测 ====================

def detect_house_defects(
    house_shape: str,
    coordinates: Optional[List[Dict]] = None,
    center_point: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    检测房屋缺角凸角
    
    Args:
        house_shape: 房屋形状（'矩形', 'L形', 'U形', '不规则'）
        coordinates: 房屋坐标点列表 [{'x': float, 'y': float}, ...]
        center_point: 中心点坐标
    
    Returns:
        {
            'success': bool,
            'defects': List,         # 缺角信息
            'protrusions': List,     # 凸角信息
            'layout_score': float,   # 格局评分
            'analysis': Dict,        # 分析结果
        }
    """
    try:
        defects = []
        protrusions = []
        layout_score = 100.0
        
        ideal_shapes = {
            '矩形': {'defects': 0, 'score': 100},
            'L形': {'defects': 1, 'score': 75},
            'U形': {'defects': 2, 'score': 70},
            '不规则': {'defects': -1, 'score': 60},
        }
        
        shape_info = ideal_shapes.get(house_shape, ideal_shapes['不规则'])
        base_score = shape_info['score']
        
        if house_shape == 'L形':
            defects.append({
                'position': '缺角',
                'direction': '待定',
                'impact': '影响对应方位的运势',
                'severity': '中等',
                'suggestion': '可在缺角处放置对应五行物品化解',
            })
            layout_score = base_score
        elif house_shape == 'U形':
            defects.append({
                'position': '缺角',
                'direction': '待定',
                'impact': '影响对应方位的运势',
                'severity': '较高',
                'suggestion': '建议通过装修或摆放物品来填补',
            })
            layout_score = base_score
        elif house_shape == '不规则':
            defects.append({
                'position': '不规则',
                'direction': '多处',
                'impact': '气场不稳，影响整体运势',
                'severity': '高',
                'suggestion': '建议通过隔断或装饰来规整空间',
            })
            layout_score = base_score
        else:
            layout_score = 100.0
        
        if coordinates and center_point:
            advanced_result = _analyze_coordinates(coordinates, center_point)
            defects.extend(advanced_result.get('defects', []))
            protrusions.extend(advanced_result.get('protrusions', []))
        
        analysis = {
            'house_shape': house_shape,
            'is_regular': house_shape == '矩形',
            'defect_count': len(defects),
            'protrusion_count': len(protrusions),
        }
        
        return {
            'success': True,
            'defects': defects,
            'protrusions': protrusions,
            'layout_score': layout_score,
            'analysis': analysis,
        }
    except Exception as e:
        logger.error(f"检测缺角凸角失败: {e}")
        return {'success': False, 'error': str(e)}


def _analyze_coordinates(coordinates: List[Dict], center_point: Dict) -> Dict[str, Any]:
    """
    根据坐标分析缺角凸角
    """
    defects = []
    protrusions = []
    
    directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北']
    direction_angles = [0, 45, 90, 135, 180, 225, 270, 315]
    
    return {'defects': defects, 'protrusions': protrusions}


# ==================== 房间功能定位 ====================

def calculate_room_position(
    mingua: str,
    house_layout: Dict,
    room_types: List[str],
    feixing_pan: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    计算房间最佳位置
    
    Args:
        mingua: 命卦
        house_layout: 房屋布局 {'north': str, 'south': str, ...}
        room_types: 需要定位的房间类型列表
        feixing_pan: 飞星盘（可选）
    
    Returns:
        {
            'success': bool,
            'room_positions': Dict,    # 各房间建议位置
            'priority_order': List,    # 房间优先级
            'avoid_positions': List,   # 需避开的位置
        }
    """
    try:
        ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
        xiong_fangwei = BAZHAI_XIONG_FANGWEI.get(mingua, {})
        
        room_positions = {}
        priority_order = []
        avoid_positions = []
        
        room_priority = {
            '主卧': 1,
            '书房': 2,
            '客厅': 3,
            '厨房': 4,
            '卫生间': 5,
            '餐厅': 6,
            '儿童房': 7,
            '老人房': 8,
        }
        
        for room_type in room_types:
            best_position = None
            best_gua = None
            
            for ji_name, gua in ji_fangwei.items():
                room_info = ROOM_BAGUA_MAP.get(gua, {})
                if room_type in room_info.get('suitable', []):
                    best_gua = gua
                    best_position = BAGUA_FANGWEI.get(gua, '')
                    break
            
            if best_gua:
                room_positions[room_type] = {
                    'best_position': best_position,
                    'gua': best_gua,
                    'reason': f"位于{best_gua}宫，属于吉位",
                    'alternative': [],
                }
                priority_order.append((room_type, room_priority.get(room_type, 99)))
            else:
                for gua in DONG_SI_MING + XI_SI_MING:
                    room_info = ROOM_BAGUA_MAP.get(gua, {})
                    if room_type not in room_info.get('avoid', []):
                        best_gua = gua
                        best_position = BAGUA_FANGWEI.get(gua, '')
                        break
                
                if best_gua:
                    room_positions[room_type] = {
                        'best_position': best_position,
                        'gua': best_gua,
                        'reason': f"位于{best_gua}宫，中等适宜",
                        'alternative': [],
                    }
                else:
                    room_positions[room_type] = {
                        'best_position': '待定',
                        'gua': '',
                        'reason': '需根据实际情况综合考量',
                        'alternative': [],
                    }
                priority_order.append((room_type, room_priority.get(room_type, 99)))
        
        for xiong_name, gua in xiong_fangwei.items():
            avoid_positions.append({
                'position': BAGUA_FANGWEI.get(gua, ''),
                'gua': gua,
                'type': xiong_name,
                'avoid_for': ['主卧', '书房', '办公室'],
            })
        
        priority_order.sort(key=lambda x: x[1])
        
        return {
            'success': True,
            'room_positions': room_positions,
            'priority_order': [item[0] for item in priority_order],
            'avoid_positions': avoid_positions,
        }
    except Exception as e:
        logger.error(f"计算房间位置失败: {e}")
        return {'success': False, 'error': str(e)}


# ==================== 工位摆放优化 ====================

def calculate_desk_position(
    room_direction: str,
    mingua: str,
    occupation_type: str,
    room_size: Optional[Dict] = None,
    existing_furniture: Optional[List] = None,
) -> Dict[str, Any]:
    """
    计算工位/办公桌最佳摆放位置
    
    Args:
        room_direction: 房间朝向（二十四山）
        mingua: 命卦
        occupation_type: 职业类型
        room_size: 房间尺寸 {'width': float, 'length': float}
        existing_furniture: 现有家具位置列表
    
    Returns:
        {
            'success': bool,
            'desk_position': Dict,      # 最佳桌位位置
            'desk_direction': str,      # 桌面朝向
            'avoid_directions': List,   # 需避开朝向
            'enhancement_items': List,  # 增运物品建议
        }
    """
    try:
        ji_fangwei = BAZHAI_JI_FANGWEI.get(mingua, {})
        xiong_fangwei = BAZHAI_XIONG_FANGWEI.get(mingua, {})
        
        room_gua = shan_to_gua(room_direction)
        
        occupation_wuxing = OCCUPATION_WUXING.get(occupation_type, '土')
        
        best_direction = None
        best_gua = None
        best_reason = ""
        
        for ji_name, gua in ji_fangwei.items():
            gua_wuxing = FANGWEI_WUXING.get(gua, '土')
            if gua_wuxing == occupation_wuxing or ji_name == '生气':
                best_gua = gua
                best_direction = BAGUA_FANGWEI.get(gua, '')
                best_reason = f"位于{ji_name}位（{gua}宫），五行{gua_wuxing}，适合{occupation_type}职业"
                break
        
        if not best_gua:
            for ji_name, gua in ji_fangwei.items():
                best_gua = gua
                best_direction = BAGUA_FANGWEI.get(gua, '')
                best_reason = f"位于{ji_name}位（{gua}宫），属于吉位"
                break
        
        desk_direction = None
        opposite_gua = _get_opposite_gua(best_gua) if best_gua else None
        if opposite_gua:
            desk_direction = BAGUA_FANGWEI.get(opposite_gua, '')
        
        avoid_directions = []
        for xiong_name, gua in xiong_fangwei.items():
            if xiong_name in ['绝命', '五鬼']:
                avoid_directions.append({
                    'direction': BAGUA_FANGWEI.get(gua, ''),
                    'gua': gua,
                    'reason': f"属于{xiong_name}位，不宜坐向此方",
                })
        
        enhancement_items = _get_enhancement_items(occupation_type, occupation_wuxing)
        
        desk_position = {
            'area': best_direction,
            'gua': best_gua,
            'relative_position': f"房间{best_direction}侧",
            'reason': best_reason,
        }
        
        if room_size:
            desk_position['room_size'] = room_size
            if room_size.get('width') and room_size.get('length'):
                width = room_size['width']
                length = room_size['length']
                desk_position['suggested_area'] = {
                    'x_min': width * 0.1,
                    'x_max': width * 0.4,
                    'y_min': length * 0.1,
                    'y_max': length * 0.4,
                }
        
        return {
            'success': True,
            'desk_position': desk_position,
            'desk_direction': desk_direction,
            'face_direction': desk_direction,
            'avoid_directions': avoid_directions,
            'enhancement_items': enhancement_items,
        }
    except Exception as e:
        logger.error(f"计算工位位置失败: {e}")
        return {'success': False, 'error': str(e)}


def _get_opposite_gua(gua: str) -> Optional[str]:
    """
    获取对宫卦
    """
    opposite_map = {
        '坎': '离', '离': '坎',
        '震': '兑', '兑': '震',
        '巽': '乾', '乾': '巽',
        '艮': '坤', '坤': '艮',
    }
    return opposite_map.get(gua)


def _get_enhancement_items(occupation_type: str, wuxing: str) -> List[Dict]:
    """
    获取增运物品建议
    """
    items = {
        '木': [
            {'item': '绿植', 'reason': '增强木气，利于创意发展'},
            {'item': '文竹', 'reason': '提升学业和事业运'},
            {'item': '书籍', 'reason': '增添文气，利于思考'},
        ],
        '火': [
            {'item': '红色装饰', 'reason': '增强火气，提升热情'},
            {'item': '台灯', 'reason': '光明照耀，前途光明'},
            {'item': '三角形物品', 'reason': '火形助运'},
        ],
        '土': [
            {'item': '黄水晶', 'reason': '增强土气，稳定财运'},
            {'item': '陶瓷饰品', 'reason': '土质物品，助稳固'},
            {'item': '方形物品', 'reason': '土形助运'},
        ],
        '金': [
            {'item': '金属摆件', 'reason': '增强金气，利于决策'},
            {'item': '铜钟', 'reason': '金声振耳，提升权威'},
            {'item': '圆形物品', 'reason': '金形助运'},
        ],
        '水': [
            {'item': '鱼缸', 'reason': '水生财，利于财运'},
            {'item': '流水摆件', 'reason': '活水聚财，财源滚滚'},
            {'item': '黑色饰品', 'reason': '水色助运'},
        ],
    }
    return items.get(wuxing, items['土'])


# ==================== 流年飞星计算 ====================

def calculate_yearly_feixing(year: int) -> Dict[str, Any]:
    """
    计算流年飞星
    
    Args:
        year: 年份
    
    Returns:
        {
            'success': bool,
            'year': int,
            'year_star': Dict,    # 年星位置
            'jiu_gong': Dict,     # 九宫飞星位置
        }
    """
    try:
        year_last_digit = year % 10
        year_star = 9 - year_last_digit + 2004
        
        while year_star > 9:
            year_star -= 9
        if year_star <= 0:
            year_star += 9
        
        jiu_gong = {}
        center_star = year_star
        
        fly_order = [5, 6, 7, 8, 9, 1, 2, 3, 4]
        center_idx = fly_order.index(center_star) if center_star in fly_order else 0
        
        gua_order = ['中', '乾', '兑', '艮', '离', '坎', '坤', '震', '巽']
        positions = [(1, 1), (0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)]
        
        for i, gua in enumerate(gua_order):
            star_idx = (center_idx + i) % 9
            star = fly_order[star_idx]
            star_name = [k for k, v in FEIXING.items() if v['star'] == star][0]
            jiu_gong[gua] = {
                'star': star,
                'name': star_name,
                'wuxing': FEIXING[star_name]['wuxing'],
                'position': BAGUA_FANGWEI.get(gua, '中') if gua != '中' else '中宫',
            }
        
        return {
            'success': True,
            'year': year,
            'year_star': year_star,
            'jiu_gong': jiu_gong,
        }
    except Exception as e:
        logger.error(f"计算流年飞星失败: {e}")
        return {'success': False, 'error': str(e)}


# ==================== 综合分析 ====================

def fengshui_calculate(
    birth_year: int,
    gender: str,
    house_direction: str,
    house_shape: str = '矩形',
    construction_year: Optional[int] = None,
    room_types: Optional[List[str]] = None,
    occupation_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    风水综合计算入口函数
    
    Args:
        birth_year: 出生年份
        gender: 性别
        house_direction: 房屋朝向
        house_shape: 房屋形状
        construction_year: 建造年份
        room_types: 需要定位的房间类型
        occupation_type: 职业类型
    
    Returns:
        综合分析结果
    """
    try:
        mingua_result = calculate_bazhai_mingua(birth_year, gender)
        if not mingua_result.get('success'):
            return mingua_result
        
        mingua = mingua_result['mingua']
        
        orientation_result = calculate_orientation_score(house_direction, mingua, birth_year)
        
        defect_result = detect_house_defects(house_shape)
        
        room_result = None
        if room_types:
            room_result = calculate_room_position(mingua, {}, room_types)
        
        desk_result = None
        if occupation_type:
            desk_result = calculate_desk_position(house_direction, mingua, occupation_type)
        
        feixing_result = None
        if construction_year:
            zuo_shan = _get_opposite_shan(house_direction)
            feixing_result = calculate_xuankong_feixing(construction_year, zuo_shan, house_direction)
        
        return {
            'success': True,
            'mingua': mingua_result,
            'orientation': orientation_result,
            'defect': defect_result,
            'room': room_result,
            'desk': desk_result,
            'feixing': feixing_result,
        }
    except Exception as e:
        logger.error(f"风水综合计算失败: {e}")
        return {'success': False, 'error': str(e)}


def _get_opposite_shan(shan: str) -> str:
    """
    获取对向山（坐山与向首相对）
    """
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
