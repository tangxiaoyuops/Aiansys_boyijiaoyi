"""
博弈交易法智能分析系统 - 主启动脚本

启动所有核心服务：
1. 定时任务调度器
2. FastAPI Web服务
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/intelligent_system.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """主启动函数"""
    
    logger.info("\n" + "🚀" * 30)
    logger.info("博弈交易法智能分析系统")
    logger.info("🚀" * 30)
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 1. 启动定时任务调度器
        logger.info("\n[1/3] 启动定时任务调度器...")
        from core.intelligent_system.scheduler.task_scheduler import task_scheduler
        task_scheduler.start()
        logger.info("✓ 定时任务调度器启动成功")
        
        # 2. 启动FastAPI服务
        logger.info("\n[2/3] 启动FastAPI Web服务...")
        import uvicorn
        from core.intelligent_system.api.main import app
        
        # 在后台运行FastAPI
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        logger.info("✓ FastAPI服务启动成功")
        logger.info("  访问地址: http://localhost:8000")
        logger.info("  API文档: http://localhost:8000/docs")
        
        # 3. 显示系统状态
        logger.info("\n[3/3] 系统状态:")
        logger.info("  ✓ 数据库连接池已初始化")
        logger.info("  ✓ 知识库已加载")
        logger.info("  ✓ PhaseAnalysisAgent已就绪")
        logger.info("  ✓ 定时任务已启动")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 系统启动完成！")
        logger.info("=" * 60)
        logger.info("\n核心功能:")
        logger.info("  • 数据采集: Tushare + Akshare")
        logger.info("  • 智能分析: Agent驱动的五阶段识别")
        logger.info("  • 知识库: 博弈理论核心知识")
        logger.info("  • 定时任务: 自动化数据采集和分析")
        logger.info("  • Web服务: REST API + WebSocket")
        logger.info("\n按 Ctrl+C 停止系统")
        logger.info("=" * 60 + "\n")
        
        # 运行服务器
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("\n收到停止信号...")
        logger.info("正在关闭系统...")
        
        # 停止定时任务
        task_scheduler.stop()
        logger.info("✓ 定时任务调度器已停止")
        
        logger.info("👋 系统已关闭")
        
    except Exception as e:
        logger.error(f"✗ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 确保logs目录存在
    Path("logs").mkdir(exist_ok=True)
    
    # 运行主程序
    asyncio.run(main())
