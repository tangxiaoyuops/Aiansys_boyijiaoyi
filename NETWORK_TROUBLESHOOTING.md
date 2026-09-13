# 🔧 网络错误排查

## ❌ 问题: 前端报错 "network error"

---

## ✅ 排查步骤

### 1. 检查后端服务是否运行

```bash
# Windows
netstat -ano | findstr :8001

# 应该看到 LISTENING
TCP    0.0.0.0:8001    0.0.0.0:0    LISTENING
```

**如果没看到:**
```bash
python start_agent_ui.py
```

---

### 2. 测试API是否可访问

```bash
# 用浏览器访问
http://localhost:8001/api/health

# 应该看到
{
  "status": "healthy",
  "agent_configured": true,
  "tools_loaded": true
}
```

---

### 3. 检查前端配置

**正确的API地址:**
```typescript
const API_BASE = 'http://localhost:8001/api';
```

---

### 4. 检查浏览器控制台

**打开方式:**
1. 按 F12
2. 切换到 Console 标签
3. 查看错误信息

**常见错误:**

#### 错误1: CORS跨域
```
Access to XMLHttpRequest at 'http://localhost:8001/api/analyze/stream' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决:** 后端已配置CORS允许所有来源,应该不会有这个问题

#### 错误2: Connection refused
```
ERR_CONNECTION_REFUSED
```

**解决:** 后端未启动,运行 `python start_agent_ui.py`

#### 错误3: Net::ERR_BLOCKED_BY_CLIENT
```
ERR_BLOCKED_BY_CLIENT
```

**解决:** 关闭浏览器广告拦截插件

---

## 🎯 已修复的问题

### 问题: fetch API跨域问题

**原因:** 
- 原生fetch可能有跨域限制
- 某些浏览器不支持ReadableStream

**解决:**
- 改用axios
- axios已经配置了跨域支持

---

## 📝 测试连接

### 方法1: 浏览器直接访问

打开浏览器访问:
```
http://localhost:8001/api/health
```

**预期结果:**
```json
{
  "status": "healthy"
}
```

### 方法2: Python测试

```bash
python test_real_api.py
```

**预期输出:**
```
健康检查: 200
工具列表: 200
流式端点: 200
```

---

## 🚀 启动顺序

**正确的启动顺序:**

```bash
# 1. 启动后端 (8001端口)
python start_agent_ui.py

# 2. 等待看到
# INFO: Uvicorn running on http://0.0.0.0:8001
# [自动初始化] Agent配置成功!

# 3. 启动前端
cd frontend
npm run dev

# 4. 访问前端
# 点击 "Agent框架"
```

---

## 💡 调试技巧

### 查看前端请求

1. 打开浏览器开发者工具 (F12)
2. 切换到 Network 标签
3. 发送一个消息
4. 查看请求详情:
   - Request URL
   - Status Code
   - Response

### 查看后端日志

后端终端会显示:
```
INFO: POST /api/analyze/stream HTTP/1.1" 200 OK
```

---

## 🔧 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 主项目API | 8000 | 您的主项目 |
| Agent框架API | 8001 | Agent服务 ✅ |
| 前端开发 | 5173 | Vite开发服务器 |

---

## ✅ 检查清单

启动前检查:
- [ ] 后端已启动 (8001端口)
- [ ] 前端已启动
- [ ] 浏览器能访问 http://localhost:8001/api/health
- [ ] 前端代码API地址正确
- [ ] 没有广告拦截插件

---

**按照以上步骤排查,应该可以解决网络错误!** 🔧
