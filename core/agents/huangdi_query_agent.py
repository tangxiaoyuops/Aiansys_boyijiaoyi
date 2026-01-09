"""
黄帝内经知识查询Agent
根据用户问题查询相关经文，并提供解释
"""
import logging
from typing import Dict, Any, Optional

from core.tools.huangdi_knowledge_base import get_knowledge_base
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)


def huangdi_query_node(
    question: str,
    include_llm: bool = True,
    k: int = 5,
) -> Dict[str, Any]:
    """
    知识查询节点
    
    Args:
        question: 用户问题
        include_llm: 是否使用LLM进行解释
        k: 返回结果数量
        
    Returns:
        查询结果
    """
    try:
        logger.info(f"[知识查询] 开始查询: {question}")
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 执行搜索
        search_results = kb.search(
            query=question,
            search_type="hybrid",
            k=k,
        )
        
        # 提取相关经文
        relevant_chapters = []
        for result in search_results.get('combined_results', [])[:k]:
            chapter_info = {
                'book': result.get('book', ''),
                'chapter_title': result.get('chapter_title', ''),
                'content': result.get('content', ''),
                'relevance_score': result.get('relevance_score', 0),
                'themes': result.get('themes', []),
            }
            relevant_chapters.append(chapter_info)
        
        # LLM解释
        llm_explanation = None
        if include_llm and relevant_chapters:
            try:
                llm_explanation = _generate_explanation(question, relevant_chapters)
            except Exception as e:
                logger.error(f"LLM解释生成失败: {e}")
                llm_explanation = None
        
        result = {
            'success': True,
            'question': question,
            'relevant_chapters': relevant_chapters,
            'llm_explanation': llm_explanation,
            'total_results': len(relevant_chapters),
        }
        
        logger.info(f"[知识查询] 查询完成，找到 {len(relevant_chapters)} 条相关结果")
        return result
        
    except Exception as e:
        logger.error(f"[知识查询] 查询失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'question': question,
        }


def _generate_explanation(question: str, chapters: list) -> str:
    """
    使用LLM生成解释
    
    Args:
        question: 用户问题
        chapters: 相关章节列表
        
    Returns:
        LLM生成的解释
    """
    system_prompt = """你是一位精通《黄帝内经》的中医专家，擅长用通俗易懂的语言解释经典理论。
请根据提供的经文内容，回答用户的问题。要求：
1. 准确引用相关经文
2. 用现代语言解释经典理论
3. 提供实用的理解建议
4. 保持专业性和准确性"""

    # 构建用户提示词
    user_prompt_parts = [
        f"用户问题：{question}",
        "",
        "相关经文：",
    ]
    
    for i, chapter in enumerate(chapters, 1):
        user_prompt_parts.append(f"\n【{i}】{chapter['book']} - {chapter['chapter_title']}")
        user_prompt_parts.append(f"内容：{chapter['content'][:500]}...")  # 限制长度
    
    user_prompt_parts.append("\n请基于以上经文内容，详细回答用户的问题。")
    
    user_prompt = "\n".join(user_prompt_parts)
    
    # 调用LLM
    explanation = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )
    
    return explanation


if __name__ == "__main__":
    # 测试查询
    logging.basicConfig(level=logging.INFO)
    
    result = huangdi_query_node("什么是阴阳", include_llm=True)
    print(f"查询结果: {result.get('success')}")
    print(f"相关章节数: {result.get('total_results', 0)}")
    if result.get('llm_explanation'):
        print(f"\nLLM解释:\n{result['llm_explanation']}")
