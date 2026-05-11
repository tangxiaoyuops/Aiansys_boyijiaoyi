# -*- coding: utf-8 -*-
"""
八字排盘逻辑验证测试
验证输入：2000年6月13日15时
"""
import sys
sys.path.insert(0, 'G:/projects/博弈交易/Aiansys_boyijiaoyi')

from datetime import datetime
from core.tools.bazi_calculator import (
    calculate_sizhu, 
    get_tian_gan, 
    get_di_zhi, 
    get_day_gan_zhi, 
    hour_to_shi_chen,
    TIAN_GAN,
    DI_ZHI,
    YUE_GAN_TABLE,
    SHI_GAN_TABLE,
)
from core.tools.solar_terms import get_solar_term_date, get_solar_term, get_month_zhi_by_solar_term

print("=" * 60)
print("八字排盘逻辑验证测试")
print("输入：2000年6月13日15时")
print("=" * 60)

year, month, day, hour = 2000, 6, 13, 15

# 1. 验证时辰转换
print("\n【1. 时辰转换验证】")
shi_chen = hour_to_shi_chen(hour)
print(f"15时 -> 时辰地支: {shi_chen}")
print(f"预期: 申时 (15:00-16:59)")
result1 = "正确" if shi_chen == "申" else "错误"
print(f"结果: {result1}")

# 2. 验证年柱计算
print("\n【2. 年柱计算验证】")
# 2000年的立春日期
lichun_2000 = get_solar_term_date(2000, 0)
print(f"2000年立春日期: {lichun_2000}")

birth_date = datetime(2000, 6, 13, 15)
print(f"出生日期: {birth_date}")

if birth_date < lichun_2000:
    bazi_year = 1999
    print(f"出生日期在立春前，八字年份: {bazi_year}")
else:
    bazi_year = 2000
    print(f"出生日期在立春后，八字年份: {bazi_year}")

nian_gan = get_tian_gan(bazi_year)
nian_zhi = get_di_zhi(bazi_year)
print(f"年柱: {nian_gan}{nian_zhi}")
print(f"预期: 庚辰 (2000年是庚辰年)")
result2 = "正确" if nian_gan == "庚" and nian_zhi == "辰" else "错误"
print(f"结果: {result2}")

# 3. 验证月柱计算（节气）
print("\n【3. 月柱计算验证（节气）】")
term_name, term_index = get_solar_term(year, month, day)
print(f"当前节气: {term_name} (索引: {term_index})")

yue_zhi = get_month_zhi_by_solar_term(year, month, day)
print(f"月支: {yue_zhi}")

# 月干查表
from core.tools.solar_terms import get_month_index_by_solar_term
month_index = get_month_index_by_solar_term(year, month, day)
print(f"月份索引: {month_index}")

yue_gan = YUE_GAN_TABLE.get(nian_gan, {}).get(month_index, "丙")
print(f"月干: {yue_gan} (年干{nian_gan}的第{month_index}个月)")
print(f"月柱: {yue_gan}{yue_zhi}")

# 验证：2000年6月13日应该在芒种之后，小暑之前，属于午月
# 芒种约在6月5-6日，小暑约在7月7日
print(f"预期: 午月 (芒种后，小暑前)")
result3 = "正确" if yue_zhi == "午" else "错误"
print(f"结果: {result3}")

# 4. 验证日柱计算
print("\n【4. 日柱计算验证】")
ri_gan, ri_zhi = get_day_gan_zhi(year, month, day)
print(f"日柱: {ri_gan}{ri_zhi}")

# 手动验证日柱
base_date = datetime(1900, 1, 1)
target_date = datetime(year, month, day)
days_diff = (target_date - base_date).days
print(f"从1900年1月1日到{year}年{month}月{day}日的天数: {days_diff}")
print(f"天干索引: {days_diff % 10} -> {TIAN_GAN[days_diff % 10]}")
print(f"地支索引: {days_diff % 12} -> {DI_ZHI[days_diff % 12]}")

# 2000年6月13日应该是壬申日
# 让我验证一下
print(f"日柱计算结果: {ri_gan}{ri_zhi}")

# 5. 验证时柱计算
print("\n【5. 时柱计算验证】")
shi_gan = SHI_GAN_TABLE.get(ri_gan, {}).get(shi_chen, "甲")
print(f"时干: {shi_gan} (日干{ri_gan}的{shi_chen}时)")
print(f"时柱: {shi_gan}{shi_chen}")

# 6. 完整四柱计算
print("\n【6. 完整四柱计算】")
sizhu = calculate_sizhu(year, month, day, hour)
print(f"年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}")
print(f"月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}")
print(f"日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}")
print(f"时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")

# 7. 验证节气日期计算
print("\n【7. 节气日期验证】")
print("2000年主要节气日期:")
solar_terms_list = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
            '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
for i, term in enumerate(solar_terms_list):
    term_date = get_solar_term_date(2000, i)
    print(f"  {term}: {term_date.strftime('%Y-%m-%d %H:%M')}")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)

# 额外验证：检查2000年6月13日的具体位置
print("\n【额外验证：确定6月13日所在月份】")
mangzhong_date = get_solar_term_date(2000, 8)  # 芒种是第8个节气（从立春开始算）
xiaoshu_date = get_solar_term_date(2000, 10)   # 小暑是第10个节气
print(f"芒种日期: {mangzhong_date}")
print(f"小暑日期: {xiaoshu_date}")
print(f"出生日期: {birth_date}")
print(f"芒种 <= 出生日期 < 小暑: {mangzhong_date <= birth_date < xiaoshu_date}")
