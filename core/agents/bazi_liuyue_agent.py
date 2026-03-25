"""
八字流月分析Agent
分析未来月份的运势走向
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

from core.tools.bazi_calculator import calculate_liuyue_list

logger = logging.getLogger(__name__)


def bazi_liuyue_analysis(
    sizhu: Dict[str, Any],
    months_count: int = 6,
    birth_year: Optional[int] = None,
    gender: str = '男',
    wuxing_analysis: Optional[Dict[str, Any]] = None,
    include_llm: bool = True,
    analysis_style: str = 'classic',
) -> Dict[str, Any]:
    """
    流月推演分析
    
    Args:
        sizhu: 四柱数据
        months_count: 推演月数（默认6个月）
        birth_year: 出生年份（用于确定当前大运）
        gender: 性别
        wuxing_analysis: 五行分析结果
        include_llm: 是否包含LLM深度分析
        analysis_style: 分析风格
    
    Returns:
        流月分析结果
    """
    try:
        logger.info(f"开始流月推演分析: 推演{months_count}个月")
        
        # 获取当前时间
        now = datetime.now()
        start_year = now.year
        start_month = now.month
        
        # 计算流月列表
        result = calculate_liuyue_list(
            sizhu=sizhu,
            start_year=start_year,
            start_month=start_month,
            months_count=months_count,
            birth_year=birth_year,
            gender=gender,
            wuxing_analysis=wuxing_analysis,
        )
        
        # LLM深度分析
        if include_llm and result.get('liuyue_list'):
            try:
                llm_result = _build_liuyue_llm_analysis(
                    sizhu=sizhu,
                    liuyue_result=result,
                    analysis_style=analysis_style,
                )
                if llm_result.get('success'):
                    result['llm_analysis'] = llm_result.get('analysis', '')
                else:
                    result['llm_analysis_error'] = llm_result.get('error', 'LLM分析失败')
            except Exception as e:
                logger.error(f"LLM流月分析异常: {e}")
                result['llm_analysis_error'] = str(e)
        
        result['current_year'] = start_year
        result['current_month'] = start_month
        
        logger.info(f"流月推演分析完成: {len(result.get('liuyue_list', []))}个月")
        return result
        
    except Exception as e:
        logger.error(f"流月分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


def _build_liuyue_llm_analysis(
    sizhu: Dict[str, Any],
    liuyue_result: Dict[str, Any],
    analysis_style: str = 'classic',
) -> Dict[str, Any]:
    """
    构建流月LLM分析
    
    Args:
        sizhu: 四柱数据
        liuyue_result: 流月计算结果
        analysis_style: 分析风格
    
    Returns:
        LLM分析结果
    """
    try:
        from core.agents.bazi_prompt_styles import get_system_prompt
        from core.tools.llm_client import call_llm
        
        system_prompt = get_system_prompt(analysis_style)
        user_prompt = _build_liuyue_prompt(sizhu, liuyue_result)
        
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.3)
        
        return {
            'success': True,
            'analysis': llm_response,
            'style': analysis_style,
        }
        
    except Exception as e:
        error_str = str(e)
        error_msg = error_str
        
        if 'inappropriate content' in error_str or 'data_inspection_failed' in error_str:
            error_msg = "内容审核未通过，建议重新尝试。"
        elif 'timeout' in error_str.lower() or 'timed out' in error_str.lower():
            error_msg = "请求超时，请稍后重试。"
        
        logger.error(f"LLM流月分析失败: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
        }


def _build_liuyue_prompt(sizhu: Dict[str, Any], liuyue_result: Dict[str, Any]) -> str:
    """
    构建流月分析提示词
    
    Args:
        sizhu: 四柱数据
        liuyue_result: 流月计算结果
    
    Returns:
        提示词字符串
    """
    rizhu_gan = sizhu.get('ri_zhu_tiangan', '')
    rizhu_zhi = sizhu.get('ri_zhu', {}).get('di_zhi', '')
    
    # 五行喜忌
    wuxing_xi_ji = liuyue_result.get('wuxing_xi_ji', {})
    xi_wuxing = wuxing_xi_ji.get('xi_wuxing', [])
    ji_wuxing = wuxing_xi_ji.get('ji_wuxing', [])
    is_rizhu_qiang = wuxing_xi_ji.get('is_rizhu_qiang', False)
    
    # 当前大运
    current_dayun = liuyue_result.get('current_dayun', {})
    
    prompt_parts = [
        "## 流月推演分析",
        "",
        "### 命主基本信息",
        f"- 日主：{rizhu_gan}{rizhu_zhi}",
        f"- 五行分析：日主{'偏强' if is_rizhu_qiang else '偏弱'}，喜{','.join(xi_wuxing) if xi_wuxing else '暂无'}，忌{','.join(ji_wuxing) if ji_wuxing else '暂无'}",
    ]
    
    if current_dayun:
        prompt_parts.append(f"- 当前大运：{current_dayun.get('gan', '')}{current_dayun.get('zhi', '')} ({current_dayun.get('start_age', 0)}-{current_dayun.get('end_age', 0)}岁)")
    
    prompt_parts.append("")
    prompt_parts.append("### 流月详情")
    prompt_parts.append("")
    
    liuyue_list = liuyue_result.get('liuyue_list', [])
    for liuyue in liuyue_list:
        year = liuyue.get('year', '')
        month = liuyue.get('month', '')
        gan_zhi = liuyue.get('gan_zhi', '')
        shishen = liuyue.get('shishen_to_rizhu', {})
        auspicious = liuyue.get('auspicious', {})
        level = auspicious.get('level', '平') if auspicious else '平'
        score = auspicious.get('score', 50) if auspicious else 50
        suggestions = auspicious.get('suggestions', []) if auspicious else []
        
        prompt_parts.append(f"#### {year}年{month}月（{gan_zhi}）")
        prompt_parts.append(f"- 十神关系：天干{shishen.get('gan_shishen', '')}，地支{shishen.get('zhi_shishen', '')}")
        prompt_parts.append(f"- 吉凶评级：{level}（{score}分）")
        if suggestions:
            for sug in suggestions[:2]:
                prompt_parts.append(f"  - {sug}")
        prompt_parts.append("")
    
    prompt_parts.extend([
        "### 分析要求",
        "",
        "请根据以上信息，提供以下分析：",
        "",
        "1. **整体运势概述**：概述未来几个月的整体运势走向。",
        "",
        "2. **月份详细解读**：",
        "   - 重点解读吉凶评级为\"大吉\"或\"大凶\"的月份",
        "   - 分析这些月份的主要特点和注意事项",
        "   - 结合十神关系提示财运、感情、事业方面的提示",
        "",
        "3. **建议与注意事项**：",
        "   - 针对有利月份给出把握建议",
        "   - 针对不利月份给出化解方案",
        "",
        "**特别提醒**：请用通俗易通的语言进行分析，避免过度专业术语，注重实用性和可操作性。",
    ])
    
    return "\n".join(prompt_parts)


def bazi_liuyue_stream_analysis(
    sizhu: Dict[str, Any],
    months_count: int = 6,
    birth_year: Optional[int] = None,
    gender: str = '男',
    wuxing_analysis: Optional[Dict[str, Any]] = None,
    analysis_style: str = 'classic',
):
    """
    流月推演流式分析（同步生成器）
    
    Args:
        sizhu: 四柱数据
        months_count: 推演月数
        birth_year: 出生年份
        gender: 性别
        wuxing_analysis: 五行分析结果
        analysis_style: 分析风格
    
    Yields:
        流式输出的数据块（SSE格式）
    """
    from core.agents.bazi_prompt_styles import get_system_prompt
    from core.tools.llm_client import call_llm_stream
    
    # 获取当前时间
    now = datetime.now()
    start_year = now.year
    start_month = now.month
    
    # 计算流月列表
    result = calculate_liuyue_list(
        sizhu=sizhu,
        start_year=start_year,
        start_month=start_month,
        months_count=months_count,
        birth_year=birth_year,
        gender=gender,
        wuxing_analysis=wuxing_analysis,
    )
    
    if not result.get('success'):
        yield f"data: {json.dumps({'error': result.get('error', '计算失败')}, ensure_ascii=False)}\n\n"
        return
    
    # 先返回基础数据
    base_data = {
        'type': 'base',
        'liuyue_list': result.get('liuyue_list', []),
        'wuxing_xi_ji': result.get('wuxing_xi_ji', {}),
        'current_dayun': result.get('current_dayun'),
        'current_year': start_year,
        'current_month': start_month,
    }
    yield f"data: {json.dumps(base_data, ensure_ascii=False)}\n\n"
    
    # LLM流式分析
    system_prompt = get_system_prompt(analysis_style)
    user_prompt = _build_liuyue_prompt(sizhu, result)
    
    full_analysis = []
    for chunk in call_llm_stream(system_prompt, user_prompt):
        full_analysis.append(chunk)
        llm_data = {'type': 'llm_chunk', 'chunk': chunk}
        yield f"data: {json.dumps(llm_data, ensure_ascii=False)}\n\n"
    
    # 返回完成信号
    complete_data = {
        'type': 'complete',
        'llm_analysis': ''.join(full_analysis),
    }
    yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"


def get_liuyue_summary(liuyue_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取流月摘要信息
    
    Args:
        liuyue_result: 流月分析结果
    
    Returns:
        摘要信息
    """
    liuyue_list = liuyue_result.get('liuyue_list', [])
    
    if not liuyue_list:
        return {'total': 0}
    
    ji_count = 0
    xiong_count = 0
    ping_count = 0
    best_month = None
    worst_month = None
    best_score = 0
    worst_score = 100
    
    for liuyue in liuyue_list:
        auspicious = liuyue.get('auspicious', {})
        if not auspicious:
            continue
            
        level = auspicious.get('level', '平')
        score = auspicious.get('score', 50)
        
        if level in ['大吉', '中吉']:
            ji_count += 1
        elif level in ['中凶', '大凶']:
            xiong_count += 1
        else:
            ping_count += 1
        
        if score > best_score:
            best_score = score
            best_month = liuyue
        if score < worst_score:
            worst_score = score
            worst_month = liuyue
    
    return {
        'total': len(liuyue_list),
        'ji_count': ji_count,
        'xiong_count': xiong_count,
        'ping_count': ping_count,
        'best_month': best_month,
        'worst_month': worst_month,
    }