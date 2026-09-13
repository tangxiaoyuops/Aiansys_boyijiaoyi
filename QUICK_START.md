# 🚀 快速启动指南

## 一步启动Web UI

### Windows用户:

双击运行 `start_agent_ui.py` 或在命令行执行:

```bash
python start_agent_ui.py
```

### Linux/Mac用户:

```bash
python start_agent_ui.py
```

---

## 访问地址

启动成功后,在浏览器中打开:

**🌐 Web界面**: http://localhost:8000/ui

**📚 API文档**: http://localhost:8000/docs

---

## 使用流程

```
┌─────────────────┐
│  1. 配置Agent    │  输入API Key
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 输入任务     │  描述分析需求
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 开始分析     │  点击按钮执行
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 查看结果     │  分析结论+轨迹
└─────────────────┘
```

---

## 示例任务

### 简单分析:
```
获取股票000001的K线数据
```

### 阶段判断:
```
分析股票000001处于哪个阶段
```

### 洗盘识别:
```
股票000001是否有洗盘行为
```

### 完整分析:
```
完整分析股票000001,包括阶段、洗盘、买卖点
```

---

## 首次使用必读

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备API Key

- 获取OpenAI API Key: https://platform.openai.com/api-keys
- 或使用兼容的API服务

### 3. 启动服务

```bash
python start_agent_ui.py
```

---

## 功能特性

✅ ReAct自主循环
✅ 工具自动选择
✅ 执行轨迹追踪
✅ 实时结果展示
✅ 快速任务模板
✅ API接口完整

---

## 遇到问题?

### 查看详细文档

- [Web UI使用指南](core/agent_framework/api/WEB_UI_GUIDE.md)
- [框架使用指南](core/agent_framework/USAGE_GUIDE.md)
- [框架README](core/agent_framework/README.md)

### 检查依赖

```bash
pip list | grep -E "fastapi|uvicorn|openai|pydantic"
```

### 查看日志

终端会实时显示:
- Agent决策过程
- 工具调用详情
- 错误信息

---

## 快速测试API

### 健康检查

```bash
curl http://localhost:8000/api/health
```

### 列出工具

```bash
curl http://localhost:8000/api/tools
```

---

**祝您使用愉快! 🎉**
