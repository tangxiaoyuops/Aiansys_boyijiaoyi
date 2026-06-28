"""
对比不同八字的匹配分数分布
分析为什么某些八字合婚分数普遍较低
"""
# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import calculate_hepan


def analyze_bazi_match_distribution(
    year, month, day, hour, gender, 
    label,
    start_year=1990, end_year=2005
):
    """分析某个八字的匹配分数分布"""
    
    sizhu_a = calculate_sizhu(year, month, day, hour)
    sizhu_a['gender'] = gender
    
    target_gender = '女' if gender == '男' else '男'
    
    score_distribution = {}
    max_score = 0
    max_match = None
    
    for year_b in range(start_year, end_year + 1):
        for month_b in range(1, 13):
            days_in_month = 31 if month_b in [1, 3, 5, 7, 8, 10, 12] else 30
            if month_b == 2:
                if (year_b % 4 == 0 and year_b % 100 != 0) or (year_b % 400 == 0):
                    days_in_month = 29
                else:
                    days_in_month = 28

            for day_b in range(1, days_in_month + 1):
                for hour_b in [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
                    try:
                        sizhu_b = calculate_sizhu(year_b, month_b, day_b, hour_b)
                        sizhu_b['gender'] = target_gender

                        hepan_result = calculate_hepan(
                            sizhu_a, sizhu_b,
                            hepan_type='couple',
                            gender_a=gender,
                            gender_b=target_gender
                        )

                        total_score = hepan_result['scores']['total']
                        
                        score_bucket = total_score // 10 * 10
                        score_distribution[score_bucket] = score_distribution.get(score_bucket, 0) + 1
                        
                        if total_score > max_score:
                            max_score = total_score
                            max_match = {
                                'year': year_b,
                                'month': month_b,
                                'day': day_b,
                                'hour': hour_b,
                                'sizhu': sizhu_b,
                                'hepan': hepan_result
                            }
                    except:
                        continue
    
    return {
        'label': label,
        'bazi': f"{sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']} "
                f"{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']} "
                f"{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} "
                f"{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}",
        'rizhu': sizhu_a['ri_zhu_tiangan'],
        'score_distribution': score_distribution,
        'max_score': max_score,
        'max_match': max_match
    }


def main():
    print("="*70)
    print("不同八字合婚分数分布对比分析")
    print("="*70)
    
    # 测试多个八字
    test_cases = [
        # 男 1997年1月3日 8点 (原八字)
        (1997, 1, 3, 8, '男', "1997年男(原八字)"),
        # 男 1990年1月1日 8点
        (1990, 1, 1, 8, '男', "1990年男"),
        # 男 1985年5月5日 12点
        (1985, 5, 5, 12, '男', "1985年男"),
        # 男 1995年8月8日 10点
        (1995, 8, 8, 10, '男', "1995年男"),
        # 男 2000年2月14日 6点
        (2000, 2, 14, 6, '男', "2000年男"),
    ]
    
    results = []
    for year, month, day, hour, gender, label in test_cases:
        print(f"\n正在分析: {label}...")
        result = analyze_bazi_match_distribution(year, month, day, hour, gender, label)
        results.append(result)
    
    # 打印对比结果
    print("\n" + "="*70)
    print("对比结果汇总")
    print("="*70)
    
    for r in results:
        print(f"\n【{r['label']}】")
        print(f"  八字: {r['bazi']}")
        print(f"  日主: {r['rizhu']}")
        print(f"  最高分: {r['max_score']}分")
        print(f"  分数分布:", end="")
        for score in sorted(r['score_distribution'].keys(), reverse=True):
            print(f" {score}-{score+9}分:{r['score_distribution'][score]}人", end="")
        print()
    
    # 分析为什么分数低
    print("\n" + "="*70)
    print("分数差异原因分析")
    print("="*70)
    
    for r in results:
        print(f"\n【{r['label']}】- 最高分{r['max_score']}分")
        if r['max_match']:
            m = r['max_match']
            hepan = m['hepan']
            scores = hepan['scores']
            
            print(f"  最佳匹配八字: {m['year']}年{m['month']}月{m['day']}日")
            print(f"  分项得分:")
            print(f"    地支: {scores['di_zhi']}分 ({scores['di_zhi_desc']})")
            print(f"    五行: {scores['wuxing']}分 ({scores['wuxing_desc']})")
            print(f"    日主: {scores['rizhu']}分 ({scores['rizhu_desc']})")
            print(f"    天干: {scores['tian_gan']}分 ({scores['tian_gan_desc']})")
            print(f"    十神: {scores['shishen']}分 ({scores['shishen_desc']})")
            
            # 地支关系详情
            di_zhi = hepan['di_zhi_relation']
            if di_zhi.get('liu_he'):
                print(f"  六合: {', '.join([h['desc'] for h in di_zhi['liu_he']])}")
            if di_zhi.get('san_he'):
                print(f"  三合: {', '.join([s['desc'] for s in di_zhi['san_he']])}")
            if di_zhi.get('liu_chong'):
                print(f"  六冲: {', '.join([c['desc'] for c in di_zhi['liu_chong']])}")


if __name__ == "__main__":
    main()
