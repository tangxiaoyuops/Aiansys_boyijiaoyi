"""
八字完整分析Agent
整合所有分析模块，提供完整的分析结果
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.agents.bazi_liunian_agent import bazi_liunian_node
from core.agents.bazi_shensha_agent import bazi_shensha_node
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)

def bazi_complete_analysis(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = '男',
    include_wuxing: bool = True,
    include_shishen: bool = True,
    include_dayun: bool = True,
    include_liunian: bool = False,
    include_shensha: bool = True,
    include_llm: bool = False,
    target_year: Optional[int] = None,
    analysis_style: str = 'classic',
) -> Dict[str, Any]:
    """
    完整的八字分析
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
        include_wuxing: 是否包含五行分析
        include_shishen: 是否包含十神分析
        include_dayun: 是否包含大运分析
        include_liunian: 是否包含流年分析
        include_shensha: 是否包含神煞分析
        include_llm: 是否包含LLM深度分析
        target_year: 目标年份（用于流年分析）
        analysis_style: 分析风格（classic/simple/life_guide/business/emotion）
    
    Returns:
        完整的分析结果
    """
    try:
        print(f"[完整分析] ========== 开始八字完整分析 ==========")
        print(f"[完整分析] 参数: {year}年{month}月{day}日{hour}时, 性别={gender}")
        print(f"[完整分析] 分析风格: {analysis_style}")
        print(f"[完整分析] 分析选项: 五行={include_wuxing}, 十神={include_shishen}, 大运={include_dayun}, 流年={include_liunian}, 神煞={include_shensha}, LLM={include_llm}")
        logger.info(f"开始完整分析: {year}年{month}月{day}日{hour}时, 风格={analysis_style}")
        
        # 1. 基础排盘
        print(f"[完整分析] 步骤1: 开始基础排盘...")
        pan_result = bazi_pan_node(year, month, day, hour, gender)
        if not pan_result.get('success'):
            print(f"[完整分析] 步骤1失败: {pan_result.get('error', '未知错误')}")
            return pan_result
        print(f"[完整分析] 步骤1完成: 基础排盘成功")
        
        sizhu = pan_result['sizhu']
        
        # 2. 五行分析
        wuxing_analysis = None
        if include_wuxing:
            print(f"[完整分析] 步骤2: 开始五行分析...")
            wuxing_result = bazi_wuxing_node(sizhu)
            if wuxing_result.get('success'):
                wuxing_analysis = wuxing_result
                print(f"[完整分析] 步骤2完成: 五行分析成功")
            else:
                print(f"[完整分析] 步骤2失败: {wuxing_result.get('error', '未知错误')}")
        
        # 3. 十神分析
        shishen_analysis = None
        if include_shishen:
            print(f"[完整分析] 步骤3: 开始十神分析...")
            shishen_result = bazi_shishen_node(sizhu)
            if shishen_result.get('success'):
                shishen_analysis = shishen_result
                print(f"[完整分析] 步骤3完成: 十神分析成功")
            else:
                print(f"[完整分析] 步骤3失败: {shishen_result.get('error', '未知错误')}")
        
        # 4. 大运分析
        dayun_analysis = None
        if include_dayun:
            print(f"[完整分析] 步骤4: 开始大运分析...")
            dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
            if dayun_result.get('success'):
                dayun_analysis = dayun_result
                print(f"[完整分析] 步骤4完成: 大运分析成功")
            else:
                print(f"[完整分析] 步骤4失败: {dayun_result.get('error', '未知错误')}")
        
        # 5. 流年分析
        liunian_analysis = None
        if include_liunian:
            print(f"[完整分析] 步骤5: 开始流年分析...")
            liunian_result = bazi_liunian_node(sizhu, target_year)
            if liunian_result.get('success'):
                liunian_analysis = liunian_result
                print(f"[完整分析] 步骤5完成: 流年分析成功")
            else:
                print(f"[完整分析] 步骤5失败: {liunian_result.get('error', '未知错误')}")
        
        # 6. 神煞分析
        shensha_analysis = None
        if include_shensha:
            print(f"[完整分析] 步骤6: 开始神煞分析...")
            shensha_result = bazi_shensha_node(sizhu)
            if shensha_result.get('success'):
                shensha_analysis = shensha_result
                print(f"[完整分析] 步骤6完成: 神煞分析成功")
            else:
                print(f"[完整分析] 步骤6失败: {shensha_result.get('error', '未知错误')}")
        
        # 7. LLM深度分析
        llm_analysis = None
        if include_llm:
            print(f"[完整分析] 步骤7: 开始LLM深度分析...")
            try:
                llm_result = _build_llm_analysis(sizhu, wuxing_analysis, shishen_analysis, dayun_analysis, shensha_analysis, analysis_style)
                if llm_result.get('success'):
                    llm_analysis = llm_result
                    print(f"[完整分析] 步骤7完成: LLM深度分析成功")
                else:
                    print(f"[完整分析] 步骤7失败: {llm_result.get('error', '未知错误')}")
            except Exception as e:
                print(f"[完整分析] 步骤7异常: {e}")
                llm_analysis = {
                    'success': False,
                    'error': str(e),
                }
        
        # 构建最终结果
        result = {
            'success': True,
            'sizhu': sizhu,
            'wuxing_analysis': wuxing_analysis,
            'shishen_analysis': shishen_analysis,
            'dayun_analysis': dayun_analysis,
            'liunian_analysis': liunian_analysis,
            'shensha_analysis': shensha_analysis,
            'llm_analysis': llm_analysis,
        }
        
        print(f"[完整分析] ========== 分析完成 ==========")
        logger.info("完整分析完成")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"完整分析失败: {error_msg}", exc_info=True)
        print(f"[完整分析] 发生异常: {error_msg}")
        import traceback
        print(f"[完整分析] 异常堆栈:\n{traceback.format_exc()}")
        return {
            'success': False,
            'error': error_msg,
        }

def _build_llm_analysis(
    sizhu: Dict[str, Any],
    wuxing_analysis: Optional[Dict[str, Any]],
    shishen_analysis: Optional[Dict[str, Any]],
    dayun_analysis: Optional[Dict[str, Any]],
    shensha_analysis: Optional[Dict[str, Any]],
    analysis_style: str = 'classic'
) -> Dict[str, Any]:
    """
    构建LLM分析
    
    Args:
        sizhu: 四柱数据
        wuxing_analysis: 五行分析结果
        shishen_analysis: 十神分析结果
        dayun_analysis: 大运分析结果
        shensha_analysis: 神煞分析结果
        analysis_style: 分析风格
    
    Returns:
        LLM分析结果
    """
    try:
        from core.agents.bazi_prompt_styles import get_system_prompt, build_bazi_prompt
        
        system_prompt = get_system_prompt(analysis_style)
        user_prompt = build_bazi_prompt(sizhu, wuxing_analysis, shishen_analysis, dayun_analysis, shensha_analysis)
        
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.3)
        
        return {
            'success': True,
            'analysis': llm_response,
            'style': analysis_style,
        }
        
    except Exception as e:
        error_str = str(e)
        error_msg = error_str
        
        # 处理内容审核错误
        if 'inappropriate content' in error_str or 'data_inspection_failed' in error_str:
            error_msg = "内容审核未通过：模型认为输出内容可能包含不当内容。建议重新表述问题或关闭AI深度分析。"
        elif 'timeout' in error_str.lower() or 'timed out' in error_str.lower():
            error_msg = "请求超时：LLM响应时间过长，请稍后重试。"
        elif 'authentication' in error_str.lower() or 'unauthorized' in error_str.lower():
            error_msg = "认证失败：请检查API密钥配置。"
        elif 'rate limit' in error_str.lower():
            error_msg = "请求频率过高：请稍后重试。"
        
        logger.error(f"LLM解卦分析失败: {error_msg}")
        import traceback
        logger.debug(f"LLM解卦分析异常堆栈: {traceback.format_exc()}")
        
        return {
            'success': False,
            'error': error_msg,
        }


def _build_bazi_prompt(
    sizhu: Dict[str, Any],
    wuxing_analysis: Optional[Dict[str, Any]],
    shishen_analysis: Optional[Dict[str, Any]],
    dayun_analysis: Optional[Dict[str, Any]],
    shensha_analysis: Optional[Dict[str, Any]]
) -> str:
    """
    构建八字分析的提示词（已迁移到 bazi_prompt_styles.py）
    保留此函数以保持向后兼容
    """
    from core.agents.bazi_prompt_styles import build_bazi_prompt
    return build_bazi_prompt(sizhu, wuxing_analysis, shishen_analysis, dayun_analysis, shensha_analysis)


