"""
八字大运分析Agent
分析大运对命局的影响
"""
from typing import Dict, Any, Optional
import logging

from core.tools.bazi_calculator import calculate_dayun

logger = logging.getLogger(__name__)

def bazi_dayun_node(
    sizhu: Dict[str, Any],
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str
) -> Dict[str, Any]:
    """
    大运分析节点
    
    Args:
        sizhu: 四柱数据（包含bazi_year字段）
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
    
    Returns:
        大运分析结果
    """
    try:
        logger.info("开始大运分析")
        
        # 从sizhu获取八字年份（以立春为界的年份）
        bazi_year = sizhu.get('bazi_year', year)
        
        # 计算大运（传入八字年份）
        dayun_list = calculate_dayun(year, month, day, hour, gender, bazi_year=bazi_year)
        
        result = {
            'dayun_list': dayun_list,
            'success': True,
        }
        
        logger.info("大运分析完成")
        return result
        
    except Exception as e:
        logger.error(f"大运分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }