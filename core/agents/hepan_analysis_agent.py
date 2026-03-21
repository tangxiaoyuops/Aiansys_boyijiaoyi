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

logger = logging.getLogger(__name__)


def hepan_complete_analysis(
    # 命盘A参数
    year_a: int,
    month_a: int,
    day_a: int,
    hour_a: int,
    gender_a: str = '男',
    # 命盘B参数
    year_b: int,
    month_b: int,
    day_b: int,
    hour_b: int,
    gender_b: str = '女',
    # 分析选项
    hepan_type: str = 'couple',
    include_llm: bool = True,
    analysis_style: str = 'emotion',
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
    hepan_type: str = 'couple'
) -> str:
    """
    构建合盘分析提示词
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配分析结果
        hepan_type: 合盘类型
    
    Returns:
        提示词字符串
    """
    lines = ["## 八字合盘分析信息\n"]
    
    # 命盘A信息
    lines.append("### 命盘A")
    sizhu_a = pan_a.get('sizhu', {})
    lines.append(f"四柱: {sizhu_a.get('nian_zhu', {}).get('tian_gan', '')}{sizhu_a.get('nian_zhu', {}).get('di_zhi', '')}年 "
                f"{sizhu_a.get('yue_zhu', {}).get('tian_gan', '')}{sizhu_a.get('yue_zhu', {}).get('di_zhi', '')}月 "
                f"{sizhu_a.get('ri_zhu', {}).get('tian_gan', '')}{sizhu_a.get('ri_zhu', {}).get('di_zhi', '')}日 "
                f"{sizhu_a.get('shi_zhu', {}).get('tian_gan', '')}{sizhu_a.get('shi_zhu', {}).get('di_zhi', '')}时")
    lines.append(f"日主: {sizhu_a.get('ri_zhu_tiangan', '')}")
    lines.append(f"性别: {hepan_result.get('gender_a', '男')}")
    if sizhu_a.get('lunar_year'):
        lines.append(f"农历: {sizhu_a.get('lunar_year')}年{sizhu_a.get('lunar_month')}月{sizhu_a.get('lunar_day')}日")
    lines.append("")
    
    # 命盘B信息
    lines.append("### 命盘B")
    sizhu_b = pan_b.get('sizhu', {})
    lines.append(f"四柱: {sizhu_b.get('nian_zhu', {}).get('tian_gan', '')}{sizhu_b.get('nian_zhu', {}).get('di_zhi', '')}年 "
                f"{sizhu_b.get('yue_zhu', {}).get('tian_gan', '')}{sizhu_b.get('yue_zhu', {}).get('di_zhi', '')}月 "
                f"{sizhu_b.get('ri_zhu', {}).get('tian_gan', '')}{sizhu_b.get('ri_zhu', {}).get('di_zhi', '')}日 "
                f"{sizhu_b.get('shi_zhu', {}).get('tian_gan', '')}{sizhu_b.get('shi_zhu', {}).get('di_zhi', '')}时")
    lines.append(f"日主: {sizhu_b.get('ri_zhu_tiangan', '')}")
    lines.append(f"性别: {hepan_result.get('gender_b', '女')}")
    if sizhu_b.get('lunar_year'):
        lines.append(f"农历: {sizhu_b.get('lunar_year')}年{sizhu_b.get('lunar_month')}月{sizhu_b.get('lunar_day')}日")
    lines.append("")
    
    # 合盘匹配结果
    lines.append("### 合盘匹配分析")
    scores = hepan_result.get('scores', {})
    lines.append(f"**总评分: {scores.get('total', 0)}分 ({scores.get('grade', '')})**")
    lines.append(f"- 地支匹配: {scores.get('di_zhi', 0)}分 - {scores.get('di_zhi_desc', '')}")
    lines.append(f"- 五行互补: {scores.get('wuxing', 0)}分 - {scores.get('wuxing_desc', '')}")
    lines.append(f"- 日主关系: {scores.get('rizhu', 0)}分 - {scores.get('rizhu_desc', '')}")
    lines.append(f"- 天干合化: {scores.get('tian_gan', 0)}分 - {scores.get('tian_gan_desc', '')}")
    lines.append("")
    
    # 地支关系详情
    di_zhi = hepan_result.get('di_zhi_relation', {})
    if di_zhi.get('liu_he'):
        lines.append("**地支六合:**")
        for he in di_zhi['liu_he']:
            lines.append(f"- {he['desc']}")
    if di_zhi.get('liu_chong'):
        lines.append("**地支六冲:**")
        for chong in di_zhi['liu_chong']:
            lines.append(f"- {chong['desc']}")
    lines.append("")
    
    # 日主关系详情
    rizhu = hepan_result.get('rizhu_relation', {})
    if rizhu.get('relations'):
        lines.append("**日主关系:**")
        for rel in rizhu['relations']:
            lines.append(f"- {rel['desc']}")
    lines.append("")
    
    # 五行互补详情
    wuxing = hepan_result.get('wuxing_match', {})
    lines.append("**五行分布:**")
    lines.append(f"- 命盘A: 金{wuxing.get('wuxing_a', {}).get('金', 0)} 木{wuxing.get('wuxing_a', {}).get('木', 0)} "
                f"水{wuxing.get('wuxing_a', {}).get('水', 0)} 火{wuxing.get('wuxing_a', {}).get('火', 0)} "
                f"土{wuxing.get('wuxing_a', {}).get('土', 0)}")
    lines.append(f"- 命盘B: 金{wuxing.get('wuxing_b', {}).get('金', 0)} 木{wuxing.get('wuxing_b', {}).get('木', 0)} "
                f"水{wuxing.get('wuxing_b', {}).get('水', 0)} 火{wuxing.get('wuxing_b', {}).get('火', 0)} "
                f"土{wuxing.get('wuxing_b', {}).get('土', 0)}")
    if wuxing.get('complement'):
        lines.append("- 互补: " + ", ".join([c['desc'] for c in wuxing['complement']]))
    lines.append("")
    
    # 建议
    if hepan_result.get('suggestions'):
        lines.append("**系统建议:**")
        for sug in hepan_result['suggestions'][:5]:
            lines.append(f"- {sug}")
        lines.append("")
    
    lines.append("---")
    if hepan_type == 'couple':
        lines.append("请根据以上信息，进行专业的八字合婚分析，重点分析婚姻和谐度、性格互补、未来发展等。")
    else:
        lines.append("请根据以上信息，进行专业的商业合盘分析，重点分析合作契合度、财运互补、决策风格等。")
    
    return "\n".join(lines)


def get_hepan_system_prompt(hepan_type: str = 'couple') -> str:
    """
    获取合盘分析的系统提示词
    
    Args:
        hepan_type: 合盘类型
    
    Returns:
        系统提示词
    """
    if hepan_type == 'couple':
        return """你是一位精通传统命理学的专业合婚分析师，拥有深厚的理论功底和丰富的实战经验。

请按照以下专业框架进行合婚分析：

## 一、命盘概览
- 双方四柱结构对比
- 日主五行分析

## 二、合盘匹配分析
- 地支六合六冲解读
- 天干合化影响
- 五行互补情况
- 日主关系详解

## 三、婚姻运势分析
- 感情契合度
- 性格互补性
- 沟通与相处
- 家庭关系

## 四、发展建议
- 优势与机遇
- 需要注意的问题
- 趋吉避凶建议

请使用专业术语，但需解释其含义。分析要全面深入，逻辑清晰，给出实用的建议。"""
    
    else:  # business
        return """你是一位精通商业命理的专业顾问，擅长分析合作伙伴之间的命盘契合度。

请按照以下专业框架进行商业合盘分析：

## 一、命盘概览
- 双方四柱结构对比
- 日主五行分析

## 二、合作契合度分析
- 性格匹配度
- 决策风格对比
- 风险承受能力
- 五行互补情况

## 三、财运分析
- 各自财运特点
- 合财可能性
- 投资风格差异

## 四、合作建议
- 优势互补点
- 需要注意的问题
- 最佳合作方式
- 趋吉避凶建议

请使用专业术语，但需解释其含义。分析要客观理性，给出实用的商业建议。"""


def hepan_llm_analysis(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple'
) -> str:
    """
    使用LLM进行合盘深度分析（非流式）
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配结果
        hepan_type: 合盘类型
    
    Returns:
        LLM分析结果
    """
    system_prompt = get_hepan_system_prompt(hepan_type)
    user_prompt = build_hepan_prompt(pan_a, pan_b, hepan_result, hepan_type)
    
    try:
        return call_llm(system_prompt, user_prompt, temperature=0.3)
    except Exception as e:
        logger.error(f"合盘LLM分析失败: {e}")
        return f"分析失败: {str(e)}"


def hepan_llm_analysis_stream(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple'
):
    """
    使用LLM进行合盘深度分析（流式）
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配结果
        hepan_type: 合盘类型
    
    Yields:
        LLM分析结果片段
    """
    system_prompt = get_hepan_system_prompt(hepan_type)
    user_prompt = build_hepan_prompt(pan_a, pan_b, hepan_result, hepan_type)
    
    try:
        for chunk in call_llm_stream(system_prompt, user_prompt, temperature=0.3):
            yield chunk
    except Exception as e:
        logger.error(f"合盘LLM流式分析失败: {e}")
        yield f"分析失败: {str(e)}"