import requests
import json

# 测试API
BASE_URL = "http://localhost:8001"

print("="*60)
print("测试API接口")
print("="*60)

# 1. 测试健康检查
print("\n1. 测试健康检查...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# 2. 测试工具列表
print("\n2. 测试工具列表...")
try:
    response = requests.get(f"{BASE_URL}/api/tools")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"工具数量: {data.get('total', 0)}")
except Exception as e:
    print(f"错误: {e}")

# 3. 测试配置接口
print("\n3. 测试配置接口...")
try:
    response = requests.post(
        f"{BASE_URL}/api/config",
        json={
            "api_key": "pk-f76c715b-429c-40bd-87c4-b4077464b4ae",
            "model": "GLM-5",
            "base_url": "https://modelservice.jdcloud.com/coding/openai/v1"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*60)
