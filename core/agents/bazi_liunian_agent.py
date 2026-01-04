"""
八字流年分析Agent
分析流年对命局的影响
"""
from typing import Dict, Any, Optional
import logging

from core.tools.bazi_calculator import calculate_liunian

logger = logging.getLogger(__name__)

def bazi_liunian_node(
    sizhu: Dict[str, Any],
    target_year: Optional[int] = None
) -> Dict[str, Any]:
    """
    流年分析节点
    
    Args:
        sizhu: 四柱数据
        target_year: 目标年份（如果为None，使用当前年份）
    
    Returns:
        流年分析结果
    """
    try:
        if target_year is None:
            from datetime import datetime
            target_year = datetime.now().year
        
        logger.info(f"开始流年分析: {target_year}年")
        
        # 计算流年
        liunian_data = calculate_liunian(sizhu, target_year)
        
        result = {
            'liunian_data': liunian_data,
            'success': True,
        }
        
        logger.info("流年分析完成")
        return result
        
    except Exception as e:
        logger.error(f"流年分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


