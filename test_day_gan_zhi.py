# -*- coding: utf-8 -*-
"""
日柱基准日期验证
验证1900年1月1日的实际干支
"""
import sys
sys.path.insert(0, 'G:/projects/博弈交易/Aiansys_boyijiaoyi')

from datetime import datetime, timedelta

# 已知的甲子日（通过万年历确认）
# 2024年1月1日是甲子日吗？让我查一下...
# 根据万年历，2024年1月1日是甲子日
# 让我们用这个作为基准

# 更可靠的基准：1984年1月1日是甲子年甲子月甲子日（难得的三甲日）
# 实际上，1984年是甲子年，但1984年1月1日不是甲子日

# 让我找一个已知的甲子日
# 根据万年历：2000年1月7日是甲子日
# 验证：从2000年1月7日到2000年6月13日的天数

known_jiazi_date = datetime(2000, 1, 7)  # 已知的甲子日
target_date = datetime(2000, 6, 13)
days_diff = (target_date - known_jiazi_date).days

print(f"从2000年1月7日（甲子日）到2000年6月13日: {days_diff}天")
print(f"天干索引: {days_diff % 10}")
print(f"地支索引: {days_diff % 12}")

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

gan_idx = days_diff % 10
zhi_idx = days_diff % 12
print(f"计算结果: {TIAN_GAN[gan_idx]}{DI_ZHI[zhi_idx]}")

# 如果从甲子日起算，经过days_diff天后：
# 2000年1月7日是甲子日，天干索引0，地支索引0
# 2000年6月13日应该是：
# 天干：(0 + days_diff) % 10
# 地支：(0 + days_diff) % 12

print(f"\n验证2000年6月13日的干支:")
gan = TIAN_GAN[(0 + days_diff) % 10]
zhi = DI_ZHI[(0 + days_diff) % 12]
print(f"结果: {gan}{zhi}")

# 现在验证1900年1月1日的干支
# 从2000年1月7日往回推算到1900年1月1日
base_1900 = datetime(1900, 1, 1)
days_to_1900 = (known_jiazi_date - base_1900).days
print(f"\n从1900年1月1日到2000年1月7日（甲子日）: {days_to_1900}天")

# 如果2000年1月7日是甲子日，那么1900年1月1日的干支是：
# 天干索引 = (0 - days_to_1900) % 10 = (-days_to_1900) % 10
# 地支索引 = (0 - days_to_1900) % 12 = (-days_to_1900) % 12

gan_1900_idx = (-days_to_1900) % 10
zhi_1900_idx = (-days_to_1900) % 12
print(f"1900年1月1日干支索引: 天干{gan_1900_idx}, 地支{zhi_1900_idx}")
print(f"1900年1月1日干支: {TIAN_GAN[gan_1900_idx]}{DI_ZHI[zhi_1900_idx]}")

# 用正确的基准日期重新计算2000年6月13日的干支
print(f"\n使用正确的基准日期重新计算:")
# 1900年1月1日的干支是 {TIAN_GAN[gan_1900_idx]}{DI_ZHI[zhi_1900_idx]}
# 从1900年1月1日到2000年6月13日的天数
days_36688 = (target_date - base_1900).days
print(f"天数差: {days_36688}")

# 正确的计算方式
# 天干索引 = (基准天干索引 + 天数差) % 10
# 地支索引 = (基准地支索引 + 天数差) % 12
correct_gan_idx = (gan_1900_idx + days_36688) % 10
correct_zhi_idx = (zhi_1900_idx + days_36688) % 12
print(f"正确天干索引: {correct_gan_idx} -> {TIAN_GAN[correct_gan_idx]}")
print(f"正确地支索引: {correct_zhi_idx} -> {DI_ZHI[correct_zhi_idx]}")
print(f"正确日柱: {TIAN_GAN[correct_gan_idx]}{DI_ZHI[correct_zhi_idx]}")

# 检查原代码的计算
print(f"\n原代码计算（假设1900年1月1日是甲子日）:")
wrong_gan_idx = days_36688 % 10
wrong_zhi_idx = days_36688 % 12
print(f"错误天干索引: {wrong_gan_idx} -> {TIAN_GAN[wrong_gan_idx]}")
print(f"错误地支索引: {wrong_zhi_idx} -> {DI_ZHI[wrong_zhi_idx]}")
print(f"错误日柱: {TIAN_GAN[wrong_gan_idx]}{DI_ZHI[wrong_zhi_idx]}")

# 验证一些其他已知日期
print("\n" + "=" * 60)
print("验证其他已知日期:")
print("=" * 60)

test_dates = [
    (datetime(2000, 1, 7), "甲子"),  # 已知甲子日
    (datetime(2000, 1, 8), "乙丑"),  # 甲子后一天
    (datetime(2000, 1, 17), "甲戌"), # 甲子后10天
    (datetime(2024, 1, 1), "甲子"),  # 验证2024年1月1日
]

for test_date, expected in test_dates:
    days_from_1900 = (test_date - base_1900).days
    calc_gan_idx = (gan_1900_idx + days_from_1900) % 10
    calc_zhi_idx = (zhi_1900_idx + days_from_1900) % 12
    calc_result = f"{TIAN_GAN[calc_gan_idx]}{DI_ZHI[calc_zhi_idx]}"
    status = "正确" if calc_result == expected else "错误"
    print(f"{test_date.strftime('%Y-%m-%d')}: 计算={calc_result}, 预期={expected} -> {status}")
