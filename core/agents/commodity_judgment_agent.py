"""
大宗商品自动判定Agent
自动判定缺口、矛盾、关键驱动，生成建议搜索查询
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.llm_client import call_llm


def commodity_judgment_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    自动判定节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[自动判定] 开始自动判定")
    
    structured_analysis = state.get("structured_analysis")
    raw_evidence = state.get("raw_evidence")
    
    if not structured_analysis:
        print("[自动判定] 警告: 没有结构化分析结果")
        state["judgment"] = {
            "missing_data": [],
            "contradictions": [],
            "key_drivers": [],
            "suggested_queries": []
        }
        return state
    
    system_prompt = """你是一个大宗商品市场分析专家。请对提供的分析结果进行自动判定。

你需要评估以下内容：
1. 缺失数据：哪些关键信息缺失（供给、价格、新闻等）
2. 矛盾点：多源数据是否存在冲突
3. 关键驱动：当前阶段最需要关注的因子
4. 建议搜索：需要补充信息的搜索查询（中英文均可）

请以JSON格式返回判定结果，格式如下：
{
    "missing_data": ["缺失数据类型1", "缺失数据类型2", ...],
    "contradictions": ["矛盾描述1", "矛盾描述2", ...],
    "key_drivers": ["关键驱动1", "关键驱动2", ...],
    "suggested_queries": ["搜索查询1", "搜索查询2", ...]
}

如果没有缺失数据或矛盾，请将对应字段设为空数组。
如果没有需要补充的信息，请将suggested_queries设为空数组。"""

    user_prompt = f"""请对以下分析结果进行自动判定：

品种/产业链：{raw_evidence.get('commodity_or_chain', '未知')}

结构化分析结果：
- 摘要: {structured_analysis.get('summary')}
- 市场分类: {structured_analysis.get('classification')}
- 驱动因子: {structured_analysis.get('key_drivers')}
- 供给链摘要: {structured_analysis.get('supply_chain_summary')}
- 价格摘要: {structured_analysis.get('price_summary')}
- 置信度: {structured_analysis.get('confidence')}

原始数据统计：
- 供给链: {len(raw_evidence.get('supply_chain', []))} 条
- 价格: {len(raw_evidence.get('prices', []))} 条
- 新闻: {len(raw_evidence.get('news', []))} 条

请进行自动判定，识别缺失数据、矛盾点和关键驱动，并生成建议搜索查询。"""

    try:
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        import json
        judgment = json.loads(result)
        
        state["judgment"] = judgment
        state["search_queries"] = judgment.get("suggested_queries", [])
        
        print(f"[自动判定] 判定完成")
        print(f"[自动判定] 缺失数据: {judgment.get('missing_data')}")
        print(f"[自动判定] 矛盾点: {judgment.get('contradictions')}")
        print(f"[自动判定] 关键驱动: {judgment.get('key_drivers')}")
        print(f"[自动判定] 建议查询: {judgment.get('suggested_queries')}")
        
    except Exception as e:
        error_msg = f"自动判定失败: {str(e)}"
        print(f"[自动判定] {error_msg}")
        state["judgment"] = {
            "missing_data": [],
            "contradictions": [],
            "key_drivers": [],
            "suggested_queries": []
        }
        state["search_queries"] = []
    
    return state
