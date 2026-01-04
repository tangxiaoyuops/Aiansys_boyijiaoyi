"""
八字基础排盘Agent
计算四柱
"""
from typing import Dict, Any
import logging

from core.tools.bazi_calculator import calculate_sizhu

logger = logging.getLogger(__name__)

def bazi_pan_node(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = '男'
) -> Dict[str, Any]:
    """
    八字基础排盘节点
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
    
    Returns:
        基础排盘数据
    """
    try:
        logger.info(f"开始八字排盘: {year}年{month}月{day}日{hour}时, 性别={gender}")
        
        # 计算四柱
        sizhu = calculate_sizhu(year, month, day, hour)
        
        result = {
            'sizhu': sizhu,
            'success': True,
        }
        
        logger.info("八字排盘完成")
        return result
        
    except Exception as e:
        logger.error(f"八字排盘失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


