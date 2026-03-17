"""
智能数据获取Agent
使用大模型智能构造数据查询参数和处理数据
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
from core.tools.llm_client import call_llm


def smart_fetch_commodity_data(
    commodity: str,
    time_range: Optional[dict] = None,
    data_type: str = "price"
) -> Dict[str, Any]:
    """
    使用大模型智能获取商品数据
    
    Args:
        commodity: 商品名称（如：原油、玉米、甲醇）
        time_range: 时间范围 {"start": "2026-03-01", "end": "2026-03-08"}
        data_type: 数据类型（price, supply, news）
    
    Returns:
        结构化的数据
    """
    print(f"[智能数据获取] 开始获取 {commodity} 的 {data_type} 数据")
    
    # 构造提示词
    system_prompt = """你是一个专业的期货数据获取助手。你的任务是：
1. 根据商品名称，构造正确的期货合约代码
2. 确定数据源和查询参数
3. 返回结构化的查询配置

请严格按照JSON格式返回结果，不要添加任何其他内容。"""

    user_prompt = f"""请帮我构造获取以下商品数据的查询配置：

商品名称：{commodity}
数据类型：{data_type}
时间范围：{time_range or "最近60个交易日"}
当前日期：{datetime.now().strftime("%Y-%m-%d")}

请返回JSON格式的配置，包含以下字段：
{{
    "futures_code": "期货合约代码（主力连续合约，格式如：SC0、RB0、MA0）",
    "exchange": "交易所代码（SHFE、DCE、CZCE、INE等）",
    "product_name": "品种名称（中文）",
    "product_code": "品种代码（英文大写，如：SC、RB、MA）",
    "unit": "价格单位（如：元/吨、元/桶、元/克）",
    "contract_type": "合约类型（主力连续、近月合约等）",
    "data_source": "数据源（akshare、vnpy等）",
    "query_params": {{
        "symbol": "合约代码",
        "days": 数据天数,
        "其他参数": "值"
    }},
    "notes": "注意事项和说明"
}}

注意：
1. 主力连续合约代码格式：品种代码 + "0"（如：SC0、RB0、MA0）
2. 原油期货在INE交易所，代码是SC
3. 螺纹钢、热卷在SHFE交易所，代码是RB、HC
4. 玉米、豆粕在大连商品交易所DCE，代码是C、M
5. 甲醇在郑州商品交易所CZCE，代码是MA
6. 价格单位：原油是元/桶，其他大部分是元/吨，贵金属是元/克"""

    try:
        # 调用大模型
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1  # 低温度，确保输出稳定
        )
        
        print(f"[智能数据获取] LLM返回: {result}")
        
        # 解析JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            config = json.loads(json_match.group(0))
            print(f"[智能数据获取] 解析的配置: {json.dumps(config, ensure_ascii=False, indent=2)}")
            return config
        else:
            print(f"[智能数据获取] 未找到JSON格式")
            return get_default_config(commodity)
            
    except Exception as e:
        print(f"[智能数据获取] 失败: {e}")
        return get_default_config(commodity)


def get_default_config(commodity: str) -> Dict[str, Any]:
    """
    获取默认配置（备用方案）
    """
    # 品种名称到合约代码的映射
    commodity_mapping = {
        "原油": {"futures_code": "SC0", "exchange": "INE", "unit": "元/桶"},
        "布伦特": {"futures_code": "BRENT0", "exchange": "ICE", "unit": "美元/桶"},
        "WTI": {"futures_code": "WTI0", "exchange": "NYMEX", "unit": "美元/桶"},
        "玉米": {"futures_code": "C0", "exchange": "DCE", "unit": "元/吨"},
        "甲醇": {"futures_code": "MA0", "exchange": "CZCE", "unit": "元/吨"},
        "PTA": {"futures_code": "TA0", "exchange": "CZCE", "unit": "元/吨"},
        "螺纹钢": {"futures_code": "RB0", "exchange": "SHFE", "unit": "元/吨"},
        "热卷": {"futures_code": "HC0", "exchange": "SHFE", "unit": "元/吨"},
        "铁矿": {"futures_code": "I0", "exchange": "DCE", "unit": "元/吨"},
        "铜": {"futures_code": "CU0", "exchange": "SHFE", "unit": "元/吨"},
        "铝": {"futures_code": "AL0", "exchange": "SHFE", "unit": "元/吨"},
        "锌": {"futures_code": "ZN0", "exchange": "SHFE", "unit": "元/吨"},
        "黄金": {"futures_code": "AU0", "exchange": "SHFE", "unit": "元/克"},
        "白银": {"futures_code": "AG0", "exchange": "SHFE", "unit": "元/千克"},
        "豆粕": {"futures_code": "M0", "exchange": "DCE", "unit": "元/吨"},
        "豆油": {"futures_code": "Y0", "exchange": "DCE", "unit": "元/吨"},
        "大豆": {"futures_code": "A0", "exchange": "DCE", "unit": "元/吨"},
        "棉花": {"futures_code": "CF0", "exchange": "CZCE", "unit": "元/吨"},
        "白糖": {"futures_code": "SR0", "exchange": "CZCE", "unit": "元/吨"},
        "橡胶": {"futures_code": "RU0", "exchange": "SHFE", "unit": "元/吨"},
        "焦煤": {"futures_code": "JM0", "exchange": "DCE", "unit": "元/吨"},
        "焦炭": {"futures_code": "J0", "exchange": "DCE", "unit": "元/吨"},
        "PP": {"futures_code": "PP0", "exchange": "DCE", "unit": "元/吨"},
        "PVC": {"futures_code": "V0", "exchange": "DCE", "unit": "元/吨"},
        "乙二醇": {"futures_code": "EG0", "exchange": "DCE", "unit": "元/吨"},
        "尿素": {"futures_code": "UR0", "exchange": "CZCE", "unit": "元/吨"},
        "纯碱": {"futures_code": "SA0", "exchange": "CZCE", "unit": "元/吨"},
        "玻璃": {"futures_code": "FG0", "exchange": "CZCE", "unit": "元/吨"},
    }
    
    config = commodity_mapping.get(commodity, {
        "futures_code": f"{commodity[:2].upper()}0",
        "exchange": "SHFE",
        "unit": "元/吨"
    })
    
    return {
        "futures_code": config["futures_code"],
        "exchange": config["exchange"],
        "product_name": commodity,
        "product_code": config["futures_code"][:-1],
        "unit": config["unit"],
        "contract_type": "主力连续",
        "data_source": "akshare",
        "query_params": {
            "symbol": config["futures_code"],
            "days": 60
        },
        "notes": "使用默认配置"
    }


def smart_process_data(
    raw_data: Any,
    commodity: str,
    data_type: str
) -> Dict[str, Any]:
    """
    使用大模型智能处理原始数据
    
    Args:
        raw_data: 原始数据（可能是DataFrame、JSON等）
        commodity: 商品名称
        data_type: 数据类型
    
    Returns:
        处理后的结构化数据
    """
    print(f"[智能数据处理] 开始处理 {commodity} 的 {data_type} 数据")
    
    # 如果数据为空，返回空结果
    if raw_data is None:
        return {"success": False, "error": "数据为空"}
    
    # 构造提示词
    system_prompt = """你是一个专业的数据处理助手。你的任务是：
1. 分析原始数据的格式和内容
2. 提取关键信息
3. 返回结构化的数据

请严格按照JSON格式返回结果。"""

    # 将原始数据转换为字符串
    if hasattr(raw_data, 'to_dict'):
        # DataFrame - 获取最新的10条数据
        data_str = raw_data.tail(10).to_string()  # ✅ 使用最新的10条数据
    elif isinstance(raw_data, list):
        data_str = str(raw_data[-10:])  # ✅ 使用最新的10条数据
    else:
        data_str = str(raw_data)
    
    user_prompt = f"""请帮我处理以下原始数据：

商品名称：{commodity}
数据类型：{data_type}
原始数据（前10条）：
{data_str}

请返回JSON格式的处理结果，包含以下字段：
{{
    "success": true/false,
    "data_count": 数据条数,
    "latest_value": 最新值,
    "latest_date": 最新日期,
    "data_range": {{
        "min": 最小值,
        "max": 最大值,
        "avg": 平均值
    }},
    "trend": "趋势描述（上涨、下跌、震荡等）",
    "anomalies": ["异常点说明"],
    "processed_data": [处理后的数据列表]
}}"""

    try:
        # 调用大模型
        result = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )
        
        print(f"[智能数据处理] LLM返回: {result[:200]}...")
        
        # 解析JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            processed = json.loads(json_match.group(0))
            print(f"[智能数据处理] 处理成功")
            return processed
        else:
            return {"success": False, "error": "无法解析LLM返回"}
            
    except Exception as e:
        print(f"[智能数据处理] 失败: {e}")
        return {"success": False, "error": str(e)}
