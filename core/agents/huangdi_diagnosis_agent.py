"""
黄帝内经诊断建议Agent
根据症状提供中医诊断思路（仅提供理论参考，不提供具体诊断）
"""
import logging
import re
from typing import Dict, Any, List, Optional

from core.tools.huangdi_knowledge_base import get_knowledge_base
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)

# 常见症状关键词映射
SYMPTOM_KEYWORDS = {
    "头痛": ["头痛", "头", "痛"],
    "发热": ["发热", "发烧", "热", "体温"],
    "恶寒": ["恶寒", "怕冷", "寒", "冷"],
    "咳嗽": ["咳嗽", "咳", "嗽"],
    "腹痛": ["腹痛", "肚子痛", "腹", "痛"],
    "腹泻": ["腹泻", "拉肚子", "泄", "泻"],
    "失眠": ["失眠", "睡不着", "不寐"],
    "乏力": ["乏力", "无力", "疲倦", "累"],
    "胸闷": ["胸闷", "胸", "闷"],
    "心悸": ["心悸", "心慌", "心跳"],
}


def extract_symptoms(symptom_text: str) -> List[str]:
    """
    从症状描述中提取关键词
    
    Args:
        symptom_text: 症状描述文本
        
    Returns:
        提取的症状关键词列表
    """
    symptoms = []
    symptom_lower = symptom_text.lower()
    
    # 先进行简单包含匹配（兼容性好）
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in symptom_lower:
                if symptom not in symptoms:
                    symptoms.append(symptom)
                break
    
    # 使用分组正则匹配多字词，提升准确性
    # 构建关键字到症状的映射，并按长度降序匹配，避免短词覆盖长词
    if not symptoms:
        kw_to_symptom = {}
        all_keywords: List[str] = []
        for sym, kws in SYMPTOM_KEYWORDS.items():
            for k in kws:
                kw_to_symptom[k] = sym
                all_keywords.append(k)
        # 去重并按长度降序
        all_keywords = sorted(set(all_keywords), key=lambda s: len(s), reverse=True)
        if all_keywords:
            pattern = r"(" + "|".join(re.escape(k) for k in all_keywords) + r")"
            matches = re.findall(pattern, symptom_text)
            for m in matches:
                sym = kw_to_symptom.get(m)
                if sym and sym not in symptoms:
                    symptoms.append(sym)
    
    return symptoms if symptoms else [symptom_text[:20]]  # 如果没有匹配，返回前20个字符


def huangdi_diagnosis_node(
    symptoms: str,
    include_llm: bool = True,
    k: int = 5,
) -> Dict[str, Any]:
    """
    诊断建议节点
    
    Args:
        symptoms: 症状描述
        include_llm: 是否使用LLM进行分析
        k: 返回结果数量
        
    Returns:
        诊断建议结果
    """
    try:
        logger.info(f"[诊断建议] 开始分析症状: {symptoms}")
        
        # 提取症状关键词
        symptom_keywords = extract_symptoms(symptoms)
        logger.info(f"[诊断建议] 提取的症状关键词: {symptom_keywords}")
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 搜索相关理论（重点搜索病因病机、诊断相关主题）
        search_queries = [
            symptoms,  # 原始症状描述
            " ".join(symptom_keywords),  # 症状关键词
            "病因病机",  # 病因病机理论
        ]
        
        all_results = []
        for query in search_queries:
            search_results = kb.search(
                query=query,
                search_type="hybrid",
                k=k,
                theme="病因病机",  # 优先搜索病因病机相关
            )
            all_results.extend(search_results.get('combined_results', []))
        
        # 去重
        seen = set()
        unique_results = []
        for result in all_results:
            key = f"{result.get('book', '')}_{result.get('chapter_title', '')}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # 限制数量
        relevant_theories = unique_results[:k]
        
        # LLM分析
        llm_analysis = None
        if include_llm:
            try:
                llm_analysis = _generate_diagnosis_analysis(symptoms, symptom_keywords, relevant_theories)
            except Exception as e:
                logger.error(f"LLM分析生成失败: {e}")
                llm_analysis = None
        
        result = {
            'success': True,
            'symptoms': symptoms,
            'symptom_keywords': symptom_keywords,
            'relevant_theories': [
                {
                    'book': r.get('book', ''),
                    'chapter_title': r.get('chapter_title', ''),
                    'content': r.get('content', ''),
                    'relevance_score': r.get('relevance_score', 0),
                }
                for r in relevant_theories
            ],
            'llm_analysis': llm_analysis,
            'disclaimer': '本分析仅提供《黄帝内经》理论参考，不能替代专业医疗诊断。如有疾病，请及时就医。',
        }
        
        logger.info(f"[诊断建议] 分析完成，找到 {len(relevant_theories)} 条相关理论")
        return result
        
    except Exception as e:
        logger.error(f"[诊断建议] 分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'symptoms': symptoms,
        }


def _generate_diagnosis_analysis(
    symptoms: str,
    symptom_keywords: List[str],
    theories: list
) -> str:
    """
    使用LLM生成诊断分析
    
    Args:
        symptoms: 症状描述
        symptom_keywords: 症状关键词
        theories: 相关理论列表
        
    Returns:
        LLM生成的分析
    """
    system_prompt = """你是一位精通《黄帝内经》的中医理论专家。
请根据提供的症状和相关理论，提供诊断思路分析。要求：
1. 基于《黄帝内经》的理论框架进行分析
2. 分析可能的病机（如阴阳失调、脏腑功能异常等）
3. 提供理论参考方向（不提供具体诊断）
4. 强调这仅是理论参考，不能替代专业医疗诊断
5. 用专业但易懂的语言表达"""

    # 构建用户提示词
    user_prompt_parts = [
        f"症状描述：{symptoms}",
        f"提取的症状关键词：{', '.join(symptom_keywords)}",
        "",
        "相关理论：",
    ]
    
    for i, theory in enumerate(theories, 1):
        user_prompt_parts.append(f"\n【{i}】{theory['book']} - {theory['chapter_title']}")
        user_prompt_parts.append(f"内容：{theory['content'][:500]}...")
    
    user_prompt_parts.append(
        "\n请基于以上理论，分析这些症状可能的病机，并提供诊断思路参考。"
        "注意：仅提供理论分析，不提供具体诊断建议。"
    )
    
    user_prompt = "\n".join(user_prompt_parts)
    
    # 调用LLM
    analysis = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )
    
    return analysis


if __name__ == "__main__":
    # 测试诊断
    logging.basicConfig(level=logging.INFO)
    
    result = huangdi_diagnosis_node("头痛、发热、恶寒", include_llm=True)
    print(f"诊断结果: {result.get('success')}")
    print(f"症状关键词: {result.get('symptom_keywords', [])}")
    print(f"相关理论数: {len(result.get('relevant_theories', []))}")
    if result.get('llm_analysis'):
        print(f"\nLLM分析:\n{result['llm_analysis']}")
