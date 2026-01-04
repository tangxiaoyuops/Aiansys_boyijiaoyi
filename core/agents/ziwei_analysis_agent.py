"""
紫微斗数完整分析Agent
整合所有分析模块，提供完整的分析结果
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.agents.ziwei_pan_agent import ziwei_pan_node
from core.agents.ziwei_daxian_agent import ziwei_daxian_node
from core.agents.ziwei_liunian_agent import ziwei_liunian_node
from core.agents.ziwei_liuyue_agent import ziwei_liuyue_node
from core.agents.ziwei_shensha_agent import ziwei_shensha_node
from core.agents.ziwei_geju_agent import ziwei_geju_node
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)

def ziwei_complete_analysis(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = '男',
    include_daxian: bool = True,
    include_liunian: bool = False,
    include_liuyue: bool = False,
    include_shensha: bool = True,
    include_geju: bool = True,
    include_llm: bool = False,
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
) -> Dict[str, Any]:
    """
    完整的紫微斗数分析
    
    Args:
        year: 公历年份
        month: 公历月份
        day: 公历日期
        hour: 时辰（0-23）
        gender: 性别（'男' 或 '女'）
        include_daxian: 是否包含大限分析
        include_liunian: 是否包含流年分析
        include_liuyue: 是否包含流月分析
        include_shensha: 是否包含神煞分析
        include_geju: 是否包含格局分析
        include_llm: 是否包含LLM深度分析
        target_year: 目标年份（用于流年流月分析）
        target_month: 目标月份（用于流月分析）
    
    Returns:
        完整的分析结果
    """
    try:
        print(f"[完整分析] ========== 开始完整分析 ==========")
        print(f"[完整分析] 参数: {year}年{month}月{day}日{hour}时, 性别={gender}")
        print(f"[完整分析] 分析选项: 大限={include_daxian}, 流年={include_liunian}, 流月={include_liuyue}, 神煞={include_shensha}, 格局={include_geju}, LLM={include_llm}")
        logger.info(f"开始完整分析: {year}年{month}月{day}日{hour}时")
        
        # 1. 基础排盘和四化
        print(f"[完整分析] 步骤1: 开始基础排盘和四化分析...")
        pan_result = ziwei_pan_node(year, month, day, hour, gender)
        if not pan_result.get('success'):
            print(f"[完整分析] 步骤1失败: {pan_result.get('error', '未知错误')}")
            return pan_result
        print(f"[完整分析] 步骤1完成: 基础排盘成功")
        
        pan_data = pan_result['pan_data']
        si_hua_analysis = pan_result.get('si_hua_analysis', {})
        
        # 2. 大限分析
        daxian_analysis = None
        if include_daxian:
            print(f"[完整分析] 步骤2: 开始大限分析...")
            daxian_result = ziwei_daxian_node(pan_data, target_year)
            if daxian_result.get('success'):
                daxian_analysis = daxian_result
                print(f"[完整分析] 步骤2完成: 大限分析成功")
            else:
                print(f"[完整分析] 步骤2失败: {daxian_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤2: 跳过大限分析")
        
        # 3. 流年分析
        liunian_analysis = None
        if include_liunian:
            print(f"[完整分析] 步骤3: 开始流年分析...")
            liunian_result = ziwei_liunian_node(pan_data, target_year)
            if liunian_result.get('success'):
                liunian_analysis = liunian_result
                print(f"[完整分析] 步骤3完成: 流年分析成功")
            else:
                print(f"[完整分析] 步骤3失败: {liunian_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤3: 跳过流年分析")
        
        # 4. 流月分析
        liuyue_analysis = None
        if include_liuyue:
            print(f"[完整分析] 步骤4: 开始流月分析...")
            liuyue_result = ziwei_liuyue_node(pan_data, target_year, target_month)
            if liuyue_result.get('success'):
                liuyue_analysis = liuyue_result
                print(f"[完整分析] 步骤4完成: 流月分析成功")
            else:
                print(f"[完整分析] 步骤4失败: {liuyue_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤4: 跳过流月分析")
        
        # 5. 神煞分析
        shensha_analysis = None
        if include_shensha:
            print(f"[完整分析] 步骤5: 开始神煞分析...")
            shensha_result = ziwei_shensha_node(pan_data)
            if shensha_result.get('success'):
                shensha_analysis = shensha_result
                print(f"[完整分析] 步骤5完成: 神煞分析成功")
            else:
                print(f"[完整分析] 步骤5失败: {shensha_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤5: 跳过神煞分析")
        
        # 6. 格局分析
        geju_analysis = None
        if include_geju:
            print(f"[完整分析] 步骤6: 开始格局分析...")
            geju_result = ziwei_geju_node(pan_data)
            if geju_result.get('success'):
                geju_analysis = geju_result
                print(f"[完整分析] 步骤6完成: 格局分析成功")
            else:
                print(f"[完整分析] 步骤6失败: {geju_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤6: 跳过格局分析")
        
        # 7. LLM深度分析
        llm_analysis = None
        if include_llm:
            print(f"[完整分析] 步骤7: 开始LLM深度分析（可能需要较长时间）...")
            try:
                llm_analysis = _build_llm_analysis(
                    pan_data,
                    si_hua_analysis,
                    daxian_analysis,
                    liunian_analysis,
                    shensha_analysis,
                    geju_analysis
                )
                if llm_analysis.get('success'):
                    print(f"[完整分析] 步骤7完成: LLM深度分析成功")
                else:
                    print(f"[完整分析] 步骤7失败: {llm_analysis.get('error', '未知错误')}")
            except Exception as e:
                print(f"[完整分析] 步骤7异常: {e}")
                import traceback
                print(f"[完整分析] 步骤7异常堆栈: {traceback.format_exc()}")
                llm_analysis = {
                    'success': False,
                    'error': str(e),
                }
        else:
            print(f"[完整分析] 步骤7: 跳过LLM深度分析")
        
        # 构建完整结果
        print(f"[完整分析] 开始构建最终结果...")
        result = {
            'pan_data': pan_data,
            'si_hua_analysis': si_hua_analysis,
            'daxian_analysis': daxian_analysis,
            'liunian_analysis': liunian_analysis,
            'liuyue_analysis': liuyue_analysis,
            'shensha_analysis': shensha_analysis,
            'geju_analysis': geju_analysis,
            'llm_analysis': llm_analysis,
            'success': True,
        }
        
        print(f"[完整分析] ========== 完整分析完成 ==========")
        logger.info("完整分析完成")
        return result
        
    except Exception as e:
        logger.error(f"完整分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }

def _build_llm_analysis(
    pan_data: Dict[str, Any],
    si_hua_analysis: Dict[str, Any],
    daxian_analysis: Optional[Dict[str, Any]],
    liunian_analysis: Optional[Dict[str, Any]],
    shensha_analysis: Optional[Dict[str, Any]],
    geju_analysis: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """构建LLM深度分析"""
    try:
        logger.info("开始构建LLM分析提示词...")
        
        # 构建系统提示词
        system_prompt = """你是一位资深的紫微斗数命理分析专家，具有深厚的命理学知识和丰富的实践经验。
请根据提供的命盘数据，进行深入、全面、专业的分析，包括：
1. 命盘整体格局评价
2. 性格特点分析
3. 事业财运分析
4. 感情婚姻分析
5. 健康运势分析
6. 人生建议和注意事项

请用专业但易懂的语言进行分析，避免过于玄学的表述，注重实用性和指导性。"""
        
        # 构建用户提示词（命盘数据）
        user_prompt = _build_ziwei_analysis_prompt(
            pan_data,
            si_hua_analysis,
            daxian_analysis,
            liunian_analysis,
            shensha_analysis,
            geju_analysis
        )
        
        logger.info("开始调用LLM进行深度分析...")
        # 调用LLM（注意：call_llm需要system_prompt和user_prompt两个参数）
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.3)
        
        logger.info(f"LLM分析完成，返回长度: {len(llm_response)} 字符")
        
        return {
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'response': llm_response,
            'success': True,
        }
    except Exception as e:
        logger.error(f"LLM分析失败: {e}", exc_info=True)
        import traceback
        logger.error(f"LLM分析异常堆栈: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
        }

def _build_ziwei_analysis_prompt(
    pan_data: Dict[str, Any],
    si_hua_analysis: Dict[str, Any],
    daxian_analysis: Optional[Dict[str, Any]],
    liunian_analysis: Optional[Dict[str, Any]],
    shensha_analysis: Optional[Dict[str, Any]],
    geju_analysis: Optional[Dict[str, Any]],
) -> str:
    """构建LLM分析提示词（用户提示词部分）"""
    import json
    
    prompt_parts = [
        "=== 紫微斗数命盘数据 ===",
        "",
        "【基础信息】",
        f"命宫：{pan_data.get('ming_gong', '未知')}",
        f"身宫：{pan_data.get('shen_gong', '未知')}",
    ]
    
    # 出生信息
    if pan_data.get('birth_info'):
        birth = pan_data['birth_info']
        prompt_parts.append(f"出生：{birth.get('year', '')}年{birth.get('month', '')}月{birth.get('day', '')}日{birth.get('hour', '')}时")
        prompt_parts.append(f"年柱：{birth.get('year_gan', '')}{birth.get('year_zhi', '')}")
    
    # 主星分布
    if pan_data.get('main_stars'):
        prompt_parts.append("")
        prompt_parts.append("【主星分布】")
        main_stars = pan_data['main_stars']
        for star, palace_index in main_stars.items():
            palace_name = pan_data.get('palaces', [{}])[palace_index].get('name', f'宫位{palace_index}') if palace_index < len(pan_data.get('palaces', [])) else f'宫位{palace_index}'
            prompt_parts.append(f"{star}：{palace_name}")
    
    # 四化分析
    prompt_parts.append("")
    prompt_parts.append("【四化星分析】")
    if si_hua_analysis.get('summary'):
        prompt_parts.append(si_hua_analysis['summary'])
    if si_hua_analysis.get('statistics'):
        stats = si_hua_analysis['statistics']
        prompt_parts.append(f"化禄：{stats.get('化禄_count', 0)}个，化权：{stats.get('化权_count', 0)}个，化科：{stats.get('化科_count', 0)}个，化忌：{stats.get('化忌_count', 0)}个")
    
    # 大限分析
    if daxian_analysis:
        prompt_parts.append("")
        prompt_parts.append("【大限分析】")
        daxian_summary = daxian_analysis.get('daxian_analysis', {}).get('summary', '')
        if daxian_summary:
            prompt_parts.append(daxian_summary)
        else:
            prompt_parts.append(str(daxian_analysis.get('summary', '')))
    
    # 神煞分析
    if shensha_analysis:
        prompt_parts.append("")
        prompt_parts.append("【神煞分析】")
        shensha_summary = shensha_analysis.get('shensha_analysis', {}).get('summary', '')
        if shensha_summary:
            prompt_parts.append(shensha_summary)
        else:
            prompt_parts.append(str(shensha_analysis.get('summary', '')))
    
    # 格局分析
    if geju_analysis:
        prompt_parts.append("")
        prompt_parts.append("【格局分析】")
        geju_summary = geju_analysis.get('geju_analysis', {}).get('summary', '')
        if geju_summary:
            prompt_parts.append(geju_summary)
        else:
            prompt_parts.append(str(geju_analysis.get('summary', '')))
    
    prompt_parts.append("")
    prompt_parts.append("请基于以上命盘数据，提供详细、专业、实用的命盘解读和人生建议。")
    
    return "\n".join(prompt_parts)

