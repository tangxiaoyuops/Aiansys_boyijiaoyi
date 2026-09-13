"""
测试八字分析Agent系统
"""
import sys
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_config_agent import BaziConfigAgent
from core.agents.bazi_analysis_logic_agent import BaziAnalysisAgent

def test_config_agent():
    """测试配置检索Agent"""
    print("=" * 80)
    print("测试配置检索Agent")
    print("=" * 80)
    
    agent = BaziConfigAgent()
    
    # 示例1：获取第一步配置
    print("\n【示例1】获取第一步配置")
    print("-" * 80)
    step1_config = agent.get_analysis_step_config("step1")
    print(f"第一步配置长度：{len(step1_config)} 字符")
    # print(f"前300字符：\n{step1_config[:300]}...")
    
    # 示例2：获取十神信息
    print("\n【示例2】获取印星信息（身强格）")
    print("-" * 80)
    shishen_info = agent.get_shishen_info("印星", "strong")
    print(f"印星用法：{shishen_info['usage']}")
    
    # 示例3：获取合局信息
    print("\n【示例3】获取子辰合水局信息")
    print("-" * 80)
    he_info = agent.get_he_chong_info("地支六合", ["子", "丑"])
    print(f"合局信息：{he_info}")
    
    # 示例4：动态构建提示词
    print("\n【示例4】动态构建提示词")
    print("-" * 80)
    context = {
        "current_step": "step1",
        "shishen_involved": ["印星", "食伤"],
        "day_strength": "strong",
        "need_examples": True,
        "case_type": "身强印旺"
    }
    dynamic_prompt = agent.build_dynamic_prompt(context)
    print(f"动态提示词长度：{len(dynamic_prompt)} 字符")
    # print(f"前500字符：\n{dynamic_prompt[:500]}...")
    
    # 对比：完整提示词 vs 动态提示词
    print("\n【对比】完整提示词 vs 动态提示词")
    print("-" * 80)
    from core.config.bazi_analysis_config import QIJI_FLOW_ANALYSIS_RULES
    full_length = len(QIJI_FLOW_ANALYSIS_RULES)
    dynamic_length = len(dynamic_prompt)
    reduction = (1 - dynamic_length / full_length) * 100
    
    print(f"完整提示词长度：{full_length} 字符")
    print(f"动态提示词长度：{dynamic_length} 字符")
    print(f"减少比例：{reduction:.1f}%")
    
    return agent

def test_analysis_agent():
    """测试分析逻辑Agent"""
    print("\n" + "=" * 80)
    print("测试分析逻辑Agent")
    print("=" * 80)
    
    agent = BaziAnalysisAgent()
    
    # 模拟数据
    sizhu = {
        'ri_zhu': {'tian_gan': '乙', 'di_zhi': '卯'},
        'yue_zhu': {'tian_gan': '丁', 'di_zhi': '亥'},
        'nian_zhu': {'tian_gan': '乙', 'di_zhi': '亥'},
        'shi_zhu': {'tian_gan': '己', 'di_zhi': '卯'}
    }
    
    wuxing = {
        'wuxing_data': {
            'wuxing_count': {'金': 0, '木': 4, '水': 2, '火': 1, '土': 1}
        }
    }
    
    shishen = {
        'shishen_data': {
            'ri_zhu': {'gan_shishen': '比肩'}
        }
    }
    
    dayun = {
        'current_dayun': {'gan': '癸', 'zhi': '卯'}
    }
    
    liunian = {
        'gan': '庚',
        'zhi': '子'
    }
    
    # 分析情况
    print("\n【分析命局情况】")
    print("-" * 80)
    context = agent.analyze_situation(sizhu, wuxing, shishen, dayun, liunian)
    
    print(f"日主强弱：{context['day_strength']}")
    print(f"涉及的十神：{context['shishen_involved']}")
    print(f"合局冲局：{context['he_chong_involved']}")
    print(f"是否需要案例：{context['need_examples']}")
    print(f"案例类型：{context['case_type']}")
    
    # 获取第一步指导
    print("\n【获取第一步指导】")
    print("-" * 80)
    guidance = agent.get_step_guidance(1, context)
    print(f"指导长度：{len(guidance)} 字符")
    # print(f"前500字符：\n{guidance[:500]}...")
    
    # 获取快速参考
    print("\n【获取快速参考】")
    print("-" * 80)
    quick_ref = agent.get_quick_reference("身强格十神")
    print(quick_ref)
    
    return agent

def main():
    """主测试函数"""
    print("=" * 80)
    print("八字分析Agent系统测试")
    print("=" * 80)
    
    # 测试配置检索Agent
    config_agent = test_config_agent()
    
    # 测试分析逻辑Agent
    analysis_agent = test_analysis_agent()
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print("\n【核心优势】")
    print("1. 动态构建提示词，减少token使用量")
    print("2. 智能识别分析场景，按需加载配置")
    print("3. 分步骤提供指导，避免一次性加载所有配置")
    print("4. 快速参考功能，提供常用信息")

if __name__ == "__main__":
    main()
