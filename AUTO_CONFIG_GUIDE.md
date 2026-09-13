# 环境变量自动配置说明

## ✅ 已支持环境变量自动配置

Agent框架现在支持从环境变量自动读取配置,无需手动输入!

---

## 🔧 配置方式

### 方式一: 使用项目根目录的.env文件(推荐)

在项目根目录创建 `.env` 文件:

```env
OPENAI_API_KEY=pk-f76c715b-429c-40bd-87c4-b4077464b4ae
OPENAI_BASE_URL=https://modelservice.jdcloud.com/coding/openai/v1
QWEN_MODEL=GLM-5
```

### 方式二: 使用前端的.env文件

在 `frontend/.env` 文件中配置:

```env
VITE_OPENAI_API_KEY=pk-f76c715b-429c-40bd-87c4-b4077464b4ae
VITE_OPENAI_BASE_URL=https://modelservice.jdcloud.com/coding/openai/v1
VITE_QWEN_MODEL=GLM-5
```

---

## 🚀 自动配置流程

### 后端自动初始化

启动后端时,会自动检测环境变量:

```bash
python start_agent_ui.py
```

**输出示例:**

```
============================================================
启动Web服务...
============================================================

服务地址:
  - Web界面: http://localhost:8000/ui
  - API文档: http://localhost:8000/docs
  - 健康检查: http://localhost:8000/api/health

[自动初始化] 检测到环境变量配置
  API Key: pk-f76c715b-429c-4...
  Base URL: https://modelservice.jdcloud.com/coding/openai/v1
  Model: GLM-5
[自动初始化] Agent配置成功! 已加载 7 个工具
```

### 前端自动配置

前端启动时,会自动读取环境变量并配置:

1. 如果检测到环境变量配置,自动调用配置接口
2. 无需手动点击"配置Agent"
3. 直接开始对话

---

## 📊 配置优先级

配置读取优先级(从高到低):

1. **手动输入** - 在界面中手动配置
2. **前端环境变量** - `frontend/.env`
3. **后端环境变量** - 项目根目录 `.env`

---

## 🔍 检查配置状态

### 查看健康状态

访问: http://localhost:8000/api/health

```json
{
  "status": "healthy",
  "agent_configured": true,
  "tools_loaded": true,
  "env_configured": true
}
```

- `env_configured: true` - 环境变量已配置

---

## 💡 使用示例

### 首次使用(有环境变量)

1. **启动后端**: `python start_agent_ui.py`
   - 自动读取环境变量并配置Agent

2. **启动前端**: `cd frontend && npm run dev`

3. **访问界面**: 点击 "Agent框架"
   - 自动配置,直接显示"已就绪"

4. **开始对话**: 无需手动配置

### 首次使用(无环境变量)

1. **启动服务**

2. **点击配置**: 点击左侧"配置Agent"按钮

3. **输入配置**: 如果.env文件中有配置,会自动填充

4. **确认配置**: 点击"配置"按钮

---

## ⚠️ 注意事项

### 1. API Key安全

- `.env` 文件不要提交到Git
- 已在 `.gitignore` 中添加

### 2. 环境变量格式

**后端环境变量:**
```env
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
QWEN_MODEL=GLM-5
```

**前端环境变量(需要VITE_前缀):**
```env
VITE_OPENAI_API_KEY=your-key
VITE_OPENAI_BASE_URL=https://api.openai.com/v1
VITE_QWEN_MODEL=GLM-5
```

### 3. 修改配置后重启

修改 `.env` 文件后,需要重启服务才能生效:

```bash
# 停止服务
Ctrl + C

# 重启服务
python start_agent_ui.py
```

---

## 🎯 当前配置

您的项目已配置:

- ✅ API Key: `pk-f76c715b-429c-40bd-87c4-b4077464b4ae`
- ✅ Base URL: `https://modelservice.jdcloud.com/coding/openai/v1`
- ✅ Model: `GLM-5`

**可以直接使用,无需手动配置!**

---

## 🚀 快速启动

```bash
# 1. 启动后端(自动配置)
python start_agent_ui.py

# 2. 启动前端(自动配置)
cd frontend
npm run dev

# 3. 访问界面,开始对话
```

---

**环境变量配置完成!享受零配置的Agent体验!** 🎉
