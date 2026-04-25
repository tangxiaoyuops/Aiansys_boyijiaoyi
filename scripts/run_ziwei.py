# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.tools.ziwei_calculator import create_pan, get_palace_name
from core.tools.ziwei_si_hua import apply_si_hua_to_pan, analyze_si_hua_impact

# 1997年1月3日 早上8点
year, month, day, hour, gender = 1997, 1, 3, 8, '男'
pan_data = create_pan(year, month, day, hour, gender)
year_gan = pan_data['birth_info']['year_gan']
pan_data = apply_si_hua_to_pan(pan_data, year_gan)
si_hua_analysis = analyze_si_hua_impact(pan_data)

print('='*70)
print('紫微斗数命盘分析 - 男命')
print('出生：1997年1月3日 早上8点（辰时）')
print('='*70)

birth_info = pan_data['birth_info']
print(f'公历：{birth_info["year"]}年{birth_info["month"]}月{birth_info["day"]}日 {birth_info["hour"]}时')
print(f'农历：{birth_info["lunar_year"]}年{birth_info["lunar_month"]}月{birth_info["lunar_day"]}日')
print(f'年柱：{birth_info["year_gan"]}{birth_info["year_zhi"]}')
print(f'命宫：{get_palace_name(pan_data["ming_gong"])}')
print(f'身宫：{get_palace_name(pan_data["shen_gong"])}')
print(f'紫微星：{get_palace_name(pan_data["ziwei_palace"])}')

print('='*70)
print('【十二宫主星】')
print('='*70)
palace_names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母']
for i, palace in enumerate(pan_data['palaces']):
    main = palace.get('main_stars', [])
    other = palace.get('other_stars', [])
    si_hua = palace.get('si_hua', [])
    marker = ''
    if pan_data['ming_gong'] == i: marker = ' [命宫]'
    if pan_data['shen_gong'] == i: marker += ' [身宫]'
    stars = ', '.join(main) if main else '无主星'
    si_hua_str = f' 四化:{",".join(si_hua)}' if si_hua else ''
    print(f'{palace_names[i]}：{stars}{marker}{si_hua_str}')
    if other:
        print(f'  辅星：{", ".join(other)}')

print('='*70)
print('【四化分析】')
print('='*70)
print(si_hua_analysis.get('summary', ''))
for imp in si_hua_analysis.get('impacts', [])[:8]:
    print(f'  - {imp}')

print('='*70)
print('【重点解读】')
print('='*70)
ming = pan_data['palaces'][pan_data['ming_gong']]
print(f'命宫主星：{", ".join(ming.get("main_stars", [])) if ming.get("main_stars") else "无主星"}')
fuqi = pan_data['palaces'][2]
print(f'夫妻宫主星：{", ".join(fuqi.get("main_stars", [])) if fuqi.get("main_stars") else "无主星"}')
guanlu = pan_data['palaces'][8]
print(f'官禄宫主星：{", ".join(guanlu.get("main_stars", [])) if guanlu.get("main_stars") else "无主星"}')
caibo = pan_data['palaces'][4]
print(f'财帛宫主星：{", ".join(caibo.get("main_stars", [])) if caibo.get("main_stars") else "无主星"}')
