"""
男方感情运势分析——未来是否有更合适的？
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING

# 夫妻星查法（男命以财星为妻星）
# 正财：阳土戊、阴土己
# 偏财：阴土己、阳土戊

def analyze_male_marriage_future():
    """分析男方未来婚姻运势"""
    
    print("=" * 70)
    print("男方感情运势分析——未来是否有更合适的？")
    print("出生：1997年1月3日 早上8点")
    print("=" * 70)
    
    year, month, day, hour, gender = 1997, 1, 3, 8, '男'
    
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    sizhu = pan_result['sizhu']
    
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【一、八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}木")
    
    nian_zhi = nian_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    all_zhi = [nian_zhu['di_zhi'], yue_zhu['di_zhi'], ri_zhu['di_zhi'], shi_zhu['di_zhi']]
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    # ========== 妻星分析 ==========
    print(f"\n{'=' * 70}")
    print("【二、妻星分析（男命以财星为妻）】")
    print("=" * 70)
    
    # 找财星
    cai_list = []
    zheng_cai_list = []
    pian_cai_list = []
    
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        if '财' in gan_shishen:
            cai_list.append({'position': f'{label}天干', 'element': gan, 'shishen': gan_shishen, 'type': '透出'})
            if '正财' in gan_shishen:
                zheng_cai_list.append({'position': f'{label}天干', 'element': gan})
            else:
                pian_cai_list.append({'position': f'{label}天干', 'element': gan})
        
        for cg in zhi_cang_gan:
            if '财' in cg.get('shishen', ''):
                cai_list.append({'position': f'{label}地支{zhi}', 'element': cg['cang_gan'], 'shishen': cg['shishen'], 'type': '藏干'})
                if '正财' in cg['shishen']:
                    zheng_cai_list.append({'position': f'{label}地支{zhi}', 'element': cg['cang_gan']})
                else:
                    pian_cai_list.append({'position': f'{label}地支{zhi}', 'element': cg['cang_gan']})
    
    print(f"\n妻星（财星）分布：")
    for cai in cai_list:
        zheng_pian = '正财（正妻）' if '正财' in cai['shishen'] else '偏财（偏缘）'
        print(f"  - {cai['position']}：{cai['element']}（{cai['shishen']}，{zheng_pian}）")
    
    print(f"\n妻星统计：")
    print(f"  正财（正妻）：{len(zheng_cai_list)}个")
    print(f"  偏财（偏缘）：{len(pian_cai_list)}个")
    print(f"  妻星总数：{len(cai_list)}个")
    
    print(f"\n【妻星分析】")
    
    # 正财在时柱
    zheng_cai_shizhu = [c for c in zheng_cai_list if '时' in c['position']]
    if zheng_cai_shizhu:
        print(f"\n★ 正财在时柱")
        print(f"  正财代表正妻，在时柱说明：")
        print(f"  → 妻子在命盘中")
        print(f"  → 重视婚姻")
        print(f"  → 晚婚可能更合适")
        print(f"  → 妻子可能是后来认识的")
    
    # 偏财位置
    if pian_cai_list:
        print(f"\n★ 偏财{len(pian_cai_list)}个")
        print(f"  偏财代表偏缘、桃花")
        print(f"  → 异性缘好")
        print(f"  → 可能有多次感情")
        print(f"  → 但有正财，最终会稳定")
    
    print(f"\n【妻星结论】")
    print(f"  妻星总数{len(cai_list)}个，说明妻缘不缺")
    print(f"  正财{len(zheng_cai_list)}个，有正妻缘")
    print(f"  偏财{len(pian_cai_list)}个，感情经历可能较丰富")
    
    # ========== 夫妻宫分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、夫妻宫分析】")
    print("=" * 70)
    
    print(f"\n日支（夫妻宫）：{ri_zhi}")
    
    # 夫妻宫藏干
    from core.tools.bazi_calculator import DI_ZHI_CANG_GAN
    ri_zhi_cang = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    
    print(f"夫妻宫藏干：{ri_zhi_cang}")
    
    # 分析夫妻宫
    print(f"\n【夫妻宫分析】")
    
    # 未土藏己土（偏财）、丁火（食神）、乙木（比肩）
    if ri_zhi == '未':
        print(f"  未土藏：己土（偏财）、丁火（食神）、乙木（比肩）")
        print(f"  → 夫妻宫藏偏财：妻子有魅力")
        print(f"  → 夫妻宫藏食神：妻子温柔、会照顾人")
        print(f"  → 夫妻宫藏比肩：可能有小争执")
        print(f"  → 整体：夫妻宫不错，妻子条件好")
    
    # 大运分析
    print(f"\n{'=' * 70}")
    print("【四、大运婚运分析】")
    print("=" * 70)
    
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
    print(f"\n大运排列：")
    
    # 计算十神
    def get_shishen(rizhu_gan, target_gan=None, target_zhi=None):
        rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
        WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
        TIAN_GAN_YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
        
        if target_gan:
            target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
            target_yinyang = TIAN_GAN_YINYANG.get(target_gan, '')
            
            if target_wuxing == rizhu_wuxing:
                return '比肩' if target_yinyang == TIAN_GAN_YINYANG.get(rizhu_gan, '') else '劫财'
            elif WUXING_SHENG.get(rizhu_wuxing) == target_wuxing:
                return '食神' if target_yinyang == TIAN_GAN_YINYANG.get(rizhu_gan, '') else '伤官'
            elif WUXING_SHENG.get(target_wuxing) == rizhu_wuxing:
                return '偏印' if target_yinyang == TIAN_GAN_YINYANG.get(rizhu_gan, '') else '正印'
            elif WUXING_KE.get(rizhu_wuxing) == target_wuxing:
                return '偏财' if target_yinyang == TIAN_GAN_YINYANG.get(rizhu_gan, '') else '正财'
            elif WUXING_KE.get(target_wuxing) == rizhu_wuxing:
                return '七杀' if target_yinyang == TIAN_GAN_YINYANG.get(rizhu_gan, '') else '正官'
        return ''
    
    hunyun_dayun = []
    
    for i, dy in enumerate(dayun_list):
        dy_gan = dy['gan']
        dy_zhi = dy['zhi']
        dy_gan_shishen = get_shishen(rizhu_gan, dy_gan)
        dy_zhi_shishen = get_shishen(rizhu_gan, None, dy_zhi)
        
        is_cai = '财' in dy_gan_shishen or '财' in dy_zhi_shishen
        
        marker = " ★ 财运（婚运）" if is_cai else ""
        
        print(f"\n第{i+1}步：{dy_gan}{dy_zhi}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）{marker}")
        print(f"   天干{dy_gan}：{dy_gan_shishen}")
        print(f"   地支{dy_zhi}：{dy_zhi_shishen}")
        
        if is_cai:
            hunyun_dayun.append({
                'step': i+1,
                'gan_zhi': f"{dy_gan}{dy_zhi}",
                'start_age': dy['start_age'],
                'end_age': dy['end_age'],
                'start_year': dy['start_year'],
                'end_year': dy['end_year'],
                'gan_shishen': dy_gan_shishen,
                'zhi_shishen': dy_zhi_shishen
            })
    
    print(f"\n【婚运大运】")
    if hunyun_dayun:
        for dy in hunyun_dayun:
            print(f"\n  第{dy['step']}步：{dy['gan_zhi']}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）")
            print(f"  天干：{dy['gan_shishen']}")
            print(f"  地支：{dy['zhi_shishen']}")
    else:
        print(f"\n  暂无明显婚运大运")
    
    # ========== 流年分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、流年婚运分析（2024-2035年）】")
    print("=" * 70)
    
    print(f"\n流年婚运分析：")
    
    liunian_hunyun = []
    
    for year_offset in range(2024 - 1997, 2036 - 1997):
        target_year = 1997 + year_offset
        age = year_offset
        
        base_year = 1984
        gan_index = (target_year - base_year) % 10
        zhi_index = (target_year - base_year) % 12
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        liunian_gan_shishen = get_shishen(rizhu_gan, liunian_gan)
        liunian_zhi_shishen = get_shishen(rizhu_gan, None, liunian_zhi)
        
        is_hunyun = False
        reasons = []
        
        # 财星年
        if '财' in liunian_gan_shishen:
            is_hunyun = True
            reasons.append(f"天干{liunian_gan}为{liunian_gan_shishen}（妻星）")
        if '财' in liunian_zhi_shishen:
            is_hunyun = True
            reasons.append(f"地支{liunian_zhi}为{liunian_zhi_shishen}（妻星）")
        
        # 与日支相合
        DI_ZHI_LIU_HE = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯', '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
        if DI_ZHI_LIU_HE.get(ri_zhi) == liunian_zhi:
            is_hunyun = True
            reasons.append(f"流年{liunian_zhi}与日支{ri_zhi}相合（婚动）")
        
        if is_hunyun:
            liunian_hunyun.append({
                'year': target_year,
                'age': age,
                'gan_zhi': f"{liunian_gan}{liunian_zhi}",
                'reasons': reasons
            })
    
    if liunian_hunyun:
        for ln in liunian_hunyun:
            print(f"\n  {ln['year']}年（{ln['age']}岁）：{ln['gan_zhi']}年 ★ 婚运 ★")
            for r in ln['reasons']:
                print(f"    - {r}")
    else:
        print(f"\n  暂无明显婚运流年")
    
    # ========== 离开这个女生的分析 ==========
    print(f"\n{'=' * 70}")
    print("【六、如果离开这个女生，还有更合适的吗？】")
    print("=" * 70)
    
    print(f"""
从男方八字分析：

【一、男方婚姻运势】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 妻星情况：
   - 正财1个（时支辰）：有正妻缘
   - 偏财2个（月支丑、日支未）：异性缘好
   - 妻星总数3个：妻缘不缺

2. 夫妻宫情况：
   - 日支未土藏偏财、食神、比肩
   - 夫妻宫条件不错
   - 妻子条件好

3. 大运财运：
   - 当前己卯运（20-30岁）：偏财运
   - 2027年后庚辰运（30-40岁）：正财运
   - 都在财运，婚运不断

4. 流年婚运：
   - 2026年：午未合（婚动）
   - 2028年：戊申年（正财年）
   - 2029年：己酉年（偏财年）
   - 2030年：庚戌年（正财年）
   - 婚运持续到30多岁

【二、离开后有更合适的吗？】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

答案：会有！

原因：

1. 妻星不缺
   ─────────────────────────────────────────────
   男方有3个财星（妻星）
   → 说明命中有妻缘
   → 不止一次感情机会
   → 离开后还会有新的缘分

2. 正财在时柱
   ─────────────────────────────────────────────
   正财在时柱辰土
   → 时柱代表晚运
   → 正妻可能晚一点出现
   → 最终会遇到正缘

3. 大运持续财运
   ─────────────────────────────────────────────
   2017-2027年：己卯运（偏财运）
   2027-2037年：庚辰运（正财运）
   → 20年财运
   → 婚运持续
   → 不缺感情机会

4. 流年婚运多
   ─────────────────────────────────────────────
   2026年：婚动年
   2028年：正财年
   2029年：偏财年
   2030年：正财年
   → 每隔几年就有婚运
   → 不止一次机会

【三、但是！需要考虑的问题】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 偏财多
   ─────────────────────────────────────────────
   男方有2个偏财
   → 感情经历可能较多
   → 可能有几次恋爱
   → 但最终会稳定

2. 伤官透干
   ─────────────────────────────────────────────
   年干丙火伤官
   → 追求变化
   → 不喜欢稳定
   → 可能有几次感情变化

3. 七杀透干
   ─────────────────────────────────────────────
   月干辛金七杀
   → 事业心强
   → 可能因为事业忽略感情

【四、什么样的女生更适合？】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

从男方八字看，适合的女生类型：

1. 五行互补：
   ─────────────────────────────────────────────
   男方缺火、木弱
   → 适合火旺或木旺的女生
   → 女方正好木旺（3个木）、火旺（3个火）
   → 这个女生五行互补是合适的

2. 性格互补：
   ─────────────────────────────────────────────
   男方伤官+七杀 → 追求变化、事业心强
   → 适合性格稳定、能包容的女生
   → 女方乙木日主 → 温和、能包容
   → 性格上是可以的

3. 问题在于：
   ─────────────────────────────────────────────
   女方食伤旺 → 喜欢变化、热闹
   男方伤官+七杀 → 也喜欢变化
   → 两人都追求变化
   → 可能不够稳定

【五、如果分开，什么时候会遇到新的？】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

根据流年婚运：

  2026年：午未合（婚动年）
  → 如果现在在一起，今年是婚运
  
  2028年：戊申年（正财年）
  → 如果分开，2028年有正缘机会
  
  2030年：庚戌年（正财年）
  → 另一个正缘机会

结论：
  如果离开这个女生，2028年、2030年有遇到正缘的机会
  但要注意：男方偏财多，可能需要几次感情才能稳定

【六、最终建议】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

考虑几个问题：

1. 感情问题是否可以解决？
   ─────────────────────────────────────────────
   - 女方喜欢热闹 vs 男方也能适应
   - 女方回消息慢 → 理解她的性格
   - 这些问题可以通过沟通解决

2. 合盘分数：
   ─────────────────────────────────────────────
   - 71分（良好）
   - 亥卯未三合局 → 缘分很深
   - 庚乙合 → 男方正是女方夫星
   - 这种组合不是随随便便能遇到的

3. 如果分开：
   ─────────────────────────────────────────────
   - 会有新的缘分（妻星不缺）
   - 但需要时间（2028年左右）
   - 可能需要几次感情才能稳定

【建议】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

如果感情问题可以沟通解决，建议珍惜这段缘分：
  
  ✓ 三合局注定的缘分
  ✓ 男方正女方的夫星
  ✓ 五行互补
  ✓ 婚运同步
  
如果确实无法继续，也会有新的缘分：
  
  ✓ 男方妻星不缺
  ✓ 大运财运持续
  ✓ 流年婚运多
  ✓ 2028年、2030年有机会

最终选择要看两个人的实际情况和感受。
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_marriage_future()
