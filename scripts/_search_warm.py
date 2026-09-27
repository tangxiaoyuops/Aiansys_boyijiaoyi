# -*- coding: utf-8 -*-
"""
暖局定向搜索：为乙木身弱·子月寒湿男命(1997-01-03 丙子庚子乙巳庚辰)
寻找 1994-2000 出生、火土最旺的女性命局
评分核心（非传统合婚，而是命理补益视角）：
  - 火元素：调候暖局关键，权重最高
  - 土元素：制水培木、藏金收水，次高
  - 木(与日主同气)/其他：低分
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.tools.bazi_calculator import calculate_sizhu

TIAN_GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
DI_ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}

# 天干地支的旺度：干1分，支按藏干加权。这里支给1.5。火/土再按"调候重要性"修正
def warm_score(b):
    score = 0.0
    fire = 0.0
    earth = 0.0
    # 年柱
    yg = b['nian_zhu']['tian_gan']; yz = b['nian_zhu']['di_zhi']
    mg = b['yue_zhu']['tian_gan']; mz = b['yue_zhu']['di_zhi']
    rg = b['ri_zhu']['tian_gan']; rz = b['ri_zhu']['di_zhi']
    sg = b['shi_zhu']['tian_gan']; sz = b['shi_zhu']['di_zhi']
    for gan in [yg, mg, rg, sg]:
        w = TIAN_GAN_WUXING[gan]
        if w == '火':
            fire += 1.0
        elif w == '土':
            earth += 1.0
        elif w == '水':
            score -= 1.0  # 水寒，减分
    for zhi in [yz, mz, rz, sz]:
        w = DI_ZHI_WUXING[zhi]
        if w == '火':
            fire += 1.5
        elif w == '土':
            earth += 1.5
        elif w == '水':
            score -= 1.5
    # 火权重1.6(调候)，土权重1.2(制水)
    score += fire * 1.6 + earth * 1.2
    return round(score, 1), fire, earth

def fmt_b(sizhu):
    return (sizhu['nian_zhu']['tian_gan']+sizhu['nian_zhu']['di_zhi']+' '+
            sizhu['yue_zhu']['tian_gan']+sizhu['yue_zhu']['di_zhi']+' '+
            sizhu['ri_zhu']['tian_gan']+sizhu['ri_zhu']['di_zhi']+' '+
            sizhu['shi_zhu']['tian_gan']+sizhu['shi_zhu']['di_zhi'])

def main():
    results = []
    for y in range(1994, 2001):
        for m in range(1, 13):
            dim = 31 if m in [1,3,5,7,8,10,12] else (29 if m==2 and ((y%4==0 and y%100!=0) or y%400==0) else (28 if m==2 else 30))
            for d in range(1, dim+1):
                for h in [0,1,3,5,7,9,11,13,15,17,19,21]:
                    try:
                        b = calculate_sizhu(y, m, d, h)
                    except Exception:
                        continue
                    s, fire, earth = warm_score(b)
                    results.append((y, m, d, h, b, s, fire, earth))
    results.sort(key=lambda x: x[5], reverse=True)
    print('搜索 1994-2000 共', len(results), '命局，按暖局分排序 Top 40:')
    nian_gz = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
    for i, (y,m,d,h,b,s,fire,earth) in enumerate(results[:40], 1):
        rizhu = b['ri_zhu_tiangan']
        print(f'#{i:2d} 暖分{s:5.1f} (火{fire:.1f}/土{earth:.1f})  {y}-{m:02d}-{d:02d} {h:02d}时  八字 {fmt_b(b)}  日主{rizhu}')

if __name__ == '__main__':
    main()