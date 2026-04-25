"""
八字合盘分析：1997年1月3日早上8点男生 vs 1999年3月4日21点女生
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.hepan_analysis_agent import hepan_complete_analysis, hepan_llm_analysis

def main():
    # 男方：1997年1月3日 早上8点
    year_a = 1997
    month_a = 1
    day_a = 3
    hour_a = 8
    gender_a = '男'
    
    # 女方：1999年3月4日 21点
    year_b = 1999
    month_b = 3
    day_b = 4
    hour_b = 21
    gender_b = '女'
    
    print("=" * 60)
    print("八字合盘分析报告")
    print("=" * 60)
    print(f"\n【男方】出生于 {year_a}年{month_a}月{day_a}日 {hour_a}时")
    print(f"【女方】出生于 {year_b}年{month_b}月{day_b}日 {hour_b}时")
    print(f"\n分析类型：情侣合婚")
    print("-" * 60)
    
    # 执行合盘分析
    result = hepan_complete_analysis(
        year_a=year_a,
        month_a=month_a,
        day_a=day_a,
        hour_a=hour_a,
        gender_a=gender_a,
        year_b=year_b,
        month_b=month_b,
        day_b=day_b,
        hour_b=hour_b,
        gender_b=gender_b,
        hepan_type='couple',
        include_llm=False,
        include_dayun=True,
        include_shensha=True
    )
    
    if not result.get('success'):
        print(f"\n分析失败: {result.get('error')}")
        return
    
    # 打印基本信息
    print("\n" + "=" * 60)
    print("一、男方八字命盘")
    print("=" * 60)
    pan_a = result['pan_a']
    sizhu_a = pan_a['sizhu']
    print(f"年柱：{sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']}")
    print(f"月柱：{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']}")
    print(f"日柱：{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} (日主)")
    print(f"时柱：{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}")
    
    if pan_a.get('wuxing_analysis'):
        wx_a = pan_a['wuxing_analysis']
        print(f"\n五行分布：{wx_a.get('wuxing_count', {})}")
    
    if pan_a.get('shensha_analysis'):
        ss_a = pan_a['shensha_analysis']
        print(f"神煞：{ss_a.get('shensha_list', [])}")
    
    print("\n" + "=" * 60)
    print("二、女方八字命盘")
    print("=" * 60)
    pan_b = result['pan_b']
    sizhu_b = pan_b['sizhu']
    print(f"年柱：{sizhu_b['nian_zhu']['tian_gan']}{sizhu_b['nian_zhu']['di_zhi']}")
    print(f"月柱：{sizhu_b['yue_zhu']['tian_gan']}{sizhu_b['yue_zhu']['di_zhi']}")
    print(f"日柱：{sizhu_b['ri_zhu']['tian_gan']}{sizhu_b['ri_zhu']['di_zhi']} (日主)")
    print(f"时柱：{sizhu_b['shi_zhu']['tian_gan']}{sizhu_b['shi_zhu']['di_zhi']}")
    
    if pan_b.get('wuxing_analysis'):
        wx_b = pan_b['wuxing_analysis']
        print(f"\n五行分布：{wx_b.get('wuxing_count', {})}")
    
    if pan_b.get('shensha_analysis'):
        ss_b = pan_b['shensha_analysis']
        print(f"神煞：{ss_b.get('shensha_list', [])}")
    
    # 打印合盘分析
    hepan = result['hepan']
    
    print("\n" + "=" * 60)
    print("三、合盘匹配分析")
    print("=" * 60)
    
    # 评分
    scores = hepan['scores']
    print(f"\n【综合评分】")
    print(f"总评分：{scores['total']}分 / 100分")
    print(f"匹配等级：{scores['grade']} - {scores['grade_desc']}")
    print(f"\n分项得分：")
    print(f"  地支组合：{scores['di_zhi']}分/25分 ({scores['di_zhi_desc']})")
    print(f"  五行互补：{scores['wuxing']}分/25分 ({scores['wuxing_desc']})")
    print(f"  日主关系：{scores['rizhu']}分/20分 ({scores['rizhu_desc']})")
    print(f"  天干合化：{scores['tian_gan']}分/15分 ({scores['tian_gan_desc']})")
    print(f"  夫妻星配：{scores['shishen']}分/15分 ({scores['shishen_desc']})")
    
    # 地支关系
    print(f"\n【地支关系分析】")
    di_zhi = hepan['di_zhi_relation']
    if di_zhi['liu_he']:
        print("六合：")
        for he in di_zhi['liu_he']:
            print(f"  ✓ {he['desc']}")
    if di_zhi['san_he']:
        print("三合：")
        for sh in di_zhi['san_he']:
            sources = ', '.join([f"{s['zhi']}({s['source']})" for s in sh['zhi_sources']])
            print(f"  ✓ {sh['desc']} [{sources}]")
    if di_zhi['liu_chong']:
        print("六冲：")
        for ch in di_zhi['liu_chong']:
            print(f"  ✗ {ch['desc']}")
    if not di_zhi['liu_he'] and not di_zhi['liu_chong'] and not di_zhi['san_he']:
        print("  无明显合冲关系")
    
    # 天干关系
    print(f"\n【天干合化分析】")
    tian_gan = hepan['tian_gan_relation']
    if tian_gan['wu_he']:
        for he in tian_gan['wu_he']:
            print(f"  ✓ {he['desc']}")
    else:
        print("  无天干合化")
    
    # 五行互补
    print(f"\n【五行互补分析】")
    wuxing = hepan['wuxing_match']
    print(f"  男方五行：{wuxing['wuxing_a']}")
    print(f"  女方五行：{wuxing['wuxing_b']}")
    if wuxing['complement']:
        print("互补情况：")
        for c in wuxing['complement']:
            print(f"  ✓ {c['desc']}")
    if wuxing['conflict']:
        print("冲突情况：")
        for c in wuxing['conflict']:
            print(f"  ✗ {c['desc']}")
    
    # 日主关系
    print(f"\n【日主关系分析】")
    rizhu = hepan['rizhu_relation']
    print(f"  男方日主：{rizhu['rizhu_a']}（{rizhu['wuxing_a']}）")
    print(f"  女方日主：{rizhu['rizhu_b']}（{rizhu['wuxing_b']}）")
    if rizhu['relations']:
        for r in rizhu['relations']:
            print(f"  {r['desc']}")
    print(f"  整体关系：{rizhu['overall_desc']}")
    
    # 夫妻星匹配
    if 'spouse_star_match' in hepan:
        print(f"\n【夫妻星匹配分析】")
        spouse = hepan['spouse_star_match']
        if spouse.get('details'):
            for d in spouse['details']:
                print(f"  {'✓' if d.get('positive') else '○'} {d['desc']}")
        else:
            print("  无明显夫妻星匹配")
    
    # 建议
    print(f"\n【合盘建议】")
    for i, sug in enumerate(hepan['suggestions'], 1):
        print(f"  {i}. {sug}")
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
