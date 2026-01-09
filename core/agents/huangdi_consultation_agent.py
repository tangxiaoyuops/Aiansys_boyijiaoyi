"""
黄帝内经健康咨询Agent
基于内经理论提供养生建议
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.tools.huangdi_knowledge_base import get_knowledge_base
from core.tools.llm_client import call_llm

logger = logging.getLogger(__name__)

# 季节映射
SEASON_MAP = {
    1: "春", 2: "春", 3: "春",
    4: "夏", 5: "夏", 6: "夏",
    7: "秋", 8: "秋", 9: "秋",
    10: "冬", 11: "冬", 12: "冬",
}

# 体质关键词
CONSTITUTION_KEYWORDS = {
    "阳虚": ["阳虚", "怕冷", "手脚凉", "畏寒"],
    "阴虚": ["阴虚", "怕热", "口干", "盗汗"],
    "气虚": ["气虚", "乏力", "气短", "易累"],
    "血虚": ["血虚", "面色苍白", "头晕", "心悸"],
    "痰湿": ["痰湿", "肥胖", "痰多", "胸闷"],
    "湿热": ["湿热", "口苦", "口臭", "大便黏"],
    "气郁": ["气郁", "情绪", "抑郁", "易怒"],
    "血瘀": ["血瘀", "疼痛", "瘀血", "色暗"],
}


def get_current_season() -> str:
    """
    获取当前季节
    
    Returns:
        季节名称（春/夏/秋/冬）
    """
    month = datetime.now().month
    return SEASON_MAP.get(month, "春")


def extract_constitution(user_info: str) -> list:
    """
    从用户信息中提取体质关键词
    
    Args:
        user_info: 用户信息文本
        
    Returns:
        体质关键词列表
    """
    constitution = []
    info_lower = user_info.lower()
    
    for const_type, keywords in CONSTITUTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in info_lower:
                if const_type not in constitution:
                    constitution.append(const_type)
                break
    
    return constitution


def huangdi_consultation_node(
    user_info: str,
    season: Optional[str] = None,
    age: Optional[int] = None,
    include_llm: bool = True,
    k: int = 5,
) -> Dict[str, Any]:
    """
    健康咨询节点
    
    Args:
        user_info: 用户情况描述（体质、生活习惯等）
        season: 季节（春/夏/秋/冬），如果为None则自动获取当前季节
        age: 年龄（可选）
        include_llm: 是否使用LLM生成建议
        k: 返回结果数量
        
    Returns:
        健康咨询结果
    """
    try:
        logger.info(f"[健康咨询] 开始咨询: {user_info}")
        
        # 确定季节
        if season is None:
            season = get_current_season()
        
        # 提取体质信息
        constitution = extract_constitution(user_info)
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 构建搜索查询
        search_queries = [
            f"{season}季养生",  # 季节养生
            "四时养生",  # 四时理论
            "饮食有节",  # 饮食理论
            "起居有常",  # 起居理论
        ]
        
        # 如果有体质信息，添加体质相关查询
        if constitution:
            search_queries.extend([f"{c}体质" for c in constitution])
        
        # 执行搜索
        all_results = []
        for query in search_queries:
            search_results = kb.search(
                query=query,
                search_type="hybrid",
                k=k,
                theme="养生",  # 优先搜索养生相关
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
        
        # LLM生成建议
        llm_suggestions = None
        if include_llm:
            try:
                llm_suggestions = _generate_consultation_suggestions(
                    user_info, season, age, constitution, relevant_theories
                )
            except Exception as e:
                logger.error(f"LLM建议生成失败: {e}")
                llm_suggestions = None
        
        result = {
            'success': True,
            'user_info': user_info,
            'season': season,
            'age': age,
            'constitution': constitution,
            'relevant_theories': [
                {
                    'book': r.get('book', ''),
                    'chapter_title': r.get('chapter_title', ''),
                    'content': r.get('content', ''),
                    'relevance_score': r.get('relevance_score', 0),
                }
                for r in relevant_theories
            ],
            'llm_suggestions': llm_suggestions,
            'disclaimer': '本建议基于《黄帝内经》理论，仅供参考。如有疾病，请及时就医。',
        }
        
        logger.info(f"[健康咨询] 咨询完成，找到 {len(relevant_theories)} 条相关理论")
        return result
        
    except Exception as e:
        logger.error(f"[健康咨询] 咨询失败: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'user_info': user_info,
        }


def _generate_consultation_suggestions(
    user_info: str,
    season: str,
    age: Optional[int],
    constitution: list,
    theories: list
) -> str:
    """
    使用LLM生成健康建议
    
    Args:
        user_info: 用户信息
        season: 季节
        age: 年龄
        constitution: 体质列表
        theories: 相关理论列表
        
    Returns:
        LLM生成的建议
    """
    system_prompt = """你是一位精通《黄帝内经》的养生专家。
请根据提供的用户情况和相关理论，提供个性化的养生建议。要求：
1. 基于《黄帝内经》的养生理论
2. 结合季节特点（四时养生）
3. 考虑体质因素（如有）
4. 提供饮食、起居、情志、运动等方面的建议
5. 用通俗易懂的语言表达
6. 强调这是理论参考，不能替代医疗建议"""

    # 构建用户提示词
    user_prompt_parts = [
        f"用户情况：{user_info}",
        f"当前季节：{season}",
    ]
    
    if age:
        user_prompt_parts.append(f"年龄：{age}岁")
    
    if constitution:
        user_prompt_parts.append(f"体质特点：{', '.join(constitution)}")
    
    user_prompt_parts.append("")
    user_prompt_parts.append("相关理论：")
    
    for i, theory in enumerate(theories, 1):
        user_prompt_parts.append(f"\n【{i}】{theory['book']} - {theory['chapter_title']}")
        user_prompt_parts.append(f"内容：{theory['content'][:500]}...")
    
    user_prompt_parts.append(
        f"\n请基于以上理论，为这位用户提供{season}季的个性化养生建议，"
        "包括饮食、起居、情志、运动等方面。"
    )
    
    user_prompt = "\n".join(user_prompt_parts)
    
    # 调用LLM
    suggestions = call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )
    
    return suggestions


if __name__ == "__main__":
    # 测试咨询
    logging.basicConfig(level=logging.INFO)
    
    result = huangdi_consultation_node(
        "平时容易疲劳，手脚比较凉",
        season="冬",
        age=35,
        include_llm=True
    )
    print(f"咨询结果: {result.get('success')}")
    print(f"季节: {result.get('season')}")
    print(f"体质: {result.get('constitution', [])}")
    print(f"相关理论数: {len(result.get('relevant_theories', []))}")
    if result.get('llm_suggestions'):
        print(f"\nLLM建议:\n{result['llm_suggestions']}")

