"""
紫微斗数神煞计算模块
基于 iztro 逻辑的完整实现

神煞：天乙贵人、红鸾天喜、孤辰寡宿等辅助星曜
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ==================== 神煞基础定义 ====================

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天乙贵人查表（根据年干和日干）
# 格式：年干 -> 日干 -> 天乙贵人所在宫位
TIANYI_GUIREN_TABLE = {
    '甲': {'戊': 1, '己': 7},  # 甲年：戊日贵人在丑，己日贵人在未
    '乙': {'己': 0, '庚': 6},  # 乙年：己日贵人在子，庚日贵人在午
    '丙': {'丁': 9, '壬': 3},  # 丙年：丁日贵人在亥，壬日贵人在卯
    '丁': {'丙': 9, '癸': 3},  # 丁年：丙日贵人在亥，癸日贵人在卯
    '戊': {'己': 1, '庚': 7},  # 戊年：己日贵人在丑，庚日贵人在未
    '己': {'戊': 1, '庚': 7},  # 己年：戊日贵人在丑，庚日贵人在未
    '庚': {'乙': 11, '辛': 5}, # 庚年：乙日贵人在寅，辛日贵人在申
    '辛': {'甲': 11, '庚': 5}, # 辛年：甲日贵人在寅，庚日贵人在申
    '壬': {'丁': 9, '癸': 3},  # 壬年：丁日贵人在亥，癸日贵人在卯
    '癸': {'丙': 9, '壬': 3},  # 癸年：丙日贵人在亥，壬日贵人在卯
}

# 红鸾天喜查表（根据年支）
# 红鸾和天喜相对（相隔6个宫位）
HONGLUAN_TIANXI_TABLE = {
    '子': {'红鸾': 2, '天喜': 8},  # 子年：红鸾在寅，天喜在申
    '丑': {'红鸾': 1, '天喜': 7},  # 丑年：红鸾在丑，天喜在未
    '寅': {'红鸾': 0, '天喜': 6},  # 寅年：红鸾在子，天喜在午
    '卯': {'红鸾': 11, '天喜': 5}, # 卯年：红鸾在亥，天喜在巳
    '辰': {'红鸾': 10, '天喜': 4}, # 辰年：红鸾在戌，天喜在辰
    '巳': {'红鸾': 9, '天喜': 3},  # 巳年：红鸾在酉，天喜在卯
    '午': {'红鸾': 8, '天喜': 2},  # 午年：红鸾在申，天喜在寅
    '未': {'红鸾': 7, '天喜': 1},  # 未年：红鸾在未，天喜在丑
    '申': {'红鸾': 6, '天喜': 0},  # 申年：红鸾在午，天喜在子
    '酉': {'红鸾': 5, '天喜': 11}, # 酉年：红鸾在巳，天喜在亥
    '戌': {'红鸾': 4, '天喜': 10}, # 戌年：红鸾在辰，天喜在戌
    '亥': {'红鸾': 3, '天喜': 9},  # 亥年：红鸾在卯，天喜在酉
}

# 孤辰寡宿查表（根据年支）
GUCHEN_GUASU_TABLE = {
    '子': {'孤辰': 2, '寡宿': 10},  # 子年：孤辰在寅，寡宿在戌
    '丑': {'孤辰': 2, '寡宿': 10},  # 丑年：孤辰在寅，寡宿在戌
    '寅': {'孤辰': 5, '寡宿': 1},   # 寅年：孤辰在巳，寡宿在丑
    '卯': {'孤辰': 5, '寡宿': 1},   # 卯年：孤辰在巳，寡宿在丑
    '辰': {'孤辰': 5, '寡宿': 1},   # 辰年：孤辰在巳，寡宿在丑
    '巳': {'孤辰': 8, '寡宿': 4},   # 巳年：孤辰在申，寡宿在辰
    '午': {'孤辰': 8, '寡宿': 4},   # 午年：孤辰在申，寡宿在辰
    '未': {'孤辰': 8, '寡宿': 4},   # 未年：孤辰在申，寡宿在辰
    '申': {'孤辰': 11, '寡宿': 7},  # 申年：孤辰在亥，寡宿在未
    '酉': {'孤辰': 11, '寡宿': 7},  # 酉年：孤辰在亥，寡宿在未
    '戌': {'孤辰': 11, '寡宿': 7},  # 戌年：孤辰在亥，寡宿在未
    '亥': {'孤辰': 2, '寡宿': 10},  # 亥年：孤辰在寅，寡宿在戌
}

# ==================== 工具函数 ====================

def get_di_zhi_index(zhi: str) -> int:
    """获取地支索引"""
    return DI_ZHI.index(zhi)

def normalize_palace_index(index: int) -> int:
    """标准化宫位索引（0-11）"""
    return index % 12

# ==================== 神煞计算函数 ====================

def calculate_tianyi_guiren(year_gan: str, day_gan: str) -> Optional[int]:
    """
    计算天乙贵人所在宫位
    
    Args:
        year_gan: 年干
        day_gan: 日干
    
    Returns:
        天乙贵人所在宫位索引，如果未找到则返回None
    """
    if year_gan not in TIANYI_GUIREN_TABLE:
        logger.warning(f"未找到年干 {year_gan} 的天乙贵人表")
        return None
    
    if day_gan not in TIANYI_GUIREN_TABLE[year_gan]:
        logger.debug(f"年干 {year_gan} 的日干 {day_gan} 无天乙贵人")
        return None
    
    palace = TIANYI_GUIREN_TABLE[year_gan][day_gan]
    logger.debug(f"天乙贵人: 年干={year_gan}, 日干={day_gan}, 宫位={palace}")
    return palace

def calculate_hongluan_tianxi(year_zhi: str) -> Dict[str, int]:
    """
    计算红鸾天喜所在宫位
    
    Args:
        year_zhi: 年支
    
    Returns:
        红鸾和天喜所在宫位索引字典
    """
    if year_zhi not in HONGLUAN_TIANXI_TABLE:
        logger.warning(f"未找到年支 {year_zhi} 的红鸾天喜表")
        return {}
    
    result = HONGLUAN_TIANXI_TABLE[year_zhi].copy()
    logger.debug(f"红鸾天喜: 年支={year_zhi}, {result}")
    return result

def calculate_guchen_guasu(year_zhi: str) -> Dict[str, int]:
    """
    计算孤辰寡宿所在宫位
    
    Args:
        year_zhi: 年支
    
    Returns:
        孤辰和寡宿所在宫位索引字典
    """
    if year_zhi not in GUCHEN_GUASU_TABLE:
        logger.warning(f"未找到年支 {year_zhi} 的孤辰寡宿表")
        return {}
    
    result = GUCHEN_GUASU_TABLE[year_zhi].copy()
    logger.debug(f"孤辰寡宿: 年支={year_zhi}, {result}")
    return result

def calculate_all_shensha(year_gan: str, year_zhi: str, day_gan: str) -> Dict[str, int]:
    """
    计算所有神煞位置
    
    Args:
        year_gan: 年干
        year_zhi: 年支
        day_gan: 日干
    
    Returns:
        所有神煞名称到宫位索引的字典
    """
    all_shensha = {}
    
    # 天乙贵人
    tianyi = calculate_tianyi_guiren(year_gan, day_gan)
    if tianyi is not None:
        all_shensha['天乙贵人'] = tianyi
    
    # 红鸾天喜
    hongluan_tianxi = calculate_hongluan_tianxi(year_zhi)
    all_shensha.update(hongluan_tianxi)
    
    # 孤辰寡宿
    guchen_guasu = calculate_guchen_guasu(year_zhi)
    all_shensha.update(guchen_guasu)
    
    logger.info(f"所有神煞: {all_shensha}")
    return all_shensha

# ==================== 神煞影响分析 ====================

def analyze_shensha_impact(pan_data: Dict, shensha_data: Dict) -> Dict:
    """
    分析神煞对命盘的影响
    
    Args:
        pan_data: 命盘数据
        shensha_data: 神煞数据（神煞名称到宫位索引的字典）
    
    Returns:
        神煞影响分析结果
    """
    palaces = pan_data.get('palaces', [])
    
    # 分析各神煞的影响
    analysis = {
        'tianyi_guiren': _analyze_tianyi_guiren(shensha_data, palaces),
        'hongluan_tianxi': _analyze_hongluan_tianxi(shensha_data, palaces),
        'guchen_guasu': _analyze_guchen_guasu(shensha_data, palaces),
    }
    
    # 生成总结
    summary = _generate_shensha_summary(analysis)
    
    result = {
        'shensha_data': shensha_data,
        'analysis': analysis,
        'summary': summary,
    }
    
    logger.info("神煞影响分析完成")
    return result

def _analyze_tianyi_guiren(shensha_data: Dict, palaces: List[Dict]) -> Dict:
    """分析天乙贵人的影响"""
    if '天乙贵人' not in shensha_data:
        return {'message': '无天乙贵人'}
    
    palace_index = shensha_data['天乙贵人']
    palace = next((p for p in palaces if p['index'] == palace_index), None)
    
    if not palace:
        return {'message': '天乙贵人宫位未找到'}
    
    analysis = {
        'palace': palace['name'],
        'palace_index': palace_index,
        'impact': f"天乙贵人在{palace['name']}，该宫位有贵人相助，容易得到帮助和支持",
    }
    
    return analysis

def _analyze_hongluan_tianxi(shensha_data: Dict, palaces: List[Dict]) -> Dict:
    """分析红鸾天喜的影响"""
    analysis = {}
    
    if '红鸾' in shensha_data:
        palace_index = shensha_data['红鸾']
        palace = next((p for p in palaces if p['index'] == palace_index), None)
        if palace:
            analysis['红鸾'] = {
                'palace': palace['name'],
                'palace_index': palace_index,
                'impact': f"红鸾在{palace['name']}，该宫位与感情、婚姻相关，容易有桃花运",
            }
    
    if '天喜' in shensha_data:
        palace_index = shensha_data['天喜']
        palace = next((p for p in palaces if p['index'] == palace_index), None)
        if palace:
            analysis['天喜'] = {
                'palace': palace['name'],
                'palace_index': palace_index,
                'impact': f"天喜在{palace['name']}，该宫位与喜庆、好事相关",
            }
    
    if not analysis:
        analysis['message'] = '无红鸾天喜'
    
    return analysis

def _analyze_guchen_guasu(shensha_data: Dict, palaces: List[Dict]) -> Dict:
    """分析孤辰寡宿的影响"""
    analysis = {}
    
    if '孤辰' in shensha_data:
        palace_index = shensha_data['孤辰']
        palace = next((p for p in palaces if p['index'] == palace_index), None)
        if palace:
            analysis['孤辰'] = {
                'palace': palace['name'],
                'palace_index': palace_index,
                'impact': f"孤辰在{palace['name']}，该宫位可能较为孤独，需要注意人际关系",
            }
    
    if '寡宿' in shensha_data:
        palace_index = shensha_data['寡宿']
        palace = next((p for p in palaces if p['index'] == palace_index), None)
        if palace:
            analysis['寡宿'] = {
                'palace': palace['name'],
                'palace_index': palace_index,
                'impact': f"寡宿在{palace['name']}，该宫位可能较为孤单，需要注意情感生活",
            }
    
    if not analysis:
        analysis['message'] = '无孤辰寡宿'
    
    return analysis

def _generate_shensha_summary(analysis: Dict) -> str:
    """生成神煞分析总结"""
    summary_parts = []
    
    # 天乙贵人
    if 'tianyi_guiren' in analysis and 'impact' in analysis['tianyi_guiren']:
        summary_parts.append(analysis['tianyi_guiren']['impact'])
    
    # 红鸾天喜
    if 'hongluan_tianxi' in analysis:
        if '红鸾' in analysis['hongluan_tianxi']:
            summary_parts.append(analysis['hongluan_tianxi']['红鸾']['impact'])
        if '天喜' in analysis['hongluan_tianxi']:
            summary_parts.append(analysis['hongluan_tianxi']['天喜']['impact'])
    
    # 孤辰寡宿
    if 'guchen_guasu' in analysis:
        if '孤辰' in analysis['guchen_guasu']:
            summary_parts.append(analysis['guchen_guasu']['孤辰']['impact'])
        if '寡宿' in analysis['guchen_guasu']:
            summary_parts.append(analysis['guchen_guasu']['寡宿']['impact'])
    
    return "；".join(summary_parts) if summary_parts else "无特殊神煞影响"

