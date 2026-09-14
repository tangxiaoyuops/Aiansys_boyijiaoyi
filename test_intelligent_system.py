"""
测试脚本 - 验证基础功能

测试内容：
1. 数据采集功能
2. 数据库连接
3. 数据保存
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.intelligent_system.data_collection.stock_collector import StockDataCollector
from core.intelligent_system.database.db_manager import DatabaseManager
from core.intelligent_system.config import settings

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_data_collection():
    """测试数据采集功能"""
    logger.info("=" * 60)
    logger.info("测试1: 数据采集功能")
    logger.info("=" * 60)
    
    # 创建数据采集器
    collector = StockDataCollector(tushare_token=settings.TUSHARE_TOKEN)
    
    # 测试1: 获取大盘指数
    logger.info("\n[测试] 获取大盘指数...")
    indices = await collector.get_market_indices()
    if indices:
        logger.info(f"✓ 成功获取 {len(indices)} 个大盘指数")
        for idx in indices:
            logger.info(f"  - {idx['index_name']}: {idx['price']:.2f} ({idx['change_percent']:+.2f}%)")
    else:
        logger.warning("✗ 获取大盘指数失败")
    
    # 测试2: 获取涨停股票
    logger.info("\n[测试] 获取涨停股票...")
    limit_ups = await collector.get_limit_up_stocks()
    if limit_ups:
        logger.info(f"✓ 成功获取 {len(limit_ups)} 只涨停股票")
        for i, stock in enumerate(limit_ups[:5], 1):
            logger.info(f"  {i}. {stock['stock_code']} {stock['stock_name']}: {stock['change_percent']:.2f}%")
    else:
        logger.warning("✗ 获取涨停股票失败（可能是非交易时间）")
    
    # 测试3: 获取单只股票日线数据
    logger.info("\n[测试] 获取日线数据 (000001.SZ)...")
    daily_data = await collector.get_daily_data(
        stock_code="000001.SZ",
        start_date="20240101",
        end_date="20241231"
    )
    
    if daily_data:
        logger.info(f"✓ 成功获取 {len(daily_data)} 条日线数据")
        latest = daily_data[0]
        logger.info(f"  最新数据: {latest['time'].strftime('%Y-%m-%d')} 收盘价: {latest['close']:.2f}")
    else:
        logger.warning("✗ 获取日线数据失败")
    
    return collector


async def test_database():
    """测试数据库功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 数据库功能")
    logger.info("=" * 60)
    
    # 创建数据库管理器
    db = DatabaseManager(
        database_url=settings.DATABASE_URL,
        timescaledb_url=settings.TIMESCALEDB_URL
    )
    
    try:
        # 测试连接
        logger.info("\n[测试] 数据库连接...")
        await db.connect()
        logger.info("✓ 数据库连接成功")
        
        # 测试保存日线数据
        if daily_data:
            logger.info("\n[测试] 保存日线数据...")
            await db.save_stock_daily_data(daily_data[:10])  # 只保存10条测试
            logger.info("✓ 日线数据保存成功")
        
        # 测试查询
        logger.info("\n[测试] 查询数据...")
            data = await db.get_stock_daily_data(
                stock_code="000001.SZ",
                start_date="2024-01-01",
                end_date="2024-12-31",
                limit=10
            )
            logger.info(f"✓ 查询到 {len(data)} 条数据")
        
    except Exception as e:
        logger.error(f"✗ 数据库测试失败: {e}")
    finally:
        await db.disconnect()
        logger.info("\n✓ 数据库连接已关闭")


async def main():
    """主测试函数"""
    logger.info("\n" + "🚀" * 30)
    logger.info("博弈交易法智能分析系统 - 基础功能测试")
    logger.info("🚀" * 30 + "\n")
    
    # 测试数据采集
    collector = await test_data_collection()
    
    # 测试数据库
    await test_database()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 测试完成！")
    logger.info("=" * 60)
    logger.info("\n下一步:")
    logger.info("1. 实现PhaseAnalysisAgent（五阶段识别）")
    logger.info("2. 实现知识库基础（博弈理论知识）")
    logger.info("3. 实现定时任务调度器")


if __name__ == "__main__":
    asyncio.run(main())
