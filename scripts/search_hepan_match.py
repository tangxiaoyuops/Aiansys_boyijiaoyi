"""
八字合盘搜索脚本
搜索与指定八字合盘分数达到90分的命局
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import calculate_hepan


def search_hepan_matches(
    year_a: int,
    month_a: int,
    day_a: int,
    hour_a: int,
    gender_a: str,
    target_gender: str,
    age_range: int = 3,
    min_score: int = 90,
    year_range: tuple = None,
) -> List[Dict[str, Any]]:
    """
    搜索合盘匹配达到指定分数的命局
    
    Args:
        year_a: 命盘A年份
        month_a: 命盘A月份
        day_a: 命盘A日期
        hour_a: 命盘A时辰
        gender_a: 命盘A性别
        target_gender: 目标性别
        age_range: 年龄浮动范围（默认3岁）
        min_score: 最低匹配分数（默认90分）
        year_range: 自定义年份范围 (start_year, end_year)
    
    Returns:
        匹配结果列表
    """
    # 计算命盘A的八字
    sizhu_a = calculate_sizhu(year_a, month_a, day_a, hour_a)
    sizhu_a['gender'] = gender_a
    
    print(f"\n{'='*60}")
    print(f"命盘A（您）:")
    print(f"  出生时间: {year_a}年{month_a}月{day_a}日{hour_a}时")
    print(f"  性别: {gender_a}")
    print(f"  八字: {sizhu_a['nian_zhu']['tian_gan']}{sizhu_a['nian_zhu']['di_zhi']} "
          f"{sizhu_a['yue_zhu']['tian_gan']}{sizhu_a['yue_zhu']['di_zhi']} "
          f"{sizhu_a['ri_zhu']['tian_gan']}{sizhu_a['ri_zhu']['di_zhi']} "
          f"{sizhu_a['shi_zhu']['tian_gan']}{sizhu_a['shi_zhu']['di_zhi']}")
    print(f"  日主: {sizhu_a['ri_zhu_tiangan']}")
    print(f"{'='*60}")
    
    # 确定搜索年份范围
    if year_range:
        start_year, end_year = year_range
    else:
        start_year = year_a - age_range
        end_year = year_a + age_range
    
    print(f"\n搜索范围: {start_year}年 - {end_year}年")
    print(f"目标性别: {target_gender}")
    print(f"最低匹配分数: {min_score}分")
    print(f"\n开始搜索...")
    
    matches = []
    total_checked = 0
    
    # 遍历年份
    for year_b in range(start_year, end_year + 1):
        # 遍历月份
        for month_b in range(1, 13):
            # 遍历日期（简化处理，每月最多31天）
            days_in_month = 31 if month_b in [1, 3, 5, 7, 8, 10, 12] else 30
            if month_b == 2:
                # 简单判断闰年
                if (year_b % 4 == 0 and year_b % 100 != 0) or (year_b % 400 == 0):
                    days_in_month = 29
                else:
                    days_in_month = 28
            
            for day_b in range(1, days_in_month + 1):
                # 遍历时辰（每2小时一个时辰，共12个时辰）
                # 时辰对应：子(23,0), 丑(1,2), 寅(3,4), 卯(5,6), 辰(7,8), 巳(9,10)
                #          午(11,12), 未(13,14), 申(15,16), 酉(17,18), 戌(19,20), 亥(21,22)
                for hour_b in [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]:
                    total_checked += 1
                    
                    try:
                        # 计算命盘B的八字
                        sizhu_b = calculate_sizhu(year_b, month_b, day_b, hour_b)
                        sizhu_b['gender'] = target_gender
                        
                        # 计算合盘分数
                        hepan_result = calculate_hepan(
                            sizhu_a, sizhu_b,
                            hepan_type='couple',
                            gender_a=gender_a,
                            gender_b=target_gender
                        )
                        
                        total_score = hepan_result['scores']['total']
                        
                        # 如果分数达到要求，记录结果
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
                            
                            # 实时打印找到的结果
                            print(f"\n找到匹配! 分数: {total_score}分")
                            print(f"  出生: {year_b}年{month_b}月{day_b}日{hour_b}时")
                            print(f"  八字: {sizhu_b['nian_zhu']['tian_gan']}{sizhu_b['nian_zhu']['di_zhi']} "
                                  f"{sizhu_b['yue_zhu']['tian_gan']}{sizhu_b['yue_zhu']['di_zhi']} "
                                  f"{sizhu_b['ri_zhu']['tian_gan']}{sizhu_b['ri_zhu']['di_zhi']} "
                                  f"{sizhu_b['shi_zhu']['tian_gan']}{sizhu_b['shi_zhu']['di_zhi']}")
                            
                            # 如果找到高分匹配，可以提前结束
                            if total_score >= 95:
                                print(f"\n找到95分以上的高分匹配！")
                    
                    except Exception as e:
                        # 跳过无效日期
                        continue
    
    print(f"\n搜索完成! 共检查了 {total_checked} 个命局组合")
    print(f"找到 {len(matches)} 个符合条件的命局")
    
    # 按分数排序
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return matches


def print_match_details(match: Dict[str, Any], index: int):
    """打印匹配详情"""
    print(f"\n{'='*60}")
    print(f"匹配 #{index} - 分数: {match['score']}分")
    print(f"{'='*60}")
    
    sizhu = match['sizhu']
    hepan = match['hepan']
    
    print(f"\n命盘B（匹配对象）:")
    print(f"  出生时间: {match['year']}年{match['month']}月{match['day']}日{match['hour']}时")
    print(f"  性别: {match['gender']}")
    print(f"  八字: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']} "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']} "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
    print(f"  日主: {sizhu['ri_zhu_tiangan']}")
    
    print(f"\n合盘详情:")
    scores = hepan['scores']
    print(f"  地支评分: {scores['di_zhi']}分 - {scores['di_zhi_desc']}")
    print(f"  五行评分: {scores['wuxing']}分 - {scores['wuxing_desc']}")
    print(f"  日主评分: {scores['rizhu']}分 - {scores['rizhu_desc']}")
    print(f"  天干评分: {scores['tian_gan']}分 - {scores['tian_gan_desc']}")
    print(f"  十神评分: {scores['shishen']}分 - {scores['shishen_desc']}")
    print(f"  总分: {scores['total']}分 - {scores['grade']}")
    print(f"  评价: {scores['grade_desc']}")
    
    # 打印地支关系
    di_zhi = hepan['di_zhi_relation']
    if di_zhi.get('liu_he'):
        print(f"\n  六合关系:")
        for he in di_zhi['liu_he']:
            print(f"    - {he['desc']}")
    if di_zhi.get('san_he'):
        print(f"  三合关系:")
        for sh in di_zhi['san_he']:
            print(f"    - {sh['desc']}")
    if di_zhi.get('liu_chong'):
        print(f"  六冲关系:")
        for ch in di_zhi['liu_chong']:
            print(f"    - {ch['desc']}")
    
    # 打印建议
    if hepan.get('suggestions'):
        print(f"\n合盘建议:")
        for sug in hepan['suggestions']:
            print(f"  - {sug}")


def main():
    """主函数"""
    # 用户信息：1999年3月4日23点出生的女生
    year_a = 1999
    month_a = 3
    day_a = 4
    hour_a = 23  # 晚上23点
    gender_a = '女'  # 女生
    
    # 搜索异性（男性）
    target_gender = '男'
    
    # 年龄浮动3岁：1996-2002年
    age_range = 3
    
    # 最低分数 - 搜索90分以上
    min_score = 90
    
    print("="*60)
    print("八字合盘搜索系统")
    print("="*60)
    
    # 执行搜索
    matches = search_hepan_matches(
        year_a=year_a,
        month_a=month_a,
        day_a=day_a,
        hour_a=hour_a,
        gender_a=gender_a,
        target_gender=target_gender,
        age_range=age_range,
        min_score=min_score
    )
    
    # 打印所有匹配结果
    if matches:
        print(f"\n\n{'#'*60}")
        print(f"匹配结果汇总 (共{len(matches)}个)")
        print(f"{'#'*60}")
        
        # 只显示前10个最高分的匹配
        for i, match in enumerate(matches[:10]):
            print_match_details(match, i + 1)
            
            # 限制只显示前10个
            if i >= 9:
                break
        
        if len(matches) > 10:
            print(f"\n... 还有 {len(matches) - 10} 个匹配结果未显示")
    else:
        print("\n未找到符合条件的命局")
        print("建议：可以尝试降低分数要求或扩大年龄范围")


if __name__ == "__main__":
    main()
