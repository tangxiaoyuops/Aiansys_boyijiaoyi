"""
测试自定义JSON编码器
验证能否正确处理Pandas Timestamp等类型
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, date
from decimal import Decimal

# 导入自定义编码器
from server.app import CustomJSONEncoder, safe_json_dumps


def test_json_encoder():
    """测试自定义JSON编码器"""
    
    print("=" * 80)
    print("测试自定义JSON编码器")
    print("=" * 80)
    
    # 测试数据：包含各种特殊类型
    test_data = {
        "pandas_timestamp": pd.Timestamp("2024-01-15 10:30:00"),
        "datetime": datetime.now(),
        "date": date.today(),
        "numpy_int": np.int64(100),
        "numpy_float": np.float64(3.14159),
        "numpy_array": np.array([1, 2, 3, 4, 5]),
        "decimal": Decimal("123.45"),
        "nan": float('nan'),
        "inf": float('inf'),
        "normal_string": "测试字符串",
        "normal_int": 123,
        "normal_float": 45.67,
    }
    
    print("\n测试数据类型:")
    for key, value in test_data.items():
        print(f"  {key}: {type(value).__name__}")
    
    # 测试标准JSON编码器（应该失败）
    print("\n" + "-" * 80)
    print("测试标准JSON编码器:")
    try:
        result = json.dumps(test_data)
        print("  [FAIL] 标准编码器成功了？这不应该发生")
    except TypeError as e:
        print(f"  [OK] 标准编码器失败（预期）: {e}")
    
    # 测试自定义JSON编码器
    print("\n" + "-" * 80)
    print("测试自定义JSON编码器:")
    try:
        result = safe_json_dumps(test_data)
        print(f"  [OK] 自定义编码器成功!")
        print(f"  结果长度: {len(result)} 字符")
        print(f"  前200字符: {result[:200]}...")
        
        # 验证能否解析回来
        parsed = json.loads(result)
        print(f"\n  解析验证:")
        print(f"    pandas_timestamp: {parsed['pandas_timestamp']}")
        print(f"    datetime: {parsed['datetime']}")
        print(f"    numpy_array: {parsed['numpy_array']}")
        print(f"    nan处理: {parsed['nan']} (原值: {test_data['nan']})")
        
    except Exception as e:
        print(f"  [FAIL] 自定义编码器失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试DataFrame
    print("\n" + "-" * 80)
    print("测试Pandas DataFrame:")
    df = pd.DataFrame({
        '日期': pd.date_range('2024-01-01', periods=5),
        '价格': [100.0, 101.5, 102.3, 101.8, 103.2],
        '成交量': [1000, 1200, 1100, 1300, 1250]
    })
    
    test_df_data = {
        "dataframe": df,
        "series": df['价格'],
    }
    
    try:
        result = safe_json_dumps(test_df_data)
        print(f"  [OK] DataFrame序列化成功!")
        print(f"  结果长度: {len(result)} 字符")
        
        parsed = json.loads(result)
        print(f"  DataFrame记录数: {len(parsed['dataframe'])}")
        print(f"  第一条记录: {parsed['dataframe'][0]}")
        
    except Exception as e:
        print(f"  [FAIL] DataFrame序列化失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    test_json_encoder()
