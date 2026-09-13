"""
测试八字分析工作流系统集成
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.workflow.orchestrator import get_workflow_orchestrator
from core.agents.bazi_dialogue_agent import BaziContext


def test_workflow_basic():
    """测试基础工作流功能"""
    print("=" * 80)
    print("测试1: 基础八字分析工作流")
    print("=" * 80)
    
    # 准备测试数据
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '乙', 'di_zhi': '亥', 'cang_gan': ['壬', '甲']},
            'yue_zhu': {'tian_gan': '丁', 'di_zhi': '亥', 'cang_gan': ['壬', '甲']},
            'ri_zhu': {'tian_gan': '乙', 'di_zhi': '卯', 'cang_gan': ['乙']},
            'shi_zhu': {'tian_gan': '己', 'di_zhi': '卯', 'cang_gan': ['乙']},
            'ri_zhu_tiangan': '乙'
        },
        wuxing_analysis={
            'wuxing_data': {
                'mu': 3,
                'huo': 1,
                'tu': 1,
                'jin': 0,
                'shui': 2
            }
        },
        gender='男',
        birth_info={'year': 1995}
    )
    
    user_question = "请分析我的八字命局"
    
    # 获取编排器
    orchestrator = get_workflow_orchestrator()
    
    # 执行分析
    print(f"\n用户问题: {user_question}")
    print("\n开始执行工作流...")
    
    result = orchestrator.process_bazi_analysis(
        user_question=user_question,
        bazi_context=bazi_context
    )
    
    # 输出结果
    if result.get('success'):
        print("\n✅ 工作流执行成功!")
        print("\n分析报告:")
        print("-" * 80)
        print(result.get('report', result.get('response', '')))
        print("-" * 80)
    else:
        print("\n❌ 工作流执行失败!")
        print(f"错误: {result.get('error', '未知错误')}")
    
    return result


def test_workflow_career():
    """测试事业运势分析"""
    print("\n" + "=" * 80)
    print("测试2: 事业运势分析工作流")
    print("=" * 80)
    
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '甲', 'di_zhi': '子'},
            'yue_zhu': {'tian_gan': '丙', 'di_zhi': '子'},
            'ri_zhu': {'tian_gan': '甲', 'di_zhi': '辰'},
            'shi_zhu': {'tian_gan': '丁', 'di_zhi': '卯'}
        },
        gender='男',
        birth_info={'year': 1984}
    )
    
    user_question = "我今年事业运势如何?适合换工作吗?"
    
    orchestrator = get_workflow_orchestrator()
    
    print(f"\n用户问题: {user_question}")
    print("\n开始执行工作流...")
    
    result = orchestrator.process_bazi_analysis(
        user_question=user_question,
        bazi_context=bazi_context
    )
    
    if result.get('success'):
        print("\n✅ 工作流执行成功!")
        print("\n分析报告:")
        print("-" * 80)
        print(result.get('report', result.get('response', '')))
        print("-" * 80)
    else:
        print("\n❌ 工作流执行失败!")
        print(f"错误: {result.get('error', '未知错误')}")
    
    return result


def test_workflow_conversation():
    """测试多轮对话"""
    print("\n" + "=" * 80)
    print("测试3: 多轮对话工作流")
    print("=" * 80)
    
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '癸', 'di_zhi': '亥'},
            'yue_zhu': {'tian_gan': '壬', 'di_zhi': '子'},
            'ri_zhu': {'tian_gan': '甲', 'di_zhi': '辰'},
            'shi_zhu': {'tian_gan': '乙', 'di_zhi': '丑'}
        },
        gender='男',
        birth_info={'year': 1983}
    )
    
    orchestrator = get_workflow_orchestrator()
    
    conversation_history = []
    
    # 第一轮
    print("\n【第一轮对话】")
    user_question1 = "请分析我的八字"
    print(f"用户: {user_question1}")
    
    result1 = orchestrator.process_bazi_analysis(
        user_question=user_question1,
        bazi_context=bazi_context
    )
    
    if result1.get('success'):
        response1 = result1.get('report', result1.get('response', ''))
        print(f"助手: {response1[:200]}...")
        
        conversation_history.append({
            'user': user_question1,
            'assistant': response1
        })
    else:
        print(f"❌ 失败: {result1.get('error')}")
        return
    
    # 第二轮(追问)
    print("\n【第二轮对话】")
    user_question2 = "那我2025年财运如何?"
    print(f"用户: {user_question2}")
    
    result2 = orchestrator.process_bazi_analysis(
        user_question=user_question2,
        bazi_context=bazi_context,
        conversation_history=conversation_history
    )
    
    if result2.get('success'):
        response2 = result2.get('report', result2.get('response', ''))
        print(f"助手: {response2[:200]}...")
    else:
        print(f"❌ 失败: {result2.get('error')}")


def test_workflow_router():
    """测试路由决策"""
    print("\n" + "=" * 80)
    print("测试4: 工作流路由决策")
    print("=" * 80)
    
    from core.workflow.router import get_workflow_router
    
    router = get_workflow_router()
    
    # 测试不同意图
    test_cases = [
        {"intent": "full_analysis", "expected": "full_analysis"},
        {"intent": "career_analysis", "expected": "full_analysis"},
        {"intent": "wealth_analysis", "expected": "full_analysis"},
        {"intent": "follow_up", "expected": "conversation"},
        {"intent": "quick_query", "expected": "quick_query"},
    ]
    
    for case in test_cases:
        workflow_name = router.route(case)
        expected = case['expected']
        status = "✅" if workflow_name == expected else "❌"
        print(f"{status} 意图'{case['intent']}' → 工作流'{workflow_name}' (期望: {expected})")


if __name__ == "__main__":
    print("\n" + "🚀 " * 20)
    print("八字分析工作流系统集成测试")
    print("🚀 " * 20 + "\n")
    
    # 测试路由决策
    test_workflow_router()
    
    # 测试基础功能
    # test_workflow_basic()
    
    # 测试事业分析
    # test_workflow_career()
    
    # 测试多轮对话
    # test_workflow_conversation()
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
