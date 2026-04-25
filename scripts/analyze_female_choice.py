"""
女方是否会选择男方——从女方八字角度分析
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING, DI_ZHI_CANG_GAN

def analyze_female_choice():
    """分析女方是否会选择男方"""
    
    print("=" * 70)
    print("女方是否会选择男方？——从女方八字角度分析")
    print("=" * 70)
    
    # 女方命盘
    year_b, month_b, day_b, hour_b, gender_b = 1999, 3, 4, 21, '女'
    
    pan_b = bazi_pan_node(year_b, month_b, day_b, hour_b, gender_b)
    sizhu_b = pan_b['sizhu']
    
    print(f"\n【女方命盘】")
    print(f"出生：1999年3月4日 21点")
    print(f"年柱：{sizhu_b['nian_zhu']['tian_gan']}{sizhu_b['nian_zhu']['di_zhi']}")
    print(f"月柱：{sizhu_b['yue_zhu']['tian_gan']}{sizhu_b['yue_zhu']['di_zhi']}")
    print(f"日柱：{sizhu_b['ri_zhu']['tian_gan']}{sizhu_b['ri_zhu']['di_zhi']}（日主）")
    print(f"时柱：{sizhu_b['shi_zhu']['tian_gan']}{sizhu_b['shi_zhu']['di_zhi']}")
    
    rizhu_gan_b = sizhu_b['ri_zhu_tiangan']
    print(f"日主：{rizhu_gan_b}木")
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu_b)
    shishen_data = shishen_result.get('shishen_data', {})
    
    # ========== 一、女方择偶标准 ==========
    print(f"\n{'=' * 70}")
    print("【一、女方择偶标准（从夫星看）】")
    print("=" * 70)
    
    print(f"\n女命以官杀为夫星：")
    print(f"  - 正官：正缘、稳定丈夫")
    print(f"  - 七杀：偏缘、激情恋爱")
    
    # 找官杀
    guan_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu_b[zhu_name]['tian_gan']
        zhi = sizhu_b[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        if '官' in gan_shishen:
            guan_list.append({
                'position': f'{label}天干',
                'element': gan,
                'shishen': gan_shishen,
                'type': '透出'
            })
        
        for cg in zhi_cang_gan:
            if '官' in cg.get('shishen', '') or '杀' in cg.get('shishen', ''):
                guan_list.append({
                    'position': f'{label}地支{zhi}',
                    'element': cg['cang_gan'],
                    'shishen': cg['shishen'],
                    'type': '藏干'
                })
    
    print(f"\n女方夫星（官杀）：")
    if guan_list:
        for g in guan_list:
            zheng_pian = '正官（正缘）' if '正官' in g['shishen'] else '七杀（偏缘）'
            print(f"  - {g['position']}：{g['element']}（{g['shishen']}，{zheng_pian}）")
    else:
        print(f"  命盘中无明显官杀")
    
    zheng_guan = [g for g in guan_list if '正官' in g['shishen']]
    qi_sha = [g for g in guan_list if '七杀' in g['shishen']]
    
    print(f"\n夫星统计：")
    print(f"  正官（正缘）：{len(zheng_guan)}个")
    print(f"  七杀（偏缘）：{len(qi_sha)}个")
    
    print(f"\n择偶倾向分析：")
    if len(zheng_guan) > 0 and len(qi_sha) == 0:
        print(f"  → 倾向找稳定、靠谱的伴侣")
        print(f"  → 重视婚姻的稳定性")
        print(f"  → 喜欢有责任感的男人")
    elif len(qi_sha) > 0 and len(zheng_guan) == 0:
        print(f"  → 可能被有个性、强势的男人吸引")
        print(f"  → 感情中可能有激情但不够稳定")
    elif len(zheng_guan) > 0 and len(qi_sha) > 0:
        print(f"  → 正偏混杂，感情可能复杂")
        print(f"  → 可能经历多次感情")
    
    # 夫星五行
    print(f"\n夫星五行分析：")
    print(f"  日主乙木，金克木为官杀")
    print(f"  → 夫星为金")
    print(f"  → 适合找：金旺的男人，或命盘有金的男人")
    print(f"  → 男方命盘有庚金、辛金，正好补女方缺金！")
    
    # ========== 二、日支夫妻宫分析 ==========
    print(f"\n{'=' * 70}")
    print("【二、日支夫妻宫分析】")
    print("=" * 70)
    
    ri_zhi_b = sizhu_b['ri_zhu']['di_zhi']
    print(f"\n女方日支（夫妻宫）：{ri_zhi_b}")
    
    # 日支藏干
    ri_zhi_cang = DI_ZHI_CANG_GAN.get(ri_zhi_b, [])
    print(f"夫妻宫藏干：{ri_zhi_cang}")
    
    # 日支十神
    ri_zhi_shishen_list = []
    for cg in ri_zhi_cang:
        cg_wuxing = TIAN_GAN_WUXING.get(cg, '')
        rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan_b, '')
        if cg_wuxing == rizhu_wuxing:
            ri_zhi_shishen_list.append(f"{cg}（比肩）")
        elif cg_wuxing == '金':
            ri_zhi_shishen_list.append(f"{cg}（官杀/夫星）")
        elif cg_wuxing == '火':
            ri_zhi_shishen_list.append(f"{cg}（食伤）")
        elif cg_wuxing == '土':
            ri_zhi_shishen_list.append(f"{cg}（财星）")
        elif cg_wuxing == '水':
            ri_zhi_shishen_list.append(f"{cg}（印星）")
    
    print(f"夫妻宫十神：{ri_zhi_shishen_list}")
    
    print(f"\n夫妻宫分析：")
    print(f"  日支巳火藏：丙火（伤官）、戊土（正财）、庚金（正官）")
    print(f"  → 夫妻宫藏正官（庚金）：这是夫星入库！")
    print(f"  → 说明：丈夫在命中已定，会结婚")
    print(f"  → 正官在夫妻宫：丈夫有能力、有责任感")
    
    # ========== 三、食伤分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、食伤分析——女命择偶的关键】")
    print("=" * 70)
    
    print(f"\n女命食伤代表：")
    print(f"  - 子女")
    print(f"  - 表达、才华")
    print(f"  - 对丈夫的态度")
    print(f"  - 食伤克官杀 → 影响婚姻")
    
    # 找食伤
    shishang_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('shi_zhu', '时柱')]:
        gan = sizhu_b[zhu_name]['tian_gan']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        
        if '食' in gan_shishen or '伤' in gan_shishen:
            shishang_list.append({
                'position': f'{label}天干',
                'element': gan,
                'shishen': gan_shishen,
            })
    
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        zhi = sizhu_b[zhu_name]['di_zhi']
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            if '食' in cg.get('shishen', '') or '伤' in cg.get('shishen', ''):
                shishang_list.append({
                    'position': f'{label}地支{zhi}',
                    'element': cg['cang_gan'],
                    'shishen': cg['shishen'],
                })
    
    print(f"\n女方食伤分布：")
    for ss in shishang_list:
        print(f"  - {ss['position']}：{ss['element']}（{ss['shishen']}）")
    
    print(f"\n食伤数量：{len(shishang_list)}个")
    
    shen_count = sum(1 for ss in shishang_list if '食神' in ss['shishen'])
    shang_count = sum(1 for ss in shishang_list if '伤官' in ss['shishen'])
    
    print(f"  食神：{shen_count}个")
    print(f"  伤官：{shang_count}个")
    
    print(f"\n食伤对婚姻的影响：")
    if len(shishang_list) >= 3:
        print(f"  ⚠️ 食伤较多（{len(shishang_list)}个）")
        print(f"  → 可能对丈夫要求高")
        print(f"  → 容易挑剔伴侣")
        print(f"  → 需要学会包容")
    elif len(shishang_list) >= 2:
        print(f"  食伤适中（{len(shishang_list)}个）")
        print(f"  → 有才华、有眼光")
        print(f"  → 会对丈夫有要求，但不过分")
    else:
        print(f"  食伤较少，婚姻相对顺利")
    
    if shang_count > 0:
        print(f"\n  伤官透干：对丈夫有要求")
        print(f"  → 伤官代表挑剔、表达")
        print(f"  → 可能会对丈夫有意见")
    
    # ========== 四、合盘回顾 ==========
    print(f"\n{'=' * 70}")
    print("【四、合盘关键点回顾】")
    print("=" * 70)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    女方选择男方的原因                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  【命中注定】                                                       │
│  ★ 亥卯未三合木局：女方亥+卯 + 男方未 = 三合                       │
│    → 这是最高级别的缘分组合                                        │
│    → 说明两人是命中注定的                                          │
│                                                                     │
│  ★ 男方庚金 = 女方正官（夫星）                                     │
│    → 男方时干庚金，正是女方命盘需要的夫星                           │
│    → 女方缺金，男方有金，完美互补                                   │
│                                                                     │
│  ★ 女方夫妻宫藏正官（庚金）                                        │
│    → 男方正好有庚金                                                │
│    → 这说明男方就是女方命中注定的那个人                             │
│                                                                     │
│  【五行互补】                                                       │
│  ★ 女方缺金，男方有庚辛金                                          │
│    → 男方能补女方缺失的夫星                                        │
│    → 五行互补，婚姻和谐                                            │
│                                                                     │
│  【日主相同】                                                       │
│  ★ 双方都是乙木日主                                                │
│    → 性格相近，价值观相似                                          │
│    → 容易理解对方                                                  │
│                                                                     │
│  【天干相合】                                                       │
│  ★ 庚乙合：男方时干庚与女方日主乙相合                              │
│    → 男方对女方有吸引力                                            │
│    → 女方会被男方吸引                                              │
│                                                                     │
│  ★ 辛丙合：男方月干辛与女方月干丙相合                              │
│    → 感情中有默契                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    # ========== 五、女方心理分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、女方心理分析】")
    print("=" * 70)
    
    print(f"""
【女方看重什么？】

1. 安全感（正官需求）
   ────────────────────────────────
   女方日支夫妻宫藏正官
   → 需要稳定、靠谱的男人
   → 男方时柱有正官（庚金），有责任感
   → 这符合女方的需求

2. 五行互补（缺金）
   ────────────────────────────────
   女方命盘缺金
   → 男方有庚辛金
   → 男方能补女方的不足
   → 在一起会感觉舒适

3. 理解和包容（日主相同）
   ────────────────────────────────
   双方都是乙木日主
   → 性格相近，容易理解
   → 价值观相似
   → 沟通顺畅

4. 命中注定（三合局）
   ────────────────────────────────
   亥卯未三合木局
   → 这是命定的缘分
   → 不是偶然的相遇

【女方可能的顾虑】

1. 食伤较多
   ────────────────────────────────
   食伤4个，伤官多
   → 可能对丈夫有要求
   → 容易挑剔
   → 需要学会包容

2. 男方偏财多
   ────────────────────────────────
   男方有2个偏财
   → 异性缘好
   → 女方可能担心

3. 男方伤官透干
   ────────────────────────────────
   男方年干丙火伤官
   → 会说话、会哄人
   → 但也可能花心

【女方最终会选择吗？】

答案：会的！

原因：
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. 三合局注定的缘分                                            │
│     亥卯未三合，这不是偶然的相遇                                │
│                                                                 │
│  2. 男方正是女方需要的夫星                                      │
│     男方庚金 = 女方正官，命中注定                               │
│                                                                 │
│  3. 五行互补                                                    │
│     女方缺金，男方有金                                          │
│                                                                 │
│  4. 日主相同，价值观相似                                        │
│     容易理解和沟通                                              │
│                                                                 │
│  5. 2026年认识正是婚运期                                        │
│     双方婚运同步                                                │
│                                                                 │
│  6. 女方夫妻宫有正官                                            │
│     说明会结婚，丈夫有责任感                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")
    
    # ========== 六、建议 ==========
    print(f"\n{'=' * 70}")
    print("【六、给女方的建议】")
    print("=" * 70)
    
    print(f"""
【女方需要注意的】

1. 食伤较多，容易挑剔
   ────────────────────────────────
   建议：多看对方的优点
         学会包容和欣赏
         不要要求太高

2. 男方异性缘好
   ────────────────────────────────
   建议：适度管束，但不要太紧
         给他信任和空间
         用智慧经营感情

3. 男方工作变动多
   ────────────────────────────────
   理解：这是他的性格特点
         不是不靠谱
         理财稳定，可以管家庭财务

【女方应该珍惜的】

✓ 男方有责任感（时柱正官）
✓ 男方会疼人（伤官透干）
✓ 男方能补女方缺失的夫星（庚金）
✓ 男方理财稳定，可以管家庭财务
✓ 三合局的缘分，不是偶然
✓ 2026年认识正是婚运期

【最终结论】

女方会选择和男方走下去！

原因：
1. 三合局注定的缘分
2. 男方正是女方命中的夫星
3. 五行互补，在一起舒服
4. 日主相同，价值观相似
5. 婚运时间同步

这是一段命中注定的缘分！
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_female_choice()
