# -*- coding: utf-8 -*-
"""
女生身体健康分析
出生：1999年3月4日 21点（亥时）
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING, DI_ZHI_CANG_GAN

def analyze_female_health():
    """分析女生身体健康"""
    
    print("=" * 70)
    print("女生身体健康分析")
    print("出生：1999年3月4日 21点（亥时）")
    print("=" * 70)
    
    year, month, day, hour, gender = 1999, 3, 4, 21, '女'
    
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    sizhu = pan_result['sizhu']
    wuxing_result = bazi_wuxing_node(sizhu)
    shishen_result = bazi_shishen_node(sizhu)
    
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    
    # 五行统计
    wuxing_data = wuxing_result.get('wuxing_data', {})
    wuxing_count = wuxing_data.get('wuxing_count', {})
    
    print(f"\n{'=' * 70}")
    print("【一、五行分布】")
    print("=" * 70)
    
    for wx in ['木', '火', '土', '金', '水']:
        count = wuxing_count.get(wx, 0)
        status = "旺" if count >= 3 else ("正常" if count >= 1 else "缺")
        print(f"{wx}：{count}个 - {status}")
    
    # 身体健康分析
    print(f"\n{'=' * 70}")
    print("【二、身体健康分析】")
    print("=" * 70)
    
    # 日主分析
    print(f"\n日主：{rizhu_gan}木")
    print(f"\n【日主强弱】")
    
    # 木的强弱
    wood_count = wuxing_count.get('木', 0)
    water_count = wuxing_count.get('水', 0)
    
    print(f"木（日主）：{wood_count}个")
    print(f"水（生木）：{water_count}个")
    
    # 分析
    print(f"\n{'=' * 70}")
    print("【三、健康问题分析】")
    print("=" * 70)
    
    # 1. 五行缺失的影响
    print(f"\n【五行缺失对身体的影响】")
    
    jin_count = wuxing_count.get('金', 0)
    if jin_count == 0:
        print(f"\n★ 缺金（0个）")
        print(f"  金主：肺、呼吸系统、皮肤、大肠")
        print(f"  影响：")
        print(f"  - 肺气不足，容易气短、乏力")
        print(f"  - 呼吸系统较弱，容易感冒")
        print(f"  - 皮肤可能比较敏感")
        print(f"  - 容易过敏")
        print(f"  → 缺金的人容易疲劳、没精神")
    
    # 2. 木火旺的影响
    huo_count = wuxing_count.get('火', 0)
    print(f"\n★ 木旺（{wood_count}个）+ 火旺（{huo_count}个）")
    print(f"  木主：肝、胆、眼睛、筋骨")
    print(f"  火主：心脏、血液、小肠、眼睛")
    print(f"  影响：")
    print(f"  - 肝火可能旺，容易上火")
    print(f"  - 眼睛可能容易疲劳")
    print(f"  - 情绪波动可能大")
    print(f"  - 睡眠质量可能不好")
    
    # 3. 水的影响
    print(f"\n★ 水（{water_count}个）")
    print(f"  水主：肾、膀胱、耳朵、骨骼")
    if water_count >= 2:
        print(f"  水不算缺，肾气还可以")
    else:
        print(f"  水偏弱，注意肾脏保养")
    
    # 4. 亥时出生的影响
    print(f"\n{'=' * 70}")
    print("【四、亥时出生的影响】")
    print("=" * 70)
    
    print(f"\n出生时间：亥时（21:00-23:00）")
    print(f"\n亥时特点：")
    print(f"  • 亥属水，主收藏")
    print(f"  • 亥时出生的人：")
    print(f"  - 晚上精神，白天容易困")
    print(f"  - 作息可能不规律")
    print(f"  - 容易熬夜")
    print(f"  - 生物钟可能偏晚")
    print(f"\n这是亥时出生的常见特点，")
    print(f"不是身体虚弱，是作息规律问题。")
    
    # 5. 食伤旺的影响
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n{'=' * 70}")
    print("【五、食伤旺对健康的影响】")
    print("=" * 70)
    
    # 统计食伤
    shishen_count = {}
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if gan_shishen:
            shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
        
        zhi_cang_gan_shishen = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan_shishen:
            shishen_name = cg.get('shishen', '')
            if shishen_name:
                shishen_count[shishen_name] = shishen_count.get(shishen_name, 0) + 1
    
    shishang_count = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
    
    print(f"\n食伤总数：{shishang_count}个")
    print(f"  食神：{shishen_count.get('食神', 0)}个")
    print(f"  伤官：{shishen_count.get('伤官', 0)}个")
    
    if shishang_count >= 3:
        print(f"\n★ 食伤旺（{shishang_count}个）")
        print(f"  食伤主：表达、发泄、消耗")
        print(f"  对健康的影响：")
        print(f"  - 精力消耗大，容易累")
        print(f"  - 思维活跃，睡眠可能不好")
        print(f"  - 情绪波动大，影响身体")
        print(f"  - 爱玩、爱热闹，消耗精力")
        print(f"\n  → 食伤旺的人，精力消耗快，容易疲劳")
    
    # 6. 结论
    print(f"\n{'=' * 70}")
    print("【六、总结】")
    print("=" * 70)
    
    print(f"""
从八字分析：

【容易犯困、疲劳的原因】

1. 缺金（0个）
   ─────────────────────────────────────────────
   • 金主肺，肺主气
   • 缺金 = 肺气不足
   • 肺气不足 = 容易气短、乏力、没精神
   • 这是体质问题，不是病

2. 食伤旺（{shishang_count}个）
   ─────────────────────────────────────────────
   • 食伤代表消耗、发泄
   • 食伤旺 = 精力消耗大
   • 爱玩、爱热闹、晚上精神
   • 消耗快，恢复慢

3. 亥时出生
   ─────────────────────────────────────────────
   • 亥时（21-23点）属水
   • 晚上精神，白天困
   • 作息可能不规律
   • 经常熬夜，白天补觉

4. 木火旺
   ─────────────────────────────────────────────
   • 木旺 = 肝火可能旺
   • 火旺 = 容易上火
   • 可能睡眠质量不好
   • 睡不好，白天就容易困

【结论】

她不是"身体虚弱"，而是：

  1. 体质问题
     • 缺金，肺气不足
     • 容易疲劳、没精神
     • 这是先天体质

  2. 作息问题
     • 亥时生，夜猫子
     • 晚上精神，白天困
     • 作息不规律

  3. 消耗问题
     • 食伤旺，消耗大
     • 爱玩、爱热闹
     • 精力消耗快

【建议】

  1. 补金
     • 多吃白色食物（银耳、百合、白萝卜）
     • 适当运动，增强肺活量
     • 注意呼吸系统保养

  2. 调整作息
     • 尽量早睡
     • 白天多晒太阳
     • 规律作息

  3. 节制消耗
     • 不要玩太晚
     • 注意休息
     • 不要过度消耗精力

  4. 养肝
     • 少熬夜（最重要）
     • 少生气
     • 多喝水

她不是病态的虚弱，是体质+作息导致的容易疲劳。
调整作息，注意保养，可以改善。
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_female_health()
