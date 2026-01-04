"""
紫微斗数流月分析Agent
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.tools.ziwei_liuyue import (
    get_current_liuyue,
    calculate_liuyue_pan,
    analyze_liuyue_impact,
)
from core.tools.ziwei_liunian import get_tian_gan

logger = logging.getLogger(__name__)

def ziwei_liuyue_node(
    pan_data: Dict[str, Any],
    target_year: Optional[int] = None,
    target_month: Optional[int] = None
) -> Dict[str, Any]:
    """
    流月分析节点
    
    Args:
        pan_data: 命盘数据
        target_year: 目标年份（如果为None，使用当前年份）
        target_month: 目标月份（如果为None，使用当前月份，农历月份）
    
    Returns:
        流月分析结果
    """
    try:
        if target_year is None:
            target_year = datetime.now().year
        if target_month is None:
            target_month = datetime.now().month
        
        # 获取流年天干
        liunian_gan = get_tian_gan(target_year)
        
        # 计算流月命盘
        liuyue_data = calculate_liuyue_pan(liunian_gan, target_month)
        
        # 分析流月影响
        liuyue_analysis = analyze_liuyue_impact(pan_data, liuyue_data)
        
        result = {
            'liuyue_data': liuyue_data,
            'liuyue_analysis': liuyue_analysis,
            'success': True,
        }
        
        logger.info(f"流月分析完成: {target_year}年{target_month}月")
        return result
        
    except Exception as e:
        logger.error(f"流月分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


