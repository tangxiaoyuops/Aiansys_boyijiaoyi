"""
八字神煞分析Agent
分析各种神煞
"""
from typing import Dict, Any
import logging

from core.tools.bazi_calculator import calculate_shensha

logger = logging.getLogger(__name__)

def bazi_shensha_node(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    神煞分析节点
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        神煞分析结果
    """
    try:
        logger.info("开始神煞分析")
        
        # 计算神煞
        shensha_data = calculate_shensha(sizhu)
        
        result = {
            'shensha_data': shensha_data,
            'success': True,
        }
        
        logger.info("神煞分析完成")
        return result
        
    except Exception as e:
        logger.error(f"神煞分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


