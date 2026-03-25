"""
八字排盘计算器
实现四柱、五行、十神、大运、流年、神煞的计算
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# ==================== 基础常量定义 ====================

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干五行
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 地支五行
DI_ZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 天干阴阳
TIAN_GAN_YINYANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
    '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
    '壬': '阳', '癸': '阴',
}

# 地支藏干（每个地支包含1-3个天干）
# 格式：地支 -> [本气, 中气, 余气]
DI_ZHI_CANG_GAN = {
    '子': ['癸'],                    # 本气：癸
    '丑': ['己', '癸', '辛'],        # 本气：己，中气：癸，余气：辛
    '寅': ['甲', '丙', '戊'],        # 本气：甲，中气：丙，余气：戊
    '卯': ['乙'],                    # 本气：乙
    '辰': ['戊', '乙', '癸'],        # 本气：戊，中气：乙，余气：癸
    '巳': ['丙', '戊', '庚'],        # 本气：丙，中气：戊，余气：庚
    '午': ['丁', '己'],              # 本气：丁，中气：己
    '未': ['己', '丁', '乙'],        # 本气：己，中气：丁，余气：乙
    '申': ['庚', '壬', '戊'],        # 本气：庚，中气：壬，余气：戊
    '酉': ['辛'],                    # 本气：辛
    '戌': ['戊', '辛', '丁'],        # 本气：戊，中气：辛，余气：丁
    '亥': ['壬', '甲'],              # 本气：壬，中气：甲
}

# 十神关系（以日主为基准）
# 生我者为印（正印、偏印），我生者为食伤（食神、伤官）
# 克我者为官杀（正官、七杀），我克者为财（正财、偏财）
# 同我者为比劫（比肩、劫财）
SHI_SHEN_MAP = {
    '比肩': {'same': True, 'same_yinyang': True},
    '劫财': {'same': True, 'same_yinyang': False},
    '食神': {'sheng_wo': False, 'wo_sheng': True, 'same_yinyang': True},
    '伤官': {'sheng_wo': False, 'wo_sheng': True, 'same_yinyang': False},
    '偏财': {'sheng_wo': False, 'wo_ke': True, 'same_yinyang': True},
    '正财': {'sheng_wo': False, 'wo_ke': True, 'same_yinyang': False},
    '七杀': {'sheng_wo': True, 'ke_wo': True, 'same_yinyang': True},
    '正官': {'sheng_wo': True, 'ke_wo': True, 'same_yinyang': False},
    '偏印': {'sheng_wo': True, 'ke_wo': False, 'same_yinyang': True},
    '正印': {'sheng_wo': True, 'ke_wo': False, 'same_yinyang': False},
}

# 五行生克关系
WUXING_SHENG = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
}

WUXING_KE = {
    '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
}

# 月份对应地支（农历月份，正月为寅）
MONTH_TO_DI_ZHI = {
    1: '寅', 2: '卯', 3: '辰', 4: '巳', 5: '午', 6: '未',
    7: '申', 8: '酉', 9: '戌', 10: '亥', 11: '子', 12: '丑',
}

# 月干查表（根据年干和月份）
# 格式：年干 -> 月份(1-12) -> 月干
YUE_GAN_TABLE = {
    '甲': {1: '丙', 2: '丁', 3: '戊', 4: '己', 5: '庚', 6: '辛',
           7: '壬', 8: '癸', 9: '甲', 10: '乙', 11: '丙', 12: '丁'},
    '乙': {1: '戊', 2: '己', 3: '庚', 4: '辛', 5: '壬', 6: '癸',
           7: '甲', 8: '乙', 9: '丙', 10: '丁', 11: '戊', 12: '己'},
    '丙': {1: '庚', 2: '辛', 3: '壬', 4: '癸', 5: '甲', 6: '乙',
           7: '丙', 8: '丁', 9: '戊', 10: '己', 11: '庚', 12: '辛'},
    '丁': {1: '壬', 2: '癸', 3: '甲', 4: '乙', 5: '丙', 6: '丁',
           7: '戊', 8: '己', 9: '庚', 10: '辛', 11: '壬', 12: '癸'},
    '戊': {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己',
           7: '庚', 8: '辛', 9: '壬', 10: '癸', 11: '甲', 12: '乙'},
    '己': {1: '丙', 2: '丁', 3: '戊', 4: '己', 5: '庚', 6: '辛',
           7: '壬', 8: '癸', 9: '甲', 10: '乙', 11: '丙', 12: '丁'},
    '庚': {1: '戊', 2: '己', 3: '庚', 4: '辛', 5: '壬', 6: '癸',
           7: '甲', 8: '乙', 9: '丙', 10: '丁', 11: '戊', 12: '己'},
    '辛': {1: '庚', 2: '辛', 3: '壬', 4: '癸', 5: '甲', 6: '乙',
           7: '丙', 8: '丁', 9: '戊', 10: '己', 11: '庚', 12: '辛'},
    '壬': {1: '壬', 2: '癸', 3: '甲', 4: '乙', 5: '丙', 6: '丁',
           7: '戊', 8: '己', 9: '庚', 10: '辛', 11: '壬', 12: '癸'},
    '癸': {1: '甲', 2: '乙', 3: '丙', 4: '丁', 5: '戊', 6: '己',
           7: '庚', 8: '辛', 9: '壬', 10: '癸', 11: '甲', 12: '乙'},
}

# 时干查表（根据日干和时辰）
# 格式：日干 -> 时辰地支 -> 时干
SHI_GAN_TABLE = {
    '甲': {'子': '甲', '丑': '乙', '寅': '丙', '卯': '丁', '辰': '戊', '巳': '己',
           '午': '庚', '未': '辛', '申': '壬', '酉': '癸', '戌': '甲', '亥': '乙'},
    '乙': {'子': '丙', '丑': '丁', '寅': '戊', '卯': '己', '辰': '庚', '巳': '辛',
           '午': '壬', '未': '癸', '申': '甲', '酉': '乙', '戌': '丙', '亥': '丁'},
    '丙': {'子': '戊', '丑': '己', '寅': '庚', '卯': '辛', '辰': '壬', '巳': '癸',
           '午': '甲', '未': '乙', '申': '丙', '酉': '丁', '戌': '戊', '亥': '己'},
    '丁': {'子': '庚', '丑': '辛', '寅': '壬', '卯': '癸', '辰': '甲', '巳': '乙',
           '午': '丙', '未': '丁', '申': '戊', '酉': '己', '戌': '庚', '亥': '辛'},
    '戊': {'子': '壬', '丑': '癸', '寅': '甲', '卯': '乙', '辰': '丙', '巳': '丁',
           '午': '戊', '未': '己', '申': '庚', '酉': '辛', '戌': '壬', '亥': '癸'},
    '己': {'子': '甲', '丑': '乙', '寅': '丙', '卯': '丁', '辰': '戊', '巳': '己',
           '午': '庚', '未': '辛', '申': '壬', '酉': '癸', '戌': '甲', '亥': '乙'},
    '庚': {'子': '丙', '丑': '丁', '寅': '戊', '卯': '己', '辰': '庚', '巳': '辛',
           '午': '壬', '未': '癸', '申': '甲', '酉': '乙', '戌': '丙', '亥': '丁'},
    '辛': {'子': '戊', '丑': '己', '寅': '庚', '卯': '辛', '辰': '壬', '巳': '癸',
           '午': '甲', '未': '乙', '申': '丙', '酉': '丁', '戌': '戊', '亥': '己'},
    '壬': {'子': '庚', '丑': '辛', '寅': '壬', '卯': '癸', '辰': '甲', '巳': '乙',
           '午': '丙', '未': '丁', '申': '戊', '酉': '己', '戌': '庚', '亥': '辛'},
    '癸': {'子': '壬', '丑': '癸', '寅': '甲', '卯': '乙', '辰': '丙', '巳': '丁',
           '午': '戊', '未': '己', '申': '庚', '酉': '辛', '戌': '壬', '亥': '癸'},
}

# ==================== 工具函数 ====================

def get_tian_gan(year: int) -> str:
    """根据年份获取天干"""
    base_year = 1984  # 1984年是甲子年
    gan_index = (year - base_year) % 10
    return TIAN_GAN[gan_index]

def get_di_zhi(year: int) -> str:
    """根据年份获取地支"""
    base_year = 1984  # 1984年是甲子年
    zhi_index = (year - base_year) % 12
    return DI_ZHI[zhi_index]

def get_tian_gan_index(gan: str) -> int:
    """获取天干索引"""
    return TIAN_GAN.index(gan)

def get_di_zhi_index(zhi: str) -> int:
    """获取地支索引"""
    return DI_ZHI.index(zhi)

def convert_to_lunar(year: int, month: int, day: int) -> Tuple[int, int, int]:
    """
    将公历日期转换为农历日期
    复用紫微斗数的农历转换逻辑
    """
    try:
        from core.tools.ziwei_calculator import convert_to_lunar as ziwei_convert
        return ziwei_convert(year, month, day)
    except Exception as e:
        logger.warning(f"农历转换失败: {e}，使用公历日期")
        return year, month, day

def get_day_gan_zhi(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算日柱的天干地支
    使用1900年1月1日为基准（甲子日）
    """
    base_date = datetime(1900, 1, 1)
    target_date = datetime(year, month, day)
    days_diff = (target_date - base_date).days
    
    # 1900年1月1日是甲子日（天干索引0，地支索引0）
    gan_index = (days_diff) % 10
    zhi_index = (days_diff) % 12
    
    return TIAN_GAN[gan_index], DI_ZHI[zhi_index]

def hour_to_shi_chen(hour: int) -> str:
    """将24小时制转换为地支时辰"""
    hour_to_shi_chen_map = {
        23: '子', 0: '子', 1: '丑', 2: '丑', 3: '寅', 4: '寅',
        5: '卯', 6: '卯', 7: '辰', 8: '辰', 9: '巳', 10: '巳',
        11: '午', 12: '午', 13: '未', 14: '未', 15: '申', 16: '申',
        17: '酉', 18: '酉', 19: '戌', 20: '戌', 21: '亥', 22: '亥'
    }
    return hour_to_shi_chen_map.get(hour, '子')

# ==================== 核心计算函数 ====================

def calculate_sizhu(year: int, month: int, day: int, hour: int) -> Dict[str, Any]:
    """
    计算四柱（年柱、月柱、日柱、时柱）
    使用节气确定年柱和月柱，确保准确性
    
    重要：八字命理中，年柱以立春为界，而非公历新年
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
    
    Returns:
        四柱数据字典
    """
    # 转换为农历（用于显示）
    lunar_year, lunar_month, lunar_day = convert_to_lunar(year, month, day)
    
    # 确定八字年份：以立春为界
    # 立春前出生的，年柱属于上一年；立春后出生的，年柱属于当年
    from core.tools.solar_terms import get_solar_term_date
    
    birth_date = datetime(year, month, day, hour if hour else 12)
    
    # 获取当年的立春日期
    this_year_lichun = get_solar_term_date(year, 0)  # 立春是第0个节气
    
    # 判断出生日期是否在立春之前
    if birth_date < this_year_lichun:
        # 立春前出生，年柱属于上一年
        bazi_year = year - 1
        logger.info(f"出生日期 {year}-{month}-{day} 在立春前，八字年份为 {bazi_year}")
    else:
        # 立春后出生，年柱属于当年
        bazi_year = year
        logger.info(f"出生日期 {year}-{month}-{day} 在立春后，八字年份为 {bazi_year}")
    
    # 年柱（使用八字年份）
    nian_gan = get_tian_gan(bazi_year)
    nian_zhi = get_di_zhi(bazi_year)
    
    # 月柱：使用节气确定（专业方法）
    from core.tools.solar_terms import get_month_zhi_by_solar_term, get_month_index_by_solar_term
    yue_zhi = get_month_zhi_by_solar_term(year, month, day)
    month_index = get_month_index_by_solar_term(year, month, day)
    yue_gan = YUE_GAN_TABLE.get(nian_gan, {}).get(month_index, '丙')
    
    # 日柱
    ri_gan, ri_zhi = get_day_gan_zhi(year, month, day)
    
    # 时柱
    shi_chen = hour_to_shi_chen(hour)
    shi_gan = SHI_GAN_TABLE.get(ri_gan, {}).get(shi_chen, '甲')
    shi_zhi = shi_chen
    
    return {
        'nian_zhu': {'tian_gan': nian_gan, 'di_zhi': nian_zhi},
        'yue_zhu': {'tian_gan': yue_gan, 'di_zhi': yue_zhi},
        'ri_zhu': {'tian_gan': ri_gan, 'di_zhi': ri_zhi},
        'shi_zhu': {'tian_gan': shi_gan, 'di_zhi': shi_zhi},
        'ri_zhu_tiangan': ri_gan,  # 日主
        'lunar_year': lunar_year,
        'lunar_month': lunar_month,
        'lunar_day': lunar_day,
        'month_index': month_index,  # 月份索引（1-12，基于节气）
        'bazi_year': bazi_year,  # 八字年份（可能与公历年份不同）
    }

def calculate_wuxing(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算五行分布（考虑地支藏干）
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        五行数据字典
    """
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    
    # 统计天干五行
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        zhi = zhu.get('di_zhi', '')
        
        # 天干五行（权重1）
        if gan and gan in TIAN_GAN_WUXING:
            wuxing = TIAN_GAN_WUXING[gan]
            wuxing_count[wuxing] = wuxing_count.get(wuxing, 0) + 1
        
        # 地支藏干五行（考虑藏干）
        if zhi and zhi in DI_ZHI_CANG_GAN:
            cang_gan_list = DI_ZHI_CANG_GAN[zhi]
            for cang_gan in cang_gan_list:
                if cang_gan in TIAN_GAN_WUXING:
                    wuxing = TIAN_GAN_WUXING[cang_gan]
                    # 本气权重1，中气权重0.5，余气权重0.25
                    if len(cang_gan_list) == 1:
                        weight = 1.0  # 只有本气
                    elif cang_gan == cang_gan_list[0]:
                        weight = 1.0  # 本气
                    elif cang_gan == cang_gan_list[1]:
                        weight = 0.5  # 中气
                    else:
                        weight = 0.25  # 余气
                    wuxing_count[wuxing] = wuxing_count.get(wuxing, 0) + weight
    
    # 日主五行
    ri_zhu_gan = sizhu.get('ri_zhu_tiangan', '')
    rizhu_wuxing = TIAN_GAN_WUXING.get(ri_zhu_gan, '')
    
    # 转换为整数（四舍五入）
    return {
        'jin': round(wuxing_count.get('金', 0)),
        'mu': round(wuxing_count.get('木', 0)),
        'shui': round(wuxing_count.get('水', 0)),
        'huo': round(wuxing_count.get('火', 0)),
        'tu': round(wuxing_count.get('土', 0)),
        'rizhu_wuxing': rizhu_wuxing,
        'wuxing_count': {k: round(v) for k, v in wuxing_count.items()},
        'wuxing_count_detail': wuxing_count,  # 保留详细数据（带小数）
    }

def calculate_shishen(sizhu: Dict[str, Any], rizhu_tiangan: str) -> Dict[str, Any]:
    """
    计算十神关系
    
    Args:
        sizhu: 四柱数据
        rizhu_tiangan: 日主天干
    
    Returns:
        十神数据字典
    """
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_tiangan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_tiangan, '')
    
    shishen_result = {
        'nian_zhu': {},
        'yue_zhu': {},
        'ri_zhu': {},
        'shi_zhu': {},
    }
    
    def get_shishen(target_gan: str, target_zhi: str) -> Dict[str, str]:
        """计算单个天干地支的十神"""
        result = {}
        
        # 天干十神
        if target_gan:
            target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
            target_yinyang = TIAN_GAN_YINYANG.get(target_gan, '')
            
            if target_wuxing == rizhu_wuxing:
                # 同我者
                if target_yinyang == rizhu_yinyang:
                    result['gan_shishen'] = '比肩'
                else:
                    result['gan_shishen'] = '劫财'
            elif WUXING_SHENG.get(rizhu_wuxing) == target_wuxing:
                # 我生者
                if target_yinyang == rizhu_yinyang:
                    result['gan_shishen'] = '食神'
                else:
                    result['gan_shishen'] = '伤官'
            elif WUXING_SHENG.get(target_wuxing) == rizhu_wuxing:
                # 生我者
                if target_yinyang == rizhu_yinyang:
                    result['gan_shishen'] = '偏印'
                else:
                    result['gan_shishen'] = '正印'
            elif WUXING_KE.get(rizhu_wuxing) == target_wuxing:
                # 我克者
                if target_yinyang == rizhu_yinyang:
                    result['gan_shishen'] = '偏财'
                else:
                    result['gan_shishen'] = '正财'
            elif WUXING_KE.get(target_wuxing) == rizhu_wuxing:
                # 克我者
                if target_yinyang == rizhu_yinyang:
                    result['gan_shishen'] = '七杀'
                else:
                    result['gan_shishen'] = '正官'
        
        # 地支十神（使用地支藏干计算，更准确）
        if target_zhi and target_zhi in DI_ZHI_CANG_GAN:
            cang_gan_list = DI_ZHI_CANG_GAN[target_zhi]
            # 计算所有藏干的十神，主要使用本气
            if len(cang_gan_list) > 0:
                # 使用本气（第一个藏干）计算十神
                cang_gan = cang_gan_list[0]
                cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
                cang_gan_yinyang = TIAN_GAN_YINYANG.get(cang_gan, '')
                
                if cang_gan_wuxing == rizhu_wuxing:
                    if cang_gan_yinyang == rizhu_yinyang:
                        result['zhi_shishen'] = '比肩'
                    else:
                        result['zhi_shishen'] = '劫财'
                elif WUXING_SHENG.get(rizhu_wuxing) == cang_gan_wuxing:
                    if cang_gan_yinyang == rizhu_yinyang:
                        result['zhi_shishen'] = '食神'
                    else:
                        result['zhi_shishen'] = '伤官'
                elif WUXING_SHENG.get(cang_gan_wuxing) == rizhu_wuxing:
                    if cang_gan_yinyang == rizhu_yinyang:
                        result['zhi_shishen'] = '偏印'
                    else:
                        result['zhi_shishen'] = '正印'
                elif WUXING_KE.get(rizhu_wuxing) == cang_gan_wuxing:
                    if cang_gan_yinyang == rizhu_yinyang:
                        result['zhi_shishen'] = '偏财'
                    else:
                        result['zhi_shishen'] = '正财'
                elif WUXING_KE.get(cang_gan_wuxing) == rizhu_wuxing:
                    if cang_gan_yinyang == rizhu_yinyang:
                        result['zhi_shishen'] = '七杀'
                    else:
                        result['zhi_shishen'] = '正官'
                
                # 保存所有藏干的十神信息（用于详细分析）
                cang_gan_shishen_list = []
                for cang_gan in cang_gan_list:
                    cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
                    cang_gan_yinyang = TIAN_GAN_YINYANG.get(cang_gan, '')
                    
                    if cang_gan_wuxing == rizhu_wuxing:
                        shishen_name = '比肩' if cang_gan_yinyang == rizhu_yinyang else '劫财'
                    elif WUXING_SHENG.get(rizhu_wuxing) == cang_gan_wuxing:
                        shishen_name = '食神' if cang_gan_yinyang == rizhu_yinyang else '伤官'
                    elif WUXING_SHENG.get(cang_gan_wuxing) == rizhu_wuxing:
                        shishen_name = '偏印' if cang_gan_yinyang == rizhu_yinyang else '正印'
                    elif WUXING_KE.get(rizhu_wuxing) == cang_gan_wuxing:
                        shishen_name = '偏财' if cang_gan_yinyang == rizhu_yinyang else '正财'
                    elif WUXING_KE.get(cang_gan_wuxing) == rizhu_wuxing:
                        shishen_name = '七杀' if cang_gan_yinyang == rizhu_yinyang else '正官'
                    else:
                        shishen_name = ''
                    
                    if shishen_name:
                        cang_gan_shishen_list.append({
                            'cang_gan': cang_gan,
                            'shishen': shishen_name,
                        })
                
                if cang_gan_shishen_list:
                    result['zhi_cang_gan_shishen'] = cang_gan_shishen_list
        
        return result
    
    # 计算各柱的十神
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        zhi = zhu.get('di_zhi', '')
        
        if zhu_name == 'ri_zhu':
            # 日柱天干是日主，不计算十神
            zhi_result = get_shishen('', zhi)
            shishen_result[zhu_name] = {
                'gan_shishen': '日主',
                'zhi_shishen': zhi_result.get('zhi_shishen', ''),
                'zhi_cang_gan_shishen': zhi_result.get('zhi_cang_gan_shishen', []),
            }
        else:
            shishen_result[zhu_name] = get_shishen(gan, zhi)
    
    return shishen_result

def calculate_dayun(year: int, month: int, day: int, hour: int, gender: str, bazi_year: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    计算大运（精确计算起运年龄）
    根据年柱天干阴阳和性别确定顺逆，每10年一运

    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
        bazi_year: 八字年份（可选，如果提供则使用，否则根据立春计算）

    Returns:
        大运列表（每10年一运，共8步大运）
    """
    # 确定八字年份（以立春为界）
    if bazi_year is None:
        from core.tools.solar_terms import get_solar_term_date
        birth_date = datetime(year, month, day, hour if hour else 12)
        this_year_lichun = get_solar_term_date(year, 0)
        
        if birth_date < this_year_lichun:
            bazi_year = year - 1
        else:
            bazi_year = year
    
    # 计算年柱（使用八字年份）
    nian_gan = get_tian_gan(bazi_year)
    nian_zhi = get_di_zhi(bazi_year)
    nian_gan_yinyang = TIAN_GAN_YINYANG.get(nian_gan, '阳')

    # 确定顺逆：阳年男顺，阴年女顺；阳年女逆，阴年男逆
    is_shun = (nian_gan_yinyang == '阳' and gender == '男') or (nian_gan_yinyang == '阴' and gender == '女')

    # 精确计算起运年龄（根据节气）
    # 起运年龄计算规则：
    # 1. 24节气分为"节"和"气"，只有"节"用于起运计算
    # 2. "节"的索引：0(立春), 2(惊蛰), 4(清明), 6(立夏), 8(芒种), 10(小暑),
    #              12(立秋), 14(白露), 16(寒露), 18(立冬), 20(大雪), 22(小寒)
    # 3. 顺排：计算到下一个"节"的天数
    # 4. 逆排：计算到上一个"节"的天数
    # 5. 3天=1岁

    from core.tools.solar_terms import get_solar_term_date, SOLAR_TERMS

    target_date = datetime(year, month, day, hour)

    # "节"的索引列表（偶数索引）
    JIE_TERMS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]  # 立春、惊蛰、清明、立夏、芒种、小暑、立秋、白露、寒露、立冬、大雪、小寒

    def get_next_jie(target_date, current_year):
        """获取下一个节"""
        for year_offset in range(-1, 3):  # 查找前一年到后两年的范围
            check_year = current_year + year_offset
            for jie_idx in JIE_TERMS:
                jie_date = get_solar_term_date(check_year, jie_idx)
                if jie_date > target_date:
                    return jie_date
        return None

    def get_prev_jie(target_date, current_year):
        """获取上一个节"""
        for year_offset in range(2, -2, -1):  # 查找后两年到前一年的范围（倒序）
            check_year = current_year + year_offset
            for jie_idx in reversed(JIE_TERMS):  # 从最后一个节开始倒序查找
                jie_date = get_solar_term_date(check_year, jie_idx)
                if jie_date <= target_date:
                    return jie_date
        return None

    if is_shun:
        # 顺排：计算到下一个"节"的天数
        next_jie_date = get_next_jie(target_date, year)
        if next_jie_date:
            delta = next_jie_date - target_date
        else:
            # 找不到时使用默认值
            delta = timedelta(days=3)
    else:
        # 逆排：计算到上一个"节"的天数
        prev_jie_date = get_prev_jie(target_date, year)
        if prev_jie_date:
            delta = target_date - prev_jie_date
        else:
            # 找不到时使用默认值
            delta = timedelta(days=3)

    days_diff = delta.total_seconds() / 86400.0

    # 如果天数差为负数或太大（超过400天），说明计算有误，使用默认值
    if days_diff < 0 or days_diff > 400:
        logger.warning(f"起运年龄计算异常: days_diff={days_diff}, target_date={target_date}, 使用默认值1岁")
        qiyun_age_years = 1.0
    else:
        # 起运年龄计算：3天=1岁
        qiyun_age_years = days_diff / 3.0

        # 如果起运年龄小于0.1岁，设置为0.1岁（最小起运年龄）
        if qiyun_age_years < 0.1:
            qiyun_age_years = 0.1
        # 如果起运年龄大于10岁，说明计算有误，使用默认值
        elif qiyun_age_years > 10.0:
            logger.warning(f"起运年龄过大: {qiyun_age_years}岁, 使用默认值1岁")
            qiyun_age_years = 1.0

    # 计算大运
    dayun_list = []
    current_zhi_index = get_di_zhi_index(nian_zhi)
    current_gan_index = get_tian_gan_index(nian_gan)
    
    for i in range(8):  # 8步大运
        if is_shun:
            # 顺排
            zhi_index = (current_zhi_index + i + 1) % 12
            gan_index = (current_gan_index + i + 1) % 10
        else:
            # 逆排
            zhi_index = (current_zhi_index - i - 1) % 12
            gan_index = (current_gan_index - i - 1) % 10
        
        zhi = DI_ZHI[zhi_index]
        gan = TIAN_GAN[gan_index]
        
        # 起运年龄（精确到小数点后1位）
        start_age = round(qiyun_age_years + i * 10, 1)
        end_age = round(start_age + 9.9, 1)  # 每步大运10年
        
        dayun_list.append({
            'gan': gan,
            'zhi': zhi,
            'start_age': start_age,
            'end_age': end_age,
            'start_year': int(year + start_age),
            'end_year': int(year + end_age),
        })
    
    return dayun_list

def calculate_liunian(sizhu: Dict[str, Any], target_year: int) -> Dict[str, Any]:
    """
    计算流年（指定年份的干支）
    
    Args:
        sizhu: 四柱数据
        target_year: 目标年份
    
    Returns:
        流年数据
    """
    liunian_gan = get_tian_gan(target_year)
    liunian_zhi = get_di_zhi(target_year)
    
    return {
        'year': target_year,
        'gan': liunian_gan,
        'zhi': liunian_zhi,
        'gan_zhi': f"{liunian_gan}{liunian_zhi}",
    }

def calculate_shensha(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算神煞（扩展版本，包含多种常见神煞）
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        神煞数据
    """
    rizhu_gan = sizhu.get('ri_zhu_tiangan', '')
    rizhu_zhi = sizhu.get('ri_zhu', {}).get('di_zhi', '')
    yue_zhi = sizhu.get('yue_zhu', {}).get('di_zhi', '')
    
    shensha_list = []
    shensha_positions = set()  # 避免重复
    
    # 收集所有地支
    all_zhi = []
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi = sizhu.get(zhu_name, {}).get('di_zhi', '')
        if zhi:
            all_zhi.append((zhu_name, zhi))
    
    # 1. 天乙贵人
    # 甲戊见牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，庚辛逢虎马
    tianyi_guiren_map = {
        '甲': ['丑', '未'], '戊': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'],
        '丙': ['亥', '酉'], '丁': ['亥', '酉'],
        '壬': ['卯', '巳'], '癸': ['卯', '巳'],
        '庚': ['寅', '午'], '辛': ['寅', '午'],
    }
    
    tianyi_zhi = tianyi_guiren_map.get(rizhu_gan, [])
    for zhu_name, zhi in all_zhi:
        if zhi in tianyi_zhi:
            shensha_list.append({
                'name': '天乙贵人',
                'position': zhu_name,
                'zhi': zhi,
                'type': '吉',
            })
            shensha_positions.add((zhu_name, '天乙贵人'))
            break
    
    # 2. 桃花
    # 寅午戌见卯，申子辰见酉，巳酉丑见午，亥卯未见子
    taohua_map = {
        '寅': '卯', '午': '卯', '戌': '卯',
        '申': '酉', '子': '酉', '辰': '酉',
        '巳': '午', '酉': '午', '丑': '午',
        '亥': '子', '卯': '子', '未': '子',
    }
    
    for zhu_name, zhi in all_zhi:
        taohua_zhi = taohua_map.get(zhi, '')
        if taohua_zhi:
            for other_zhu_name, other_zhi in all_zhi:
                if other_zhi == taohua_zhi and (other_zhu_name, '桃花') not in shensha_positions:
                    shensha_list.append({
                        'name': '桃花',
                        'position': other_zhu_name,
                        'zhi': taohua_zhi,
                        'type': '中性',
                    })
                    shensha_positions.add((other_zhu_name, '桃花'))
                    break
    
    # 3. 驿马
    # 申子辰见寅，寅午戌见申，巳酉丑见亥，亥卯未见巳
    yima_map = {
        '申': '寅', '子': '寅', '辰': '寅',
        '寅': '申', '午': '申', '戌': '申',
        '巳': '亥', '酉': '亥', '丑': '亥',
        '亥': '巳', '卯': '巳', '未': '巳',
    }
    
    for zhu_name, zhi in all_zhi:
        yima_zhi = yima_map.get(zhi, '')
        if yima_zhi:
            for other_zhu_name, other_zhi in all_zhi:
                if other_zhi == yima_zhi and (other_zhu_name, '驿马') not in shensha_positions:
                    shensha_list.append({
                        'name': '驿马',
                        'position': other_zhu_name,
                        'zhi': yima_zhi,
                        'type': '中性',
                    })
                    shensha_positions.add((other_zhu_name, '驿马'))
                    break
    
    # 4. 华盖
    # 寅午戌见戌，申子辰见辰，巳酉丑见丑，亥卯未见未
    huagai_map = {
        '寅': '戌', '午': '戌', '戌': '戌',
        '申': '辰', '子': '辰', '辰': '辰',
        '巳': '丑', '酉': '丑', '丑': '丑',
        '亥': '未', '卯': '未', '未': '未',
    }
    
    for zhu_name, zhi in all_zhi:
        huagai_zhi = huagai_map.get(zhi, '')
        if huagai_zhi:
            for other_zhu_name, other_zhi in all_zhi:
                if other_zhi == huagai_zhi and (other_zhu_name, '华盖') not in shensha_positions:
                    shensha_list.append({
                        'name': '华盖',
                        'position': other_zhu_name,
                        'zhi': huagai_zhi,
                        'type': '中性',
                    })
                    shensha_positions.add((other_zhu_name, '华盖'))
                    break
    
    # 5. 文昌
    # 甲乙见巳，丙丁见申，戊己见申，庚辛见亥，壬癸见寅
    wenchang_map = {
        '甲': '巳', '乙': '巳',
        '丙': '申', '丁': '申',
        '戊': '申', '己': '申',
        '庚': '亥', '辛': '亥',
        '壬': '寅', '癸': '寅',
    }
    
    wenchang_zhi = wenchang_map.get(rizhu_gan, '')
    if wenchang_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == wenchang_zhi and (zhu_name, '文昌') not in shensha_positions:
                shensha_list.append({
                    'name': '文昌',
                    'position': zhu_name,
                    'zhi': wenchang_zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '文昌'))
                break
    
    # 6. 学堂（与文昌相关，通常在同一位置）
    if wenchang_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == wenchang_zhi and (zhu_name, '学堂') not in shensha_positions:
                shensha_list.append({
                    'name': '学堂',
                    'position': zhu_name,
                    'zhi': wenchang_zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '学堂'))
                break
    
    # 7. 天医
    # 正月见丑，二月见寅，三月见卯，四月见辰，五月见巳，六月见午
    # 七月见未，八月见申，九月见酉，十月见戌，十一月见亥，十二月见子
    tianyi_month_map = {
        1: '丑', 2: '寅', 3: '卯', 4: '辰', 5: '巳', 6: '午',
        7: '未', 8: '申', 9: '酉', 10: '戌', 11: '亥', 12: '子',
    }
    
    # 获取月支对应的月份索引（需要从sizhu中获取，如果没有则使用默认值）
    month_index = sizhu.get('month_index', 1)
    tianyi_zhi = tianyi_month_map.get(month_index, '')
    if tianyi_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == tianyi_zhi and (zhu_name, '天医') not in shensha_positions:
                shensha_list.append({
                    'name': '天医',
                    'position': zhu_name,
                    'zhi': tianyi_zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '天医'))
                break
    
    # 8. 天德（根据月支）
    # 寅月见丁，卯月见申，辰月见壬，巳月见辛，午月见亥，未月见甲
    # 申月见癸，酉月见寅，戌月见丙，亥月见乙，子月见庚，丑月见己
    tiande_month_map = {
        '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
        '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
        '戌': '丙', '亥': '乙', '子': '庚', '丑': '己',
    }
    
    tiande_gan = tiande_month_map.get(yue_zhi, '')
    if tiande_gan:
        for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
            gan = sizhu.get(zhu_name, {}).get('tian_gan', '')
            if gan == tiande_gan and (zhu_name, '天德') not in shensha_positions:
                shensha_list.append({
                    'name': '天德',
                    'position': zhu_name,
                    'gan': tiande_gan,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '天德'))
                break
    
    # 9. 月德（根据月支）
    # 寅月见丙，卯月见甲，辰月见壬，巳月见庚，午月见丙，未月见甲
    # 申月见壬，酉月见庚，戌月见丙，亥月见甲，子月见壬，丑月见庚
    yuede_month_map = {
        '寅': '丙', '卯': '甲', '辰': '壬', '巳': '庚',
        '午': '丙', '未': '甲', '申': '壬', '酉': '庚',
        '戌': '丙', '亥': '甲', '子': '壬', '丑': '庚',
    }
    
    yuede_gan = yuede_month_map.get(yue_zhi, '')
    if yuede_gan:
        for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
            gan = sizhu.get(zhu_name, {}).get('tian_gan', '')
            if gan == yuede_gan and (zhu_name, '月德') not in shensha_positions:
                shensha_list.append({
                    'name': '月德',
                    'position': zhu_name,
                    'gan': yuede_gan,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '月德'))
                break
    
    return {
        'shensha_list': shensha_list,
        'count': len(shensha_list),
    }

# ==================== 地支关系常量（用于流月分析） ====================

# 地支六合
DI_ZHI_LIU_HE = {
    '子': '丑', '丑': '子',
    '寅': '亥', '亥': '寅',
    '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰',
    '巳': '申', '申': '巳',
    '午': '未', '未': '午',
}

# 地支六冲
DI_ZHI_LIU_CHONG = {
    '子': '午', '午': '子',
    '丑': '未', '未': '丑',
    '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯',
    '辰': '戌', '戌': '辰',
    '巳': '亥', '亥': '巳',
}

# 地支三刑
DI_ZHI_SAN_XING = [
    {'寅', '巳', '申'},  # 寅巳申三刑
    {'丑', '戌', '未'},  # 丑戌未三刑
    {'子', '卯'},        # 子卯相刑
]

# 地支三合
DI_ZHI_SAN_HE = [
    {'申', '子', '辰'},  # 申子辰合水
    {'寅', '午', '戌'},  # 寅午戌合火
    {'巳', '酉', '丑'},  # 巳酉丑合金
    {'亥', '卯', '未'},  # 亥卯未合木
]

# 天干合化
TIAN_GAN_HE = {
    '甲': ('己', '土'), '己': ('甲', '土'),
    '乙': ('庚', '金'), '庚': ('乙', '金'),
    '丙': ('辛', '水'), '辛': ('丙', '水'),
    '丁': ('壬', '木'), '壬': ('丁', '木'),
    '戊': ('癸', '火'), '癸': ('戊', '火'),
}

# ==================== 流月计算函数 ====================

def get_single_shishen(rizhu_tiangan: str, target_gan: str = None, target_zhi: str = None) -> Dict[str, str]:
    """
    计算单个天干或地支与日主的十神关系
    
    Args:
        rizhu_tiangan: 日主天干
        target_gan: 目标天干（可选）
        target_zhi: 目标地支（可选）
    
    Returns:
        十神关系字典
    """
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_tiangan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_tiangan, '')
    
    result = {}
    
    # 计算天干十神
    if target_gan:
        target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
        target_yinyang = TIAN_GAN_YINYANG.get(target_gan, '')
        
        if target_wuxing == rizhu_wuxing:
            result['gan_shishen'] = '比肩' if target_yinyang == rizhu_yinyang else '劫财'
        elif WUXING_SHENG.get(rizhu_wuxing) == target_wuxing:
            result['gan_shishen'] = '食神' if target_yinyang == rizhu_yinyang else '伤官'
        elif WUXING_SHENG.get(target_wuxing) == rizhu_wuxing:
            result['gan_shishen'] = '偏印' if target_yinyang == rizhu_yinyang else '正印'
        elif WUXING_KE.get(rizhu_wuxing) == target_wuxing:
            result['gan_shishen'] = '偏财' if target_yinyang == rizhu_yinyang else '正财'
        elif WUXING_KE.get(target_wuxing) == rizhu_wuxing:
            result['gan_shishen'] = '七杀' if target_yinyang == rizhu_yinyang else '正官'
    
    # 计算地支十神（使用地支本气）
    if target_zhi and target_zhi in DI_ZHI_CANG_GAN:
        cang_gan = DI_ZHI_CANG_GAN[target_zhi][0]  # 本气
        cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
        cang_gan_yinyang = TIAN_GAN_YINYANG.get(cang_gan, '')
        
        if cang_gan_wuxing == rizhu_wuxing:
            result['zhi_shishen'] = '比肩' if cang_gan_yinyang == rizhu_yinyang else '劫财'
        elif WUXING_SHENG.get(rizhu_wuxing) == cang_gan_wuxing:
            result['zhi_shishen'] = '食神' if cang_gan_yinyang == rizhu_yinyang else '伤官'
        elif WUXING_SHENG.get(cang_gan_wuxing) == rizhu_wuxing:
            result['zhi_shishen'] = '偏印' if cang_gan_yinyang == rizhu_yinyang else '正印'
        elif WUXING_KE.get(rizhu_wuxing) == cang_gan_wuxing:
            result['zhi_shishen'] = '偏财' if cang_gan_yinyang == rizhu_yinyang else '正财'
        elif WUXING_KE.get(cang_gan_wuxing) == rizhu_wuxing:
            result['zhi_shishen'] = '七杀' if cang_gan_yinyang == rizhu_yinyang else '正官'
    
    return result

def analyze_zhi_relation(zhi1: str, zhi2: str) -> Dict[str, Any]:
    """
    分析两个地支之间的关系
    
    Args:
        zhi1: 第一个地支
        zhi2: 第二个地支
    
    Returns:
        关系字典
    """
    relations = []
    
    # 六合
    if DI_ZHI_LIU_HE.get(zhi1) == zhi2:
        relations.append({'type': '六合', 'desc': f'{zhi1}{zhi2}合'})
    
    # 六冲
    if DI_ZHI_LIU_CHONG.get(zhi1) == zhi2:
        relations.append({'type': '六冲', 'desc': f'{zhi1}{zhi2}冲'})
    
    # 检查三刑
    for xing_set in DI_ZHI_SAN_XING:
        if zhi1 in xing_set and zhi2 in xing_set:
            relations.append({'type': '相刑', 'desc': f'{zhi1}{zhi2}相刑'})
            break
    
    return {'relations': relations, 'has_he': any(r['type'] == '六合' for r in relations), 
            'has_chong': any(r['type'] == '六冲' for r in relations)}

def analyze_gan_relation(gan1: str, gan2: str) -> Dict[str, Any]:
    """
    分析两个天干之间的关系
    
    Args:
        gan1: 第一个天干
        gan2: 第二个天干
    
    Returns:
        关系字典
    """
    relations = []
    
    # 天干合化
    if TIAN_GAN_HE.get(gan1, (None, None))[0] == gan2:
        hua_wuxing = TIAN_GAN_HE[gan1][1]
        relations.append({'type': '天干合', 'desc': f'{gan1}{gan2}合化{hua_wuxing}'})
    
    # 天干相克
    wuxing1 = TIAN_GAN_WUXING.get(gan1, '')
    wuxing2 = TIAN_GAN_WUXING.get(gan2, '')
    if wuxing1 and wuxing2:
        if WUXING_KE.get(wuxing1) == wuxing2:
            relations.append({'type': '天干克', 'desc': f'{gan1}克{gan2}'})
    
    return {'relations': relations}

def calculate_wuxing_xi_ji(sizhu: Dict[str, Any], wuxing_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    计算五行喜忌（基于日主强弱和五行分布）
    
    Args:
        sizhu: 四柱数据
        wuxing_analysis: 五行分析结果（可选）
    
    Returns:
        五行喜忌字典
    """
    rizhu_gan = sizhu.get('ri_zhu_tiangan', '')
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
    
    # 获取五行分布
    if wuxing_analysis:
        wuxing_count = wuxing_analysis.get('wuxing_count_detail', {})
    else:
        wuxing_count = calculate_wuxing(sizhu).get('wuxing_count_detail', {})
    
    # 简化判断：根据日主五行和五行分布判断喜忌
    # 日主五行统计
    rizhu_count = wuxing_count.get(rizhu_wuxing, 0)
    
    # 生我（印星）的五行
    sheng_wo_wuxing = None
    for wuxing, sheng in WUXING_SHENG.items():
        if sheng == rizhu_wuxing:
            sheng_wo_wuxing = wuxing
            break
    
    # 我生（食伤）的五行
    wo_sheng_wuxing = WUXING_SHENG.get(rizhu_wuxing, '')
    
    # 克我（官杀）的五行
    ke_wo_wuxing = WUXING_KE.get(rizhu_wuxing, '')
    
    # 我克（财星）的五行
    wo_ke_wuxing = None
    for wuxing, ke in WUXING_KE.items():
        if ke == rizhu_wuxing:
            wo_ke_wuxing = wuxing
            break
    
    # 简化规则：日主弱喜印比，日主强喜食财官
    # 判断日主强弱（简化：同五行+生我五行 > 3 为强）
    same_wuxing_count = rizhu_count
    if sheng_wo_wuxing:
        same_wuxing_count += wuxing_count.get(sheng_wo_wuxing, 0)
    
    is_rizhu_qiang = same_wuxing_count > 3
    
    xi_wuxing = []  # 喜用五行
    ji_wuxing = []  # 忌讳五行
    
    if is_rizhu_qiang:
        # 日主强：喜泄耗克（食伤、财、官杀）
        if wo_sheng_wuxing:
            xi_wuxing.append(wo_sheng_wuxing)
        if wo_ke_wuxing:
            xi_wuxing.append(wo_ke_wuxing)
        if ke_wo_wuxing:
            xi_wuxing.append(ke_wo_wuxing)
        # 忌生扶
        if sheng_wo_wuxing:
            ji_wuxing.append(sheng_wo_wuxing)
        ji_wuxing.append(rizhu_wuxing)
    else:
        # 日主弱：喜生扶（印、比劫）
        if sheng_wo_wuxing:
            xi_wuxing.append(sheng_wo_wuxing)
        xi_wuxing.append(rizhu_wuxing)
        # 忌泄耗克
        if wo_sheng_wuxing:
            ji_wuxing.append(wo_sheng_wuxing)
        if wo_ke_wuxing:
            ji_wuxing.append(wo_ke_wuxing)
        if ke_wo_wuxing:
            ji_wuxing.append(ke_wo_wuxing)
    
    return {
        'rizhu_wuxing': rizhu_wuxing,
        'is_rizhu_qiang': is_rizhu_qiang,
        'xi_wuxing': list(set(xi_wuxing)),
        'ji_wuxing': list(set(ji_wuxing)),
        'sheng_wo_wuxing': sheng_wo_wuxing,
        'wo_sheng_wuxing': wo_sheng_wuxing,
        'ke_wo_wuxing': ke_wo_wuxing,
        'wo_ke_wuxing': wo_ke_wuxing,
    }

def evaluate_auspicious(
    liuyue_data: Dict[str, Any],
    sizhu: Dict[str, Any],
    wuxing_xi_ji: Dict[str, Any],
    dayun_data: Dict[str, Any] = None,
    liunian_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    评估流月吉凶
    
    Args:
        liuyue_data: 流月数据
        sizhu: 四柱数据
        wuxing_xi_ji: 五行喜忌
        dayun_data: 当前大运数据（可选）
        liunian_data: 流年数据（可选）
    
    Returns:
        吉凶评估结果
    """
    liuyue_gan = liuyue_data['gan']
    liuyue_zhi = liuyue_data['zhi']
    liuyue_gan_wuxing = TIAN_GAN_WUXING.get(liuyue_gan, '')
    liuyue_zhi_wuxing = DI_ZHI_WUXING.get(liuyue_zhi, '')
    
    xi_wuxing = wuxing_xi_ji.get('xi_wuxing', [])
    ji_wuxing = wuxing_xi_ji.get('ji_wuxing', [])
    
    score = 50  # 基础分50
    factors = []
    
    # 1. 流月天干五行喜忌
    if liuyue_gan_wuxing in xi_wuxing:
        score += 15
        factors.append({'factor': '天干五行', 'impact': '吉', 'desc': f'流月天干{liuyue_gan}属{liuyue_gan_wuxing}，为喜用五行'})
    elif liuyue_gan_wuxing in ji_wuxing:
        score -= 10
        factors.append({'factor': '天干五行', 'impact': '凶', 'desc': f'流月天干{liuyue_gan}属{liuyue_gan_wuxing}，为忌讳五行'})
    
    # 2. 流月地支五行喜忌
    if liuyue_zhi_wuxing in xi_wuxing:
        score += 10
        factors.append({'factor': '地支五行', 'impact': '吉', 'desc': f'流月地支{liuyue_zhi}属{liuyue_zhi_wuxing}，为喜用五行'})
    elif liuyue_zhi_wuxing in ji_wuxing:
        score -= 8
        factors.append({'factor': '地支五行', 'impact': '凶', 'desc': f'流月地支{liuyue_zhi}属{liuyue_zhi_wuxing}，为忌讳五行'})
    
    # 3. 与原局地支的关系
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi = sizhu.get(zhu_name, {}).get('di_zhi', '')
        if zhi:
            relation = analyze_zhi_relation(liuyue_zhi, zhi)
            if relation['has_he']:
                score += 8
                factors.append({'factor': f'与{zhu_name}地支', 'impact': '吉', 'desc': f'流月{liuyue_zhi}与{zhu_name}{zhi}相合'})
            if relation['has_chong']:
                score -= 10
                factors.append({'factor': f'与{zhu_name}地支', 'impact': '凶', 'desc': f'流月{liuyue_zhi}与{zhu_name}{zhi}相冲'})
    
    # 4. 与大运的关系
    if dayun_data:
        dayun_gan = dayun_data.get('gan', '')
        dayun_zhi = dayun_data.get('zhi', '')
        
        # 天干关系
        if dayun_gan:
            gan_rel = analyze_gan_relation(liuyue_gan, dayun_gan)
            for rel in gan_rel['relations']:
                if rel['type'] == '天干合':
                    score += 5
                    factors.append({'factor': '与大运天干', 'impact': '吉', 'desc': rel['desc']})
        
        # 地支关系
        if dayun_zhi:
            zhi_rel = analyze_zhi_relation(liuyue_zhi, dayun_zhi)
            if zhi_rel['has_he']:
                score += 8
                factors.append({'factor': '与大运地支', 'impact': '吉', 'desc': f'流月{liuyue_zhi}与大运{dayun_zhi}相合'})
            if zhi_rel['has_chong']:
                score -= 10
                factors.append({'factor': '与大运地支', 'impact': '凶', 'desc': f'流月{liuyue_zhi}与大运{dayun_zhi}相冲'})
    
    # 5. 与流年的关系
    if liunian_data:
        liunian_gan = liunian_data.get('gan', '')
        liunian_zhi = liunian_data.get('zhi', '')
        
        # 天干关系
        if liunian_gan:
            gan_rel = analyze_gan_relation(liuyue_gan, liunian_gan)
            for rel in gan_rel['relations']:
                if rel['type'] == '天干合':
                    score += 5
                    factors.append({'factor': '与流年天干', 'impact': '吉', 'desc': rel['desc']})
        
        # 地支关系
        if liunian_zhi:
            zhi_rel = analyze_zhi_relation(liuyue_zhi, liunian_zhi)
            if zhi_rel['has_he']:
                score += 8
                factors.append({'factor': '与流年地支', 'impact': '吉', 'desc': f'流月{liuyue_zhi}与流年{liunian_zhi}相合'})
            if zhi_rel['has_chong']:
                score -= 10
                factors.append({'factor': '与流年地支', 'impact': '凶', 'desc': f'流月{liuyue_zhi}与流年{liunian_zhi}相冲'})
    
    # 确定吉凶等级
    if score >= 75:
        level = '大吉'
    elif score >= 60:
        level = '中吉'
    elif score >= 45:
        level = '平'
    elif score >= 30:
        level = '中凶'
    else:
        level = '大凶'
    
    # 生成建议
    suggestions = []
    good_factors = [f for f in factors if f['impact'] == '吉']
    bad_factors = [f for f in factors if f['impact'] == '凶']
    
    if good_factors:
        suggestions.append(f"有利因素：{'；'.join([f['desc'] for f in good_factors[:3]])}")
    if bad_factors:
        suggestions.append(f"注意事项：{'；'.join([f['desc'] for f in bad_factors[:3]])}")
    
    return {
        'score': max(0, min(100, score)),
        'level': level,
        'factors': factors,
        'suggestions': suggestions,
    }

def calculate_liuyue(
    liunian_gan: str,
    month: int,
    rizhu_tiangan: str,
    sizhu: Dict[str, Any] = None,
    wuxing_xi_ji: Dict[str, Any] = None,
    dayun_data: Dict[str, Any] = None,
    liunian_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    计算单个月份的流月信息
    
    Args:
        liunian_gan: 流年天干
        month: 月份(1-12)
        rizhu_tiangan: 日主天干
        sizhu: 四柱数据（用于吉凶评估）
        wuxing_xi_ji: 五行喜忌分析结果
        dayun_data: 当前大运数据（可选）
        liunian_data: 流年数据（可选）
    
    Returns:
        流月信息字典
    """
    # 流月地支（固定）
    liuyue_zhi = MONTH_TO_DI_ZHI.get(month, '寅')
    
    # 流月天干（根据流年天干查表）
    liuyue_gan = YUE_GAN_TABLE.get(liunian_gan, {}).get(month, '丙')
    
    # 流月干支
    gan_zhi = f"{liuyue_gan}{liuyue_zhi}"
    
    # 五行属性
    gan_wuxing = TIAN_GAN_WUXING.get(liuyue_gan, '')
    zhi_wuxing = DI_ZHI_WUXING.get(liuyue_zhi, '')
    
    # 与日主的十神关系
    shishen_result = get_single_shishen(rizhu_tiangan, liuyue_gan, liuyue_zhi)
    
    result = {
        'month': month,
        'gan': liuyue_gan,
        'zhi': liuyue_zhi,
        'gan_zhi': gan_zhi,
        'wuxing': {
            'gan': gan_wuxing,
            'zhi': zhi_wuxing,
        },
        'shishen_to_rizhu': shishen_result,
    }
    
    # 吉凶评估
    if sizhu and wuxing_xi_ji:
        auspicious_result = evaluate_auspicious(
            result, sizhu, wuxing_xi_ji, dayun_data, liunian_data
        )
        result['auspicious'] = auspicious_result
    
    return result

def calculate_liuyue_list(
    sizhu: Dict[str, Any],
    start_year: int,
    start_month: int,
    months_count: int,
    birth_year: int = None,
    gender: str = '男',
    wuxing_analysis: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    计算未来N个月的流月列表
    
    Args:
        sizhu: 四柱数据
        start_year: 起始年份
        start_month: 起始月份(1-12)
        months_count: 推演月数
        birth_year: 出生年份（用于确定当前大运）
        gender: 性别
        wuxing_analysis: 五行分析结果
    
    Returns:
        流月列表数据
    """
    rizhu_tiangan = sizhu.get('ri_zhu_tiangan', '')
    
    # 计算五行喜忌
    wuxing_xi_ji = calculate_wuxing_xi_ji(sizhu, wuxing_analysis)
    
    # 获取当前大运
    current_dayun = None
    if birth_year:
        from datetime import datetime
        current_year = datetime.now().year
        current_age = current_year - birth_year
        
        dayun_list = calculate_dayun(birth_year, 1, 1, 12, gender, sizhu.get('bazi_year'))
        for dayun in dayun_list:
            if dayun['start_age'] <= current_age <= dayun['end_age']:
                current_dayun = dayun
                break
    
    liuyue_list = []
    current_year = start_year
    current_month = start_month
    
    for i in range(months_count):
        # 计算流年
        liunian_gan = get_tian_gan(current_year)
        liunian_zhi = get_di_zhi(current_year)
        liunian_data = {
            'year': current_year,
            'gan': liunian_gan,
            'zhi': liunian_zhi,
        }
        
        # 计算流月
        liuyue = calculate_liuyue(
            liunian_gan=liunian_gan,
            month=current_month,
            rizhu_tiangan=rizhu_tiangan,
            sizhu=sizhu,
            wuxing_xi_ji=wuxing_xi_ji,
            dayun_data=current_dayun,
            liunian_data=liunian_data,
        )
        liuyue['year'] = current_year
        liuyue_list.append(liuyue)
        
        # 递增月份
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    
    return {
        'success': True,
        'start_year': start_year,
        'start_month': start_month,
        'months_count': months_count,
        'wuxing_xi_ji': wuxing_xi_ji,
        'current_dayun': current_dayun,
        'liuyue_list': liuyue_list,
    }

