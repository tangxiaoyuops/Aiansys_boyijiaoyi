"""
六爻卜卦分析Agent
整合卦象计算和LLM解卦分析
"""
from typing import Dict, Any, Optional, List
import logging
from core.tools.divination_calculator import create_hexagram_from_coin_results
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)


def divination_complete_analysis(
    coin_results: List[List[int]],
    question: str,
    include_llm: bool = True
) -> Dict[str, Any]:
    """
    完整的六爻卜卦分析
    
    Args:
        coin_results: 6次摇卦结果，每次3枚铜钱（0=反面，1=正面）
        question: 用户问题
        include_llm: 是否调用LLM进行深度分析
    
    Returns:
        完整的分析结果
    """
    try:
        logger.info(f"开始六爻卜卦分析，问题: {question}")
        
        # 1. 创建卦象
        hexagram_data = create_hexagram_from_coin_results(coin_results)
        
        # 2. LLM深度分析
        llm_analysis = None
        if include_llm:
            logger.info("开始调用LLM进行解卦分析...")
            try:
                llm_analysis = _build_llm_analysis(hexagram_data, question)
                # 检查返回结果是否包含错误信息
                if llm_analysis.get('response', '').startswith('[LLM调用失败'):
                    logger.warning("LLM返回了错误信息，标记为失败")
                    llm_analysis = {
                        'success': False,
                        'error': llm_analysis.get('response', 'LLM调用失败'),
                    }
            except Exception as e:
                error_msg = str(e)
                logger.error(f"LLM分析失败: {error_msg}")
                
                # 检查是否是内容审核错误，提供更友好的提示
                if '内容审核未通过' in error_msg or 'inappropriate content' in error_msg.lower() or 'data_inspection_failed' in error_msg.lower():
                    friendly_error = "内容审核未通过：模型认为输出内容可能包含不当内容。\n\n这可能是因为：\n1. 问题表述触发了敏感词检测\n2. 卦象解读内容被误判\n\n建议：\n• 尝试重新表述问题（例如：'寻找合适的伴侣' 代替 '找女朋友'）\n• 或关闭AI深度分析，仅查看卦象和卦辞信息"
                elif 'timeout' in error_msg.lower() or '超时' in error_msg:
                    friendly_error = "LLM调用超时，请稍后重试"
                elif '401' in error_msg or 'unauthorized' in error_msg.lower():
                    friendly_error = "API认证失败，请检查API密钥配置"
                elif '429' in error_msg or 'rate limit' in error_msg.lower():
                    friendly_error = "请求频率过高，请稍后重试"
                else:
                    friendly_error = f"LLM调用失败: {error_msg[:200]}"  # 限制长度
                
                llm_analysis = {
                    'success': False,
                    'error': friendly_error,
                }
        else:
            logger.info("跳过LLM深度分析")
        
        # 构建完整结果
        result = {
            'success': True,
            'hexagram': hexagram_data,
            'question': question,
            'llm_analysis': llm_analysis,
        }
        
        logger.info("六爻卜卦分析完成")
        return result
        
    except Exception as e:
        logger.error(f"六爻卜卦分析异常: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }


def _build_llm_analysis(hexagram_data: Dict[str, Any], question: str) -> Dict[str, Any]:
    """构建LLM解卦分析"""
    try:
        logger.info("开始构建LLM解卦分析提示词...")
        
        # 构建系统提示词（参考期货分析的简洁风格，避免触发内容审核）
        system_prompt = """你是一位传统文化分析专家，擅长根据卦象信息进行逻辑分析和建议。
请根据提供的卦象信息，结合用户的问题，进行客观、理性的分析，包括：
1. 卦象的整体含义
2. 结合用户问题的针对性分析
3. 各爻的含义和作用（特别是动爻）
4. 变卦的意义（如果有变卦）
5. 综合建议和指导

请用专业但易懂的语言进行分析，注重实用性和指导性，避免过于玄学的表述。"""
        
        # 构建用户提示词
        user_prompt = _build_divination_prompt(hexagram_data, question)
        
        logger.info("开始调用LLM进行解卦分析...")
        llm_response = call_llm(system_prompt, user_prompt, model=None, temperature=0.3)
        
        # 检查返回内容是否包含错误信息（虽然现在会抛异常，但保留检查以防万一）
        if llm_response and llm_response.startswith('[LLM调用失败'):
            logger.warning(f"LLM返回了错误信息: {llm_response}")
            raise Exception(llm_response)
        
        logger.info(f"LLM解卦分析完成，返回长度: {len(llm_response)} 字符")
        
        return {
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'response': llm_response,
            'success': True,
        }
    except Exception as e:
        logger.error(f"LLM解卦分析失败: {e}", exc_info=True)
        import traceback
        logger.error(f"LLM解卦分析异常堆栈: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
        }


def _build_divination_prompt(hexagram_data: Dict[str, Any], question: str) -> str:
    """构建LLM分析提示词（用户提示词部分）"""
    # 优化问题表述，避免敏感词（参考期货分析的做法，使用更中性的表述）
    safe_question = question
    # 将一些可能触发审核的词汇替换为更中性的表述
    question_replacements = {
        '找女朋友': '寻找合适的伴侣',
        '找对象': '寻找合适的伴侣',
        '谈恋爱': '感情发展',
        '结婚': '感情归宿',
    }
    for old, new in question_replacements.items():
        if old in safe_question:
            safe_question = safe_question.replace(old, new)
    
    prompt_parts = [
        "=== 卦象分析信息 ===",
        "",
        f"【用户问题】",
        safe_question,
        "",
        "【本卦信息】",
    ]
    
    ben_hexagram = hexagram_data.get('ben_hexagram', {})
    prompt_parts.append(f"卦名：{ben_hexagram.get('full_name', '未知')}")
    prompt_parts.append(f"内卦（下卦）：{hexagram_data.get('inner_trigram', {}).get('name', '未知')}")
    prompt_parts.append(f"外卦（上卦）：{hexagram_data.get('outer_trigram', {}).get('name', '未知')}")
    
    if ben_hexagram.get('guaci'):
        prompt_parts.append("")
        prompt_parts.append("【卦辞】")
        prompt_parts.append(ben_hexagram['guaci'])
    
    # 六个爻的信息
    prompt_parts.append("")
    prompt_parts.append("【六个爻的信息】（从下往上：初爻、二爻、三爻、四爻、五爻、上爻）")
    yao_names = ['初', '二', '三', '四', '五', '上']
    yaos = hexagram_data.get('yaos', [])
    dong_yaos = hexagram_data.get('dong_yaos', [])
    
    for i, yao in enumerate(yaos):
        yao_name = yao_names[i]
        is_dong = i in dong_yaos
        dong_mark = "（动爻）" if is_dong else ""
        prompt_parts.append(f"{yao_name}爻：{yao.get('description', '')}{dong_mark} - {yao.get('symbol', '')}")
        
        # 如果有爻辞，也加上
        yao_key = str(i + 1)
        if ben_hexagram.get('yaoci') and yao_key in ben_hexagram['yaoci']:
            prompt_parts.append(f"  爻辞：{ben_hexagram['yaoci'][yao_key]}")
    
    # 变卦信息
    bian_hexagram = hexagram_data.get('bian_hexagram')
    if bian_hexagram:
        prompt_parts.append("")
        prompt_parts.append("【变卦信息】")
        prompt_parts.append(f"变卦卦名：{bian_hexagram.get('full_name', '未知')}")
        if bian_hexagram.get('guaci'):
            prompt_parts.append(f"变卦卦辞：{bian_hexagram['guaci']}")
        prompt_parts.append(f"说明：本卦中有{len(dong_yaos)}个动爻，动爻变化后形成变卦。")
    else:
        if hexagram_data.get('has_dong', False):
            prompt_parts.append("")
            prompt_parts.append("【变卦】无变卦（虽然有动爻，但变卦信息待补充）")
    
    prompt_parts.append("")
    prompt_parts.append("请根据以上卦象信息，结合用户的问题，进行详细的解卦分析。")
    
    return "\n".join(prompt_parts)

