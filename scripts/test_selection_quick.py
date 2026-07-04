"""
选股策略快速测试脚本
用于验证选股功能是否正常工作
"""
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_data_fetch():
    """测试数据获取功能"""
    logger.info("="*60)
    logger.info("步骤1: 测试数据获取功能")
    logger.info("="*60)
    
    from core.tools.data_fetcher import fetch_stock_data, get_stock_name
    
    # 测试获取单只股票数据
    test_code = "600519"  # 贵州茅台
    logger.info(f"测试获取 {test_code} 数据...")
    
    try:
        df = fetch_stock_data(test_code, days=100)
        if df is not None and not df.empty:
            logger.info(f"✅ 成功获取 {test_code} 数据: {len(df)} 条记录")
            logger.info(f"   数据列: {list(df.columns)}")
            logger.info(f"   最新日期: {df.iloc[-1]['日期'] if '日期' in df.columns else 'N/A'}")
            logger.info(f"   最新收盘: {df.iloc[-1]['收盘'] if '收盘' in df.columns else 'N/A'}")
            
            # 获取股票名称
            name = get_stock_name(test_code)
            logger.info(f"   股票名称: {name}")
            
            return True
        else:
            logger.error(f"❌ 获取 {test_code} 数据失败: 返回空数据")
            return False
    except Exception as e:
        logger.error(f"❌ 获取 {test_code} 数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_buy_point_detection():
    """测试买点识别功能"""
    logger.info("\n" + "="*60)
    logger.info("步骤2: 测试买点识别功能")
    logger.info("="*60)
    
    from core.selection import BuyPointDetector, SelectionConfig
    from core.tools.data_fetcher import fetch_stock_data
    
    # 测试股票
    test_codes = ["600519", "000001", "600036"]
    
    config = SelectionConfig()
    detector = BuyPointDetector(config)
    
    success_count = 0
    
    for code in test_codes:
        try:
            logger.info(f"\n测试 {code} 买点识别...")
            df = fetch_stock_data(code, days=250)
            
            if df is None or df.empty:
                logger.warning(f"  ⚠️  跳过 {code}: 无法获取数据")
                continue
            
            buy_points = detector.detect_buy_points(code, df)
            
            if buy_points:
                logger.info(f"  ✅ {code}: 检测到 {len(buy_points)} 个买点")
                for bp in buy_points[:2]:  # 只显示前2个
                    logger.info(f"     - {bp.buy_type}: 价格{bp.price:.2f}, 评分{bp.score:.1f}")
                success_count += 1
            else:
                logger.info(f"  ℹ️  {code}: 未检测到买点(正常情况)")
                success_count += 1
                
        except Exception as e:
            logger.error(f"  ❌ {code} 检测失败: {e}")
    
    if success_count > 0:
        logger.info(f"\n✅ 买点识别测试通过: {success_count}/{len(test_codes)} 只股票")
        return True
    else:
        logger.error(f"\n❌ 买点识别测试失败: 所有股票都检测失败")
        return False


def test_selection_strategy():
    """测试选股策略"""
    logger.info("\n" + "="*60)
    logger.info("步骤3: 测试选股策略")
    logger.info("="*60)
    
    from core.selection import StockSelectionStrategy, SelectionConfig
    
    # 测试股票池
    test_pool = ["600519", "000001", "600036", "000333", "600030"]
    
    logger.info(f"测试股票池: {test_pool}")
    
    try:
        # 创建策略
        config = SelectionConfig()
        strategy = StockSelectionStrategy(config)
        
        # 执行选股
        logger.info("开始执行选股...")
        result = strategy.select_stocks_sync(test_pool)
        
        logger.info(f"\n选股结果:")
        logger.info(f"  - 扫描股票: {result.total_candidates} 只")
        logger.info(f"  - 合格股票: {result.qualified_candidates} 只")
        logger.info(f"  - 推荐股票: {len(result.top_candidates)} 只")
        
        if result.top_candidates:
            logger.info(f"\n推荐股票:")
            for idx, candidate in enumerate(result.top_candidates[:3], 1):
                logger.info(f"  {idx}. {candidate.code} {candidate.name}")
                logger.info(f"     评分: {candidate.overall_score:.1f}")
                logger.info(f"     买点: {candidate.best_buy_point.buy_type}")
                logger.info(f"     价格: {candidate.best_buy_point.price:.2f}")
        
        if result.errors:
            logger.warning(f"\n错误信息:")
            for error in result.errors[:3]:
                logger.warning(f"  - {error['code']}: {error['error']}")
        
        logger.info("\n✅ 选股策略测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 选股策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_test():
    """快速测试（只测试核心功能）"""
    logger.info("\n" + "="*80)
    logger.info("博弈交易选股策略 - 快速测试")
    logger.info("="*80 + "\n")
    
    results = []
    
    # 1. 测试数据获取
    results.append(("数据获取", test_data_fetch()))
    
    # 2. 测试买点识别
    results.append(("买点识别", test_buy_point_detection()))
    
    # 3. 测试选股策略
    results.append(("选股策略", test_selection_strategy()))
    
    # 总结
    logger.info("\n" + "="*80)
    logger.info("测试总结")
    logger.info("="*80)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        logger.info("\n🎉 所有测试通过！选股系统工作正常")
        logger.info("\n下一步:")
        logger.info("1. 启动后端服务: python -m uvicorn server.app:app --reload --port 8000")
        logger.info("2. 启动前端服务: cd frontend && npm run dev")
        logger.info("3. 访问系统: http://localhost:5173/selection")
    else:
        logger.error("\n⚠️  部分测试失败，请检查:")
        logger.error("1. 网络连接是否正常")
        logger.error("2. 数据源是否可访问")
        logger.error("3. 依赖库是否正确安装")
    
    logger.info("="*80)


def main():
    """主函数"""
    import os
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    logger.info(f"工作目录: {os.getcwd()}\n")
    
    # 运行快速测试
    quick_test()


if __name__ == "__main__":
    main()
