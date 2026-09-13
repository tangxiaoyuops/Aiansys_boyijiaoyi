import requests

print("测试API连接...")

try:
    r = requests.get("http://localhost:8001/api/health")
    print(f"健康检查: {r.status_code}")
    print(f"响应: {r.json()}")
except Exception as e:
    print(f"错误: {e}")

try:
    r = requests.get("http://localhost:8001/api/tools")
    print(f"\n工具列表: {r.status_code}")
    print(f"工具数量: {r.json().get('total', 0)}")
except Exception as e:
    print(f"错误: {e}")

try:
    # 测试流式端点
    print("\n测试流式端点...")
    r = requests.post(
        "http://localhost:8001/api/analyze/stream",
        json={"task": "测试"},
        stream=True
    )
    print(f"流式端点: {r.status_code}")
except Exception as e:
    print(f"错误: {e}")
