"""
通用自主规划Agent框架 - FastAPI后端
提供REST API和Web界面
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# 加载环境变量
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[环境变量] 已加载: {env_path}")
else:
    print(f"[环境变量] 未找到.env文件: {env_path}")

from core.agent_framework import ToolRegistry
from core.agent_framework.agents import ReActAgent
from core.agent_framework.llm_client import LLMClient

# 创建FastAPI应用
app = FastAPI(
    title="通用自主规划Agent框架",
    description="支持ReAct循环、工具调用、嵌套Agent的通用框架",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
agent_instance = None
registry_instance = None
llm_client_instance = None


# ========== 请求模型 ==========

class AnalyzeRequest(BaseModel):
    """分析请求"""
    task: str
    stock_code: Optional[str] = None
    max_iterations: Optional[int] = 10
    context: Optional[Dict[str, Any]] = None


class ConfigRequest(BaseModel):
    """配置请求"""
    api_key: str
    model: Optional[str] = "gpt-4o"
    base_url: Optional[str] = None


# ========== API路由 ==========

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>Agent Framework</title></head>
        <body>
            <h1>通用自主规划Agent框架</h1>
            <p>请访问 <a href="/docs">/docs</a> 查看API文档</p>
            <p>或访问 <a href="/ui">/ui</a> 使用Web界面</p>
        </body>
    </html>
    """


@app.get("/ui", response_class=HTMLResponse)
async def web_ui():
    """Web界面"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="UI文件未找到")


@app.post("/api/config")
async def configure_agent(config: ConfigRequest):
    """配置Agent(设置API Key等)"""
    global agent_instance, registry_instance, llm_client_instance
    
    try:
        # 如果没有传入配置,使用环境变量
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        base_url = config.base_url or os.getenv("OPENAI_BASE_URL")
        model = config.model or os.getenv("QWEN_MODEL", "GLM-5")
        
        if not api_key:
            raise HTTPException(status_code=400, detail="缺少API Key,请配置OPENAI_API_KEY环境变量或传入api_key参数")
        
        # 创建LLM客户端
        llm_client_instance = LLMClient(
            model=model,
            api_key=api_key,
            base_url=base_url
        )
        
        # 创建博弈交易工具注册中心
        from core.agent_framework.examples.boyi_real_tools import create_real_boyi_tool_registry
        registry_instance = create_real_boyi_tool_registry()
        
        # 创建Agent
        agent_instance = ReActAgent(
            name="boyi_master",
            tool_registry=registry_instance,
            llm_client=llm_client_instance,
            max_iterations=15
        )
        
        return {
            "success": True,
            "message": "Agent配置成功",
            "tools_count": len(registry_instance),
            "tools": [tool.metadata.name for tool in registry_instance]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置失败: {str(e)}")


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """执行分析任务"""
    global agent_instance
    
    if not agent_instance:
        raise HTTPException(status_code=400, detail="请先配置Agent(调用/api/config)")
    
    try:
        # 运行Agent
        result = agent_instance.run(
            user_input={
                "task": request.task,
                "stock_code": request.stock_code
            },
            context=request.context
        )
        
        return {
            "success": True,
            "response": result["response"],
            "iterations": result["iterations"],
            "execution_trace": result["execution_trace"],
            "collected_info": result["collected_info"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/api/analyze/stream")
async def analyze_stream(request: AnalyzeRequest):
    """流式执行分析任务 - 实时推送每一步"""
    global agent_instance
    
    if not agent_instance:
        raise HTTPException(status_code=400, detail="请先配置Agent(调用/api/config)")
    
    from .app_stream import stream_agent_execution
    
    return StreamingResponse(
        stream_agent_execution(
            agent_instance,
            user_input={
                "task": request.task,
                "stock_code": request.stock_code
            },
            context=request.context
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/tools")
async def list_tools():
    """列出所有可用工具"""
    global registry_instance
    
    if not registry_instance:
        # 返回默认工具列表
        from core.agent_framework.examples.boyi_tools import create_boyi_tool_registry
        registry_instance = create_boyi_tool_registry()
    
    tools = []
    for tool in registry_instance:
        tools.append({
            "name": tool.metadata.name,
            "description": tool.metadata.description,
            "type": tool.metadata.tool_type,
            "capabilities": tool.metadata.capabilities,
            "cost_level": tool.metadata.cost_level,
            "estimated_time": tool.metadata.estimated_time
        })
    
    return {
        "success": True,
        "tools": tools,
        "total": len(tools)
    }


@app.get("/api/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """获取工具详细信息"""
    global registry_instance
    
    if not registry_instance:
        from core.agent_framework.examples.boyi_tools import create_boyi_tool_registry
        registry_instance = create_boyi_tool_registry()
    
    try:
        tool = registry_instance.get_tool(tool_name)
        return {
            "success": True,
            "tool": {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "type": tool.metadata.tool_type,
                "parameters": tool.metadata.parameters,
                "required_parameters": tool.metadata.required_parameters,
                "optional_parameters": tool.metadata.optional_parameters,
                "capabilities": tool.metadata.capabilities,
                "examples": tool.metadata.examples,
                "cost_level": tool.metadata.cost_level,
                "estimated_time": tool.metadata.estimated_time
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, parameters: Dict[str, Any]):
    """直接执行工具"""
    global registry_instance
    
    if not registry_instance:
        from core.agent_framework.examples.boyi_tools import create_boyi_tool_registry
        registry_instance = create_boyi_tool_registry()
    
    try:
        tool = registry_instance.get_tool(tool_name)
        result = tool.execute(parameters, {})
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """应用启动时自动初始化"""
    global agent_instance, registry_instance, llm_client_instance
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("QWEN_MODEL", "GLM-5")
    
    if api_key:
        print(f"\n[自动初始化] 检测到环境变量配置")
        print(f"  API Key: {api_key[:20]}...")
        print(f"  Base URL: {base_url}")
        print(f"  Model: {model}")
        
        try:
            # 创建LLM客户端
            llm_client_instance = LLMClient(
                model=model,
                api_key=api_key,
                base_url=base_url
            )
            
            # 创建真实博弈交易工具注册中心
            from core.agent_framework.examples.boyi_real_tools import create_real_boyi_tool_registry
            registry_instance = create_real_boyi_tool_registry()
            
            # 创建Agent
            agent_instance = ReActAgent(
                name="boyi_master",
                tool_registry=registry_instance,
                llm_client=llm_client_instance,
                max_iterations=15
            )
            
            print(f"[自动初始化] Agent配置成功! 已加载 {len(registry_instance)} 个真实工具\n")
            
        except Exception as e:
            print(f"[自动初始化] 失败: {str(e)}\n")
    else:
        print("\n[提示] 未检测到环境变量配置,请在前端界面手动配置\n")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent_configured": agent_instance is not None,
        "tools_loaded": registry_instance is not None,
        "env_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


# ========== 启动配置 ==========

# 确保静态文件目录存在
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# 挂载静态文件
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("通用自主规划Agent框架 - Web服务")
    print("="*60)
    print("\n访问地址:")
    print("  - API文档: http://localhost:8001/docs")
    print("  - Web界面: http://localhost:8001/ui")
    print("\n启动服务...")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
