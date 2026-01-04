"""
24节气计算模块
用于八字排盘中的月柱确定和大运起运年龄计算
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 24节气列表（按顺序）
SOLAR_TERMS = [
    '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
    '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
    '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
    '立冬', '小雪', '大雪', '冬至', '小寒', '大寒'
]

# 月支对应节气（以立春为正月开始）
# 立春-惊蛰=寅月(1)，惊蛰-清明=卯月(2)，以此类推
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

def get_solar_term_date(year: int, term_index: int) -> datetime:
    """
    计算指定年份的某个节气日期（简化算法）
    使用近似公式，实际应用中应使用精确的天文计算
    
    Args:
        year: 年份
        term_index: 节气索引（0-23，对应24个节气）
    
    Returns:
        节气的日期时间
    """
    # 立春大约在2月4日左右，每个节气间隔约15.2天
    base_date = datetime(year, 2, 4, 12, 0, 0)  # 立春基准日期（中午12点）
    
    # 每个节气约15.2184天（365.25/24）
    days_per_term = 365.25 / 24
    days_offset = term_index * days_per_term
    
    term_date = base_date + timedelta(days=days_offset)
    
    # 尝试使用更精确的方法（如果有zhdate库）
    try:
        # 这里可以集成更精确的节气计算
        # 目前使用简化公式
        pass
    except Exception:
        pass
    
    return term_date

def get_solar_term(year: int, month: int, day: int) -> Tuple[str, int]:
    """
    根据公历日期确定所在的节气
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        (节气名称, 节气索引)
    """
    target_date = datetime(year, month, day)
    
    # 查找最近的节气
    for i in range(24):
        term_name = SOLAR_TERMS[i]
        term_date = get_solar_term_date(year, i)
        
        # 下一个节气
        next_i = (i + 1) % 24
        next_year = year if next_i != 0 else year + 1
        next_term_date = get_solar_term_date(next_year, next_i)
        
        # 如果当前日期在某个节气之后，且在下个节气之前
        if term_date <= target_date < next_term_date:
            return term_name, i
    
    # 如果没找到（可能在年初），返回大寒
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
    """
    获取下一个节气的日期时间
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
    
    Returns:
        下一个节气的日期时间
    """
    term_name, term_index = get_solar_term(year, month, day)
    
    # 下一个节气
    next_term_index = (term_index + 1) % 24
    next_year = year if next_term_index != 0 else year + 1
    
    next_term_date = get_solar_term_date(next_year, next_term_index)
    
    return next_term_date

def calculate_days_to_next_term(year: int, month: int, day: int, hour: int = 0) -> float:
    """
    计算从指定日期到下一个节气的天数
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
    
    Returns:
        到下一个节气的天数（浮点数，包含小时）
    """
    target_date = datetime(year, month, day, hour)
    next_term_date = get_next_solar_term(year, month, day)
    
    delta = next_term_date - target_date
    days = delta.total_seconds() / 86400.0  # 转换为天数
    
    return max(0, days)  # 确保非负
