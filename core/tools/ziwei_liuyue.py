"""
紫微斗数流月计算模块
基于 iztro 逻辑的完整实现

流月：每月的天干地支，以及流月四化等
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ==================== 流月基础定义 ====================

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 月份对应地支（农历月份）
MONTH_TO_DI_ZHI = {
    1: '寅', 2: '卯', 3: '辰', 4: '巳', 5: '午', 6: '未',
    7: '申', 8: '酉', 9: '戌', 10: '亥', 11: '子', 12: '丑',
}

# 流月天干查表（根据流年天干和月份）
# 格式：流年天干 -> 月份(1-12) -> 流月天干
LIUYUE_GAN_TABLE = {
    '甲': {1: '丙', 2: '丁', 3: '戊', 4: '己', 5: '庚', 6: '辛', 7: '壬', 8: '癸', 9: '甲', 10: '乙', 11: '丙', 12: '丁'},
    '乙': {1: '戊', 2: '己', 3: '庚', 4: '辛', 5: '壬', 6: '癸', 7: '甲', 8: '乙', 9: '丙', 10: '丁', 11: '戊', 12: '己'},
    '丙': {1: '庚', 2: '辛', 3: '壬', 4: '癸', 5: '甲', 6: '乙', 7: '丙', 8: '丁', 9: '戊', 10: '己', 11: '庚', 12: '辛'},
    '丁': {1: '壬', 2: '癸', 3: '甲', 4: '乙', 5: '丙', 6: '丁', 7: '戊', 8: '己', 9: '庚', 10: '辛', 11: '壬', 12: '癸'},
    '戊': {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己', 7: '庚', 8: '辛', 9: '壬', 10: '癸', 11: '甲', 12: '乙'},
    '己': {1: '丙', 2: '丁', 3: '戊', 4: '己', 5: '庚', 6: '辛', 7: '壬', 8: '癸', 9: '甲', 10: '乙', 11: '丙', 12: '丁'},
    '庚': {1: '戊', 2: '己', 3: '庚', 4: '辛', 5: '壬', 6: '癸', 7: '甲', 8: '乙', 9: '丙', 10: '丁', 11: '戊', 12: '己'},
    '辛': {1: '庚', 2: '辛', 3: '壬', 4: '癸', 5: '甲', 6: '乙', 7: '丙', 8: '丁', 9: '戊', 10: '己', 11: '庚', 12: '辛'},
    '壬': {1: '壬', 2: '癸', 3: '甲', 4: '乙', 5: '丙', 6: '丁', 7: '戊', 8: '己', 9: '庚', 10: '辛', 11: '壬', 12: '癸'},
    '癸': {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己', 7: '庚', 8: '辛', 9: '壬', 10: '癸', 11: '甲', 12: '乙'},
}

# ==================== 流月计算函数 ====================

def get_liuyue_gan(liunian_gan: str, month: int) -> str:
    """
    根据流年天干和月份获取流月天干
    
    Args:
        liunian_gan: 流年天干
        month: 月份（1-12，农历月份）
    
    Returns:
        流月天干
    """
    if liunian_gan not in LIUYUE_GAN_TABLE:
        logger.warning(f"未找到流年天干 {liunian_gan} 的流月天干表")
        return TIAN_GAN[0]  # 默认返回甲
    
    if month not in LIUYUE_GAN_TABLE[liunian_gan]:
        logger.warning(f"月份 {month} 超出范围")
        return TIAN_GAN[0]
    
    liuyue_gan = LIUYUE_GAN_TABLE[liunian_gan][month]
    logger.debug(f"流月天干: 流年天干={liunian_gan}, 月份={month}, 流月天干={liuyue_gan}")
    return liuyue_gan

def get_liuyue_zhi(month: int) -> str:
    """
    根据月份获取流月地支
    
    Args:
        month: 月份（1-12，农历月份）
    
    Returns:
        流月地支
    """
    if month not in MONTH_TO_DI_ZHI:
        logger.warning(f"月份 {month} 超出范围")
        return DI_ZHI[0]  # 默认返回子
    
    liuyue_zhi = MONTH_TO_DI_ZHI[month]
    logger.debug(f"流月地支: 月份={month}, 流月地支={liuyue_zhi}")
    return liuyue_zhi

# ==================== 流月四化计算 ====================

def calculate_liuyue_si_hua(liuyue_gan: str) -> Dict[str, str]:
    """
    计算流月四化配置
    
    流月四化根据流月天干确定，规则与年干四化相同
    
    Args:
        liuyue_gan: 流月天干
    
    Returns:
        流月四化配置：{化禄: 星名, 化权: 星名, 化科: 星名, 化忌: 星名}
    """
    try:
        from core.tools.ziwei_si_hua import get_si_hua_stars
        si_hua_config = get_si_hua_stars(liuyue_gan)
        logger.debug(f"流月四化: 流月天干={liuyue_gan}, 四化配置={si_hua_config}")
        return si_hua_config
    except ImportError:
        logger.warning("无法导入四化星模块，使用简化处理")
        return {
            '化禄': '',
            '化权': '',
            '化科': '',
            '化忌': '',
        }

def calculate_liuyue_pan(liunian_gan: str, month: int) -> Dict:
    """
    计算流月命盘数据
    
    Args:
        liunian_gan: 流年天干
        month: 月份（1-12，农历月份）
    
    Returns:
        流月命盘数据
    """
    # 计算流月天干地支
    liuyue_gan = get_liuyue_gan(liunian_gan, month)
    liuyue_zhi = get_liuyue_zhi(month)
    
    # 计算流月四化
    si_hua_config = calculate_liuyue_si_hua(liuyue_gan)
    
    # 构建流月数据
    liuyue_data = {
        'month': month,
        'gan': liuyue_gan,
        'zhi': liuyue_zhi,
        'gan_zhi': f"{liuyue_gan}{liuyue_zhi}",
        'si_hua': si_hua_config,
    }
    
    logger.info(f"流月命盘计算完成: {month}月 ({liuyue_gan}{liuyue_zhi})")
    return liuyue_data

def get_current_liuyue(liunian_gan: str, current_month: int) -> Dict:
    """
    获取当前流月信息
    
    Args:
        liunian_gan: 流年天干
        current_month: 当前月份（1-12，农历月份）
    
    Returns:
        当前流月信息
    """
    liuyue_gan = get_liuyue_gan(liunian_gan, current_month)
    liuyue_zhi = get_liuyue_zhi(current_month)
    si_hua_config = calculate_liuyue_si_hua(liuyue_gan)
    
    current_liuyue = {
        'month': current_month,
        'gan': liuyue_gan,
        'zhi': liuyue_zhi,
        'gan_zhi': f"{liuyue_gan}{liuyue_zhi}",
        'si_hua': si_hua_config,
    }
    
    logger.info(f"当前流月: {current_month}月 ({liuyue_gan}{liuyue_zhi})")
    return current_liuyue

# ==================== 流月影响分析 ====================

def analyze_liuyue_impact(pan_data: Dict, liuyue_data: Dict) -> Dict:
    """
    分析流月对命盘的影响
    
    Args:
        pan_data: 原命盘数据
        liuyue_data: 流月数据
    
    Returns:
        流月影响分析结果
    """
    # 分析流月四化
    si_hua_analysis = _analyze_liuyue_si_hua(liuyue_data)
    
    # 生成总结
    summary = _generate_liuyue_summary(liuyue_data, si_hua_analysis)
    
    result = {
        'liuyue': liuyue_data,
        'si_hua_analysis': si_hua_analysis,
        'summary': summary,
    }
    
    logger.info("流月影响分析完成")
    return result

def _analyze_liuyue_si_hua(liuyue_data: Dict) -> Dict:
    """分析流月四化影响"""
    si_hua_config = liuyue_data.get('si_hua', {})
    
    analysis = {
        'config': si_hua_config,
        'has_hua_lu': bool(si_hua_config.get('化禄')),
        'has_hua_quan': bool(si_hua_config.get('化权')),
        'has_hua_ke': bool(si_hua_config.get('化科')),
        'has_hua_ji': bool(si_hua_config.get('化忌')),
        'impact': [],
    }
    
    if analysis['has_hua_lu']:
        analysis['impact'].append(f"流月有{si_hua_config['化禄']}化禄，财运和福气较好")
    
    if analysis['has_hua_quan']:
        analysis['impact'].append(f"流月有{si_hua_config['化权']}化权，权力和掌控力较强")
    
    if analysis['has_hua_ke']:
        analysis['impact'].append(f"流月有{si_hua_config['化科']}化科，名声和贵人运不错")
    
    if analysis['has_hua_ji']:
        analysis['impact'].append(f"⚠️ 流月有{si_hua_config['化忌']}化忌，需要特别注意")
    
    if not analysis['impact']:
        analysis['impact'].append('流月无四化，影响较为平稳')
    
    return analysis

def _generate_liuyue_summary(liuyue_data: Dict, si_hua_analysis: Dict) -> str:
    """生成流月分析总结"""
    summary_parts = []
    
    # 基本信息
    summary_parts.append(
        f"{liuyue_data['month']}月（{liuyue_data['gan_zhi']}）"
    )
    
    # 四化影响
    if si_hua_analysis['impact']:
        summary_parts.extend(si_hua_analysis['impact'])
    
    return "；".join(summary_parts)

