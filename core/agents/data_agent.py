"""
数据获取Agent
"""
from core.models.state import AnalysisState
from core.tools.data_fetcher import fetch_stock_data, get_stock_name


def data_fetch_node(state: AnalysisState) -> AnalysisState:
    """数据获取节点"""
    stock_code = state.get("stock_code", "")
    days = state.get("days", 180)

    if not stock_code:
        raise ValueError("股票代码不能为空")

    try:
        # 获取股票数据（带重试和多数据源兜底）
        stock_data = fetch_stock_data(stock_code, days)
        stock_name = get_stock_name(stock_code)

        # 更新状态
        state["stock_data"] = stock_data
        state["stock_name"] = stock_name

        return state
    except Exception as e:
        error_msg = str(e)
        # 提供更友好的错误信息
        if "proxy" in error_msg.lower():
            raise Exception(
                f"获取股票数据失败: 网络代理配置问题。"
                f"请检查代理设置或取消代理配置。"
                f"原始错误: {error_msg}"
            )
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            raise Exception(
                f"获取股票数据失败: 网络连接问题。"
                f"请检查网络连接或稍后重试。"
                f"原始错误: {error_msg}"
            )
        else:
            raise Exception(f"获取股票数据失败: {error_msg}")

