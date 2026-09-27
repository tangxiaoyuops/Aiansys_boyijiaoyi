"""
搜索与指定八字合婚的高分对象
男: 1997年1月3日 辰时 (丙子 庚子 乙巳 庚辰)
搜索范围: 1994-2000年出生（上下浮动3年）
"""
# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import calculate_hepan


SEARCH_YEARS = (1994, 2000)   # 用户出生1997，上下浮动3年


def search_hepan_matches():
    # 男方八字：1997年1月3日 辰时
    year_a = 1997
    month_a = 1
    day_a = 3
    hour_a = 8
    gender_a = '男'

    sizhu_a = calculate_sizhu(year_a, month_a, day_a, hour_a)
    sizhu_a['gender'] = gender_a

    print("=" * 60)
    print("男方命盘:")
    print(f"  出生: {year_a}年{month_a}月{day_a}日{hour_a}时")
    print(f"  八字: {sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']} "
          f"{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']} "
          f"{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} "
          f"{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}")
    print(f"  日主: {sizhu_a['ri_zhu_tiangan']}")
    print("=" * 60)

    target_gender = '女'
    start_year, end_year = SEARCH_YEARS
    min_score = 70  # 放低阈值，先收集候选再排序

    print(f"\n搜索范围: {start_year}年 - {end_year}年 (用户±3年)")
    print(f"目标性别: {target_gender}")
    print(f"最低匹配分数: {min_score}分\n")

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

    print(f"搜索完成! 共检查 {total_checked} 个命局，找到 {len(matches)} 个≥{min_score}分的\n")

    matches.sort(key=lambda x: x['score'], reverse=True)

    hour_names = {0: '子', 1: '丑', 3: '寅', 5: '卯', 7: '辰', 9: '巳',
                 11: '午', 13: '未', 15: '申', 17: '酉', 19: '戌', 21: '亥'}
    wuxing_map = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                  '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}

    # 只打印 Top 60
    top_n = min(60, len(matches))
    for i in range(top_n):
        match = matches[i]
        sizhu = match['sizhu']
        scores = match['hepan']['scores']
        bazi_str = (f"{sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']} "
                    f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']} "
                    f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} "
                    f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
        hour_name = hour_names.get(match['hour'], '?')

        print(f"\n{'='*60}")
        print(f"#{i+1} - 分数: {match['score']}分 ({scores['grade']} {scores['grade_desc']})")
        print(f"  出生: {match['year']}年{match['month']}月{match['day']}日 {hour_name}时({match['hour']}点)")
        print(f"  八字: {bazi_str}")
        print(f"  日主: {sizhu['ri_zhu_tiangan']} ({wuxing_map.get(sizhu['ri_zhu_tiangan'], '?')}命)  年龄差:{abs(1997 - match['year'])}岁")

    return matches


if __name__ == "__main__":
    # 将 stdout 重定向到 UTF-8 文件，避免 PowerShell 的 GBK/UTF-16 乱码
    _out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "search_person_match_result.txt")
    sys.stdout = open(_out_path, 'w', encoding='utf-8')
    search_hepan_matches()
    sys.stdout.flush()