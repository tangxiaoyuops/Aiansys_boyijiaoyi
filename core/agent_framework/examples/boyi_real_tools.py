"""
博弈交易真实工具集
连接项目现有的真实数据和分析功能
"""
from typing import Dict, Any
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from core.agent_framework.tools.base import ToolMetadata
from core.agent_framework.tools.function_tool import FunctionTool
from core.agent_framework.registry import ToolRegistry


# ========== 真实数据获取函数 ==========

def fetch_real_kline_data(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """
    获取真实K线数据
    
    Args:
        stock_code: 股票代码
        days: 天数
    
    Returns:
        K线数据
    """
    from core.tools.data_fetcher import fetch_stock_data
    import pandas as pd
    
    try:
        # 调用真实的数据获取函数
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据",
                "stock_code": stock_code
            }
        
        # 转换为字典格式
        kline_data = df.to_dict('records')
        
        # 获取股票名称
        from core.tools.data_fetcher import get_stock_name
        stock_name = get_stock_name(stock_code)
        
        return {
            "status": "success",
            "stock_code": stock_code,
            "stock_name": stock_name,
            "days": len(kline_data),
            "data": kline_data[-min(days, len(kline_data)):],  # 返回最近N天
            "latest_price": float(df.iloc[-1]['收盘']) if not df.empty else 0,
            "message": f"成功获取 {stock_name}({stock_code}) 最近 {len(kline_data)} 天K线数据"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


def calculate_real_indicators(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """
    计算真实技术指标
    
    Args:
        stock_code: 股票代码
        days: 天数
    
    Returns:
        技术指标
    """
    from core.tools.technical_analyzer import (
        calculate_ma,
        calculate_macd,
        calculate_rsi,
        compute_gains,
        compute_max_drawdown,
        compute_volatility,
        compute_days_from_high
    )
    from core.tools.data_fetcher import fetch_stock_data
    
    try:
        # 获取K线数据
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 计算技术指标
        indicators = {
            "current_price": float(df.iloc[-1]['收盘']),
            "volume": float(df.iloc[-1]['成交量']) if '成交量' in df.columns else 0,
        }
        
        # 均线 - 使用DataFrame
        df_ma = calculate_ma(df, periods=[5, 20, 60])
        indicators.update({
            "ma5": float(df_ma.iloc[-1]['MA5']) if 'MA5' in df_ma.columns and not df_ma.empty else 0,
            "ma20": float(df_ma.iloc[-1]['MA20']) if 'MA20' in df_ma.columns and not df_ma.empty else 0,
            "ma60": float(df_ma.iloc[-1]['MA60']) if 'MA60' in df_ma.columns and not df_ma.empty else 0,
        })
        
        # MACD - 使用DataFrame
        df_macd = calculate_macd(df)
        indicators.update({
            "macd": float(df_macd.iloc[-1]['MACD']) if 'MACD' in df_macd.columns and not df_macd.empty else 0,
            "macd_signal": float(df_macd.iloc[-1]['MACD_Signal']) if 'MACD_Signal' in df_macd.columns and not df_macd.empty else 0,
            "macd_hist": float(df_macd.iloc[-1]['MACD_Hist']) if 'MACD_Hist' in df_macd.columns and not df_macd.empty else 0,
            "macd_positive": bool(df_macd.iloc[-1]['MACD_Hist'] > 0) if 'MACD_Hist' in df_macd.columns and not df_macd.empty else False,
        })
        
        # RSI - 使用DataFrame
        df_rsi = calculate_rsi(df)
        indicators["rsi"] = float(df_rsi.iloc[-1]['RSI']) if 'RSI' in df_rsi.columns and not df_rsi.empty else 50
        
        # 涨跌幅
        gains = compute_gains(df)
        indicators.update({
            "recent_gain_20d": gains.get('gain_20d', 0),
            "recent_gain_60d": gains.get('gain_60d', 0),
            "recent_gain_120d": gains.get('gain_120d', 0),
        })
        
        # 最大回撤
        # compute_max_drawdown 返回float,不是字典
        max_dd_60 = compute_max_drawdown(df, window=60)
        max_dd_120 = compute_max_drawdown(df, window=120)
        indicators.update({
            "max_drawdown_60d": max_dd_60 if max_dd_60 is not None else 0,
            "max_drawdown_120d": max_dd_120 if max_dd_120 is not None else 0,
        })
        
        # 波动率
        # compute_volatility 返回float,不是字典
        vol_20 = compute_volatility(df, window=20)
        vol_60 = compute_volatility(df, window=60)
        indicators.update({
            "volatility_20d": vol_20 if vol_20 is not None else 0,
            "volatility_60d": vol_60 if vol_60 is not None else 0,
        })
        
        # 距离高点
        days_from_high, high_gap = compute_days_from_high(df)
        indicators.update({
            "days_from_high": days_from_high,
            "high_gap_pct": high_gap,
        })
        
        indicators["status"] = "success"
        indicators["message"] = "技术指标计算成功"
        
        return indicators
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


def analyze_real_stage(stock_code: str) -> Dict[str, Any]:
    """
    真实阶段分析
    
    Args:
        stock_code: 股票代码
    
    Returns:
        阶段分析结果
    """
    from core.agents.stage_analysis_agent import analyze_stage_with_llm
    from core.tools.data_fetcher import fetch_stock_data
    from core.tools.technical_analyzer import identify_stage_indicators
    
    try:
        # 获取数据
        df = fetch_stock_data(stock_code, 365)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 计算指标
        indicators = identify_stage_indicators(df)
        
        # 分析阶段
        result = analyze_stage_with_llm(df, indicators)
        
        result["status"] = "success"
        result["stock_code"] = stock_code
        result["message"] = f"阶段分析完成: {result.get('stage_name', '未知')}"
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 创建真实工具注册中心 ==========

def create_real_boyi_tool_registry() -> ToolRegistry:
    """
    创建真实博弈交易工具注册中心
    
    Returns:
        配置好的工具注册中心
    """
    registry = ToolRegistry()
    
    # 注册真实数据获取工具
    registry.register_tool(FunctionTool(
        func=fetch_real_kline_data,
        metadata=ToolMetadata(
            name="fetch_kline",
            description="获取股票真实K线数据,包括开盘价、最高价、最低价、收盘价、成交量等",
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
            capabilities=["data_fetch", "real_data"],
            cost_level="low",
            estimated_time="2-5s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=calculate_real_indicators,
        metadata=ToolMetadata(
            name="calc_indicators",
            description="计算真实技术指标,包括均线MA、MACD、RSI、波动率、最大回撤、涨跌幅等",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "days": {
                    "type": "integer",
                    "description": "计算最近N天的指标,默认180天",
                    "default": 180
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["indicator_calculation", "real_data"],
            cost_level="free",
            estimated_time="1-3s"
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=analyze_real_stage,
        metadata=ToolMetadata(
            name="analyze_stage",
            description="分析股票当前所处的真实阶段(一至五阶段),识别O点,计算置信度",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                }
            },
            required_parameters=["stock_code"],
            capabilities=["stage_recognition", "o_point", "real_analysis"],
            cost_level="medium",
            estimated_time="5-10s"
        )
    ))
    
    # ========== 集成博弈交易法专用工具 ==========
    from core.agent_framework.tools.boyi_analysis_tools import (
        check_o_point,
        identify_washout,
        identify_distribution,
        analyze_emotion_ratio,
        check_anchor_status
    )
    
    # 4. O点识别工具
    registry.register_tool(FunctionTool(
        func=check_o_point,
        metadata=ToolMetadata(
            name="check_o_point",
            description="识别O点（原始低点），判断趋势是否存在，O点不破则趋势存在",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码，如'000001'"
                },
                "lookback_days": {
                    "type": "integer",
                    "description": "回看天数，默认730天（约2年）",
                    "default": 730
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["lookback_days"],
            capabilities=["trend_analysis", "o_point_detection"],
            cost_level="low",
            estimated_time="1-2s"
        )
    ))
    
    # 5. 洗盘识别工具
    registry.register_tool(FunctionTool(
        func=identify_washout,
        metadata=ToolMetadata(
            name="identify_washout",
            description="识别洗盘特征和强度，包括洗盘类型（K线组合/波段）、恐惧程度、焦虑程度",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "days": {
                    "type": "integer",
                    "description": "分析天数，默认180天",
                    "default": 180
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["washout_detection", "emotion_analysis"],
            cost_level="low",
            estimated_time="1-3s"
        )
    ))
    
    # 6. 出货识别工具
    registry.register_tool(FunctionTool(
        func=identify_distribution,
        metadata=ToolMetadata(
            name="identify_distribution",
            description="识别出货特征，判断出货规模（大/中/小），评估出货强度和风险等级",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "days": {
                    "type": "integer",
                    "description": "分析天数，默认365天",
                    "default": 365
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["distribution_detection", "risk_assessment"],
            cost_level="medium",
            estimated_time="2-4s"
        )
    ))
    
    # 7. 情绪比例分析工具
    registry.register_tool(FunctionTool(
        func=analyze_emotion_ratio,
        metadata=ToolMetadata(
            name="analyze_emotion_ratio",
            description="分析情绪比例关系，评估出货好看度和洗盘难看度，判断后市走势",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "days": {
                    "type": "integer",
                    "description": "分析天数，默认90天",
                    "default": 90
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["emotion_analysis", "outlook_prediction"],
            cost_level="medium",
            estimated_time="1-3s"
        )
    ))
    
    # 8. 锚定状态检查工具
    registry.register_tool(FunctionTool(
        func=check_anchor_status,
        metadata=ToolMetadata(
            name="check_anchor_status",
            description="检查多方/空方锚定状态，识别散户思维被锚定的方向和强度",
            tool_type="function",
            parameters={
                "stock_code": {
                    "type": "string",
                    "description": "股票代码"
                },
                "days": {
                    "type": "integer",
                    "description": "分析天数，默认180天",
                    "default": 180
                }
            },
            required_parameters=["stock_code"],
            optional_parameters=["days"],
            capabilities=["anchor_detection", "sentiment_analysis"],
            cost_level="low",
            estimated_time="1-2s"
        )
    ))
    
    return registry


# ========== 兼容旧接口 ==========

def create_boyi_tool_registry() -> ToolRegistry:
    """
    创建博弈交易工具注册中心(兼容接口)
    默认使用真实工具
    """
    return create_real_boyi_tool_registry()


if __name__ == "__main__":
    # 测试真实工具
    print("="*60)
    print("测试真实博弈交易工具")
    print("="*60)
    
    # 测试数据获取
    print("\n测试数据获取:")
    result = fetch_real_kline_data("000001", 30)
    print(f"状态: {result.get('status')}")
    print(f"消息: {result.get('message')}")
    
    # 测试指标计算
    print("\n测试指标计算:")
    result = calculate_real_indicators("000001", 60)
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"当前价格: {result.get('current_price')}")
        print(f"MA20: {result.get('ma20')}")
        print(f"RSI: {result.get('rsi')}")
    
    # 测试阶段分析
    print("\n测试阶段分析:")
    result = analyze_real_stage("000001")
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"阶段: {result.get('stage_name')}")
        print(f"置信度: {result.get('confidence')}")
