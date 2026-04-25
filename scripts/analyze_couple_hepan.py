"""
详细合盘分析：戊土女（1999年3月4日23时） vs 乙木男（1997年1月3日8时）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_wuxing, calculate_shishen,
    calculate_dayun, calculate_shensha,
    TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_WUXING,
    WUXING_KE, WUXING_SHENG
)
from core.tools.hepan_calculator import (
    calculate_hepan, get_all_gan_zhi,
    analyze_di_zhi_he_chong, analyze_tian_gan_he,
    analyze_wuxing_match, analyze_rizhu_relation,
    analyze_spouse_star_match, get_shishen_for_gan,
    DI_ZHI_LIU_HE, DI_ZHI_SAN_HE, TIAN_GAN_WU_HE
)

def analyze_hepan_detail():
    """详细合盘分析"""
    
    # 女命：1999年3月4日23时
    sizhu_nv = calculate_sizhu(1999, 3, 4, 23)
    sizhu_nv['gender'] = '女'
    
    # 男命：1997年1月3日8时
    sizhu_nan = calculate_sizhu(1997, 1, 3, 8)
    sizhu_nan['gender'] = '男'
    
    # 计算合盘
    hepan = calculate_hepan(sizhu_nan, sizhu_nv, 'couple', '男', '女')
    
    print("=" * 70)
    print("八字合盘详细分析")
    print("男命：1997年1月3日8时（乙木）")
    print("女命：1999年3月4日23时（戊土）")
    print("=" * 70)
    
    # 八字排盘
    print(f"""
【男命八字】
年柱: {sizhu_nan['nian_zhu']['tian_gan']}{sizhu_nan['nian_zhu']['di_zhi']}
月柱: {sizhu_nan['yue_zhu']['tian_gan']}{sizhu_nan['yue_zhu']['di_zhi']}
日柱: {sizhu_nan['ri_zhu']['tian_gan']}{sizhu_nan['ri_zhu']['di_zhi']} (日主: 乙木)
时柱: {sizhu_nan['shi_zhu']['tian_gan']}{sizhu_nan['shi_zhu']['di_zhi']}

【女命八字】
年柱: {sizhu_nv['nian_zhu']['tian_gan']}{sizhu_nv['nian_zhu']['di_zhi']}
月柱: {sizhu_nv['yue_zhu']['tian_gan']}{sizhu_nv['yue_zhu']['di_zhi']}
日柱: {sizhu_nv['ri_zhu']['tian_gan']}{sizhu_nv['ri_zhu']['di_zhi']} (日主: 戊土)
时柱: {sizhu_nv['shi_zhu']['tian_gan']}{sizhu_nv['shi_zhu']['di_zhi']}
""")
    
    # 合盘得分
    scores = hepan['scores']
    print("=" * 70)
    print("合盘得分")
    print("=" * 70)
    print(f"""
地支评分: {scores['di_zhi']}分 - {scores['di_zhi_desc']}
五行评分: {scores['wuxing']}分 - {scores['wuxing_desc']}
日主评分: {scores['rizhu']}分 - {scores['rizhu_desc']}
天干评分: {scores['tian_gan']}分 - {scores['tian_gan_desc']}
十神评分: {scores['shishen']}分 - {scores['shishen_desc']}

总分: {scores['total']}分
等级: {scores['grade']}
评价: {scores['grade_desc']}
""")
    
    # 日主关系分析
    print("=" * 70)
    print("日主关系分析")
    print("=" * 70)
    
    rizhu_nan = sizhu_nan['ri_zhu_tiangan']
    rizhu_nv = sizhu_nv['ri_zhu_tiangan']
    wx_nan = TIAN_GAN_WUXING.get(rizhu_nan, '')
    wx_nv = TIAN_GAN_WUXING.get(rizhu_nv, '')
    
    print(f"""
【日主五行】
男命日主: {rizhu_nan} ({wx_nan})
女命日主: {rizhu_nv} ({wx_nv})

【五行关系】
""")
    
    # 检查相克关系
    if WUXING_KE.get(wx_nan) == wx_nv:
        print(f"男命{rizhu_nan}({wx_nan}) 克 女命{rizhu_nv}({wx_nv})")
        print(f"这是【正官】关系（异性相克）")
        print(f"在婚姻中：夫克妻是正常关系，代表丈夫能管住妻子")
    elif WUXING_KE.get(wx_nv) == wx_nan:
        print(f"女命{rizhu_nv}({wx_nv}) 克 男命{rizhu_nan}({wx_nan})")
        print(f"这是【七杀】关系（同性相克）或【正官】关系")
    
    # 夫妻星分析
    print("\n" + "=" * 70)
    print("夫妻星分析")
    print("=" * 70)
    
    print(f"""
【男命看妻星】
男命日主: {rizhu_nan}木
妻星 = 我克者 = 土
""")
    
    gans_nv, zhis_nv = get_all_gan_zhi(sizhu_nv)
    for gan in gans_nv:
        shishen = get_shishen_for_gan(rizhu_nan, gan)
        if shishen in ['正财', '偏财']:
            print(f"女命天干{gan}: {shishen} (妻星)")
    
    print(f"""
【女命看夫星】
女命日主: {rizhu_nv}土
夫星 = 克我者 = 木
""")
    
    gans_nan, zhis_nan = get_all_gan_zhi(sizhu_nan)
    for gan in gans_nan:
        shishen = get_shishen_for_gan(rizhu_nv, gan)
        if shishen in ['正官', '偏官']:
            print(f"男命天干{gan}: {shishen} ({'正官' if shishen == '正官' else '七杀/偏官'}夫星)")
    
    # 地支关系
    print("\n" + "=" * 70)
    print("地支关系分析")
    print("=" * 70)
    
    di_zhi_result = hepan['di_zhi_relation']
    
    print(f"""
【男方地支】{', '.join(zhis_nan)}
【女方地支】{', '.join(zhis_nv)}
""")
    
    if di_zhi_result['liu_he']:
        print("【六合】")
        for he in di_zhi_result['liu_he']:
            print(f"  {he['desc']}")
    else:
        print("【六合】无")
    
    if di_zhi_result['san_he']:
        print("\n【三合】")
        for sh in di_zhi_result['san_he']:
            sources = ', '.join([f"{s['zhi']}({s['source']})" for s in sh['zhi_sources']])
            print(f"  {sh['desc']} - {sources}")
    else:
        print("\n【三合】无")
    
    if di_zhi_result['liu_chong']:
        print("\n【六冲】")
        for ch in di_zhi_result['liu_chong']:
            print(f"  {ch['desc']}")
    else:
        print("\n【六冲】无")
    
    # 天干关系
    print("\n" + "=" * 70)
    print("天干关系分析")
    print("=" * 70)
    
    tian_gan_result = hepan['tian_gan_relation']
    
    print(f"""
【男方天干】{', '.join(gans_nan)}
【女方天干】{', '.join(gans_nv)}
""")
    
    if tian_gan_result['wu_he']:
        print("【天干五合】")
        for he in tian_gan_result['wu_he']:
            print(f"  {he['desc']}")
    else:
        print("【天干五合】无")
    
    # 五行互补
    print("\n" + "=" * 70)
    print("五行互补分析")
    print("=" * 70)
    
    wuxing_result = hepan['wuxing_match']
    
    print(f"""
【男方五行】金:{wuxing_result['wuxing_a']['金']} 木:{wuxing_result['wuxing_a']['木']} 水:{wuxing_result['wuxing_a']['水']} 火:{wuxing_result['wuxing_a']['火']} 土:{wuxing_result['wuxing_a']['土']}
【女方五行】金:{wuxing_result['wuxing_b']['金']} 木:{wuxing_result['wuxing_b']['木']} 水:{wuxing_result['wuxing_b']['水']} 火:{wuxing_result['wuxing_b']['火']} 土:{wuxing_result['wuxing_b']['土']}
""")
    
    if wuxing_result['complement']:
        print("【五行互补】")
        for comp in wuxing_result['complement']:
            print(f"  {comp['desc']}")
    
    if wuxing_result['conflict']:
        print("\n【五行冲突】")
        for conf in wuxing_result['conflict']:
            print(f"  {conf['desc']}")
    
    # 详细建议
    print("\n" + "=" * 70)
    print("合盘建议")
    print("=" * 70)
    
    for suggestion in hepan['suggestions']:
        print(f"- {suggestion}")
    
    # 深度分析
    print("\n" + "=" * 70)
    print("深度分析：能走到一起吗？")
    print("=" * 70)
    
    print(f"""
【核心问题分析】

1. 夫妻星匹配
   - 女命戊土日主，以木为夫星
   - 男命乙木日主，是女命的正官（夫星）
   - 这意味着男命是女命的"正缘"类型
   
2. 日主关系
   - 乙木克戊土 = 正官关系（异性相克）
   - 在婚姻中，男克女是正常关系
   - 正官代表稳定、温和、尊重
   
3. 关键区别：正官 vs 七杀
   
   女命八字中：
   - 时干有甲木 = 七杀透出
   - 这意味着她命中注定会遇到七杀型男性（甲木）
   - 而您是乙木 = 正官型
   
【正官型（您）vs 七杀型（甲木）】

┌──────────────────┬──────────────────┬──────────────────┐
│     对比项        │    您（乙木）    │  甲木（七杀）    │
├──────────────────┼──────────────────┼──────────────────┤
│ 对她的感觉        │ 平淡、稳定       │ 心动、激烈       │
│ 感情模式          │ 平等、和谐       │ 一方主导         │
│ 她的付出          │ 双方平等         │ 她付出更多       │
│ 长久性            │ 更稳定           │ 激情但可能消耗   │
│ 符合她命理        │ 正官夫星         │ 七杀夫星         │
│ 她命中注定        │ 不是首选         │ 命中注定         │
└──────────────────┴──────────────────┴──────────────────┘

【合盘分数解读】

总分 {scores['total']}分 - {scores['grade']}

这个分数意味着：
- 缘分有一定基础
- 不是最高分（99分那种一见钟情型）
- 但也不是低分
- 属于"良好"或"中等"级别

【她会被您吸引吗？】

从命理角度：
- 她的七杀（甲木）透出，注定被七杀型吸引
- 您是正官（乙木），不是她的"命中注定"
- 她对您的感觉可能是"好，但不够心动"

【你们能走到一起吗？】

命理不是全部，但有参考价值：

优势：
- 合盘分数尚可（{scores['total']}分）
- 您是她的正官夫星，代表稳定
- 正官婚姻更平等、更长久
- 地支有合，缘分基础在

劣势：
- 她命中注定被七杀型吸引
- 您给不了她"心动"的感觉
- 可能永远处于"好人"位置

【最终答案】

从命理角度：
- 缘分存在，但不是"命中注定"的那种
- 需要时间和耐心
- 可能需要等到她经历过七杀后
- 正官婚姻更稳定，但吸引力不如七杀

从现实角度：
- 命理只是参考，不是绝对
- 人的选择可以超越命理
- 如果她理性成熟，可能选择稳定
- 如果她追求激情，可能选择七杀

【关键时间点】

您即将进入官杀年：
- 2030年庚戌年（正官年）- 事业运、感情运
- 2031年辛亥年（七杀年）- 压力大、变动

如果在她之前遇到其他缘分，可能错过。
如果等到她经历过七杀，可能是机会。
""")


if __name__ == "__main__":
    analyze_hepan_detail()
