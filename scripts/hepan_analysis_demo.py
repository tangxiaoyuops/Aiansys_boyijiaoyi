"""
计算两个命盘的合盘分析
1997年1月3日8点 男 vs 1999年3月4日23点 女
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.hepan_analysis_agent import hepan_complete_analysis
import json

# 男命：1997年1月3日8点
year_nan = 1997
month_nan = 1
day_nan = 3
hour_nan = 8
gender_nan = '男'

# 女命：1999年3月4日23点
year_nv = 1999
month_nv = 3
day_nv = 4
hour_nv = 23
gender_nv = '女'

print("="*60)
print("八字合盘分析")
print("="*60)

print(f"\n男方: {year_nan}年{month_nan}月{day_nan}日{hour_nan}时")
print(f"女方: {year_nv}年{month_nv}月{day_nv}日{hour_nv}时")

# 进行合盘分析
result = hepan_complete_analysis(
    year_a=year_nan, month_a=month_nan, day_a=day_nan, hour_a=hour_nan, gender_a=gender_nan,
    year_b=year_nv, month_b=month_nv, day_b=day_nv, hour_b=hour_nv, gender_b=gender_nv,
    hepan_type='couple',
    include_llm=False
)

if result.get('success'):
    print("\n" + "="*60)
    print("男方命盘")
    print("="*60)
    pan_a = result['pan_a']
    sizhu_a = pan_a['sizhu']
    print(f"八字: {sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']} "
          f"{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']} "
          f"{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} "
          f"{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}")
    print(f"日主: {sizhu_a['ri_zhu_tiangan']}")
    
    print("\n" + "="*60)
    print("女方命盘")
    print("="*60)
    pan_b = result['pan_b']
    sizhu_b = pan_b['sizhu']
    print(f"八字: {sizhu_b['nian_zhu']['tian_gan']}{sizhu_b['nian_zhu']['di_zhi']} "
          f"{sizhu_b['yue_zhu']['tian_gan']}{sizhu_b['yue_zhu']['di_zhi']} "
          f"{sizhu_b['ri_zhu']['tian_gan']}{sizhu_b['ri_zhu']['di_zhi']} "
          f"{sizhu_b['shi_zhu']['tian_gan']}{sizhu_b['shi_zhu']['di_zhi']}")
    print(f"日主: {sizhu_b['ri_zhu_tiangan']}")
    
    print("\n" + "="*60)
    print("合盘分析结果")
    print("="*60)
    
    hepan = result['hepan']
    scores = hepan['scores']
    
    print(f"\n【总分: {scores['total']}分】 - {scores['grade']}")
    print(f"评价: {scores['grade_desc']}")
    
    print(f"\n【各项评分明细】")
    print(f"  地支评分: {scores['di_zhi']}分 - {scores['di_zhi_desc']}")
    print(f"  五行评分: {scores['wuxing']}分 - {scores['wuxing_desc']}")
    print(f"  日主评分: {scores['rizhu']}分 - {scores['rizhu_desc']}")
    print(f"  天干评分: {scores['tian_gan']}分 - {scores['tian_gan_desc']}")
    print(f"  十神评分: {scores['shishen']}分 - {scores['shishen_desc']}")
    
    # 地支关系详情
    print(f"\n【地支关系】")
    di_zhi = hepan['di_zhi_relation']
    if di_zhi.get('liu_he'):
        print(f"  六合:")
        for he in di_zhi['liu_he']:
            print(f"    - {he['desc']}")
    if di_zhi.get('san_he'):
        print(f"  三合:")
        for sh in di_zhi['san_he']:
            sources = [s['source'] for s in sh['zhi_sources']]
            print(f"    - {sh['desc']} ({', '.join(sources)})")
    if di_zhi.get('liu_chong'):
        print(f"  六冲:")
        for ch in di_zhi['liu_chong']:
            print(f"    - {ch['desc']}")
    if not di_zhi.get('liu_he') and not di_zhi.get('san_he') and not di_zhi.get('liu_chong'):
        print(f"  无明显合冲关系")
    
    # 天干关系
    print(f"\n【天干关系】")
    tian_gan = hepan['tian_gan_relation']
    if tian_gan.get('wu_he'):
        print(f"  五合:")
        for he in tian_gan['wu_he']:
            print(f"    - {he['desc']}")
    else:
        print(f"  无天干合化")
    
    # 五行互补
    print(f"\n【五行互补】")
    wuxing = hepan['wuxing_match']
    print(f"  男方五行: 金{wuxing['wuxing_a']['金']} 木{wuxing['wuxing_a']['木']} "
          f"水{wuxing['wuxing_a']['水']} 火{wuxing['wuxing_a']['火']} 土{wuxing['wuxing_a']['土']}")
    print(f"  女方五行: 金{wuxing['wuxing_b']['金']} 木{wuxing['wuxing_b']['木']} "
          f"水{wuxing['wuxing_b']['水']} 火{wuxing['wuxing_b']['火']} 土{wuxing['wuxing_b']['土']}")
    if wuxing.get('complement'):
        print(f"  互补:")
        for comp in wuxing['complement']:
            print(f"    - {comp['desc']}")
    if wuxing.get('conflict'):
        print(f"  冲突:")
        for conf in wuxing['conflict']:
            print(f"    - {conf['desc']}")
    
    # 日主关系
    print(f"\n【日主关系】")
    rizhu = hepan['rizhu_relation']
    print(f"  男方日主: {rizhu['rizhu_a']} ({rizhu['wuxing_a']})")
    print(f"  女方日主: {rizhu['rizhu_b']} ({rizhu['wuxing_b']})")
    if rizhu.get('relations'):
        for rel in rizhu['relations']:
            print(f"  - {rel['desc']}")
    print(f"  总体评价: {rizhu['overall_desc']}")
    
    # 夫妻星匹配
    if hepan.get('spouse_star_match'):
        print(f"\n【夫妻星匹配】")
        spouse = hepan['spouse_star_match']
        print(f"  {spouse['desc']}")
        if spouse.get('details'):
            for det in spouse['details']:
                print(f"    - {det['desc']}")
    
    # 合盘建议
    print(f"\n【合盘建议】")
    for sug in hepan.get('suggestions', []):
        print(f"  - {sug}")
    
else:
    print(f"分析失败: {result.get('error')}")
