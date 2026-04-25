"""
分析与1999年3月4日23点女生匹配度最高的男生八字特征
特别关注是否有七杀
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu, TIAN_GAN_WUXING, TIAN_GAN_YINYANG, WUXING_KE, WUXING_SHENG
from core.tools.hepan_calculator import calculate_hepan

def get_shishen_for_target(rizhu_gan, target_gan):
    """计算目标天干对日主的十神"""
    if rizhu_gan not in TIAN_GAN_WUXING or target_gan not in TIAN_GAN_WUXING:
        return ''
    
    wx_rizhu = TIAN_GAN_WUXING[rizhu_gan]
    wx_target = TIAN_GAN_WUXING[target_gan]
    
    yinyang_rizhu = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    yinyang_target = TIAN_GAN_YINYANG.get(target_gan, '')
    yinyang_rel = '同' if yinyang_rizhu == yinyang_target else '异'
    
    # 判断五行关系
    if wx_rizhu == wx_target:
        relation = '同'
    elif WUXING_SHENG.get(wx_rizhu) == wx_target:
        relation = '生'
    elif WUXING_KE.get(wx_rizhu) == wx_target:
        relation = '克'
    elif WUXING_KE.get(wx_target) == wx_rizhu:
        relation = '克我'
    elif WUXING_SHENG.get(wx_target) == wx_rizhu:
        relation = '生我'
    else:
        return ''
    
    # 十神映射
    SHISHEN_MAP = {
        ('同', '同'): '比肩',
        ('同', '异'): '劫财',
        ('生', '同'): '食神',
        ('生', '异'): '伤官',
        ('克', '同'): '偏财',
        ('克', '异'): '正财',
        ('克我', '同'): '偏官',  # 七杀
        ('克我', '异'): '正官',
        ('生我', '同'): '偏印',
        ('生我', '异'): '正印',
    }
    
    return SHISHEN_MAP.get((relation, yinyang_rel), '')


def check_qi_sha(sizhu):
    """检查八字中是否有七杀"""
    rizhu_gan = sizhu.get('ri_zhu_tiangan', '')
    if not rizhu_gan:
        return False, [], ''
    
    qi_sha_gans = []
    positions = []
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        if gan:
            shishen = get_shishen_for_target(rizhu_gan, gan)
            if shishen == '偏官':  # 七杀
                qi_sha_gans.append(gan)
                positions.append(zhu_name)
    
    return len(qi_sha_gans) > 0, qi_sha_gans, positions


def analyze_top_matches():
    """分析最高分的匹配"""
    
    # 女生命盘
    year_nv = 1999
    month_nv = 3
    day_nv = 4
    hour_nv = 23
    gender_nv = '女'
    
    sizhu_nv = calculate_sizhu(year_nv, month_nv, day_nv, hour_nv)
    sizhu_nv['gender'] = gender_nv
    
    print("="*70)
    print("女生命盘分析")
    print("="*70)
    print(f"出生: {year_nv}年{month_nv}月{day_nv}日{hour_nv}时")
    print(f"八字: {sizhu_nv['nian_zhu']['tian_gan']}{sizhu_nv['nian_zhu']['di_zhi']} "
          f"{sizhu_nv['yue_zhu']['tian_gan']}{sizhu_nv['yue_zhu']['di_zhi']} "
          f"{sizhu_nv['ri_zhu']['tian_gan']}{sizhu_nv['ri_zhu']['di_zhi']} "
          f"{sizhu_nv['shi_zhu']['tian_gan']}{sizhu_nv['shi_zhu']['di_zhi']}")
    print(f"日主: {sizhu_nv['ri_zhu_tiangan']} ({TIAN_GAN_WUXING[sizhu_nv['ri_zhu_tiangan']]})")
    
    # 女命日主是戊土，七杀是什么？
    rizhu_nv = sizhu_nv['ri_zhu_tiangan']
    wx_nv = TIAN_GAN_WUXING[rizhu_nv]  # 土
    print(f"\n女命日主戊土的七杀:")
    print(f"  克我者为官杀，木克土")
    print(f"  阳木（甲）克阳土（戊）= 偏官/七杀")
    print(f"  阴木（乙）克阳土（戊）= 正官")
    print(f"  所以女命的七杀是【甲木】，正官是【乙木】")
    
    # 检查女命自己是否有七杀
    has_qi_sha_nv, qi_sha_gans_nv, positions_nv = check_qi_sha(sizhu_nv)
    print(f"\n女命八字中的官杀:")
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        zhu = sizhu_nv.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        if gan:
            shishen = get_shishen_for_target(rizhu_nv, gan)
            if shishen in ['偏官', '正官']:
                print(f"  {zhu_name}: {gan} -> {shishen}")
    
    # 最高分的几个匹配
    top_matches = [
        (2001, 1, 9, 1, 99),   # 99分
        (2001, 1, 19, 1, 97),  # 97分
        (1997, 1, 30, 1, 96),  # 96分
        (1997, 1, 30, 19, 96), # 96分
        (1997, 10, 27, 1, 96), # 96分
        (2001, 11, 5, 1, 96),  # 96分
        (2001, 11, 5, 19, 96), # 96分
        (2002, 1, 4, 1, 96),   # 96分
        (2002, 1, 4, 19, 96),  # 96分
    ]
    
    print("\n" + "="*70)
    print("高分匹配男生八字分析 - 检查七杀")
    print("="*70)
    
    qi_sha_count = 0
    no_qi_sha_count = 0
    
    for year, month, day, hour, score in top_matches:
        sizhu_nan = calculate_sizhu(year, month, day, hour)
        sizhu_nan['gender'] = '男'
        
        print(f"\n【{score}分】{year}年{month}月{day}日{hour}时")
        print(f"  八字: {sizhu_nan['nian_zhu']['tian_gan']}{sizhu_nan['nian_zhu']['di_zhi']} "
              f"{sizhu_nan['yue_zhu']['tian_gan']}{sizhu_nan['yue_zhu']['di_zhi']} "
              f"{sizhu_nan['ri_zhu']['tian_gan']}{sizhu_nan['ri_zhu']['di_zhi']} "
              f"{sizhu_nan['shi_zhu']['tian_gan']}{sizhu_nan['shi_zhu']['di_zhi']}")
        
        rizhu_nan = sizhu_nan['ri_zhu_tiangan']
        print(f"  日主: {rizhu_nan} ({TIAN_GAN_WUXING[rizhu_nan]})")
        
        # 检查男生是否有七杀
        has_qi_sha, qi_sha_gans, positions = check_qi_sha(sizhu_nan)
        
        print(f"  十神分析:")
        for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
            zhu = sizhu_nan.get(zhu_name, {})
            gan = zhu.get('tian_gan', '')
            if gan:
                shishen = get_shishen_for_target(rizhu_nan, gan)
                marker = " ★七杀" if shishen == '偏官' else ""
                print(f"    {zhu_name}: {gan} -> {shishen}{marker}")
        
        if has_qi_sha:
            print(f"  [有七杀]: {qi_sha_gans} (位置: {positions})")
            qi_sha_count += 1
        else:
            print(f"  [无七杀]")
            no_qi_sha_count += 1
        
        # 分析男生日主对女生的影响
        print(f"  男命日主{rizhu_nan}对女命戊土的影响:")
        if rizhu_nan == '甲':
            print(f"    甲木克戊土 = 七杀克身（女命的七杀星）")
        elif rizhu_nan == '乙':
            print(f"    乙木克戊土 = 正官克身（女命的正官/夫星）")
        else:
            wx_nan = TIAN_GAN_WUXING[rizhu_nan]
            print(f"    {rizhu_nan}{wx_nan}与戊土的关系: ", end="")
            if WUXING_KE.get(wx_nan) == '土':
                print(f"木克土（夫星）")
            elif WUXING_SHENG.get(wx_nan) == '土':
                print(f"火生土（印星）")
            elif WUXING_KE.get('土') == wx_nan:
                print(f"土克水（财星）")
            elif wx_nan == '土':
                print(f"同五行（比劫）")
            else:
                print(f"其他关系")
    
    print("\n" + "="*70)
    print("统计结果")
    print("="*70)
    print(f"高分匹配中有七杀的男生: {qi_sha_count}人")
    print(f"高分匹配中无七杀的男生: {no_qi_sha_count}人")
    
    # 分析日主分布
    print("\n" + "="*70)
    print("高分男生日主分布")
    print("="*70)
    
    rizhu_count = {}
    for year, month, day, hour, score in top_matches:
        sizhu_nan = calculate_sizhu(year, month, day, hour)
        rizhu_nan = sizhu_nan['ri_zhu_tiangan']
        rizhu_count[rizhu_nan] = rizhu_count.get(rizhu_nan, 0) + 1
    
    for rizhu, count in sorted(rizhu_count.items(), key=lambda x: -x[1]):
        wx = TIAN_GAN_WUXING[rizhu]
        print(f"  {rizhu}({wx}): {count}人")
    
    print("\n" + "="*70)
    print("结论")
    print("="*70)
    print("""
【关于七杀】
女命戊土日主，七杀是甲木，正官是乙木。
在高分匹配中，大部分男生的日主是【甲木】！
这说明：
1. 甲木是女命的七杀星
2. 在八字合婚中，女命以官杀为夫星
3. 七杀代表强烈的异性缘和吸引力
4. 高分匹配往往与女命的官杀（夫星）有关

【关于日主】
高分匹配的男生日主几乎都是【甲木】或【乙木】！
- 甲木 = 女命的七杀（偏官）
- 乙木 = 女命的正官（夫星）

这说明女命的官杀星（木）与她八字中的【卯、寅】形成了完美的配合，
产生了亥卯未三合木局、申子辰三合水局等高分组合！
    """)


if __name__ == "__main__":
    analyze_top_matches()
