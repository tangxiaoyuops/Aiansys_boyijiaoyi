# 通用自主规划Agent框架

一个基于ReAct循环的通用自主规划Agent框架,支持工具调用、嵌套Agent、动态规划。

## ✨ 核心特性

- 🔄 **ReAct循环** - 观察-思考-行动-判断的自主决策循环
- 🛠️ **统一工具系统** - 函数、工作流、Agent、API四种工具类型
- 🤖 **嵌套Agent** - Agent可作为工具被其他Agent调用
- 📊 **动态规划** - 根据中间结果动态调整执行策略
- ⚡ **并行执行** - 支持工具的并行和串行执行
- 📝 **完整日志** - 执行轨迹、统计信息、错误追踪

## 📦 安装

```bash
# 安装依赖
pip install openai pydantic requests
```

## 🚀 快速开始

### 1. 创建简单工具

```python
from core.agent_framework import ToolMetadata, FunctionTool, ToolRegistry

# 定义函数
def calculate(operation: str, a: int, b: int) -> float:
    """执行数学运算"""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    # ...

# 创建工具
tool = FunctionTool(
    func=calculate,
    metadata=ToolMetadata(
        name="calculate",
        description="执行基本数学运算",
        tool_type="function",
        parameters={
            "operation": {"type": "string"},
            "a": {"type": "integer"},
            "b": {"type": "integer"}
        },
        required_parameters=["operation", "a", "b"],
        capabilities=["math"]
    )
)

# 注册到注册中心
registry = ToolRegistry()
registry.register_tool(tool)

# 执行工具
result = tool.execute({"operation": "add", "a": 5, "b": 3}, {})
print(result)  # {"status": "success", "result": 8, ...}
```

### 2. 创建Agent

```python
from core.agent_framework import ReActAgent
from core.agent_framework.llm_client import LLMClient

# 创建LLM客户端
llm_client = LLMClient(
    model="gpt-4o",
    api_key="your-api-key"
)

# 创建Agent
agent = ReActAgent(
    name="my_agent",
    tool_registry=registry,
    llm_client=llm_client,
    max_iterations=10
)

# 运行Agent
result = agent.run({
    "task": "计算(10 + 5) * 2"
})

print(result['response'])
```

### 3. 嵌套Agent

```python
from core.agent_framework import AgentTool

# 创建子Agent
sub_agent = ReActAgent(
    name="sub_agent",
    tool_registry=sub_registry,
    llm_client=llm_client,
    max_iterations=5
)

# 将子Agent注册为工具
main_registry.register_tool(AgentTool(
    agent_instance=sub_agent,
    metadata=ToolMetadata(
        name="call_sub_agent",
        description="调用子Agent处理复杂任务",
        tool_type="agent",
        parameters={"task": {"type": "string"}},
        required_parameters=["task"]
    )
))
```

## 📁 项目结构

```
core/agent_framework/
├── __init__.py                 # 框架入口
├── tools/                      # 工具系统
│   ├── __init__.py
│   ├── base.py                 # 工具基类和元数据
│   ├── function_tool.py        # 函数工具
│   ├── agent_tool.py           # Agent工具
│   ├── workflow_tool.py        # 工作流工具
│   └── api_tool.py             # API工具
├── agents/                     # Agent系统
│   ├── __init__.py
│   ├── base.py                 # Agent基类和状态
│   └── react_agent.py          # ReAct Agent实现
├── registry.py                 # 工具注册中心
├── engine.py                   # 执行引擎
├── llm_client.py               # LLM客户端封装
├── examples/                   # 示例代码
│   ├── boyi_tools.py           # 博弈交易工具集
│   └── simple_demo.py          # 简单示例
├── tests/                      # 测试用例
│   └── test_framework.py
└── README.md                   # 本文档
```

## 🔧 工具类型

### 1. FunctionTool (函数工具)

```python
# 包装Python函数
tool = FunctionTool(
    func=my_function,
    metadata=ToolMetadata(
        name="my_tool",
        description="工具描述",
        tool_type="function",
        parameters={...},
        required_parameters=[...],
        capabilities=["capability1", "capability2"]
    )
)
```

### 2. AgentTool (Agent工具)

```python
# 包装子Agent
tool = AgentTool(
    agent_instance=sub_agent,
    metadata=ToolMetadata(
        name="sub_agent_tool",
        description="子Agent描述",
        tool_type="agent",
        parameters={...}
    )
)
```

### 3. WorkflowTool (工作流工具)

```python
# 包装LangGraph工作流
tool = WorkflowTool(
    workflow_config_path="path/to/workflow.yaml",
    metadata=ToolMetadata(
        name="workflow_tool",
        description="工作流描述",
        tool_type="workflow",
        parameters={...}
    )
)
```

### 4. APITool (API工具)

```python
# 包装外部API
tool = APITool(
    api_endpoint="https://api.example.com/endpoint",
    metadata=ToolMetadata(
        name="api_tool",
        description="API描述",
        tool_type="api",
        parameters={...}
    )
)
```

## 🎯 ReAct循环

Agent的执行流程遵循ReAct模式:

```
1. 观察 (Observe)
   ↓ 分析当前状态、已收集信息、缺失信息

2. 思考 (Think)
   ↓ 决定下一步行动、选择合适工具

3. 行动 (Act)
   ↓ 执行工具调用、获取结果

4. 判断 (Evaluate)
   ↓ 判断任务是否完成

→ 如果未完成,回到步骤1(最多迭代N次)
```

## 📊 博弈交易应用

框架已为博弈交易系统预设工具集:

```python
from core.agent_framework.examples.boyi_tools import create_boyi_master_agent

# 创建博弈交易主控Agent
agent, registry = create_boyi_master_agent(
    llm_client=llm_client,
    max_iterations=15
)

# 运行分析
result = agent.run({
    "task": "分析股票000001,告诉我它处于哪个阶段,是否有洗盘,买卖点在哪里?"
})

print(result['response'])
```

### 可用工具

- `fetch_kline` - 获取K线数据
- `calc_indicators` - 计算技术指标
- `get_stock_info` - 获取股票信息
- `analyze_stage` - 五阶段分析
- `detect_washout` - 洗盘识别
- `analyze_distribution` - 出货分析
- `find_trading_points` - 买卖点识别

## 🧪 运行测试

```bash
# 运行测试套件
python core/agent_framework/tests/test_framework.py

# 运行简单示例
python core/agent_framework/examples/simple_demo.py
```

## 📝 API文档

### ToolMetadata

工具元数据类

```python
class ToolMetadata(BaseModel):
    name: str                      # 工具名称
    description: str               # 工具描述
    tool_type: str                 # 工具类型
    parameters: Dict[str, Any]     # 参数schema
    required_parameters: List[str] # 必需参数
    optional_parameters: List[str] # 可选参数
    capabilities: List[str]        # 能力标签
    cost_level: str                # 成本等级
    estimated_time: str            # 预估时间
```

### BaseTool

工具基类

```python
class BaseTool(ABC):
    def execute(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        pass
    
    def get_description_for_agent(self) -> str:
        """生成给Agent看的描述"""
        pass
```

### ToolRegistry

工具注册中心

```python
class ToolRegistry:
    def register_tool(self, tool: BaseTool) -> None:
        """注册工具"""
        pass
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """获取工具"""
        pass
    
    def list_tools(self, tool_type=None, capability=None) -> List[BaseTool]:
        """列出工具"""
        pass
    
    def search_tools_by_capability(self, capabilities: List[str]) -> List[BaseTool]:
        """根据能力搜索"""
        pass
```

### ReActAgent

ReAct Agent

```python
class ReActAgent(BaseAgent):
    def run(
        self, 
        user_input: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """运行Agent"""
        pass
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        pass
```

### ExecutionEngine

执行引擎

```python
class ExecutionEngine:
    def execute_tool(self, tool, parameters, context) -> Dict[str, Any]:
        """执行单个工具"""
        pass
    
    def execute_tools_parallel(self, tools_with_params, context) -> List[Dict]:
        """并行执行多个工具"""
        pass
    
    def execute_tools_sequential(self, tools_with_params, context) -> List[Dict]:
        """顺序执行多个工具"""
        pass
```

## 🎓 设计理念

### 1. 通用性
不绑定特定业务,适用于各种Agent应用场景

### 2. 可扩展性
易于添加新工具类型和新Agent策略

### 3. 可组合性
工具和Agent可以自由组合,支持嵌套

### 4. 可观测性
完整的执行日志和追踪,便于调试和优化

## 🔗 相关资源

- [设计方案文档](../../.cursor/plans/通用自主规划Agent框架设计方案.md)
- [博弈交易分析报告](../../博弈交易法_分析报告.md)

## 📄 License

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request!

---

**Created with ❤️ for AI Agent Development**
