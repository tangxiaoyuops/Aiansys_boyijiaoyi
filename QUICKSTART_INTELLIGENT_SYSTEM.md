# 博弈交易法智能分析系统 - 快速启动指南

## 📦 已完成模块

### ✅ 1. 项目基础结构
```
core/intelligent_system/
├── __init__.py          # 核心模块入口
├── config.py            # 配置管理
├── database/
│   └── db_manager.py    # 数据库管理器
└── data_collection/
    └── stock_collector.py  # 数据采集器
```

### ✅ 2. 数据库管理
- **TimescaleDB**: 时序数据存储（日线数据、Agent分析结果）
- **PostgreSQL**: 关系数据存储（用户、持仓、信号、预警）
- **特性**:
  - 连接池管理
  - 异步操作
  - 自动重连

### ✅ 3. 数据采集
- **数据源**: Tushare（主）、Akshare（备用）
- **功能**:
  - 获取股票列表
  - 获取日线数据
  - 获取实时行情
  - 获取涨停股票
  - 获取大盘指数

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_intelligent.txt
```

### 2. 配置环境变量

创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=postgresql://boyi:password@localhost:5432/boyi
TIMESCALEDB_URL=postgresql://boyi:password@localhost:5433/boyi_ts
REDIS_URL=redis://localhost:6379/0

# 数据源配置
TUSHARE_TOKEN=your_tushare_token_here

# AI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

### 3. 初始化数据库

```bash
# 方式1: 使用Docker启动PostgreSQL + TimescaleDB
docker-compose up -d postgres timescaledb

# 方式2: 连接到现有数据库并执行初始化脚本
psql -h localhost -U boyi -d boyi -f scripts/init_database.sql
```

### 4. 运行测试

```bash
python test_intelligent_system.py
```

## 📊 核心功能演示

### 数据采集示例

```python
from core.intelligent_system.data_collection.stock_collector import StockDataCollector
import asyncio

async def demo():
    # 创建采集器
    collector = StockDataCollector(tushare_token="your_token")
    
    # 获取涨停股票
    limit_ups = await collector.get_limit_up_stocks()
    print(f"发现 {len(limit_ups)} 只涨停股票")
    
    # 获取日线数据
    daily_data = await collector.get_daily_data(
        stock_code="000001.SZ",
        start_date="20240101",
        end_date="20241231"
    )
    print(f"获取到 {len(daily_data)} 条日线数据")

asyncio.run(demo())
```

### 数据库操作示例

```python
from core.intelligent_system.database.db_manager import DatabaseManager
import asyncio

async def demo():
    # 创建数据库管理器
    db = DatabaseManager(
        database_url="postgresql://boyi:password@localhost:5432/boyi",
        timescaledb_url="postgresql://boyi:password@localhost:5433/boyi_ts"
    )
    
    await db.connect()
    
    # 保存日线数据
    await db.save_stock_daily_data(daily_data)
    
    # 查询数据
    data = await db.get_stock_daily_data(
        stock_code="000001.SZ",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    await db.disconnect()

asyncio.run(demo())
```

## 🔧 下一步开发计划

### P0 - 核心功能（本周完成）

1. **PhaseAnalysisAgent（五阶段识别）**
   - 文件: `core/intelligent_system/agents/phase_analyzer.py`
   - 功能: Agent驱动的阶段识别
   - 依赖: LangChain + OpenAI

2. **知识库基础**
   - 文件: `core/intelligent_system/agents/knowledge_base.py`
   - 功能: 博弈理论知识存储和检索
   - 依赖: ChromaDB + Sentence Transformers

3. **定时任务调度器**
   - 文件: `core/intelligent_system/scheduler/task_scheduler.py`
   - 功能: 定时执行数据采集和Agent分析
   - 依赖: APScheduler

### P1 - Web服务（下周完成）

4. **FastAPI Web服务**
   - 文件: `core/intelligent_system/api/main.py`
   - 功能: REST API + WebSocket推送
   - 依赖: FastAPI + Uvicorn

5. **前端看板**
   - 文件: `frontend/src/views/DashboardView.vue`
   - 功能: 实时监控看板
   - 依赖: Vue 3 + Element Plus

## 📁 完整目录结构

```
Aiansys_boyijiaoyi/
├── core/
│   └── intelligent_system/
│       ├── __init__.py
│       ├── config.py
│       ├── database/
│       │   ├── __init__.py
│       │   └── db_manager.py
│       ├── data_collection/
│       │   ├── __init__.py
│       │   └── stock_collector.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── phase_analyzer.py (待开发)
│       │   └── knowledge_base.py (待开发)
│       ├── scheduler/
│       │   ├── __init__.py
│       │   └── task_scheduler.py (待开发)
│       └── api/
│           ├── __init__.py
│           └── main.py (待开发)
├── scripts/
│   └── init_database.sql
├── test_intelligent_system.py
├── requirements_intelligent.txt
└── .env
```

## ⚠️ 注意事项

1. **数据源限制**
   - Tushare需要积分才能获取更多数据
   - Akshare免费但请求频率有限制
   - 建议本地缓存数据

2. **数据库要求**
   - PostgreSQL 12+
   - TimescaleDB 2.0+
   - 推荐使用Docker部署

3. **API密钥**
   - 需要OpenAI API Key（GPT-4）
   - 需要Tushare Token
   - 请妥善保管，不要提交到Git

## 🎯 测试清单

- [ ] 数据库连接正常
- [ ] 数据采集功能正常
- [ ] 日线数据保存成功
- [ ] Agent分析功能（待开发）
- [ ] Web服务启动（待开发）

## 📞 问题排查

### 问题1: 数据库连接失败
```bash
# 检查PostgreSQL是否运行
docker ps | grep postgres

# 检查端口
netstat -an | grep 5432

# 测试连接
psql -h localhost -U boyi -d boyi
```

### 问题2: Tushare无法获取数据
```bash
# 检查Token是否正确
echo $TUSHARE_TOKEN

# 测试API
python -c "import tushare as ts; ts.set_token('your_token'); print(ts.pro_api().trade_calendar(exchange='SSE', start_date='20240101', end_date='20240110'))"
```

### 问题3: 依赖安装失败
```bash
# 使用国内镜像
pip install -r requirements_intelligent.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# TA-Lib需要单独安装
# Windows: 下载whl文件安装
# Linux: sudo apt-get install ta-lib
# Mac: brew install ta-lib
```

## 🎉 完成标志

当看到以下输出时，说明基础功能已就绪：

```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
博弈交易法智能分析系统 - 基础功能测试
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
测试1: 数据采集功能
============================================================

[测试] 获取大盘指数...
✓ 成功获取 3 个大盘指数

[测试] 获取涨停股票...
✓ 发现 20 只涨停股票

[测试] 获取日线数据...
✓ 成功获取 250 条日线数据

============================================================
测试2: 数据库功能
============================================================

[测试] 数据库连接...
✓ 数据库连接成功

[测试] 保存日线数据...
✓ 日线数据保存成功

============================================================
✅ 测试完成！
============================================================
```

准备好后，我们继续开发 **PhaseAnalysisAgent**！
