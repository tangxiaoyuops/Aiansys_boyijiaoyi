"""
期货数据获取Agent
"""
from core.models.futures_state import FuturesAnalysisState
from core.tools.futures_data_fetcher import (
    fetch_futures_data,
    get_futures_name
)
from core.tools.vnpy_integration import get_futures_contract_info


def futures_data_fetch_node(state: FuturesAnalysisState) -> FuturesAnalysisState:
    """期货数据获取节点"""
    futures_code = state.get("futures_code", "")
    days = state.get("days", 180)

    print(f"[期货数据获取] 开始获取期货数据: {futures_code}, 天数: {days}")

    if not futures_code:
        print("[期货数据获取] 错误: 期货合约代码为空")
        raise ValueError("期货合约代码不能为空")

    try:
        # 获取合约信息
        print(f"[期货数据获取] 正在获取合约信息: {futures_code}")
        contract_info = get_futures_contract_info(futures_code)
        if contract_info:
            state["futures_name"] = contract_info.get("name", futures_code)
            state["exchange"] = contract_info.get("exchange", "SHFE")
            state["contract_month"] = contract_info.get("contract_month")
            state["product_code"] = contract_info.get("product_code")
            state["margin_rate"] = contract_info.get("margin_rate", 0.10)
            state["contract_multiplier"] = contract_info.get("multiplier", 10)
            print(f"[期货数据获取] 合约信息获取成功: {contract_info.get('name')}, 交易所: {contract_info.get('exchange')}, 保证金率: {contract_info.get('margin_rate', 0.10):.1%}")
        else:
            # 如果无法获取合约信息，使用默认值
            state["futures_name"] = get_futures_name(futures_code)
            state["exchange"] = "SHFE"
            state["margin_rate"] = 0.10
            state["contract_multiplier"] = 10
            print(f"[期货数据获取] 无法获取合约信息，使用默认值: 交易所=SHFE, 保证金率=10%")

        # 获取期货数据
        print(f"[期货数据获取] 正在从数据源获取K线数据...")
        try:
            futures_data = fetch_futures_data(futures_code, days)
            print(f"[期货数据获取] 数据获取成功: 共 {len(futures_data)} 条记录")
        except Exception as fetch_error:
            print(f"[期货数据获取] fetch_futures_data 调用失败: {fetch_error}")
            raise
        if not futures_data.empty:
            print(f"[期货数据获取] 数据时间范围: {futures_data.iloc[0]['日期']} 至 {futures_data.iloc[-1]['日期']}")
            print(f"[期货数据获取] 最新价格: {futures_data.iloc[-1]['收盘']:.2f}")

        # 更新状态
        state["futures_data"] = futures_data
        print(f"[期货数据获取] 数据获取节点完成")

        return state
    except Exception as e:
        error_msg = str(e)
        import traceback
        print(f"[期货数据获取] 数据获取节点异常: {error_msg}")
        print(f"[期货数据获取] 错误堆栈: {traceback.format_exc()}")
        
        # 提供更友好的错误信息
        if "proxy" in error_msg.lower():
            raise Exception(
                f"获取期货数据失败: 网络代理配置问题。"
                f"请检查代理设置或取消代理配置。"
                f"原始错误: {error_msg}"
            )
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            raise Exception(
                f"获取期货数据失败: 网络连接问题。"
                f"请检查网络连接或稍后重试。"
                f"原始错误: {error_msg}"
            )
        else:
            raise Exception(f"获取期货数据失败: {error_msg}")

