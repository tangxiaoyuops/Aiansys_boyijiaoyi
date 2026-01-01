# 博弈交易法分析系统

基于LangGraph框架的多Agent股票分析系统，实现博弈交易法的完整分析流程。

## 系统架构

### 核心组件

1. **状态管理** (`core/models/state.py`)
   - 定义LangGraph工作流的状态结构
   - 包含所有分析结果和中间数据

2. **工具模块** (`core/tools/`)
   - `data_fetcher.py`: 数据获取工具（akshare）
   - `technical_analyzer.py`: 技术分析工具（MA、MACD、RSI等）
   - `pattern_recognizer.py`: 形态识别工具
   - `calculator.py`: 计算工具（洗盘公式、情绪比例关系等）

3. **分析Agent** (`core/agents/`)
   - `intent_agent.py`: 意图识别Agent
   - `data_agent.py`: 数据获取Agent
   - `stage_analysis_agent.py`: 阶段分析Agent（一至五阶段）
   - `o_point_agent.py`: O点识别Agent
   - `washout_agent.py`: 洗盘分析Agent
   - `distribution_agent.py`: 出货分析Agent
   - `emotion_ratio_agent.py`: 情绪比例关系Agent
   - `anchor_agent.py`: 锚定分析Agent
   - `summary_agent.py`: 分析总结Agent
   - `strategy_agent.py`: 策略推荐Agent
   - `regular_analysis_agent.py`: 常规分析Agent
   - `backtest_agent.py`: 回溯测试Agent

4. **工作流** (`core/graph/analysis_graph.py`)
   - 使用LangGraph定义完整的工作流
   - 支持条件分支（常规分析 vs 博弈分析）
   - 支持可选的回溯测试

5. **API服务** (`server/app.py`)
   - FastAPI服务
   - 提供流式和非流式接口
   - 支持SSE实时返回

## 工作流程

```
开始
  ↓
意图识别
  ↓
数据获取
  ↓
路由判断
  ├─→ 博弈分析路径
  │     ├─ 阶段分析
  │     ├─ O点识别
  │     ├─ 洗盘分析
  │     ├─ 出货分析
  │     ├─ 情绪比例关系
  │     ├─ 锚定分析
  │     ├─ 分析总结
  │     └─ 策略推荐
  │
  └─→ 常规分析路径
        ├─ 技术指标分析
        └─ 策略推荐
  ↓
生成最终报告
  ↓
可选回溯测试
  ↓
结束
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
# 启动后端服务
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

## API接口

### 1. 意图识别

**POST** `/api/intent/recognize`

```json
{
  "message": "分析000001的阶段和洗盘"
}
```

### 2. 聊天接口（流式）

**GET** `/api/chat/stream`

参数：
- `message`: 用户消息
- `stock_code`: 股票代码（可选，会从消息中提取）
- `analysis_type`: 分析类型（auto/regular/game_theory）
- `days`: 分析天数（默认180）
- `run_backtest`: 是否回测（默认false）

### 3. 聊天接口（非流式）

**POST** `/api/chat`

请求体：
```json
{
  "message": "分析000001的博弈分析",
  "stock_code": "000001",
  "analysis_type": "auto",
  "days": 180,
  "run_backtest": false
}
```

## 使用示例

### 博弈交易法分析

```
用户输入：分析000001的阶段和洗盘情况

系统响应：
1. 识别意图：博弈交易法分析
2. 进行博弈分析
3. 显示结果：
   - 阶段分析：一阶段（趋势形成初期）
   - 洗盘分析：处于洗盘状态，类型：kline，洗盘强度：0.65
   - 情绪比例关系：看涨
   - O点分析：O点价格10.50，相对涨幅15.2%
   - 交易建议：买入，轻仓（最多1/3仓位）
```

### 常规分析

```
用户输入：000001的技术指标分析

系统响应：
1. 识别意图：常规分析
2. 进行常规技术分析
3. 显示结果：
   - 交易建议：买入（信心：高）
   - 风险评估：中
   - 综合评分：75/100
```

## 项目结构

```
project/
├── core/
│   ├── agents/          # 分析Agent
│   ├── tools/           # 工具模块
│   ├── models/          # 数据模型
│   └── graph/           # LangGraph工作流
├── server/              # FastAPI服务
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## 技术栈

- **LangGraph**: 多Agent工作流框架
- **FastAPI**: Web框架
- **akshare**: 股票数据获取
- **pandas/numpy**: 数据处理
- **LangChain**: LLM集成（可选）

## 后续优化方向

1. **LLM集成**: 在各个分析节点中集成大模型，提高分析准确性
2. **流式输出优化**: 改进SSE流式输出，实时显示分析进度
3. **回测功能增强**: 实现更完整的回测逻辑
4. **缓存机制**: 添加数据缓存，提高响应速度
5. **错误处理**: 完善错误处理和重试机制

## 注意事项

1. 股票代码必须是6位数字（A股代码）
2. 博弈分析需要至少60个交易日的数据
3. 如果网络不稳定，建议设置较长的超时时间
4. 意图识别基于关键词匹配，后续可以优化为LLM识别
