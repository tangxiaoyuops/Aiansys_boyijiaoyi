# 🚀 博弈交易法智能分析系统 - 3种启动方式

## 方式一：快速演示（推荐新手）

**无需配置，立即可用！**

```bash
python demo_quick_start.py
```

**演示内容：**
- ✅ 知识库查询（博弈理论核心知识）
- ✅ K线数据分析（技术指标计算）
- ✅ 博弈理论逻辑（情绪比例关系）
- ✅ 完整分析流程（阶段识别）

**适合人群：**
- 想快速了解系统功能
- 还没有配置数据库和API密钥
- 想看核心逻辑演示

---

## 方式二：完整测试（推荐开发者）

**需要基础配置**

### 步骤：

1. **安装依赖**
```bash
pip install -r requirements_intelligent.txt
```

2. **创建 .env 文件**
```bash
# 数据库（可选，用于完整功能）
DATABASE_URL=postgresql://boyi:password@localhost:5432/boyi
TIMESCALEDB_URL=postgresql://boyi:password@localhost:5433/boyi_ts

# 数据源（可选）
TUSHARE_TOKEN=your_tushare_token

# AI（可选，用于Agent分析）
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4-turbo-preview
```

3. **运行测试**
```bash
python test_complete_system.py
```

**测试内容：**
- 数据库连接测试
- 数据采集功能测试
- 知识库测试
- Agent测试
- API测试

---

## 方式三：完整系统（推荐生产使用）

**需要完整配置**

### 步骤：

1. **安装依赖**
```bash
pip install -r requirements_intelligent.txt
```

2. **配置环境变量（.env）**
```bash
# 数据库（必须）
DATABASE_URL=postgresql://boyi:password@localhost:5432/boyi
TIMESCALEDB_URL=postgresql://boyi:password@localhost:5433/boyi_ts
REDIS_URL=redis://localhost:6379/0

# 数据源（必须）
TUSHARE_TOKEN=your_tushare_token_here

# AI（必须）
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7

# 向量数据库
CHROMA_PERSIST_DIR=./data/chroma
```

3. **启动数据库**
```bash
# 方式1: Docker（推荐）
docker-compose up -d postgres timescaledb redis

# 方式2: 手动安装PostgreSQL + TimescaleDB
# 参考: https://docs.timescale.com/
```

4. **初始化数据库**
```bash
psql -f scripts/init_database.sql
```

5. **启动系统**
```bash
python start_intelligent_system.py
```

6. **访问系统**
- Web服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws/client1

---

## 📊 功能对比

| 功能 | 快速演示 | 完整测试 | 完整系统 |
|------|---------|---------|---------|
| 知识库查询 | ✅ | ✅ | ✅ |
| 数据分析 | ✅ 模拟 | ✅ 真实 | ✅ 真实 |
| Agent分析 | ❌ | ⚠️ 可选 | ✅ |
| 数据采集 | ❌ | ✅ | ✅ |
| 数据库存储 | ❌ | ⚠️ 可选 | ✅ |
| 定时任务 | ❌ | ❌ | ✅ |
| Web服务 | ❌ | ✅ 测试 | ✅ 完整 |
| 实时推送 | ❌ | ❌ | ✅ |

---

## 🎯 选择建议

### 🟢 快速演示
- 刚接触系统
- 想快速了解功能
- 时间有限

### 🟡 完整测试
- 开发者
- 想验证功能
- 部分配置可用

### 🔵 完整系统
- 生产使用
- 完整配置
- 长期运行

---

## 📁 核心文件说明

### 演示和测试
- `demo_quick_start.py` - 快速演示（无需配置）
- `test_complete_system.py` - 完整测试（需要基础配置）

### 系统启动
- `start_intelligent_system.py` - 启动完整系统
- `requirements_intelligent.txt` - 依赖清单

### 核心模块
- `core/intelligent_system/agents/knowledge_base.py` - 知识库
- `core/intelligent_system/agents/phase_analyzer.py` - Agent
- `core/intelligent_system/data_collection/stock_collector.py` - 数据采集
- `core/intelligent_system/api/main.py` - Web服务

### 文档
- `IMPLEMENTATION_COMPLETE_REPORT.md` - 完整实施报告
- `QUICKSTART_INTELLIGENT_SYSTEM.md` - 快速启动指南

---

## ⚡ 快速开始（3步）

**最简单的方式：**

```bash
# 1. 安装基础依赖
pip install chromadb sentence-transformers pandas numpy

# 2. 运行演示
python demo_quick_start.py

# 3. 查看结果
# 系统会自动展示所有核心功能！
```

---

## 🆘 常见问题

### Q1: 提示缺少依赖？
```bash
# 安装基础依赖
pip install chromadb sentence-transformers pandas numpy
```

### Q2: 知识库初始化失败？
```bash
# 创建必要目录
mkdir -p data/chroma logs
```

### Q3: 想测试Agent但没API密钥？
```bash
# 使用快速演示模式，无需API密钥
python demo_quick_start.py
```

### Q4: 数据库连接失败？
```bash
# 使用Docker快速启动数据库
docker-compose up -d postgres timescaledb
```

---

## 🎉 开始体验

**选择你的方式：**

1. **想快速看效果** → `python demo_quick_start.py`
2. **想测试功能** → `python test_complete_system.py`
3. **想完整使用** → `python start_intelligent_system.py`

---

**系统已准备就绪！选择适合你的方式开始吧！** 🚀
