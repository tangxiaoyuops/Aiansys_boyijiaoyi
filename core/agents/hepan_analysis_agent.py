"""
八字合盘分析Agent
整合两个命盘的分析，提供完整的合盘分析结果
"""
from typing import Dict, Any, Optional
import logging

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.agents.bazi_shensha_agent import bazi_shensha_node
from core.tools.hepan_calculator import calculate_hepan
from core.tools.llm_client import call_llm, call_llm_stream
from core.agents.bazi_prompt_styles import get_hepan_system_prompt, build_hepan_prompt as build_hepan_prompt_from_styles

logger = logging.getLogger(__name__)


def hepan_complete_analysis(
    # 命盘A参数
    year_a: int,
    month_a: int,
    day_a: int,
    hour_a: int,
    gender_a: str = '男',
    # 命盘B参数
    year_b: int = 1990,
    month_b: int = 1,
    day_b: int = 1,
    hour_b: int = 11,
    gender_b: str = '女',
    # 分析选项
    hepan_type: str = 'couple',
    include_llm: bool = True,
    analysis_style: str = 'emotion',  # 保留以兼容前端，但合盘分析使用hepan_type决定风格
    include_dayun: bool = True,
    include_shensha: bool = True,
) -> Dict[str, Any]:
    """
    完整的八字合盘分析
    
    Args:
        # 命盘A参数
        year_a: 命盘A公历年份
        month_a: 命盘A公历月份
        day_a: 命盘A公历日期
        hour_a: 命盘A时辰（0-23）
        gender_a: 命盘A性别
        
        # 命盘B参数
        year_b: 命盘B公历年份
        month_b: 命盘B公历月份
        day_b: 命盘B公历日期
        hour_b: 命盘B时辰（0-23）
        gender_b: 命盘B性别
        
        # 分析选项
        hepan_type: 合盘类型 ('couple' | 'business')
        include_llm: 是否包含LLM深度分析
        analysis_style: 分析风格
        include_dayun: 是否包含大运分析
        include_shensha: 是否包含神煞分析
    
    Returns:
        完整的合盘分析结果
    """
    try:
        print(f"[合盘分析] ========== 开始八字合盘分析 ==========")
        print(f"[合盘分析] 命盘A: {year_a}年{month_a}月{day_a}日{hour_a}时, 性别={gender_a}")
        print(f"[合盘分析] 命盘B: {year_b}年{month_b}月{day_b}日{hour_b}时, 性别={gender_b}")
        print(f"[合盘分析] 合盘类型: {hepan_type}")
        logger.info(f"开始合盘分析: A={year_a}/{month_a}/{day_a}, B={year_b}/{month_b}/{day_b}")
        
        # ========== 分析命盘A ==========
        print(f"[合盘分析] 分析命盘A...")
        pan_a = _analyze_single_pan(
            year_a, month_a, day_a, hour_a, gender_a,
            include_dayun=include_dayun,
            include_shensha=include_shensha
        )
        
        # ========== 分析命盘B ==========
        print(f"[合盘分析] 分析命盘B...")
        pan_b = _analyze_single_pan(
            year_b, month_b, day_b, hour_b, gender_b,
            include_dayun=include_dayun,
            include_shensha=include_shensha
        )
        
        # 检查排盘是否成功
        if not pan_a.get('success'):
            return {'success': False, 'error': f'命盘A分析失败: {pan_a.get("error", "未知错误")}'}
        if not pan_b.get('success'):
            return {'success': False, 'error': f'命盘B分析失败: {pan_b.get("error", "未知错误")}'}
        
        # ========== 合盘匹配分析 ==========
        print(f"[合盘分析] 计算合盘匹配度...")
        hepan_result = calculate_hepan(
            pan_a['sizhu'],
            pan_b['sizhu'],
            hepan_type=hepan_type,
            gender_a=gender_a,
            gender_b=gender_b
        )
        
        # ========== 构建结果 ==========
        result = {
            'success': True,
            'pan_a': pan_a,
            'pan_b': pan_b,
            'hepan': hepan_result,
            'hepan_type': hepan_type,
            'birth_info_a': {
                'year': year_a, 'month': month_a, 'day': day_a, 'hour': hour_a, 'gender': gender_a
            },
            'birth_info_b': {
                'year': year_b, 'month': month_b, 'day': day_b, 'hour': hour_b, 'gender': gender_b
            },
        }
        
        print(f"[合盘分析] 合盘分析完成，匹配度: {hepan_result['scores']['total']}分")
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"[合盘分析] 错误: {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': error_msg,
        }


def _analyze_single_pan(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str,
    include_dayun: bool = True,
    include_shensha: bool = True,
) -> Dict[str, Any]:
    """
    分析单个命盘
    """
    try:
        # 1. 基础排盘
        pan_result = bazi_pan_node(year, month, day, hour, gender)
        if not pan_result.get('success'):
            return pan_result
        
        sizhu = pan_result['sizhu']
        
        # 2. 五行分析
        wuxing_result = bazi_wuxing_node(sizhu)
        wuxing_analysis = wuxing_result if wuxing_result.get('success') else None
        
        # 3. 十神分析
        shishen_result = bazi_shishen_node(sizhu)
        shishen_analysis = shishen_result if shishen_result.get('success') else None
        
        # 4. 大运分析
        dayun_analysis = None
        if include_dayun:
            dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
            dayun_analysis = dayun_result if dayun_result.get('success') else None
        
        # 5. 神煞分析
        shensha_analysis = None
        if include_shensha:
            shensha_result = bazi_shensha_node(sizhu)
            shensha_analysis = shensha_result if shensha_result.get('success') else None
        
        return {
            'success': True,
            'sizhu': sizhu,
            'wuxing_analysis': wuxing_analysis,
            'shishen_analysis': shishen_analysis,
            'dayun_analysis': dayun_analysis,
            'shensha_analysis': shensha_analysis,
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def build_hepan_prompt(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple',
    name_a: Optional[str] = None,
    name_b: Optional[str] = None
) -> str:
    """
    构建合盘分析提示词（包装函数）
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配分析结果
        hepan_type: 合盘类型
        name_a: 命盘A姓名（可选）
        name_b: 命盘B姓名（可选）
    
    Returns:
        提示词字符串
    """
    return build_hepan_prompt_from_styles(pan_a, pan_b, hepan_result, hepan_type, name_a=name_a, name_b=name_b)


def hepan_llm_analysis(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple',
    name_a: Optional[str] = None,
    name_b: Optional[str] = None
) -> str:
    """
    使用LLM进行合盘深度分析（非流式）
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配结果
        hepan_type: 合盘类型
        name_a: 命盘A姓名（可选）
        name_b: 命盘B姓名（可选）
    
    Returns:
        LLM分析结果
    """
    system_prompt = get_hepan_system_prompt(hepan_type)
    user_prompt = build_hepan_prompt(pan_a, pan_b, hepan_result, hepan_type, name_a=name_a, name_b=name_b)
    
    try:
        return call_llm(system_prompt, user_prompt, temperature=0.3)
    except Exception as e:
        logger.error(f"合盘LLM分析失败: {e}")
        return f"分析失败: {str(e)}"


def hepan_llm_analysis_stream(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple',
    name_a: Optional[str] = None,
    name_b: Optional[str] = None
):
    """
    使用LLM进行合盘深度分析（流式）
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配结果
        hepan_type: 合盘类型
        name_a: 命盘A姓名（可选）
        name_b: 命盘B姓名（可选）
    
    Yields:
        LLM分析结果片段
    """
    system_prompt = get_hepan_system_prompt(hepan_type)
    user_prompt = build_hepan_prompt(pan_a, pan_b, hepan_result, hepan_type, name_a=name_a, name_b=name_b)
    
    try:
        for chunk in call_llm_stream(system_prompt, user_prompt, temperature=0.3):
            yield chunk
    except Exception as e:
        logger.error(f"合盘LLM流式分析失败: {e}")
        yield f"分析失败: {str(e)}"