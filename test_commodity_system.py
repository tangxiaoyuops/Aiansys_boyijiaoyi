"""
大宗商品分析系统测试脚本
测试各个模块的功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph.commodity_analysis_graph import run_commodity_analysis


def test_commodity_analysis():
    """测试大宗商品分析功能"""
    print("=" * 60)
    print("大宗商品分析系统测试")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "原油趋势分析",
            "params": {
                "commodity_or_chain": "原油",
                "strategy_type": "trend",
                "enable_backtest": True,
                "max_rounds": 1
            }
        },
        {
            "name": "铜套利分析",
            "params": {
                "commodity_or_chain": "铜",
                "strategy_type": "arbitrage",
                "enable_backtest": False,
                "max_rounds": 1
            }
        },
        {
            "name": "大豆事件驱动分析",
            "params": {
                "commodity_or_chain": "大豆",
                "strategy_type": "event_driven",
                "enable_backtest": True,
                "max_rounds": 1
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"{'=' * 60}")
        
        try:
            result = run_commodity_analysis(**test_case["params"])
            
            if result["success"]:
                data = result["data"]
                print(f"\n✓ 测试成功")
                print(f"  - 报告长度: {len(data.get('report', ''))} 字符")
                print(f"  - 策略数量: {len(data.get('strategies', []))}")
                print(f"  - 回测结果: {len(data.get('backtest_results', []))}")
                print(f"  - 总耗时: {data.get('total_duration', 0):.2f} 秒")
                print(f"  - 使用轮次: {data.get('rounds_used', 0)}")
                
                if data.get('strategies'):
                    print(f"\n  策略示例:")
                    for j, strategy in enumerate(data['strategies'][:2], 1):
                        print(f"    {j}. {strategy.get('direction')} @ {strategy.get('entry_price')}")
                        print(f"       目标: {strategy.get('target_price')}, 止损: {strategy.get('stop_loss')}")
                        print(f"       置信度: {strategy.get('confidence')}")
                
                if data.get('backtest_results'):
                    print(f"\n  回测示例:")
                    for j, backtest in enumerate(data['backtest_results'][:1], 1):
                        print(f"    {j}. 收益率: {backtest.get('total_return'):.2f}%")
                        print(f"       夏普比率: {backtest.get('sharpe_ratio'):.2f}")
                        print(f"       最大回撤: {backtest.get('max_drawdown'):.2f}%")
                        print(f"       胜率: {backtest.get('win_rate'):.2f}%")
            else:
                print(f"\n✗ 测试失败: {result.get('message')}")
                
        except Exception as e:
            print(f"\n✗ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("所有测试完成")
    print(f"{'=' * 60}")


def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("API端点测试")
    print("=" * 60)
    
    api_endpoints = [
        "POST /api/commodity/analyze",
        "POST /api/commodity/strategy",
        "POST /api/commodity/backtest",
        "GET /api/commodity/strategies",
        "GET /api/commodity/health"
    ]
    
    print("\n可用的API端点:")
    for endpoint in api_endpoints:
        print(f"  - {endpoint}")
    
    print("\n提示: 启动服务器后，可以使用curl或Postman测试这些端点")
    print("      示例: curl -X POST http://localhost:8000/api/commodity/analyze \\")
    print("             -H 'Content-Type: application/json' \\")
    print("             -d '{\"commodity_or_chain\":\"原油\",\"strategy_type\":\"trend\"}'")


def test_data_models():
    """测试数据模型"""
    print("\n" + "=" * 60)
    print("数据模型测试")
    print("=" * 60)
    
    from core.models.commodity_models import SupplyNode, PricePoint, NewsItem, RawEvidence
    from core.models.strategy_models import StrategySignal, BacktestResult, TechnicalIndicators
    from core.models.commodity_state import CommodityAnalysisState
    
    print("\n✓ commodity_models 模块导入成功")
    print("  - SupplyNode")
    print("  - PricePoint")
    print("  - NewsItem")
    print("  - RawEvidence")
    
    print("\n✓ strategy_models 模块导入成功")
    print("  - StrategySignal")
    print("  - BacktestResult")
    print("  - TechnicalIndicators")
    
    print("\n✓ commodity_state 模块导入成功")
    print("  - CommodityAnalysisState")
    
    print("\n✓ 所有数据模型导入成功")


def test_tools():
    """测试工具模块"""
    print("\n" + "=" * 60)
    print("工具模块测试")
    print("=" * 60)
    
    try:
        from core.tools.commodity_fetcher import create_commodity_fetcher
        from core.tools.commodity_search import create_commodity_searcher
        from core.tools.technical_indicators import create_technical_indicator_calculator
        from core.tools.backtest_engine import create_backtest_engine
        
        print("\n✓ commodity_fetcher 模块导入成功")
        
        print("\n✓ commodity_search 模块导入成功")
        
        print("\n✓ technical_indicators 模块导入成功")
        
        print("\n✓ backtest_engine 模块导入成功")
        
        print("\n✓ 所有工具模块导入成功")
        
    except Exception as e:
        print(f"\n✗ 工具模块导入失败: {str(e)}")


def test_agents():
    """测试Agent模块"""
    print("\n" + "=" * 60)
    print("Agent模块测试")
    print("=" * 60)
    
    try:
        from core.agents import commodity_intent_agent
        from core.agents import commodity_fetch_agent
        from core.agents import commodity_analysis_agent
        from core.agents import commodity_judgment_agent
        from core.agents import commodity_search_agent
        from core.agents import technical_indicators_agent
        from core.agents import strategy_generation_agent
        from core.agents import strategy_risk_agent
        from core.agents import strategy_backtest_agent
        from core.agents import commodity_report_agent
        
        print("\n✓ commodity_intent_agent 模块导入成功")
        print("✓ commodity_fetch_agent 模块导入成功")
        print("✓ commodity_analysis_agent 模块导入成功")
        print("✓ commodity_judgment_agent 模块导入成功")
        print("✓ commodity_search_agent 模块导入成功")
        print("✓ technical_indicators_agent 模块导入成功")
        print("✓ strategy_generation_agent 模块导入成功")
        print("✓ strategy_risk_agent 模块导入成功")
        print("✓ strategy_backtest_agent 模块导入成功")
        print("✓ commodity_report_agent 模块导入成功")
        
        print("\n✓ 所有Agent模块导入成功")
        
    except Exception as e:
        print(f"\n✗ Agent模块导入失败: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="大宗商品分析系统测试")
    parser.add_argument(
        "--full",
        action="store_true",
        help="运行完整测试（包括实际分析）"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="仅运行快速测试（模块导入）"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        print("\n运行快速测试（模块导入）...")
        test_data_models()
        test_tools()
        test_agents()
        test_api_endpoints()
    elif args.full:
        print("\n运行完整测试（包括实际分析）...")
        test_data_models()
        test_tools()
        test_agents()
        test_commodity_analysis()
        test_api_endpoints()
    else:
        print("\n运行默认测试（模块导入）...")
        test_data_models()
        test_tools()
        test_agents()
        test_api_endpoints()
        print("\n提示: 使用 --full 运行完整测试")
        print("      使用 --quick 运行快速测试")
