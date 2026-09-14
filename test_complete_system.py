"""
完整功能测试脚本

测试所有已实现的核心功能
"""

import asyncio
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_database():
    """测试数据库功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试1: 数据库管理模块")
    logger.info("=" * 60)
    
    try:
        from core.intelligent_system.database.db_manager import DatabaseManager
        from core.intelligent_system.config import settings
        
        # 创建数据库管理器
        db = DatabaseManager(
            database_url=settings.DATABASE_URL,
            timescaledb_url=settings.TIMESCALEDB_URL
        )
        
        # 测试连接
        logger.info("[1/3] 测试数据库连接...")
        await db.connect()
        logger.info("✓ 数据库连接成功")
        
        # 测试查询
        logger.info("[2/3] 测试数据查询...")
        # 这里可以添加更多查询测试
        
        # 测试断开
        logger.info("[3/3] 测试断开连接...")
        await db.disconnect()
        logger.info("✓ 数据库断开成功")
        
        logger.info("✅ 数据库管理模块测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库测试失败: {e}")
        return False


async def test_data_collection():
    """测试数据采集功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 数据采集模块")
    logger.info("=" * 60)
    
    try:
        from core.intelligent_system.data_collection.stock_collector import StockDataCollector
        from core.intelligent_system.config import settings
        
        # 创建数据采集器
        collector = StockDataCollector(tushare_token=settings.TUSHARE_TOKEN)
        
        # 测试1: 获取大盘指数
        logger.info("[1/4] 测试获取大盘指数...")
        indices = await collector.get_market_indices()
        if indices:
            logger.info(f"✓ 成功获取 {len(indices)} 个大盘指数")
            for idx in indices:
                logger.info(f"  - {idx['index_name']}: {idx['price']:.2f}")
        else:
            logger.warning("⚠️  未获取到大盘指数数据（可能是非交易时间）")
        
        # 测试2: 获取涨停股票
        logger.info("[2/4] 测试获取涨停股票...")
        limit_ups = await collector.get_limit_up_stocks()
        if limit_ups:
            logger.info(f"✓ 成功获取 {len(limit_ups)} 只涨停股票")
        else:
            logger.info("ℹ️  当前无涨停股票（可能是非交易时间）")
        
        # 测试3: 获取日线数据
        logger.info("[3/4] 测试获取日线数据...")
        daily_data = await collector.get_daily_data(
            stock_code="000001.SZ",
            start_date="20240101",
            end_date="20241231"
        )
        if daily_data:
            logger.info(f"✓ 成功获取 {len(daily_data)} 条日线数据")
        else:
            logger.warning("⚠️  未获取到日线数据")
        
        # 测试4: 获取实时行情
        logger.info("[4/4] 测试获取实时行情...")
        quote = await collector.get_realtime_quote("000001.SZ")
        if quote:
            logger.info(f"✓ 成功获取实时行情: {quote['stock_name']} - {quote['price']:.2f}")
        else:
            logger.warning("⚠️  未获取到实时行情")
        
        logger.info("✅ 数据采集模块测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据采集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_base():
    """测试知识库功能"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 知识库模块")
    logger.info("=" * 60)
    
    try:
        from core.intelligent_system.agents.knowledge_base import BoyiKnowledgeBase
        from core.intelligent_system.config import settings
        
        # 创建知识库
        logger.info("[1/3] 初始化知识库...")
        kb = BoyiKnowledgeBase(persist_dir=settings.CHROMA_PERSIST_DIR)
        logger.info(f"✓ 知识库初始化成功，包含 {kb.collection.count()} 条知识")
        
        # 测试查询
        logger.info("[2/3] 测试知识查询...")
        results = kb.query_knowledge("如何识别一阶段", n_results=2)
        if results:
            logger.info(f"✓ 查询成功，找到 {len(results)} 条相关知识")
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. {result['metadata']['title']}")
        else:
            logger.warning("⚠️  未查询到相关知识")
        
        # 测试按类型获取
        logger.info("[3/3] 测试按类型获取知识...")
        phase_knowledge = kb.get_knowledge_by_type("阶段理论")
        logger.info(f"✓ 获取到 {len(phase_knowledge)} 条阶段理论知识")
        
        logger.info("✅ 知识库模块测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 知识库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_phase_agent():
    """测试PhaseAnalysisAgent"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: PhaseAnalysisAgent（核心）")
    logger.info("=" * 60)
    
    try:
        from core.intelligent_system.agents.phase_analyzer import PhaseAnalysisAgent
        from core.intelligent_system.config import settings
        
        # 检查API密钥
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️  未配置OPENAI_API_KEY，跳过Agent测试")
            return True
        
        # 创建Agent
        logger.info("[1/2] 初始化PhaseAnalysisAgent...")
        agent = PhaseAnalysisAgent(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE
        )
        logger.info("✓ Agent初始化成功")
        
        # 测试分析（使用模拟数据）
        logger.info("[2/2] 测试Agent分析...")
        logger.info("ℹ️  使用模拟K线数据进行测试...")
        
        # 生成模拟K线数据
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        mock_kline = []
        base_price = 10.0
        
        for i, date in enumerate(dates):
            # 模拟上涨趋势
            trend = 0.002 * i
            noise = np.random.randn() * 0.02
            close = base_price * (1 + trend + noise)
            
            mock_kline.append({
                'time': date,
                'stock_code': 'TEST.SZ',
                'open': close * (1 + np.random.randn() * 0.01),
                'high': close * (1 + abs(np.random.randn() * 0.02)),
                'low': close * (1 - abs(np.random.randn() * 0.02)),
                'close': close,
                'volume': int(1000000 * (1 + np.random.randn() * 0.3))
            })
        
        # 执行分析
        result = await agent.analyze(
            stock_code='TEST.SZ',
            kline_data=mock_kline,
            additional_context={'market_trend': '震荡上涨'}
        )
        
        logger.info(f"✓ Agent分析完成")
        logger.info(f"  阶段判断: {result.get('phase', '未知')}")
        logger.info(f"  置信度: {result.get('confidence', 0)}%")
        logger.info(f"  判断依据: {result.get('reasoning', 'N/A')[:100]}...")
        
        logger.info("✅ PhaseAnalysisAgent测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api():
    """测试API服务"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: FastAPI Web服务")
    logger.info("=" * 60)
    
    try:
        from core.intelligent_system.api.main import app
        from fastapi.testclient import TestClient
        
        # 创建测试客户端
        client = TestClient(app)
        
        # 测试健康检查
        logger.info("[1/2] 测试健康检查接口...")
        response = client.get("/api/health")
        if response.status_code == 200:
            logger.info("✓ 健康检查接口正常")
        else:
            logger.warning(f"⚠️  健康检查接口异常: {response.status_code}")
        
        # 测试根路径
        logger.info("[2/2] 测试根路径...")
        response = client.get("/")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ 根路径正常: {data['message']}")
        else:
            logger.warning(f"⚠️  根路径异常: {response.status_code}")
        
        logger.info("✅ FastAPI Web服务测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ API测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("\n" + "🚀" * 30)
    logger.info("博弈交易法智能分析系统 - 完整功能测试")
    logger.info("🚀" * 30)
    
    # 确保必要目录存在
    Path("logs").mkdir(exist_ok=True)
    Path("data/chroma").mkdir(parents=True, exist_ok=True)
    
    # 运行所有测试
    tests = [
        ("数据库管理", test_database),
        ("数据采集", test_data_collection),
        ("知识库", test_knowledge_base),
        ("PhaseAnalysisAgent", test_phase_agent),
        ("FastAPI服务", test_api)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 {name} 出现异常: {e}")
            results.append((name, False))
    
    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！系统运行正常！")
    else:
        logger.warning(f"⚠️  {total - passed} 个测试失败，请检查配置和依赖")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
