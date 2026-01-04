"""
紫微斗数大限分析Agent
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.tools.ziwei_daxian import (
    determine_daxian_direction,
    calculate_all_daxian,
    get_current_daxian,
    analyze_daxian_impact,
)

logger = logging.getLogger(__name__)

def ziwei_daxian_node(pan_data: Dict[str, Any], current_year: Optional[int] = None) -> Dict[str, Any]:
    """
    大限分析节点
    
    Args:
        pan_data: 命盘数据
        current_year: 当前年份（如果为None，使用当前年份）
    
    Returns:
        大限分析结果
    """
    try:
        if current_year is None:
            current_year = datetime.now().year
        
        birth_info = pan_data.get('birth_info', {})
        year_gan = birth_info.get('year_gan', '')
        gender = birth_info.get('gender', '男')
        birth_year = birth_info.get('year', current_year)
        ming_gong = pan_data.get('ming_gong', 0)
        
        # 确定大限方向
        direction = determine_daxian_direction(year_gan, gender)
        
        # 计算所有大限
        all_daxian = calculate_all_daxian(ming_gong, direction)
        
        # 获取当前大限
        current_daxian = get_current_daxian(birth_year, current_year, ming_gong, direction)
        
        # 分析大限影响
        daxian_analysis = analyze_daxian_impact(pan_data, current_daxian)
        
        result = {
            'all_daxian': all_daxian,
            'current_daxian': current_daxian,
            'daxian_analysis': daxian_analysis,
            'success': True,
        }
        
        logger.info("大限分析完成")
        return result
        
    except Exception as e:
        logger.error(f"大限分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }

