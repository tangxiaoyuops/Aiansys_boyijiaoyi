"""
分析八字财运
男: 1997年1月3日 早上8点
八字: 丙子 辛丑 乙巳 庚辰
"""
# -*- coding: utf-8 -*-
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import calculate_sizhu


def analyze_wealth():
    """分析财运"""
    
    # 计算八字
    sizhu = calculate_sizhu(1997, 1, 3, 8)
    
    print("="*60)
    print("八字财运分析")
    print("="*60)
    
    # 基本信息
    print(f"\n【基本信息】")
    print(f"出生: 1997年1月3日 早上8点")
    print(f"八字: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']} "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']} "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']} "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
    print(f"日主: {sizhu['ri_zhu_tiangan']} (木)")
    
    # 天干地支
    gans = [
        sizhu['nian_zhu']['tian_gan'],
        sizhu['yue_zhu']['tian_gan'],
        sizhu['ri_zhu']['tian_gan'],
        sizhu['shi_zhu']['tian_gan']
    ]
    zhis = [
        sizhu['nian_zhu']['di_zhi'],
        sizhu['yue_zhu']['di_zhi'],
        sizhu['ri_zhu']['di_zhi'],
        sizhu['shi_zhu']['di_zhi']
    ]
    
    # 五行对应
    tian_gan_wuxing = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火',
        '戊': '土', '己': '土', '庚': '金', '辛': '金',
        '壬': '水', '癸': '水',
    }
    di_zhi_wuxing = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水',
    }
    
    # 十神定义
    # 日主乙木，木的财星是土（我克者为财）
    # 木克土，所以土是财星
    # 戊土是偏财（阳土），己土是正财（阴土）
    
    print(f"\n【财星分析】")
    print(f"日主乙木，木克土，土为财星")
    print(f"  - 戊土 = 偏财（大财、横财、投资财）")
    print(f"  - 己土 = 正财（工资、稳定收入）")
    
    # 查找财星
    ca_xing = []  # 财星位置
    for i, gan in enumerate(gans):
        wx = tian_gan_wuxing.get(gan, '')
        if wx == '土':
            zhu_name = ['年干', '月干', '日干', '时干'][i]
            ca_type = '偏财' if gan == '戊' else '正财'
            ca_xing.append({'pos': zhu_name, 'gan': gan, 'type': ca_type})
    
    for i, zhi in enumerate(zhis):
        wx = di_zhi_wuxing.get(zhi, '')
        if wx == '土':
            zhu_name = ['年支', '月支', '日支', '时支'][i]
            ca_xing.append({'pos': zhu_name, 'zhi': zhi, 'type': '财星根'})
    
    print(f"\n八字中的财星:")
    if ca_xing:
        for ca in ca_xing:
            if 'gan' in ca:
                print(f"  - {ca['pos']}: {ca['gan']} ({ca['type']})")
            else:
                print(f"  - {ca['pos']}: {ca['zhi']} ({ca['type']})")
    else:
        print(f"  天干无财星透出")
    
    # 地支藏干中的财星
    print(f"\n地支藏干:")
    cang_gan_map = {
        '子': ['癸'],  # 水
        '丑': ['己', '癸', '辛'],  # 土水金
        '寅': ['甲', '丙', '戊'],  # 木火土
        '卯': ['乙'],  # 木
        '辰': ['戊', '乙', '癸'],  # 土木水
        '巳': ['丙', '庚', '戊'],  # 火金土
        '午': ['丁', '己'],  # 火土
        '未': ['己', '丁', '乙'],  # 土火木
        '申': ['庚', '壬', '戊'],  # 金水土
        '酉': ['辛'],  # 金
        '戌': ['戊', '辛', '丁'],  # 土金火
        '亥': ['壬', '甲'],  # 水木
    }
    
    for i, zhi in enumerate(zhis):
        zhu_name = ['年支', '月支', '日支', '时支'][i]
        cang = cang_gan_map.get(zhi, [])
        cang_str = ', '.join(cang)
        # 检查藏干中的财星
        ca_in_cang = [g for g in cang if tian_gan_wuxing.get(g) == '土']
        if ca_in_cang:
            print(f"  {zhu_name}({zhi}): {cang_str} ← 藏有财星{ca_in_cang}")
        else:
            print(f"  {zhu_name}({zhi}): {cang_str}")
    
    # 五行统计
    print(f"\n【五行统计】")
    wuxing_count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
    for gan in gans:
        wx = tian_gan_wuxing.get(gan, '')
        if wx:
            wuxing_count[wx] += 1
    for zhi in zhis:
        wx = di_zhi_wuxing.get(zhi, '')
        if wx:
            wuxing_count[wx] += 1
    
    for wx, count in wuxing_count.items():
        bar = '█' * count
        print(f"  {wx}: {bar} ({count})")
    
    # 身强身弱判断
    print(f"\n【身强身弱】")
    # 日主乙木
    # 生我者：水（印星）
    # 同我者：木（比劫）
    sheng_wo = wuxing_count['水']  # 印
    tong_wo = wuxing_count['木']   # 比劫
    wo_sheng = wuxing_count['火']  # 食伤
    wo_ke = wuxing_count['土']     # 财
    ke_wo = wuxing_count['金']     # 官杀
    
    zi_shen = sheng_wo + tong_wo  # 自身力量
    hao_xie = wo_sheng + wo_ke + ke_wo  # 耗泄力量
    
    print(f"  印星(水): {sheng_wo}  比劫(木): {tong_wo}")
    print(f"  食伤(火): {wo_sheng}  财星(土): {wo_ke}  官杀(金): {ke_wo}")
    print(f"  自身力量(印+比劫): {zi_shen}")
    print(f"  耗泄力量(食伤+财+官杀): {hao_xie}")
    
    if zi_shen > hao_xie:
        shen_qiang = True
        print(f"  判断: 身强 (自身力量 > 耗泄力量)")
    else:
        shen_qiang = False
        print(f"  判断: 身弱 (自身力量 < 耗泄力量)")
    
    # 财运分析
    print(f"\n【财运分析】")
    
    # 1. 财星情况
    print(f"\n1. 财星透出情况:")
    has_gan_ca = any('gan' in ca for ca in ca_xing)
    if has_gan_ca:
        print(f"   天干有财星透出，财气外露，求财机会多")
    else:
        print(f"   天干财星不透，财藏于地支，需努力挖掘")
    
    # 2. 财星根气
    print(f"\n2. 财星根气:")
    ca_gen = [ca for ca in ca_xing if 'zhi' in ca]
    if len(ca_gen) >= 2:
        print(f"   财星有根({len(ca_gen)}个地支)，财源稳固")
    elif len(ca_gen) == 1:
        print(f"   财星有根，但根气不旺")
    else:
        print(f"   财星无根，财来财去，难聚财")
    
    # 3. 身强身弱对财运的影响
    print(f"\n3. 身强身弱与财运:")
    if shen_qiang:
        print(f"   身强能担财，可以主动求财、投资创业")
        print(f"   走食伤运(火)或财运(土)时财运好")
        print(f"   走比劫运(木)或印运(水)时破财风险大")
    else:
        print(f"   身弱不胜财，财多反而为祸")
        print(f"   需走印运(水)或比劫运(木)帮身才能得财")
        print(f"   不宜冒险投资，适合稳定工作")
    
    # 4. 具体财运特点
    print(f"\n【财运特点】")
    
    # 月支丑土 - 财星在月令
    print(f"1. 月支丑土为财星")
    print(f"   - 财星得令，先天财运不错")
    print(f"   - 月柱辛丑，辛金克乙木，官星透出")
    print(f"   - 适合正职工作、体制内、大公司")
    
    # 时干庚金 - 官星
    print(f"\n2. 时干庚金为正官")
    print(f"   - 官星透出，有事业心")
    print(f"   - 庚金合乙木(日主)，官来合身")
    print(f"   - 工作稳定，有贵人相助")
    
    # 日支巳火 - 食神
    print(f"\n3. 日支巳火为食神")
    print(f"   - 食神生财，有赚钱头脑")
    print(f"   - 巳火生丑土(月支财星)，食神生财")
    print(f"   - 适合技术、创意、策划类工作")
    
    # 年干丙火 - 伤官
    print(f"\n4. 年干丙火为伤官")
    print(f"   - 伤官透出，聪明有才华")
    print(f"   - 但伤官见官(丙火克庚金)，事业有波折")
    print(f"   - 不宜过于张扬，低调求财")
    
    # 总结
    print(f"\n{'='*60}")
    print(f"【财运总结】")
    print(f"{'='*60}")
    
    print(f"""
整体财运：中等偏上

优势：
  - 月令有财星，先天财运根基好
  - 食神生财，有赚钱能力和头脑
  - 官星合身，工作稳定有靠山
  - 身弱但有印星(年支子水)帮身

劣势：
  - 天干财星不透，财不外露
  - 身弱不胜大财，不宜冒险
  - 伤官见官，事业有阻碍

适合方向：
  - 正职工作、稳定收入为主
  - 技术、策划、创意类工作
  - 不适合高风险投资
  - 中年后财运渐好

财富等级：
  - 小富可期，大富难求
  - 一生衣食无忧
  - 靠积累致富，非横财
""")


if __name__ == "__main__":
    analyze_wealth()
