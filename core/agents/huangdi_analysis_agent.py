"""
黄帝内经完整分析Agent
整合所有分析模块，提供完整的分析结果
"""
import logging
from typing import Dict, Any, Optional

from core.agents.huangdi_query_agent import huangdi_query_node
from core.agents.huangdi_diagnosis_agent import huangdi_diagnosis_node
from core.agents.huangdi_consultation_agent import huangdi_consultation_node

logger = logging.getLogger(__name__)


def detect_query_type(question: str) -> str:
    """
    检测查询类型
    
    Args:
        question: 用户问题
        
    Returns:
        查询类型 ('query', 'diagnosis', 'consultation')
    """
    question_lower = question.lower()
    
    # 诊断相关关键词
    diagnosis_keywords = [
        "症状", "病", "痛", "不适", "诊断", "什么病", "怎么了",
        "头痛", "发热", "咳嗽", "腹痛", "腹泻", "失眠",
    ]
    
    # 咨询相关关键词
    consultation_keywords = [
        "养生", "保健", "健康", "建议", "如何", "怎么",
        "饮食", "作息", "运动", "季节", "体质",
    ]
    
    # 检查是否包含诊断关键词
    if any(keyword in question_lower for keyword in diagnosis_keywords):
        # 进一步判断：如果同时包含咨询关键词，优先判断为咨询
        if any(keyword in question_lower for keyword in consultation_keywords):
            return "consultation"
        return "diagnosis"
    
    # 检查是否包含咨询关键词
    if any(keyword in question_lower for keyword in consultation_keywords):
        return "consultation"
    
    # 默认为知识查询
    return "query"


def huangdi_complete_analysis(
    question: str,
    query_type: Optional[str] = None,
    include_llm: bool = True,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    完整的黄帝内经分析
    
    Args:
        question: 用户问题
        query_type: 查询类型 ('query', 'diagnosis', 'consultation')，如果为None则自动检测
        include_llm: 是否包含LLM分析
        context: 额外上下文（如症状、体质、季节、年龄等）
    
    Returns:
        完整的分析结果
    """
    try:
        logger.info(f"[完整分析] ========== 开始黄帝内经分析 ==========")
        logger.info(f"[完整分析] 问题: {question}")
        logger.info(f"[完整分析] 查询类型: {query_type}")
        logger.info(f"[完整分析] 上下文: {context}")
        
        # 自动检测查询类型
        if query_type is None:
            query_type = detect_query_type(question)
            logger.info(f"[完整分析] 自动检测的查询类型: {query_type}")
        
        # 根据查询类型调用相应的Agent
        if query_type == "diagnosis":
            # 诊断建议
            logger.info(f"[完整分析] 调用诊断建议Agent...")
            diagnosis_result = huangdi_diagnosis_node(
                symptoms=question,
                include_llm=include_llm,
            )
            
            result = {
                'success': diagnosis_result.get('success', False),
                'query_type': 'diagnosis',
                'question': question,
                'diagnosis_result': diagnosis_result,
            }
            
        elif query_type == "consultation":
            # 健康咨询
            logger.info(f"[完整分析] 调用健康咨询Agent...")
            consultation_result = huangdi_consultation_node(
                user_info=question,
                season=context.get('season') if context else None,
                age=context.get('age') if context else None,
                include_llm=include_llm,
            )
            
            result = {
                'success': consultation_result.get('success', False),
                'query_type': 'consultation',
                'question': question,
                'consultation_result': consultation_result,
            }
            
        else:
            # 知识查询（默认）
            logger.info(f"[完整分析] 调用知识查询Agent...")
            query_result = huangdi_query_node(
                question=question,
                include_llm=include_llm,
            )
            
            result = {
                'success': query_result.get('success', False),
                'query_type': 'query',
                'question': question,
                'query_result': query_result,
            }
        
        logger.info(f"[完整分析] ========== 分析完成 ==========")
        return result
        
    except Exception as e:
        logger.error(f"[完整分析] 分析失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'question': question,
            'query_type': query_type,
        }


if __name__ == "__main__":
    # 测试完整分析
    logging.basicConfig(level=logging.INFO)
    
    # 测试知识查询
    print("=" * 50)
    print("测试1: 知识查询")
    print("=" * 50)
    result1 = huangdi_complete_analysis("什么是阴阳", query_type="query")
    print(f"成功: {result1.get('success')}")
    print(f"类型: {result1.get('query_type')}")
    
    # 测试诊断建议
    print("\n" + "=" * 50)
    print("测试2: 诊断建议")
    print("=" * 50)
    result2 = huangdi_complete_analysis("头痛、发热、恶寒", query_type="diagnosis")
    print(f"成功: {result2.get('success')}")
    print(f"类型: {result2.get('query_type')}")
    
    # 测试健康咨询
    print("\n" + "=" * 50)
    print("测试3: 健康咨询")
    print("=" * 50)
    result3 = huangdi_complete_analysis(
        "平时容易疲劳，手脚比较凉",
        query_type="consultation",
        context={"season": "冬", "age": 35}
    )
    print(f"成功: {result3.get('success')}")
    print(f"类型: {result3.get('query_type')}")

