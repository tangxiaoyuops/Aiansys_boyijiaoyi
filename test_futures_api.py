"""
测试期货分析API
"""
import requests
import json

# 测试期货分析流式接口
url = "http://localhost:8000/api/futures/analyze/stream"
params = {
    "message": "分析rb2501",
    "futures_code": "rb2501",
    "analysis_type": "game_theory",
    "days": 60
}

print("=" * 80)
print("测试期货分析API")
print("=" * 80)
print(f"URL: {url}")
print(f"参数: {params}")
print()

try:
    # 发送请求
    response = requests.get(url, params=params, stream=True, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print()
    
    # 读取流式响应
    print("开始接收流式数据:")
    print("-" * 80)
    
    line_count = 0
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"第{line_count + 1}行: {line_str}")
            
            # 尝试解析JSON
            if line_str.startswith('data: '):
                json_str = line_str[6:]
                try:
                    data = json.loads(json_str)
                    print(f"  解析结果: {json.dumps(data, ensure_ascii=False, indent=2)}")
                except Exception as e:
                    print(f"  JSON解析失败: {e}")
            
            line_count += 1
            
            # 只读取前50行用于测试
            if line_count >= 50:
                print("\n... 已读取50行，停止测试 ...")
                break
    
    print("-" * 80)
    print(f"总共读取 {line_count} 行")
    
except Exception as e:
    print(f"请求失败: {e}")
    import traceback
    traceback.print_exc()
