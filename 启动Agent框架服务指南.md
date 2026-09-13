# 启动Agent框架服务指南

## 问题诊断

### 发现的问题
1. **端口冲突**: Agent框架和主服务器都使用8000端口
2. **JSON序列化**: Agent框架的 `app_stream.py` 缺少自定义编码器
3. **未启动**: Agent框架服务没有运行

### 已完成的修复
✅ 添加了 `CustomJSONEncoder` 到 `app_stream.py`
✅ 替换了所有 `json.dumps` 为 `safe_json_dumps`
✅ 更改Agent框架端口为 **8001**

## 启动步骤

### 方案1：分别启动（推荐）

#### 终端1 - 主服务器（端口8000）
```powershell
cd G:\projects\博弈交易\Aiansys_boyijiaoyi
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

#### 终端2 - Agent框架（端口8001）
```powershell
cd G:\projects\博弈交易\Aiansys_boyijiaoyi
python core/agent_framework/api/app.py
```

### 方案2：使用Python脚本同时启动
创建 `start_all_services.py`:
```python
import subprocess
import time

# 启动主服务器
print("启动主服务器 (端口8000)...")
main_server = subprocess.Popen(
    ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
)

time.sleep(2)

# 启动Agent框架
print("启动Agent框架 (端口8001)...")
agent_server = subprocess.Popen(
    ["python", "core/agent_framework/api/app.py"]
)

print("\n✅ 两个服务已启动:")
print("  - 主服务器: http://localhost:8000")
print("  - Agent框架: http://localhost:8001")
print("  - Agent界面: http://localhost:8001/ui")

try:
    # 等待
    main_server.wait()
    agent_server.wait()
except KeyboardInterrupt:
    print("\n停止服务...")
    main_server.terminate()
    agent_server.terminate()
```

## 访问地址

### 主服务器 (端口8000)
- API文档: http://localhost:8000/docs
- 股票分析: http://localhost:5173 (前端代理)
- 期货分析: http://localhost:5173/futures (前端代理)

### Agent框架 (端口8001)
- API文档: http://localhost:8001/docs
- Web界面: http://localhost:8001/ui
- Agent聊天: http://localhost:8001/agent/chat

## 验证服务

### 测试主服务器
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/vnpy/status -UseBasicParsing
```

### 测试Agent框架
```powershell
Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing
```

## 故障排除

### 如果端口被占用
```powershell
# 检查8000端口
netstat -ano | findstr :8000

# 检查8001端口
netstat -ano | findstr :8001

# 终止进程（替换PID）
taskkill /F /PID <PID>
```

### 如果JSON序列化错误
- 确认已重启服务（代码修改需要重启才能生效）
- 检查日志中是否有 "CustomJSONEncoder" 加载信息

## 前端配置

如果前端需要连接Agent框架，需要配置：
```javascript
const AGENT_API_BASE = 'http://localhost:8001';
```

## 下一步

1. 启动两个服务
2. 访问 http://localhost:8001/ui 使用Agent框架
3. 测试股票分析功能
4. 检查是否还有JSON序列化错误
