"""
测试大运起运时间计算
验证是否正确
"""
import sys
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.tools.bazi_calculator import calculate_dayun, calculate_sizhu
from core.tools.solar_terms import get_next_jie, get_prev_jie, get_solar_term_date
from datetime import datetime

def test_dayun_calculation():
    """测试大运计算"""
    print("=" * 80)
    print("大运起运时间计算测试")
    print("=" * 80)
    
    # 测试案例1：2026年2月4日立春后出生（阳年男命）
    print("\n【案例1】2026年2月5日 12:00 出生（男命）")
    print("-" * 80)
    year, month, day, hour = 2026, 2, 5, 12
    gender = '男'
    
    # 计算四柱
    sizhu = calculate_sizhu(year, month, day, hour)
    print(f"四柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}年 "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}月 "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}日 "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}时")
    
    # 计算大运
    dayun_list = calculate_dayun(year, month, day, hour, gender, sizhu.get('bazi_year'), sizhu)
    
    print(f"\n公历出生年份: {year}年")
    print(f"八字年份: {sizhu.get('bazi_year', year)}年")
    print(f"性别: {gender}")
    
    # 获取立春时间
    lichun = get_solar_term_date(year, 0)
    print(f"立春时间: {lichun}")
    
    # 获取下一个节
    next_jie = get_next_jie(year, month, day, hour)
    print(f"下一个节: {next_jie}")
    
    # 计算天数差
    birth_date = datetime(year, month, day, hour)
    delta = next_jie - birth_date
    days_diff = delta.total_seconds() / 86400.0
    qiyun_age = days_diff / 3.0
    
    print(f"出生时间: {birth_date}")
    print(f"到下一个节的天数: {days_diff:.1f}天")
    print(f"起运年龄: {qiyun_age:.1f}岁")
    print(f"起运年份: {year + qiyun_age:.0f}年")
    
    print(f"\n大运列表:")
    for i, dayun in enumerate(dayun_list, 1):
        print(f"  第{i}步: {dayun['gan']}{dayun['zhi']} "
              f"({dayun['start_age']}-{dayun['end_age']}岁, "
              f"{dayun['start_year']}-{dayun['end_year']}年)")
    
    # 测试案例2：1985年7月15日出生（阴年男命）
    print("\n" + "=" * 80)
    print("【案例2】1985年7月15日 14:00 出生（女命）")
    print("-" * 80)
    year, month, day, hour = 1985, 7, 15, 14
    gender = '女'
    
    sizhu = calculate_sizhu(year, month, day, hour)
    print(f"四柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}年 "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}月 "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}日 "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}时")
    
    dayun_list = calculate_dayun(year, month, day, hour, gender, sizhu.get('bazi_year'), sizhu)
    
    print(f"\n公历出生年份: {year}年")
    print(f"八字年份: {sizhu.get('bazi_year', year)}年")
    print(f"性别: {gender}")
    
    # 获取上一个节
    prev_jie = get_prev_jie(year, month, day, hour)
    print(f"上一个节: {prev_jie}")
    
    # 计算天数差
    birth_date = datetime(year, month, day, hour)
    delta = birth_date - prev_jie
    days_diff = delta.total_seconds() / 86400.0
    qiyun_age = days_diff / 3.0
    
    print(f"出生时间: {birth_date}")
    print(f"到上一个节的天数: {days_diff:.1f}天")
    print(f"起运年龄: {qiyun_age:.1f}岁")
    print(f"起运年份: {year + qiyun_age:.0f}年")
    
    print(f"\n大运列表:")
    for i, dayun in enumerate(dayun_list, 1):
        print(f"  第{i}步: {dayun['gan']}{dayun['zhi']} "
              f"({dayun['start_age']}-{dayun['end_age']}岁, "
              f"{dayun['start_year']}-{dayun['end_year']}年)")
    
    # 测试案例3：立春前出生
    print("\n" + "=" * 80)
    print("【案例3】2026年1月15日 10:00 出生（男命，立春前）")
    print("-" * 80)
    year, month, day, hour = 2026, 1, 15, 10
    gender = '男'
    
    sizhu = calculate_sizhu(year, month, day, hour)
    print(f"四柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}年 "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}月 "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}日 "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}时")
    
    dayun_list = calculate_dayun(year, month, day, hour, gender, sizhu.get('bazi_year'), sizhu)
    
    print(f"\n公历出生年份: {year}年")
    print(f"八字年份: {sizhu.get('bazi_year', year)}年（立春前，应比公历年小1岁）")
    print(f"性别: {gender}")
    
    # 获取立春时间
    lichun = get_solar_term_date(year, 0)
    print(f"立春时间: {lichun}")
    
    # 获取下一个节
    next_jie = get_next_jie(year, month, day, hour)
    print(f"下一个节: {next_jie}")
    
    # 计算天数差
    birth_date = datetime(year, month, day, hour)
    delta = next_jie - birth_date
    days_diff = delta.total_seconds() / 86400.0
    qiyun_age = days_diff / 3.0
    
    print(f"出生时间: {birth_date}")
    print(f"到下一个节的天数: {days_diff:.1f}天")
    print(f"起运年龄: {qiyun_age:.1f}岁")
    
    # 这里有问题：应该用八字年份，而不是公历年份
    print(f"起运年份（错误计算）: {year + qiyun_age:.0f}年")
    print(f"起运年份（正确计算）: {sizhu.get('bazi_year', year) + qiyun_age:.0f}年")
    
    print(f"\n大运列表（当前实现）:")
    for i, dayun in enumerate(dayun_list, 1):
        print(f"  第{i}步: {dayun['gan']}{dayun['zhi']} "
              f"({dayun['start_age']}-{dayun['end_age']}岁, "
              f"{dayun['start_year']}-{dayun['end_year']}年)")
    
    print("\n" + "=" * 80)
    print("【问题分析】")
    print("=" * 80)
    print("1. 对于立春前出生的人，八字年份与公历年份不同")
    print("2. 当前代码使用公历年份计算起运年份，这是错误的")
    print("3. 应该使用八字年份计算起运年份")
    print("\n修正方案:")
    print(f"  - 将 start_year = int(year + start_age)")
    print(f"  - 改为 start_year = int(bazi_year + start_age)")

if __name__ == "__main__":
    test_dayun_calculation()
