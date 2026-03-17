"""
大宗商品结构化分析Agent
对原始证据包做结构化分析
"""
from typing import Dict, Any
from core.models.commodity_state import CommodityAnalysisState
from core.tools.llm_client import call_llm


def commodity_structured_analysis_node(state: CommodityAnalysisState) -> CommodityAnalysisState:
    """
    结构化分析节点
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    print(f"[结构化分析] 开始结构化分析")
    
    raw_evidence = state.get("raw_evidence")
    
    if not raw_evidence:
        print("[结构化分析] 警告: 没有原始证据数据")
        state["structured_analysis"] = {
            "summary": "暂无数据",
            "classification": "unknown",
            "key_drivers": [],
            "confidence": 0.0
        }
        return state
    
    system_prompt = """你是一个大宗商品市场分析专家。请对提供的大宗商品数据进行结构化分析。

你需要分析以下内容：
1. 供给链摘要：产能、库存、贸易流等
2. 价格摘要：价格走势、价差变化等
3. 驱动因子：影响价格的关键因素
4. 市场分类：上涨/下跌/震荡
5. 置信度：分析的可信度（0-1）

请以JSON格式返回分析结果，格式如下：
{
    "summary": "整体分析摘要",
    "classification": "市场分类（bullish/bearish/neutral）",
    "key_drivers": ["驱动因子1", "驱动因子2", ...],
    "supply_chain_summary": "供给链摘要",
    "price_summary": "价格摘要",
    "confidence": 0.85
}"""

    user_prompt = f"""请分析以下大宗商品数据：

品种/产业链：{raw_evidence.get('commodity_or_chain', '未知')}
时间范围：{raw_evidence.get('time_range', '未指定')}

供给链数据（{len(raw_evidence.get('supply_chain', []))}条）：
{format_supply_chain(raw_evidence.get('supply_chain', []))}

价格数据（{len(raw_evidence.get('prices', []))}条）：
{format_prices(raw_evidence.get('prices', []))}

新闻数据（{len(raw_evidence.get('news', []))}条）：
{format_news(raw_evidence.get('news', []))}

请进行结构化分析。"""

    try:
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        import json
        structured_analysis = json.loads(result)
        
        state["structured_analysis"] = structured_analysis
        
        print(f"[结构化分析] 分析完成")
        print(f"[结构化分析] 市场分类: {structured_analysis.get('classification')}")
        print(f"[结构化分析] 置信度: {structured_analysis.get('confidence')}")
        
    except Exception as e:
        error_msg = f"结构化分析失败: {str(e)}"
        print(f"[结构化分析] {error_msg}")
        state["structured_analysis"] = {
            "summary": error_msg,
            "classification": "unknown",
            "key_drivers": [],
            "confidence": 0.0
        }
    
    return state


def format_supply_chain(supply_chain: list) -> str:
    """格式化供给链数据"""
    if not supply_chain:
        return "无数据"
    
    lines = []
    for item in supply_chain[:3]:
        lines.append(f"- 地区: {item.get('region')}, 产能: {item.get('capacity_or_output')}, 库存: {item.get('inventory')}")
    
    if len(supply_chain) > 3:
        lines.append(f"... 还有 {len(supply_chain) - 3} 条数据")
    
    return "\n".join(lines)


def format_prices(prices: list) -> str:
    """格式化价格数据"""
    if not prices:
        return "无数据"
    
    lines = []
    for item in prices[-5:]:
        lines.append(f"- {item.get('as_of_date')}: {item.get('value')} {item.get('unit')} ({item.get('price_type')})")
    
    if len(prices) > 5:
        lines.append(f"... 还有 {len(prices) - 5} 条数据")
    
    return "\n".join(lines)


def format_news(news: list) -> str:
    """格式化新闻数据"""
    if not news:
        return "无数据"
    
    lines = []
    for item in news[:3]:
        lines.append(f"- {item.get('published_at')}: {item.get('title')}")
        lines.append(f"  摘要: {item.get('summary')}")
    
    if len(news) > 3:
        lines.append(f"... 还有 {len(news) - 3} 条新闻")
    
    return "\n".join(lines)
