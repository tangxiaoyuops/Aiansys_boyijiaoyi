"""
紫微斗数流年分析Agent
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.tools.ziwei_liunian import (
    get_current_liunian,
    calculate_liunian_pan,
    analyze_liunian_impact,
)

logger = logging.getLogger(__name__)

def ziwei_liunian_node(pan_data: Dict[str, Any], target_year: Optional[int] = None) -> Dict[str, Any]:
    """
    流年分析节点
    
    Args:
        pan_data: 命盘数据
        target_year: 目标年份（如果为None，使用当前年份）
    
    Returns:
        流年分析结果
    """
    try:
        if target_year is None:
            target_year = datetime.now().year
        
        # 计算流年命盘
        liunian_data = calculate_liunian_pan(target_year, pan_data)
        
        # 分析流年影响
        liunian_analysis = analyze_liunian_impact(pan_data, liunian_data)
        
        result = {
            'liunian_data': liunian_data,
            'liunian_analysis': liunian_analysis,
            'success': True,
        }
        
        logger.info(f"流年分析完成: {target_year}年")
        return result
        
    except Exception as e:
        logger.error(f"流年分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


