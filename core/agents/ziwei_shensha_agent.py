"""
紫微斗数神煞分析Agent
"""
from typing import Dict, Any
import logging

from core.tools.ziwei_shensha import (
    calculate_all_shensha,
    analyze_shensha_impact,
)
from core.tools.ziwei_calculator import get_tian_gan, get_di_zhi

logger = logging.getLogger(__name__)

def ziwei_shensha_node(pan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    神煞分析节点
    
    Args:
        pan_data: 命盘数据
    
    Returns:
        神煞分析结果
    """
    try:
        birth_info = pan_data.get('birth_info', {})
        year = birth_info.get('year', 2000)
        year_gan = birth_info.get('year_gan', '')
        year_zhi = birth_info.get('year_zhi', '')
        
        # 计算日干（需要从农历日期计算，这里简化处理）
        # 实际应该从农历日期计算日干，这里先用年干作为示例
        day_gan = year_gan  # 简化：实际应该计算日干
        
        # 计算所有神煞
        shensha_data = calculate_all_shensha(year_gan, year_zhi, day_gan)
        
        # 分析神煞影响
        shensha_analysis = analyze_shensha_impact(pan_data, shensha_data)
        
        # 将神煞数据添加到命盘
        pan_data['shensha'] = shensha_data
        
        result = {
            'shensha_data': shensha_data,
            'shensha_analysis': shensha_analysis,
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


