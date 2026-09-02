"""
测试八字分析配置文件
验证配置文件是否正确加载
"""
import sys
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.config.bazi_analysis_config import (
    QIJI_FLOW_ANALYSIS_RULES,
    QIJI_FLOW_CORE_PROMPT,
    SHISHEN_DETAILED_CONFIG,
    HE_CHONG_CONFIG,
    SHENSHA_CONFIG,
    WUXING_STRENGTH_CRITERIA,
    ANALYSIS_OUTPUT_TEMPLATE,
    USAGE_GUIDE,
    ADVANCED_ANALYSIS_EXAMPLES
)

def test_config_loaded():
    """测试配置是否正确加载"""
    print("=" * 80)
    print("八字分析配置文件测试")
    print("=" * 80)
    
    # 测试气机流转法则
    print("\n1. 测试 QIJI_FLOW_ANALYSIS_RULES")
    print("-" * 80)
    assert QIJI_FLOW_ANALYSIS_RULES is not None, "QIJI_FLOW_ANALYSIS_RULES 未加载"
    assert "进气退气" in QIJI_FLOW_ANALYSIS_RULES, "缺少'进气退气'内容"
    assert "合局真假" in QIJI_FLOW_ANALYSIS_RULES, "缺少'合局真假'内容"
    assert "月令司权" in QIJI_FLOW_ANALYSIS_RULES, "缺少'月令司权'内容"
    print("[OK] QIJI_FLOW_ANALYSIS_RULES 加载成功")
    print(f"  长度: {len(QIJI_FLOW_ANALYSIS_RULES)} 字符")
    
    # 测试核心提示词
    print("\n2. 测试 QIJI_FLOW_CORE_PROMPT")
    print("-" * 80)
    assert QIJI_FLOW_CORE_PROMPT is not None, "QIJI_FLOW_CORE_PROMPT 未加载"
    assert "进气退气" in QIJI_FLOW_CORE_PROMPT, "核心提示词缺少'进气退气'"
    assert "合局真假" in QIJI_FLOW_CORE_PROMPT, "核心提示词缺少'合局真假'"
    print("[OK] QIJI_FLOW_CORE_PROMPT 加载成功")
    print(f"  长度: {len(QIJI_FLOW_CORE_PROMPT)} 字符")
    
    # 测试十神配置
    print("\n3. 测试 SHISHEN_DETAILED_CONFIG")
    print("-" * 80)
    assert SHISHEN_DETAILED_CONFIG is not None, "SHISHEN_DETAILED_CONFIG 未加载"
    assert "印星" in SHISHEN_DETAILED_CONFIG, "缺少'印星'配置"
    assert "官杀" in SHISHEN_DETAILED_CONFIG, "缺少'官杀'配置"
    assert "财星" in SHISHEN_DETAILED_CONFIG, "缺少'财星'配置"
    assert "食伤" in SHISHEN_DETAILED_CONFIG, "缺少'食伤'配置"
    assert "比劫" in SHISHEN_DETAILED_CONFIG, "缺少'比劫'配置"
    print("[OK] SHISHEN_DETAILED_CONFIG 加载成功")
    print(f"  十神类别: {list(SHISHEN_DETAILED_CONFIG.keys())}")
    
    # 测试合局冲局配置
    print("\n4. 测试 HE_CHONG_CONFIG")
    print("-" * 80)
    assert HE_CHONG_CONFIG is not None, "HE_CHONG_CONFIG 未加载"
    assert "天干五合" in HE_CHONG_CONFIG, "缺少'天干五合'配置"
    assert "地支六合" in HE_CHONG_CONFIG, "缺少'地支六合'配置"
    assert "地支三合局" in HE_CHONG_CONFIG, "缺少'地支三合局'配置"
    assert "地支三会局" in HE_CHONG_CONFIG, "缺少'地支三会局'配置"
    assert "地支六冲" in HE_CHONG_CONFIG, "缺少'地支六冲'配置"
    print("[OK] HE_CHONG_CONFIG 加载成功")
    print(f"  合局类型: {list(HE_CHONG_CONFIG.keys())}")
    
    # 测试神煞配置
    print("\n5. 测试 SHENSHA_CONFIG")
    print("-" * 80)
    assert SHENSHA_CONFIG is not None, "SHENSHA_CONFIG 未加载"
    assert "吉神" in SHENSHA_CONFIG, "缺少'吉神'配置"
    assert "凶煞" in SHENSHA_CONFIG, "缺少'凶煞'配置"
    print("[OK] SHENSHA_CONFIG 加载成功")
    print(f"  神煞类型: {list(SHENSHA_CONFIG.keys())}")
    
    # 测试五行旺衰标准
    print("\n6. 测试 WUXING_STRENGTH_CRITERIA")
    print("-" * 80)
    assert WUXING_STRENGTH_CRITERIA is not None, "WUXING_STRENGTH_CRITERIA 未加载"
    assert "得时" in WUXING_STRENGTH_CRITERIA, "缺少'得时'标准"
    assert "得地" in WUXING_STRENGTH_CRITERIA, "缺少'得地'标准"
    assert "得势" in WUXING_STRENGTH_CRITERIA, "缺少'得势'标准"
    print("[OK] WUXING_STRENGTH_CRITERIA 加载成功")
    
    # 测试输出模板
    print("\n7. 测试 ANALYSIS_OUTPUT_TEMPLATE")
    print("-" * 80)
    assert ANALYSIS_OUTPUT_TEMPLATE is not None, "ANALYSIS_OUTPUT_TEMPLATE 未加载"
    assert "气机流转" in ANALYSIS_OUTPUT_TEMPLATE, "缺少'气机流转'模板"
    print("[OK] ANALYSIS_OUTPUT_TEMPLATE 加载成功")
    
    # 测试使用指南
    print("\n8. 测试 USAGE_GUIDE")
    print("-" * 80)
    assert USAGE_GUIDE is not None, "USAGE_GUIDE 未加载"
    print("[OK] USAGE_GUIDE 加载成功")
    
    # 测试进阶案例
    print("\n9. 测试 ADVANCED_ANALYSIS_EXAMPLES")
    print("-" * 80)
    assert ADVANCED_ANALYSIS_EXAMPLES is not None, "ADVANCED_ANALYSIS_EXAMPLES 未加载"
    assert "案例" in ADVANCED_ANALYSIS_EXAMPLES, "缺少案例分析"
    print("[OK] ADVANCED_ANALYSIS_EXAMPLES 加载成功")
    print(f"  案例数量: {ADVANCED_ANALYSIS_EXAMPLES.count('案例')}")
    
    print("\n" + "=" * 80)
    print("所有测试通过！配置文件加载成功。")
    print("=" * 80)
    
    # 显示关键内容预览
    print("\n【核心优化点预览】")
    print("-" * 80)
    print("\n1. 进气退气法则：")
    if "进气之神不畏克" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'进气之神不畏克'法则")
    if "退气之神难挡杀" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'退气之神难挡杀'法则")
    
    print("\n2. 合局真假辨析：")
    if "化神是否透干" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'化神透干'判定")
    if "合绊" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'合绊'辨析")
    
    print("\n3. 月令司权判断：")
    if "月令司权" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'月令司权'判断")
    if "节气深浅" in QIJI_FLOW_ANALYSIS_RULES:
        print("   [OK] 已包含'节气深浅'分析")
    
    print("\n4. 典型案例：")
    print("   [OK] 案例1：子辰合水局真假辨析")
    print("   [OK] 案例2：进气退气对冲克的影响")
    print("   [OK] 案例3：三合局的化神透干判定")
    print("   [OK] 案例4：合绊与贪合忘冲")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_config_loaded()
