# -*- coding: utf-8 -*-
"""
八字排盘逻辑详细验证
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
    MONTH_TO_DI_ZHI,
)
from core.tools.solar_terms import get_solar_term_date, get_solar_term, get_month_zhi_by_solar_term, get_month_index_by_solar_term

year, month, day, hour = 2000, 6, 13, 15

# 保存结果到文件
results = []

def add_result(title, content):
    results.append(f"\n{title}")
    results.append(content)

add_result("=" * 60, "八字排盘逻辑验证报告")
add_result("输入参数", f"年份: {year}, 月份: {month}, 日期: {day}, 时辰: {hour}")
add_result("=" * 60, "")

# 1. 时辰转换
shi_chen = hour_to_shi_chen(hour)
add_result("【1. 时辰转换】", f"15时 -> {shi_chen}时 (预期: 申时) -> {'正确' if shi_chen == '申' else '错误'}")

# 2. 年柱
lichun_2000 = get_solar_term_date(2000, 0)
birth_date = datetime(2000, 6, 13, 15)
bazi_year = 2000 if birth_date >= lichun_2000 else 1999
nian_gan = get_tian_gan(bazi_year)
nian_zhi = get_di_zhi(bazi_year)
add_result("【2. 年柱】", f"八字年份: {bazi_year}, 年柱: {nian_gan}{nian_zhi} (预期: 庚辰) -> {'正确' if nian_gan == '庚' and nian_zhi == '辰' else '错误'}")

# 3. 月柱（节气）
term_name, term_index = get_solar_term(year, month, day)
yue_zhi = get_month_zhi_by_solar_term(year, month, day)
month_index = get_month_index_by_solar_term(year, month, day)
yue_gan = YUE_GAN_TABLE.get(nian_gan, {}).get(month_index, '丙')
add_result("【3. 月柱】", f"节气: {term_name}, 月支: {yue_zhi}, 月份索引: {month_index}")
add_result("", f"庚年第{month_index}月天干: {yue_gan}, 月柱: {yue_gan}{yue_zhi}")
add_result("", f"预期: 壬午 -> {'正确' if yue_gan == '壬' and yue_zhi == '午' else '错误'}")

# 4. 日柱
ri_gan, ri_zhi = get_day_gan_zhi(year, month, day)
base_date = datetime(1900, 1, 1)
target_date = datetime(year, month, day)
days_diff = (target_date - base_date).days
gan_idx = days_diff % 10
zhi_idx = days_diff % 12
add_result("【4. 日柱】", f"从1900年1月1日起算，天数差: {days_diff}")
add_result("", f"天干索引: {gan_idx} -> {TIAN_GAN[gan_idx]}, 地支索引: {zhi_idx} -> {DI_ZHI[zhi_idx]}")
add_result("", f"日柱: {ri_gan}{ri_zhi} (预期: 壬申) -> {'正确' if ri_gan == '壬' and ri_zhi == '申' else '错误'}")

# 5. 时柱
shi_gan = SHI_GAN_TABLE.get(ri_gan, {}).get(shi_chen, '甲')
add_result("【5. 时柱】", f"壬日{shi_chen}时天干: {shi_gan}")
add_result("", f"时柱: {shi_gan}{shi_chen} (预期: 戊申) -> {'正确' if shi_gan == '戊' and shi_chen == '申' else '错误'}")

# 6. 完整四柱
sizhu = calculate_sizhu(year, month, day, hour)
sizhu_str = f"{sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}年 " \
            f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}月 " \
            f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}日 " \
            f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}时"
add_result("【6. 最终四柱】", sizhu_str)
add_result("", f"预期: 庚辰年 壬午月 壬申日 戊申时")

# 7. 节气日期精确度检查
add_result("【7. 节气日期检查】", "2000年关键节气日期（简化算法计算）:")
solar_terms_list = ['立春', '惊蛰', '清明', '立夏', '芒种', '小暑']
for term in solar_terms_list:
    idx = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑'].index(term)
    term_date = get_solar_term_date(2000, idx)
    add_result("", f"  {term}: {term_date.strftime('%Y-%m-%d')}")

# 网上查的2000年实际节气日期（供对比）
add_result("", "\n实际节气日期（天文计算）:")
add_result("", "  立春: 2000-02-04")
add_result("", "  惊蛰: 2000-03-05")
add_result("", "  清明: 2000-04-05")
add_result("", "  立夏: 2000-05-05")
add_result("", "  芒种: 2000-06-05")
add_result("", "  小暑: 2000-07-07")

# 8. 月干查表验证
add_result("【8. 月干查表验证】", f"庚年各月天干:")
for m in range(1, 13):
    gan = YUE_GAN_TABLE.get('庚', {}).get(m, '')
    zhi = MONTH_TO_DI_ZHI.get(m, '')
    add_result("", f"  第{m}月({zhi}月): {gan}{zhi}")

# 9. 时干查表验证（壬日）
add_result("【9. 时干查表验证】", f"壬日各时辰天干:")
for shi in DI_ZHI:
    gan = SHI_GAN_TABLE.get('壬', {}).get(shi, '')
    add_result("", f"  {shi}时: {gan}{shi}")

# 写入文件
output = '\n'.join(results)
with open('G:/projects/博弈交易/Aiansys_boyijiaoyi/bazi_verify_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print("验证结果已保存到 bazi_verify_result.txt")