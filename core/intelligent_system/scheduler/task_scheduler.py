"""
定时任务调度器

管理所有定时任务的调度和执行
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, time
import asyncio
from typing import Dict, List, Callable
import logging

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    任务调度器
    
    管理所有定时任务的调度和执行
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, Callable] = {}
        self.task_status: Dict[str, str] = {}
        
    def setup_tasks(self):
        """配置所有定时任务"""
        
        logger.info("开始配置定时任务...")
        
        # ========== 盘前任务（09:00-09:30）==========
        
        # 09:00 - 系统启动检查
        self.scheduler.add_job(
            self.pre_market_check,
            CronTrigger(hour=9, minute=0),
            id='pre_market_check',
            name='盘前系统检查',
            replace_existing=True
        )
        
        # ========== 盘后任务（15:00-20:00）==========
        
        # 15:05 - 日线数据采集
        self.scheduler.add_job(
            self.collect_daily_data,
            CronTrigger(hour=15, minute=5),
            id='collect_daily_data',
            name='日线数据采集',
            replace_existing=True
        )
        
        # 15:30 - Agent全量分析
        self.scheduler.add_job(
            self.agent_daily_analysis,
            CronTrigger(hour=15, minute=30),
            id='agent_daily_analysis',
            name='Agent全量分析',
            replace_existing=True
        )
        
        # 16:00 - 生成日度报告
        self.scheduler.add_job(
            self.generate_daily_report,
            CronTrigger(hour=16, minute=0),
            id='generate_daily_report',
            name='生成日度报告',
            replace_existing=True
        )
        
        # ========== 夜间任务（23:00-08:00）==========
        
        # 23:00 - 全市场数据同步
        self.scheduler.add_job(
            self.sync_all_market_data,
            CronTrigger(hour=23, minute=0),
            id='sync_all_market_data',
            name='全市场数据同步',
            replace_existing=True
        )
        
        # 02:00 - Agent知识库更新
        self.scheduler.add_job(
            self.update_knowledge_base,
            CronTrigger(hour=2, minute=0),
            id='update_knowledge_base',
            name='Agent知识库更新',
            replace_existing=True
        )
        
        # 06:00 - 生成早报
        self.scheduler.add_job(
            self.generate_morning_report,
            CronTrigger(hour=6, minute=0),
            id='generate_morning_report',
            name='生成早报',
            replace_existing=True
        )
        
        logger.info(f"定时任务配置完成，共 {len(self.scheduler.get_jobs())} 个任务")
    
    # ========== 盘前任务实现 ==========
    
    async def pre_market_check(self):
        """盘前系统检查"""
        logger.info("=" * 60)
        logger.info("开始盘前系统检查...")
        logger.info("=" * 60)
        
        try:
            # 检查数据源
            logger.info("检查数据源...")
            # TODO: 实现数据源检查
            
            # 检查数据库连接
            logger.info("检查数据库连接...")
            from core.intelligent_system.database.db_manager import get_db_manager
            db = await get_db_manager()
            
            logger.info("✓ 盘前系统检查通过")
            
        except Exception as e:
            logger.error(f"✗ 盘前系统检查失败: {e}")
    
    # ========== 盘后任务实现 ==========
    
    async def collect_daily_data(self):
        """日线数据采集"""
        logger.info("=" * 60)
        logger.info("开始日线数据采集...")
        logger.info("=" * 60)
        
        try:
            from core.intelligent_system.data_collection.stock_collector import get_collector
            from core.intelligent_system.database.db_manager import get_db_manager
            
            # 获取数据采集器
            collector = get_collector()
            
            # 获取数据库管理器
            db = await get_db_manager()
            
            # 获取股票列表
            logger.info("获取股票列表...")
            stock_list = await collector.get_stock_list()
            logger.info(f"共 {len(stock_list)} 只股票")
            
            # 采集最近7天的数据
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
            
            logger.info(f"采集时间范围: {start_date} - {end_date}")
            
            success_count = 0
            failed_count = 0
            
            # 批量采集（每批50只）
            batch_size = 50
            for i in range(0, len(stock_list), batch_size):
                batch = stock_list[i:i + batch_size]
                
                tasks = []
                for stock in batch:
                    task = collector.get_daily_data(
                        stock['stock_code'],
                        start_date,
                        end_date
                    )
                    tasks.append(task)
                
                # 并发采集
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 保存数据
                for result in results:
                    if isinstance(result, Exception):
                        failed_count += 1
                    elif result and len(result) > 0:
                        try:
                            await db.save_stock_daily_data(result)
                            success_count += 1
                        except Exception as e:
                            logger.error(f"保存数据失败: {e}")
                            failed_count += 1
                
                logger.info(
                    f"进度: {i + len(batch)}/{len(stock_list)}, "
                    f"成功: {success_count}, 失败: {failed_count}"
                )
                
                # 避免请求过快
                await asyncio.sleep(0.5)
            
            logger.info(f"✓ 日线数据采集完成: 成功 {success_count}, 失败 {failed_count}")
            
        except Exception as e:
            logger.error(f"✗ 日线数据采集失败: {e}")
    
    async def agent_daily_analysis(self):
        """
        Agent全量分析
        
        每日盘后对自选股进行Agent分析
        """
        logger.info("=" * 60)
        logger.info("开始Agent全量分析...")
        logger.info("=" * 60)
        
        try:
            from core.intelligent_system.agents.phase_analyzer import get_phase_agent
            from core.intelligent_system.database.db_manager import get_db_manager
            
            # 获取Agent
            agent = await get_phase_agent()
            
            # 获取数据库管理器
            db = await get_db_manager()
            
            # TODO: 获取自选股列表
            # 这里先用测试股票
            test_stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
            
            for stock_code in test_stocks:
                try:
                    logger.info(f"分析股票 {stock_code}...")
                    
                    # 获取K线数据
                    kline_data = await db.get_stock_daily_data(
                        stock_code=stock_code,
                        start_date=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d"),
                        limit=180
                    )
                    
                    if len(kline_data) < 60:
                        logger.warning(f"数据不足，跳过 {stock_code}")
                        continue
                    
                    # Agent分析
                    result = await agent.analyze(
                        stock_code=stock_code,
                        kline_data=kline_data
                    )
                    
                    logger.info(f"✓ {stock_code}: {result.get('phase', '未知')} (置信度: {result.get('confidence', 0)}%)")
                    
                except Exception as e:
                    logger.error(f"✗ 分析失败 {stock_code}: {e}")
            
            logger.info("✓ Agent全量分析完成")
            
        except Exception as e:
            logger.error(f"✗ Agent全量分析失败: {e}")
    
    async def generate_daily_report(self):
        """生成日度报告"""
        logger.info("=" * 60)
        logger.info("生成日度报告...")
        logger.info("=" * 60)
        
        try:
            # TODO: 实现报告生成逻辑
            
            logger.info("✓ 日度报告生成完成")
            
        except Exception as e:
            logger.error(f"✗ 日度报告生成失败: {e}")
    
    # ========== 夜间任务实现 ==========
    
    async def sync_all_market_data(self):
        """全市场数据同步"""
        logger.info("=" * 60)
        logger.info("全市场数据同步...")
        logger.info("=" * 60)
        
        try:
            # TODO: 实现全市场数据同步
            
            logger.info("✓ 全市场数据同步完成")
            
        except Exception as e:
            logger.error(f"✗ 全市场数据同步失败: {e}")
    
    async def update_knowledge_base(self):
        """Agent知识库更新"""
        logger.info("=" * 60)
        logger.info("Agent知识库更新...")
        logger.info("=" * 60)
        
        try:
            # TODO: 实现知识库更新逻辑
            
            logger.info("✓ Agent知识库更新完成")
            
        except Exception as e:
            logger.error(f"✗ Agent知识库更新失败: {e}")
    
    async def generate_morning_report(self):
        """生成早报"""
        logger.info("=" * 60)
        logger.info("生成早报...")
        logger.info("=" * 60)
        
        try:
            # TODO: 实现早报生成逻辑
            
            logger.info("✓ 早报生成完成")
            
        except Exception as e:
            logger.error(f"✗ 早报生成失败: {e}")
    
    # ========== 调度器控制 ==========
    
    def start(self):
        """启动调度器"""
        self.setup_tasks()
        self.scheduler.start()
        logger.info("🚀 任务调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("⏹️ 任务调度器已停止")
    
    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()


# 创建全局调度器实例
task_scheduler = TaskScheduler()


# 需要导入timedelta
from datetime import timedelta
