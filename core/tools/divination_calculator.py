"""
六爻起卦计算器
实现铜钱摇卦、卦象识别、变卦生成等功能
"""
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
import os

logger = logging.getLogger(__name__)

# ==================== 八卦定义 ====================
# 八卦名称：乾(111)、坤(000)、震(100)、巽(011)、坎(010)、离(101)、艮(001)、兑(110)
TRIGRAMS = {
    '111': {'name': '乾', 'nature': '天'},
    '000': {'name': '坤', 'nature': '地'},
    '100': {'name': '震', 'nature': '雷'},
    '011': {'name': '巽', 'nature': '风'},
    '010': {'name': '坎', 'nature': '水'},
    '101': {'name': '离', 'nature': '火'},
    '001': {'name': '艮', 'nature': '山'},
    '110': {'name': '兑', 'nature': '泽'},
}

# 八卦反向映射（名称 -> 二进制）
TRIGRAM_TO_BINARY = {v['name']: k for k, v in TRIGRAMS.items()}

# ==================== 六十四卦数据加载 ====================
# 从JSON文件加载完整的六十四卦数据
# 卦序号按照《周易》传统顺序排列
# 格式：{序号: {name: 卦名, full_name: 全名, inner: 内卦, outer: 外卦, guaci: 卦辞, yaoci: {1-6: 爻辞}}}

def _load_hexagrams() -> Dict[str, Dict[str, Any]]:
    """
    从JSON文件加载六十四卦数据
    
    Returns:
        六十四卦数据字典
    """
    # 获取JSON文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, '..', 'data', 'hexagrams.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            hexagrams = json.load(f)
        # 验证数据完整性
        complete_count = sum(1 for h in hexagrams.values() 
                            if h.get('guaci') and h.get('guaci') != '（卦辞待补充）')
        logger.info(f"成功加载 {len(hexagrams)} 个卦的数据，其中 {complete_count} 个卦有完整卦辞")
        return hexagrams
    except FileNotFoundError:
        logger.warning(f"未找到六十四卦数据文件: {json_path}，使用空字典")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"解析JSON文件失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"加载六十四卦数据时出错: {e}")
        return {}

# 加载六十四卦数据
HEXAGRAMS = _load_hexagrams()

# 六十四卦查找表：根据内卦和外卦查找卦序号
# 格式：{内卦名_外卦名: 卦序号}
HEXAGRAM_LOOKUP = {}
# 从已加载的HEXAGRAMS数据生成查找表
for hexagram_id, hexagram_info in HEXAGRAMS.items():
    inner_name = hexagram_info.get('inner', '')
    outer_name = hexagram_info.get('outer', '')
    if inner_name and outer_name:
        HEXAGRAM_LOOKUP[f"{inner_name}_{outer_name}"] = hexagram_id


def coin_toss_to_yao(coins: List[int]) -> Dict[str, Any]:
    """
    将3枚铜钱的结果转换为爻信息
    
    Args:
        coins: 3枚铜钱的结果列表，1=正面，0=反面
    
    Returns:
        爻信息字典，包含：
        - yao_number: 爻数（6=老阴，7=少阳，8=少阴，9=老阳）
        - is_yang: 是否为阳爻
        - is_dong: 是否为动爻
        - symbol: 爻符号
    """
    if len(coins) != 3:
        raise ValueError("必须提供3枚铜钱的结果")
    
    heads_count = sum(coins)  # 正面数量
    
    if heads_count == 3:
        # 三正：老阳（动爻，记为9）
        return {
            'yao_number': 9,
            'is_yang': True,
            'is_dong': True,
            'symbol': '⚊',
            'description': '老阳（动爻）'
        }
    elif heads_count == 0:
        # 三反：老阴（动爻，记为6）
        return {
            'yao_number': 6,
            'is_yang': False,
            'is_dong': True,
            'symbol': '⚋',
            'description': '老阴（动爻）'
        }
    elif heads_count == 2:
        # 两正一反：少阳（静爻，记为7）
        return {
            'yao_number': 7,
            'is_yang': True,
            'is_dong': False,
            'symbol': '⚊',
            'description': '少阳（静爻）'
        }
    else:  # heads_count == 1
        # 两反一正：少阴（静爻，记为8）
        return {
            'yao_number': 8,
            'is_yang': False,
            'is_dong': False,
            'symbol': '⚋',
            'description': '少阴（静爻）'
        }


def yao_to_binary(yao_info: Dict[str, Any]) -> str:
    """
    将爻信息转换为二进制表示（用于组成八卦）
    
    Args:
        yao_info: 爻信息字典
    
    Returns:
        '0'（阴）或'1'（阳）
    """
    return '1' if yao_info['is_yang'] else '0'


def identify_trigram(yao_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    根据三个爻识别八卦
    
    Args:
        yao_list: 三个爻的信息列表（从下往上）
    
    Returns:
        八卦信息字典
    """
    if len(yao_list) != 3:
        raise ValueError("八卦需要3个爻")
    
    # 从下往上组成二进制字符串
    binary_str = ''.join([yao_to_binary(yao) for yao in reversed(yao_list)])
    
    if binary_str in TRIGRAMS:
        trigram_info = TRIGRAMS[binary_str].copy()
        trigram_info['binary'] = binary_str
        return trigram_info
    else:
        raise ValueError(f"无效的八卦二进制表示: {binary_str}")


def identify_hexagram(inner_trigram: str, outer_trigram: str, hexagrams_data: Dict) -> Optional[Dict[str, Any]]:
    """
    根据内卦和外卦识别六十四卦
    
    Args:
        inner_trigram: 内卦名称
        outer_trigram: 外卦名称
        hexagrams_data: 六十四卦数据字典
    
    Returns:
        卦信息字典，如果未找到返回None
    """
    # 遍历查找匹配的卦
    for hexagram_id, hexagram_info in hexagrams_data.items():
        if (hexagram_info.get('inner') == inner_trigram and 
            hexagram_info.get('outer') == outer_trigram):
            result = hexagram_info.copy()
            result['id'] = hexagram_id
            return result
    
    return None


def get_hexagram_by_trigrams(inner_trigram_name: str, outer_trigram_name: str) -> Optional[Dict[str, Any]]:
    """
    根据内卦和外卦名称直接查找六十四卦（使用标准查找表）
    
    Args:
        inner_trigram_name: 内卦名称（如：乾、坤、震等）
        outer_trigram_name: 外卦名称（如：乾、坤、震等）
    
    Returns:
        卦信息字典，如果未找到则返回基本信息
    """
    # 先尝试从HEXAGRAMS中查找
    result = identify_hexagram(inner_trigram_name, outer_trigram_name, HEXAGRAMS)
    if result:
        return result
    
    # 如果找不到，返回基本信息（用于演示，实际应该包含完整数据）
    return {
        'name': f"{outer_trigram_name}{inner_trigram_name}",
        'full_name': f"{outer_trigram_name}上{inner_trigram_name}下",
        'inner': inner_trigram_name,
        'outer': outer_trigram_name,
        'guaci': '（卦辞待补充）',
        'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)},
    }


def create_hexagram(yao_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    根据6次摇卦结果创建完整的卦象信息
    
    Args:
        yao_results: 6次摇卦结果列表（从下往上：初爻、二爻、三爻、四爻、五爻、上爻）
    
    Returns:
        完整的卦象信息字典
    """
    if len(yao_results) != 6:
        raise ValueError("六爻卦需要6次摇卦结果")
    
    # 从下往上排列（yao_results已经是这个顺序）
    # 下三爻组成内卦（下卦）
    inner_yaos = yao_results[0:3]
    # 上三爻组成外卦（上卦）
    outer_yaos = yao_results[3:6]
    
    # 识别内卦和外卦
    inner_trigram = identify_trigram(inner_yaos)
    outer_trigram = identify_trigram(outer_yaos)
    
    # 查找对应的六十四卦
    hexagram_detail = get_hexagram_by_trigrams(inner_trigram['name'], outer_trigram['name'])
    
    # 调试：检查卦辞是否存在
    if hexagram_detail and not hexagram_detail.get('guaci'):
        logger.warning(f"找到卦 {hexagram_detail.get('name', '未知')} 但缺少卦辞")
    
    if not hexagram_detail:
        # 如果找不到，使用基本信息
        hexagram_detail = {
            'name': f"{outer_trigram['name']}{inner_trigram['name']}",
            'full_name': f"{outer_trigram['name']}上{inner_trigram['name']}下",
            'inner': inner_trigram['name'],
            'outer': outer_trigram['name'],
            'guaci': '（卦辞待补充）',
            'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)}
        }
    
    hexagram_info = hexagram_detail.copy()
    hexagram_info['inner_trigram'] = inner_trigram['name']
    hexagram_info['outer_trigram'] = outer_trigram['name']
    
    # 检查是否有动爻
    dong_yaos = [i for i, yao in enumerate(yao_results) if yao.get('is_dong', False)]
    
    # 生成变卦（如果有动爻）
    bian_hexagram = None
    if dong_yaos:
        bian_yaos = []
        for i, yao in enumerate(yao_results):
            if yao.get('is_dong', False):
                # 动爻变：老阴变阳，老阳变阴
                new_yao = yao.copy()
                new_yao['is_yang'] = not yao['is_yang']
                new_yao['is_dong'] = False
                new_yao['symbol'] = '⚊' if new_yao['is_yang'] else '⚋'
                new_yao['yao_number'] = 7 if new_yao['is_yang'] else 8
                bian_yaos.append(new_yao)
            else:
                bian_yaos.append(yao)
        
        # 识别变卦
        bian_inner_yaos = bian_yaos[0:3]
        bian_outer_yaos = bian_yaos[3:6]
        bian_inner_trigram = identify_trigram(bian_inner_yaos)
        bian_outer_trigram = identify_trigram(bian_outer_yaos)
        
        bian_hexagram_detail = get_hexagram_by_trigrams(
            bian_inner_trigram['name'], 
            bian_outer_trigram['name']
        )
        
        if bian_hexagram_detail:
            bian_hexagram = bian_hexagram_detail.copy()
            bian_hexagram['inner_trigram'] = bian_inner_trigram['name']
            bian_hexagram['outer_trigram'] = bian_outer_trigram['name']
        else:
            bian_hexagram = {
                'name': f"{bian_outer_trigram['name']}{bian_inner_trigram['name']}",
                'full_name': f"{bian_outer_trigram['name']}上{bian_inner_trigram['name']}下",
                'inner': bian_inner_trigram['name'],
                'outer': bian_outer_trigram['name'],
                'inner_trigram': bian_inner_trigram['name'],
                'outer_trigram': bian_outer_trigram['name'],
                'guaci': '（变卦卦辞待补充）',
                'yaoci': {str(i+1): f"第{i+1}爻：爻辞待补充" for i in range(6)}
            }
    
    return {
        'ben_hexagram': hexagram_info,  # 本卦
        'bian_hexagram': bian_hexagram,  # 变卦（如果有动爻）
        'yaos': yao_results,  # 六个爻的详细信息
        'dong_yaos': dong_yaos,  # 动爻索引列表（0-5，从下往上）
        'inner_trigram': inner_trigram,
        'outer_trigram': outer_trigram,
        'has_dong': len(dong_yaos) > 0,
    }


def create_hexagram_from_coin_results(coin_results: List[List[int]]) -> Dict[str, Any]:
    """
    从6次摇卦的铜钱结果创建卦象
    
    Args:
        coin_results: 6次摇卦结果，每次3枚铜钱（0=反面，1=正面）
    
    Returns:
        完整的卦象信息
    """
    # 将每次摇卦结果转换为爻信息
    yao_results = []
    for coins in coin_results:
        yao_info = coin_toss_to_yao(coins)
        yao_results.append(yao_info)
    
    # 创建卦象
    hexagram_data = create_hexagram(yao_results)
    
    return hexagram_data

