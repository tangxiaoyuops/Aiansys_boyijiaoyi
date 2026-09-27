"""
八字出生时辰定盘反推校准器

核心思路：已知命主的"年月日柱"（时辰待定或无把握），遍历 12 个候选时辰，
为每个时辰生成完整的"四柱 + 五行 + 十神 + 喜忌 + 时支神煞"盘，
并输出为结构化的横向对比，供 LLM 对照命主的"已知事实"反向推断真实时辰。

传统"定时辰/定盘"的核心依据（本模块提供数据驱动支撑）：
1. 时干十神不同 = 用神喜忌方向不同
2. 时支与年日月支的合冲 = 家庭、六亲、健康特征的差异
3. 喜忌受时辰影响，故不同时辰在同一流年的"应事"不同 —— 反推的关键锚点
4. 神煞（将星/羊刃/桃花/驿马等）常落于时支，直接影响外貌、性格、六亲、际遇
"""
from typing import Dict, List, Any, Optional
import logging

from core.tools.bazi_calculator import (
    calculate_sizhu,
    calculate_wuxing,
    calculate_shishen,
    calculate_wuxing_xi_ji,
    calculate_shensha,
    calculate_zhi_relations,
    calculate_gan_relations,
)

logger = logging.getLogger(__name__)

# 12 个时辰的代表起点小时 + 显示名
SHI_CHEN_HOURS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
SHI_CHEN_NAMES = {
    0: '子时(23-1)', 2: '丑时(1-3)', 4: '寅时(3-5)', 6: '卯时(5-7)',
    8: '辰时(7-9)', 10: '巳时(9-11)', 12: '午时(11-13)', 14: '未时(13-15)',
    16: '申时(15-17)', 18: '酉时(17-19)', 20: '戌时(19-21)', 22: '亥时(21-23)',
}


def _extract_shi_zhi_relation(zhi_relations: Dict) -> Dict[str, List[str]]:
    """提取与时支相关的六合/六冲/三合描述，用于判别六亲健康与应期。"""
    out: Dict[str, List[str]] = {'六合': [], '六冲': [], '三合': []}
    # 六合 & 六冲：仅保留涉及"时支"的组合（六亲/健康/应期判别关键）
    for item in zhi_relations.get('liu_he', []):
        zhunames = {item.get('zhu1'), item.get('zhu2')}
        if 'shi_zhu' in zhunames:
            out['六合'].append(item.get('desc', ''))
    for item in zhi_relations.get('liu_chong', []):
        zhunames = {item.get('zhu1'), item.get('zhu2')}
        if 'shi_zhu' in zhunames:
            out['六冲'].append(item.get('desc', ''))
    for item in zhi_relations.get('san_he', []):
        # 三合描述不区分位置，全量列出（时支参与三合也会被反推出来）
        out['三合'].append(item.get('desc', ''))
    return out


def build_time_candidate(
    year: int,
    month: int,
    day: int,
    hour: int,
) -> Optional[Dict]:
    """
    构建单个时辰的完整候选盘。

    Args:
        year/month/day: 公历出生年月日
        hour: 该时辰的代表时刻（0-23，见 SHI_CHEN_HOURS）

    Returns:
        候选字典；计算失败返回 None
    """
    try:
        sizhu = calculate_sizhu(year, month, day, hour)
    except Exception as e:
        logger.warning(f"计算四柱失败 hour={hour}: {e}", exc_info=True)
        return None

    rizhu = sizhu.get('ri_zhu_tiangan', '')
    if not rizhu:
        return None

    try:
        wuxing = calculate_wuxing(sizhu)
        shishen = calculate_shishen(sizhu, rizhu)
        xiji = calculate_wuxing_xi_ji(sizhu, wuxing)
        shensha = calculate_shensha(sizhu)
        zhi_relations = calculate_zhi_relations(sizhu)
        gan_relations = calculate_gan_relations(sizhu)
    except Exception as e:
        logger.warning(f"计算候选盘衍生数据失败 hour={hour}: {e}", exc_info=True)
        return None

    # 时柱十神
    shi_ten = shishen.get('shi_zhu', {})
    shi_cang = [
        {"gan": c.get('cang_gan'), "shen": c.get('shishen')}
        for c in shi_ten.get('zhi_cang_gan_shishen', [])
    ]

    return {
        "hour_code": hour,
        "shi_chen": SHI_CHEN_NAMES.get(hour, f"{hour}时"),
        "sizhu": {
            "nian": f"{sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}",
            "yue": f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}",
            "ri": f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}",
            "shi": f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}",
            "shi_gan": sizhu['shi_zhu']['tian_gan'],
            "shi_zhi": sizhu['shi_zhu']['di_zhi'],
        },
        "wuxing": wuxing.get('wuxing_count_detail', {}),
        "rizhu_wuxing": wuxing.get('rizhu_wuxing', ''),
        "shishen": {
            "shi_gan": shi_ten.get('gan_shishen', ''),
            "shi_zhi": shi_ten.get('zhi_shishen', ''),
            "shi_cang": shi_cang,
        },
        "xi_ji": {
            "is_rizhu_qiang": xiji.get('is_rizhu_qiang', False),
            "xi": xiji.get('xi_wuxing', []),
            "ji": xiji.get('ji_wuxing', []),
        },
        "shensha_in_shi": [
            {"name": s.get('name'), "zhi": s.get('zhi')}
            for s in shensha.get('shensha_list', [])
            if s.get('position') == 'shi_zhu'
        ],
        "shi_zhi_relation": _extract_shi_zhi_relation(zhi_relations),
        "gan_relation": {
            "he": [r['desc'] for r in gan_relations.get('tian_gan_he', [])],
            "chong": [r['desc'] for r in gan_relations.get('tian_gan_chong', [])],
        },
    }


def build_time_candidates(
    year: int,
    month: int,
    day: int,
) -> List[Dict[str, Any]]:
    """构建 12 个候选时辰盘（有序：从子时到亥时）。"""
    candidates = []
    for hour in SHI_CHEN_HOURS:
        cand = build_time_candidate(year, month, day, hour)
        if cand:
            candidates.append(cand)
    return candidates


def format_candidate_table(candidates: List[Dict[str, Any]]) -> str:
    """
    将 12 个候选时辰格式化为 LLM 易读的对比表。
    每个候选独立成段，突出"时柱、时干十神、喜忌、时支神煞、时支合冲"这几个判别维度。
    """
    if not candidates:
        return "（无法计算候选时辰：请核对出生日期）"

    lines = []
    first = candidates[0]
    # 年柱、日柱与时辰无关；但交节当天，不同时辰的月柱可能不同（强判别信号）
    nian_yue_set = {}  # 月柱 -> 时辰列表
    for c in candidates:
        nian_yue_set.setdefault((c['sizhu']['nian'], c['sizhu']['yue']), []).append(c['shi_chen'])
    month_varies = len(nian_yue_set) > 1

    lines.append(
        f"固定两柱（与时辰无关）：年柱 {first['sizhu']['nian']}，"
        f"日柱 {first['sizhu']['ri']}，日主为{first['rizhu_wuxing']}五行。"
    )
    if month_varies:
        lines.append(
            f"⚠️ 注：该日处于交节前后，不同时辰的【月柱】不同，这是极强的定盘信号——"
            f"{ '；'.join(f'{v}为{n}{y}月' for (n, y), v in nian_yue_set.items()) }。"
        )
    else:
        lines.append(f"月柱 {first['sizhu']['yue']}（12 个时辰均相同）")
    lines.append("下列 12 个候选，主要差异在【时柱】及由其引起的【五行·十神·喜忌·神煞·时支关系】：\n")

    for cand in candidates:
        lines.append(f"■ {cand['shi_chen']} —— 时柱 {cand['sizhu']['shi']}（月柱 {cand['sizhu']['yue']}）")
        lines.append(f"   - 时干十神：{cand['shishen']['shi_gan']}；时支本气十神：{cand['shishen']['shi_zhi']}")
        if cand['shishen']['shi_cang']:
            cang_str = "、".join(f"{c['gan']}({c['shen']})" for c in cand['shishen']['shi_cang'])
            lines.append(f"   - 时支藏干十神：{cang_str}")
        # 五行明细
        wx = cand['wuxing']
        lines.append(
            f"   - 合盘五行（含藏干）：金{wx.get('金', 0)} 木{wx.get('木', 0)} "
            f"水{wx.get('水', 0)} 火{wx.get('火', 0)} 土{wx.get('土', 0)}"
        )
        xj = cand['xi_ji']
        strong = "身强" if xj['is_rizhu_qiang'] else "身弱"
        lines.append(
            f"   - 旺衰/喜忌：{strong}；喜用[{'、'.join(xj['xi']) or '无'}]，忌神[{'、'.join(xj['ji']) or '无'}]"
        )
        # 时支神煞
        if cand['shensha_in_shi']:
            ss_str = "、".join(f"{s['name']}" for s in cand['shensha_in_shi'])
            lines.append(f"   - 时支神煞：{ss_str}")
        # 时支合冲
        rel = cand['shi_zhi_relation']
        rel_parts = []
        if rel['六冲']:
            rel_parts.append("六冲:" + "、".join(rel['六冲']))
        if rel['六合']:
            rel_parts.append("六合:" + "、".join(rel['六合']))
        if rel['三合']:
            rel_parts.append("三合:" + "、".join(rel['三合']))
        if rel_parts:
            lines.append(f"   - 时支与他支关系：{'；'.join(rel_parts)}")

    return "\n".join(lines)


def generate_time_calibration_context(
    year: int,
    month: int,
    day: int,
) -> str:
    """
    对外主入口：给定出生年月日，返回用于定盘反推的完整上下文文本，
    可直接拼接进 build_context_text。
    """
    candidates = build_time_candidates(year, month, day)
    return format_candidate_table(candidates)