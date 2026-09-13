"""
测试Agent框架集成到主后端
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("测试Agent框架集成")
print("=" * 80)

# 测试1：配置Agent
print("\n[测试1] 配置Agent框架")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/agent/config",
        json={},
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 配置成功!")
        print(f"   工具数量: {data['tools_count']}")
        print(f"   工具列表: {data['tools']}")
    else:
        print(f"❌ 配置失败: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试2：检查状态
print("\n[测试2] 检查Agent状态")
print("-" * 80)
try:
    response = requests.get(
        f"{BASE_URL}/api/agent/status",
        timeout=5
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 状态检查成功!")
        print(f"   已配置: {data['configured']}")
        print(f"   工具数量: {data['tools_count']}")
    else:
        print(f"❌ 状态检查失败: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试3：执行分析（非流式）
print("\n[测试3] 执行Agent分析（非流式）")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/agent/analyze",
        json={
            "task": "分析601225的博弈阶段",
            "stock_code": "601225",
            "max_iterations": 5
        },
        timeout=60
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 分析完成!")
        print(f"   迭代次数: {data['iterations']}")
        print(f"   响应长度: {len(data['response'])} 字符")
        print(f"   响应预览: {data['response'][:200]}...")
    else:
        print(f"❌ 分析失败: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试4：执行分析（流式）
print("\n[测试4] 执行Agent分析（流式）")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/api/agent/analyze/stream",
        json={
            "task": "分析rb2501的博弈阶段",
            "stock_code": "rb2501",
            "max_iterations": 3
        },
        stream=True,
        timeout=60
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 开始接收流式数据:")
        line_count = 0
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        event_type = data.get('type', 'unknown')
                        if event_type == 'start':
                            print(f"   [{event_type}] {data.get('message', '')}")
                        elif event_type == 'thinking':
                            print(f"   [{event_type}] 正在思考...")
                        elif event_type == 'thought':
                            print(f"   [{event_type}] 思考完成")
                        elif event_type == 'action_start':
                            print(f"   [{event_type}] 执行工具: {data.get('tool', '')}")
                        elif event_type == 'action_result':
                            print(f"   [{event_type}] 工具执行完成")
                        elif event_type == 'complete':
                            print(f"   [{event_type}] 分析完成")
                            print(f"   迭代次数: {data.get('iterations', 0)}")
                            break
                        line_count += 1
                        if line_count >= 20:  # 限制输出
                            print("   ... (输出已截断)")
                            break
                    except Exception as e:
                        print(f"   解析错误: {e}")
    else:
        print(f"❌ 流式分析失败: {response.text}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
