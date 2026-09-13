"""
博弈交易法专用工具集
基于五阶段理论和博弈分析的专业工具
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# 添加项目路径
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from core.agent_framework.tools.base import ToolMetadata
from core.agent_framework.tools.function_tool import FunctionTool
from core.agent_framework.registry import ToolRegistry


# ========== 1. O点识别工具 ==========

def check_o_point(stock_code: str, lookback_days: int = 730) -> Dict[str, Any]:
    """
    识别O点（原始低点）
    
    Args:
        stock_code: 股票代码
        lookback_days: 回看天数（默认730天，约2年）
    
    Returns:
        O点识别结果
    """
    from core.tools.data_fetcher import fetch_stock_data
    
    try:
        # 获取长期数据
        df = fetch_stock_data(stock_code, lookback_days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 找到最低点
        min_idx = df['收盘'].idxmin()
        o_point_price = float(df.loc[min_idx, '收盘'])
        o_point_date = df.loc[min_idx, '日期']
        
        # 当前价格
        current_price = float(df.iloc[-1]['收盘'])
        
        # 计算距离O点的幅度
        distance_from_o = (current_price - o_point_price) / o_point_price * 100
        
        # 检查是否破位
        recent_low = float(df['收盘'].tail(60).min())
        is_broken = bool(recent_low < o_point_price * 0.95)  # 破位5%
        
        # 计算O点后的涨幅
        df_after_o = df[df['日期'] >= o_point_date].copy()
        if len(df_after_o) > 0:
            gain_after_o = (current_price - o_point_price) / o_point_price * 100
            days_after_o = len(df_after_o)
        else:
            gain_after_o = 0
            days_after_o = 0
        
        return {
            "status": "success",
            "o_point_price": round(o_point_price, 2),
            "o_point_date": str(o_point_date),
            "current_price": round(current_price, 2),
            "distance_from_o_pct": round(distance_from_o, 2),
            "is_broken": bool(is_broken),
            "gain_after_o_pct": round(gain_after_o, 2),
            "days_after_o": int(days_after_o),
            "trend_exists": bool(not is_broken),
            "message": f"O点识别完成：价格{o_point_price:.2f}，当前距离{distance_from_o:.2f}%，趋势{'存在' if not is_broken else '已破坏'}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 2. 洗盘识别工具 ==========

def identify_washout(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """
    识别洗盘特征和强度
    
    Args:
        stock_code: 股票代码
        days: 分析天数
    
    Returns:
        洗盘识别结果
    """
    from core.tools.data_fetcher import fetch_stock_data
    from core.tools.technical_analyzer import compute_max_drawdown
    
    try:
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 计算洗盘指标
        # 1. 下跌幅度（恐惧程度）
        # compute_max_drawdown 返回的是float值,不是字典
        max_drawdown = compute_max_drawdown(df, window=60)
        if max_drawdown is None:
            max_drawdown = 0.0
        
        # 2. 震荡频率（焦虑程度）
        df['daily_change'] = df['收盘'].pct_change()
        volatility = df['daily_change'].std() * np.sqrt(252) * 100
        
        # 3. 阴线比例
        down_days = len(df[df['收盘'] < df['收盘'].shift(1)])
        total_days = len(df)
        down_ratio = down_days / total_days if total_days > 0 else 0
        
        # 4. 成交量变化
        recent_volume = df['成交量'].tail(20).mean()
        avg_volume = df['成交量'].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # 5. 识别洗盘类型
        # K线组合洗盘：连续3-5天下跌
        df['is_down'] = df['收盘'] < df['收盘'].shift(1)
        consecutive_down = 0
        max_consecutive_down = 0
        for is_down in df['is_down']:
            if is_down:
                consecutive_down += 1
                max_consecutive_down = max(max_consecutive_down, consecutive_down)
            else:
                consecutive_down = 0
        
        # 波段洗盘：一段时间的下跌
        recent_trend = df['收盘'].tail(30).values
        trend_direction = "下跌" if recent_trend[-1] < recent_trend[0] else "上涨"
        
        # 洗盘效果评分
        fear_score = min(max_drawdown / 20, 1.0)  # 最大回撤20%为满分
        anxiety_score = min(volatility / 40, 1.0)  # 波动率40%为满分
        volume_score = min(abs(volume_ratio - 1), 0.5) * 2  # 缩量程度
        
        washout_effect = fear_score * 0.4 + anxiety_score * 0.3 + volume_score * 0.3
        
        # 判断是否在洗盘
        is_washout = bool(
            max_drawdown > 10 and  # 有一定跌幅
            volume_ratio < 0.8 and  # 成交量萎缩
            down_ratio > 0.5  # 阴线较多
        )
        
        # 洗盘类型
        washout_type = "unknown"
        if max_consecutive_down >= 3:
            washout_type = "K线组合洗盘"
        elif trend_direction == "下跌" and max_drawdown > 15:
            washout_type = "波段洗盘"
        
        return {
            "status": "success",
            "is_washout": is_washout,
            "washout_type": washout_type,
            "washout_effect": round(washout_effect, 2),
            "fear_score": round(fear_score, 2),
            "anxiety_score": round(anxiety_score, 2),
            "volume_score": round(volume_score, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "down_ratio": round(down_ratio, 2),
            "volume_ratio": round(volume_ratio, 2),
            "max_consecutive_down": max_consecutive_down,
            "trend_direction": trend_direction,
            "message": f"洗盘识别完成：{'是' if is_washout else '否'}，类型{washout_type}，效果{washout_effect:.2f}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 3. 出货识别工具 ==========

def identify_distribution(stock_code: str, days: int = 365) -> Dict[str, Any]:
    """
    识别出货特征
    
    Args:
        stock_code: 股票代码
        days: 分析天数
    
    Returns:
        出货识别结果
    """
    from core.tools.data_fetcher import fetch_stock_data
    
    try:
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 识别出货高点
        # 出货高点特征：高位震荡，成交量放大，散户买入多
        
        # 1. 找到相对高点
        rolling_high = df['收盘'].rolling(window=20, center=True).max()
        is_high_point = df['收盘'] == rolling_high
        high_points = df[is_high_point].copy()
        
        # 2. 分析高点特征
        distribution_signals = []
        
        for idx, row in high_points.iterrows():
            # 高点成交量
            volume_at_high = row['成交量']
            avg_volume = df['成交量'].mean()
            
            # 高点后的走势
            if idx < len(df) - 10:
                future_prices = df.iloc[idx+1:idx+11]['收盘'].values
                price_after = future_prices[-1]
                price_at_high = row['收盘']
                
                # 如果高点后下跌，可能是出货点
                if price_after < price_at_high * 0.95:  # 下跌5%以上
                    distribution_signals.append({
                        'date': str(row['日期']),
                        'price': float(row['收盘']),
                        'volume_ratio': float(volume_at_high / avg_volume),
                        'price_drop_pct': float((price_at_high - price_after) / price_at_high * 100)
                    })
        
        # 3. 判断出货规模
        washout_period = days  # 简化：使用分析周期
        
        if washout_period > 365:
            distribution_scale = "大规模出货"
            risk_level = "高"
        elif washout_period > 180:
            distribution_scale = "中等规模出货"
            risk_level = "中"
        else:
            distribution_scale = "小规模出货"
            risk_level = "低"
        
        # 4. 出货强度评分
        if len(distribution_signals) > 0:
            avg_price_drop = np.mean([s['price_drop_pct'] for s in distribution_signals])
            avg_volume_ratio = np.mean([s['volume_ratio'] for s in distribution_signals])
            
            distribution_strength = (
                min(len(distribution_signals) / 5, 1.0) * 0.4 +  # 出货点数量
                min(avg_price_drop / 10, 1.0) * 0.3 +  # 平均跌幅
                min(avg_volume_ratio / 2, 1.0) * 0.3   # 成交量放大
            )
        else:
            distribution_strength = 0
            avg_price_drop = 0
            avg_volume_ratio = 0
        
        return {
            "status": "success",
            "has_distribution": bool(len(distribution_signals) > 0),
            "distribution_scale": distribution_scale,
            "distribution_strength": round(distribution_strength, 2),
            "distribution_points_count": len(distribution_signals),
            "avg_price_drop_pct": round(avg_price_drop, 2),
            "avg_volume_ratio": round(avg_volume_ratio, 2),
            "risk_level": risk_level,
            "recent_distribution_points": distribution_signals[-3:] if distribution_signals else [],
            "message": f"出货识别完成：{'有' if len(distribution_signals) > 0 else '无'}，规模{distribution_scale}，强度{distribution_strength:.2f}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 4. 情绪比例分析工具 ==========

def analyze_emotion_ratio(stock_code: str, days: int = 90) -> Dict[str, Any]:
    """
    分析情绪比例关系
    
    Args:
        stock_code: 股票代码
        days: 分析天数
    
    Returns:
        情绪比例关系分析结果
    """
    from core.tools.data_fetcher import fetch_stock_data
    
    try:
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 分段分析：前段（出货）+ 后段（洗盘）
        mid_point = len(df) // 2
        first_half = df.iloc[:mid_point].copy()
        second_half = df.iloc[mid_point:].copy()
        
        # 分析前段（假设为出货段）
        first_gain = (first_half['收盘'].iloc[-1] - first_half['收盘'].iloc[0]) / first_half['收盘'].iloc[0] * 100
        first_up_days = len(first_half[first_half['收盘'] > first_half['收盘'].shift(1)])
        first_volume_ratio = first_half['成交量'].mean() / df['成交量'].mean()
        
        # 出货好看度评分
        distribution_beauty = (
            min(max(first_gain, 0) / 20, 1.0) * 0.4 +  # 涨幅
            min(first_up_days / len(first_half), 1.0) * 0.3 +  # 阳线比例
            min(first_volume_ratio / 1.5, 1.0) * 0.3  # 成交量放大
        )
        
        # 分析后段（假设为洗盘段）
        second_gain = (second_half['收盘'].iloc[-1] - second_half['收盘'].iloc[0]) / second_half['收盘'].iloc[0] * 100
        second_down_days = len(second_half[second_half['收盘'] < second_half['收盘'].shift(1)])
        second_volume_ratio = second_half['成交量'].mean() / df['成交量'].mean()
        
        # 洗盘难看度评分
        washout_ugliness = (
            min(abs(min(second_gain, 0)) / 15, 1.0) * 0.4 +  # 跌幅
            min(second_down_days / len(second_half), 1.0) * 0.3 +  # 阴线比例
            min(abs(second_volume_ratio - 1), 0.5) * 2 * 0.3  # 缩量程度
        )
        
        # 情绪比例关系判断
        # 较为好看的出货 + 非常难看的洗盘 = 后市看涨
        # 较为难看的洗盘后 + 直接跟非常好看的出货 = 后市看跌
        
        if distribution_beauty > 0.6 and washout_ugliness > 0.6:
            outlook = "看涨"
            confidence = (distribution_beauty + washout_ugliness) / 2
        elif washout_ugliness > 0.6 and distribution_beauty < 0.4:
            outlook = "看跌"
            confidence = washout_ugliness
        else:
            outlook = "中性"
            confidence = 0.5
        
        return {
            "status": "success",
            "distribution_beauty": round(distribution_beauty, 2),
            "washout_ugliness": round(washout_ugliness, 2),
            "emotion_ratio": round(distribution_beauty / (washout_ugliness + 0.01), 2),
            "outlook": outlook,
            "confidence": round(confidence, 2),
            "first_half_gain_pct": round(first_gain, 2),
            "second_half_gain_pct": round(second_gain, 2),
            "message": f"情绪比例分析：出货好看度{distribution_beauty:.2f}，洗盘难看度{washout_ugliness:.2f}，展望{outlook}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 5. 锚定状态检查工具 ==========

def check_anchor_status(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """
    检查多方/空方锚定状态
    
    Args:
        stock_code: 股票代码
        days: 分析天数
    
    Returns:
        锚定状态分析结果
    """
    from core.tools.data_fetcher import fetch_stock_data
    
    try:
        df = fetch_stock_data(stock_code, days)
        
        if df.empty:
            return {
                "status": "error",
                "error": f"无法获取股票 {stock_code} 的数据"
            }
        
        # 多方锚定检查
        # 特征：阳线个头越来越大，散户愿意买入
        
        df['up_days'] = df['收盘'] > df['收盘'].shift(1)
        df['up_pct'] = df['收盘'].pct_change() * 100
        
        # 近期上涨天数
        recent_up_days = df['up_days'].tail(20).sum()
        recent_up_pct = df[df['up_days']]['up_pct'].tail(10).mean()
        
        # 阳线越来越大趋势
        up_candles = df[df['up_days']]['up_pct'].tail(20).values
        if len(up_candles) >= 5:
            up_trend = float(np.polyfit(range(len(up_candles)), up_candles, 1)[0])
            is_bull_anchor = bool(up_trend > 0 and recent_up_days > 12)
        else:
            is_bull_anchor = False
            up_trend = 0.0
        
        # 空方锚定检查
        # 特征：下跌初期恐怖性下跌，持续补空锚
        
        df['down_pct'] = df['收盘'].pct_change() * 100
        recent_down_pct = df[df['收盘'] < df['收盘'].shift(1)]['down_pct'].tail(10).mean()
        
        # 恐怖性下跌
        scary_down_days = len(df[df['down_pct'] < -5])  # 单日跌幅超过5%
        
        # 是否有补空锚（跌破前低）
        recent_low = float(df['收盘'].tail(30).min())
        previous_low = float(df['收盘'].iloc[:-30].min()) if len(df) > 30 else recent_low
        is_filling_anchor = bool(recent_low < previous_low)
        
        is_bear_anchor = bool(scary_down_days > 2 or (abs(recent_down_pct) > 3 and is_filling_anchor))
        
        # 锚定强度
        if is_bull_anchor:
            anchor_type = "多方锚定"
            anchor_strength = min((recent_up_days / 20 + abs(up_trend) / 0.5) / 2, 1.0)
        elif is_bear_anchor:
            anchor_type = "空方锚定"
            anchor_strength = min((scary_down_days / 5 + abs(recent_down_pct) / 5) / 2, 1.0)
        else:
            anchor_type = "无明确锚定"
            anchor_strength = 0
        
        return {
            "status": "success",
            "anchor_type": anchor_type,
            "is_bull_anchor": bool(is_bull_anchor),
            "is_bear_anchor": bool(is_bear_anchor),
            "anchor_strength": round(anchor_strength, 2),
            "recent_up_days": int(recent_up_days),
            "recent_up_pct_avg": round(recent_up_pct, 2) if not pd.isna(recent_up_pct) else 0,
            "scary_down_days": int(scary_down_days),
            "is_filling_anchor": bool(is_filling_anchor),
            "message": f"锚定状态：{anchor_type}，强度{anchor_strength:.2f}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "stock_code": stock_code
        }


# ========== 创建博弈交易法工具注册中心 ==========

def create_boyi_analysis_registry() -> ToolRegistry:
    """
    创建博弈交易法专用工具注册中心
    
    Returns:
        配置好的工具注册中心
    """
    registry = ToolRegistry()
    
    # 1. O点识别工具
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
    
    # 2. 洗盘识别工具
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
    
    # 3. 出货识别工具
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
    
    # 4. 情绪比例分析工具
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
    
    # 5. 锚定状态检查工具
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


# 如果直接运行，测试工具
if __name__ == "__main__":
    print("=" * 80)
    print("博弈交易法工具集测试")
    print("=" * 80)
    
    # 测试股票代码
    test_code = "000001"
    
    print(f"\n测试股票: {test_code}")
    print("-" * 80)
    
    # 测试O点识别
    print("\n1. O点识别测试:")
    result = check_o_point(test_code)
    print(f"   状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   O点价格: {result['o_point_price']}")
        print(f"   当前价格: {result['current_price']}")
        print(f"   趋势存在: {result['trend_exists']}")
    
    # 测试洗盘识别
    print("\n2. 洗盘识别测试:")
    result = identify_washout(test_code)
    print(f"   状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   是否洗盘: {result['is_washout']}")
        print(f"   洗盘类型: {result['washout_type']}")
        print(f"   洗盘效果: {result['washout_effect']}")
    
    print("\n" + "=" * 80)
