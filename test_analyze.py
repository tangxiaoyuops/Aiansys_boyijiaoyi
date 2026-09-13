import requests
import json

print("测试非流式API...")

try:
    response = requests.post(
        "http://localhost:8001/api/analyze",
        json={
            "task": "分析股票000001",
            "max_iterations": 3
        },
        timeout=60
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data.get('success')}")
        print(f"迭代次数: {data.get('iterations')}")
        print(f"响应长度: {len(data.get('response', ''))}")
        print(f"\n响应内容前200字符:")
        print(data.get('response', '')[:200])
    else:
        print(f"错误: {response.text}")
        
except requests.exceptions.Timeout:
    print("错误: 请求超时")
except requests.exceptions.ConnectionError:
    print("错误: 无法连接到服务器")
except Exception as e:
    print(f"错误: {e}")
