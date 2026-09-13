# 通用自主规划Agent框架 - Web UI 使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn openai pydantic requests
```

### 2. 启动服务

**方法一: 使用启动脚本**

```bash
python start_agent_ui.py
```

**方法二: 直接启动**

```bash
uvicorn core.agent_framework.api.app:app_instance --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问Web界面

打开浏览器访问:

- **Web界面**: http://localhost:8000/ui
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

---

## 📖 使用步骤

### 第一步: 配置Agent

在Web界面中:

1. 输入您的 **OpenAI API Key**
2. 选择模型 (推荐 GPT-4o)
3. (可选) 输入自定义的 API Base URL
4. 点击 **"配置Agent"** 按钮

配置成功后,状态栏会显示 "已就绪"。

### 第二步: 输入分析任务

有两种方式:

**方式一: 手动输入**

在任务描述框中输入您的分析任务,例如:
```
分析股票000001,判断当前所处的阶段,识别洗盘特征,给出买卖建议
```

**方式二: 使用快速任务**

点击下方的快速任务按钮:
- 阶段分析
- 洗盘识别
- 买卖建议
- 完整分析

### 第三步: 开始分析

1. 设置最大迭代次数 (默认10次)
2. 点击 **"开始分析"** 按钮
3. 等待Agent执行完成

### 第四步: 查看结果

分析完成后,页面会显示:

1. **最终响应** - Agent的分析结论
2. **执行轨迹** - 每一轮迭代的详细过程
   - 思考内容
   - 使用的工具
   - 执行状态
   - 执行时间

---

## 🛠️ 可用工具

系统预置了7个博弈交易专用工具:

| 工具名称 | 描述 | 能力标签 |
|---------|------|---------|
| fetch_kline | 获取股票K线数据 | data_fetch |
| calc_indicators | 计算技术指标 | indicator_calculation |
| get_stock_info | 获取股票基本信息 | data_fetch |
| analyze_stage | 五阶段分析 | stage_recognition, o_point |
| detect_washout | 洗盘识别 | washout |
| analyze_distribution | 出货分析 | distribution |
| find_trading_points | 买卖点识别 | trading_points |

---

## 🔌 API接口

### 1. 配置Agent

```http
POST /api/config
Content-Type: application/json

{
  "api_key": "sk-...",
  "model": "gpt-4o",
  "base_url": "https://api.openai.com/v1"  // 可选
}
```

**响应:**
```json
{
  "success": true,
  "message": "Agent配置成功",
  "tools_count": 7,
  "tools": ["fetch_kline", "calc_indicators", ...]
}
```

### 2. 执行分析

```http
POST /api/analyze
Content-Type: application/json

{
  "task": "分析股票000001,判断当前阶段",
  "stock_code": "000001",  // 可选
  "max_iterations": 10
}
```

**响应:**
```json
{
  "success": true,
  "response": "分析结论...",
  "iterations": 5,
  "execution_trace": [...],
  "collected_info": {...}
}
```

### 3. 列出工具

```http
GET /api/tools
```

**响应:**
```json
{
  "success": true,
  "tools": [
    {
      "name": "fetch_kline",
      "description": "获取K线数据",
      "type": "function",
      "capabilities": ["data_fetch"],
      ...
    }
  ],
  "total": 7
}
```

### 4. 执行单个工具

```http
POST /api/tools/fetch_kline/execute
Content-Type: application/json

{
  "stock_code": "000001",
  "days": 180
}
```

### 5. 健康检查

```http
GET /api/health
```

**响应:**
```json
{
  "status": "healthy",
  "agent_configured": true,
  "tools_loaded": true
}
```

---

## 📊 示例场景

### 场景1: 完整分析

**任务:**
```
完整分析股票000001
```

**Agent执行流程:**
1. 调用 `fetch_kline` 获取K线数据
2. 调用 `calc_indicators` 计算技术指标
3. 调用 `analyze_stage` 分析阶段
4. 调用 `detect_washout` 检测洗盘
5. 调用 `analyze_distribution` 分析出货
6. 调用 `find_trading_points` 找买卖点
7. 生成综合报告

### 场景2: 快速查询

**任务:**
```
获取股票000001的K线数据和技术指标
```

**Agent执行流程:**
1. 调用 `fetch_kline`
2. 调用 `calc_indicators`
3. 返回结果

### 场景3: 深度分析

**任务:**
```
分析股票000001处于哪个阶段,是否在洗盘,给出详细的买卖建议
```

**Agent执行流程:**
1. 获取数据
2. 阶段分析
3. 洗盘检测
4. 买卖点识别
5. 综合判断
6. 生成详细报告

---

## ⚙️ 高级配置

### 环境变量

可以设置环境变量代替手动输入:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Windows
set OPENAI_API_KEY=sk-...
set OPENAI_BASE_URL=https://api.openai.com/v1
```

### 自定义端口

```bash
uvicorn core.agent_framework.api.app:app_instance --port 9000
```

### 生产环境部署

```bash
# 使用gunicorn
gunicorn core.agent_framework.api.app:app_instance \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000
```

---

## 🐛 常见问题

### Q1: 配置失败,提示API Key无效?

**A:** 检查以下几点:
- API Key格式是否正确(以sk-开头)
- API Key是否有效(未过期)
- Base URL是否正确(如果使用自定义)

### Q2: 分析卡住不动?

**A:** 可能原因:
- 网络问题,无法访问API
- 模型响应慢,请耐心等待
- 迭代次数设置过小

解决方法:
- 检查网络连接
- 增加最大迭代次数
- 查看后台日志

### Q3: 结果不理想?

**A:** 优化建议:
- 任务描述要清晰具体
- 包含股票代码
- 指明分析重点

**好的任务示例:**
```
分析股票000001,判断当前处于第几阶段,
识别是否有洗盘行为,如果存在洗盘,
给出买入建议
```

**不好的任务示例:**
```
分析股票
```

### Q4: 如何查看详细日志?

**A:** 查看终端输出,包含:
- Agent决策过程
- 工具调用详情
- 执行时间
- 错误信息

---

## 📝 最佳实践

### 1. 任务描述
- ✅ 清晰具体
- ✅ 包含关键信息
- ✅ 明确分析目标
- ❌ 模糊不清
- ❌ 过于宽泛

### 2. 迭代次数
- 简单任务: 3-5次
- 中等任务: 8-10次
- 复杂任务: 12-15次

### 3. 结果验证
- 查看执行轨迹
- 检查工具调用顺序
- 验证结论合理性

---

## 🔗 相关资源

- [框架README](../README.md)
- [使用指南](../USAGE_GUIDE.md)
- [设计方案](../../.cursor/plans/通用自主规划Agent框架设计方案.md)

---

## 💡 提示

- 首次使用建议先运行简单任务测试
- 复杂分析建议分步进行
- 定期检查API使用量和成本
- 保存重要分析结果

---

**祝您使用愉快!** 🎉
