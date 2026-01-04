"""
紫微斗数格局分析Agent
"""
from typing import Dict, Any
import logging

from core.tools.ziwei_geju import analyze_geju_impact

logger = logging.getLogger(__name__)

def ziwei_geju_node(pan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格局分析节点
    
    Args:
        pan_data: 命盘数据
    
    Returns:
        格局分析结果
    """
    try:
        # 分析格局影响
        geju_analysis = analyze_geju_impact(pan_data)
        
        # 将格局数据添加到命盘
        pan_data['geju'] = geju_analysis
        
        result = {
            'geju_analysis': geju_analysis,
            'success': True,
        }
        
        logger.info("格局分析完成")
        return result
        
    except Exception as e:
        logger.error(f"格局分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


