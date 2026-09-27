# -*- coding: utf-8 -*-
"""
排盘回归测试：验证节气/年柱/月柱修复（此前月柱经常差一个月）

覆盖：
1. 权威锚点（2024元旦/春节/正月初二/惊蛰 已从万年历核实）
2. 交节边界不同时刻的月柱切换（立春/惊蛰/清明）
3. 立春前出生换年（年柱属上一年）
4. 五鼠遁时柱验算
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.tools.bazi_calculator import calculate_sizhu

# (年,月,日,时, 期望'年柱 月柱 日柱 时柱', 说明)
TEST_CASES = [
    # —— 权威锚点（万年历核实） ——
    (2024, 1, 1, 11,  '癸卯 甲子 甲子 庚午', '2024元旦午时'),
    (2024, 2, 10, 11, '甲辰 丙寅 甲辰 庚午', '2024春节午时'),
    (2024, 2, 11, 11, '甲辰 丙寅 乙巳 壬午', '2024正月初二午时'),
    (2024, 3, 5, 12,  '甲辰 丁卯 戊辰 戊午', '2024惊蛰日午时'),
    (2024, 3, 6, 12,  '甲辰 丁卯 己巳 庚午', '2024惊蛰后午时'),
    # —— 交节边界：同一天不同时刻，月柱/年柱必须切换 ——
    (2024, 2, 4, 8,   '癸卯 乙丑 戊戌 丙辰', '2024立春前08:00 → 癸卯年丑月'),
    (2024, 2, 4, 20,  '甲辰 丙寅 戊戌 壬戌', '2024立春后20:00 → 甲辰年寅月'),
    (2024, 3, 5, 9,   '甲辰 丙寅 戊辰 丁巳', '2024惊蛰前09:00 → 寅月'),
    (2024, 3, 5, 14,  '甲辰 丁卯 戊辰 己未', '2024惊蛰后14:00 → 卯月'),
    (2024, 4, 4, 20,  '甲辰 戊辰 戊戌 壬戌', '2024清明后20:00 → 辰月'),
    # —— 立春前出生，年柱属上一年 ——
    (2001, 2, 3, 10,  '庚辰 己丑 丁酉 乙巳', '2001立春前 → 庚辰年'),
    # —— 五鼠遁验算 ——
    (2001, 3, 15, 4,  '辛巳 辛卯 丁丑 壬寅', '丁日寅时=壬寅'),
    (2001, 3, 15, 6,  '辛巳 辛卯 丁丑 癸卯', '丁日卯时=癸卯'),
    (2024, 2, 11, 6,  '甲辰 丙寅 乙巳 己卯', '乙日卯时=己卯'),
]


def run():
    fail = 0
    print('=' * 80)
    print('排盘回归测试（年柱/月柱/日柱/时柱）')
    print('=' * 80)
    for y, m, d, h, expected, desc in TEST_CASES:
        s = calculate_sizhu(y, m, d, h)
        got = (s['nian_zhu']['tian_gan'] + s['nian_zhu']['di_zhi'] + ' ' +
               s['yue_zhu']['tian_gan'] + s['yue_zhu']['di_zhi'] + ' ' +
               s['ri_zhu']['tian_gan'] + s['ri_zhu']['di_zhi'] + ' ' +
               s['shi_zhu']['tian_gan'] + s['shi_zhu']['di_zhi'])
        ok = got == expected
        if not ok:
            fail += 1
        print(f"  {'[OK]' if ok else '[FAIL]'} {desc}: {got}" + ('' if ok else f'  期望[{expected}]'))

    print()
    print(f'结果: {len(TEST_CASES) - fail}/{len(TEST_CASES)} 通过')
    if fail:
        print('[FAIL] 存在失败用例')
        sys.exit(1)
    print('[OK] 全部通过 —— 年柱/月柱修复正常，无回归')


if __name__ == '__main__':
    run()