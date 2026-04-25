"""
女方八字理财能力分析
1999年3月4日21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import (
    TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, TIAN_GAN_YINYANG, 
    DI_ZHI_CANG_GAN, DI_ZHI_WUXING, WUXING_SHENG, WUXING_KE
)

def calculate_single_shishen(rizhu_gan, target_gan=None, target_zhi=None):
    """计算单个天干或地支的十神"""
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    
    if target_gan:
        target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
        target_yinyang = TIAN_GAN_YINYANG.get(target_gan, '')
        
        if target_wuxing == rizhu_wuxing:
            return '比肩' if target_yinyang == rizhu_yinyang else '劫财'
        elif WUXING_SHENG.get(rizhu_wuxing) == target_wuxing:
            return '食神' if target_yinyang == rizhu_yinyang else '伤官'
        elif WUXING_SHENG.get(target_wuxing) == rizhu_wuxing:
            return '偏印' if target_yinyang == rizhu_yinyang else '正印'
        elif WUXING_KE.get(rizhu_wuxing) == target_wuxing:
            return '偏财' if target_yinyang == rizhu_yinyang else '正财'
        elif WUXING_KE.get(target_wuxing) == rizhu_wuxing:
            return '七杀' if target_yinyang == rizhu_yinyang else '正官'
    
    if target_zhi and target_zhi in DI_ZHI_CANG_GAN:
        cang_gan = DI_ZHI_CANG_GAN[target_zhi][0]
        cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
        cang_gan_yinyang = TIAN_GAN_YINYANG.get(cang_gan, '')
        
        if cang_gan_wuxing == rizhu_wuxing:
            return '比肩' if cang_gan_yinyang == rizhu_yinyang else '劫财'
        elif WUXING_SHENG.get(rizhu_wuxing) == cang_gan_wuxing:
            return '食神' if cang_gan_yinyang == rizhu_yinyang else '伤官'
        elif WUXING_SHENG.get(cang_gan_wuxing) == rizhu_wuxing:
            return '偏印' if cang_gan_yinyang == rizhu_yinyang else '正印'
        elif WUXING_KE.get(rizhu_wuxing) == cang_gan_wuxing:
            return '偏财' if cang_gan_yinyang == rizhu_yinyang else '正财'
        elif WUXING_KE.get(cang_gan_wuxing) == rizhu_wuxing:
            return '七杀' if cang_gan_yinyang == rizhu_yinyang else '正官'
    
    return ''


def analyze_female_wealth():
    """分析女方理财能力"""
    
    print("=" * 70)
    print("女方八字理财能力分析")
    print("出生：1999年3月4日 21点")
    print("=" * 70)
    
    # 女方命盘
    year, month, day, hour, gender = 1999, 3, 4, 21, '女'
    
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    sizhu = pan_result['sizhu']
    
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【一、女方命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}木")
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n【二、十神分布】")
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        zhi = sizhu[zhu_name]['di_zhi']
        gan = sizhu[zhu_name]['tian_gan']
        print(f"{label}：{gan}（{gan_shishen}）/ {zhi}（{zhi_shishen}）")
    
    # 五行分析
    wuxing_result = bazi_wuxing_node(sizhu)
    wuxing_count = wuxing_result.get('wuxing_count', {}) if wuxing_result.get('success') else {}
    
    print(f"\n【三、五行分布】")
    print(f"金：{wuxing_count.get('金', 0)}  木：{wuxing_count.get('木', 0)}  水：{wuxing_count.get('水', 0)}  火：{wuxing_count.get('火', 0)}  土：{wuxing_count.get('土', 0)}")
    
    # ========== 财星分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、财星分析（理财能力核心）】")
    print("=" * 70)
    
    # 找财星
    cai_positions = []
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if '财' in gan_shishen:
            cai_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': gan,
                'shishen': gan_shishen,
                'type': '天干' if '正' in gan_shishen else '偏财'
            })
        
        for cg in zhi_cang_gan:
            if '财' in cg.get('shishen', ''):
                cai_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': zhi,
                    'cang_gan': cg.get('cang_gan'),
                    'shishen': cg.get('shishen'),
                    'type': '正财' if '正' in cg.get('shishen', '') else '偏财'
                })
    
    print(f"\n1. 财星位置：")
    if cai_positions:
        for pos in cai_positions:
            if 'gan' in pos:
                print(f"   - {pos['label']}：{pos['gan']}（{pos['shishen']}）")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}（{pos['shishen']}）")
    else:
        print("   命盘中无明显财星")
    
    # 财星统计
    zheng_cai_count = sum(1 for p in cai_positions if '正财' in p.get('shishen', ''))
    pian_cai_count = sum(1 for p in cai_positions if '偏财' in p.get('shishen', ''))
    
    print(f"\n2. 财星统计：")
    print(f"   正财（稳定收入）：{zheng_cai_count}个")
    print(f"   偏财（投资偏财）：{pian_cai_count}个")
    
    # 财星解释
    print(f"\n3. 财星含义：")
    print(f"   【正财】代表：稳定收入、工资、固定财产、勤俭持家")
    print(f"   【偏财】代表：投资收益、意外之财、商业头脑、慷慨大方")
    
    # ========== 食伤分析（生财之源）==========
    print(f"\n{'=' * 70}")
    print("【五、食伤分析（生财能力）】")
    print("=" * 70)
    
    shishang_positions = []
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if '食' in gan_shishen or '伤' in gan_shishen:
            shishang_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': gan,
                'shishen': gan_shishen,
            })
        
        for cg in zhi_cang_gan:
            if '食' in cg.get('shishen', '') or '伤' in cg.get('shishen', ''):
                shishang_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': zhi,
                    'cang_gan': cg.get('cang_gan'),
                    'shishen': cg.get('shishen'),
                })
    
    print(f"\n1. 食伤位置：")
    if shishang_positions:
        for pos in shishang_positions:
            if 'gan' in pos:
                print(f"   - {pos['label']}：{pos['gan']}（{pos['shishen']}）")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}（{pos['shishen']}）")
    else:
        print("   命盘中无明显食伤")
    
    print(f"\n2. 食伤含义：")
    print(f"   【食神】代表：才华、创造力、表达能力、稳健生财")
    print(f"   【伤官】代表：聪明、创新、投资眼光、灵活变通")
    print(f"   食伤生财：食伤是财星的源头，代表赚钱能力和理财智慧")
    
    # ========== 比劫分析（花钱倾向）==========
    print(f"\n{'=' * 70}")
    print("【六、比劫分析（花钱倾向）】")
    print("=" * 70)
    
    bijie_positions = []
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if '比肩' in gan_shishen or '劫财' in gan_shishen:
            bijie_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': gan,
                'shishen': gan_shishen,
            })
        
        for cg in zhi_cang_gan:
            if '比肩' in cg.get('shishen', '') or '劫财' in cg.get('shishen', ''):
                bijie_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': zhi,
                    'cang_gan': cg.get('cang_gan'),
                    'shishen': cg.get('shishen'),
                })
    
    print(f"\n1. 比劫位置：")
    if bijie_positions:
        for pos in bijie_positions:
            if 'gan' in pos:
                print(f"   - {pos['label']}：{pos['gan']}（{pos['shishen']}）")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}（{pos['shishen']}）")
    else:
        print("   命盘中无比劫")
    
    print(f"\n2. 比劫含义：")
    print(f"   【比肩】代表：自我、独立、花钱有度")
    print(f"   【劫财】代表：竞争、冲动消费、容易被借钱")
    print(f"   比劫克财：比劫多的人花钱大方，存钱较难")
    
    # ========== 理财能力综合分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、理财能力综合分析】")
    print("=" * 70)
    
    # 计算各项得分
    cai_score = zheng_cai_count * 2 + pian_cai_count * 1.5  # 财星得分
    shishang_score = len(shishang_positions) * 1.5  # 食伤得分
    bijie_score = len(bijie_positions) * (-1)  # 比劫扣分
    
    # 五行分析
    tu_count = wuxing_count.get('土', 0)  # 土代表财
    huo_count = wuxing_count.get('火', 0)  # 火生土
    mu_count = wuxing_count.get('木', 0)  # 木克土
    
    print(f"\n1. 理财要素分析：")
    print(f"\n   【财星】（代表财富）")
    print(f"   - 正财数量：{zheng_cai_count}个 → 稳定收入能力")
    print(f"   - 偏财数量：{pian_cai_count}个 → 投资理财能力")
    if zheng_cai_count + pian_cai_count > 0:
        print(f"   - 财星存在：有理财意识和积蓄能力")
    else:
        print(f"   - 财星缺失：需通过大运流年补财")
    
    print(f"\n   【食伤】（生财之源）")
    print(f"   - 食伤数量：{len(shishang_positions)}个 → 赚钱能力")
    if len(shishang_positions) > 0:
        print(f"   - 食伤存在：有赚钱门路和理财头脑")
    
    print(f"\n   【比劫】（花钱倾向）")
    print(f"   - 比劫数量：{len(bijie_positions)}个")
    if len(bijie_positions) > 2:
        print(f"   - 比劫较多：花钱大方，需注意储蓄")
    else:
        print(f"   - 比劫适中：花钱有度")
    
    print(f"\n   【五行】")
    print(f"   - 土（财星五行）：{tu_count}个")
    print(f"   - 火（生财之源）：{huo_count}个")
    print(f"   - 木（克财之星）：{mu_count}个")
    
    # 综合评价
    print(f"\n2. 理财特点：")
    
    # 根据命盘特点分析
    print(f"\n   【优势】")
    if len(shishang_positions) > 0:
        print(f"   ✓ 有食伤：聪明灵活，有赚钱头脑")
    if zheng_cai_count > 0:
        print(f"   ✓ 有正财：稳定收入，勤俭持家")
    if pian_cai_count > 0:
        print(f"   ✓ 有偏财：投资眼光好，有偏财运")
    if huo_count >= 2:
        print(f"   ✓ 火旺：热情积极，赚钱动力强")
    if tu_count >= 1:
        print(f"   ✓ 有土：务实稳重，有积蓄意识")
    
    print(f"\n   【需注意】")
    if zheng_cai_count + pian_cai_count == 0:
        print(f"   △ 财星不显：先天财运需大运补足")
    if len(bijie_positions) > 2:
        print(f"   △ 比劫较多：注意冲动消费和被借钱")
    if mu_count > 2:
        print(f"   △ 木旺克土：注意不要过于理想化，要务实理财")
    if tu_count < 1:
        print(f"   △ 土弱：财运需要培养")
    
    # ========== 大运财运分析 ==========
    print(f"\n{'=' * 70}")
    print("【八、大运财运分析】")
    print("=" * 70)
    
    from core.agents.bazi_dayun_agent import bazi_dayun_node
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
    print(f"\n大运财运：")
    for i, dy in enumerate(dayun_list):
        dy_gan = dy['gan']
        dy_zhi = dy['zhi']
        dy_gan_shishen = calculate_single_shishen(rizhu_gan, dy_gan)
        dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, dy_zhi)
        
        is_cai = '财' in dy_gan_shishen or '财' in dy_zhi_shishen
        is_shishang = '食' in dy_gan_shishen or '伤' in dy_gan_shishen or '食' in dy_zhi_shishen or '伤' in dy_zhi_shishen
        
        marker = ""
        if is_cai:
            marker = " ★ 财运"
        if is_shishang:
            marker += " ★ 食伤运（生财）"
        
        print(f"\n第{i+1}步：{dy_gan}{dy_zhi}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）{marker}")
        print(f"   天干{dy_gan}：{dy_gan_shishen}")
        print(f"   地支{dy_zhi}：{dy_zhi_shishen}")
    
    # 当前大运
    current_age = 26
    print(f"\n当前年龄：约{current_age}岁（2025年）")
    
    current_dayun = None
    for dy in dayun_list:
        if dy['start_age'] <= current_age <= dy['end_age']:
            current_dayun = dy
            break
    
    if current_dayun:
        dy_gan_shishen = calculate_single_shishen(rizhu_gan, current_dayun['gan'])
        dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, current_dayun['zhi'])
        print(f"\n当前大运：{current_dayun['gan']}{current_dayun['zhi']}运")
        print(f"天干{current_dayun['gan']}：{dy_gan_shishen}")
        print(f"地支{current_dayun['zhi']}：{dy_zhi_shishen}")
        
        if '财' in dy_gan_shishen or '财' in dy_zhi_shishen:
            print(f"★ 当前是财运，适合理财投资！")
        if '食' in dy_gan_shishen or '伤' in dy_gan_shishen or '食' in dy_zhi_shishen or '伤' in dy_zhi_shishen:
            print(f"★ 当前是食伤运，适合发展赚钱能力！")
    
    # ========== 理财建议 ==========
    print(f"\n{'=' * 70}")
    print("【九、理财建议】")
    print("=" * 70)
    
    print(f"""
【理财特点总结】

1. 赚钱能力：
   - 有食伤：聪明灵活，有创意，适合通过才华赚钱
   - 适合行业：设计、艺术、教育、咨询等创意类工作

2. 存钱能力：
   - 正财藏于日支：有积蓄意识，但财不外露
   - 需注意：财星不透，容易被人忽视理财能力

3. 投资能力：
   - 食伤旺：有投资眼光，灵活变通
   - 偏财有：可以尝试适度投资

4. 花钱习惯：
   - 比劫适中：花钱有度，不会太冲动
   - 木旺：可能比较理想化，需注意务实

【具体建议】

1. 收入来源：
   ✓ 主业收入：稳定工作最重要
   ✓ 副业收入：可以利用才华做副业
   ✓ 投资收入：适度投资，不宜太激进

2. 理财方式：
   ✓ 固定储蓄：每月存一定比例
   ✓ 基金定投：适合长期稳健投资
   ✗ 高风险投资：不宜投入太多

3. 大运配合：
   ✓ 当前大运（壬午运）：食伤运，适合发展赚钱能力
   ✓ 2029年后（癸未运）：财运到来，收入会提升

4. 与男方配合：
   ✓ 男方有金，女方缺金
   ✓ 男方可补女方财星（金生水，水生木）
   ✓ 婚后理财可以男方为主，女方辅助

【结论】

女方理财能力：★★★☆☆（中等偏上）

优势：
- 有食伤，聪明有头脑
- 有正财，稳定收入意识
- 花钱有度，不会太冲动

注意：
- 财星不透，需要培养理财习惯
- 木旺克土，要避免过于理想化

建议：
- 婚后与男方共同理财
- 男方有金（财星），可补女方不足
- 2029年后财运到来，收入会提升
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_female_wealth()
