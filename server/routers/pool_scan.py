"""
股票池扫描API
提供股票池管理、扫描任务触发、结果查询、定时任务配置等接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pool-scan", tags=["pool-scan"])


# ==================== 请求模型 ====================

class StockPoolCreate(BaseModel):
    """创建股票池请求"""
    pool_id: str
    pool_name: str
    pool_type: str = "custom"  # "hs300" | "custom" | "dynamic"
    codes: List[str] = []
    enabled: bool = True
    scan_days: int = 5


class StockPoolUpdate(BaseModel):
    """更新股票池请求"""
    codes: List[str]
    pool_name: Optional[str] = None
    enabled: Optional[bool] = None
    scan_days: Optional[int] = None


class ScanTriggerRequest(BaseModel):
    """触发扫描请求"""
    pool_id: Optional[str] = None  # 指定股票池ID，None表示扫描所有
    recent_days: int = 5  # 检测最近N天的信号
    notify_channels: List[str] = ["file"]  # 通知渠道


class ScheduleConfig(BaseModel):
    """定时配置请求"""
    cron: str = "30 15 * * 1-5"  # cron表达式
    enabled: bool = True
    pool_ids: List[str] = []  # 空列表表示扫描所有
    recent_days: int = 5
    notify_channels: List[str] = ["file", "email"]


class EmailConfigRequest(BaseModel):
    """邮件配置请求"""
    enabled: bool = True
    smtp_server: str
    smtp_port: int = 465
    smtp_user: str
    smtp_password: str
    use_ssl: bool = True
    recipients: List[EmailStr]
    sender_name: str = "股票扫描助手"


class WebhookConfigRequest(BaseModel):
    """Webhook配置请求"""
    enabled: bool = True
    url: str
    webhook_type: str = "custom"  # "wechat", "dingtalk", "custom"


# ==================== 股票池管理API ====================

@router.get("/pools")
async def list_stock_pools():
    """
    列出所有股票池
    """
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    pools = manager.list_pools()
    
    return {
        "success": True,
        "pools": [p.to_dict() for p in pools]
    }


@router.get("/pools/{pool_id}")
async def get_stock_pool(pool_id: str):
    """
    获取指定股票池
    """
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    pool = manager.get_pool(pool_id)
    
    if not pool:
        raise HTTPException(404, f"股票池不存在: {pool_id}")
    
    return {
        "success": True,
        "pool": pool.to_dict()
    }


@router.post("/pools")
async def create_stock_pool(request: StockPoolCreate):
    """
    创建股票池
    """
    from core.stock_pool.manager import StockPoolManager, StockPoolConfig
    
    manager = StockPoolManager()
    
    if manager.get_pool(request.pool_id):
        raise HTTPException(400, f"股票池已存在: {request.pool_id}")
    
    pool = StockPoolConfig(
        pool_id=request.pool_id,
        pool_name=request.pool_name,
        pool_type=request.pool_type,
        codes=request.codes,
        enabled=request.enabled,
        scan_days=request.scan_days
    )
    
    manager.add_pool(pool)
    
    return {
        "success": True,
        "message": f"股票池 {request.pool_id} 创建成功"
    }


@router.put("/pools/{pool_id}")
async def update_stock_pool(pool_id: str, request: StockPoolUpdate):
    """
    更新股票池
    """
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    
    if not manager.get_pool(pool_id):
        raise HTTPException(404, f"股票池不存在: {pool_id}")
    
    success = manager.update_pool(
        pool_id,
        request.codes,
        pool_name=request.pool_name,
        enabled=request.enabled,
        scan_days=request.scan_days
    )
    
    if not success:
        raise HTTPException(500, "更新股票池失败")
    
    return {
        "success": True,
        "message": f"股票池 {pool_id} 更新成功"
    }


@router.delete("/pools/{pool_id}")
async def delete_stock_pool(pool_id: str):
    """
    删除股票池
    """
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    
    success = manager.delete_pool(pool_id)
    
    if not success:
        raise HTTPException(404, f"股票池不存在: {pool_id}")
    
    return {
        "success": True,
        "message": f"股票池 {pool_id} 已删除"
    }


@router.post("/pools/{pool_id}/toggle")
async def toggle_stock_pool(pool_id: str, enabled: bool):
    """
    启用/禁用股票池
    """
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    
    success = manager.toggle_pool(pool_id, enabled)
    
    if not success:
        raise HTTPException(404, f"股票池不存在: {pool_id}")
    
    return {
        "success": True,
        "message": f"股票池 {pool_id} 已{'启用' if enabled else '禁用'}"
    }


# ==================== 扫描任务API ====================

@router.post("/trigger")
async def trigger_scan(
    request: ScanTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    手动触发一次扫描
    """
    from core.services.pool_scan_service import PoolScanService
    from core.services.notification_service import NotificationService
    from core.stock_pool.manager import StockPoolManager
    
    manager = StockPoolManager()
    
    if request.pool_id:
        pool = manager.get_pool(request.pool_id)
        if not pool:
            raise HTTPException(404, f"股票池不存在: {request.pool_id}")
        codes = pool.codes
        if pool.pool_type == "hs300":
            codes = manager._get_hs300_codes()
    else:
        codes = manager.get_active_pool_codes()
    
    if not codes:
        raise HTTPException(400, "股票池为空")
    
    # 后台执行扫描
    async def run_scan():
        try:
            service = PoolScanService(recent_days=request.recent_days)
            notifier = NotificationService()
            
            result = await service.scan_pool(codes)
            await notifier.send_notification(
                result.to_dict(),
                channels=request.notify_channels
            )
            logger.info(f"[PoolScan] 扫描完成: {len(result.signals)} 个信号")
        except Exception as e:
            logger.error(f"[PoolScan] 扫描失败: {e}")
    
    background_tasks.add_task(run_scan)
    
    return {
        "success": True,
        "message": "扫描任务已启动",
        "stock_count": len(codes)
    }


@router.get("/results")
async def list_scan_results(
    date: Optional[str] = None,
    limit: int = 10
):
    """
    获取扫描结果列表
    """
    output_dir = Path("output/scan_results")
    if not output_dir.exists():
        return {"success": True, "results": []}
    
    files = sorted(
        output_dir.glob("pool_scan_*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )[:limit]
    
    results = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                results.append({
                    "filename": f.name,
                    "scan_time": data.get("scan_time"),
                    "total_stocks": data.get("total_stocks"),
                    "scanned_stocks": data.get("scanned_stocks"),
                    "signals_count": len(data.get("signals", [])),
                    "buy_count": len([s for s in data.get("signals", []) if s.get("signal_type") == "buy"]),
                    "sell_count": len([s for s in data.get("signals", []) if s.get("signal_type") == "sell"])
                })
        except Exception as e:
            logger.error(f"读取结果文件失败: {f}, {e}")
    
    return {"success": True, "results": results}


@router.get("/results/{filename}")
async def get_scan_result(filename: str):
    """
    获取指定扫描结果详情
    """
    filepath = Path("output/scan_results") / filename
    if not filepath.exists():
        raise HTTPException(404, f"结果文件不存在: {filename}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(500, f"读取结果文件失败: {e}")


# ==================== 定时任务API ====================

@router.get("/schedule")
async def get_schedule_status():
    """
    获取定时任务状态
    """
    from core.scheduler.task_scheduler import get_scheduler
    
    scheduler = get_scheduler()
    
    return {
        "success": True,
        "running": scheduler.running,
        "tasks": scheduler.list_tasks()
    }


@router.post("/schedule")
async def update_schedule(request: ScheduleConfig):
    """
    更新定时任务配置
    """
    from core.scheduler.task_scheduler import get_scheduler
    from core.services.pool_scan_service import PoolScanService
    from core.services.notification_service import NotificationService
    from core.stock_pool.manager import StockPoolManager
    import asyncio
    
    scheduler = get_scheduler()
    
    async def scheduled_scan():
        try:
            manager = StockPoolManager()
            
            if request.pool_ids:
                codes = []
                for pool_id in request.pool_ids:
                    pool = manager.get_pool(pool_id)
                    if pool:
                        if pool.pool_type == "hs300":
                            codes.extend(manager._get_hs300_codes())
                        else:
                            codes.extend(pool.codes)
                codes = list(set(codes))
            else:
                codes = manager.get_active_pool_codes()
            
            if codes:
                service = PoolScanService(recent_days=request.recent_days)
                notifier = NotificationService()
                
                result = await service.scan_pool(codes)
                await notifier.send_notification(
                    result.to_dict(),
                    channels=request.notify_channels
                )
                logger.info(f"[ScheduledScan] 扫描完成: {len(result.signals)} 个信号")
        except Exception as e:
            logger.error(f"[ScheduledScan] 扫描失败: {e}")
    
    scheduler.add_scan_task(
        task_id="daily_pool_scan",
        task_func=scheduled_scan,
        cron_expression=request.cron
    )
    
    if request.enabled:
        scheduler.resume_task("daily_pool_scan")
    else:
        scheduler.pause_task("daily_pool_scan")
    
    return {
        "success": True,
        "message": "定时任务已更新",
        "task_status": scheduler.get_task_status("daily_pool_scan")
    }


@router.post("/schedule/{task_id}/run")
async def run_task_now(task_id: str):
    """
    立即执行一次定时任务
    """
    from core.scheduler.task_scheduler import get_scheduler
    
    scheduler = get_scheduler()
    
    success = scheduler.run_task_now(task_id)
    
    if not success:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    return {
        "success": True,
        "message": f"任务 {task_id} 已触发执行"
    }


@router.post("/schedule/{task_id}/pause")
async def pause_task(task_id: str):
    """
    暂停定时任务
    """
    from core.scheduler.task_scheduler import get_scheduler
    
    scheduler = get_scheduler()
    success = scheduler.pause_task(task_id)
    
    if not success:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    return {
        "success": True,
        "message": f"任务 {task_id} 已暂停"
    }


@router.post("/schedule/{task_id}/resume")
async def resume_task(task_id: str):
    """
    恢复定时任务
    """
    from core.scheduler.task_scheduler import get_scheduler
    
    scheduler = get_scheduler()
    success = scheduler.resume_task(task_id)
    
    if not success:
        raise HTTPException(404, f"任务不存在: {task_id}")
    
    return {
        "success": True,
        "message": f"任务 {task_id} 已恢复"
    }


# ==================== 通知配置API ====================

@router.post("/config/email")
async def update_email_config(request: EmailConfigRequest):
    """
    更新邮件配置
    """
    from core.services.notification_service import NotificationService, EmailConfig
    
    config = EmailConfig(
        enabled=request.enabled,
        smtp_server=request.smtp_server,
        smtp_port=request.smtp_port,
        smtp_user=request.smtp_user,
        smtp_password=request.smtp_password,
        use_ssl=request.use_ssl,
        recipients=request.recipients,
        sender_name=request.sender_name
    )
    
    # 保存配置到文件
    config_path = Path("config/notification_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    config_data = {
        "email": {
            "enabled": request.enabled,
            "smtp_server": request.smtp_server,
            "smtp_port": request.smtp_port,
            "smtp_user": request.smtp_user,
            "smtp_password": request.smtp_password,
            "use_ssl": request.use_ssl,
            "recipients": request.recipients,
            "sender_name": request.sender_name
        }
    }
    
    # 读取现有配置并合并
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            existing.update(config_data)
            config_data = existing
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "message": "邮件配置已更新"
    }


@router.post("/config/webhook")
async def update_webhook_config(request: WebhookConfigRequest):
    """
    更新Webhook配置
    """
    from core.services.notification_service import WebhookConfig
    
    config_path = Path("config/notification_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    config_data = {
        "webhook": {
            "enabled": request.enabled,
            "url": request.url,
            "webhook_type": request.webhook_type
        }
    }
    
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            existing.update(config_data)
            config_data = existing
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "message": "Webhook配置已更新"
    }


@router.get("/config")
async def get_notification_config():
    """
    获取通知配置
    """
    config_path = Path("config/notification_config.json")
    
    if not config_path.exists():
        return {
            "success": True,
            "config": {
                "email": {"enabled": False, "recipients": []},
                "webhook": {"enabled": False, "url": ""}
            }
        }
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 隐藏密码
    if "email" in config and "smtp_password" in config["email"]:
        config["email"]["smtp_password"] = "******"
    
    return {
        "success": True,
        "config": config
    }
