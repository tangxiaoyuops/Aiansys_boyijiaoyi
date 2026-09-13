import requests

try:
    # 测试根路径
    r = requests.get("http://localhost:8000/")
    print(f"根路径: {r.status_code}")
    print(f"内容: {r.text[:200]}")
except Exception as e:
    print(f"错误: {e}")

try:
    # 测试docs
    r = requests.get("http://localhost:8000/docs")
    print(f"\nDocs: {r.status_code}")
    print(f"内容长度: {len(r.text)}")
except Exception as e:
    print(f"错误: {e}")

try:
    # 测试openapi.json
    r = requests.get("http://localhost:8000/openapi.json")
    print(f"\nOpenAPI: {r.status_code}")
    data = r.json()
    print(f"路径数量: {len(data.get('paths', {}))}")
    print(f"路径列表: {list(data.get('paths', {}).keys())}")
except Exception as e:
    print(f"错误: {e}")
