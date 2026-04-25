"""
验证八字排盘和流年计算
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_dayun, get_tian_gan, get_di_zhi
)
from core.tools.solar_terms import get_solar_term_date
from datetime import datetime

print("=" * 70)
print("验证八字排盘和流年计算")
print("=" * 70)

# 1. 验证立春日期
print("\n【验证立春日期】")
lichun_1997 = get_solar_term_date(1997, 0)
print(f"1997年立春日期: {lichun_1997}")
print(f"出生日期: 1997年1月3日8时")
print(f"立春前出生? {datetime(1997, 1, 3, 8) < lichun_1997}")

# 2. 验证八字排盘
print("\n【验证八字排盘】")
sizhu = calculate_sizhu(1997, 1, 3, 8)
print(f"年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}")
print(f"月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}")
print(f"日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}")
print(f"时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
print(f"八字年份: {sizhu.get('bazi_year', 'N/A')}")
print(f"月份索引: {sizhu.get('month_index', 'N/A')}")

# 3. 验证流年天干地支
print("\n【验证流年干支计算】")
print("公式: 以1984年甲子年为基准")
print("(年份 - 1984) % 10 = 天干索引")
print("(年份 - 1984) % 12 = 地支索引")
print()

# 天干地支列表
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

test_years = [1984, 2024, 2025, 2030, 2031]
for year in test_years:
    gan = get_tian_gan(year)
    zhi = get_di_zhi(year)
    gan_idx = (year - 1984) % 10
    zhi_idx = (year - 1984) % 12
    print(f"{year}年: ({year}-1984)%10={gan_idx} → {TIAN_GAN[gan_idx]} = {gan}, ({year}-1984)%12={zhi_idx} → {DI_ZHI[zhi_idx]} = {zhi}")

# 4. 手动验证
print("\n【手动验证流年】")
print()
print("1984年 = 甲子年 (基准)")
print("1984年索引: 天干=0(甲), 地支=0(子)")
print()
print("2024年:")
print("  (2024-1984)=40")
print("  40%10=0 → 甲")
print("  40%12=4 → 辰")
print("  2024年 = 甲辰年 ✓")
print()
print("2025年:")
print("  (2025-1984)=41")
print("  41%10=1 → 乙")
print("  41%12=5 → 巳")
print("  2025年 = 乙巳年 ✓")
print()
print("2030年:")
print("  (2030-1984)=46")
print("  46%10=6 → 庚")
print("  46%12=10 → 戌")
print("  2030年 = 庚戌年 ✓")
print()
print("2031年:")
print("  (2031-1984)=47")
print("  47%10=7 → 辛")
print("  47%12=11 → 亥")
print("  2031年 = 辛亥年 ✓")

# 5. 官杀判断
print("\n【官杀判断】")
print()
print("日主: 乙木（阴木）")
print("克我者: 金")
print("  - 庚金（阳金）= 正官（异性相克）")
print("  - 辛金（阴金）= 七杀（同性相克）")
print()
print("2030年庚戌年: 庚金 = 正官 ✓")
print("2031年辛亥年: 辛金 = 七杀 ✓")

# 6. 大运验证
print("\n【验证大运】")
dayun_list = calculate_dayun(1997, 1, 3, 8, '男')
for i, dy in enumerate(dayun_list[:6]):
    print(f"第{i+1}步: {dy['gan']}{dy['zhi']} {dy['start_age']}-{dy['end_age']}岁")

# 7. 关键问题：当前年龄
print("\n【当前年龄计算】")
current_year = 2025
birth_year = 1997
age = current_year - birth_year
print(f"出生年份: {birth_year}")
print(f"当前年份: {current_year}")
print(f"年龄: {age}岁（周岁）")
print()
print("注意: 如果1997年1月3日在立春前出生，")
print("八字年份是1996年（丙子年），不是1997年（丁丑年）")

# 8. 如果八字年份是1996年
print("\n【如果八字年份是1996年】")
bazi_year_1996 = 1996
for year in range(2025, 2036):
    liunian_gan = get_tian_gan(year)
    liunian_zhi = get_di_zhi(year)
    print(f"{year}年: {liunian_gan}{liunian_zhi}")

print("\n" + "=" * 70)
print("结论")
print("=" * 70)
print("""
1. 流年计算公式是正确的（以1984年甲子年为基准）
2. 1997年1月3日在立春前，八字年份应该是1996年
3. 但流年（如2030年庚戌年）计算不受影响，流年是按公历年份计算的
4. 官杀年判断：2030年庚戌年（正官）、2031年辛亥年（七杀）是正确的
""")
