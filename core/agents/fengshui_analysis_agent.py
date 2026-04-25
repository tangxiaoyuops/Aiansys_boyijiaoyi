"""
风水完整分析Agent
整合所有风水分析模块，提供完整的分析结果
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from core.agents.fengshui_orientation_agent import fengshui_orientation_analysis
from core.agents.fengshui_layout_agent import fengshui_layout_analysis
from core.agents.fengshui_room_agent import fengshui_room_analysis
from core.agents.fengshui_desk_agent import fengshui_desk_analysis
from core.tools.fengshui_calculator import (
    calculate_bazhai_mingua,
    calculate_yearly_feixing,
    fengshui_calculate,
)

logger = logging.getLogger(__name__)


def fengshui_complete_analysis(
    birth_year: int,
    gender: str,
    house_info: Dict[str, Any],
    include_layout: bool = True,
    include_orientation: bool = True,
    include_room: bool = True,
    include_desk: bool = True,
    include_llm: bool = False,
    analysis_style: str = 'classic',
) -> Dict[str, Any]:
    """
    完整风水布局分析
    组合调用各子Agent，返回统一结构
    
    Args:
        birth_year: 出生年份（公历）
        gender: 性别（'男' 或 '女'）
        house_info: 房屋基本信息
            - house_shape: 房屋形状
            - house_direction: 房屋朝向
            - construction_year: 建造年份（可选）
            - room_layout: 房间布局（可选）
            - room_types: 需要定位的房间类型（可选）
            - occupation_type: 职业类型（可选）
            - room_size: 房间尺寸（可选）
        include_layout: 是否包含格局分析
        include_orientation: 是否包含朝向分析
        include_room: 是否包含房间定位
        include_desk: 是否包含工位分析
        include_llm: 是否包含LLM深度分析
        analysis_style: 分析风格
    
    Returns:
        完整分析结果
    """
    try:
        logger.info(f"开始风水完整分析: 出生{birth_year}年, 性别{gender}")
        print(f"[风水分析] ========== 开始风水完整分析 ==========")
        print(f"[风水分析] 参数: 出生{birth_year}年, 性别{gender}")
        
        house_shape = house_info.get('house_shape', '矩形')
        house_direction = house_info.get('house_direction', '子')
        construction_year = house_info.get('construction_year')
        room_layout = house_info.get('room_layout', {})
        room_types = house_info.get('room_types', ['主卧', '书房', '客厅', '厨房', '卫生间'])
        occupation_type = house_info.get('occupation_type', '管理')
        room_size = house_info.get('room_size')
        
        result = {
            'success': True,
            'birth_year': birth_year,
            'gender': gender,
            'house_info': house_info,
            'analysis_time': datetime.now().isoformat(),
        }
        
        print(f"[风水分析] 步骤1: 计算命卦...")
        mingua_result = calculate_bazhai_mingua(birth_year, gender)
        if mingua_result.get('success'):
            result['mingua'] = mingua_result
            print(f"[风水分析] 命卦: {mingua_result.get('mingua')}, {mingua_result.get('dong_si_xi_si')}")
        else:
            result['mingua_error'] = mingua_result.get('error', '命卦计算失败')
        
        if include_orientation:
            print(f"[风水分析] 步骤2: 朝向分析...")
            orientation_result = fengshui_orientation_analysis(
                birth_year=birth_year,
                gender=gender,
                house_direction=house_direction,
                include_bazhai=True,
                include_xuankong=construction_year is not None,
                construction_year=construction_year,
            )
            result['orientation_analysis'] = orientation_result
            print(f"[风水分析] 朝向评分: {orientation_result.get('orientation_score', 'N/A')}")
        
        if include_layout:
            print(f"[风水分析] 步骤3: 格局分析...")
            layout_result = fengshui_layout_analysis(
                house_shape=house_shape,
                house_direction=house_direction,
                room_layout=room_layout,
                include_defect_analysis=True,
                include_liuxian=True,
            )
            result['layout_analysis'] = layout_result
            print(f"[风水分析] 格局评分: {layout_result.get('layout_score', 'N/A')}")
        
        if include_room and mingua_result.get('success'):
            print(f"[风水分析] 步骤4: 房间定位...")
            room_result = fengshui_room_analysis(
                house_layout=room_layout,
                mingua=mingua_result['mingua'],
                room_types=room_types,
                include_feixing=construction_year is not None,
            )
            result['room_analysis'] = room_result
            print(f"[风水分析] 房间定位完成")
        
        if include_desk and mingua_result.get('success'):
            print(f"[风水分析] 步骤5: 工位分析...")
            desk_result = fengshui_desk_analysis(
                room_direction=house_direction,
                mingua=mingua_result['mingua'],
                occupation_type=occupation_type,
                room_size=room_size,
            )
            result['desk_analysis'] = desk_result
            print(f"[风水分析] 工位分析完成")
        
        current_year = datetime.now().year
        yearly_feixing = calculate_yearly_feixing(current_year)
        if yearly_feixing.get('success'):
            result['yearly_feixing'] = yearly_feixing
        
        result['overall_score'] = _calculate_overall_score(result)
        result['summary'] = _generate_summary(result)
        result['recommendations'] = _generate_recommendations(result)
        
        if include_llm:
            print(f"[风水分析] 步骤6: LLM深度分析...")
            try:
                llm_result = _build_llm_analysis(result, analysis_style)
                result['llm_analysis'] = llm_result
            except Exception as e:
                logger.error(f"LLM分析失败: {e}")
                result['llm_analysis'] = {
                    'success': False,
                    'error': str(e),
                }
        
        print(f"[风水分析] ========== 分析完成 ==========")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"风水完整分析失败: {error_msg}", exc_info=True)
        print(f"[风水分析] 发生异常: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
        }


def _calculate_overall_score(result: Dict) -> float:
    """
    计算综合评分
    """
    scores = []
    weights = []
    
    if 'orientation_analysis' in result:
        orientation_score = result['orientation_analysis'].get('orientation_score', 50)
        scores.append(orientation_score)
        weights.append(0.35)
    
    if 'layout_analysis' in result:
        layout_score = result['layout_analysis'].get('layout_score', 75)
        scores.append(layout_score)
        weights.append(0.30)
    
    if 'room_analysis' in result:
        room_score = 70
        room_positions = result['room_analysis'].get('room_positions', {})
        if room_positions:
            matched = sum(1 for pos in room_positions.values() if pos.get('gua'))
            room_score = min(100, 50 + matched * 10)
        scores.append(room_score)
        weights.append(0.20)
    
    if 'desk_analysis' in result:
        desk_score = 70
        if result['desk_analysis'].get('desk_position', {}).get('area'):
            desk_score = 80
        scores.append(desk_score)
        weights.append(0.15)
    
    if not scores:
        return 60.0
    
    total_weight = sum(weights)
    weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
    
    return round(weighted_score, 1)


def _generate_summary(result: Dict) -> Dict[str, Any]:
    """
    生成分析摘要
    """
    summary = {
        'overall_level': '',
        'key_points': [],
        'warnings': [],
    }
    
    overall_score = result.get('overall_score', 60)
    if overall_score >= 85:
        summary['overall_level'] = '优秀'
    elif overall_score >= 70:
        summary['overall_level'] = '良好'
    elif overall_score >= 50:
        summary['overall_level'] = '一般'
    else:
        summary['overall_level'] = '需改善'
    
    if 'mingua' in result:
        mingua = result['mingua'].get('mingua', '')
        dong_xi = result['mingua'].get('dong_si_xi_si', '')
        summary['key_points'].append(f"命卦为{mingua}，属于{dong_xi}")
    
    if 'orientation_analysis' in result:
        orientation = result['orientation_analysis']
        level = orientation.get('orientation_level', '')
        position_type = orientation.get('orientation_analysis', {}).get('position_type', '')
        summary['key_points'].append(f"房屋朝向适配度{level}，属于{position_type}位")
    
    if 'layout_analysis' in result:
        layout = result['layout_analysis']
        score = layout.get('layout_score', 75)
        defects = layout.get('defects', [])
        if defects:
            summary['warnings'].append(f"存在{len(defects)}处格局问题")
        summary['key_points'].append(f"格局评分{score}分")
    
    return summary


def _generate_recommendations(result: Dict) -> List[str]:
    """
    生成综合建议
    """
    recommendations = []
    
    if 'orientation_analysis' in result:
        suggestions = result['orientation_analysis'].get('orientation_suggestions', [])
        recommendations.extend(suggestions[:2])
    
    if 'layout_analysis' in result:
        suggestions = result['layout_analysis'].get('suggestions', [])
        recommendations.extend(suggestions[:2])
    
    if 'room_analysis' in result:
        room_recs = result['room_analysis'].get('room_recommendations', [])
        recommendations.extend(room_recs[:2])
    
    if 'desk_analysis' in result:
        suggestions = result['desk_analysis'].get('layout_suggestions', [])
        recommendations.extend(suggestions[:2])
    
    if not recommendations:
        recommendations.append("当前风水格局良好，建议保持现有布局")
    
    return recommendations[:8]


def _build_llm_analysis(result: Dict, analysis_style: str) -> Dict[str, Any]:
    """
    构建LLM分析
    """
    try:
        from core.tools.llm_client import call_llm
        from core.agents.fengshui_prompt_styles import get_fengshui_prompt
        
        system_prompt, user_prompt = get_fengshui_prompt(result, analysis_style)
        
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.5)
        
        return {
            'success': True,
            'analysis': llm_response,
            'style': analysis_style,
        }
        
    except ImportError:
        logger.warning("LLM客户端未找到，跳过LLM分析")
        return {
            'success': False,
            'error': 'LLM客户端未配置',
        }
    except Exception as e:
        logger.error(f"LLM分析失败: {e}")
        return {
            'success': False,
            'error': str(e),
        }
