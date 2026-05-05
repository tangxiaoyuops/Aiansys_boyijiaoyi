"""
定时任务调度模块
使用 APScheduler 实现定时扫描
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

# 全局调度器实例
_scheduler_instance: Optional["TaskScheduler"] = None


def get_scheduler() -> "TaskScheduler":
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler()
    return _scheduler_instance


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._running = False
    
    def add_scan_task(
        self,
        task_id: str,
        task_func: Callable,
        cron_expression: str = "30 15 * * 1-5",
        **kwargs
    ) -> None:
        """
        添加定时扫描任务
        
        Args:
            task_id: 任务ID
            task_func: 执行函数
            cron_expression: cron表达式，默认周一到周五 15:30
                            格式: "分 时 日 月 周"
                            例如: "30 15 * * 1-5" 表示周一到周五15:30
        """
        # 解析 cron 表达式
        parts = cron_expression.split()
        if len(parts) < 5:
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        minute, hour, day, month, day_of_week = parts
        
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day if day != "*" else None,
            month=month if month != "*" else None,
            day_of_week=day_of_week if day_of_week != "*" else None
        )
        
        self.scheduler.add_job(
            task_func,
            trigger=trigger,
            id=task_id,
            kwargs=kwargs,
            replace_existing=True
        )
        
        self.tasks[task_id] = {
            "func_name": task_func.__name__ if hasattr(task_func, "__name__") else str(task_func),
            "cron": cron_expression,
            "enabled": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_run": None,
            "next_run": None
        }
        
        logger.info(f"[TaskScheduler] 添加任务: {task_id}, cron: {cron_expression}")
    
    def add_interval_task(
        self,
        task_id: str,
        task_func: Callable,
        seconds: int = 60,
        **kwargs
    ) -> None:
        """
        添加间隔执行任务
        
        Args:
            task_id: 任务ID
            task_func: 执行函数
            seconds: 间隔秒数
        """
        from apscheduler.triggers.interval import IntervalTrigger
        
        trigger = IntervalTrigger(seconds=seconds)
        
        self.scheduler.add_job(
            task_func,
            trigger=trigger,
            id=task_id,
            kwargs=kwargs,
            replace_existing=True
        )
        
        self.tasks[task_id] = {
            "func_name": task_func.__name__ if hasattr(task_func, "__name__") else str(task_func),
            "type": "interval",
            "seconds": seconds,
            "enabled": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_run": None,
            "next_run": None
        }
        
        logger.info(f"[TaskScheduler] 添加间隔任务: {task_id}, 间隔: {seconds}秒")
    
    def start(self) -> None:
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("[TaskScheduler] 调度器已启动")
    
    def stop(self) -> None:
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("[TaskScheduler] 调度器已停止")
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(task_id)
            if task_id in self.tasks:
                self.tasks[task_id]["enabled"] = False
            logger.info(f"[TaskScheduler] 暂停任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"[TaskScheduler] 暂停任务失败: {task_id}, {e}")
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(task_id)
            if task_id in self.tasks:
                self.tasks[task_id]["enabled"] = True
            logger.info(f"[TaskScheduler] 恢复任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"[TaskScheduler] 恢复任务失败: {task_id}, {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        try:
            self.scheduler.remove_job(task_id)
            if task_id in self.tasks:
                del self.tasks[task_id]
            logger.info(f"[TaskScheduler] 移除任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"[TaskScheduler] 移除任务失败: {task_id}, {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        job = self.scheduler.get_job(task_id)
        task_info = self.tasks[task_id].copy()
        
        if job:
            task_info["next_run"] = job.next_run_time.isoformat() if job.next_run_time else None
            task_info["trigger"] = str(job.trigger)
        
        return task_info
    
    def list_tasks(self) -> Dict[str, Dict[str, Any]]:
        """列出所有任务"""
        result = {}
        for task_id in self.tasks:
            result[task_id] = self.get_task_status(task_id)
        return result
    
    @property
    def running(self) -> bool:
        """调度器是否运行中"""
        return self._running
    
    def run_task_now(self, task_id: str) -> bool:
        """立即执行一次任务"""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                job.func(*job.args, **job.kwargs)
                return True
            return False
        except Exception as e:
            logger.error(f"[TaskScheduler] 立即执行任务失败: {task_id}, {e}")
            return False
