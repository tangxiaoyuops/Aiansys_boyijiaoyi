"""
测试修复后的数据格式问题
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from core.agent_framework.tools.boyi_analysis_tools import identify_washout, check_o_point
from core.agent_framework.examples.boyi_real_tools import calculate_real_indicators


def test_identify_washout():
    """测试洗盘识别功能"""
    print("=" * 80)
    print("测试 identify_washout 函数")
    print("=" * 80)
    
    try:
        result = identify_washout('603698', days=180)
        
        print(f"\n状态: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"[OK] 洗盘识别: {result.get('is_washout')}")
            print(f"[OK] 洗盘类型: {result.get('washout_type')}")
            print(f"[OK] 洗盘效果: {result.get('washout_effect')}")
            print(f"[OK] 最大回撤: {result.get('max_drawdown_pct')}%")
            print(f"[OK] 恐惧评分: {result.get('fear_score')}")
            print(f"[OK] 焦虑评分: {result.get('anxiety_score')}")
            print(f"[OK] 成交量比率: {result.get('volume_ratio')}")
            print("\n[SUCCESS] 测试通过! identify_washout 函数工作正常")
        else:
            print(f"[ERROR] 错误: {result.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


def test_calculate_real_indicators():
    """测试技术指标计算功能"""
    print("=" * 80)
    print("测试 calculate_real_indicators 函数")
    print("=" * 80)
    
    try:
        result = calculate_real_indicators('603698', days=180)
        
        print(f"\n状态: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"[OK] 当前价格: {result.get('current_price')}")
            print(f"[OK] MA5: {result.get('ma5')}")
            print(f"[OK] MA20: {result.get('ma20')}")
            print(f"[OK] MA60: {result.get('ma60')}")
            print(f"[OK] MACD: {result.get('macd')}")
            print(f"[OK] RSI: {result.get('rsi')}")
            print(f"[OK] 最大回撤(60日): {result.get('max_drawdown_60d')}%")
            print(f"[OK] 最大回撤(120日): {result.get('max_drawdown_120d')}%")
            print(f"[OK] 波动率(20日): {result.get('volatility_20d')}%")
            print(f"[OK] 波动率(60日): {result.get('volatility_60d')}%")
            print("\n[SUCCESS] 测试通过! calculate_real_indicators 函数工作正常")
        else:
            print(f"[ERROR] 错误: {result.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("数据格式修复测试")
    print("=" * 80 + "\n")
    
    # 测试洗盘识别
    test_identify_washout()
    
    # 测试技术指标计算
    test_calculate_real_indicators()
    
    print("=" * 80)
    print("测试完成!")
    print("=" * 80)
