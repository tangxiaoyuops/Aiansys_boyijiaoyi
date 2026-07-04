# 博弈交易选股策略系统 - 快速启动指南

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 进入项目目录
cd g:\projects\博弈交易\Aiansys_boyijiaoyi

# 启动后端服务
python -m uvicorn server.app:app --reload --port 8000
```

### 2. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖(如果还没安装)
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问系统

打开浏览器访问: http://localhost:5173

点击导航栏中的 **"选股策略"** 进入选股系统

---

## 📖 使用说明

### 方式一: Web界面使用

1. **选择配置类型**
   - 标准配置: 平衡风险和收益
   - 保守型配置: 更低风险,适合稳健投资者
   - 激进型配置: 更高风险,适合激进投资者

2. **选择股票池**
   - 手动输入: 输入股票代码,多个代码用逗号或换行分隔
   - 预设股票池: 沪深300、自选股、测试股票池

3. **执行选股**
   - 点击"开始选股"按钮
   - 等待系统分析完成
   - 查看推荐股票列表

4. **查看详细信息**
   - 点击股票卡片展开详细信息
   - 查看买点信号、评分详情、仓位建议等

5. **单只股票分析**
   - 输入单只股票代码
   - 点击"分析"按钮
   - 查看该股票的详细买点信号

### 方式二: API调用

#### 1. 执行选股

```bash
curl -X POST "http://localhost:8000/api/selection/select" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": ["600519", "000001", "600036"],
    "config_type": "standard"
  }'
```

#### 2. 分析单只股票

```bash
curl -X POST "http://localhost:8000/api/selection/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "600519",
    "days": 250
  }'
```

#### 3. 运行回测

```bash
curl -X POST "http://localhost:8000/api/selection/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "codes": ["600519", "000001", "600036"],
    "start_date": "2025-01-01",
    "end_date": "2025-03-31",
    "rebalance_freq": "weekly"
  }'
```

### 方式三: Python脚本

```python
from core.selection import StockSelectionStrategy, SelectionConfig

# 创建配置
config = SelectionConfig()  # 或保守型: SelectionConfig.conservative()

# 创建选股策略
strategy = StockSelectionStrategy(config)

# 定义股票池
stock_pool = ["600519", "000001", "600036", "000333", "600030"]

# 执行选股
result = strategy.select_stocks_sync(stock_pool)

# 查看推荐股票
for candidate in result.top_candidates:
    print(f"{candidate.code} {candidate.name}")
    print(f"  评分: {candidate.overall_score:.1f}")
    print(f"  买点: {candidate.best_buy_point.buy_type}")
    print(f"  价格: {candidate.best_buy_point.price:.2f}")
    print(f"  建议仓位: {candidate.suggested_position_pct*100:.1f}%")
    print(f"  建议买入: {candidate.suggested_shares}股")
```

---

## 📊 功能特性

### ✨ 核心功能

1. **智能买点识别**
   - 恐慌点买入(大阴线+放量)
   - 恐慌点后最低价买入
   - O点买入(趋势起点)
   - 洗盘结束买入

2. **多维度评分**
   - 阶段评分(30%)
   - 趋势评分(25%)
   - 形态评分(25%)
   - 情绪评分(20%)

3. **智能仓位分配**
   - 根据评分自动分配仓位
   - 单只股票仓位控制
   - 分散风险

4. **风险控制**
   - 阶段过滤
   - 止损止盈建议
   - 置信度验证

5. **历史回测**
   - 策略验证
   - 绩效分析
   - 优化建议

---

## ⚙️ 配置说明

### 标准配置
- 初始资金: 100万
- 最大持仓: 10只
- 单只仓位: ≤20%
- 止损: 8%
- 止盈: 15%

### 保守型配置
- 初始资金: 100万
- 最大持仓: 5只
- 单只仓位: ≤15%
- 止损: 5%
- 止盈: 12%

### 激进型配置
- 初始资金: 100万
- 最大持仓: 15只
- 单只仓位: ≤25%
- 止损: 10%
- 止盈: 20%

### 自定义配置

```python
config = SelectionConfig(
    initial_capital=500000,
    max_stocks=8,
    max_position_per_stock=0.15,
    panic_drop_threshold=-3.5,
    preferred_stages=[1, 2],
    stop_loss_ratio=0.06
)
```

---

## 📝 示例脚本

### 1. 基础选股示例

```bash
python examples/selection_examples.py
```

选择选项1-4查看不同的使用场景

### 2. 完整测试

```bash
python test_selection_strategy.py
```

运行完整的功能测试

---

## 📚 文档资源

- **使用指南**: `.cursor/skills/boyi-trading-system/selection_guide.md`
- **博弈理论**: `.cursor/skills/boyi-trading-system/SKILL.md`
- **API文档**: 访问 http://localhost:8000/docs

---

## ⚠️ 风险提示

1. **本系统基于博弈交易理论开发,仅供参考,不构成投资建议**
2. **股市有风险,投资需谨慎**
3. **历史表现不代表未来收益**
4. **请结合自身风险承受能力做出决策**
5. **严格执行止损纪律,控制仓位**

---

## 🔧 常见问题

### Q1: 为什么没有推荐股票?

**A:** 可能的原因:
- 股票池中没有符合买点条件的股票
- 筛选条件过于严格
- 当前市场环境不适合买入

**解决方案:**
- 扩大股票池范围
- 调整配置参数
- 等待更好的买入时机

### Q2: 如何查看详细的买点信息?

**A:** 点击股票卡片即可展开查看完整信息,包括:
- 买点类型和信号日期
- 置信度和评分详情
- 仓位建议和筛选条件

### Q3: 如何调整策略参数?

**A:** 有两种方式:
1. Web界面: 选择不同的配置类型
2. API调用: 传入custom_config参数

### Q4: 回测结果与实际交易会有差异吗?

**A:** 是的,回测存在局限性:
- 历史数据不代表未来
- 实际交易会有滑点和冲击成本
- 市场环境会变化

---

## 💡 使用建议

1. **先用小资金测试**,验证策略有效性
2. **定期回顾调整**,每周/每月复盘优化
3. **严格执行纪律**,按信号执行不犹豫
4. **关注大盘环境**,顺势而为
5. **控制情绪**,不被贪婪和恐惧左右

---

**记住: 交易是一场修行,改变自己才能从地狱走向天堂!** 🌟