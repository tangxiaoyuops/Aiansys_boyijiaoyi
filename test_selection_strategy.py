"""
博弈交易选股策略测试脚本
验证选股策略的功能和效果
"""
import sys
import os
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_buy_point_detector():
    """测试买点识别器"""
    logger.info("="*60)
    logger.info("测试买点识别器")
    logger.info("="*60)
    
    from core.selection.buy_point_detector import BuyPointDetector
    from core.selection.selection_config import SelectionConfig
    from core.tools.data_fetcher import fetch_stock_data
    
    # 创建配置和检测器
    config = SelectionConfig()
    detector = BuyPointDetector(config)
    
    # 测试股票
    test_codes = ["600519", "000001", "600036"]  # 茅台、平安、招行
    
    for code in test_codes:
        logger.info(f"\n测试股票: {code}")
        
        try:
            # 获取数据
            df = fetch_stock_data(code, days=250)
            if df is None or df.empty:
                logger.warning(f"无法获取 {code} 数据")
                continue
            
            logger.info(f"数据获取成功: {len(df)}条记录")
            
            # 检测买点
            buy_points = detector.detect_buy_points(code, df)
            
            if buy_points:
                logger.info(f"检测到 {len(buy_points)} 个买点:")
                for bp in buy_points[:3]:  # 只显示前3个
                    logger.info(f"  - {bp.buy_type}: 价格{bp.price:.2f}, 评分{bp.score:.1f}, 阶段{bp.stage}")
                    logger.info(f"    理由: {bp.reasoning}")
            else:
                logger.info(f"未检测到买点")
        
        except Exception as e:
            logger.error(f"测试 {code} 失败: {e}")
            import traceback
            traceback.print_exc()


def test_stock_selection_strategy():
    """测试选股策略"""
    logger.info("\n" + "="*60)
    logger.info("测试选股策略")
    logger.info("="*60)
    
    from core.selection.stock_selection_strategy import StockSelectionStrategy
    from core.selection.selection_config import SelectionConfig
    
    # 创建配置(保守型)
    config = SelectionConfig.conservative()
    config.max_stocks = 3  # 测试时只选3只
    
    logger.info(f"使用配置: 保守型, 最大持仓{config.max_stocks}只")
    
    # 创建选股策略
    strategy = StockSelectionStrategy(config)
    
    # 测试股票池
    test_pool = ["600519", "000001", "600036", "000333", "600030"]
    
    logger.info(f"测试股票池: {test_pool}")
    
    try:
        # 执行选股(同步版本)
        result = strategy.select_stocks_sync(test_pool)
        
        logger.info(f"\n选股结果:")
        logger.info(f"  - 扫描时间: {result.scan_time}")
        logger.info(f"  - 候选股票: {result.total_candidates}只")
        logger.info(f"  - 合格股票: {result.qualified_candidates}只")
        logger.info(f"  - 推荐股票: {len(result.top_candidates)}只")
        
        if result.top_candidates:
            logger.info(f"\n推荐股票:")
            for idx, candidate in enumerate(result.top_candidates, 1):
                logger.info(f"  {idx}. {candidate.code} {candidate.name}")
                logger.info(f"     - 评分: {candidate.overall_score:.1f}")
                logger.info(f"     - 阶段: {candidate.stage_name}")
                logger.info(f"     - 买点: {candidate.best_buy_point.buy_type}")
                logger.info(f"     - 价格: {candidate.best_buy_point.price:.2f}")
                logger.info(f"     - 建议仓位: {candidate.suggested_position_pct*100:.1f}%")
                logger.info(f"     - 建议股数: {candidate.suggested_shares}股")
        
        if result.errors:
            logger.warning(f"\n错误信息: {len(result.errors)}个")
            for error in result.errors[:3]:
                logger.warning(f"  - {error['code']}: {error['error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"选股策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_selection_reporter():
    """测试报告生成器"""
    logger.info("\n" + "="*60)
    logger.info("测试报告生成器")
    logger.info("="*60)
    
    from core.selection.selection_reporter import SelectionReporter
    from core.selection.stock_selection_strategy import StockSelectionStrategy
    from core.selection.selection_config import SelectionConfig
    
    # 执行选股
    config = SelectionConfig.conservative()
    config.max_stocks = 5
    strategy = StockSelectionStrategy(config)
    
    test_pool = ["600519", "000001", "600036", "000333", "600030", "000651"]
    result = strategy.select_stocks_sync(test_pool)
    
    if result is None:
        logger.warning("选股失败,无法生成报告")
        return
    
    # 创建报告生成器
    reporter = SelectionReporter()
    
    # 生成Markdown报告
    logger.info("生成Markdown报告...")
    md_report = reporter.generate_selection_report(result, "markdown")
    
    # 保存报告
    report_path = "output/selection_report.md"
    reporter.save_report(md_report, report_path)
    
    # 显示报告摘要
    logger.info("\n报告摘要:")
    lines = md_report.split('\n')
    for line in lines[:20]:  # 只显示前20行
        logger.info(line)
    
    logger.info(f"\n完整报告已保存到: {report_path}")


def test_selection_backtester():
    """测试选股回测框架"""
    logger.info("\n" + "="*60)
    logger.info("测试选股回测框架")
    logger.info("="*60)
    
    from core.selection.selection_backtester import SelectionBacktester
    from core.selection.selection_config import SelectionConfig
    
    # 创建配置
    config = SelectionConfig.conservative()
    config.initial_capital = 500000  # 测试资金50万
    
    logger.info(f"回测配置: 初始资金{config.initial_capital}元, 最大持仓{config.max_stocks}只")
    
    # 创建回测器
    backtester = SelectionBacktester(config)
    
    # 测试股票池
    test_pool = ["600519", "000001", "600036", "000333", "600030"]
    
    # 回测区间(最近3个月)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - pd.Timedelta(days=90)).strftime("%Y-%m-%d") if 'pd' in globals() else "2025-01-01"
    
    # 使用固定日期测试
    start_date = "2025-01-01"
    end_date = "2025-03-31"
    
    logger.info(f"回测区间: {start_date} 至 {end_date}")
    logger.info(f"股票池: {test_pool}")
    
    try:
        # 运行回测
        logger.info("开始回测...")
        result = backtester.run_backtest(
            codes=test_pool,
            start_date=start_date,
            end_date=end_date,
            rebalance_freq="weekly"
        )
        
        # 显示结果
        perf = result.performance
        logger.info(f"\n回测结果:")
        logger.info(f"  - 总收益率: {perf.total_return:.2f}%")
        logger.info(f"  - 年化收益率: {perf.annual_return:.2f}%")
        logger.info(f"  - 最大回撤: {perf.max_drawdown:.2f}%")
        logger.info(f"  - 夏普比率: {perf.sharpe_ratio:.2f}")
        logger.info(f"  - 胜率: {perf.win_rate:.2f}%")
        logger.info(f"  - 交易次数: {perf.total_trades}")
        
        if result.trades:
            logger.info(f"\n交易明细:")
            for trade in result.trades[:5]:  # 只显示前5笔
                logger.info(f"  - {trade.code} {trade.name}")
                logger.info(f"    买入: {trade.buy_date} @ {trade.buy_price:.2f}")
                logger.info(f"    卖出: {trade.sell_date} @ {trade.sell_price:.2f}")
                logger.info(f"    盈亏: {trade.pnl:.2f}元 ({trade.pnl_pct:.2f}%)")
        
        # 生成回测报告
        from core.selection.selection_reporter import SelectionReporter
        reporter = SelectionReporter()
        
        backtest_report = reporter.generate_backtest_report(result, "markdown")
        report_path = "output/backtest_report.md"
        reporter.save_report(backtest_report, report_path)
        
        logger.info(f"\n回测报告已保存到: {report_path}")
        
    except Exception as e:
        logger.error(f"回测测试失败: {e}")
        import traceback
        traceback.print_exc()


def run_all_tests():
    """运行所有测试"""
    logger.info("\n" + "="*80)
    logger.info("博弈交易选股策略完整测试")
    logger.info("="*80)
    
    # 1. 测试买点识别器
    test_buy_point_detector()
    
    # 2. 测试选股策略
    selection_result = test_stock_selection_strategy()
    
    # 3. 测试报告生成器
    test_selection_reporter()
    
    # 4. 测试回测框架
    # test_selection_backtester()  # 回测耗时较长,可选测试
    
    logger.info("\n" + "="*80)
    logger.info("测试完成!")
    logger.info("="*80)


if __name__ == "__main__":
    # 导入pandas
    import pandas as pd
    
    # 创建输出目录
    os.makedirs("output", exist_ok=True)
    
    # 运行测试
    run_all_tests()