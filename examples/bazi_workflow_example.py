"""
八字分析工作流使用示例

展示如何使用工作流系统进行八字分析
"""
from core.workflow.orchestrator import get_workflow_orchestrator
from core.agents.bazi_dialogue_agent import BaziContext


def example_full_analysis():
    """示例1: 完整八字分析"""
    print("=" * 80)
    print("示例1: 完整八字分析")
    print("=" * 80)
    
    # 1. 准备八字数据
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '乙', 'di_zhi': '亥'},
            'yue_zhu': {'tian_gan': '丁', 'di_zhi': '亥'},
            'ri_zhu': {'tian_gan': '乙', 'di_zhi': '卯'},
            'shi_zhu': {'tian_gan': '己', 'di_zhi': '卯'},
            'ri_zhu_tiangan': '乙'
        },
        wuxing_analysis={
            'wuxing_data': {
                'mu': 3, 'huo': 1, 'tu': 1, 'jin': 0, 'shui': 2
            }
        },
        shishen_analysis={
            'shishen_data': {
                'nian_zhu': {'gan_shishen': '比肩', 'zhi_shishen': '正印'},
                'yue_zhu': {'gan_shishen': '食神', 'zhi_shishen': '正印'},
                'ri_zhu': {'gan_shishen': '日主', 'zhi_shishen': '比肩'},
                'shi_zhu': {'gan_shishen': '偏财', 'zhi_shishen': '比肩'}
            }
        },
        gender='男',
        birth_info={'year': 1995}
    )
    
    # 2. 用户问题
    user_question = "请帮我分析一下我的八字命局"
    
    # 3. 获取编排器
    orchestrator = get_workflow_orchestrator()
    
    # 4. 执行分析
    result = orchestrator.process_bazi_analysis(
        user_question=user_question,
        bazi_context=bazi_context
    )
    
    # 5. 输出结果
    if result.get('success'):
        print("\n分析报告:")
        print(result.get('report', ''))
    else:
        print("分析失败:", result.get('error'))
    
    return result


def example_career_analysis():
    """示例2: 事业运势分析"""
    print("\n" + "=" * 80)
    print("示例2: 事业运势分析")
    print("=" * 80)
    
    # 1. 准备八字数据(同上)
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
    
    # 2. 用户问题(具体问题)
    user_question = "我今年事业运势如何?适合换工作吗?"
    
    # 3. 执行分析
    orchestrator = get_workflow_orchestrator()
    result = orchestrator.process_bazi_analysis(
        user_question=user_question,
        bazi_context=bazi_context
    )
    
    # 4. 输出结果
    if result.get('success'):
        print("\n分析报告:")
        print(result.get('report', ''))
    
    return result


def example_conversation():
    """示例3: 多轮对话"""
    print("\n" + "=" * 80)
    print("示例3: 多轮对话")
    print("=" * 80)
    
    # 1. 准备八字数据
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
    
    # 2. 第一轮对话
    orchestrator = get_workflow_orchestrator()
    
    conversation_history = []
    
    # 第一问
    user_question1 = "请分析我的八字"
    result1 = orchestrator.process_bazi_analysis(
        user_question=user_question1,
        bazi_context=bazi_context
    )
    conversation_history.append({
        'user': user_question1,
        'assistant': result1.get('report', '')
    })
    
    print("\n第一轮对话:")
    print(f"用户: {user_question1}")
    print(f"助手: {result1.get('report', '')[:200]}...")
    
    # 第二问(追问)
    user_question2 = "那我2025年财运如何?"
    result2 = orchestrator.process_bazi_analysis(
        user_question=user_question2,
        bazi_context=bazi_context,
        conversation_history=conversation_history
    )
    
    print("\n第二轮对话:")
    print(f"用户: {user_question2}")
    print(f"助手: {result2.get('response', '')}")
    
    return result2


def example_quick_query():
    """示例4: 快速查询"""
    print("\n" + "=" * 80)
    print("示例4: 快速查询")
    print("=" * 80)
    
    # 1. 准备八字数据
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '丙', 'di_zhi': '戌'},
            'yue_zhu': {'tian_gan': '己', 'di_zhi': '亥'},
            'ri_zhu': {'tian_gan': '癸', 'di_zhi': '亥'},
            'shi_zhu': {'tian_gan': '壬', 'di_zhi': '子'}
        },
        gender='女',
        birth_info={'year': 2006}
    )
    
    # 2. 快速查询
    user_question = "我今年的运势如何?"
    
    orchestrator = get_workflow_orchestrator()
    result = orchestrator.process_bazi_analysis(
        user_question=user_question,
        bazi_context=bazi_context
    )
    
    print(f"\n用户: {user_question}")
    print(f"助手: {result.get('result', '')}")
    
    return result


if __name__ == "__main__":
    # 运行示例
    print("八字分析工作流系统 - 使用示例\n")
    
    # 示例1: 完整分析
    example_full_analysis()
    
    # 示例2: 事业分析
    # example_career_analysis()
    
    # 示例3: 多轮对话
    # example_conversation()
    
    # 示例4: 快速查询
    # example_quick_query()
    
    print("\n" + "=" * 80)
    print("示例运行完成!")
    print("=" * 80)
