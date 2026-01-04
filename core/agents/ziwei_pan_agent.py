"""
紫微斗数排盘Agent
整合基础排盘和四化星计算
"""
from typing import Dict, Any
import logging
from datetime import datetime

from core.tools.ziwei_calculator import create_pan
from core.tools.ziwei_si_hua import apply_si_hua_to_pan, analyze_si_hua_impact

logger = logging.getLogger(__name__)

def ziwei_pan_node(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = '男'
) -> Dict[str, Any]:
    """
    紫微斗数排盘节点
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
    
    Returns:
        完整的命盘数据和分析结果
    """
    try:
        logger.info(f"开始排盘: {year}年{month}月{day}日{hour}时, 性别={gender}")
        
        # 1. 创建基础命盘
        pan_data = create_pan(year, month, day, hour, gender)
        
        # 2. 应用四化星
        year_gan = pan_data['birth_info']['year_gan']
        pan_data = apply_si_hua_to_pan(pan_data, year_gan)
        
        # 3. 分析四化星影响
        si_hua_analysis = analyze_si_hua_impact(pan_data)
        
        result = {
            'pan_data': pan_data,
            'si_hua_analysis': si_hua_analysis,
            'success': True,
        }
        
        logger.info("排盘完成")
        return result
        
    except Exception as e:
        logger.error(f"排盘失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


