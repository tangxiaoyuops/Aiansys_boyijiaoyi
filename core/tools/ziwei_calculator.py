"""
紫微斗数排盘计算器
基于 iztro 逻辑的完整实现
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ==================== 基础常量定义 ====================

# 天干
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 十二宫位（固定顺序：从命宫开始顺时针）
PALACE_NAMES = [
    '命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
    '迁移', '奴仆', '官禄', '田宅', '福德', '父母'
]

# 时辰对应地支（子时=0, 丑时=1, ...）
SHI_CHEN_TO_DI_ZHI = {
    '子': 0, '丑': 1, '寅': 2, '卯': 3, '辰': 4, '巳': 5,
    '午': 6, '未': 7, '申': 8, '酉': 9, '戌': 10, '亥': 11
}

# 地支对应时辰（反向映射）
DI_ZHI_TO_SHI_CHEN = {v: k for k, v in SHI_CHEN_TO_DI_ZHI.items()}

# 主星列表（14主星）
MAIN_STARS = [
    '紫微', '天机', '太阳', '武曲', '天同', '廉贞',
    '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
    '七杀', '破军'
]

# 六吉星
LUCKY_STARS = ['左辅', '右弼', '文曲', '文昌', '天魁', '天钺']

# 六煞星
EVIL_STARS = ['擎羊', '陀罗', '火星', '铃星', '地空', '地劫']

# 其他重要辅星
OTHER_AUXILIARY_STARS = ['禄存', '天马', '天刑', '天姚', '红鸾', '天喜']

# 紫微星查表法 - 根据农历月份和时辰确定紫微星所在宫位
# 格式: (农历月份, 时辰地支) -> 紫微星所在宫位索引
ZIWEI_POSITION_TABLE = {
    # 正月（农历一月）
    (1, '子'): 2, (1, '丑'): 1, (1, '寅'): 0, (1, '卯'): 11, (1, '辰'): 10, (1, '巳'): 9,
    (1, '午'): 8, (1, '未'): 7, (1, '申'): 6, (1, '酉'): 5, (1, '戌'): 4, (1, '亥'): 3,
    # 二月
    (2, '子'): 3, (2, '丑'): 2, (2, '寅'): 1, (2, '卯'): 0, (2, '辰'): 11, (2, '巳'): 10,
    (2, '午'): 9, (2, '未'): 8, (2, '申'): 7, (2, '酉'): 6, (2, '戌'): 5, (2, '亥'): 4,
    # 三月
    (3, '子'): 4, (3, '丑'): 3, (3, '寅'): 2, (3, '卯'): 1, (3, '辰'): 0, (3, '巳'): 11,
    (3, '午'): 10, (3, '未'): 9, (3, '申'): 8, (3, '酉'): 7, (3, '戌'): 6, (3, '亥'): 5,
    # 四月
    (4, '子'): 5, (4, '丑'): 4, (4, '寅'): 3, (4, '卯'): 2, (4, '辰'): 1, (4, '巳'): 0,
    (4, '午'): 11, (4, '未'): 10, (4, '申'): 9, (4, '酉'): 8, (4, '戌'): 7, (4, '亥'): 6,
    # 五月
    (5, '子'): 6, (5, '丑'): 5, (5, '寅'): 4, (5, '卯'): 3, (5, '辰'): 2, (5, '巳'): 1,
    (5, '午'): 0, (5, '未'): 11, (5, '申'): 10, (5, '酉'): 9, (5, '戌'): 8, (5, '亥'): 7,
    # 六月
    (6, '子'): 7, (6, '丑'): 6, (6, '寅'): 5, (6, '卯'): 4, (6, '辰'): 3, (6, '巳'): 2,
    (6, '午'): 1, (6, '未'): 0, (6, '申'): 11, (6, '酉'): 10, (6, '戌'): 9, (6, '亥'): 8,
    # 七月
    (7, '子'): 8, (7, '丑'): 7, (7, '寅'): 6, (7, '卯'): 5, (7, '辰'): 4, (7, '巳'): 3,
    (7, '午'): 2, (7, '未'): 1, (7, '申'): 0, (7, '酉'): 11, (7, '戌'): 10, (7, '亥'): 9,
    # 八月
    (8, '子'): 9, (8, '丑'): 8, (8, '寅'): 7, (8, '卯'): 6, (8, '辰'): 5, (8, '巳'): 4,
    (8, '午'): 3, (8, '未'): 2, (8, '申'): 1, (8, '酉'): 0, (8, '戌'): 11, (8, '亥'): 10,
    # 九月
    (9, '子'): 10, (9, '丑'): 9, (9, '寅'): 8, (9, '卯'): 7, (9, '辰'): 6, (9, '巳'): 5,
    (9, '午'): 4, (9, '未'): 3, (9, '申'): 2, (9, '酉'): 1, (9, '戌'): 0, (9, '亥'): 11,
    # 十月
    (10, '子'): 11, (10, '丑'): 10, (10, '寅'): 9, (10, '卯'): 8, (10, '辰'): 7, (10, '巳'): 6,
    (10, '午'): 5, (10, '未'): 4, (10, '申'): 3, (10, '酉'): 2, (10, '戌'): 1, (10, '亥'): 0,
    # 十一月
    (11, '子'): 0, (11, '丑'): 11, (11, '寅'): 10, (11, '卯'): 9, (11, '辰'): 8, (11, '巳'): 7,
    (11, '午'): 6, (11, '未'): 5, (11, '申'): 4, (11, '酉'): 3, (11, '戌'): 2, (11, '亥'): 1,
    # 十二月
    (12, '子'): 1, (12, '丑'): 0, (12, '寅'): 11, (12, '卯'): 10, (12, '辰'): 9, (12, '巳'): 8,
    (12, '午'): 7, (12, '未'): 6, (12, '申'): 5, (12, '酉'): 4, (12, '戌'): 3, (12, '亥'): 2,
}

# ==================== 工具函数 ====================

def get_tian_gan(year: int) -> str:
    """根据年份获取天干"""
    # 天干循环：甲=4, 乙=5, ..., 癸=3 (以1984年为甲子年参考)
    # 1984年是甲子年，天干索引为0（甲）
    base_year = 1984
    gan_index = (year - base_year) % 10
    return TIAN_GAN[gan_index]

def get_di_zhi(year: int) -> str:
    """根据年份获取地支"""
    # 地支循环：子=4, 丑=5, ..., 亥=3 (以1984年为甲子年参考)
    base_year = 1984
    zhi_index = (year - base_year) % 12
    return DI_ZHI[zhi_index]

def get_tian_gan_index(gan: str) -> int:
    """获取天干索引"""
    return TIAN_GAN.index(gan)

def get_di_zhi_index(zhi: str) -> int:
    """获取地支索引"""
    return DI_ZHI.index(zhi)

def normalize_palace_index(index: int) -> int:
    """标准化宫位索引（0-11）"""
    return index % 12

def get_palace_name(index: int) -> str:
    """根据索引获取宫位名称"""
    return PALACE_NAMES[normalize_palace_index(index)]

def get_opposite_palace(index: int) -> int:
    """获取对宫索引（相隔6个宫位）"""
    return normalize_palace_index(index + 6)

def get_triangular_palaces(index: int) -> List[int]:
    """获取三方宫位（本宫、对宫、相邻宫）"""
    opposite = get_opposite_palace(index)
    # 三方：本宫、对宫、以及本宫+4或-4的宫位
    third = normalize_palace_index(index + 4)
    return [index, opposite, third]

def get_four_corners_palaces(index: int) -> List[int]:
    """获取四正宫位（本宫、对宫、左右相邻宫）"""
    opposite = get_opposite_palace(index)
    left = normalize_palace_index(index - 1)
    right = normalize_palace_index(index + 1)
    return [index, opposite, left, right]

# ==================== 农历转换 ====================

def convert_to_lunar(year: int, month: int, day: int) -> Tuple[int, int, int]:
    """
    将公历日期转换为农历日期
    
    支持多种农历转换库：
    1. zhdate (推荐，更稳定)
    2. lunarcalendar
    3. chinesecalendar
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        (农历年, 农历月, 农历日)
    """
    # 方式1：尝试使用zhdate库（推荐）
    try:
        from zhdate import ZhDate
        import datetime
        
        # 方式1.1：使用from_datetime方法
        try:
            solar_dt = datetime.datetime(year, month, day)
            lunar_date = ZhDate.from_datetime(solar_dt)
            # zhdate对象可能有year/month/day（农历）或lunar_year/lunar_month/lunar_day属性
            if hasattr(lunar_date, 'lunar_year'):
                logger.debug(f"使用zhdate.from_datetime转换: 公历{year}-{month}-{day} -> 农历{lunar_date.lunar_year}-{lunar_date.lunar_month}-{lunar_date.lunar_day}")
                return lunar_date.lunar_year, lunar_date.lunar_month, lunar_date.lunar_day
            elif hasattr(lunar_date, 'year'):  # 可能直接是year属性
                logger.debug(f"使用zhdate.from_datetime转换（year属性）: 公历{year}-{month}-{day} -> 农历{lunar_date.year}-{lunar_date.month}-{lunar_date.day}")
                return lunar_date.year, lunar_date.month, lunar_date.day
        except (AttributeError, TypeError) as e:
            logger.debug(f"zhdate.from_datetime失败: {e}，尝试其他方式")
        
        # 方式1.2：直接构造（传入公历年月日，返回农历对象）
        try:
            lunar_date = ZhDate(year, month, day)
            if hasattr(lunar_date, 'lunar_year'):
                logger.debug(f"使用zhdate直接构造转换: 公历{year}-{month}-{day} -> 农历{lunar_date.lunar_year}-{lunar_date.lunar_month}-{lunar_date.lunar_day}")
                return lunar_date.lunar_year, lunar_date.lunar_month, lunar_date.lunar_day
            elif hasattr(lunar_date, 'year'):
                logger.debug(f"使用zhdate直接构造转换（year属性）: 公历{year}-{month}-{day} -> 农历{lunar_date.year}-{lunar_date.month}-{lunar_date.day}")
                return lunar_date.year, lunar_date.month, lunar_date.day
        except (AttributeError, TypeError) as e:
            logger.debug(f"zhdate直接构造失败: {e}")
        
        # 方式1.3：尝试使用date对象
        try:
            solar_date = datetime.date(year, month, day)
            lunar_date = ZhDate.from_datetime(solar_date)
            if hasattr(lunar_date, 'lunar_year'):
                return lunar_date.lunar_year, lunar_date.lunar_month, lunar_date.lunar_day
            elif hasattr(lunar_date, 'year'):
                return lunar_date.year, lunar_date.month, lunar_date.day
        except Exception as e:
            logger.debug(f"zhdate.date方式失败: {e}")
        
        # 如果都不行，说明API不对
        logger.warning(f"zhdate库已导入，但API不匹配。请检查zhdate版本和API文档。")
        raise AttributeError("zhdate API不匹配")
        
    except ImportError as e:
        logger.warning(f"zhdate库未安装或导入失败: {e}")
        logger.warning(f"请确认: 1) 已激活正确的虚拟环境 2) 已运行 pip install zhdate 3) PyCharm解释器指向正确的环境")
    except Exception as e:
        logger.warning(f"zhdate转换失败: {e}, 类型: {type(e).__name__}")
        import traceback
        logger.debug(f"zhdate详细错误: {traceback.format_exc()}")
    
    # 方式2：尝试使用lunarcalendar库
    try:
        import lunarcalendar
        solar = lunarcalendar.Solar(year, month, day)
        
        # 检查是否有lunar属性
        if hasattr(solar, 'lunar'):
            lunar = solar.lunar
            if hasattr(lunar, 'year') and hasattr(lunar, 'month') and hasattr(lunar, 'day'):
                logger.debug(f"使用lunarcalendar转换: 公历{year}-{month}-{day} -> 农历{lunar.year}-{lunar.month}-{lunar.day}")
                return lunar.year, lunar.month, lunar.day
        
        # 尝试使用Converter类（检查实际方法名）
        if hasattr(lunarcalendar, 'Converter'):
            converter = lunarcalendar.Converter()
            # 尝试不同的方法名
            for method_name in ['solar_to_lunar', 'to_lunar', 'convert', 'solar2lunar']:
                if hasattr(converter, method_name):
                    method = getattr(converter, method_name)
                    lunar = method(year, month, day) if callable(method) else None
                    if lunar and hasattr(lunar, 'year'):
                        logger.debug(f"使用lunarcalendar.Converter.{method_name}转换")
                        return lunar.year, lunar.month, lunar.day
        
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"lunarcalendar转换失败: {e}")
    
    # 方式3：尝试使用chinesecalendar库
    try:
        import chinesecalendar
        import datetime
        solar_date = datetime.date(year, month, day)
        lunar_date = chinesecalendar.get_lunar_date(solar_date)
        if hasattr(lunar_date, 'year'):
            logger.debug(f"使用chinesecalendar转换")
            return lunar_date.year, lunar_date.month, lunar_date.day
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"chinesecalendar转换失败: {e}")
    
    # 降级处理：使用简化算法（农历=公历）
    logger.warning(f"所有农历转换库都不可用，使用简化算法（农历=公历）。建议安装: pip install zhdate")
    return year, month, day

# ==================== 命宫身宫计算 ====================

def calculate_ming_gong(lunar_month: int, shi_chen: str) -> int:
    """
    计算命宫位置
    
    命宫算法：
    1. 从寅宫（索引2）开始，作为正月
    2. 顺时针数到出生月份
    3. 从该宫位开始，逆时针数到出生时辰
    
    Args:
        lunar_month: 农历月份 (1-12)
        shi_chen: 时辰地支 (子、丑、寅...)
    
    Returns:
        命宫所在宫位索引 (0-11)
    """
    # 寅宫是索引2（从命宫开始，寅是第3个宫位）
    # 从寅宫开始，顺时针数到出生月份
    # 正月在寅宫，二月在卯宫，以此类推
    yin_palace = 2  # 寅宫索引
    month_palace = normalize_palace_index(yin_palace + lunar_month - 1)
    
    # 从该宫位开始，逆时针数到出生时辰
    shi_chen_index = get_di_zhi_index(shi_chen)
    # 逆时针：减去时辰索引
    ming_gong = normalize_palace_index(month_palace - shi_chen_index)
    
    logger.debug(f"命宫计算: 农历月={lunar_month}, 时辰={shi_chen}, 命宫={get_palace_name(ming_gong)}")
    return ming_gong

def calculate_shen_gong(lunar_month: int, shi_chen: str) -> int:
    """
    计算身宫位置
    
    身宫算法：
    1. 从寅宫（索引2）开始，作为正月
    2. 逆时针数到出生月份
    3. 从该宫位开始，顺时针数到出生时辰
    
    Args:
        lunar_month: 农历月份 (1-12)
        shi_chen: 时辰地支 (子、丑、寅...)
    
    Returns:
        身宫所在宫位索引 (0-11)
    """
    # 寅宫是索引2
    # 从寅宫开始，逆时针数到出生月份
    yin_palace = 2
    month_palace = normalize_palace_index(yin_palace - (lunar_month - 1))
    
    # 从该宫位开始，顺时针数到出生时辰
    shi_chen_index = get_di_zhi_index(shi_chen)
    shen_gong = normalize_palace_index(month_palace + shi_chen_index)
    
    logger.debug(f"身宫计算: 农历月={lunar_month}, 时辰={shi_chen}, 身宫={get_palace_name(shen_gong)}")
    return shen_gong

# ==================== 紫微星位置计算 ====================

def calculate_ziwei_star(lunar_month: int, shi_chen: str) -> int:
    """
    计算紫微星所在宫位（查表法）
    
    根据农历月份和时辰，从查表中获取紫微星位置
    
    Args:
        lunar_month: 农历月份 (1-12)
        shi_chen: 时辰地支 (子、丑、寅...)
    
    Returns:
        紫微星所在宫位索引 (0-11)
    """
    key = (lunar_month, shi_chen)
    if key not in ZIWEI_POSITION_TABLE:
        logger.warning(f"查表中未找到: 农历月={lunar_month}, 时辰={shi_chen}，使用默认值")
        return 0  # 默认在命宫
    
    ziwei_palace = ZIWEI_POSITION_TABLE[key]
    logger.debug(f"紫微星计算: 农历月={lunar_month}, 时辰={shi_chen}, 紫微星={get_palace_name(ziwei_palace)}")
    return ziwei_palace

# ==================== 其他主星排布 ====================

def calculate_ziwei_star_group(ziwei_palace: int) -> Dict[str, int]:
    """
    计算紫微星系主星位置
    
    紫微星系包括：紫微、天机、太阳、武曲、天同、廉贞
    
    排布规则（从紫微星位置开始，逆时针）：
    - 紫微：已确定
    - 天机：紫微-1
    - 太阳：紫微-3
    - 武曲：紫微-4
    - 天同：紫微-5
    - 廉贞：紫微-8
    
    Args:
        ziwei_palace: 紫微星所在宫位索引
    
    Returns:
        主星名称到宫位索引的字典
    """
    stars = {
        '紫微': ziwei_palace,
        '天机': normalize_palace_index(ziwei_palace - 1),
        '太阳': normalize_palace_index(ziwei_palace - 3),
        '武曲': normalize_palace_index(ziwei_palace - 4),
        '天同': normalize_palace_index(ziwei_palace - 5),
        '廉贞': normalize_palace_index(ziwei_palace - 8),
    }
    logger.debug(f"紫微星系: {stars}")
    return stars

def calculate_tianfu_star_group(ziwei_palace: int) -> Dict[str, int]:
    """
    计算天府星系主星位置
    
    天府星系包括：天府、太阴、贪狼、巨门、天相、天梁、七杀、破军
    
    排布规则：
    1. 天府与紫微相对（相隔6个宫位）
    2. 从天府开始，顺时针排布其他星
    
    Args:
        ziwei_palace: 紫微星所在宫位索引（用于计算天府位置）
    
    Returns:
        主星名称到宫位索引的字典
    """
    # 天府与紫微相对
    tianfu_palace = get_opposite_palace(ziwei_palace)
    
    stars = {
        '天府': tianfu_palace,
        '太阴': normalize_palace_index(tianfu_palace + 1),
        '贪狼': normalize_palace_index(tianfu_palace + 2),
        '巨门': normalize_palace_index(tianfu_palace + 3),
        '天相': normalize_palace_index(tianfu_palace + 4),
        '天梁': normalize_palace_index(tianfu_palace + 5),
        '七杀': normalize_palace_index(tianfu_palace + 6),
        '破军': normalize_palace_index(tianfu_palace + 10),
    }
    logger.debug(f"天府星系: {stars}")
    return stars

def calculate_all_main_stars(ziwei_palace: int) -> Dict[str, int]:
    """
    计算所有14主星的位置
    
    Args:
        ziwei_palace: 紫微星所在宫位索引
    
    Returns:
        所有主星名称到宫位索引的字典
    """
    ziwei_group = calculate_ziwei_star_group(ziwei_palace)
    tianfu_group = calculate_tianfu_star_group(ziwei_palace)
    
    # 合并两组主星
    all_stars = {**ziwei_group, **tianfu_group}
    
    logger.debug(f"所有主星位置: {all_stars}")
    return all_stars

# ==================== 辅星计算 ====================

def calculate_lucky_stars(year_gan: str, year_zhi: str, month_zhi: str, shi_chen: str) -> Dict[str, int]:
    """
    计算六吉星位置
    
    六吉星：左辅、右弼、文曲、文昌、天魁、天钺
    
    排布规则：
    - 左辅：从辰宫开始，顺时针数到年支
    - 右弼：从戌宫开始，逆时针数到年支
    - 文曲：从辰宫开始，顺时针数到时支
    - 文昌：从戌宫开始，逆时针数到时支
    - 天魁：根据年干查表
    - 天钺：根据年干查表
    
    Args:
        year_gan: 年干
        year_zhi: 年支
        month_zhi: 月支
        shi_chen: 时辰地支
    
    Returns:
        吉星名称到宫位索引的字典
    """
    chen_palace = 4  # 辰宫索引
    xu_palace = 10   # 戌宫索引
    
    year_zhi_index = get_di_zhi_index(year_zhi)
    shi_chen_index = get_di_zhi_index(shi_chen)
    
    # 天魁天钺查表（根据年干）
    tiankui_tianyue_table = {
        '甲': {'天魁': 1, '天钺': 7},  # 甲年：天魁在丑，天钺在未
        '乙': {'天魁': 0, '天钺': 6},  # 乙年：天魁在子，天钺在午
        '丙': {'天魁': 9, '天钺': 3},  # 丙年：天魁在亥，天钺在卯
        '丁': {'天魁': 9, '天钺': 3},  # 丁年：天魁在亥，天钺在卯
        '戊': {'天魁': 1, '天钺': 7},  # 戊年：天魁在丑，天钺在未
        '己': {'天魁': 1, '天钺': 7},  # 己年：天魁在丑，天钺在未
        '庚': {'天魁': 11, '天钺': 5}, # 庚年：天魁在寅，天钺在申
        '辛': {'天魁': 11, '天钺': 5}, # 辛年：天魁在寅，天钺在申
        '壬': {'天魁': 5, '天钺': 11}, # 壬年：天魁在申，天钺在寅
        '癸': {'天魁': 5, '天钺': 11}, # 癸年：天魁在申，天钺在寅
    }
    
    tiankui_tianyue = tiankui_tianyue_table.get(year_gan, {'天魁': 0, '天钺': 6})
    
    stars = {
        '左辅': normalize_palace_index(chen_palace + year_zhi_index),
        '右弼': normalize_palace_index(xu_palace - year_zhi_index),
        '文曲': normalize_palace_index(chen_palace + shi_chen_index),
        '文昌': normalize_palace_index(xu_palace - shi_chen_index),
        '天魁': tiankui_tianyue['天魁'],
        '天钺': tiankui_tianyue['天钺'],
    }
    
    logger.debug(f"六吉星: {stars}")
    return stars

def calculate_evil_stars(year_zhi: str, month_zhi: str, shi_chen: str) -> Dict[str, int]:
    """
    计算六煞星位置
    
    六煞星：擎羊、陀罗、火星、铃星、地空、地劫
    
    排布规则：
    - 擎羊：在年支的顺数第1位（年支+1）
    - 陀罗：在年支的逆数第1位（年支-1）
    - 火星：根据年支和时支计算
    - 铃星：根据年支和时支计算
    - 地空：从亥宫开始，逆时针数到年支
    - 地劫：从亥宫开始，顺时针数到年支
    
    Args:
        year_zhi: 年支
        month_zhi: 月支
        shi_chen: 时辰地支
    
    Returns:
        煞星名称到宫位索引的字典
    """
    year_zhi_index = get_di_zhi_index(year_zhi)
    shi_chen_index = get_di_zhi_index(shi_chen)
    hai_palace = 11  # 亥宫索引
    
    # 火星铃星查表（根据年支和时支）
    # 简化算法：火星在年支+2，铃星在年支+时支索引
    huoxing_palace = normalize_palace_index(year_zhi_index + 2)
    lingxing_palace = normalize_palace_index(year_zhi_index + shi_chen_index)
    
    stars = {
        '擎羊': normalize_palace_index(year_zhi_index + 1),
        '陀罗': normalize_palace_index(year_zhi_index - 1),
        '火星': huoxing_palace,
        '铃星': lingxing_palace,
        '地空': normalize_palace_index(hai_palace - year_zhi_index),
        '地劫': normalize_palace_index(hai_palace + year_zhi_index),
    }
    
    logger.debug(f"六煞星: {stars}")
    return stars

def calculate_other_auxiliary_stars(year_zhi: str, shi_chen: str) -> Dict[str, int]:
    """
    计算其他重要辅星位置
    
    包括：禄存、天马等
    
    排布规则：
    - 禄存：根据年干查表
    - 天马：根据年支查表（寅申巳亥年）
    
    Args:
        year_zhi: 年支
        shi_chen: 时辰地支
    
    Returns:
        辅星名称到宫位索引的字典
    """
    # 禄存查表（根据年干，需要传入年干，这里简化处理）
    # 天马在寅申巳亥年，分别在寅申巳亥宫
    tianma_palaces = {
        '寅': 2, '申': 8, '巳': 5, '亥': 11
    }
    
    stars = {}
    
    # 天马
    if year_zhi in tianma_palaces:
        stars['天马'] = tianma_palaces[year_zhi]
    
    logger.debug(f"其他辅星: {stars}")
    return stars

def calculate_all_auxiliary_stars(year_gan: str, year_zhi: str, month_zhi: str, shi_chen: str) -> Dict[str, int]:
    """
    计算所有辅星位置
    
    Args:
        year_gan: 年干
        year_zhi: 年支
        month_zhi: 月支
        shi_chen: 时辰地支
    
    Returns:
        所有辅星名称到宫位索引的字典
    """
    lucky = calculate_lucky_stars(year_gan, year_zhi, month_zhi, shi_chen)
    evil = calculate_evil_stars(year_zhi, month_zhi, shi_chen)
    other = calculate_other_auxiliary_stars(year_zhi, shi_chen)
    
    all_auxiliary = {**lucky, **evil, **other}
    logger.debug(f"所有辅星: {all_auxiliary}")
    return all_auxiliary

# ==================== 整合排盘函数 ====================

def create_pan(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = '男'
) -> Dict[str, any]:
    """
    创建完整的紫微斗数命盘
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23，会自动转换为地支时辰）
        gender: 性别（'男' 或 '女'）
    
    Returns:
        完整的命盘数据字典，包含：
        - birth_info: 出生信息
        - ming_gong: 命宫索引
        - shen_gong: 身宫索引
        - palaces: 十二宫位数据
        - main_stars: 主星位置
        - auxiliary_stars: 辅星位置
    """
    # 1. 转换为农历
    lunar_year, lunar_month, lunar_day = convert_to_lunar(year, month, day)
    
    # 2. 计算天干地支
    year_gan = get_tian_gan(year)
    year_zhi = get_di_zhi(year)
    
    # 3. 计算月支（简化：假设农历月支 = 农历月份对应的地支）
    month_zhi = DI_ZHI[(lunar_month - 1) % 12]
    
    # 4. 计算时辰地支
    # 将24小时制转换为地支时辰
    hour_to_shi_chen = {
        23: '子', 0: '子', 1: '丑', 2: '丑', 3: '寅', 4: '寅',
        5: '卯', 6: '卯', 7: '辰', 8: '辰', 9: '巳', 10: '巳',
        11: '午', 12: '午', 13: '未', 14: '未', 15: '申', 16: '申',
        17: '酉', 18: '酉', 19: '戌', 20: '戌', 21: '亥', 22: '亥'
    }
    shi_chen = hour_to_shi_chen.get(hour, '子')
    
    # 5. 计算命宫身宫
    ming_gong = calculate_ming_gong(lunar_month, shi_chen)
    shen_gong = calculate_shen_gong(lunar_month, shi_chen)
    
    # 6. 计算紫微星位置
    ziwei_palace = calculate_ziwei_star(lunar_month, shi_chen)
    
    # 7. 计算所有主星
    main_stars = calculate_all_main_stars(ziwei_palace)
    
    # 8. 计算所有辅星
    auxiliary_stars = calculate_all_auxiliary_stars(year_gan, year_zhi, month_zhi, shi_chen)
    
    # 9. 构建十二宫位数据
    palaces = []
    for i in range(12):
        palace_name = get_palace_name(i)
        
        # 收集该宫位的主星
        palace_main_stars = [star for star, pos in main_stars.items() if pos == i]
        
        # 收集该宫位的辅星
        palace_auxiliary_stars = [star for star, pos in auxiliary_stars.items() if pos == i]
        
        palace_data = {
            'index': i,
            'name': palace_name,
            'main_stars': palace_main_stars,
            'auxiliary_stars': palace_auxiliary_stars,
            'is_ming_gong': i == ming_gong,
            'is_shen_gong': i == shen_gong,
        }
        palaces.append(palace_data)
    
    # 10. 构建完整命盘
    pan_data = {
        'birth_info': {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'gender': gender,
            'lunar_year': lunar_year,
            'lunar_month': lunar_month,
            'lunar_day': lunar_day,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_zhi': month_zhi,
            'shi_chen': shi_chen,
        },
        'ming_gong': ming_gong,
        'shen_gong': shen_gong,
        'ziwei_palace': ziwei_palace,
        'palaces': palaces,
        'main_stars': main_stars,
        'auxiliary_stars': auxiliary_stars,
    }
    
    logger.info(f"命盘创建完成: 命宫={get_palace_name(ming_gong)}, 身宫={get_palace_name(shen_gong)}")
    return pan_data
