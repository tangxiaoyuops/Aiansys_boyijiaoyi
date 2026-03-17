"""
大宗商品数据采集Agent
从公开网站/API获取供给、价格、新闻数据
集成智能数据获取功能
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.commodity_fetcher import create_commodity_fetcher
from core.agents.smart_data_fetcher_agent import smart_fetch_commodity_data, smart_process_data


def commodity_fetch_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    数据采集节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[数据采集] 开始采集数据")
    
    commodity_or_chain = state.get("commodity_or_chain", "")
    time_range = state.get("time_range")
    
    try:
        # 使用智能数据获取 agent 构造查询配置
        print(f"[数据采集] 使用智能数据获取 agent 构造查询配置...")
        query_config = smart_fetch_commodity_data(
            commodity=commodity_or_chain,
            time_range=time_range,
            data_type="price"
        )
        
        print(f"[数据采集] 智能配置: {query_config}")
        
        fetcher = create_commodity_fetcher()
        raw_evidence = fetcher.fetch_commodity_data(
            commodity_or_chain=commodity_or_chain,
            time_range=time_range
        )
        
        # 使用智能数据处理 agent 处理数据
        if raw_evidence and raw_evidence.get("prices"):
            print(f"[数据采集] 使用智能数据处理 agent 处理价格数据...")
            processed_prices = smart_process_data(
                raw_data=raw_evidence.get("prices"),
                commodity=commodity_or_chain,
                data_type="price"
            )
            print(f"[数据采集] 处理结果: {processed_prices}")
        
        state["raw_evidence"] = raw_evidence
        state["fetch_error"] = None
        state["query_config"] = query_config
        state["processed_data"] = processed_prices if 'processed_prices' in locals() else None
        
        print(f"[数据采集] 数据采集成功")
        print(f"[数据采集] 供给链: {len(raw_evidence['supply_chain'])} 条")
        print(f"[数据采集] 价格: {len(raw_evidence['prices'])} 条")
        print(f"[数据采集] 新闻: {len(raw_evidence['news'])} 条")
        
    except Exception as e:
        error_msg = f"数据采集失败: {str(e)}"
        print(f"[数据采集] {error_msg}")
        state["fetch_error"] = error_msg
        state["raw_evidence"] = None
    
    return state
