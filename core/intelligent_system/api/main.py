"""
FastAPI Web服务

提供REST API和WebSocket实时推送
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from datetime import datetime
import json

from core.intelligent_system.config import settings
from core.intelligent_system.database.db_manager import get_db_manager
from core.intelligent_system.data_collection.stock_collector import get_collector
from core.intelligent_system.agents.phase_analyzer import get_phase_agent

# 创建FastAPI应用
app = FastAPI(
    title="博弈交易法智能分析系统",
    description="基于博弈理论的智能股票分析系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


# ========== 数据模型 ==========

class StockAnalysisRequest(BaseModel):
    """股票分析请求"""
    stock_code: str


class AlertResponse(BaseModel):
    """预警响应"""
    id: int
    alert_type: str
    stock_code: Optional[str]
    title: str
    message: Optional[str]
    priority: int
    status: str
    create_time: datetime


# ========== REST API ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "博弈交易法智能分析系统",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now()
    }


# ========== 股票数据API ==========

@app.get("/api/stocks/{stock_code}")
async def get_stock_info(stock_code: str):
    """获取股票基本信息"""
    try:
        db = await get_db_manager()
        info = await db.get_stock_info(stock_code)
        
        if not info:
            raise HTTPException(status_code=404, detail="股票不存在")
        
        return info
        
    except Exception as e:
        logger.error(f"获取股票信息失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{stock_code}/kline")
async def get_stock_kline(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 180
):
    """获取股票K线数据"""
    try:
        db = await get_db_manager()
        
        # 默认时间范围
        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await db.get_stock_daily_data(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return {
            "stock_code": stock_code,
            "count": len(data),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"获取K线数据失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{stock_code}/realtime")
async def get_realtime_quote(stock_code: str):
    """获取实时行情"""
    try:
        collector = get_collector()
        quote = await collector.get_realtime_quote(stock_code)
        
        if not quote:
            raise HTTPException(status_code=404, detail="无法获取实时行情")
        
        return quote
        
    except Exception as e:
        logger.error(f"获取实时行情失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Agent分析API ==========

@app.post("/api/analyze/{stock_code}")
async def analyze_stock(stock_code: str):
    """
    Agent分析股票
    
    返回详细的阶段分析结果
    """
    try:
        logger.info(f"开始分析股票 {stock_code}")
        
        # 获取Agent
        agent = await get_phase_agent()
        
        # 获取数据库管理器
        db = await get_db_manager()
        
        # 获取K线数据
        kline_data = await db.get_stock_daily_data(
            stock_code=stock_code,
            start_date=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            limit=180
        )
        
        if len(kline_data) < 60:
            raise HTTPException(
                status_code=400,
                detail="数据不足，至少需要60个交易日的数据"
            )
        
        # Agent分析
        result = await agent.analyze(
            stock_code=stock_code,
            kline_data=kline_data
        )
        
        return {
            "stock_code": stock_code,
            "analysis": result,
            "analyzed_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/{stock_code}/analysis")
async def get_stock_analysis(stock_code: str):
    """获取股票的最新分析结果"""
    try:
        db = await get_db_manager()
        
        # 从TimescaleDB获取最新分析
        result = await db.get_latest_agent_analysis(
            stock_code=stock_code,
            analysis_type="phase_analysis"
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="暂无分析结果")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析结果失败 {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 预警API ==========

@app.get("/api/alerts")
async def get_alerts(limit: int = 50):
    """获取预警列表"""
    try:
        db = await get_db_manager()
        alerts = await db.get_unread_alerts(user_id=1, limit=limit)
        
        return {
            "count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"获取预警失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 市场数据API ==========

@app.get("/api/market/indices")
async def get_market_indices():
    """获取大盘指数"""
    try:
        collector = get_collector()
        indices = await collector.get_market_indices()
        
        return {
            "count": len(indices),
            "indices": indices
        }
        
    except Exception as e:
        logger.error(f"获取大盘指数失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/limit-up")
async def get_limit_up_stocks():
    """获取涨停股票"""
    try:
        collector = get_collector()
        stocks = await collector.get_limit_up_stocks()
        
        return {
            "count": len(stocks),
            "stocks": stocks
        }
        
    except Exception as e:
        logger.error(f"获取涨停股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== WebSocket实时推送 ==========

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """广播消息"""
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点"""
    await manager.connect(websocket)
    
    try:
        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "CONNECTED",
            "message": "WebSocket连接成功",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        # 保持连接
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                logger.info(f"收到客户端消息: {message}")
                
                # 处理不同类型的消息
                if message.get("type") == "PING":
                    await manager.send_personal_message({
                        "type": "PONG",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            except json.JSONDecodeError:
                logger.warning(f"无效的JSON消息: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"客户端 {client_id} 断开连接")


# ========== 启动事件 ==========

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 60)
    logger.info("博弈交易法智能分析系统启动中...")
    logger.info("=" * 60)
    
    # 初始化数据库连接
    try:
        db = await get_db_manager()
        logger.info("✓ 数据库连接成功")
    except Exception as e:
        logger.error(f"✗ 数据库连接失败: {e}")
    
    logger.info("=" * 60)
    logger.info("🚀 系统启动完成！")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("系统关闭中...")
    
    # 关闭数据库连接
    try:
        db = await get_db_manager()
        await db.disconnect()
        logger.info("✓ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"✗ 数据库关闭失败: {e}")


# 需要导入timedelta
from datetime import timedelta


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
