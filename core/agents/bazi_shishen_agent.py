"""
八字十神分析Agent
分析十神关系和分布
"""
from typing import Dict, Any
import logging

from core.tools.bazi_calculator import calculate_shishen

logger = logging.getLogger(__name__)

def bazi_shishen_node(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    十神分析节点
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        十神分析结果
    """
    try:
        logger.info("开始十神分析")
        
        rizhu_tiangan = sizhu.get('ri_zhu_tiangan', '')
        
        # 计算十神
        shishen_data = calculate_shishen(sizhu, rizhu_tiangan)
        
        # 统计十神分布
        shishen_count = {}
        for zhu_name, shishen_info in shishen_data.items():
            gan_shishen = shishen_info.get('gan_shishen', '')
            zhi_shishen = shishen_info.get('zhi_shishen', '')
            
            if gan_shishen and gan_shishen != '日主':
                shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
            if zhi_shishen:
                shishen_count[zhi_shishen] = shishen_count.get(zhi_shishen, 0) + 1
        
        result = {
            'shishen_data': shishen_data,
            'shishen_count': shishen_count,
            'success': True,
        }
        
        logger.info("十神分析完成")
        return result
        
    except Exception as e:
        logger.error(f"十神分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


