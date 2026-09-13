# 🔍 配置错误排查指南

## 问题: 点击"配置"按钮报错

### 排查步骤:

---

### 1️⃣ 检查后端是否启动

**测试命令:**

```bash
# 检查健康状态
curl http://localhost:8000/api/health
```

**预期响应:**

```json
{
  "status": "healthy",
  "agent_configured": false,
  "tools_loaded": true,
  "env_configured": true
}
```

**如果无响应:**
- 后端未启动,运行: `python start_agent_ui.py`

---

### 2️⃣ 检查环境变量是否加载

**测试命令:**

```bash
python test_env.py
```

**预期输出:**

```
OPENAI_API_KEY: pk-f76c715b-429c-40b...
OPENAI_BASE_URL: https://modelservice.jdcloud.com/coding/openai/v1
QWEN_MODEL: GLM-5
```

**如果显示NOT FOUND:**
- 检查 `.env` 文件是否在项目根目录
- 检查文件内容格式是否正确

---

### 3️⃣ 测试API接口

**测试命令:**

```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"pk-f76c715b-429c-40bd-87c4-b4077464b4ae\",\"model\":\"GLM-5\",\"base_url\":\"https://modelservice.jdcloud.com/coding/openai/v1\"}"
```

**预期响应:**

```json
{
  "success": true,
  "message": "Agent配置成功",
  "tools_count": 7,
  "tools": ["fetch_kline", "calc_indicators", ...]
}
```

**如果失败:**
- 查看后端终端的错误日志
- 检查API Key是否有效
- 检查Base URL是否可访问

---

### 4️⃣ 检查浏览器控制台

**打开方式:**
1. 按 F12
2. 切换到 Console 标签
3. 查看错误信息

**常见错误:**

#### 错误1: Network Error

```
Error: Network Error
```

**原因:** 后端未启动或跨域问题
**解决:** 确保后端已启动

---

#### 错误2: 404 Not Found

```
POST http://localhost:8000/api/config 404 (Not Found)
```

**原因:** 路由路径错误
**解决:** 检查后端路由是否正确注册

---

#### 错误3: 500 Internal Server Error

```
POST http://localhost:8000/api/config 500 (Internal Server Error)
```

**原因:** 后端代码错误
**解决:** 查看后端终端日志,修复代码错误

---

### 5️⃣ 查看后端日志

**启动后端时的输出:**

```
[环境变量] 已加载: G:\projects\博弈交易\Aiansys_boyijiaoyi\.env
[自动初始化] 检测到环境变量配置
  API Key: pk-f76c715b-429c-4...
  Base URL: https://modelservice.jdcloud.com/coding/openai/v1
  Model: GLM-5
[自动初始化] Agent配置成功! 已加载 7 个工具
```

**如果没有自动初始化:**
- 检查环境变量是否正确加载
- 检查API Key格式

---

## 🛠️ 快速修复方案

### 方案1: 手动配置(推荐)

1. 启动后端: `python start_agent_ui.py`
2. 打开前端,点击"Agent框架"
3. 点击左侧"配置Agent"按钮
4. 输入配置:
   - API Key: `pk-f76c715b-429c-40bd-87c4-b4077464b4ae`
   - Model: `GLM-5`
   - Base URL: `https://modelservice.jdcloud.com/coding/openai/v1`
5. 点击"配置"按钮

---

### 方案2: 重启服务

```bash
# 1. 停止所有服务
Ctrl + C

# 2. 重新启动后端
python start_agent_ui.py

# 3. 重新启动前端
cd frontend
npm run dev
```

---

### 方案3: 检查端口占用

```bash
# Windows
netstat -ano | findstr :8000

# 如果有进程占用,杀掉进程
taskkill /PID <PID> /F
```

---

## 📊 当前配置信息

### 后端环境变量 (.env)

```env
OPENAI_API_KEY=pk-f76c715b-429c-40bd-87c4-b4077464b4ae
OPENAI_BASE_URL=https://modelservice.jdcloud.com/coding/openai/v1
QWEN_MODEL=GLM-5
```

### 前端环境变量 (frontend/.env)

```env
VITE_OPENAI_API_KEY=pk-f76c715b-429c-40bd-87c4-b4077464b4ae
VITE_OPENAI_BASE_URL=https://modelservice.jdcloud.com/coding/openai/v1
VITE_QWEN_MODEL=GLM-5
```

---

## 🎯 预期行为

### 正常启动流程:

1. **后端启动**
   ```
   [环境变量] 已加载: ...
   [自动初始化] Agent配置成功! 已加载 7 个工具
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. **前端访问**
   - 显示"已就绪"状态
   - 工具列表显示7个工具
   - 可以直接输入任务

3. **开始对话**
   - 输入问题
   - Agent响应
   - 多轮对话

---

## 💡 常见问题

### Q: 为什么环境变量没生效?

**A:** 检查:
1. `.env` 文件是否在项目根目录
2. 文件名是否正确(注意是 `.env`,不是 `env`)
3. 文件格式是否正确(没有多余空格)

### Q: 为什么配置失败?

**A:** 可能原因:
1. API Key无效或过期
2. Base URL无法访问
3. 网络问题
4. 后端未正确加载环境变量

### Q: 如何验证配置成功?

**A:** 访问健康检查接口:

```bash
curl http://localhost:8000/api/health
```

应该看到 `agent_configured: true`

---

## 🚀 完整启动命令

```bash
# 1. 确保在项目根目录
cd G:\projects\博弈交易\Aiansys_boyijiaoyi

# 2. 启动后端
python start_agent_ui.py

# 3. 新开终端,启动前端
cd frontend
npm run dev

# 4. 访问
# 前端地址: http://localhost:5173 (或其他端口)
# 点击导航中的"Agent框架"
```

---

**如果以上步骤都无法解决,请提供:**
1. 后端终端的完整日志
2. 浏览器控制台的错误信息
3. 具体的错误截图
