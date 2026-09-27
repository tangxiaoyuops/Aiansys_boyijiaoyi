# -*- coding: utf-8 -*-
"""
调候+扶抑综合评分：为乙木身弱·子月寒湿男命(1997-01-03 丙子庚子乙巳庚辰)
寻找火候适中(不焚不晦)、木水有根(不枯不溺)的中和女性命局。
关键辩证：
  - 火：太弱不暖，太旺焚木 -> 设最优区间
  - 土：湿土培根佳，燥土渴木不佳
  - 水：润木生身佳，但子月本就寒 -> 需要有火配
  - 木：帮身生根佳
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.tools.bazi_calculator import calculate_sizhu

TG = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
DZ = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
# 地支含火(藏火)判暖：午(满火)巳(火), 未/戌含火微
LICHANG_HOT = {'午':1.5,'巳':1.0,'未':0.5,'戌':0.5}

def score(b):
    sizhu = [b['nian_zhu'], b['yue_zhu'], b['ri_zhu'], b['shi_zhu']]
    fire = 0.0
    earth = 0.0
    water = 0.0
    wood = 0.0
    for p in sizhu:
        wg = TG[p['tian_gan']]
        gj = LICHANG_HOT.get(p['di_zhi'], 0.0)
        if wg == '火': fire += 1.0
        elif wg == '土':
            earth += 1.0
            if p['di_zhi'] in ['辰','丑','未']:
                fire += 0.4   # 湿土略带藏火
        elif wg == '水': water += 1.0
        elif wg == '木': wood += 1.0
        # 地支
        wz = DZ[p['di_zhi']]
        if wz == '火': fire += 1.4
        elif wz == '土': earth += 1.4
        elif wz == '水': water += 1.4
        elif wz == '木': wood += 1.4

    # 火候：最佳区间 3~6；<2 不暖，>7 焚身
    if fire < 2.0:
        fire_ok = fire - 2.0     # 负分代表不够暖
    elif fire <= 6.0:
        fire_ok = 6.0 - abs(fire - 4.0) + 2.0   # 顶值在4左右
    else:
        fire_ok = - (fire - 6.0) * 2            # 过火扣分
    # 土：湿土培木佳，但太多板结
    earth_ok = earth if earth <= 5.0 else 5.0 - (earth - 5.0) * 2
    # 木：帮身佳
    wood_ok = wood * 1.2
    # 水：寒水需有火润，这里水少加分
    water_ok = max(0, 3.0 - water * 0.5)
    return round(fire_ok + earth_ok + wood_ok + water_ok, 2), round(fire,1), round(earth,1), round(wood,1), round(water,1)

def fmt_b(s):
    return (s['nian_zhu']['tian_gan']+s['nian_zhu']['di_zhi']+' '+
            s['yue_zhu']['tian_gan']+s['yue_zhu']['di_zhi']+' '+
            s['ri_zhu']['tian_gan']+s['ri_zhu']['di_zhi']+' '+
            s['shi_zhu']['tian_gan']+s['shi_zhu']['di_zhi'])

def main():
    res = []
    for y in range(1994, 2001):
        for m in range(1, 13):
            dim = 31 if m in [1,3,5,7,8,10,12] else (29 if m==2 and ((y%4==0 and y%100!=0) or y%400==0) else (28 if m==2 else 30))
            for d in range(1, dim+1):
                for h in [0,1,3,5,7,9,11,13,15,17,19,21]:
                    try:
                        b = calculate_sizhu(y, m, d, h)
                    except Exception:
                        continue
                    s, f, e, wd, wt = score(b)
                    res.append((y,m,d,h,b,s,f,e,wd,wt))
    res.sort(key=lambda x: x[5], reverse=True)
    print('搜索 1994-2000 共', len(res), '命局，按「调候与扶抑综合」排序 Top 40:')
    for i, (y,m,d,h,b,s,f,e,wd,wt) in enumerate(res[:40], 1):
        print(f'#{i:2d} 综合分{s:5.1f} (火{f:.1f}/土{e:.1f}/木{wd:.1f}/水{wt:.1f})  {y}-{m:02d}-{d:02d} {h:02d}时  八字[{fmt_b(b)}] 日主{b["ri_zhu_tiangan"]}')

if __name__ == '__main__':
    main()