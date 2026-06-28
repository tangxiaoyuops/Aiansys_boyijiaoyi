"""
搜索与指定八字合婚分数达到80分的女性命局
男: 1997年1月3日 早上8点
"""
# -*- coding: utf-8 -*-
import sys
import os
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import calculate_hepan


def search_hepan_matches():
    # 男方八字：1997年1月3日 早上8点
    year_a = 1997
    month_a = 1
    day_a = 3
    hour_a = 8
    gender_a = '男'

    # 计算男方八字
    sizhu_a = calculate_sizhu(year_a, month_a, day_a, hour_a)
    sizhu_a['gender'] = gender_a

    print("=" * 60)
    print("男方命盘:")
    print(f"  出生时间: {year_a}年{month_a}月{day_a}日{hour_a}时")
    print(f"  八字: {sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']} "
          f"{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']} "
          f"{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} "
          f"{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}")
    print(f"  日主: {sizhu_a['ri_zhu_tiangan']}")
    print("=" * 60)

    # 搜索女方范围: 1990-2005年
    target_gender = '女'
    start_year = 1990
    end_year = 2005
    min_score = 80

    print(f"\n搜索范围: {start_year}年 - {end_year}年")
    print(f"目标性别: {target_gender}")
    print(f"最低匹配分数: {min_score}分")
    print(f"\n开始搜索...\n")

    matches = []
    total_checked = 0

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
                    total_checked += 1
                    try:
                        sizhu_b = calculate_sizhu(year_b, month_b, day_b, hour_b)
                        sizhu_b['gender'] = target_gender

                        hepan_result = calculate_hepan(
                            sizhu_a, sizhu_b,
                            hepan_type='couple',
                            gender_a=gender_a,
                            gender_b=target_gender
                        )

                        total_score = hepan_result['scores']['total']

                        if total_score >= min_score:
                            matches.append({
                                'year': year_b,
                                'month': month_b,
                                'day': day_b,
                                'hour': hour_b,
                                'gender': target_gender,
                                'sizhu': sizhu_b,
                                'hepan': hepan_result,
                                'score': total_score
                            })

                    except Exception:
                        continue

    print(f"搜索完成! 共检查了 {total_checked} 个命局组合")
    print(f"找到 {len(matches)} 个{min_score}分以上的命局\n")

    # 按分数排序
    matches.sort(key=lambda x: x['score'], reverse=True)

    # 打印所有匹配结果详情
    print("#" * 60)
    print(f"匹配结果详情 (共{len(matches)}个，按分数排序)")
    print("#" * 60)

    hour_names = {0: '子', 1: '丑', 3: '寅', 5: '卯', 7: '辰', 9: '巳',
                 11: '午', 13: '未', 15: '申', 17: '酉', 19: '戌', 21: '亥'}
    wuxing_map = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                  '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}

    for i, match in enumerate(matches):
        sizhu = match['sizhu']
        hepan = match['hepan']
        scores = hepan['scores']

        bazi_str = (f"{sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']} "
                   f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']} "
                   f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} "
                   f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")

        hour_name = hour_names.get(match['hour'], '?')

        print(f"\n{'='*60}")
        print(f"#{i+1} - 分数: {match['score']}分")
        print(f"  出生: {match['year']}年{match['month']}月{match['day']}日 {hour_name}时({match['hour']}点)")
        print(f"  八字: {bazi_str}")
        print(f"  日主: {sizhu['ri_zhu_tiangan']} ({wuxing_map.get(sizhu['ri_zhu_tiangan'], '?')}命)")
        print(f"  分项得分:")
        print(f"    地支: {scores['di_zhi']}分 - {scores['di_zhi_desc']}")
        print(f"    五行: {scores['wuxing']}分 - {scores['wuxing_desc']}")
        print(f"    日主: {scores['rizhu']}分 - {scores['rizhu_desc']}")
        print(f"    天干: {scores['tian_gan']}分 - {scores['tian_gan_desc']}")
        print(f"    十神: {scores['shishen']}分 - {scores['shishen_desc']}")
        print(f"  等级: {scores['grade']} - {scores['grade_desc']}")

        # 地支关系
        di_zhi = hepan['di_zhi_relation']
        relations = []
        if di_zhi.get('liu_he'):
            for h in di_zhi['liu_he']:
                relations.append(f"六合:{h['desc']}")
        if di_zhi.get('san_he'):
            for s in di_zhi['san_he']:
                relations.append(f"三合:{s['desc']}")
        if di_zhi.get('liu_chong'):
            for c in di_zhi['liu_chong']:
                relations.append(f"六冲:{c['desc']}")
        if relations:
            print(f"  地支关系: {'; '.join(relations)}")

    # 汇总统计
    print(f"\n\n{'='*60}")
    print("八字特征统计分析:")
    print("=" * 60)

    ri_zhu_stats = {}
    wuxing_stats = {}
    year_stats = {}

    for match in matches:
        rizhu = match['sizhu']['ri_zhu_tiangan']
        ri_zhu_stats[rizhu] = ri_zhu_stats.get(rizhu, 0) + 1

        wx = wuxing_map.get(rizhu, '?')
        wuxing_stats[wx] = wuxing_stats.get(wx, 0) + 1

        year_stats[match['year']] = year_stats.get(match['year'], 0) + 1

    print(f"\n日主分布:")
    for rz, count in sorted(ri_zhu_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rz}({wuxing_map.get(rz, '?')}) : {count}人")

    print(f"\n日主五行分布:")
    for wx, count in sorted(wuxing_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {wx} : {count}人")

    print(f"\n出生年份分布:")
    for year, count in sorted(year_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {year}年 : {count}人")


if __name__ == "__main__":
    search_hepan_matches()
