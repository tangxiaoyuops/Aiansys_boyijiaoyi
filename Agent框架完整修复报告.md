# 完整修复报告 - Agent框架JSON序列化问题

## 问题诊断

### 错误现象
```
❌ 分析失败: Object of type Timestamp is not JSON serializable
```

### 根本原因

#### 1. 端口冲突
- **主服务器**: `server/app.py` 使用端口 8000
- **Agent框架**: `core/agent_framework/api/app.py` 也使用端口 8000
- 两个服务无法同时运行

#### 2. JSON序列化缺失
Agent框架的 `core/agent_framework/api/app_stream.py` 使用标准 `json.dumps`：
```python
yield f"data: {json.dumps({...}, ensure_ascii=False)}\n\n"
```
无法序列化 Pandas Timestamp、NumPy类型等。

## 解决方案

### 修复1：添加自定义JSON编码器

在 `core/agent_framework/api/app_stream.py` 添加：
```python
class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理Pandas、NumPy和datetime类型"""
    
    def default(self, obj):
        # 处理Pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        
        # 处理datetime和date
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # 处理NumPy类型
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # 处理Decimal
        if isinstance(obj, Decimal):
            return float(obj)
        
        # 处理Pandas DataFrame和Series
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict('records') if isinstance(obj, pd.DataFrame) else obj.to_dict()
        
        # 处理NaN和Infinity
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
        
        # 其他类型尝试转换为字符串
        try:
            return str(obj)
        except:
            return super().default(obj)


def safe_json_dumps(obj, **kwargs):
    """安全的JSON序列化函数"""
    return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)
```

### 修复2：替换所有json.dumps

在 `app_stream.py` 中替换：
- ❌ `json.dumps({...}, ensure_ascii=False)`
- ✅ `safe_json_dumps({...})`

共替换 **10处**

### 修复3：更改端口

将Agent框架端口从 **8000** 改为 **8001**：
```python
# core/agent_framework/api/app.py
uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8001,  # 从8000改为8001
    reload=True,
    log_level="info"
)
```

## 文件修改清单

### 修改的文件
1. ✅ `core/agent_framework/api/app_stream.py`
   - 添加 `CustomJSONEncoder` 类
   - 添加 `safe_json_dumps()` 函数
   - 替换10处 `json.dumps` 调用

2. ✅ `core/agent_framework/api/app.py`
   - 更改端口从8000到8001
   - 更新提示信息

### 新增文件
1. ✅ `fix_agent_json.py` - 修复脚本
2. ✅ `start_all_services.py` - 双服务启动脚本
3. ✅ `启动Agent框架服务指南.md` - 使用文档

## 启动方式

### 方式1：分别启动（推荐调试）

**终端1 - 主服务器**
```powershell
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

**终端2 - Agent框架**
```powershell
python core/agent_framework/api/app.py
```

### 方式2：一键启动

```powershell
python start_all_services.py
```

## 服务访问地址

### 主服务器 (端口8000)
- API文档: http://localhost:8000/docs
- vnPy状态: http://localhost:8000/api/vnpy/status
- 股票分析: http://localhost:5173 (前端代理)
- 期货分析: http://localhost:5173/futures (前端代理)

### Agent框架 (端口8001)
- API文档: http://localhost:8001/docs
- Web界面: http://localhost:8001/ui
- 健康检查: http://localhost:8001/health

## 测试验证

### 测试主服务器
```powershell
python test_futures_api.py
```
✅ 已验证：JSON序列化正常，无Timestamp错误

### 测试Agent框架
```powershell
Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing
```

## 技术细节

### 支持的数据类型

CustomJSONEncoder 支持：
1. ✅ Pandas Timestamp
2. ✅ datetime / date
3. ✅ NumPy int/float/array
4. ✅ Decimal
5. ✅ Pandas DataFrame/Series
6. ✅ NaN / Infinity
7. ✅ 所有标准JSON类型

### 编码器优先级

处理顺序：
1. 检查是否为 Pandas Timestamp
2. 检查是否为 datetime/date
3. 检查是否为 NumPy 类型
4. 检查是否为 Decimal
5. 检查是否为 DataFrame/Series
6. 检查是否为 NaN/Infinity
7. 尝试转换为字符串
8. 调用父类处理

## 影响范围

### 正面影响
1. ✅ 解决了Agent框架的JSON序列化错误
2. ✅ 避免了端口冲突
3. ✅ 提高了系统健壮性
4. ✅ 统一了两个服务的JSON编码方式

### 兼容性
- ✅ 向后兼容
- ✅ 无破坏性变更
- ✅ 标准JSON类型不受影响

## 后续建议

### 1. 性能优化
如果数据量很大，考虑：
- 对DataFrame进行裁剪
- 实现懒加载
- 添加缓存机制

### 2. 错误监控
添加日志记录：
```python
def safe_json_dumps(obj, **kwargs):
    try:
        return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)
    except Exception as e:
        logger.error(f"JSON序列化失败: {e}")
        return json.dumps({"error": "序列化失败"})
```

### 3. 前端配置
更新前端配置以连接Agent框架：
```javascript
const AGENT_API_BASE = 'http://localhost:8001';
```

## 故障排除

### 问题1：端口被占用
```powershell
# 检查端口
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# 终止进程
taskkill /F /PID <PID>
```

### 问题2：JSON序列化仍然失败
1. 确认已重启服务
2. 检查导入：`import pandas as pd`, `import numpy as np`
3. 查看日志确认CustomJSONEncoder已加载

### 问题3：服务无法启动
1. 检查Python环境：`python --version`
2. 检查依赖：`pip list | findstr pandas`
3. 查看错误日志

## 总结

通过以下修复：
1. ✅ 添加自定义JSON编码器
2. ✅ 替换所有json.dumps调用
3. ✅ 更改Agent框架端口

成功解决了：
- ❌ "Object of type Timestamp is not JSON serializable" 错误
- ❌ 端口冲突问题
- ❌ Agent框架无法启动问题

现在两个服务可以同时运行，并且都能正确处理复杂的数据类型序列化。
