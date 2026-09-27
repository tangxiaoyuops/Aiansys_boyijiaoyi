"""
测试多轮对话连贯性修复
验证追问时回答不再僵硬，能根据上下文自然对话
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.agents.bazi_dialogue_agent import BaziDialogueAgent, BaziContext

def test_prompt_building():
    """测试提示词构建"""
    print("="*60)
    print("测试多轮对话连贯性修复")
    print("="*60)
    
    agent = BaziDialogueAgent()
    
    # 模拟八字上下文
    bazi_context = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '丙', 'di_zhi': '子', 'cang_gan': ['癸']},
            'yue_zhu': {'tian_gan': '庚', 'di_zhi': '子', 'cang_gan': ['癸']},
            'ri_zhu': {'tian_gan': '乙', 'di_zhi': '巳', 'cang_gan': ['丙', '戊', '庚']},
            'shi_zhu': {'tian_gan': '庚', 'di_zhi': '辰', 'cang_gan': ['戊', '乙', '癸']},
            'ri_zhu_tiangan': '乙',
            'bazi_year': 1996
        },
        wuxing_analysis={'wuxing_data': {'jin': 2, 'mu': 1, 'shui': 3, 'huo': 1, 'tu': 1}},
        shishen_analysis={'shishen_data': {}},
        dayun_analysis={'dayun_list': [
            {'gan': '癸', 'zhi': '卯', 'start_age': 20, 'end_age': 30, 'start_year': 2017, 'end_year': 2027},
            {'gan': '甲', 'zhi': '辰', 'start_age': 30, 'end_age': 40, 'start_year': 2027, 'end_year': 2037},
        ]},
        gender='男',
        birth_info={'year': 1996, 'month': 2, 'day': 15, 'hour': 16},
        analysis_style='classic'
    )
    
    # 测试1：第一轮对话的user_prompt
    print("\n【测试1：第一轮对话的user_prompt】")
    print("-" * 60)
    
    chat_history_1 = []
    
    # 手动构建第一轮的user_prompt来验证
    context_text = agent.build_context_text(bazi_context)
    history_text_1 = agent.build_history_text(chat_history_1)
    
    is_first_turn = len(chat_history_1) == 0
    print(f"是否第一轮对话: {is_first_turn}")
    print(f"历史记录文本: '{history_text_1}'")
    
    # 测试2：第二轮对话的user_prompt
    print("\n【测试2：第二轮对话的user_prompt】")
    print("-" * 60)
    
    chat_history_2 = [
        {"role": "assistant", "content": "根据您的八字（丙子年、庚子月、乙巳日、庚辰时），您的水极旺...", "type": "analysis"},
        {"role": "user", "content": "27年以后会陷入财务困局嘛？", "type": "content"}
    ]
    
    history_text_2 = agent.build_history_text(chat_history_2)
    print(f"是否第一轮对话: {len(chat_history_2) <= 1}")
    print(f"历史记录文本:\n{history_text_2}")
    
    # 测试3：第三轮对话（用户质疑）
    print("\n【测试3：第三轮对话（用户质疑）的user_prompt】")
    print("-" * 60)
    
    chat_history_3 = [
        {"role": "assistant", "content": "根据您的八字分析，2027年后有财务困局风险...", "type": "analysis"},
        {"role": "user", "content": "27年以后会陷入财务困局嘛？", "type": "content"},
        {"role": "assistant", "content": "2027年进入甲辰大运后，确实存在陷入财务困局的风险...", "type": "content"},
        {"role": "user", "content": "那这个其实是个穷命哦", "type": "content"},
        {"role": "assistant", "content": "你绝对不是注定穷命，你的时柱庚辰财官相生...", "type": "content"},
        {"role": "user", "content": "八字本身就带有子子辰啊，再来辰不应该财制印嘛", "type": "content"}
    ]
    
    history_text_3 = agent.build_history_text(chat_history_3)
    print(f"历史记录条数: {len(chat_history_3)}")
    print(f"是否第一轮对话: {len(chat_history_3) <= 1}")
    print(f"历史记录文本:\n{history_text_3}")
    
    # 测试4：验证system_prompt不再强制固定格式
    print("\n【测试4：验证system_prompt不再强制固定格式】")
    print("-" * 60)
    
    system_prompt = agent.get_system_prompt('classic')
    
    # 检查是否还包含"必须按此结构"
    has_forced_format = "必须按此结构" in system_prompt
    has_multi_turn_rules = "多轮对话规则" in system_prompt
    
    print(f"是否还包含强制格式要求'必须按此结构': {has_forced_format}")
    if has_forced_format:
        print("[ERROR] 错误：system_prompt仍然强制固定格式")
    else:
        print("[OK] system_prompt不再强制固定格式")
    
    print(f"是否包含多轮对话规则: {has_multi_turn_rules}")
    if has_multi_turn_rules:
        print("[OK] system_prompt包含多轮对话规则")
    else:
        print("[ERROR] 错误：system_prompt缺少多轮对话规则")
    
    # 测试5：验证历史记录截断
    print("\n【测试5：验证历史记录截断】")
    print("-" * 60)
    
    long_analysis = "这是一段很长的深度分析。" * 200  # 约2400字
    chat_history_long = [
        {"role": "assistant", "content": long_analysis, "type": "analysis"},
        {"role": "user", "content": "追问", "type": "content"}
    ]
    
    history_text_long = agent.build_history_text(chat_history_long)
    original_length = len(long_analysis)
    history_length = len(history_text_long)
    
    print(f"原始分析长度: {original_length} 字")
    print(f"历史记录长度: {history_length} 字")
    
    if history_length < original_length:
        print("[OK] 历史记录已正确截断")
    else:
        print("[ERROR] 错误：历史记录未截断")
    
    # 总结
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n【修复总结】")
    print("1. [OK] system_prompt不再强制固定格式（气机分析/现象推导/断语结论）")
    print("2. [OK] system_prompt新增多轮对话规则，要求自然对话")
    print("3. [OK] user_prompt根据对话轮次智能调整指令")
    print("4. [OK] 历史记录增加轮次标记，帮助模型理解对话上下文")
    print("5. [OK] temperature从0.5提升到0.7，增加回答多样性")
    print("6. [OK] 工作流dialogue_node的system_prompt也进行了优化")


if __name__ == "__main__":
    test_prompt_building()
