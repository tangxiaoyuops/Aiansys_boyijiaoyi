# 通用自主规划Agent框架 - 使用指南

## ✅ 已完成功能

### 1. 核心工具系统
- ✅ `BaseTool` - 工具基类
- ✅ `ToolMetadata` - 工具元数据管理
- ✅ `FunctionTool` - Python函数工具
- ✅ `AgentTool` - 嵌套Agent工具
- ✅ `WorkflowTool` - LangGraph工作流工具
- ✅ `APITool` - 外部API工具

### 2. 工具注册中心
- ✅ `ToolRegistry` - 统一工具管理
- ✅ 工具注册/注销
- ✅ 能力索引和类型索引
- ✅ 工具搜索和描述生成

### 3. Agent系统
- ✅ `AgentState` - Agent状态管理
- ✅ `BaseAgent` - Agent基类
- ✅ `ReActAgent` - ReAct循环Agent

### 4. 执行引擎
- ✅ `ExecutionEngine` - 执行引擎
- ✅ 单工具执行
- ✅ 并行执行
- ✅ 串行执行
- ✅ DAG依赖执行

### 5. 博弈交易集成
- ✅ 博弈交易工具集(7个工具)
- ✅ 数据获取、阶段分析、洗盘检测等
- ✅ LLM客户端封装

### 6. 测试和文档
- ✅ 快速测试套件
- ✅ 完整测试套件
- ✅ 使用示例
- ✅ README文档

---

## 🚀 快速开始

### 安装依赖

```bash
pip install openai pydantic requests
```

### 基础使用

```python
from core.agent_framework import ToolMetadata, FunctionTool, ToolRegistry

# 1. 定义函数
def my_function(param: str) -> str:
    return f"处理结果: {param}"

# 2. 创建工具
tool = FunctionTool(
    func=my_function,
    metadata=ToolMetadata(
        name="my_tool",
        description="我的工具",
        tool_type="function",
        parameters={
            "param": {"type": "string", "description": "参数"}
        },
        required_parameters=["param"],
        capabilities=["custom"]
    )
)

# 3. 注册工具
registry = ToolRegistry()
registry.register_tool(tool)

# 4. 执行工具
result = tool.execute({"param": "test"}, {})
print(result)
```

---

## 📊 博弈交易应用示例

### 创建博弈交易Agent

```python
from core.agent_framework.llm_client import LLMClient
from core.agent_framework.examples.boyi_tools import create_boyi_master_agent

# 创建LLM客户端
llm_client = LLMClient(
    model="gpt-4o",
    api_key="your-api-key"
)

# 创建博弈交易主控Agent
agent, registry = create_boyi_master_agent(
    llm_client=llm_client,
    max_iterations=15
)

# 运行分析
result = agent.run({
    "task": "分析股票000001,判断当前阶段,识别洗盘,给出买卖建议"
})

print(result['response'])
```

### 可用工具列表

1. **fetch_kline** - 获取K线数据
2. **calc_indicators** - 计算技术指标
3. **get_stock_info** - 获取股票信息
4. **analyze_stage** - 五阶段分析
5. **detect_washout** - 洗盘识别
6. **analyze_distribution** - 出货分析
7. **find_trading_points** - 买卖点识别

---

## 🔧 高级功能

### 1. 嵌套Agent

```python
from core.agent_framework import AgentTool

# 创建子Agent
sub_agent = ReActAgent(
    name="sub_agent",
    tool_registry=sub_registry,
    llm_client=llm_client
)

# 将子Agent注册为工具
main_registry.register_tool(AgentTool(
    agent_instance=sub_agent,
    metadata=ToolMetadata(
        name="call_sub_agent",
        description="调用子Agent",
        tool_type="agent",
        parameters={"task": {"type": "string"}},
        required_parameters=["task"]
    )
))
```

### 2. 并行执行

```python
from core.agent_framework import ExecutionEngine

engine = ExecutionEngine(max_workers=5)

# 并行执行多个工具
results = engine.execute_tools_parallel(
    [
        {"tool": tool1, "parameters": {...}},
        {"tool": tool2, "parameters": {...}}
    ],
    context={}
)

engine.shutdown()
```

### 3. DAG依赖执行

```python
# 定义DAG节点
dag_nodes = [
    {
        "id": "step1",
        "tool": tool1,
        "parameters": {...},
        "depends_on": []
    },
    {
        "id": "step2",
        "tool": tool2,
        "parameters": {...},
        "depends_on": ["step1"]  # 依赖step1
    }
]

# 执行DAG
results = engine.execute_dag(dag_nodes, context={})
```

---

## 🧪 测试

### 运行快速测试

```bash
python core/agent_framework/tests/quick_test.py
```

**测试内容:**
- ✅ 工具系统
- ✅ 工具注册中心
- ✅ 执行引擎
- ✅ 博弈交易工具

### 运行完整测试

```bash
# 需要设置API Key
export OPENAI_API_KEY="your-api-key"

python core/agent_framework/tests/test_framework.py
```

**测试内容:**
- ✅ 工具系统
- ✅ 工具注册中心
- ✅ 执行引擎
- ✅ 博弈交易工具
- ⚠️ ReAct Agent(需要API Key)
- ⚠️ 嵌套Agent(需要API Key)

---

## 📁 项目结构

```
core/agent_framework/
├── __init__.py                 # 框架入口
├── tools/                      # 工具系统
│   ├── __init__.py
│   ├── base.py                 # 工具基类
│   ├── function_tool.py        # 函数工具
│   ├── agent_tool.py           # Agent工具
│   ├── workflow_tool.py        # 工作流工具
│   └── api_tool.py             # API工具
├── agents/                     # Agent系统
│   ├── __init__.py
│   ├── base.py                 # Agent基类
│   └── react_agent.py          # ReAct Agent
├── registry.py                 # 工具注册中心
├── engine.py                   # 执行引擎
├── llm_client.py               # LLM客户端
├── examples/                   # 示例代码
│   ├── boyi_tools.py           # 博弈交易工具集
│   └── simple_demo.py          # 简单示例
├── tests/                      # 测试用例
│   ├── quick_test.py           # 快速测试
│   └── test_framework.py       # 完整测试
├── README.md                   # 详细文档
└── USAGE_GUIDE.md              # 本使用指南
```

---

## 🎯 核心概念

### ReAct循环

```
观察(Observe) → 思考(Think) → 行动(Act) → 判断(Evaluate)
      ↑                                              ↓
      └──────────────── 未完成 ←─────────────────────┘
```

### 工具类型

1. **FunctionTool** - 包装Python函数
2. **AgentTool** - 包装子Agent
3. **WorkflowTool** - 包装工作流
4. **APITool** - 包装外部API

### 状态管理

- `iteration` - 当前迭代次数
- `execution_history` - 执行历史
- `collected_info` - 已收集信息
- `conversation_history` - 对话历史
- `task_complete` - 任务是否完成

---

## 💡 最佳实践

### 1. 工具设计
- 单一职责原则
- 清晰的参数定义
- 完善的错误处理
- 详细的能力标签

### 2. Agent配置
- 合理设置最大迭代次数
- 根据任务复杂度调整
- 监控执行轨迹

### 3. 性能优化
- 使用并行执行提升效率
- 合理使用工具缓存
- 控制Token使用量

---

## 🔍 常见问题

### Q: 如何调试Agent执行过程?
A: 查看执行轨迹 `result['execution_trace']`

### Q: 如何添加自定义工具?
A: 继承`BaseTool`类或使用`FunctionTool`

### Q: 如何处理工具执行失败?
A: Agent会自动尝试其他工具,查看`result['errors']`

### Q: 如何限制执行成本?
A: 设置`max_iterations`,选择合适的工具

---

## 📞 支持

- 查看 [README.md](./README.md) 获取详细文档
- 运行测试用例验证功能
- 查看示例代码学习用法

---

**框架已全部实现并通过测试,可以立即使用!** ✅
