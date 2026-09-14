"""
博弈交易法智能分析系统 - 快速演示脚本

无需数据库和API密钥即可运行的核心功能演示
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_knowledge_base():
    """演示知识库功能"""
    logger.info("\n" + "=" * 60)
    logger.info("演示1: 博弈理论知识库")
    logger.info("=" * 60)
    
    try:
        # 确保目录存在
        Path("data/chroma").mkdir(parents=True, exist_ok=True)
        
        from core.intelligent_system.agents.knowledge_base import BoyiKnowledgeBase
        
        # 初始化知识库
        logger.info("初始化知识库...")
        kb = BoyiKnowledgeBase(persist_dir="./data/chroma")
        
        logger.info(f"✓ 知识库已加载，包含 {kb.collection.count()} 条核心知识\n")
        
        # 演示查询
        queries = [
            "如何识别一阶段",
            "洗盘的特征是什么",
            "二阶段的牛股结构",
            "出货识别方法"
        ]
        
        for query in queries:
            logger.info(f"🔍 查询: {query}")
            results = kb.query_knowledge(query, n_results=1)
            
            if results:
                result = results[0]
                logger.info(f"📚 找到: {result['metadata']['title']}")
                logger.info(f"📝 内容摘要: {result['content'][:150]}...\n")
        
        logger.info("✅ 知识库演示完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 知识库演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def demo_data_analysis():
    """演示数据分析功能"""
    logger.info("\n" + "=" * 60)
    logger.info("演示2: K线数据分析")
    logger.info("=" * 60)
    
    try:
        # 生成模拟K线数据
        logger.info("生成模拟K线数据...")
        
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        base_price = 10.0
        
        kline_data = []
        for i, date in enumerate(dates):
            # 模拟上涨趋势（模拟一阶段进入二阶段）
            if i < 60:
                # 一阶段：缓慢上涨
                trend = 0.001 * i
                volatility = 0.03
            elif i < 120:
                # 二阶段：快速上涨
                trend = 0.002 * (i - 60) + 0.06
                volatility = 0.04
            else:
                # 继续上涨
                trend = 0.0015 * (i - 120) + 0.18
                volatility = 0.025
            
            noise = np.random.randn() * volatility
            close = base_price * (1 + trend + noise)
            
            high = close * (1 + abs(np.random.randn() * 0.02))
            low = close * (1 - abs(np.random.randn() * 0.02))
            open_price = close * (1 + np.random.randn() * 0.01)
            
            kline_data.append({
                'time': date,
                'stock_code': 'DEMO.SZ',
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': int(1000000 * (1 + np.random.randn() * 0.3))
            })
        
        df = pd.DataFrame(kline_data)
        
        logger.info(f"✓ 生成了 {len(df)} 个交易日的K线数据\n")
        
        # 计算技术指标
        logger.info("计算技术指标:")
        
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        latest = df.iloc[-1]
        first = df.iloc[0]
        
        logger.info(f"  起始价格: {first['close']:.2f} 元")
        logger.info(f"  最新价格: {latest['close']:.2f} 元")
        logger.info(f"  涨幅: {((latest['close'] - first['close']) / first['close'] * 100):.2f}%")
        logger.info(f"  MA5: {latest['ma5']:.2f} 元")
        logger.info(f"  MA10: {latest['ma10']:.2f} 元")
        logger.info(f"  MA20: {latest['ma20']:.2f} 元")
        logger.info(f"  MA60: {latest['ma60']:.2f} 元\n")
        
        # 识别O点
        logger.info("识别O点:")
        o_point_idx = df['low'].idxmin()
        o_point = df.loc[o_point_idx]
        
        logger.info(f"  O点价格: {o_point['low']:.2f} 元")
        logger.info(f"  O点日期: {o_point['time'].strftime('%Y-%m-%d')}")
        logger.info(f"  O点后最低点: {df.loc[o_point_idx:, 'low'].min():.2f} 元")
        
        # 判断O点是否确认
        after_o = df.loc[o_point_idx:, 'low']
        o_confirmed = after_o.min() == o_point['low']
        logger.info(f"  O点确认: {'是 ✓' if o_confirmed else '否 ✗'}\n")
        
        # 趋势分析
        logger.info("趋势分析:")
        df['ma20_slope'] = df['ma20'].diff() / df['ma20'].shift(1)
        avg_slope = df['ma20_slope'].mean()
        
        if avg_slope > 0.005:
            trend = "强势上涨"
        elif avg_slope > 0:
            trend = "上涨"
        else:
            trend = "下跌"
        
        logger.info(f"  趋势判断: {trend}")
        logger.info(f"  平均斜率: {avg_slope:.4f}\n")
        
        # 简单阶段判断
        logger.info("初步阶段判断:")
        
        total_change = (latest['close'] - first['close']) / first['close']
        
        if total_change < 0.3 and avg_slope < 0.01:
            phase = "一阶段（趋势形成初期）"
            reason = "涨幅较小，趋势缓慢"
        elif total_change < 0.8 and avg_slope > 0.005:
            phase = "二阶段（快速上涨）"
            reason = "涨幅适中，趋势强劲"
        elif total_change > 0.8 and avg_slope > 0.01:
            phase = "三阶段（疯狂上涨）"
            reason = "涨幅巨大，趋势猛烈"
        else:
            phase = "需要进一步分析"
            reason = "特征不明确"
        
        logger.info(f"  当前阶段: {phase}")
        logger.info(f"  判断依据: {reason}")
        
        logger.info("\n✅ 数据分析演示完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据分析演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def demo_trading_logic():
    """演示博弈理论核心逻辑"""
    logger.info("\n" + "=" * 60)
    logger.info("演示3: 博弈理论核心逻辑")
    logger.info("=" * 60)
    
    try:
        # 模拟场景分析
        scenarios = [
            {
                "name": "一阶段牛股结构",
                "emotion_ratio": {
                    "distribution_beauty": 7,  # 出货好看程度
                    "washing_ugliness": 9      # 洗盘难看程度
                },
                "washing_duration": 45,  # 洗盘天数
                "volume_shrink": True    # 成交量萎缩
            },
            {
                "name": "二阶段牛股结构",
                "emotion_ratio": {
                    "distribution_beauty": 5,
                    "washing_ugliness": 8
                },
                "washing_duration": 30,
                "volume_shrink": True
            },
            {
                "name": "出货形态",
                "emotion_ratio": {
                    "distribution_beauty": 9,
                    "washing_ugliness": 3
                },
                "washing_duration": 120,
                "volume_shrink": False
            }
        ]
        
        for scenario in scenarios:
            logger.info(f"\n📊 场景: {scenario['name']}")
            logger.info("-" * 60)
            
            # 情绪比例分析
            er = scenario['emotion_ratio']
            logger.info(f"情绪比例关系:")
            logger.info(f"  出货好看程度: {er['distribution_beauty']}/10")
            logger.info(f"  洗盘难看程度: {er['washing_ugliness']}/10")
            
            # 判断逻辑
            if er['washing_ugliness'] > er['distribution_beauty'] + 1:
                logger.info(f"  ✓ 情绪比例关系合格（洗盘难看 > 出货好看）")
            elif er['distribution_beauty'] > er['washing_ugliness'] + 2:
                logger.info(f"  ✗ 情绪比例关系危险（出货好看 > 洗盘难看）")
            else:
                logger.info(f"  ⚠️  情绪比例关系一般")
            
            # 洗盘分析
            logger.info(f"\n洗盘分析:")
            logger.info(f"  洗盘时间: {scenario['washing_duration']} 天")
            logger.info(f"  成交量萎缩: {'是' if scenario['volume_shrink'] else '否'}")
            
            # 综合判断
            logger.info(f"\n综合判断:")
            if scenario['washing_duration'] < 90 and er['washing_ugliness'] > 7:
                logger.info(f"  💡 建议: 可能是洗盘完成，关注买入机会")
            elif scenario['washing_duration'] > 90:
                logger.info(f"  ⚠️  警告: 洗盘时间过长，可能是出货")
            else:
                logger.info(f"  ℹ️  状态: 需要进一步观察")
        
        logger.info("\n✅ 博弈理论逻辑演示完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 博弈理论演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def demo_phase_analysis_workflow():
    """演示完整的阶段分析流程"""
    logger.info("\n" + "=" * 60)
    logger.info("演示4: 完整阶段分析流程")
    logger.info("=" * 60)
    
    try:
        logger.info("模拟Agent分析流程:\n")
        
        # 步骤1: 数据获取
        logger.info("步骤1: 数据获取")
        logger.info("  ✓ 获取180个交易日K线数据")
        logger.info("  ✓ 计算技术指标（MA5/10/20/60）")
        logger.info("  ✓ 分析成交量变化")
        
        # 步骤2: O点识别
        logger.info("\n步骤2: O点识别")
        logger.info("  ✓ 识别最低点: 10.25元")
        logger.info("  ✓ 确认不再创新低")
        logger.info("  ✓ 成交量萎缩确认")
        logger.info("  → O点已确认")
        
        # 步骤3: 趋势分析
        logger.info("\n步骤3: 趋势分析")
        logger.info("  ✓ MA20持续上行")
        logger.info("  ✓ 趋势强度: 中等")
        logger.info("  ✓ 趋势稳定性: 良好")
        logger.info("  → 趋势存在且稳定")
        
        # 步骤4: 形态识别
        logger.info("\n步骤4: 形态识别")
        logger.info("  ✓ 识别到3次洗盘")
        logger.info("  ✓ 洗盘效果评分: 75分")
        logger.info("  ✓ 无明显出货形态")
        logger.info("  ✓ 形成空方锚定")
        logger.info("  → 洗盘充分，牛股结构形成")
        
        # 步骤5: 情绪分析
        logger.info("\n步骤5: 情绪比例关系分析")
        logger.info("  ✓ 出货好看程度: 6/10")
        logger.info("  ✓ 洗盘难看程度: 8/10")
        logger.info("  ✓ 情绪比例关系合格")
        logger.info("  → 散户恐惧，场内筹码少")
        
        # 步骤6: 综合判断
        logger.info("\n步骤6: 综合判断")
        logger.info("  分析依据:")
        logger.info("  1. O点明确，从10.25元起步")
        logger.info("  2. 缓慢上涨约30%，符合一阶段特征")
        logger.info("  3. 多次洗盘，洗盘效果好")
        logger.info("  4. 情绪比例关系合格")
        logger.info("  5. 趋势稳定向上")
        
        logger.info("\n  📊 最终判断:")
        logger.info("     阶段: 一阶段末期（即将进入二阶段）")
        logger.info("     置信度: 82%")
        logger.info("     操作建议: 关注突破信号，准备在洗盘时加仓")
        
        logger.info("\n✅ 完整分析流程演示完成\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ 流程演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主演示函数"""
    logger.info("\n" + "🎯" * 30)
    logger.info("博弈交易法智能分析系统 - 核心功能演示")
    logger.info("🎯" * 30)
    logger.info(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    logger.info("\n本演示无需数据库和API密钥")
    logger.info("展示系统的核心功能和逻辑\n")
    
    # 运行所有演示
    demos = [
        ("知识库功能", demo_knowledge_base),
        ("数据分析功能", demo_data_analysis),
        ("博弈理论逻辑", demo_trading_logic),
        ("完整分析流程", demo_phase_analysis_workflow)
    ]
    
    results = []
    for name, demo_func in demos:
        try:
            result = await demo_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"演示 {name} 出现异常: {e}")
            results.append((name, False))
    
    # 打印总结
    logger.info("\n" + "=" * 60)
    logger.info("演示总结")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"演示结果: {passed}/{total} 成功")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n🎉 所有演示成功！系统核心功能正常！")
        logger.info("\n下一步:")
        logger.info("1. 配置数据库（PostgreSQL + TimescaleDB）")
        logger.info("2. 配置数据源（Tushare Token）")
        logger.info("3. 配置AI（OpenAI API Key）")
        logger.info("4. 运行: python start_intelligent_system.py")
    else:
        logger.warning(f"\n⚠️  {total - passed} 个演示失败")


if __name__ == "__main__":
    asyncio.run(main())
