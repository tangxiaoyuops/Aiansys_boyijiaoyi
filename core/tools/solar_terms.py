"""
精确24节气计算模块
使用寿星天文历算法，基于天文学计算太阳黄经来确定节气

算法原理：
1. 使用Julian日（儒略日）作为时间基准
2. 计算太阳黄经
3. 当太阳黄经为0°、15°、30°...时对应各个节气（春分0°开始）

参考：寿星天文历算法
"""
from typing import Tuple, List, Dict, Optional
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger(__name__)

# 24节气列表（按传统顺序：立春为岁首）
# 索引0=立春, 1=雨水, ..., 22=小寒, 23=大寒
TRADITIONAL_TERMS = [
    '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
    '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
    '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
    '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
]

# 节气对应的太阳黄经（度）
# 立春=315°, 雨水=330°, 惊蛰=345°, 春分=0°, 清明=15°, 谷雨=30°...
SOLAR_TERM_LONGITUDE = {
    '立春': 315, '雨水': 330, '惊蛰': 345,
    '春分': 0, '清明': 15, '谷雨': 30,
    '立夏': 45, '小满': 60, '芒种': 75,
    '夏至': 90, '小暑': 105, '大暑': 120,
    '立秋': 135, '处暑': 150, '白露': 165,
    '秋分': 180, '寒露': 195, '霜降': 210,
    '立冬': 225, '小雪': 240, '大雪': 255,
    '冬至': 270, '小寒': 285, '大寒': 300
}

# 月支对应节气（以立春为正月开始）
SOLAR_TERM_TO_MONTH_ZHI = {
    '立春': ('寅', 1), '雨水': ('寅', 1),
    '惊蛰': ('卯', 2), '春分': ('卯', 2),
    '清明': ('辰', 3), '谷雨': ('辰', 3),
    '立夏': ('巳', 4), '小满': ('巳', 4),
    '芒种': ('午', 5), '夏至': ('午', 5),
    '小暑': ('未', 6), '大暑': ('未', 6),
    '立秋': ('申', 7), '处暑': ('申', 7),
    '白露': ('酉', 8), '秋分': ('酉', 8),
    '寒露': ('戌', 9), '霜降': ('戌', 9),
    '立冬': ('亥', 10), '小雪': ('亥', 10),
    '大雪': ('子', 11), '冬至': ('子', 11),
    '小寒': ('丑', 12), '大寒': ('丑', 12),
}

# "节"的列表（用于大运计算）
JIE_TERMS = ['立春', '惊蛰', '清明', '立夏', '芒种', '小暑', '立秋', '白露', '寒露', '立冬', '大雪', '小寒']

# 节气大致日期（用于估算）
TERM_ESTIMATES = {
    0: (2, 4),    # 立春
    1: (2, 19),   # 雨水
    2: (3, 6),    # 惊蛰
    3: (3, 21),   # 春分
    4: (4, 5),    # 清明
    5: (4, 20),   # 谷雨
    6: (5, 6),    # 立夏
    7: (5, 21),   # 小满
    8: (6, 6),    # 芒种
    9: (6, 21),   # 夏至
    10: (7, 7),   # 小暑
    11: (7, 23),  # 大暑
    12: (8, 8),   # 立秋
    13: (8, 23),  # 处暑
    14: (9, 8),   # 白露
    15: (9, 23),  # 秋分
    16: (10, 8),  # 寒露
    17: (10, 24), # 霜降
    18: (11, 8),  # 立冬
    19: (11, 22), # 小雪
    20: (12, 7),  # 大雪
    21: (12, 22), # 冬至
    22: (1, 6),   # 小寒
    23: (1, 20),  # 大寒
}


def to_rad(deg: float) -> float:
    """角度转弧度"""
    return deg * math.pi / 180


def jd_from_datetime(dt: datetime) -> float:
    """
    从datetime计算Julian日（儒略日）
    """
    year = dt.year
    month = dt.month
    day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    
    if month <= 2:
        year -= 1
        month += 12
    
    a = int(year / 100)
    b = 2 - a + int(a / 4)
    
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd


def datetime_from_jd(jd: float) -> datetime:
    """从Julian日计算datetime"""
    jd = jd + 0.5
    z = int(jd)
    f = jd - z
    
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    
    day_int = int(day)
    day_frac = day - day_int
    hour = day_frac * 24
    hour_int = int(hour)
    minute = (hour - hour_int) * 60
    minute_int = int(minute)
    second = int((minute - minute_int) * 60)
    
    try:
        return datetime(year, month, day_int, hour_int, minute_int, second)
    except ValueError:
        return datetime(year, month, min(day_int, 28), 12, 0, 0)


def sun_longitude(jd: float) -> float:
    """
    计算太阳黄经（简化VSOP87算法）
    """
    t = (jd - 2451545.0) / 365250.0  # J2000.0起算的儒略世纪数
    
    # 太阳平黄经
    l0 = 280.4664567 + 360007.6982779 * t + 0.03032028 * t * t
    l0 = l0 + t * t * t / 49931 - t * t * t * t / 15300
    
    # 太阳平近点角
    m = 357.5291092 + 35999.0502909 * t - 0.0001536 * t * t
    m = m % 360
    
    # 中心方程
    c = ((1.914602 - 0.004817 * t) * math.sin(to_rad(m))
         + 0.019993 * math.sin(to_rad(2 * m))
         + 0.000289 * math.sin(to_rad(3 * m)))
    
    # 太阳真黄经
    sun_long = l0 + c
    
    # 章动修正
    omega = 125.04 - 1934.136 * t
    sun_long = sun_long - 0.00569 - 0.00478 * math.sin(to_rad(omega))
    
    # 归一化到0-360度
    sun_long = sun_long % 360
    if sun_long < 0:
        sun_long += 360
    
    return sun_long


def find_solar_term_datetime(target_longitude: float, base_jd: float) -> float:
    """
    通过迭代求解太阳黄经等于目标值的精确Julian日
    
    Args:
        target_longitude: 目标太阳黄经（度）
        base_jd: 初始估计的Julian日
    
    Returns:
        精确的Julian日
    """
    jd = base_jd
    
    for _ in range(15):
        current_long = sun_longitude(jd)
        
        # 计算黄经差
        diff = target_longitude - current_long
        
        # 处理跨0度的情况
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if abs(diff) < 0.0001:
            break
        
        jd += diff  # 每度约1天
    
    return jd


def get_solar_term_date(year: int, term_index: int) -> datetime:
    """
    获取指定年份的某个节气日期时间
    
    Args:
        year: 年份
        term_index: 节气索引（0-23，立春=0，雨水=1...大寒=23）
    
    Returns:
        节气的日期时间
    
    Note:
        对于小寒(22)和大寒(23)，返回的是year+1年1月的节气
        例如：get_solar_term_date(2024, 22) 返回2025年1月的小寒
    """
    term_name = TRADITIONAL_TERMS[term_index]
    target_longitude = SOLAR_TERM_LONGITUDE[term_name]
    
    # 根据节气估算初始日期
    est_month, est_day = TERM_ESTIMATES[term_index]
    
    # 对于小寒和大寒（索引22-23），实际日期在下一年
    if term_index >= 22:
        actual_year = year
    else:
        actual_year = year
    
    base_date = datetime(actual_year, est_month, est_day, 12, 0, 0)
    base_jd = jd_from_datetime(base_date)
    
    # 迭代求解精确时间
    result_jd = find_solar_term_datetime(target_longitude, base_jd)
    
    return datetime_from_jd(result_jd)


def get_all_solar_terms_for_year(year: int) -> List[Tuple[str, int, datetime]]:
    """
    获取指定年份（农历年/八字年）的所有节气
    
    返回的节气按时间顺序排列：
    立春 → 雨水 → ... → 冬至 → 小寒 → 大寒
    
    其中立春在year年的2月，小寒大寒在year+1年的1月
    
    Args:
        year: 年份（八字年份）
    
    Returns:
        [(节气名称, 节气索引, 日期时间), ...]
    """
    terms = []
    for i in range(24):
        term_name = TRADITIONAL_TERMS[i]
        term_date = get_solar_term_date(year, i)
        terms.append((term_name, i, term_date))
    return terms


def get_solar_term(year: int, month: int, day: int) -> Tuple[str, int]:
    """
    根据公历日期确定所在的节气区间
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        (节气名称, 节气索引)
    """
    target_date = datetime(year, month, day, 12, 0, 0)
    
    # 确定可能涉及的年份
    # 当前日期可能在：上一年小寒大寒 → 当年立春...冬至 → 下一年小寒大寒
    years_to_check = [year - 1, year, year + 1]
    
    # 收集所有相关节气
    all_terms = []
    for y in years_to_check:
        for i in range(24):
            term_date = get_solar_term_date(y, i)
            all_terms.append((TRADITIONAL_TERMS[i], i, term_date, y))
    
    # 按日期排序
    all_terms.sort(key=lambda x: x[2])
    
    # 查找目标日期所在的节气区间
    for i in range(len(all_terms) - 1):
        term_name, term_idx, term_date, term_year = all_terms[i]
        next_name, next_idx, next_date, next_year = all_terms[i + 1]
        
        if term_date <= target_date < next_date:
            return term_name, term_idx
    
    # 默认返回大寒
    return '大寒', 23


def get_month_zhi_by_solar_term(year: int, month: int, day: int) -> str:
    """
    根据节气确定月支
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        月支（地支）
    """
    term_name, _ = get_solar_term(year, month, day)
    month_zhi, _ = SOLAR_TERM_TO_MONTH_ZHI.get(term_name, ('寅', 1))
    return month_zhi


def get_month_index_by_solar_term(year: int, month: int, day: int) -> int:
    """
    根据节气确定月份索引（1-12，对应寅月到丑月）
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        月份索引（1-12）
    """
    term_name, _ = get_solar_term(year, month, day)
    _, month_index = SOLAR_TERM_TO_MONTH_ZHI.get(term_name, ('寅', 1))
    return month_index


def get_next_solar_term(year: int, month: int, day: int) -> datetime:
    """获取下一个节气的日期时间"""
    target_date = datetime(year, month, day, 12, 0, 0)
    
    years_to_check = [year - 1, year, year + 1, year + 2]
    all_terms = []
    for y in years_to_check:
        for i in range(24):
            term_date = get_solar_term_date(y, i)
            if term_date > target_date:
                all_terms.append((term_date, TRADITIONAL_TERMS[i], i))
    
    all_terms.sort(key=lambda x: x[0])
    return all_terms[0][0] if all_terms else None


def get_prev_solar_term(year: int, month: int, day: int) -> datetime:
    """获取上一个节气的日期时间"""
    target_date = datetime(year, month, day, 12, 0, 0)
    
    years_to_check = [year + 1, year, year - 1, year - 2]
    all_terms = []
    for y in years_to_check:
        for i in range(24):
            term_date = get_solar_term_date(y, i)
            if term_date <= target_date:
                all_terms.append((term_date, TRADITIONAL_TERMS[i], i))
    
    all_terms.sort(key=lambda x: x[0], reverse=True)
    return all_terms[0][0] if all_terms else None


def get_next_jie(year: int, month: int, day: int, hour: int = 0) -> Optional[datetime]:
    """获取下一个"节"的日期时间"""
    target_date = datetime(year, month, day, hour)
    
    years_to_check = [year - 1, year, year + 1, year + 2]
    all_jie = []
    for y in years_to_check:
        for i in range(24):
            term_name = TRADITIONAL_TERMS[i]
            if term_name in JIE_TERMS:
                term_date = get_solar_term_date(y, i)
                if term_date > target_date:
                    all_jie.append((term_date, term_name))
    
    all_jie.sort(key=lambda x: x[0])
    return all_jie[0][0] if all_jie else None


def get_prev_jie(year: int, month: int, day: int, hour: int = 0) -> Optional[datetime]:
    """获取上一个"节"的日期时间"""
    target_date = datetime(year, month, day, hour)
    
    years_to_check = [year + 1, year, year - 1, year - 2]
    all_jie = []
    for y in years_to_check:
        for i in range(24):
            term_name = TRADITIONAL_TERMS[i]
            if term_name in JIE_TERMS:
                term_date = get_solar_term_date(y, i)
                if term_date <= target_date:
                    all_jie.append((term_date, term_name))
    
    all_jie.sort(key=lambda x: x[0], reverse=True)
    return all_jie[0][0] if all_jie else None


def calculate_days_to_next_term(year: int, month: int, day: int, hour: int = 0) -> float:
    """计算从指定日期到下一个节气的天数"""
    target_date = datetime(year, month, day, hour)
    next_term_date = get_next_solar_term(year, month, day)
    if next_term_date:
        delta = next_term_date - target_date
        return max(0, delta.total_seconds() / 86400.0)
    return 0


def calculate_days_from_prev_term(year: int, month: int, day: int, hour: int = 0) -> float:
    """计算从上一个节气到指定日期的天数"""
    target_date = datetime(year, month, day, hour)
    prev_term_date = get_prev_solar_term(year, month, day)
    if prev_term_date:
        delta = target_date - prev_term_date
        return max(0, delta.total_seconds() / 86400.0)
    return 0


def print_year_solar_terms(year: int) -> None:
    """打印指定年份所有节气"""
    print(f"\n{year}年24节气（按时间顺序）：")
    print("=" * 60)
    terms = get_all_solar_terms_for_year(year)
    for term_name, term_idx, term_date in terms:
        print(f"{term_idx:2d}. {term_name}: {term_date.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    # 测试节气计算
    print_year_solar_terms(2024)
    
    # 测试月支计算
    test_cases = [
        (2024, 2, 3),   # 立春前（大寒）
        (2024, 2, 4),   # 立春
        (2024, 2, 5),   # 立春后
        (2024, 3, 5),   # 惊蛰附近
        (2024, 6, 5),   # 芒种附近
        (2024, 1, 6),   # 小寒附近
        (2024, 12, 22), # 冬至附近
    ]
    
    print("\n月支测试：")
    print("=" * 60)
    for year, month, day in test_cases:
        term_name, term_index = get_solar_term(year, month, day)
        month_zhi = get_month_zhi_by_solar_term(year, month, day)
        month_idx = get_month_index_by_solar_term(year, month, day)
        print(f"{year}-{month:02d}-{day:02d}: 节气[{term_index:2d}]={term_name}, 月支={month_zhi}, 月序={month_idx}")
