"""
八字五行分析Agent
分析五行分布和强弱
"""
from typing import Dict, Any
import logging

from core.tools.bazi_calculator import calculate_wuxing

logger = logging.getLogger(__name__)

def bazi_wuxing_node(sizhu: Dict[str, Any]) -> Dict[str, Any]:
    """
    五行分析节点
    
    Args:
        sizhu: 四柱数据
    
    Returns:
        五行分析结果
    """
    try:
        logger.info("开始五行分析")
        
        # 计算五行
        wuxing_data = calculate_wuxing(sizhu)
        
        # 分析五行强弱
        rizhu_wuxing = wuxing_data.get('rizhu_wuxing', '')
        wuxing_count = wuxing_data.get('wuxing_count', {})
        
        # 计算日主五行数量
        rizhu_count = wuxing_count.get(rizhu_wuxing, 0)
        
        # 分析五行平衡
        total = sum(wuxing_count.values())
        balance_analysis = []
        if total > 0:
            for wuxing, count in wuxing_count.items():
                percentage = (count / total) * 100
                balance_analysis.append({
                    'wuxing': wuxing,
                    'count': count,
                    'percentage': round(percentage, 1),
                })
        
        result = {
            'wuxing_data': wuxing_data,
            'rizhu_count': rizhu_count,
            'balance_analysis': balance_analysis,
            'success': True,
        }
        
        logger.info("五行分析完成")
        return result
        
    except Exception as e:
        logger.error(f"五行分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


