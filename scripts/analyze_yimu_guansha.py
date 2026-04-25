"""
分析乙木男命的官杀流年运势
1997年1月3日8时 乙木男
重点分析2025-2030年的官杀运
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_wuxing, calculate_shishen,
    calculate_dayun, calculate_shensha, calculate_liunian,
    get_tian_gan, get_di_zhi,
    TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_WUXING,
    WUXING_KE, WUXING_SHENG
)


def get_shishen_for_gan(rizhu_gan: str, target_gan: str) -> str:
    """获取天干对日主的十神"""
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
    target_yinyang = TIAN_GAN_YINYANG.get(target_gan, '')
    
    if target_wuxing == rizhu_wuxing:
        return '比肩' if target_yinyang == rizhu_yinyang else '劫财'
    elif WUXING_SHENG.get(rizhu_wuxing) == target_wuxing:
        return '食神' if target_yinyang == rizhu_yinyang else '伤官'
    elif WUXING_SHENG.get(target_wuxing) == rizhu_wuxing:
        return '偏印' if target_yinyang == rizhu_yinyang else '正印'
    elif WUXING_KE.get(rizhu_wuxing) == target_wuxing:
        return '偏财' if target_yinyang == rizhu_yinyang else '正财'
    elif WUXING_KE.get(target_wuxing) == rizhu_wuxing:
        return '七杀' if target_yinyang == rizhu_yinyang else '正官'
    return ''


def analyze_guansha_years():
    """分析官杀流年"""
    
    # 男命：1997年1月3日8时
    birth_year = 1997
    sizhu = calculate_sizhu(birth_year, 1, 3, 8)
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    # 计算当前年龄和大运
    current_year = 2025
    current_age = current_year - birth_year
    
    # 大运
    dayun_list = calculate_dayun(birth_year, 1, 3, 8, '男')
    
    print("=" * 70)
    print("乙木男命 · 官杀流年分析")
    print("1997年1月3日8时 乙木日主")
    print("=" * 70)
    
    print(f"""
【八字排盘】
┌─────────────────────────────────────────────────────────────┐
│  年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}  │  月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}  │
│  日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}  │  时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}  │
└─────────────────────────────────────────────────────────────┘

天干: 丙(伤官)  庚(正官)  乙(日主)  庚(正官)
地支: 子(偏印)  子(偏印)  未(偏财)  辰(偏财)

日主: 乙木（阴木）- 花草藤蔓
""")
    
    # 找到当前大运
    current_dayun = None
    current_dayun_index = 0
    for i, dy in enumerate(dayun_list):
        if dy['start_age'] <= current_age <= dy['end_age']:
            current_dayun = dy
            current_dayun_index = i
            break
    
    print("=" * 70)
    print("一、大运走势")
    print("=" * 70)
    
    print(f"\n当前年龄：{current_age}岁（{current_year}年）\n")
    print("【大运列表】")
    for i, dy in enumerate(dayun_list[:6]):
        gan = dy['gan']
        zhi = dy['zhi']
        gan_wx = TIAN_GAN_WUXING.get(gan, '')
        zhi_wx = DI_ZHI_WUXING.get(zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, gan)
        
        current_mark = " ← 当前" if dy == current_dayun else ""
        print(f"  第{i+1}步: {gan}{zhi} ({gan_wx}{zhi_wx}) {shishen}运 {dy['start_age']}-{dy['end_age']}岁{current_mark}")
    
    # 分析大运的五行喜忌
    print(f"""
【大运分析】

乙木日主，生于子月（冬月），水旺木相：
- 印星（水）有力生扶
- 但财星（土）也旺，消耗日主
- 整体：身弱，喜印比（水木），忌财官（土金）

当前大运：{current_dayun['gan'] if current_dayun else ''}{current_dayun['zhi'] if current_dayun else ''}
""")
    
    print("=" * 70)
    print("二、2025-2035年流年运势（重点关注官杀年）")
    print("=" * 70)
    
    print("\n【流年分析】\n")
    
    guansha_years = []  # 记录官杀年
    
    for year in range(2025, 2036):
        liunian_gan = get_tian_gan(year)
        liunian_zhi = get_di_zhi(year)
        liunian_gan_wx = TIAN_GAN_WUXING.get(liunian_gan, '')
        liunian_zhi_wx = DI_ZHI_WUXING.get(liunian_zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, liunian_gan)
        age = year - birth_year
        
        # 判断吉凶
        is_guansha = shishen in ['正官', '七杀']
        if is_guansha:
            guansha_years.append((year, liunian_gan, liunian_zhi, shishen, age))
        
        # 五行喜忌判断
        is_xi = liunian_gan_wx in ['水', '木']  # 喜印比
        is_ji = liunian_gan_wx in ['土', '金']  # 忌财官
        is_zhong = liunian_gan_wx == '火'  # 中性（食伤）
        
        # 吉凶标记
        if is_guansha:
            mark = "[官杀年]"
        elif is_xi:
            mark = "[喜用年]"
        elif is_ji:
            mark = "[忌神年]"
        else:
            mark = "[中性年]"
        
        print(f"  {year}年 ({age}岁): {liunian_gan}{liunian_zhi} ({liunian_gan_wx}{liunian_zhi_wx}) {shishen} {mark}")
    
    print("\n" + "=" * 70)
    print("三、官杀流年详解")
    print("=" * 70)
    
    print(f"""
【什么是官杀年？】

对于乙木日主：
- 克我者为官杀
- 金克木，所以金是官杀
- 庚金 = 正官（异性相克，阴克阳）
- 辛金 = 七杀（同性相克，阴克阴）

【官杀年的含义】

┌─────────────────────────────────────────────────────────────────┐
│                     官杀年对男命的影响                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  正官年：                                                       │
│  ★ 事业运 - 工作上有贵人、升职机会                              │
│  ★ 名誉运 - 有机会获得认可、地位提升                            │
│  ★ 责任增加 - 可能承担更多责任                                  │
│  ★ 感情运 - 正官代表正缘，感情稳定                              │
│                                                                 │
│  七杀年：                                                       │
│  ★ 压力增加 - 工作压力、生活压力                                │
│  ★ 变动机会 - 可能换工作、换环境                                │
│  ★ 竞争激烈 - 小人暗算、竞争对手                                │
│  ★ 感情波动 - 七杀代表偏缘，感情有变                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")
    
    if guansha_years:
        print("\n【您即将遇到的官杀年】\n")
        for year, gan, zhi, shishen, age in guansha_years:
            gan_wx = TIAN_GAN_WUXING.get(gan, '')
            zhi_wx = DI_ZHI_WUXING.get(zhi, '')
            
            # 分析地支藏干
            from core.tools.bazi_calculator import DI_ZHI_CANG_GAN
            cang_gan = DI_ZHI_CANG_GAN.get(zhi, [])
            cang_gan_str = ''.join(cang_gan) if cang_gan else zhi
            
            # 判断大运
            dayun_for_year = None
            for dy in dayun_list:
                if dy['start_age'] <= age <= dy['end_age']:
                    dayun_for_year = dy
                    break
            
            print(f"┌─────────────────────────────────────────────────────────────────┐")
            print(f"│  {year}年 ({age}岁): {gan}{zhi}年 - {shishen}年")
            print(f"├─────────────────────────────────────────────────────────────────┤")
            print(f"│  天干: {gan}（{gan_wx}）- {shishen}")
            print(f"│  地支: {zhi}（{zhi_wx}）- 藏干: {cang_gan_str}")
            if dayun_for_year:
                dayun_shishen = get_shishen_for_gan(rizhu_gan, dayun_for_year['gan'])
                print(f"│  大运: {dayun_for_year['gan']}{dayun_for_year['zhi']}（{dayun_shishen}运）")
            print(f"└─────────────────────────────────────────────────────────────────┘\n")
    
    print("=" * 70)
    print("四、详细运势分析")
    print("=" * 70)
    
    print(f"""
【身弱遇官杀的影响】

您是乙木日主，身弱：
- 身弱怕官杀（金）
- 官杀会消耗您的能量
- 需要印星（水）来化解

【化解之道】

┌─────────────────────────────────────────────────────────────────┐
│                     官杀年的应对策略                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 印星化解                                                    │
│     - 多学习、多读书（印代表学习）                              │
│     - 寻找贵人帮助（印代表贵人）                                │
│     - 注重休息，不要过度消耗                                    │
│                                                                 │
│  2. 食伤制杀                                                    │
│     - 用才华和技能来应对压力                                    │
│     - 用创造力来解决问题                                        │
│     - 您有伤官（丙火），可以制杀                                │
│                                                                 │
│  3. 比劫抗杀                                                    │
│     - 寻求朋友、同事的帮助                                      │
│     - 团队合作比单打独斗好                                      │
│     - 多结交志同道合的人                                        │
│                                                                 │
│  4. 心态调整                                                    │
│     - 官杀年压力大是正常的                                      │
│     - 把压力转化为动力                                          │
│     - 保持平常心                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")
    
    print("=" * 70)
    print("五、各官杀年具体分析")
    print("=" * 70)
    
    # 详细分析每个官杀年
    for year, gan, zhi, shishen, age in guansha_years:
        print(f"\n【{year}年 {gan}{zhi}年 - {shishen}年】\n")
        
        if shishen == '正官':
            print(f"""正官年特点：
★ 事业上有贵人相助
★ 有升职、加薪的机会
★ 工作稳定，事业顺遂
★ 感情方面可能有正缘出现
★ 责任增加，但压力可控

建议：
- 抓住事业机会，积极表现
- 维护好人际关系
- 感情方面可以主动
- 注意不要过于保守""")
        
        elif shishen == '七杀':
            print(f"""七杀年特点：
★ 压力较大，可能有变动
★ 竞争激烈，需要小心小人
★ 工作上可能有挑战
★ 感情方面可能有波动
★ 身体健康需要注意

建议：
- 保持低调，不要冒进
- 注意人际关系，防小人
- 身体健康放在第一位
- 遇到困难寻求帮助
- 可以考虑换工作、换环境""")
        
        # 分析与大运的关系
        for dy in dayun_list:
            if dy['start_age'] <= age <= dy['end_age']:
                dayun_shishen = get_shishen_for_gan(rizhu_gan, dy['gan'])
                print(f"\n此年大运：{dy['gan']}{dy['zhi']}（{dayun_shishen}运）")
                
                # 分析流年与大运的关系
                if dayun_shishen == '正官' and shishen == '正官':
                    print("官官相遇：事业运极佳，但压力也大")
                elif dayun_shishen == '七杀' and shishen == '七杀':
                    print("杀杀相遇：压力倍增，需要特别小心")
                elif dayun_shishen in ['正官', '七杀'] and shishen in ['正官', '七杀']:
                    print("官杀混杂：事业和压力并存，需要平衡")
                elif dayun_shishen in ['正印', '偏印']:
                    print("印星大运+官杀流年：印化杀，压力可化解，有贵人")
                elif dayun_shishen in ['比肩', '劫财']:
                    print("比劫大运+官杀流年：有朋友同事帮助，共同面对压力")
                break
    
    print("\n" + "=" * 70)
    print("六、总结与建议")
    print("=" * 70)
    
    print(f"""
【官杀年总结】

您是乙木日主，身弱：
- 官杀（金）是您的压力源
- 但官杀也代表事业和机遇
- 身弱遇官杀，需要印比来化解

【好消息】
- 您有伤官（丙火）在年干，可以制杀
- 您有印星（子水）在年支月支，可以化杀
- 您的五行均衡，适应力强

【官杀年应对口诀】

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  正官来临事业兴，贵人相助步步升                                 │
│  七杀当头压力大，变动之中见机遇                                 │
│                                                                 │
│  身弱官杀不可怕，印星比劫来帮扶                                 │
│  学习提升找贵人，团队合作渡难关                                 │
│                                                                 │
│  官杀年份多注意，身体健康莫忽视                                 │
│  压力化动力方为道，稳扎稳打向前行                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

【关键年份提醒】""")
    
    for year, gan, zhi, shishen, age in guansha_years[:3]:  # 只显示最近3个官杀年
        print(f"  - {year}年({age}岁) {gan}{zhi}年：{shishen}年，需要特别注意")
    
    print(f"""
【最后的话】

官杀年不可怕，关键是：
1. 提前准备，不要被动应对
2. 寻求帮助，不要一个人扛
3. 学习提升，增强自身实力
4. 保持健康，身体是革命本钱

祝您官杀年顺顺利利！
""")


if __name__ == "__main__":
    analyze_guansha_years()
