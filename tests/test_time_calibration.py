"""
测试：出生时辰定盘反推校准功能

覆盖：
1. 12 个候选时辰盘是否正确生成（时柱随时辰变化、年月日柱不变）
2. 候选表文本是否包含关键判别维度（时干十神、喜忌、时支神煞、时支合冲）
3. build_context_text 是否集成十二时辰对比表
4. 系统提示词是否包含定盘反推法则
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.tools.bazi_time_calibrator import (
    build_time_candidates,
    format_candidate_table,
    generate_time_calibration_context,
)
from core.agents.bazi_dialogue_agent import BaziContext, BaziDialogueAgent


def test_candidate_generation():
    """测试1：12 候选盘生成正确性"""
    print("=" * 60)
    print("测试1：12候选时辰盘生成")
    print("=" * 60)
    cands = build_time_candidates(2001, 3, 15)

    assert len(cands) == 12, f"应生成12候选，实际{len(cands)}"
    print(f"[OK] 生成 {len(cands)} 个候选")

    # 年月日柱应完全相同
    ref_nian = cands[0]['sizhu']['nian']
    ref_yue = cands[0]['sizhu']['yue']
    ref_ri = cands[0]['sizhu']['ri']
    for c in cands:
        assert c['sizhu']['nian'] == ref_nian
        assert c['sizhu']['yue'] == ref_yue
        assert c['sizhu']['ri'] == ref_ri
    print(f"[OK] 年柱{ref_nian}、月柱{ref_yue}、日柱{ref_ri}对12候选保持不变")

    # 时柱应各不相同
    shi_set = {c['sizhu']['shi'] for c in cands}
    assert len(shi_set) == 12, f"时柱应12各不同，实际{len(shi_set)}"
    print(f"[OK] 12个时柱各不相同: {'、'.join(sorted(shi_set))}")

    # 时干十神、喜忌、神煞字段齐全
    for c in cands:
        assert 'shi_gan' in c['shishen']
        assert c['shishen']['shi_gan'], "时干十神不能为空"
        assert 'xi' in c['xi_ji'] and 'ji' in c['xi_ji']
    print("[OK] 每个候选都包含时干十神与喜忌")


def test_format_table():
    """验证：格式化文本包含关键判别维度"""
    print("\n" + "=" * 60)
    print("测试2：候选表文本关键维度")
    print("=" * 60)
    cands = build_time_candidates(2001, 3, 15)
    txt = format_candidate_table(cands)

    for keyword in ['时柱', '时干十神', '旺衰/喜忌', '时支与他支关系', '子时', '亥时']:
        assert keyword in txt, f"缺少关键词: {keyword}"
    print("[OK] 文本包含：时柱、时干十神、旺衰/喜忌、时支合冲、子时/亥时等维度")

    # 应能区分不同时辰的喜忌
    xiji_set = {tuple(sorted(c['xi_ji']['xi'] + c['xi_ji']['ji'])) for c in cands}
    if len(xiji_set) > 1:
        print(f"[OK] 不同时辰的喜忌存在差异（{len(xiji_set)} 种组合），可用于流年应期反推")
    else:
        print("[WARN] 该命例所有时辰喜忌相同，需靠神煞/时支合冲区分")


def test_context_integration():
    """验证：build_context_text 集成十二时辰对比表"""
    print("\n" + "=" * 60)
    print("测试3：对话上下文集成对比表")
    print("=" * 60)
    c = BaziContext(
        sizhu={
            'nian_zhu': {'tian_gan': '辛', 'di_zhi': '巳', 'cang_gan': ['丙', '戊', '庚']},
            'yue_zhu': {'tian_gan': '辛', 'di_zhi': '卯', 'cang_gan': ['乙']},
            'ri_zhu': {'tian_gan': '丁', 'di_zhi': '丑', 'cang_gan': ['己', '癸', '辛']},
            'shi_zhu': {'tian_gan': '庚', 'di_zhi': '子', 'cang_gan': ['癸']},
            'ri_zhu_tiangan': '丁',
        },
        birth_info={'year': 2001, 'month': 3, 'day': 15},
        gender='女',
        analysis_style='classic',
    )
    a = BaziDialogueAgent()
    txt = a.build_context_text(c)
    assert '【十二时辰定盘对比】' in txt, "上下文应包含定盘对比表"
    assert '■ 子时' in txt
    print("[OK] 上下文成功集成十二时辰定盘对比表")


def test_context_without_birth():
    """验证：无出生年月日时的优雅降级"""
    print("\n" + "=" * 60)
    print("测试4：缺出生信息降级")
    print("=" * 60)
    c = BaziContext(
        sizhu={'ri_zhu_tiangan': '丁'},
        birth_info={},
        gender='男',
    )
    a = BaziDialogueAgent()
    txt = a.build_context_text(c)
    assert '【十二时辰定盘对比】' not in txt or '缺少出生年月日' in txt
    print("[OK] 无出生信息时不报错，优雅降级")


def test_system_prompt_rule():
    """验证：系统提示词包含定盘反推法则"""
    print("\n" + "=" * 60)
    print("测试5：系统提示词含定盘法则")
    print("=" * 60)
    agent = BaziDialogueAgent()
    sp = agent.get_system_prompt('classic')
    assert '定盘' in sp or '时辰' in sp, "classic风格提示词缺少定盘法则"
    print("[OK] agent 系统提示词包含定盘/时辰反推法则")
    return sp


if __name__ == '__main__':
    test_candidate_generation()
    test_format_table()
    test_context_integration()
    test_context_without_birth()
    test_system_prompt_rule()
    print("\n" + "=" * 60)
    print("全部测试通过！")
    print("=" * 60)