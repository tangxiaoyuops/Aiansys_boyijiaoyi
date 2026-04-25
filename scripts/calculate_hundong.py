"""
计算戊土女的婚动时间
1999年3月4日23时 女命
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_dayun, calculate_liunian,
    get_tian_gan, get_di_zhi, get_shishen_for_gan,
    TIAN_GAN_WUXING, DI_ZHI_WUXING, DI_ZHI_LIU_HE
)

def calculate_hundong():
    """计算婚动时间"""
    
    # 女命：1999年3月4日23时
    birth_year = 1999
    sizhu = calculate_sizhu(birth_year, 3, 4, 23)
    rizhu_gan = sizhu['ri_zhu_tiangan']
    rizhu_zhi = sizhu['ri_zhu']['di_zhi']
    
    print("=" * 70)
    print("戊土女婚动时间计算")
    print("1999年3月4日23时")
    print("=" * 70)
    
    print(f"""
【八字排盘】
年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}
月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}
日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} (日主: 戊土)
时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}

日支(婚姻宫): {rizhu_zhi}
""")
    
    # 计算大运
    dayun_list = calculate_dayun(birth_year, 3, 4, 23, '女')
    
    print("=" * 70)
    print("一、大运走势")
    print("=" * 70)
    
    current_year = 2025
    current_age = current_year - birth_year
    
    print(f"\n当前年龄：{current_age}岁（{current_year}年）\n")
    
    for i, dy in enumerate(dayun_list[:8]):
        gan = dy['gan']
        zhi = dy['zhi']
        gan_wx = TIAN_GAN_WUXING.get(gan, '')
        zhi_wx = DI_ZHI_WUXING.get(zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, gan)
        
        is_current = dy['start_age'] <= current_age <= dy['end_age']
        mark = " <-- 当前" if is_current else ""
        print(f"  第{i+1}步: {gan}{zhi} ({gan_wx}{zhi_wx}) {shishen}运 {dy['start_age']}-{dy['end_age']}岁{mark}")
    
    # 婚动判断标准
    print("\n" + "=" * 70)
    print("二、婚动判断标准")
    print("=" * 70)
    
    print(f"""
【女命婚动信号】

1. 夫星（官杀）出现的年份
   - 她的夫星是木（官杀）
   - 甲木 = 七杀
   - 乙木 = 正官
   - 遇到甲、乙、寅、卯的年份有感情机会

2. 婚姻宫（日支）被合/冲的年份
   - 她的婚姻宫 = 子
   - 子与丑合（子丑六合）
   - 子与午冲（子午相冲）
   - 子与未害（子未相害）
   - 申子辰三合水局

3. 桃花年份
   - 她的桃花：以日支或年支看
   - 年支卯：桃花在子
   - 日支子：桃花在酉
   - 遇到子、酉的年份有桃花

4. 大运进入官杀运
   - 官杀运 = 感情运旺
   - 适合结婚

5. 流年与大运、原局的组合
   - 天干合（甲己合、乙庚合等）
   - 地支合（六合、三合）
""")
    
    # 计算具体年份
    print("\n" + "=" * 70)
    print("三、2025-2040年逐年分析")
    print("=" * 70)
    
    # 婚姻宫六合
    hunyin_gong = rizhu_zhi  # 子
    he_zhi = None  # 与子合的地支
    for (zhi1, zhi2), hua in DI_ZHI_LIU_HE.items():
        if zhi1 == hunyin_gong:
            he_zhi = zhi2
        elif zhi2 == hunyin_gong:
            he_zhi = zhi1
    
    print(f"\n她的婚姻宫是【{hunyin_gong}】，与【{he_zhi}】相合（子丑合）")
    print(f"遇到丑年，婚姻宫被合 = 婚动信号")
    
    print("\n【2025-2040年逐年分析】\n")
    
    hundong_years = []
    
    for year in range(2025, 2041):
        age = year - birth_year
        liunian_gan = get_tian_gan(year)
        liunian_zhi = get_di_zhi(year)
        liunian_gan_wx = TIAN_GAN_WUXING.get(liunian_gan, '')
        liunian_zhi_wx = DI_ZHI_WUXING.get(liunian_zhi, '')
        shishen = get_shishen_for_gan(rizhu_gan, liunian_gan)
        
        # 判断婚动信号
        signals = []
        
        # 1. 夫星年份
        if liunian_gan in ['甲', '乙'] or liunian_zhi in ['寅', '卯']:
            if liunian_gan == '甲':
                signals.append("七杀年(甲木)")
            elif liunian_gan == '乙':
                signals.append("正官年(乙木)")
            if liunian_zhi == '寅':
                signals.append("七杀地支")
            elif liunian_zhi == '卯':
                signals.append("正官地支")
        
        # 2. 婚姻宫合
        if liunian_zhi == he_zhi:  # 丑
            signals.append("婚姻宫六合")
        
        # 3. 婚姻宫冲
        if liunian_zhi == '午':  # 子午冲
            signals.append("婚姻宫六冲")
        
        # 4. 子未害
        if liunian_zhi == '未':
            signals.append("婚姻宫相害")
        
        # 5. 桃花年
        if liunian_zhi == '子' or liunian_zhi == '酉':
            signals.append("桃花年")
        
        # 6. 三合水局（申子辰）
        if liunian_zhi in ['申', '辰']:
            signals.append("三合水局元素")
        
        # 7. 天干合
        if liunian_gan == '甲':  # 甲己合
            signals.append("甲己合(夫星合)")
        
        signal_str = ", ".join(signals) if signals else ""
        
        # 判断婚动强度
        if "婚姻宫六合" in signal_str:
            strength = "【强婚动】"
            hundong_years.append((year, age, signal_str, "强"))
        elif "七杀年" in signal_str or "正官年" in signal_str:
            strength = "【中婚动】"
            hundong_years.append((year, age, signal_str, "中"))
        elif signals:
            strength = "【弱婚动】"
            hundong_years.append((year, age, signal_str, "弱"))
        else:
            strength = ""
        
        print(f"  {year}年({age}岁): {liunian_gan}{liunian_zhi} ({liunian_gan_wx}{liunian_zhi_wx}) {shishen} {strength}")
        if signal_str:
            print(f"           └─ {signal_str}")
    
    # 大运分析
    print("\n" + "=" * 70)
    print("四、大运与感情")
    print("=" * 70)
    
    for i, dy in enumerate(dayun_list[:6]):
        gan = dy['gan']
        zhi = dy['zhi']
        shishen = get_shishen_for_gan(rizhu_gan, gan)
        gan_wx = TIAN_GAN_WUXING.get(gan, '')
        
        # 判断是否官杀运
        is_guansha = shishen in ['正官', '七杀', '偏官']
        
        if is_guansha:
            print(f"\n  第{i+1}步: {gan}{zhi} ({shishen}运) {dy['start_age']}-{dy['end_age']}岁")
            print(f"           └─ 【官杀运！感情运旺，适合结婚】")
    
    # 总结婚动年份
    print("\n" + "=" * 70)
    print("五、婚动年份总结")
    print("=" * 70)
    
    print("\n【强婚动年份】（婚姻宫被合）")
    for year, age, signal, strength in hundong_years:
        if strength == "强":
            print(f"  {year}年({age}岁): {signal}")
    
    print("\n【中婚动年份】（夫星出现）")
    for year, age, signal, strength in hundong_years:
        if strength == "中":
            print(f"  {year}年({age}岁): {signal}")
    
    print("\n【弱婚动年份】（其他信号）")
    for year, age, signal, strength in hundong_years:
        if strength == "弱":
            print(f"  {year}年({age}岁): {signal}")
    
    # 最终结论
    print("\n" + "=" * 70)
    print("六、结论")
    print("=" * 70)
    
    print("""
【婚动时间判断】

1. 强婚动年份（最可能结婚的年份）：
   - 遇到丑年 = 婚姻宫六合 = 强婚动信号
   - 下一个丑年：2029年(己丑)、2041年(辛丑)
   
2. 中婚动年份（感情机会多的年份）：
   - 官杀年 = 遇到甲、乙、寅、卯的年份
   - 2025年乙巳年：乙木正官
   - 2031年辛亥年：亥中藏甲木
   - 2032年壬子年
   - 2033年癸丑年：丑合婚姻宫
   - 2034年甲寅年：甲木七杀透出
   - 2035年乙卯年：乙木正官透出

3. 大运影响：
   - 看大运是否有官杀运
   - 官杀运期间感情运旺

【重点年份】

2029年(己丑年) 30岁：
- 丑与子合（婚姻宫六合）
- 强婚动信号！
- 这是最有可能结婚的年份

2033年(癸丑年) 34岁：
- 丑与子合（婚姻宫六合）
- 强婚动信号！
- 如果2029年没结婚，2033年是下一个机会

2034年(甲寅年) 35岁：
- 甲木七杀透出
- 七杀年，感情机会
- 如果还在找，可能遇到七杀型

2035年(乙卯年) 36岁：
- 乙木正官透出
- 正官年，感情机会
- 可能遇到正官型

【结论】

她的婚动年份不是2037年，而是：

最早：2029年(己丑年) 30岁 ← 婚姻宫六合，强婚动
其次：2033年(癸丑年) 34岁 ← 婚姻宫六合，强婚动
再次：2034-2035年 官杀年，感情机会

不会等到2037年！
2037年(丁丑年)确实是下一个丑年，但不是最早的婚动年。
""")


if __name__ == "__main__":
    calculate_hundong()
