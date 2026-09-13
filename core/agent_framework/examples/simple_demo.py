"""
通用自主规划Agent框架 - 简单使用示例
快速入门演示
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from core.agent_framework import (
    ToolMetadata,
    FunctionTool,
    ToolRegistry,
    ReActAgent
)
from core.agent_framework.llm_client import LLMClient


def main():
    """简单使用示例"""
    
    print("="*60)
    print("通用自主规划Agent框架 - 快速开始")
    print("="*60)
    
    # ===== 步骤1: 创建工具注册中心 =====
    print("\n【步骤1】创建工具注册中心")
    
    registry = ToolRegistry()
    print("✅ 工具注册中心已创建")
    
    # ===== 步骤2: 定义并注册工具 =====
    print("\n【步骤2】定义并注册工具")
    
    # 定义一个简单的工具函数
    def calculate(operation: str, a: int, b: int) -> float:
        """
        执行数学运算
        
        Args:
            operation: 运算类型(add/subtract/multiply/divide)
            a: 第一个数字
            b: 第二个数字
        
        Returns:
            计算结果
        """
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b if b != 0 else float('inf')
        else:
            raise ValueError(f"未知运算: {operation}")
    
    # 创建工具元数据
    calc_metadata = ToolMetadata(
        name="calculate",
        description="执行基本数学运算(加、减、乘、除)",
        tool_type="function",
        parameters={
            "operation": {
                "type": "string",
                "description": "运算类型: add(加)/subtract(减)/multiply(乘)/divide(除)"
            },
            "a": {
                "type": "integer",
                "description": "第一个数字"
            },
            "b": {
                "type": "integer",
                "description": "第二个数字"
            }
        },
        required_parameters=["operation", "a", "b"],
        capabilities=["math", "calculation"],
        cost_level="free",
        estimated_time="0-1s"
    )
    
    # 创建函数工具
    calc_tool = FunctionTool(func=calculate, metadata=calc_metadata)
    
    # 注册工具
    registry.register_tool(calc_tool)
    print("✅ 工具已注册: calculate")
    
    # ===== 步骤3: 测试工具 =====
    print("\n【步骤3】测试工具")
    
    # 直接调用工具
    result = calc_tool.execute(
        parameters={"operation": "add", "a": 5, "b": 3},
        context={}
    )
    print(f"测试计算: 5 + 3 = {result['result']}")
    print(f"执行时间: {result['execution_time']:.4f}秒")
    
    # ===== 步骤4: 创建LLM客户端 =====
    print("\n【步骤4】创建LLM客户端")
    
    # 检查API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ 未配置OPENAI_API_KEY环境变量")
        print("请设置环境变量后重试:")
        print("  Windows: set OPENAI_API_KEY=your-api-key")
        print("  Linux/Mac: export OPENAI_API_KEY=your-api-key")
        print("\n跳过Agent创建,只演示工具系统...")
        
        # 显示注册中心信息
        print("\n【注册中心信息】")
        print(f"工具数量: {len(registry)}")
        print(f"工具列表:")
        for tool in registry:
            print(f"  - {tool.metadata.name}")
        
        print(f"\n能力索引:")
        for cap, tools in registry.capabilities_index.items():
            print(f"  {cap}: {tools}")
        
        return
    
    # 创建LLM客户端
    llm_client = LLMClient(
        model="gpt-4o",
        temperature=0.7
    )
    print("✅ LLM客户端已创建")
    
    # ===== 步骤5: 创建Agent =====
    print("\n【步骤5】创建ReAct Agent")
    
    agent = ReActAgent(
        name="math_assistant",
        tool_registry=registry,
        llm_client=llm_client,
        max_iterations=5
    )
    print("✅ Agent已创建")
    
    # ===== 步骤6: 运行Agent =====
    print("\n【步骤6】运行Agent")
    print("任务: 计算(10 + 5) * 2")
    
    result = agent.run(
        user_input={
            "task": "帮我计算(10 + 5) * 2,先加法后乘法"
        }
    )
    
    print("\n" + "="*60)
    print("最终响应:")
    print(result['response'])
    print("="*60)
    
    print(f"\n执行统计:")
    print(f"  迭代次数: {result['iterations']}")
    print(f"  成功状态: {result['success']}")
    
    print("\n执行轨迹:")
    for i, trace in enumerate(result['execution_trace'], 1):
        decision = trace['decision']
        action = decision.get('action', {})
        tool_used = action.get('tool', 'none') if action else 'none'
        status = trace['result'].get('status', 'unknown')
        
        print(f"\n  第{i}轮:")
        print(f"    工具: {tool_used}")
        print(f"    状态: {status}")


def simple_tool_example():
    """最简单的工具使用示例"""
    print("\n" + "="*60)
    print("最简单的工具使用示例")
    print("="*60)
    
    # 1. 定义函数
    def greet(name: str) -> str:
        return f"你好, {name}!"
    
    # 2. 创建工具
    from core.agent_framework import ToolMetadata, FunctionTool
    
    tool = FunctionTool(
        func=greet,
        metadata=ToolMetadata(
            name="greet",
            description="问候函数",
            tool_type="function",
            parameters={
                "name": {"type": "string", "description": "名字"}
            },
            required_parameters=["name"]
        )
    )
    
    # 3. 执行工具
    result = tool.execute({"name": "张三"}, {})
    
    print(f"\n执行结果: {result['result']}")
    print(f"状态: {result['status']}")
    print(f"执行时间: {result['execution_time']:.4f}秒")


if __name__ == "__main__":
    # 运行简单示例
    simple_tool_example()
    
    # 运行完整示例
    print("\n")
    main()
