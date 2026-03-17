"""
大宗商品搜索Agent
执行自动搜索，补充证据包
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.commodity_search import create_commodity_searcher


def commodity_search_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    搜索节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[搜索执行] 开始执行搜索")
    
    search_queries = state.get("search_queries", [])
    
    if not search_queries:
        print("[搜索执行] 没有待执行的查询")
        state["search_results"] = []
        return state
    
    try:
        searcher = create_commodity_searcher()
        search_results = searcher.search(
            queries=search_queries,
            max_results_per_query=5
        )
        
        state["search_results"] = search_results
        state["round_index"] = state.get("round_index", 0) + 1
        
        print(f"[搜索执行] 搜索完成，获取 {len(search_results)} 条结果")
        
        raw_evidence = state.get("raw_evidence")
        if raw_evidence:
            for result in search_results:
                from core.models.commodity_models import NewsItem
                news_item = NewsItem(
                    title=result.get("title", ""),
                    summary=result.get("summary", ""),
                    source_name=result.get("source", ""),
                    source_url=result.get("url", ""),
                    published_at=result.get("published_at", ""),
                    related_commodities=[raw_evidence.get("commodity_or_chain", "")],
                    related_regions=["全球"],
                    tags=["search_result"]
                )
                raw_evidence["news"].append(news_item)
            
            state["raw_evidence"] = raw_evidence
            print(f"[搜索执行] 已将搜索结果合并到证据包")
        
    except Exception as e:
        error_msg = f"搜索执行失败: {str(e)}"
        print(f"[搜索执行] {error_msg}")
        state["search_results"] = []
    
    return state
