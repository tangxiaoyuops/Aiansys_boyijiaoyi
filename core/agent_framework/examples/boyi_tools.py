"""
博弈交易工具集
为博弈交易Agent框架提供专用工具
"""
from typing import Dict, Any
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from core.agent_framework.tools.base import ToolMetadata
from core.agent_framework.tools.function_tool import FunctionTool
from core.agent_framework.tools.agent_tool import AgentTool
from core.agent_framework.tools.workflow_tool import WorkflowTool
from core.agent_framework.registry import ToolRegistry


# ========== 数据获取函数 ==========

def fetch_kline_data(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """
    获取K线数据
    
    Args:
        stock_code: 股票代码
        days: 天数
    
    Returns:
        K线数据
    """
    # 这里应该调用实际的数据获取接口
    # 示例返回模拟数据
    return {
        "stock_code": stock_code,
        "days": days,
        "data": [
            {
                "date": "2024-01-01",
                "open": 10.0,
                "high": 10.5,
                "low": 9.8,
                "close": 10.2,
                "volume": 1000000,
                "change_pct": 2.0
            }
        ],
        "message": "K线数据获取成功(模拟数据)"
    }


def calculate_indicators(kline_data: list) -> Dict[str, Any]:
    """
    计算技术指标
    
    Args:
        kline_data: K线数据列表
    
    Returns:
        技术指标
    """
    # 这里应该调用实际的指标计算逻辑
    # 示例返回模拟数据
    return {
        "ma5": 10.1,
        "ma20": 10.0,
        "ma60": 9.8,
        "volatility_20": 0.05,
        "max_drawdown_60": -0.15,
        "gain_20": 0.08,
        "gain_60": 0.12,
        "message": "技术指标计算成功(模拟数据)"
    }


def get_stock_info(stock_code: str) -> Dict[str, Any]:
    """
    获取股票基本信息
    
    Args:
        stock_code: 股票代码
    
    Returns:
        股票基本信息
    """
    # 这里应该调用实际的股票信息接口
    return {
        "stock_code": stock_code,
        "stock_name": "示例股票",
        "industry": "示例行业",
        "market_cap": 1000000000,
        "message": "股票信息获取成功(模拟数据)"
    }


# ========== 博弈交易分析函数 ==========

def analyze_stage(stock_code: str, kline_data: list) -> Dict[str, Any]:
    """
    分析股票阶段(简化版)
    
    Args:
        stock_code: 股票代码
        kline_data: K线数据
    
    Returns:
        阶段分析结果
    """
    # 这里应该调用实际的阶段分析逻辑
    return {
        "stage": 2,
        "stage_name": "二阶段",
        "confidence": 0.75,
        "o_point": {
            "has_o_point": True,
            "date": "2024-01-15",
            "price": 9.5
        },
        "reasoning": "根据K线形态和技术指标分析,当前处于二阶段",
        "message": "阶段分析完成(模拟数据)"
    }


def detect_washout(stock_code: str, stage_info: dict) -> Dict[str, Any]:
    """
    检测洗盘(简化版)
    
    Args:
        stock_code: 股票代码
        stage_info: 阶段信息
    
    Returns:
        洗盘检测结果
    """
    return {
        "has_washout": True,
        "washout_type": "波段洗盘",
        "intensity": "中等",
        "effect": "良好",
        "reasoning": "检测到明显的洗盘特征",
        "message": "洗盘检测完成(模拟数据)"
    }


def analyze_distribution(stock_code: str, kline_data: list) -> Dict[str, Any]:
    """
    分析出货规模(简化版)
    
    Args:
        stock_code: 股票代码
        kline_data: K线数据
    
    Returns:
        出货分析结果
    """
    return {
        "scale": "medium",
        "scale_name": "中等规模",
        "cycle_days": 90,
        "start_date": "2023-10-01",
        "end_date": "2023-12-30",
        "reasoning": "检测到中等规模出货特征",
        "message": "出货分析完成(模拟数据)"
    }


def find_trading_points(stock_code: str, stage_info: dict, washout_info: dict) -> Dict[str, Any]:
    """
    寻找买卖点(简化版)
    
    Args:
        stock_code: 股票代码
        stage_info: 阶段信息
        washout_info: 洗盘信息
    
    Returns:
        买卖点信息
    """
    return {
        "buy_points": [
            {
                "type": "洗盘点",
                "price": 10.0,
                "confidence": 0.8,
                "reason": "洗盘结束后的反弹点"
            }
        ],
        "sell_points": [
            {
                "type": "止盈点",
                "price": 12.0,
                "confidence": 0.7,
                "reason": "二阶段目标价位"
            }
        ],
        "message": "买卖点识别完成(模拟数据)"
    }


# ========== 创建博弈交易工具注册中心 ==========

def create_boyi_tool_registry() -> ToolRegistry:
    """
    创建博弈交易工具注册中心
    
    Returns:
        配置好的工具注册中心
    """
    registry = ToolRegistry()
    
    # 注册数据获取工具
    registry.register_tool(FunctionTool(
        func=fetch_kline_data,
        metadata=ToolMetadata(
            name="fetch_kline",
            description="获取股票K线数据,包括开盘价、最高价、最低价、收盘价、成交量等",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码,如'000001'"
                },
                "days": {
                    "type": "integer",
                    "description": "获取最近N天的数据,默认180天",
                    "default": 180
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["data_fetch"],
            cost_level="low",
            estimated_time="2-3s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=calculate_indicators,
        metadata=ToolMetadata(
            name="calc_indicators",
            description="计算技术指标,包括均线、波动率、最大回撤、涨跌幅等",
            tool_type="function",
            parameters={
                "kline_data": {
                    "type": "array",
                    "description": "K线数据数组"
                }
            },
            required_parameters=["kline_data"],
            capabilities=["indicator_calculation"],
            cost_level="free",
            estimated_time="1-2s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=get_stock_info,
        metadata=ToolMetadata(
            name="get_stock_info",
            description="获取股票基本信息,包括名称、行业、市值等",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            required_parameters=["stock_code"],
            capabilities=["data_fetch"],
            cost_level="low",
            estimated_time="1-2s"
        )
    ))
    
    # 注册分析工具
    registry.register_tool(FunctionTool(
        func=analyze_stage,
        metadata=ToolMetadata(
            name="analyze_stage",
            description="分析股票当前所处的阶段(一至五阶段),识别O点",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "kline_data": {
                    "type": "array",
                    "description": "K线数据"
                }
            },
            required_parameters=["stock_code", "kline_data"],
            capabilities=["stage_recognition", "o_point"],
            cost_level="medium",
            estimated_time="10-15s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=detect_washout,
        metadata=ToolMetadata(
            name="detect_washout",
            description="检测股票是否存在洗盘行为,判断洗盘类型和效果",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "stage_info": {
                    "type": "object",
                    "description": "阶段分析结果"
                }
            },
            required_parameters=["stock_code", "stage_info"],
            capabilities=["washout"],
            cost_level="medium",
            estimated_time="5-10s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=analyze_distribution,
        metadata=ToolMetadata(
            name="analyze_distribution",
            description="分析股票出货规模和周期,判断出货类型",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "kline_data": {
                    "type": "array",
                    "description": "K线数据"
                }
            },
            required_parameters=["stock_code", "kline_data"],
            capabilities=["distribution"],
            cost_level="medium",
            estimated_time="10-15s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=find_trading_points,
        metadata=ToolMetadata(
            name="find_trading_points",
            description="根据阶段和洗盘信息,识别潜在的买卖点",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "stage_info": {
                    "type": "object",
                    "description": "阶段分析结果"
                },
                "washout_info": {
                    "type": "object",
                    "description": "洗盘分析结果"
                }
            },
            required_parameters=["stock_code", "stage_info", "washout_info"],
            capabilities=["trading_points"],
            cost_level="medium",
            estimated_time="5-10s"
        )
    ))
    
    return registry


# ========== 创建博弈交易主控Agent ==========

def create_boyi_master_agent(llm_client, max_iterations: int = 10):
    """
    创建博弈交易主控Agent
    
    Args:
        llm_client: LLM客户端实例
        max_iterations: 最大迭代次数
    
    Returns:
        配置好的Agent实例
    """
    from core.agent_framework.agents import ReActAgent
    
    # 创建工具注册中心
    registry = create_boyi_tool_registry()
    
    # 创建Agent
    agent = ReActAgent(
        name="boyi_master",
        tool_registry=registry,
        llm_client=llm_client,
        max_iterations=max_iterations
    )
    
    return agent, registry


if __name__ == "__main__":
    # 测试工具注册
    registry = create_boyi_tool_registry()
    
    print("="*60)
    print("博弈交易工具注册中心")
    print("="*60)
    print(f"\n已注册工具数量: {len(registry)}")
    print(f"\n工具列表:")
    for tool in registry:
        print(f"  - {tool.metadata.name}: {tool.metadata.description}")
    
    print(f"\n能力索引:")
    for capability, tools in registry.capabilities_index.items():
        print(f"  {capability}: {tools}")
    
    print(f"\n工具描述示例:")
    print(registry.get_tools_description(["fetch_kline", "analyze_stage"]))
