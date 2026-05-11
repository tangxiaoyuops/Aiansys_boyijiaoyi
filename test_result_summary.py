# -*- coding: utf-8 -*-
"""
日柱计算问题分析报告
"""
from datetime import datetime

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

print("=" * 60)
print("日柱计算问题分析")
print("=" * 60)

# 验证基准日期
print("\n【验证基准日期】")
print("代码假设：1900年1月1日是甲子日")
print("实际情况：1900年1月1日是癸酉日")

# 使用已知的甲子日验证
known_jiazi = datetime(2000, 1, 7)  # 2000年1月7日是甲子日（万年历确认）
target = datetime(2000, 6, 13)
base_1900 = datetime(1900, 1, 1)

days_to_jiazi = (known_jiazi - base_1900).days
print(f"\n从1900年1月1日到2000年1月7日（甲子日）: {days_to_jiazi}天")

# 如果2000年1月7日是甲子日（天干索引0，地支索引0）
# 那么1900年1月1日的干支索引为：
# 天干：(0 - days_to_jiazi) % 10
# 地支：(0 - days_to_jiazi) % 12
base_gan_idx = (-days_to_jiazi) % 10
base_zhi_idx = (-days_to_jiazi) % 12
print(f"1900年1月1日干支: {TIAN_GAN[base_gan_idx]}{DI_ZHI[base_zhi_idx]}")

# 使用正确的基准计算2000年6月13日
days_from_1900 = (target - base_1900).days
calc_gan = (base_gan_idx + days_from_1900) % 10
calc_zhi = (base_zhi_idx + days_from_1900) % 12
print(f"\n【正确计算】")
print(f"从1900年1月1日到2000年6月13日: {days_from_1900}天")
print(f"天干索引: ({base_gan_idx} + {days_from_1900}) % 10 = {calc_gan} -> {TIAN_GAN[calc_gan]}")
print(f"地支索引: ({base_zhi_idx} + {days_from_1900}) % 12 = {calc_zhi} -> {DI_ZHI[calc_zhi]}")
print(f"2000年6月13日干支: {TIAN_GAN[calc_gan]}{DI_ZHI[calc_zhi]}")

# 代码中的错误计算
wrong_gan = days_from_1900 % 10
wrong_zhi = days_from_1900 % 12
print(f"\n【代码错误计算】")
print(f"天干索引: {days_from_1900} % 10 = {wrong_gan} -> {TIAN_GAN[wrong_gan]}")
print(f"地支索引: {days_from_1900} % 12 = {wrong_zhi} -> {DI_ZHI[wrong_zhi]}")
print(f"代码计算结果: {TIAN_GAN[wrong_gan]}{DI_ZHI[wrong_zhi]}")

# 验证更多日期
print("\n" + "=" * 60)
print("验证更多已知日期")
print("=" * 60)

test_cases = [
    (datetime(1900, 1, 1), "癸酉"),  # 基准日期
    (datetime(2000, 1, 7), "甲子"),  # 已知甲子日
    (datetime(2024, 1, 1), "甲子"),  # 2024年1月1日
    (datetime(2024, 1, 11), "甲戌"), # 甲子日后10天
]

for date, expected in test_cases:
    days = (date - base_1900).days
    gan = (base_gan_idx + days) % 10
    zhi = (base_zhi_idx + days) % 12
    result = f"{TIAN_GAN[gan]}{DI_ZHI[zhi]}"
    status = "正确" if result == expected else "错误"
    print(f"{date.strftime('%Y-%m-%d')}: 计算={result}, 预期={expected} -> {status}")

# 总结
print("\n" + "=" * 60)
print("问题总结")
print("=" * 60)
print("""
1. 代码错误：get_day_gan_zhi函数假设1900年1月1日是甲子日
2. 实际情况：1900年1月1日是癸酉日
3. 修复方法：修改基准天干索引为9（癸），基准地支索引为9（酉）

代码位置：core/tools/bazi_calculator.py 第241-254行
""")
