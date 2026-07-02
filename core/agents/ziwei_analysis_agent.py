"""
紫微斗数完整分析Agent
整合所有分析模块，提供完整的分析结果
优化版本：并行执行不依赖彼此的步骤
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
    完整的紫微斗数分析（优化版本，并行执行）
    
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
        start_time = time.time()
        print(f"[完整分析] ========== 开始完整分析 ==========")
        print(f"[完整分析] 参数: {year}年{month}月{day}日{hour}时, 性别={gender}")
        print(f"[完整分析] 分析选项: 大限={include_daxian}, 流年={include_liunian}, 流月={include_liuyue}, 神煞={include_shensha}, 格局={include_geju}, LLM={include_llm}")
        logger.info(f"开始完整分析: {year}年{month}月{day}日{hour}时")
        
        # 1. 基础排盘和四化（必须先执行）
        step1_start = time.time()
        print(f"[完整分析] 步骤1: 开始基础排盘和四化分析...")
        pan_result = ziwei_pan_node(year, month, day, hour, gender)
        if not pan_result.get('success'):
            print(f"[完整分析] 步骤1失败: {pan_result.get('error', '未知错误')}")
            return pan_result
        print(f"[完整分析] 步骤1完成: 基础排盘成功, 耗时={time.time()-step1_start:.2f}秒")
        
        pan_data = pan_result['pan_data']
        si_hua_analysis = pan_result.get('si_hua_analysis', {})
        
        # 2. 并行执行大限、神煞、格局分析（这些步骤不依赖彼此）
        step2_start = time.time()
        print(f"[完整分析] 步骤2-4: 并行执行大限、神煞、格局分析...")
        
        daxian_analysis = None
        shensha_analysis = None
        geju_analysis = None
        
        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            # 提交大限分析任务
            if include_daxian:
                futures['daxian'] = executor.submit(ziwei_daxian_node, pan_data.copy(), target_year)
            
            # 提交神煞分析任务
            if include_shensha:
                futures['shensha'] = executor.submit(ziwei_shensha_node, pan_data.copy())
            
            # 提交格局分析任务
            if include_geju:
                futures['geju'] = executor.submit(ziwei_geju_node, pan_data.copy())
            
            # 收集结果
            for name, future in futures.items():
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    if result.get('success'):
                        if name == 'daxian':
                            daxian_analysis = result
                        elif name == 'shensha':
                            shensha_analysis = result
                        elif name == 'geju':
                            geju_analysis = result
                        print(f"[完整分析] {name}分析完成")
                    else:
                        print(f"[完整分析] {name}分析失败: {result.get('error', '未知错误')}")
                except Exception as e:
                    print(f"[完整分析] {name}分析异常: {e}")
        
        print(f"[完整分析] 步骤2-4完成: 并行分析耗时={time.time()-step2_start:.2f}秒")
        
        # 3. 流年分析（可选，依赖大限）
        liunian_analysis = None
        if include_liunian:
            step3_start = time.time()
            print(f"[完整分析] 步骤5: 开始流年分析...")
            liunian_result = ziwei_liunian_node(pan_data, target_year)
            if liunian_result.get('success'):
                liunian_analysis = liunian_result
                print(f"[完整分析] 步骤5完成: 流年分析成功, 耗时={time.time()-step3_start:.2f}秒")
            else:
                print(f"[完整分析] 步骤5失败: {liunian_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤5: 跳过流年分析")
        
        # 4. 流月分析（可选，依赖流年）
        liuyue_analysis = None
        if include_liuyue:
            step4_start = time.time()
            print(f"[完整分析] 步骤6: 开始流月分析...")
            liuyue_result = ziwei_liuyue_node(pan_data, target_year, target_month)
            if liuyue_result.get('success'):
                liuyue_analysis = liuyue_result
                print(f"[完整分析] 步骤6完成: 流月分析成功, 耗时={time.time()-step4_start:.2f}秒")
            else:
                print(f"[完整分析] 步骤6失败: {liuyue_result.get('error', '未知错误')}")
        else:
            print(f"[完整分析] 步骤6: 跳过流月分析")
        
        # 5. LLM深度分析（最耗时的部分）
        llm_analysis = None
        if include_llm:
            step5_start = time.time()
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
                    print(f"[完整分析] 步骤7完成: LLM深度分析成功, 耗时={time.time()-step5_start:.2f}秒")
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
        
        total_time = time.time() - start_time
        print(f"[完整分析] ========== 完整分析完成, 总耗时={total_time:.2f}秒 ==========")
        logger.info(f"完整分析完成, 耗时{total_time:.2f}秒")
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
        
        # 构建系统提示词 - 简洁明了
        system_prompt = """你是紫微斗数专家。根据命盘数据，用简洁专业的语言分析：

1. 命盘格局（主星分布特点）
2. 性格特点（3-4点）
3. 事业财运方向
4. 感情婚姻趋势
5. 人生建议（2-3条实用建议）

要求：专业术语适当解释，回复控制在500字以内。"""
        
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
        # 调用LLM，temperature设高一点让回复更快
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.5)
        
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
    """构建LLM分析提示词（用户提示词部分）- 精简版本"""
    import json
    
    prompt_parts = [
        "=== 紫微斗数命盘数据 ===",
        "",
        "【基础信息】",
    ]
    
    # 出生信息
    if pan_data.get('birth_info'):
        birth = pan_data['birth_info']
        prompt_parts.append(f"出生：{birth.get('year', '')}年{birth.get('month', '')}月{birth.get('day', '')}日{birth.get('hour', '')}时")
        prompt_parts.append(f"年柱：{birth.get('year_gan', '')}{birth.get('year_zhi', '')}")
    
    # 命宫身宫
    ming_gong = pan_data.get('ming_gong', 0)
    shen_gong = pan_data.get('shen_gong', 0)
    palace_names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母']
    prompt_parts.append(f"命宫：{palace_names[ming_gong] if ming_gong < 12 else '未知'}")
    prompt_parts.append(f"身宫：{palace_names[shen_gong] if shen_gong < 12 else '未知'}")
    
    # 主星分布（精简）
    if pan_data.get('main_stars'):
        prompt_parts.append("")
        prompt_parts.append("【主星分布】")
        main_stars = pan_data['main_stars']
        # 只显示命宫和身宫的主星
        for star, palace_index in list(main_stars.items())[:8]:  # 只显示前8个主星
            palace_name = palace_names[palace_index] if palace_index < 12 else f'宫位{palace_index}'
            prompt_parts.append(f"{star}：{palace_name}")
    
    # 四化分析（精简）
    if si_hua_analysis.get('statistics'):
        stats = si_hua_analysis['statistics']
        prompt_parts.append("")
        prompt_parts.append("【四化星】")
        prompt_parts.append(f"化禄：{stats.get('化禄_count', 0)}个，化权：{stats.get('化权_count', 0)}个，化科：{stats.get('化科_count', 0)}个，化忌：{stats.get('化忌_count', 0)}个")
    
    # 大限分析（精简）
    if daxian_analysis:
        current = daxian_analysis.get('current_daxian') or daxian_analysis.get('daxian_analysis', {}).get('current_daxian')
        if current:
            prompt_parts.append("")
            prompt_parts.append("【当前大限】")
            prompt_parts.append(f"第{current.get('number', '')}大限, {current.get('start_age', '')}-{current.get('end_age', '')}岁")
    
    # 格局分析（精简）
    if geju_analysis and geju_analysis.get('detected_geju'):
        prompt_parts.append("")
        prompt_parts.append("【格局】")
        detected = geju_analysis.get('detected_geju', {})
        for name in list(detected.keys())[:3]:  # 只显示前3个格局
            prompt_parts.append(f"- {name}")
    
    prompt_parts.append("")
    prompt_parts.append("请基于以上命盘数据，提供简洁、专业、实用的命盘解读和人生建议（控制在800字以内）。")
    
    return "\n".join(prompt_parts)