"""
分析乙木男2026-2027年的感情缘分
1997年1月3日8时 乙木男
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_wuxing, calculate_shishen,
    calculate_dayun, calculate_liunian, calculate_liuyue_list,
    get_tian_gan, get_di_zhi, get_shishen_for_gan,
    TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_WUXING,
    WUXING_KE, WUXING_SHENG, DI_ZHI_LIU_HE, DI_ZHI_CANG_GAN
)

def analyze_2026_2027_yunshi():
    """分析2026-2027年运势"""
    
    # 男命：1997年1月3日8时
    birth_year = 1997
    sizhu = calculate_sizhu(birth_year, 1, 3, 8)
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print("=" * 70)
    print("乙木男 2026-2027年 感情缘分分析")
    print("1997年1月3日8时 乙木日主")
    print("=" * 70)
    
    print(f"""
【八字排盘】
年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}
月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}
日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} (日主: 乙木)
时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}

【日主特点】
乙木 = 阴木，花草藤蔓
- 温和、柔顺、适应力强
- 善于借力，懂得合作
- 五行均衡，性格中和
""")
    
    # 大运
    dayun_list = calculate_dayun(birth_year, 1, 3, 8, '男')
    current_year = 2025
    current_age = current_year - birth_year
    
    print("=" * 70)
    print("一、大运走势")
    print("=" * 70)
    
    print(f"\n当前年龄：{current_age}岁（{current_year}年）\n")
    print("【大运列表】")
    
    current_dayun = None
    for i, dy in enumerate(dayun_list[:6]):
        gan = dy['gan']
        zhi = dy['zhi']
        gan_wx = TIAN_GAN_WUXING.get(gan, '')
        zhi_wx = DI_ZHI_WUXING.get(zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, gan)
        
        is_current = dy['start_age'] <= current_age <= dy['end_age']
        if is_current:
            current_dayun = dy
        
        mark = " <-- 当前" if is_current else ""
        print(f"  第{i+1}步: {gan}{zhi} ({gan_wx}{zhi_wx}) {shishen}运 {dy['start_age']}-{dy['end_age']}岁{mark}")
    
    # 分析2026-2027年
    print("\n" + "=" * 70)
    print("二、2026-2027年流年分析")
    print("=" * 70)
    
    for year in [2026, 2027]:
        age = year - birth_year
        liunian_gan = get_tian_gan(year)
        liunian_zhi = get_di_zhi(year)
        liunian_gan_wx = TIAN_GAN_WUXING.get(liunian_gan, '')
        liunian_zhi_wx = DI_ZHI_WUXING.get(liunian_zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, liunian_gan)
        
        # 判断五行喜忌
        is_xi = liunian_gan_wx in ['水', '木']  # 身弱喜印比
        is_ji = liunian_gan_wx in ['土', '金']  # 忌财官
        is_zhong = liunian_gan_wx == '火'  # 中性
        
        # 判断是否桃花年
        # 乙木日主，桃花在午、酉（以日支未来看）
        # 桃花：寅午戌见卯，申子辰见酉，巳酉丑见午，亥卯未见子
        rizhu_zhi = sizhu['ri_zhu']['di_zhi']
        taohua_zhi = None
        if rizhu_zhi in ['寅', '午', '戌']:
            taohua_zhi = '卯'
        elif rizhu_zhi in ['申', '子', '辰']:
            taohua_zhi = '酉'
        elif rizhu_zhi in ['巳', '酉', '丑']:
            taohua_zhi = '午'
        elif rizhu_zhi in ['亥', '卯', '未']:
            taohua_zhi = '子'
        
        is_taohua = liunian_zhi == taohua_zhi
        
        # 判断是否财星年（男命财星=妻星）
        is_cai_xing = shishen in ['正财', '偏财']
        
        # 判断是否合婚姻宫
        rizhu_zhi = sizhu['ri_zhu']['di_zhi']  # 日支 = 婚姻宫
        he_zhi = None
        for (zhi1, zhi2), hua in DI_ZHI_LIU_HE.items():
            if zhi1 == rizhu_zhi:
                he_zhi = zhi2
            elif zhi2 == rizhu_zhi:
                he_zhi = zhi1
        
        is_he_hun_yin_gong = liunian_zhi == he_zhi
        
        print(f"""
【{year}年 ({age}岁)】
流年: {liunian_gan}{liunian_zhi} ({liunian_gan_wx}{liunian_zhi_wx})
十神: {shishen}
五行: {'喜用' if is_xi else '忌神' if is_ji else '中性'}
""")
        
        print(f"【关键指标】")
        print(f"  - 桃花年: {'是' if is_taohua else '否'} {'(感情运旺)' if is_taohua else ''}")
        print(f"  - 财星年: {'是' if is_cai_xing else '否'} {'(妻星出现)' if is_cai_xing else ''}")
        print(f"  - 合婚姻宫: {'是' if is_he_hun_yin_gong else '否'} {'(婚运动)' if is_he_hun_yin_gong else ''}")
        
        # 详细分析
        print(f"\n【详细分析】")
        
        if is_taohua:
            print(f"  桃花年到！感情运旺盛，异性缘佳，有机会遇到心仪对象。")
        
        if is_cai_xing:
            print(f"  财星年！男命财星为妻星，这一年有遇到正缘的机会。")
        
        if is_he_hun_yin_gong:
            print(f"  流年合婚姻宫！这是结婚或确定关系的好时机。")
        
        # 十神分析
        if shishen == '比肩':
            print(f"  比肩年：竞争合作，感情上可能有竞争者，也可能通过朋友认识异性。")
        elif shishen == '劫财':
            print(f"  劫财年：破财之年，感情上要注意第三者，不宜冲动结婚。")
        elif shishen == '食神':
            print(f"  食神年：才华展现，魅力提升，适合追求感情。")
        elif shishen == '伤官':
            print(f"  伤官年：表达欲强，感情上可能有波动，注意沟通。")
        elif shishen == '正财':
            print(f"  正财年：正缘出现！男命正财为正妻，这是遇到正缘的好年份。")
        elif shishen == '偏财':
            print(f"  偏财年：偏缘出现，可能有桃花，但不一定是正缘。")
        elif shishen == '正官':
            print(f"  正官年：事业运旺，责任感增强，适合稳定下来。")
        elif shishen == '七杀':
            print(f"  七杀年：压力变大，变动多，感情可能有波折。")
        elif shishen == '正印':
            print(f"  正印年：贵人相助，学业进修，适合培养感情。")
        elif shishen == '偏印':
            print(f"  偏印年：学习成长，可能有精神层面的邂逅。")
        
        # 大运分析
        for dy in dayun_list:
            if dy['start_age'] <= age <= dy['end_age']:
                dayun_shishen = get_shishen_for_gan(rizhu_gan, dy['gan'])
                print(f"\n  此年大运: {dy['gan']}{dy['zhi']} ({dayun_shishen}运)")
                
                # 大运+流年组合分析
                if dayun_shishen == '正财' and shishen == '正财':
                    print(f"  财财相遇：妻星叠加，遇到正缘概率大增！")
                elif dayun_shishen == '偏财' and shishen in ['正财', '偏财']:
                    print(f"  财运逢财年：感情运旺，有望遇到另一半。")
                elif dayun_shishen == '正官' and shishen == '正官':
                    print(f"  官官相遇：事业稳定，适合成家立业。")
                break
    
    # 综合分析
    print("\n" + "=" * 70)
    print("三、2026-2027年综合分析")
    print("=" * 70)
    
    print(f"""
【2026年丙午年 (30岁)】

流年: 丙午 (火火)
十神: 伤官
大运: 己卯 (偏财运)

关键点:
- 伤官年：表达欲强，有才华展现的机会
- 大运偏财：有桃花机会
- 不是财星年：不是直接的感情年
- 不是桃花年：感情运一般
- 不合婚姻宫：婚运不强

分析:
2026年不是典型的结婚年，但可以通过社交、展现才华来吸引异性。
伤官年魅力提升，但也要注意不要太张扬。

感情运: 中等
结婚运: 较弱
建议: 主动社交，展现魅力，但不宜急躁

【2027年丁未年 (31岁)】

流年: 丁未 (火土)
十神: 食神
大运: 己卯 (偏财运)

关键点:
- 食神年：温和愉快，适合培养感情
- 大运偏财：有桃花机会
- 未土是财星（妻星）！
- 未是日支！流年地支=日支=婚姻宫！

【重要发现】
流年地支未 = 日支未
这意味着2027年"伏吟"婚姻宫！
伏吟 = 流年地支与日支相同
这是婚动的重要标志！

分析:
2027年是重要的感情年份！
1. 食神年：性格温和，容易相处
2. 未土是财星（妻星）在地支出现
3. 流年伏吟婚姻宫 = 婚动信号

感情运: 较强
结婚运: 强
建议: 这一年非常适合确定关系或结婚！
""")
    
    # 与戊土女的关系
    print("\n" + "=" * 70)
    print("四、与戊土女的缘分分析（2026-2027）")
    print("=" * 70)
    
    print(f"""
【戊土女的八字】
年柱: 己卯    月柱: 丙寅    日柱: 戊子    时柱: 甲子
日主: 戊土

【关键信息】
- 她是戊土日主
- 时干甲木透出（七杀夫星）
- 您是乙木日主（她的正官夫星）

【2026-2027年你们的关系】

2026年丙午年:
- 您是伤官年，表达欲强
- 她的八字：丙是偏印，午是正印
- 你们的流年天干相同（丙）
- 有共同话题，但不是强婚动

2027年丁未年:
- 您是食神年，未伏吟婚姻宫
- 她的八字：丁是正印，未是劫财
- 未与她的八字：未与卯有半合（卯未半合木）
- 未与她的日支子：子未相害

【关键分析】
2027年您伏吟婚姻宫，是您的婚动年。
但未与她的日支子相害（子未害），这说明：
- 您可能有婚动，但对象不一定是她
- 或者你们的关系在这一年有矛盾

【她的婚动时间】
她的日支是子，与丑合（子丑合）
遇到丑年（2028戊申年地支不是丑，2029己酉年也不是...）
下一个丑年是2037年丁丑年
或者遇到合婚姻宫的年份

【结论】
- 您2027年有婚动信号
- 但与她的八字有子未害
- 这可能意味着您的婚动对象另有其人
- 或者你们在这一年有矛盾冲突
""")
    
    # 最终建议
    print("\n" + "=" * 70)
    print("五、总结与建议")
    print("=" * 70)
    
    print(f"""
【2026年】
感情运: 中等
结婚运: 较弱
适合: 社交、展现魅力、培养感情
不建议: 急于结婚、冲动决定

【2027年】
感情运: 较强
结婚运: 强（伏吟婚姻宫）
适合: 确定关系、谈婚论嫁、结婚
注意: 子未相害，与戊土女可能有矛盾

【最终答案】

2026年：
- 有机会认识异性
- 但不是强婚动年
- 感情需要慢慢培养

2027年：
- 您有强婚动信号
- 这一年很可能结婚或确定关系
- 但对象不一定是戊土女（因为子未害）
- 如果是她，需要注意沟通，避免矛盾

【关于戊土女】
- 她的命局七杀透出，注定被甲木型吸引
- 您是乙木（正官），不是她的"命中注定"
- 2027年您婚动，但她可能还在寻找她的"心动"
- 如果她经历过七杀，可能开始珍惜正官

【建议】
1. 2026年积极社交，多认识人
2. 2027年是您的婚动年，好好把握
3. 如果还在追戊土女，2027年是关键年份
4. 但也要有心理准备，您的婚动对象可能是别人
5. 保持开放心态，缘分会在对的时间出现
""")


if __name__ == "__main__":
    analyze_2026_2027_yunshi()
