# -*- coding: utf-8 -*-
"""
快速测试 - 验证框架基本功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core.agent_framework import (
    ToolMetadata,
    FunctionTool,
    ToolRegistry,
    ExecutionEngine
)

print("="*60)
print("Framework Quick Test")
print("="*60)

# Test 1: Tool System
print("\n[Test 1] Tool System")

def add(a: int, b: int) -> int:
    return a + b

tool = FunctionTool(
    func=add,
    metadata=ToolMetadata(
        name="add",
        description="Add two numbers",
        tool_type="function",
        parameters={
            "a": {"type": "int", "description": "First number"},
            "b": {"type": "int", "description": "Second number"}
        },
        required_parameters=["a", "b"],
        capabilities=["math"]
    )
)

result = tool.execute({"a": 5, "b": 3}, {})
print(f"Tool: add(5, 3) = {result['result']}")
print(f"Status: {result['status']}")
print(f"Execution time: {result['execution_time']:.4f}s")

# Test 2: Registry
print("\n[Test 2] Tool Registry")

registry = ToolRegistry()
registry.register_tool(tool)

print(f"Tools count: {len(registry)}")
print(f"Tool names: {list(registry.tools.keys())}")
print(f"Capabilities: {registry.get_all_capabilities()}")

# Test 3: Execution Engine
print("\n[Test 3] Execution Engine")

engine = ExecutionEngine(max_workers=3)

def multiply(a: int, b: int) -> int:
    return a * b

mul_tool = FunctionTool(
    func=multiply,
    metadata=ToolMetadata(
        name="multiply",
        description="Multiply two numbers",
        tool_type="function",
        parameters={"a": {"type": "int"}, "b": {"type": "int"}},
        required_parameters=["a", "b"]
    )
)

results = engine.execute_tools_parallel(
    [
        {"tool": tool, "parameters": {"a": 10, "b": 5}},
        {"tool": mul_tool, "parameters": {"a": 10, "b": 5}}
    ],
    context={}
)

print(f"Parallel execution results:")
for r in results:
    print(f"  {r['tool_name']}: {r['result']}")

stats = engine.get_stats()
print(f"\nEngine stats:")
print(f"  Total executions: {stats['total_executions']}")
print(f"  Success count: {stats['success_count']}")

engine.shutdown()

# Test 4: Boyi Tools
print("\n[Test 4] Boyi Trading Tools")

try:
    from core.agent_framework.examples.boyi_tools import create_boyi_tool_registry
    
    boyi_registry = create_boyi_tool_registry()
    
    print(f"Boyi tools count: {len(boyi_registry)}")
    print(f"Tool list:")
    for t in boyi_registry:
        print(f"  - {t.metadata.name}: {t.metadata.description}")
    
    print(f"\nCapabilities:")
    for cap, tools in boyi_registry.capabilities_index.items():
        print(f"  {cap}: {tools}")
    
    # Test one tool
    fetch_tool = boyi_registry.get_tool("fetch_kline")
    result = fetch_tool.execute({"stock_code": "000001"}, {})
    print(f"\nTest fetch_kline:")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result['result'].get('message', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("All basic tests passed!")
print("="*60)
print("\nNote: LLM tests require OPENAI_API_KEY environment variable")
print("To test ReAct Agent, set the API key and run the full test suite")
