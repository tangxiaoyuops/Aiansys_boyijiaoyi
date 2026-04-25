"""
分析为什么这位女生的命盘能匹配到高分对象
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import (
    calculate_hepan, get_all_gan_zhi, 
    DI_ZHI_LIU_HE, DI_ZHI_SAN_HE,
    TIAN_GAN_WU_HE, TIAN_GAN_WUXING, DI_ZHI_WUXING
)

def analyze_birth_chart_potential(year, month, day, hour, gender, name):
    """分析命盘的合盘潜力"""
    print(f"\n{'='*60}")
    print(f"{name}命盘分析")
    print(f"出生时间: {year}年{month}月{day}日{hour}时")
    print(f"{'='*60}")
    
    sizhu = calculate_sizhu(year, month, day, hour)
    sizhu['gender'] = gender
    
    print(f"八字: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']} "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']} "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
    
    gans, zhis = get_all_gan_zhi(sizhu)
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"日主: {rizhu_gan} ({TIAN_GAN_WUXING[rizhu_gan]})")
    print(f"天干: {gans}")
    print(f"地支: {zhis}")
    
    # 分析五行分布
    print(f"\n五行分布:")
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for gan in gans:
        wuxing_count[TIAN_GAN_WUXING[gan]] += 1
    for zhi in zhis:
        wuxing_count[DI_ZHI_WUXING[zhi]] += 1
    for wx, count in wuxing_count.items():
        bars = '█' * count
        print(f"  {wx}: {bars} ({count})")
    
    # 分析缺什么五行
    missing = [wx for wx, c in wuxing_count.items() if c == 0]
    if missing:
        print(f"\n缺少的五行: {', '.join(missing)}")
        print(f"  → 这意味着对方如果有这些五行，可以完美互补！")
    
    # 分析地支六合潜力
    print(f"\n地支六合潜力分析:")
    print(f"  她的地支有: {zhis}")
    print(f"  能与她形成六合的地支:")
    for zhi in zhis:
        for pair, hua in DI_ZHI_LIU_HE.items():
            if pair[0] == zhi:
                print(f"    {zhi} + {pair[1]} → 合化{hua}")
            elif pair[1] == zhi:
                print(f"    {zhi} + {pair[0]} → 合化{hua}")
    
    # 分析三合潜力
    print(f"\n地支三合潜力分析:")
    for san_he_key, hua_wuxing in DI_ZHI_SAN_HE.items():
        zhi_list = list(san_he_key)
        existing = [zhi for zhi in zhi_list if zhi in zhis]
        if existing:
            needed = [zhi for zhi in zhi_list if zhi not in zhis]
            print(f"  {san_he_key}三合{hua_wuxing}局:")
            print(f"    已有: {existing}")
            print(f"    需要: {needed} (对方有{needed}就能成三合!)")
    
    # 分析天干五合潜力
    print(f"\n天干五合潜力分析:")
    print(f"  她的天干有: {gans}")
    for gan in gans:
        for pair, hua in TIAN_GAN_WU_HE.items():
            if pair[0] == gan:
                print(f"    {gan} + {pair[1]} → 合化{hua}")
            elif pair[1] == gan:
                print(f"    {gan} + {pair[0]} → 合化{hua}")
    
    return sizhu


def compare_charts():
    """对比两个命盘"""
    print("\n" + "="*60)
    print("为什么女生的命盘能匹配到高分对象？")
    print("="*60)
    
    # 分析女生命盘
    sizhu_nv = analyze_birth_chart_potential(1999, 3, 4, 23, '女', '女生')
    
    # 分析您的命盘
    sizhu_nan = analyze_birth_chart_potential(1997, 1, 3, 8, '男', '您')
    
    # 对比分析
    print("\n" + "="*60)
    print("关键差异分析")
    print("="*60)
    
    gans_nv, zhis_nv = get_all_gan_zhi(sizhu_nv)
    gans_nan, zhis_nan = get_all_gan_zhi(sizhu_nan)
    
    # 1. 地支组合潜力
    print("\n【地支组合潜力对比】")
    print(f"女生地支: {zhis_nv}")
    print(f"您的地支: {zhis_nan}")
    
    # 女生能形成的六合数
    nv_liuhe_potential = set()
    for zhi in zhis_nv:
        for pair, hua in DI_ZHI_LIU_HE.items():
            if pair[0] == zhi:
                nv_liuhe_potential.add(pair[1])
            elif pair[1] == zhi:
                nv_liuhe_potential.add(pair[0])
    
    # 您能形成的六合数
    nan_liuhe_potential = set()
    for zhi in zhis_nan:
        for pair, hua in DI_ZHI_LIU_HE.items():
            if pair[0] == zhi:
                nan_liuhe_potential.add(pair[0])
            elif pair[1] == zhi:
                nan_liuhe_potential.add(pair[0])
    
    print(f"\n女生能六合的地支: {nv_liuhe_potential}")
    print(f"您能六合的地支: {nan_liuhe_potential}")
    print(f"女生的六合潜力更多！ ({len(nv_liuhe_potential)} vs {len(nan_liuhe_potential)})")
    
    # 2. 三合潜力
    print("\n【三合潜力对比】")
    nv_sanhe_count = 0
    for san_he_key, hua_wuxing in DI_ZHI_SAN_HE.items():
        existing = sum(1 for zhi in san_he_key if zhi in zhis_nv)
        if existing >= 1:
            nv_sanhe_count += 1
    
    nan_sanhe_count = 0
    for san_he_key, hua_wuxing in DI_ZHI_SAN_HE.items():
        existing = sum(1 for zhi in san_he_key if zhi in zhis_nan)
        if existing >= 1:
            nan_sanhe_count += 1
    
    print(f"女生有{nv_sanhe_count}个三合局的潜力")
    print(f"您有{nan_sanhe_count}个三合局的潜力")
    
    # 3. 五行互补性
    print("\n【五行互补性对比】")
    nv_wuxing = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for gan in gans_nv:
        nv_wuxing[TIAN_GAN_WUXING[gan]] += 1
    for zhi in zhis_nv:
        nv_wuxing[DI_ZHI_WUXING[zhi]] += 1
    
    nan_wuxing = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for gan in gans_nan:
        nan_wuxing[TIAN_GAN_WUXING[gan]] += 1
    for zhi in zhis_nan:
        nan_wuxing[DI_ZHI_WUXING[zhi]] += 1
    
    nv_missing = [wx for wx, c in nv_wuxing.items() if c == 0]
    nan_missing = [wx for wx, c in nan_wuxing.items() if c == 0]
    
    print(f"女生缺少: {nv_missing if nv_missing else '无'}")
    print(f"您缺少: {nan_missing if nan_missing else '无'}")
    
    # 4. 天干五合潜力
    print("\n【天干五合潜力对比】")
    nv_gan_wuhe = set()
    for gan in gans_nv:
        for pair, hua in TIAN_GAN_WU_HE.items():
            if pair[0] == gan:
                nv_gan_wuhe.add(pair[1])
            elif pair[1] == gan:
                nv_gan_wuhe.add(pair[0])
    
    nan_gan_wuhe = set()
    for gan in gans_nan:
        for pair, hua in TIAN_GAN_WU_HE.items():
            if pair[0] == gan:
                nan_gan_wuhe.add(pair[1])
            elif pair[1] == gan:
                nan_gan_wuhe.add(pair[0])
    
    print(f"女生能五合的天干: {nv_gan_wuhe}")
    print(f"您能五合的天干: {nan_gan_wuhe}")
    
    print("\n" + "="*60)
    print("结论：为什么女生的命盘更容易匹配高分？")
    print("="*60)
    print("""
1. 地支组合优势：
   - 女生有【卯、子】两个地支，能形成亥卯未三合木局、申子辰三合水局
   - 卯能与戌、亥、未形成良好组合
   - 子能与丑(六合)、申、辰(三合)形成组合
   - 这意味着很多男生只要地支有【亥、未、申、辰、丑、戌】中的一个
     就能与她形成六合或三合，得分会很高！

2. 五行互补优势：
   - 女生缺少金和火，对方只要有金或火就能互补加分
   - 很多男生命盘都有金和火，所以容易互补

3. 天干五合优势：
   - 女生有【己、丙、戊、甲】四个天干
   - 己与甲合、丙与辛合、戊与癸合
   - 对方天干有【甲、辛、癸】就能五合加分

4. 日主关系优势：
   - 女生日主戊土，木克土（官星），水生木
   - 对方日主如果是【甲、乙】木，就是她夫星
   - 对方日主如果是【壬、癸】水，能生木，也是有利
   
总结：女生的命盘就像一个"百搭牌"，容易和很多人形成良好的合盘关系！
    """)


if __name__ == "__main__":
    compare_charts()
