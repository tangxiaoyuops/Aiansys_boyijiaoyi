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

# ==================== 纳音常量 ====================
# 六十甲子纳音（根据年柱或日柱干支组合）
NAYIN_TABLE = {
    '甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火',
    '戊辰': '大林木', '己巳': '大林木', '庚午': '路旁土', '辛未': '路旁土',
    '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
    '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土',
    '庚辰': '白蜡金', '辛巳': '白蜡金', '壬午': '杨柳木', '癸未': '杨柳木',
    '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
    '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木',
    '壬辰': '长流水', '癸巳': '长流水', '甲午': '沙中金', '乙未': '沙中金',
    '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
    '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金',
    '甲辰': '覆灯火', '乙巳': '覆灯火', '丙午': '天河水', '丁未': '天河水',
    '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
    '壬子': '桑柘木', '癸丑': '桑柘木', '甲寅': '大溪水', '乙卯': '大溪水',
    '丙辰': '沙中土', '丁巳': '沙中土', '戊午': '天上火', '己未': '天上火',
    '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水',
}

# 纳音五行属性
NAYIN_WUXING = {
    '海中金': '金', '炉中火': '火', '大林木': '木', '路旁土': '土',
    '剑锋金': '金', '山头火': '火', '涧下水': '水', '城头土': '土',
    '白蜡金': '金', '杨柳木': '木', '泉中水': '水', '屋上土': '土',
    '霹雳火': '火', '松柏木': '木', '长流水': '水', '沙中金': '金',
    '山下火': '火', '平地木': '木', '壁上土': '土', '金箔金': '金',
    '覆灯火': '火', '天河水': '水', '大驿土': '土', '钗钏金': '金',
    '桑柘木': '木', '大溪水': '水', '沙中土': '土', '天上火': '火',
    '石榴木': '木', '大海水': '水',
}

# 纳音详细说明
NAYIN_DESCRIPTION = {
    '海中金': '深藏不露，珍贵难得，性格深沉内敛',
    '炉中火': '热情奔放，活力充沛，有领导才能',
    '大林木': '仁慈宽厚，志向远大，有包容心',
    '路旁土': '踏实稳重，勤劳肯干，服务他人',
    '剑锋金': '锋芒毕露，刚正不阿，有决断力',
    '山头火': '外刚内柔，热情明朗，有感染力',
    '涧下水': '清澈透明，灵活变通，有智慧',
    '城头土': '固守原则，忠诚可靠，有责任心',
    '白蜡金': '温润细腻，珍贵典雅，有品位',
    '杨柳木': '柔韧灵活，适应力强，善解人意',
    '泉中水': '清冽甘甜，源源不断，有内涵',
    '屋上土': '稳重可靠，遮风挡雨，有担当',
    '霹雳火': '雷厉风行，魄力十足，有爆发力',
    '松柏木': '坚毅刚强，四季常青，有骨气',
    '长流水': '绵延不断，持之以恒，有耐心',
    '沙中金': '珍贵隐藏，需要发掘，有潜力',
    '山下火': '温和内敛，光明磊落，有修养',
    '平地木': '根基扎实，茁壮成长，有作为',
    '壁上土': '依附有力，守护一方，有依靠',
    '金箔金': '华美装饰，光彩夺目，有魅力',
    '覆灯火': '照亮他人，温暖人心，有爱心',
    '天河水': '高远清澈，滋润万物，有大爱',
    '大驿土': '通达四方，承载万物，有胸怀',
    '钗钏金': '精致华美，珠光宝气，有气质',
    '桑柘木': '坚韧挺拔，耐力持久，有韧劲',
    '大溪水': '奔流不息，气势磅礴，有魄力',
    '沙中土': '细软包容，温和沉稳，有度量',
    '天上火': '光明正大，普照万物，有大格局',
    '石榴木': '花果俱美，多子多福，有福气',
    '大海水': '浩瀚无边，包罗万象，有大智慧',
}

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
        'nian_zhu': {
            'tian_gan': nian_gan, 
            'di_zhi': nian_zhi,
            'cang_gan': DI_ZHI_CANG_GAN.get(nian_zhi, []),  # 藏干列表
        },
        'yue_zhu': {
            'tian_gan': yue_gan, 
            'di_zhi': yue_zhi,
            'cang_gan': DI_ZHI_CANG_GAN.get(yue_zhi, []),  # 藏干列表
        },
        'ri_zhu': {
            'tian_gan': ri_gan, 
            'di_zhi': ri_zhi,
            'cang_gan': DI_ZHI_CANG_GAN.get(ri_zhi, []),  # 藏干列表
        },
        'shi_zhu': {
            'tian_gan': shi_gan, 
            'di_zhi': shi_zhi,
            'cang_gan': DI_ZHI_CANG_GAN.get(shi_zhi, []),  # 藏干列表
        },
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
    
    # 10. 太极贵人
    # 甲乙生人子午全，丙丁生人卯酉全，戊己生人辰戌丑未全
    # 庚辛生人寅亥全，壬癸生人巳申全
    taiji_map = {
        '甲': ['子', '午'], '乙': ['子', '午'],
        '丙': ['卯', '酉'], '丁': ['卯', '酉'],
        '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
        '庚': ['寅', '亥'], '辛': ['寅', '亥'],
        '壬': ['巳', '申'], '癸': ['巳', '申'],
    }
    
    taiji_zhi_list = taiji_map.get(rizhu_gan, [])
    if taiji_zhi_list:
        found_zhi = []
        for zhu_name, zhi in all_zhi:
            if zhi in taiji_zhi_list and zhi not in found_zhi:
                found_zhi.append(zhi)
        # 需要至少满足两个地支才算太极贵人
        if len(found_zhi) >= 2:
            shensha_list.append({
                'name': '太极贵人',
                'position': '全局',
                'zhi': '、'.join(found_zhi),
                'type': '吉',
            })
    
    # 11. 将星
    # 子见子，丑见酉，寅见午，卯见卯，辰见子，巳见酉
    # 午见午，未见卯，申见子，酉见酉，戌见午，亥见卯
    jiangxing_map = {
        '子': '子', '丑': '酉', '寅': '午', '卯': '卯',
        '辰': '子', '巳': '酉', '午': '午', '未': '卯',
        '申': '子', '酉': '酉', '戌': '午', '亥': '卯',
    }
    
    nian_zhi = sizhu.get('nian_zhu', {}).get('di_zhi', '')
    jiangxing_zhi = jiangxing_map.get(nian_zhi, '')
    if jiangxing_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == jiangxing_zhi and (zhu_name, '将星') not in shensha_positions:
                shensha_list.append({
                    'name': '将星',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '中性',
                })
                shensha_positions.add((zhu_name, '将星'))
                break
    
    # 12. 羊刃（根据日主查）
    # 甲见卯，乙见寅，丙见午，丁见巳，戊见午，己见巳，庚见酉，辛见申，壬见子，癸见亥
    yangren_map = {
        '甲': '卯', '乙': '寅', '丙': '午', '丁': '巳',
        '戊': '午', '己': '巳', '庚': '酉', '辛': '申',
        '壬': '子', '癸': '亥',
    }
    
    yangren_zhi = yangren_map.get(rizhu_gan, '')
    if yangren_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == yangren_zhi and (zhu_name, '羊刃') not in shensha_positions:
                shensha_list.append({
                    'name': '羊刃',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '凶',
                })
                shensha_positions.add((zhu_name, '羊刃'))
                break
    
    # 13. 禄神（根据日主查）
    # 甲禄在寅，乙禄在卯，丙禄在巳，丁禄在午，戊禄在巳
    # 己禄在午，庚禄在申，辛禄在酉，壬禄在亥，癸禄在子
    lushen_map = {
        '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
        '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
        '壬': '亥', '癸': '子',
    }
    
    lushen_zhi = lushen_map.get(rizhu_gan, '')
    if lushen_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == lushen_zhi and (zhu_name, '禄神') not in shensha_positions:
                shensha_list.append({
                    'name': '禄神',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '禄神'))
                break
    
    # 14. 孤辰寡宿
    # 亥子丑年生人见寅为孤辰，见戌为寡宿
    # 寅卯辰年生人见巳为孤辰，见丑为寡宿
    # 巳午未年生人见申为孤辰，见辰为寡宿
    # 申酉戌年生人见亥为孤辰，见未为寡宿
    guchen_map = {
        '亥': ('寅', '戌'), '子': ('寅', '戌'), '丑': ('寅', '戌'),
        '寅': ('巳', '丑'), '卯': ('巳', '丑'), '辰': ('巳', '丑'),
        '巳': ('申', '辰'), '午': ('申', '辰'), '未': ('申', '辰'),
        '申': ('亥', '未'), '酉': ('亥', '未'), '戌': ('亥', '未'),
    }
    
    guchen_info = guchen_map.get(nian_zhi, ('', ''))
    if guchen_info[0]:
        for zhu_name, zhi in all_zhi:
            if zhi == guchen_info[0] and (zhu_name, '孤辰') not in shensha_positions:
                shensha_list.append({
                    'name': '孤辰',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '凶',
                })
                shensha_positions.add((zhu_name, '孤辰'))
                break
    if guchen_info[1]:
        for zhu_name, zhi in all_zhi:
            if zhi == guchen_info[1] and (zhu_name, '寡宿') not in shensha_positions:
                shensha_list.append({
                    'name': '寡宿',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '凶',
                })
                shensha_positions.add((zhu_name, '寡宿'))
                break
    
    # 15. 红鸾（根据年支查）
    # 子见卯，丑见寅，寅见丑，卯见子，辰见亥，巳见戌
    # 午见酉，未见申，申见未，酉见午，戌见巳，亥见辰
    hongluan_map = {
        '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
        '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
        '申': '未', '酉': '午', '戌': '巳', '亥': '辰',
    }
    
    hongluan_zhi = hongluan_map.get(nian_zhi, '')
    if hongluan_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == hongluan_zhi and (zhu_name, '红鸾') not in shensha_positions:
                shensha_list.append({
                    'name': '红鸾',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '红鸾'))
                break
    
    # 16. 天喜（与红鸾对冲）
    tianxi_map = {
        '子': '酉', '丑': '申', '寅': '未', '卯': '午',
        '辰': '巳', '巳': '辰', '午': '卯', '未': '寅',
        '申': '丑', '酉': '子', '戌': '亥', '亥': '戌',
    }
    
    tianxi_zhi = tianxi_map.get(nian_zhi, '')
    if tianxi_zhi:
        for zhu_name, zhi in all_zhi:
            if zhi == tianxi_zhi and (zhu_name, '天喜') not in shensha_positions:
                shensha_list.append({
                    'name': '天喜',
                    'position': zhu_name,
                    'zhi': zhi,
                    'type': '吉',
                })
                shensha_positions.add((zhu_name, '天喜'))
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

# ==================== 纳音、空亡、命宫、胎元计算 ====================

def calculate_nayin(gan: str, zhi: str) -> Dict[str, str]:
    """
    计算纳音
    
    Args:
        gan: 天干
        zhi: 地支
    
    Returns:
        纳音信息字典
    """
    gan_zhi = f"{gan}{zhi}"
    nayin_name = NAYIN_TABLE.get(gan_zhi, '')
    nayin_wuxing = NAYIN_WUXING.get(nayin_name, '')
    nayin_desc = NAYIN_DESCRIPTION.get(nayin_name, '')
    
    return {
        'name': nayin_name,
        'wuxing': nayin_wuxing,
        'description': nayin_desc,
        'gan_zhi': gan_zhi,
    }

def calculate_xun_kong(gan: str, zhi: str) -> Dict[str, Any]:
    """
    计算旬空（空亡）
    
    六十甲子分为六旬，每旬十个组合，有两个地支落空
    甲子旬：甲子、乙丑、丙寅、丁卯、戊辰、己巳、庚午、辛未、壬申、癸酉，空亡：戌、亥
    甲戌旬：甲戌、乙亥、丙子、丁丑、戊寅、己卯、庚辰、辛巳、壬午、癸未，空亡：申、酉
    甲申旬：甲申、乙酉、丙戌、丁亥、戊子、己丑、庚寅、辛卯、壬辰、癸巳，空亡：午、未
    甲午旬：甲午、乙未、丙申、丁酉、戊戌、己亥、庚子、辛丑、壬寅、癸卯，空亡：辰、巳
    甲辰旬：甲辰、乙巳、丙午、丁未、戊申、己酉、庚戌、辛亥、壬子、癸丑，空亡：寅、卯
    甲寅旬：甲寅、乙卯、丙辰、丁巳、戊午、己未、庚申、辛酉、壬戌、癸亥，空亡：子、丑
    
    Args:
        gan: 天干
        zhi: 地支
    
    Returns:
        空亡信息字典
    """
    gan_index = TIAN_GAN.index(gan)
    zhi_index = DI_ZHI.index(zhi)
    
    # 根据天干确定旬首
    # 甲（0）开头的旬：甲子、甲戌、甲申、甲午、甲辰、甲寅
    # 每旬的地支从旬首地支开始
    
    # 六旬及其空亡
    xun_kong_map = [
        {'xun_shou': '甲子', 'kong': ['戌', '亥']},  # 甲子旬
        {'xun_shou': '甲戌', 'kong': ['申', '酉']},  # 甲戌旬
        {'xun_shou': '甲申', 'kong': ['午', '未']},  # 甲申旬
        {'xun_shou': '甲午', 'kong': ['辰', '巳']},  # 甲午旬
        {'xun_shou': '甲辰', 'kong': ['寅', '卯']},  # 甲辰旬
        {'xun_shou': '甲寅', 'kong': ['子', '丑']},  # 甲寅旬
    ]
    
    # 计算当前干支属于哪一旬
    # 甲子旬的干支组合：干支索引差为0或干支在同一位
    # 简化计算：根据天干和地支的关系确定旬
    
    # 方法：找到与该天干配对的旬首地支
    # 甲(0)配子(0)为甲子旬，甲配戌(10)为甲戌旬...
    # 每旬以甲开头，甲配的地支决定属于哪旬
    
    # 计算旬序号
    # 甲子旬：天干索引-地支索引 = 0 或 -12 (即差值为0)
    # 实际上：(天干索引 - 地支索引) mod 12 可以确定旬
    
    diff = (zhi_index - gan_index) % 12
    
    # 根据差值确定空亡
    if diff <= 1:  # 子、丑
        xun_index = 0 if diff == 0 else 5
    elif diff <= 3:  # 寅、卯
        xun_index = 4 if diff == 2 else 4
    elif diff <= 5:  # 辰、巳
        xun_index = 3 if diff == 4 else 3
    elif diff <= 7:  # 午、未
        xun_index = 2 if diff == 6 else 2
    elif diff <= 9:  # 申、酉
        xun_index = 1 if diff == 8 else 1
    else:  # 戌、亥
        xun_index = 0 if diff == 10 else 0
    
    # 更精确的计算方法
    # 六十甲子表中，甲子旬从第1位开始，甲戌旬从第11位开始...
    # 我们需要确定当前干支在哪一旬
    
    # 甲子旬包含：甲子、乙丑、丙寅、丁卯、戊辰、己巳、庚午、辛未、壬申、癸酉
    # 特点：地支从子开始，顺序排列，到酉结束（共10个，空戌亥）
    
    # 简化：根据地支在十二支中的位置和天干的关系
    # 如果 天干和地支的组合在地支序列中"够不到"的位置就是空亡
    
    # 更直接的方法：
    # 对于甲子旬（甲=0）：地支 0-9 有效，10、11（戌、亥）空亡
    # 对于甲戌旬（甲=0，戌=10）：地支 10-9（循环），实际是10-11,0-7，空 8、9（申、酉）
    
    # 重新计算：从甲开始，找出当前旬
    # 甲的索引为0，旬首地支决定了旬
    
    # 当前干支的序号（0-59）
    gan_zhi_index = (gan_index * 6 + zhi_index) % 60 if zhi_index >= gan_index else (zhi_index - gan_index + 60) % 60
    
    # 实际更简单的方法：
    # 六旬按顺序：甲子旬（0-9）、甲戌旬（10-19）、甲申旬（20-29）、甲午旬（30-39）、甲辰旬（40-49）、甲寅旬（50-59）
    
    # 直接根据天干地支组合判断
    # 如果甲(0)配子(0)→甲子旬，甲(0)配戌(10)→甲戌旬...
    
    # 简化计算
    xun_info = None
    for xun_data in xun_kong_map:
        xun_shou_gan = xun_data['xun_shou'][0]
        xun_shou_zhi = xun_data['xun_shou'][1]
        xun_shou_gan_idx = TIAN_GAN.index(xun_shou_gan)
        xun_shou_zhi_idx = DI_ZHI.index(xun_shou_zhi)
        
        # 检查当前干支是否在此旬中
        # 一旬包含10个干支组合，从旬首开始
        # 天干顺序循环，地支也顺序循环
        
        # 当前干支与旬首的偏移
        gan_offset = (gan_index - xun_shou_gan_idx) % 10
        expected_zhi_idx = (xun_shou_zhi_idx + gan_offset) % 12
        
        if zhi_index == expected_zhi_idx:
            xun_info = xun_data
            break
    
    if xun_info is None:
        # 备用计算
        xun_info = xun_kong_map[0]
    
    return {
        'kong_wang': xun_info['kong'],
        'xun_shou': xun_info['xun_shou'],
        'gan_zhi': f"{gan}{zhi}",
    }

def calculate_minggong(month_zhi: str, hour_zhi: str) -> Dict[str, str]:
    """
    计算命宫
    
    命宫计算方法：
    以月支为起点，逆数到时支，再从子位顺数回到原位，即为命宫
    
    简化公式：命宫地支 = (月支索引 + 时支索引) % 12，然后找对应的天干
    
    Args:
        month_zhi: 月支
        hour_zhi: 时支
    
    Returns:
        命宫信息字典
    """
    month_idx = DI_ZHI.index(month_zhi)
    hour_idx = DI_ZHI.index(hour_zhi)
    
    # 命宫地支计算
    # 方法：从子上起正月，逆数到生月，再从生月起生时，顺数到卯，卯所在地支为命宫
    # 简化：命宫地支 = (14 - month_idx - hour_idx) % 12
    # 或：命宫地支 = (2 - month_idx - hour_idx) % 12（从卯位开始）
    
    # 传统方法：
    # 1. 从子位起正月，逆数到生月（如三月生，子-寅月，丑-卯月，寅-辰月...）
    # 2. 从生月位起子时，顺数到生时，所落宫位为命宫
    
    # 简化公式
    minggong_zhi_idx = (14 - month_idx - hour_idx) % 12
    minggong_zhi = DI_ZHI[minggong_zhi_idx]
    
    # 命宫天干（需要根据年干或五虎遁推算）
    # 使用五虎遁：甲己年起丙寅，乙庚年起戊寅，丙辛年起庚寅，丁壬年起壬寅，戊癸年起甲寅
    # 这里简化处理，假设命宫天干根据命宫地支推算
    # 实际应该结合年干
    
    # 暂时用简化方法：命宫天干根据命宫地支序号
    minggong_gan_idx = (minggong_zhi_idx + 2) % 10  # 简化
    minggong_gan = TIAN_GAN[minggong_gan_idx]
    
    return {
        'gan': minggong_gan,
        'zhi': minggong_zhi,
        'gan_zhi': f"{minggong_gan}{minggong_zhi}",
    }

def calculate_taiyuan(month_zhi: str, day_gan: str) -> Dict[str, str]:
    """
    计算胎元
    
    胎元计算方法：
    胎元天干 = 月干后一位
    胎元地支 = 月支后三位
    
    Args:
        month_zhi: 月支
        day_gan: 日干（用于更精确计算）
    
    Returns:
        胎元信息字典
    """
    month_zhi_idx = DI_ZHI.index(month_zhi)
    
    # 胎元地支：月支后三位
    taiyuan_zhi_idx = (month_zhi_idx + 3) % 12
    taiyuan_zhi = DI_ZHI[taiyuan_zhi_idx]
    
    # 胎元天干：需要根据月干推算
    # 简化：使用日干推算
    day_gan_idx = TIAN_GAN.index(day_gan)
    taiyuan_gan_idx = (day_gan_idx + 1) % 10
    taiyuan_gan = TIAN_GAN[taiyuan_gan_idx]
    
    return {
        'gan': taiyuan_gan,
        'zhi': taiyuan_zhi,
        'gan_zhi': f"{taiyuan_gan}{taiyuan_zhi}",
    }

def calculate_shen_gong(month_zhi: str, hour_zhi: str) -> Dict[str, str]:
    """
    计算身宫
    
    身宫计算方法：
    以月支为起点，顺数到时支，再从子位逆数回到原位，即为身宫
    
    Args:
        month_zhi: 月支
        hour_zhi: 时支
    
    Returns:
        身宫信息字典
    """
    month_idx = DI_ZHI.index(month_zhi)
    hour_idx = DI_ZHI.index(hour_zhi)
    
    # 身宫地支计算
    # 简化公式
    shengong_zhi_idx = (month_idx + hour_idx + 2) % 12
    shengong_zhi = DI_ZHI[shengong_zhi_idx]
    
    # 身宫天干
    shengong_gan_idx = (shengong_zhi_idx + 2) % 10
    shengong_gan = TIAN_GAN[shengong_gan_idx]
    
    return {
        'gan': shengong_gan,
        'zhi': shengong_zhi,
        'gan_zhi': f"{shengong_gan}{shengong_zhi}",
    }

def calculate_extended_info(sizhu: Dict[str, Any], birth_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    计算扩展信息（纳音、空亡、命宫、胎元、身宫等）
    
    Args:
        sizhu: 四柱数据
        birth_info: 出生信息（可选）
    
    Returns:
        扩展信息字典
    """
    result = {}
    
    # 1. 各柱纳音
    result['nayin'] = {}
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        zhi = zhu.get('di_zhi', '')
        if gan and zhi:
            result['nayin'][zhu_name] = calculate_nayin(gan, zhi)
    
    # 2. 日柱空亡（以日柱为准）
    ri_gan = sizhu.get('ri_zhu', {}).get('tian_gan', '')
    ri_zhi = sizhu.get('ri_zhu', {}).get('di_zhi', '')
    if ri_gan and ri_zhi:
        result['xun_kong'] = calculate_xun_kong(ri_gan, ri_zhi)
    
    # 3. 年柱空亡（以年柱为准，部分流派使用）
    nian_gan = sizhu.get('nian_zhu', {}).get('tian_gan', '')
    nian_zhi = sizhu.get('nian_zhu', {}).get('di_zhi', '')
    if nian_gan and nian_zhi:
        result['nian_xun_kong'] = calculate_xun_kong(nian_gan, nian_zhi)
    
    # 4. 命宫
    yue_zhi = sizhu.get('yue_zhu', {}).get('di_zhi', '')
    shi_zhi = sizhu.get('shi_zhu', {}).get('di_zhi', '')
    if yue_zhi and shi_zhi:
        result['ming_gong'] = calculate_minggong(yue_zhi, shi_zhi)
    
    # 5. 胎元
    if yue_zhi and ri_gan:
        result['tai_yuan'] = calculate_taiyuan(yue_zhi, ri_gan)
    
    # 6. 身宫
    if yue_zhi and shi_zhi:
        result['shen_gong'] = calculate_shen_gong(yue_zhi, shi_zhi)
    
    return result

def calculate_zhi_relations(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算地支之间的关系（六合、六冲、三合、三刑、相害）
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        地支关係字典
    """
    # 收集所有地支
    zhi_list = []
    zhu_names = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']
    for zhu_name in zhu_names:
        zhi = sizhu.get(zhu_name, {}).get('di_zhi', '')
        if zhi:
            zhi_list.append({'name': zhu_name, 'zhi': zhi})
    
    relations = {
        'liu_he': [],  # 六合
        'liu_chong': [],  # 六冲
        'san_he': [],  # 三合
        'san_xing': [],  # 三刑
        'liu_hai': [],  # 六害
    }
    
    # 地支六合
    liu_he_pairs = [
        ('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')
    ]
    
    # 地支六冲
    liu_chong_pairs = [
        ('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
    ]
    
    # 地支三合
    san_he_groups = [
        {'zhis': ['申', '子', '辰'], 'wuxing': '水', 'name': '申子辰合水局'},
        {'zhis': ['寅', '午', '戌'], 'wuxing': '火', 'name': '寅午戌合火局'},
        {'zhis': ['巳', '酉', '丑'], 'wuxing': '金', 'name': '巳酉丑合金局'},
        {'zhis': ['亥', '卯', '未'], 'wuxing': '木', 'name': '亥卯未合木局'},
    ]
    
    # 地支三刑
    san_xing_groups = [
        {'zhis': ['寅', '巳', '申'], 'name': '寅巳申三刑'},
        {'zhis': ['丑', '戌', '未'], 'name': '丑戌未三刑'},
        {'zhis': ['子', '卯'], 'name': '子卯相刑'},
    ]
    
    # 地支六害
    liu_hai_pairs = [
        ('子', '未'), ('丑', '午'), ('寅', '巳'), ('卯', '辰'), ('申', '亥'), ('酉', '戌')
    ]
    
    # 检查六合
    for i, item1 in enumerate(zhi_list):
        for item2 in zhi_list[i+1:]:
            pair = (item1['zhi'], item2['zhi'])
            reverse_pair = (item2['zhi'], item1['zhi'])
            if pair in liu_he_pairs or reverse_pair in liu_he_pairs:
                relations['liu_he'].append({
                    'zhi1': item1['zhi'],
                    'zhi2': item2['zhi'],
                    'zhu1': item1['name'],
                    'zhu2': item2['name'],
                    'desc': f"{item1['zhi']}{item2['zhi']}相合",
                })
    
    # 检查六冲
    for i, item1 in enumerate(zhi_list):
        for item2 in zhi_list[i+1:]:
            pair = (item1['zhi'], item2['zhi'])
            reverse_pair = (item2['zhi'], item1['zhi'])
            if pair in liu_chong_pairs or reverse_pair in liu_chong_pairs:
                relations['liu_chong'].append({
                    'zhi1': item1['zhi'],
                    'zhi2': item2['zhi'],
                    'zhu1': item1['name'],
                    'zhu2': item2['name'],
                    'desc': f"{item1['zhi']}{item2['zhi']}相冲",
                })
    
    # 检查三合
    all_zhis = [item['zhi'] for item in zhi_list]
    for group in san_he_groups:
        found = [zhi for zhi in group['zhis'] if zhi in all_zhis]
        if len(found) >= 2:  # 至少有两个才显示
            relations['san_he'].append({
                'zhis': found,
                'wuxing': group['wuxing'],
                'name': group['name'],
                'complete': len(found) == 3,
                'desc': f"{'、'.join(found)}{'（三合全）' if len(found) == 3 else '（半合）'}",
            })
    
    # 检查三刑
    for group in san_xing_groups:
        found = [zhi for zhi in group['zhis'] if zhi in all_zhis]
        if len(found) >= 2:
            relations['san_xing'].append({
                'zhis': found,
                'name': group['name'],
                'desc': f"{'、'.join(found)}相刑",
            })
    
    # 检查六害
    for i, item1 in enumerate(zhi_list):
        for item2 in zhi_list[i+1:]:
            pair = (item1['zhi'], item2['zhi'])
            reverse_pair = (item2['zhi'], item1['zhi'])
            if pair in liu_hai_pairs or reverse_pair in liu_hai_pairs:
                relations['liu_hai'].append({
                    'zhi1': item1['zhi'],
                    'zhi2': item2['zhi'],
                    'zhu1': item1['name'],
                    'zhu2': item2['name'],
                    'desc': f"{item1['zhi']}{item2['zhi']}相害",
                })
    
    return relations

def calculate_gan_relations(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算天干之间的关系（天干合化、天干相冲）
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        天干关係字典
    """
    # 收集所有天干
    gan_list = []
    zhu_names = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']
    for zhu_name in zhu_names:
        gan = sizhu.get(zhu_name, {}).get('tian_gan', '')
        if gan:
            gan_list.append({'name': zhu_name, 'gan': gan})
    
    relations = {
        'tian_gan_he': [],  # 天干合化
        'tian_gan_chong': [],  # 天干相冲
    }
    
    # 天干合化
    tian_gan_he_pairs = [
        {'gans': ['甲', '己'], 'hua': '土'},
        {'gans': ['乙', '庚'], 'hua': '金'},
        {'gans': ['丙', '辛'], 'hua': '水'},
        {'gans': ['丁', '壬'], 'hua': '木'},
        {'gans': ['戊', '癸'], 'hua': '火'},
    ]
    
    # 天干相冲（阳干对阳干，阴干对阴干）
    tian_gan_chong_pairs = [
        ('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸'), ('戊', '己'),
    ]
    
    # 检查天干合化
    for i, item1 in enumerate(gan_list):
        for item2 in gan_list[i+1:]:
            for he_pair in tian_gan_he_pairs:
                if item1['gan'] in he_pair['gans'] and item2['gan'] in he_pair['gans']:
                    relations['tian_gan_he'].append({
                        'gan1': item1['gan'],
                        'gan2': item2['gan'],
                        'zhu1': item1['name'],
                        'zhu2': item2['name'],
                        'hua_wuxing': he_pair['hua'],
                        'desc': f"{item1['gan']}{item2['gan']}合化{he_pair['hua']}",
                    })
    
    # 检查天干相冲
    for i, item1 in enumerate(gan_list):
        for item2 in gan_list[i+1:]:
            pair = (item1['gan'], item2['gan'])
            reverse_pair = (item2['gan'], item1['gan'])
            if pair in tian_gan_chong_pairs or reverse_pair in tian_gan_chong_pairs:
                relations['tian_gan_chong'].append({
                    'gan1': item1['gan'],
                    'gan2': item2['gan'],
                    'zhu1': item1['name'],
                    'zhu2': item2['name'],
                    'desc': f"{item1['gan']}{item2['gan']}相冲",
                })
    
    return relations

def calculate_liuyue_list(
    sizhu: Dict[str, Any],
    start_year: int,
    start_month: int,
    months_count: int,
    birth_year: int = None,
    gender: str = '男',
    wuxing_analysis: Dict[str, Any] = None,
    is_lunar: bool = True,
) -> Dict[str, Any]:
    """
    计算未来N个月的流月列表
    
    Args:
        sizhu: 四柱数据
        start_year: 起始年份（农历或公历）
        start_month: 起始月份(1-12，农历或公历)
        months_count: 推演月数
        birth_year: 出生年份（用于确定当前大运）
        gender: 性别
        wuxing_analysis: 五行分析结果
        is_lunar: 是否为农历时间（默认True）
    
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
        # 计算流年干支
        # 八字流年以立春为界，农历正月（寅月）开始为新年
        # 农历月份：1=寅月, 2=卯月, ..., 11=子月, 12=丑月
        # 流年干支：寅月到丑月都使用当前农历年份的干支
        
        # 农历年份直接对应流年干支（因为农历正月就是寅月，立春后）
        liunian_gan = get_tian_gan(current_year)
        liunian_zhi = get_di_zhi(current_year)
        liunian_data = {
            'year': current_year,
            'gan': liunian_gan,
            'zhi': liunian_zhi,
            'is_lunar': is_lunar,
        }
        
        # 农历月份名称
        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月',
                           '七月', '八月', '九月', '十月', '冬月', '腊月']
        lunar_month_name = lunar_month_names[current_month - 1] if 1 <= current_month <= 12 else f'{current_month}月'
        
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
        liuyue['lunar_month_name'] = lunar_month_name
        liuyue['is_lunar'] = is_lunar
        liuyue_list.append(liuyue)
        
        # 递增月份（农历月份循环）
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
        'is_lunar': is_lunar,
    }

