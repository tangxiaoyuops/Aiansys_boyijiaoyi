"""
博弈交易选股策略快速使用示例
演示如何使用选股系统进行股票筛选
"""
import logging
from datetime import datetime
from core.selection import (
    StockSelectionStrategy,
    SelectionConfig,
    SelectionReporter
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_selection():
    """基础选股示例"""
    print("\n" + "="*60)
    print("示例1: 基础选股")
    print("="*60 + "\n")
    
    # 1. 创建配置(标准配置)
    config = SelectionConfig()
    print(f"配置: 初始资金{config.initial_capital}元, 最大持仓{config.max_stocks}只")
    
    # 2. 创建选股策略
    strategy = StockSelectionStrategy(config)
    
    # 3. 定义股票池
    stock_pool = [
        "600519",  # 贵州茅台
        "000001",  # 平安银行
        "600036",  # 招商银行
        "000333",  # 美的集团
        "600030",  # 中信证券
        "000651",  # 格力电器
        "601318",  # 中国平安
        "600000",  # 浦发银行
    ]
    
    print(f"股票池: {len(stock_pool)}只股票\n")
    
    # 4. 执行选股
    print("开始选股...")
    result = strategy.select_stocks_sync(stock_pool)
    
    # 5. 显示结果
    print(f"\n选股完成!")
    print(f"  - 扫描股票: {result.total_candidates}只")
    print(f"  - 合格股票: {result.qualified_candidates}只")
    print(f"  - 推荐股票: {len(result.top_candidates)}只\n")
    
    if result.top_candidates:
        print("推荐股票列表:")
        print("-" * 80)
        for idx, candidate in enumerate(result.top_candidates, 1):
            print(f"{idx}. {candidate.code} {candidate.name}")
            print(f"   评分: {candidate.overall_score:.1f} | 阶段: {candidate.stage_name}")
            print(f"   买点: {candidate.best_buy_point.buy_type} | 价格: {candidate.best_buy_point.price:.2f}")
            print(f"   建议仓位: {candidate.suggested_position_pct*100:.1f}% | 股数: {candidate.suggested_shares}")
            print(f"   理由: {candidate.best_buy_point.reasoning}")
            print("-" * 80)
    
    return result


def example_conservative_selection():
    """保守型选股示例"""
    print("\n" + "="*60)
    print("示例2: 保守型选股")
    print("="*60 + "\n")
    
    # 使用保守型配置
    config = SelectionConfig.conservative()
    print("使用保守型配置:")
    print(f"  - 最大持仓: {config.max_stocks}只")
    print(f"  - 单只仓位上限: {config.max_position_per_stock*100}%")
    print(f"  - 优先阶段: {config.preferred_stages}")
    print(f"  - 止损比例: {config.stop_loss_ratio*100}%")
    
    strategy = StockSelectionStrategy(config)
    
    # 使用沪深300股票池
    print("\n获取沪深300成分股...")
    try:
        from core.stock_pool.manager import StockPoolManager
        pool_manager = StockPoolManager()
        stock_pool = pool_manager._get_hs300_codes()[:20]  # 只测试前20只
        print(f"测试股票: {len(stock_pool)}只\n")
    except:
        print("无法获取沪深300,使用默认股票池\n")
        stock_pool = ["600519", "000001", "600036"]
    
    # 执行选股
    result = strategy.select_stocks_sync(stock_pool)
    
    # 生成报告
    reporter = SelectionReporter()
    report = reporter.generate_selection_report(result, "markdown")
    
    # 保存报告
    reporter.save_report(report, "output/conservative_selection_report.md")
    print("报告已保存到: output/conservative_selection_report.md")
    
    return result


def example_custom_config():
    """自定义配置选股示例"""
    print("\n" + "="*60)
    print("示例3: 自定义配置选股")
    print("="*60 + "\n")
    
    # 创建自定义配置
    config = SelectionConfig(
        initial_capital=500000,  # 50万资金
        max_stocks=8,  # 最多8只股票
        max_position_per_stock=0.15,  # 单只不超过15%
        
        # 恐慌点参数
        panic_drop_threshold=-3.5,  # 跌幅至少3.5%
        panic_vol_ratio=1.8,  # 放量至少1.8倍
        
        # 阶段过滤
        preferred_stages=[1, 2],  # 只选择一二阶段
        allowed_stages=[1, 2, 5],  # 允许1、2、5阶段
        
        # 风险控制
        stop_loss_ratio=0.06,  # 6%止损
        take_profit_ratio=0.12,  # 12%止盈
    )
    
    print("自定义配置:")
    print(f"  - 初始资金: {config.initial_capital}元")
    print(f"  - 最大持仓: {config.max_stocks}只")
    print(f"  - 优先阶段: {config.preferred_stages}")
    print(f"  - 恐慌点跌幅阈值: {config.panic_drop_threshold}%")
    
    strategy = StockSelectionStrategy(config)
    
    # 股票池
    stock_pool = ["600519", "000001", "600036", "000333", "600030"]
    
    print(f"\n股票池: {len(stock_pool)}只\n")
    
    # 选股
    result = strategy.select_stocks_sync(stock_pool)
    
    # 显示结果
    if result.top_candidates:
        print(f"\n推荐买入:")
        for candidate in result.top_candidates:
            print(f"  {candidate.code} {candidate.name}: "
                  f"价格{candidate.best_buy_point.price:.2f}, "
                  f"建议买入{candidate.suggested_shares}股, "
                  f"仓位{candidate.suggested_position_pct*100:.1f}%")
    
    return result


def example_single_stock_analysis():
    """单只股票分析示例"""
    print("\n" + "="*60)
    print("示例4: 单只股票详细分析")
    print("="*60 + "\n")
    
    from core.selection.buy_point_detector import BuyPointDetector
    from core.tools.data_fetcher import fetch_stock_data, get_stock_name
    
    code = "600519"  # 贵州茅台
    
    print(f"分析股票: {code}")
    
    # 获取数据
    print("获取历史数据...")
    df = fetch_stock_data(code, days=250)
    
    if df is None:
        print(f"无法获取 {code} 数据")
        return
    
    name = get_stock_name(code)
    print(f"股票名称: {name}")
    print(f"数据范围: {len(df)}个交易日")
    
    # 创建检测器
    config = SelectionConfig()
    detector = BuyPointDetector(config)
    
    # 检测买点
    print("\n检测买点...")
    buy_points = detector.detect_buy_points(code, df)
    
    if buy_points:
        print(f"\n检测到 {len(buy_points)} 个买点信号:\n")
        for idx, bp in enumerate(buy_points[:5], 1):
            print(f"{idx}. 买点类型: {bp.buy_type}")
            print(f"   信号日期: {bp.date}")
            print(f"   买入价格: {bp.price:.2f}")
            print(f"   股票阶段: {bp.stage_name}")
            print(f"   综合评分: {bp.score:.1f}")
            print(f"   置信度: {bp.confidence:.2f}")
            print(f"   理由: {bp.reasoning}")
            
            if bp.drop_pct is not None:
                print(f"   跌幅: {bp.drop_pct:.2f}%")
            if bp.vol_ratio is not None:
                print(f"   放量倍数: {bp.vol_ratio:.2f}")
            if bp.trend_strength is not None:
                print(f"   趋势强度: {bp.trend_strength:.2f}")
            if bp.emotion_score is not None:
                print(f"   情绪评分: {bp.emotion_score:.2f}")
            print()
    else:
        print("\n未检测到买点信号")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("博弈交易选股策略 - 使用示例")
    print("="*80)
    
    # 创建输出目录
    import os
    os.makedirs("output", exist_ok=True)
    
    # 运行示例
    print("\n选择要运行的示例:")
    print("1. 基础选股")
    print("2. 保守型选股")
    print("3. 自定义配置选股")
    print("4. 单只股票详细分析")
    print("5. 运行所有示例")
    
    choice = input("\n请输入选项(1-5): ").strip()
    
    if choice == "1":
        example_basic_selection()
    elif choice == "2":
        example_conservative_selection()
    elif choice == "3":
        example_custom_config()
    elif choice == "4":
        example_single_stock_analysis()
    elif choice == "5":
        example_basic_selection()
        example_conservative_selection()
        example_custom_config()
        example_single_stock_analysis()
    else:
        print("无效选项,运行基础选股示例")
        example_basic_selection()
    
    print("\n" + "="*80)
    print("示例运行完成!")
    print("="*80)


if __name__ == "__main__":
    main()
