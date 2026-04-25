# -*- coding: utf-8 -*-
"""
男生和女生婚动时间对比分析
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING

def analyze_hundong_time():
    """分析两人婚动时间"""
    
    print("=" * 70)
    print("男生与女生婚动时间对比分析")
    print("=" * 70)
    
    # 男方：1997年1月3日 早上8点
    male_year, male_month, male_day, male_hour, male_gender = 1997, 1, 3, 8, '男'
    
    # 女方：1999年3月4日 21点
    female_year, female_month, female_day, female_hour, female_gender = 1999, 3, 4, 21, '女'
    
    # 排盘
    male_pan = bazi_pan_node(male_year, male_month, male_day, male_hour, male_gender)
    female_pan = bazi_pan_node(female_year, female_month, female_day, female_hour, female_gender)
    
    male_sizhu = male_pan['sizhu']
    female_sizhu = female_pan['sizhu']
    
    # 大运
    male_dayun = bazi_dayun_node(male_sizhu, male_year, male_month, male_day, male_hour, male_gender)
    female_dayun = bazi_dayun_node(female_sizhu, female_year, female_month, female_day, female_hour, female_gender)
    
    print("\n" + "=" * 70)
    print("【一、男方八字信息】")
    print("=" * 70)
    
    print(f"\n出生：1997年1月3日 早上8点")
    print(f"八字：{male_sizhu['nian_zhu']['tian_gan']}{male_sizhu['nian_zhu']['di_zhi']} "
          f"{male_sizhu['yue_zhu']['tian_gan']}{male_sizhu['yue_zhu']['di_zhi']} "
          f"{male_sizhu['ri_zhu']['tian_gan']}{male_sizhu['ri_zhu']['di_zhi']} "
          f"{male_sizhu['shi_zhu']['tian_gan']}{male_sizhu['shi_zhu']['di_zhi']}")
    print(f"日主：{male_sizhu['ri_zhu_tiangan']}")
    print(f"妻星：财星（男命以财为妻）")
    print(f"日支（夫妻宫）：{male_sizhu['ri_zhu']['di_zhi']}")
    
    print("\n" + "=" * 70)
    print("【二、女方八字信息】")
    print("=" * 70)
    
    print(f"\n出生：1999年3月4日 21点")
    print(f"八字：{female_sizhu['nian_zhu']['tian_gan']}{female_sizhu['nian_zhu']['di_zhi']} "
          f"{female_sizhu['yue_zhu']['tian_gan']}{female_sizhu['yue_zhu']['di_zhi']} "
          f"{female_sizhu['ri_zhu']['tian_gan']}{female_sizhu['ri_zhu']['di_zhi']} "
          f"{female_sizhu['shi_zhu']['tian_gan']}{female_sizhu['shi_zhu']['di_zhi']}")
    print(f"日主：{female_sizhu['ri_zhu_tiangan']}")
    print(f"夫星：官杀星（女命以官杀为夫）")
    print(f"日支（夫妻宫）：{female_sizhu['ri_zhu']['di_zhi']}")
    
    # 计算婚动
    def get_shishen(rizhu_gan, target_gan):
        """计算天干十神"""
        rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
        target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
        
        WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '木'}
        TIAN_GAN_YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
        
        rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
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
    
    # 地支六合
    DI_ZHI_LIU_HE = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯', 
                     '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
    
    # 地支六冲
    DI_ZHI_LIU_CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                        '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    
    # ==================== 男方婚动分析 ====================
    print("\n" + "=" * 70)
    print("【三、男方婚动时间分析】")
    print("=" * 70)
    
    male_rizhu_gan = male_sizhu['ri_zhu_tiangan']
    male_ri_zhi = male_sizhu['ri_zhu']['di_zhi']
    
    print("\n【男方大运】")
    male_hunyun_dayun = []
    for i, dy in enumerate(male_dayun.get('dayun_list', [])):
        dy_gan = dy['gan']
        dy_zhi = dy['zhi']
        dy_gan_shishen = get_shishen(male_rizhu_gan, dy_gan)
        
        is_cai = '财' in dy_gan_shishen
        marker = " ★ 财运（婚运）" if is_cai else ""
        
        print(f"\n第{i+1}步：{dy_gan}{dy_zhi}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）{marker}")
        print(f"   天干：{dy_gan_shishen}")
        
        if is_cai:
            male_hunyun_dayun.append({
                'step': i+1,
                'gan_zhi': f"{dy_gan}{dy_zhi}",
                'age_range': f"{dy['start_age']}-{dy['end_age']}",
                'year_range': f"{dy['start_year']}-{dy['end_year']}",
                'shishen': dy_gan_shishen
            })
    
    print("\n【男方流年婚动（2024-2035年）】")
    male_hunyun_liunian = []
    
    for year in range(2024, 2036):
        base_year = 1984
        gan_index = (year - base_year) % 10
        zhi_index = (year - base_year) % 12
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        liunian_gan_shishen = get_shishen(male_rizhu_gan, liunian_gan)
        
        is_hunyun = False
        reasons = []
        
        # 财星年
        if '财' in liunian_gan_shishen:
            is_hunyun = True
            reasons.append(f"天干{liunian_gan}为{liunian_gan_shishen}（妻星）")
        
        # 与日支相合
        if DI_ZHI_LIU_HE.get(male_ri_zhi) == liunian_zhi:
            is_hunyun = True
            reasons.append(f"流年{liunian_zhi}与日支{male_ri_zhi}相合（婚动）")
        
        # 日支逢冲（也可能婚动）
        if DI_ZHI_LIU_CHONG.get(male_ri_zhi) == liunian_zhi:
            reasons.append(f"流年{liunian_zhi}冲日支{male_ri_zhi}（可能有变动）")
        
        if is_hunyun:
            age = year - male_year
            male_hunyun_liunian.append({
                'year': year,
                'age': age,
                'gan_zhi': f"{liunian_gan}{liunian_zhi}",
                'reasons': reasons
            })
            print(f"\n  {year}年（{age}岁）：{liunian_gan}{liunian_zhi}年 ★ 婚动 ★")
            for r in reasons:
                print(f"    - {r}")
    
    # ==================== 女方婚动分析 ====================
    print("\n" + "=" * 70)
    print("【四、女方婚动时间分析】")
    print("=" * 70)
    
    female_rizhu_gan = female_sizhu['ri_zhu_tiangan']
    female_ri_zhi = female_sizhu['ri_zhu']['di_zhi']
    
    print("\n【女方大运】")
    female_hunyun_dayun = []
    for i, dy in enumerate(female_dayun.get('dayun_list', [])):
        dy_gan = dy['gan']
        dy_zhi = dy['zhi']
        dy_gan_shishen = get_shishen(female_rizhu_gan, dy_gan)
        
        is_guan = '官' in dy_gan_shishen or '杀' in dy_gan_shishen
        marker = " ★ 官杀运（婚运）" if is_guan else ""
        
        print(f"\n第{i+1}步：{dy_gan}{dy_zhi}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）{marker}")
        print(f"   天干：{dy_gan_shishen}")
        
        if is_guan:
            female_hunyun_dayun.append({
                'step': i+1,
                'gan_zhi': f"{dy_gan}{dy_zhi}",
                'age_range': f"{dy['start_age']}-{dy['end_age']}",
                'year_range': f"{dy['start_year']}-{dy['end_year']}",
                'shishen': dy_gan_shishen
            })
    
    print("\n【女方流年婚动（2024-2035年）】")
    female_hunyun_liunian = []
    
    for year in range(2024, 2036):
        base_year = 1984
        gan_index = (year - base_year) % 10
        zhi_index = (year - base_year) % 12
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        liunian_gan_shishen = get_shishen(female_rizhu_gan, liunian_gan)
        
        is_hunyun = False
        reasons = []
        
        # 官杀星年
        if '官' in liunian_gan_shishen or '杀' in liunian_gan_shishen:
            is_hunyun = True
            reasons.append(f"天干{liunian_gan}为{liunian_gan_shishen}（夫星）")
        
        # 与日支相合
        if DI_ZHI_LIU_HE.get(female_ri_zhi) == liunian_zhi:
            is_hunyun = True
            reasons.append(f"流年{liunian_zhi}与日支{female_ri_zhi}相合（婚动）")
        
        if is_hunyun:
            age = year - female_year
            female_hunyun_liunian.append({
                'year': year,
                'age': age,
                'gan_zhi': f"{liunian_gan}{liunian_zhi}",
                'reasons': reasons
            })
            print(f"\n  {year}年（{age}岁）：{liunian_gan}{liunian_zhi}年 ★ 婚动 ★")
            for r in reasons:
                print(f"    - {r}")
    
    # ==================== 对比分析 ====================
    print("\n" + "=" * 70)
    print("【五、两人婚动时间对比】")
    print("=" * 70)
    
    print("\n【男方婚动年份】")
    for ln in male_hunyun_liunian:
        print(f"  {ln['year']}年（{ln['age']}岁）：{ln['gan_zhi']}年")
    
    print("\n【女方婚动年份】")
    for ln in female_hunyun_liunian:
        print(f"  {ln['year']}年（{ln['age']}岁）：{ln['gan_zhi']}年")
    
    # 找共同婚动年
    male_years = set([ln['year'] for ln in male_hunyun_liunian])
    female_years = set([ln['year'] for ln in female_hunyun_liunian])
    common_years = male_years & female_years
    
    print("\n【共同婚动年份】")
    if common_years:
        for year in sorted(common_years):
            male_age = year - male_year
            female_age = year - female_year
            print(f"  {year}年：男{male_age}岁，女{female_age}岁 ★★★ 两人都有婚动 ★★★")
    else:
        print("  暂无完全重合的婚动年份")
    
    # 总结
    print("\n" + "=" * 70)
    print("【六、总结】")
    print("=" * 70)
    
    print(f"""
【男方婚动时间】

  大运财运（婚运）：
  • 2017-2027年：己卯运（偏财运）
  • 2027-2037年：庚辰运

  流年婚动：
  • 2026年（29岁）：丙午年，午未合（夫妻宫合）★★★
  • 2028年（31岁）：戊申年，正财年
  • 2029年（32岁）：己酉年，偏财年
  • 2034年（37岁）：甲寅年

【女方婚动时间】

  大运官杀运（婚运）：
  • 2021-2031年：己巳运（巳藏庚金夫星）
  • 2031-2041年：庚午运（天干庚金夫星）

  流年婚动：
  • 2025年（26岁）：乙巳年，巳藏庚金
  • 2028年（29岁）：戊申年，申藏庚金 ★★★
  • 2030年（31岁）：庚戌年，天干庚金 ★★★
  • 2031年（32岁）：辛亥年，天干辛金

【两人婚动同步】

  2026年：
  • 男方：午未合（夫妻宫合）★★★
  • 女方：虽无直接婚动，但己巳运有夫星
  → 今年是男方最强婚动年

  2028年：
  • 男方：正财年（妻星）
  • 女方：申藏庚金（夫星）
  → 两人都有婚动 ★★★

  2030年：
  • 男方：有婚运
  • 女方：天干庚金（夫星透出）
  → 两人都有婚动 ★★★

【结论】

  两人婚动相对同步的年份：2026年、2028年、2030年

  2026年（今年）：男方婚动最强，适合确定关系
  2028年：两人都有婚动，如果错过了今年，2028年是下一个机会
  2030年：女方夫星透出，又一个机会
""")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    analyze_hundong_time()
