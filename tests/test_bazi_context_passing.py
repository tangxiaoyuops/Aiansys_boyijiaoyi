"""
测试八字对话上下文传递
验证命盘参数在多轮对话中是否正确传递
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.bazi_dialogue_agent import BaziContext, BaziDialogueAgent
from core.workflow.nodes.dialogue_node import DialogueNode


def test_bazi_context_building():
    """测试八字上下文构建"""
    print("\n=== 测试八字上下文构建 ===")

    # 模拟八字数据
    sizhu = {
        'nian_zhu': {'tian_gan': '甲', 'di_zhi': '子', 'cang_gan': ['癸']},
        'yue_zhu': {'tian_gan': '丙', 'di_zhi': '寅', 'cang_gan': ['甲', '丙', '戊']},
        'ri_zhu': {'tian_gan': '戊', 'di_zhi': '午', 'cang_gan': ['丁', '己']},
        'shi_zhu': {'tian_gan': '庚', 'di_zhi': '申', 'cang_gan': ['庚', '壬', '戊']},
        'ri_zhu_tiangan': '戊',
        'bazi_year': 1984
    }

    wuxing_analysis = {
        'wuxing_data': {
            'jin': 2,
            'mu': 2,
            'shui': 1,
            'huo': 2,
            'tu': 2,
            'rizhu_wuxing': '土'
        }
    }

    shishen_analysis = {
        'shishen_data': {
            'nian_zhu': {'gan_shishen': '比肩', 'zhi_shishen': '偏财'},
            'yue_zhu': {'gan_shishen': '偏印', 'zhi_shishen': '比肩'},
            'ri_zhu': {'gan_shishen': '日主', 'zhi_shishen': '正印'},
            'shi_zhu': {'gan_shishen': '食神', 'zhi_shishen': '食神'}
        }
    }

    dayun_analysis = {
        'dayun_list': [
            {'gan': '丁', 'zhi': '卯', 'start_age': '5', 'end_age': '14', 'start_year': '1989', 'end_year': '1998'},
            {'gan': '戊', 'zhi': '辰', 'start_age': '15', 'end_age': '24', 'start_year': '1999', 'end_year': '2008'},
            {'gan': '己', 'zhi': '巳', 'start_age': '25', 'end_age': '34', 'start_year': '2009', 'end_year': '2018'},
            {'gan': '庚', 'zhi': '午', 'start_age': '35', 'end_age': '44', 'start_year': '2019', 'end_year': '2028'},
        ]
    }

    # 创建BaziContext对象
    bazi_context = BaziContext(
        sizhu=sizhu,
        wuxing_analysis=wuxing_analysis,
        shishen_analysis=shishen_analysis,
        dayun_analysis=dayun_analysis,
        gender='男',
        birth_info={'year': 1984}
    )

    # 使用BaziDialogueAgent构建上下文文本
    agent = BaziDialogueAgent()
    context_text = agent.build_context_text(bazi_context)

    print("\n生成的八字上下文文本:")
    print(context_text)

    # 验证关键信息是否包含
    assert '【四柱八字】' in context_text, "缺少四柱八字标题"
    assert '甲子' in context_text, "缺少年柱信息"
    assert '戊午' in context_text, "缺少日柱信息"
    assert '【五行分析】' in context_text, "缺少五行分析标题"
    assert '【十神分析】' in context_text, "缺少十神分析标题"
    assert '【大运分析】' in context_text, "缺少大运分析标题"

    print("\n[成功] 八字上下文构建测试通过!")
    return True


def test_dialogue_node_context():
    """测试对话节点的八字上下文处理"""
    print("\n=== 测试对话节点八字上下文处理 ===")

    # 创建对话节点
    node = DialogueNode('test_dialogue', {
        'node_subtype': 'context_understanding',
        'model': 'gpt-4o',
        'timeout': 20
    })

    # 模拟八字上下文数据
    bazi_context_dict = {
        'sizhu': {
            'nian_zhu': {'tian_gan': '甲', 'di_zhi': '子'},
            'yue_zhu': {'tian_gan': '丙', 'di_zhi': '寅'},
            'ri_zhu': {'tian_gan': '戊', 'di_zhi': '午'},
            'shi_zhu': {'tian_gan': '庚', 'di_zhi': '申'},
            'ri_zhu_tiangan': '戊',
            'bazi_year': 1984
        },
        'wuxing_analysis': {
            'wuxing_data': {
                'jin': 2, 'mu': 2, 'shui': 1, 'huo': 2, 'tu': 2,
                'rizhu_wuxing': '土'
            }
        },
        'shishen_analysis': {
            'shishen_data': {
                'nian_zhu': {'gan_shishen': '比肩'},
                'ri_zhu': {'gan_shishen': '日主'}
            }
        },
        'dayun_analysis': {
            'dayun_list': [
                {'gan': '庚', 'zhi': '午', 'start_age': '35', 'end_age': '44'}
            ]
        },
        'gender': '男',
        'birth_info': {'year': 1984},
        'analysis_style': 'classic'
    }

    # 使用新的方法构建八字上下文文本
    context_text = node._build_bazi_context_text(bazi_context_dict)

    print("\n对话节点生成的八字上下文文本:")
    print(context_text)

    # 验证关键信息
    assert '【四柱八字】' in context_text, "对话节点缺少四柱八字标题"
    assert '甲子' in context_text, "对话节点缺少年柱信息"
    assert '戊午' in context_text, "对话节点缺少日柱信息"

    print("\n[成功] 对话节点八字上下文处理测试通过!")
    return True


def test_orchestrator_data_preparation():
    """测试编排器的数据准备"""
    print("\n=== 测试编排器数据准备 ===")

    from core.workflow.orchestrator import WorkflowOrchestrator
    from core.agents.bazi_dialogue_agent import BaziContext

    orchestrator = WorkflowOrchestrator()

    # 创建BaziContext
    bazi_context = BaziContext(
        sizhu={'nian_zhu': {'tian_gan': '甲', 'di_zhi': '子'}, 'ri_zhu_tiangan': '戊'},
        wuxing_analysis={'wuxing_data': {'jin': 2, 'mu': 2}},
        shishen_analysis={'shishen_data': {}},
        dayun_analysis={'dayun_list': []},
        gender='男',
        birth_info={'year': 1984}
    )

    # 准备输入数据
    input_data = orchestrator._prepare_input_data(
        user_question="我的财运如何?",
        bazi_context=bazi_context,
        conversation_history=[],
        intent_result={'intent': 'wealth_analysis', 'confidence': 0.9}
    )

    print("\n编排器准备的输入数据:")
    print(f"- user_question: {input_data.get('user_question')}")
    print(f"- intent: {input_data.get('intent')}")
    print(f"- has bazi_context: {'bazi_context' in input_data}")
    print(f"- bazi_context keys: {list(input_data.get('bazi_context', {}).keys())}")

    # 验证
    assert 'bazi_context' in input_data, "编排器缺少bazi_context字段"
    assert input_data['bazi_context']['sizhu'] == bazi_context.sizhu, "八字数据不匹配"
    assert input_data['bazi_context']['gender'] == '男', "性别信息丢失"

    print("\n[成功] 编排器数据准备测试通过!")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("开始测试八字对话上下文传递修复")
    print("=" * 60)

    try:
        # 运行所有测试
        test_bazi_context_building()
        test_dialogue_node_context()
        test_orchestrator_data_preparation()

        print("\n" + "=" * 60)
        print("[成功] 所有测试通过!八字上下文传递修复成功!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[失败] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[失败] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
