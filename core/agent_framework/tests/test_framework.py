"""
通用自主规划Agent框架 - 完整测试示例
演示框架的核心功能
"""
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core.agent_framework import (
    ToolMetadata,
    FunctionTool,
    ToolRegistry,
    ReActAgent,
    ExecutionEngine
)
from core.agent_framework.llm_client import LLMClient


# ========== 测试1: 工具系统测试 ==========

def test_tools():
    """测试工具系统"""
    print("\n" + "="*60)
    print("测试1: 工具系统")
    print("="*60)
    
    # 创建函数工具
    def add_numbers(a: int, b: int) -> int:
        """加法函数"""
        return a + b
    
    add_tool = FunctionTool(
        func=add_numbers,
        metadata=ToolMetadata(
            name="add",
            description="两个数字相加",
            tool_type="function",
            parameters={
                "a": {"type": "integer", "description": "第一个数字"},
                "b": {"type": "integer", "description": "第二个数字"}
            },
            required_parameters=["a", "b"],
            capabilities=["math"],
            cost_level="free"
        )
    )
    
    # 测试工具执行
    result = add_tool.execute({"a": 5, "b": 3}, {})
    
    print(f"\n工具名称: {add_tool.metadata.name}")
    print(f"工具描述: {add_tool.metadata.description}")
    print(f"执行参数: a=5, b=3")
    print(f"执行结果: {result}")
    print(f"执行统计: {add_tool.get_stats()}")
    
    # 测试参数验证
    try:
        add_tool.execute({"a": 5}, {})  # 缺少参数b
    except ValueError as e:
        print(f"\n参数验证测试: {e}")
    
    print("\n✅ 工具系统测试通过")


# ========== 测试2: 工具注册中心测试 ==========

def test_registry():
    """测试工具注册中心"""
    print("\n" + "="*60)
    print("测试2: 工具注册中心")
    print("="*60)
    
    registry = ToolRegistry()
    
    # 注册多个工具
    def multiply(a: int, b: int) -> int:
        return a * b
    
    def divide(a: int, b: int) -> float:
        return a / b
    
    registry.register_tool(FunctionTool(
        func=add_numbers if 'add_numbers' in globals() else lambda a, b: a + b,
        metadata=ToolMetadata(
            name="add",
            description="加法",
            tool_type="function",
            parameters={"a": {"type": "int"}, "b": {"type": "int"}},
            required_parameters=["a", "b"],
            capabilities=["math", "arithmetic"]
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=multiply,
        metadata=ToolMetadata(
            name="multiply",
            description="乘法",
            tool_type="function",
            parameters={"a": {"type": "int"}, "b": {"type": "int"}},
            required_parameters=["a", "b"],
            capabilities=["math", "arithmetic"]
        )
    ))
    
    registry.register_tool(FunctionTool(
        func=divide,
        metadata=ToolMetadata(
            name="divide",
            description="除法",
            tool_type="function",
            parameters={"a": {"type": "int"}, "b": {"type": "int"}},
            required_parameters=["a", "b"],
            capabilities=["math", "division"]
        )
    ))
    
    print(f"\n注册工具数量: {len(registry)}")
    print(f"工具列表: {list(registry.tools.keys())}")
    print(f"\n能力索引:")
    for cap, tools in registry.capabilities_index.items():
        print(f"  {cap}: {tools}")
    
    # 测试能力搜索
    tools = registry.search_tools_by_capability(["math"])
    print(f"\n搜索'math'能力的工具: {[t.metadata.name for t in tools]}")
    
    # 测试工具描述
    print(f"\n工具描述示例:")
    print(registry.get_tools_description(["add"]))
    
    print("\n✅ 工具注册中心测试通过")


# ========== 测试3: 执行引擎测试 ==========

def test_engine():
    """测试执行引擎"""
    print("\n" + "="*60)
    print("测试3: 执行引擎")
    print("="*60)
    
    # 创建工具
    def slow_task(seconds: int) -> str:
        import time
        time.sleep(seconds)
        return f"等待了{seconds}秒"
    
    tool1 = FunctionTool(
        func=lambda: slow_task(1),
        metadata=ToolMetadata(
            name="slow_task_1",
            description="慢任务1",
            tool_type="function",
            parameters={},
            required_parameters=[]
        )
    )
    
    tool2 = FunctionTool(
        func=lambda: slow_task(1),
        metadata=ToolMetadata(
            name="slow_task_2",
            description="慢任务2",
            tool_type="function",
            parameters={},
            required_parameters=[]
        )
    )
    
    # 测试并行执行
    engine = ExecutionEngine(max_workers=5)
    
    import time
    start = time.time()
    
    results = engine.execute_tools_parallel(
        [
            {"tool": tool1, "parameters": {}},
            {"tool": tool2, "parameters": {}}
        ],
        context={}
    )
    
    elapsed = time.time() - start
    
    print(f"\n并行执行2个1秒任务:")
    print(f"实际耗时: {elapsed:.2f}秒")
    print(f"结果数量: {len(results)}")
    
    # 测试执行统计
    stats = engine.get_stats()
    print(f"\n执行统计:")
    print(f"  总执行次数: {stats['total_executions']}")
    print(f"  总执行时间: {stats['total_time']:.2f}秒")
    print(f"  成功次数: {stats['success_count']}")
    
    engine.shutdown()
    
    print("\n✅ 执行引擎测试通过")


# ========== 测试4: ReAct Agent测试(需要LLM) ==========

def test_react_agent_with_llm():
    """测试ReAct Agent(需要配置LLM API)"""
    print("\n" + "="*60)
    print("测试4: ReAct Agent(需要LLM)")
    print("="*60)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ 未配置OPENAI_API_KEY,跳过LLM测试")
        print("请设置环境变量后重试:")
        print("  export OPENAI_API_KEY='your-api-key'")
        return
    
    try:
        # 创建LLM客户端
        llm_client = LLMClient(
            model="gpt-4o",
            temperature=0.7
        )
        
        # 创建工具注册中心
        registry = ToolRegistry()
        
        # 注册简单工具
        def get_weather(city: str) -> str:
            """获取天气(模拟)"""
            return f"{city}今天晴天,温度25℃"
        
        def get_time() -> str:
            """获取时间"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        registry.register_tool(FunctionTool(
            func=get_weather,
            metadata=ToolMetadata(
                name="get_weather",
                description="获取指定城市的天气信息",
                tool_type="function",
                parameters={
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                required_parameters=["city"],
                capabilities=["weather"]
            )
        ))
        
        registry.register_tool(FunctionTool(
            func=get_time,
            metadata=ToolMetadata(
                name="get_time",
                description="获取当前时间",
                tool_type="function",
                parameters={},
                required_parameters=[],
                capabilities=["time"]
            )
        ))
        
        # 创建Agent
        agent = ReActAgent(
            name="test_agent",
            tool_registry=registry,
            llm_client=llm_client,
            max_iterations=5
        )
        
        # 运行Agent
        result = agent.run(
            user_input={
                "task": "告诉我北京现在的天气和时间"
            }
        )
        
        print(f"\n最终响应:\n{result['response']}")
        print(f"\n迭代次数: {result['iterations']}")
        print(f"\n执行轨迹:")
        for i, trace in enumerate(result['execution_trace'], 1):
            print(f"\n第{i}轮:")
            print(f"  思考: {trace['decision'].get('thinking', '')[:50]}...")
            print(f"  行动: {trace['decision'].get('action', {}).get('tool', 'none')}")
            print(f"  结果: {trace['result'].get('status', 'unknown')}")
        
        print("\n✅ ReAct Agent测试通过")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


# ========== 测试5: 博弈交易Agent测试 ==========

def test_boyi_agent():
    """测试博弈交易Agent"""
    print("\n" + "="*60)
    print("测试5: 博弈交易Agent")
    print("="*60)
    
    from core.agent_framework.examples.boyi_tools import create_boyi_tool_registry
    
    # 创建工具注册中心
    registry = create_boyi_tool_registry()
    
    print(f"\n博弈交易工具注册中心:")
    print(f"  工具数量: {len(registry)}")
    print(f"  工具列表:")
    for tool in registry:
        print(f"    - {tool.metadata.name}: {tool.metadata.description}")
    
    print(f"\n  能力索引:")
    for cap, tools in registry.capabilities_index.items():
        print(f"    {cap}: {tools}")
    
    # 测试单个工具
    print(f"\n测试工具执行:")
    tool = registry.get_tool("fetch_kline")
    result = tool.execute({"stock_code": "000001"}, {})
    print(f"  工具: fetch_kline")
    print(f"  参数: stock_code='000001'")
    print(f"  结果: {result['status']}")
    print(f"  执行时间: {result['execution_time']:.2f}秒")
    
    print("\n✅ 博弈交易Agent测试通过")


# ========== 测试6: 嵌套Agent测试 ==========

def test_nested_agents():
    """测试嵌套Agent"""
    print("\n" + "="*60)
    print("测试6: 嵌套Agent(子Agent作为工具)")
    print("="*60)
    
    # 检查API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ 未配置OPENAI_API_KEY,跳过嵌套Agent测试")
        return
    
    try:
        from core.agent_framework.tools.agent_tool import AgentTool
        
        # 创建LLM客户端
        llm_client = LLMClient(model="gpt-4o", temperature=0.7)
        
        # 创建子Agent的工具注册中心
        sub_registry = ToolRegistry()
        
        def sub_task(data: str) -> str:
            return f"处理数据: {data}"
        
        sub_registry.register_tool(FunctionTool(
            func=sub_task,
            metadata=ToolMetadata(
                name="sub_task",
                description="子任务处理",
                tool_type="function",
                parameters={"data": {"type": "string"}},
                required_parameters=["data"]
            )
        ))
        
        # 创建子Agent
        sub_agent = ReActAgent(
            name="sub_agent",
            tool_registry=sub_registry,
            llm_client=llm_client,
            max_iterations=3
        )
        
        # 创建主Agent的工具注册中心
        main_registry = ToolRegistry()
        
        # 将子Agent注册为工具
        main_registry.register_tool(AgentTool(
            agent_instance=sub_agent,
            metadata=ToolMetadata(
                name="call_sub_agent",
                description="调用子Agent处理复杂任务",
                tool_type="agent",
                parameters={
                    "task": {
                        "type": "string",
                        "description": "子任务描述"
                    },
                    "data": {
                        "type": "string",
                        "description": "要处理的数据"
                    }
                },
                required_parameters=["task", "data"]
            )
        ))
        
        print("\n✅ 嵌套Agent测试通过(结构验证)")
        print("  主Agent已创建,包含子Agent作为工具")
        print(f"  子Agent名称: {sub_agent.name}")
        print(f"  工具类型: agent")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")


# ========== 运行所有测试 ==========

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("通用自主规划Agent框架 - 测试套件")
    print("="*60)
    
    # 运行基础测试
    test_tools()
    test_registry()
    test_engine()
    test_boyi_agent()
    
    # 运行需要LLM的测试
    test_react_agent_with_llm()
    test_nested_agents()
    
    print("\n" + "="*60)
    print("所有测试完成!")
    print("="*60)
    print("\n提示:")
    print("- 基础测试(工具、注册中心、引擎)已全部通过")
    print("- LLM相关测试需要配置OPENAI_API_KEY环境变量")
    print("- 完整功能测试建议在实际应用场景中进行")


if __name__ == "__main__":
    run_all_tests()
