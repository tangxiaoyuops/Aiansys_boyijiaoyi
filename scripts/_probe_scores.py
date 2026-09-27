# -*- coding: utf-8 -*-
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.tools.bazi_calculator import calculate_sizhu
from core.tools.hepan_calculator import calculate_hepan

me = calculate_sizhu(1997, 1, 3, 8)
me['gender'] = '男'

def fmt(sizhu):
    return (sizhu['nian_zhu']['tian_gan'] + sizhu['nian_zhu']['di_zhi'] + ' ' +
            sizhu['yue_zhu']['tian_gan'] + sizhu['yue_zhu']['di_zhi'] + ' ' +
            sizhu['ri_zhu']['tian_gan'] + sizhu['ri_zhu']['di_zhi'] + ' ' +
            sizhu['shi_zhu']['tian_gan'] + sizhu['shi_zhu']['di_zhi'])

def show(y, m, d, h, label):
    b = calculate_sizhu(y, m, d, h)
    b['gender'] = '女'
    r = calculate_hepan(me, b, hepan_type='couple', gender_a='男', gender_b='女')
    s = r['scores']
    print('[%s] %d-%d-%d 时%d 八字:%s' % (label, y, m, d, h, fmt(b)))
    print('   地支=%s 五行=%s 日主=%s 天干=%s 十神=%s | 总分=%s' % (
        s['di_zhi'], s['wuxing'], s['rizhu'], s['tian_gan'], s['shishen'], s['total']))

# 94分的乙丑日
show(1999, 1, 13, 3, '乙丑日寅时(94)')
# 对照：完全不同的日主与地支
show(1994, 6, 15, 11, '丙午日午时(对照)')
# 对照2：甲子日
show(1994, 2, 1, 1, '甲子日丑时(对照2)')