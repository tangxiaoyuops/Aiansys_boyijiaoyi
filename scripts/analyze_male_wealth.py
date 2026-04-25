"""
男方八字理财能力分析
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
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


def analyze_male_wealth():
    """分析男方理财能力"""
    
    print("=" * 70)
    print("男方八字理财能力分析")
    print("出生：1997年1月3日 早上8点")
    print("=" * 70)
    
    # 男方命盘
    year, month, day, hour, gender = 1997, 1, 3, 8, '男'
    
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    sizhu = pan_result['sizhu']
    
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【一、男方命盘】")
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
                'type': '正财' if '正' in gan_shishen else '偏财'
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
                print(f"   - {pos['label']}：{pos['gan']}（{pos['shishen']}）{'★ 透出' if pos['position'] in ['yue_zhu', 'shi_zhu'] else ''}")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}（{pos['shishen']}）")
    else:
        print("   命盘中无明显财星")
    
    # 财星统计
    zheng_cai_count = sum(1 for p in cai_positions if '正财' in p.get('shishen', ''))
    pian_cai_count = sum(1 for p in cai_positions if '偏财' in p.get('shishen', ''))
    
    # 检查财星透出
    cai_tou_gan = [p for p in cai_positions if 'gan' in p]
    
    print(f"\n2. 财星统计：")
    print(f"   正财（稳定收入）：{zheng_cai_count}个")
    print(f"   偏财（投资偏财）：{pian_cai_count}个")
    print(f"   财星透出：{len(cai_tou_gan)}个")
    
    print(f"\n3. 财星含义：")
    print(f"   【正财】代表：稳定收入、工资、固定财产、勤俭持家")
    print(f"   【偏财】代表：投资收益、意外之财、商业头脑、慷慨大方")
    
    # ========== 食伤分析 ==========
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
    print(f"   【食神】代表：才华、创造力、稳健生财")
    print(f"   【伤官】代表：聪明、创新、投资眼光")
    print(f"   食伤生财：食伤是财星的源头，代表赚钱能力")
    
    # ========== 比劫分析 ==========
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
    
    # ========== 综合分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、理财能力综合分析】")
    print("=" * 70)
    
    print(f"\n1. 理财要素分析：")
    
    print(f"\n   【财星】（代表财富）")
    print(f"   - 正财数量：{zheng_cai_count}个")
    print(f"   - 偏财数量：{pian_cai_count}个")
    print(f"   - 财星透出：{len(cai_tou_gan)}个")
    if zheng_cai_count + pian_cai_count > 0:
        print(f"   - 财星存在：有理财意识和积蓄能力")
    if len(cai_tou_gan) > 0:
        print(f"   - 财星透出：财运外显，理财能力可见")
    
    print(f"\n   【食伤】（生财之源）")
    print(f"   - 食伤数量：{len(shishang_positions)}个")
    if len(shishang_positions) > 0:
        print(f"   - 有食伤：有赚钱门路和理财头脑")
    
    print(f"\n   【比劫】（花钱倾向）")
    print(f"   - 比劫数量：{len(bijie_positions)}个")
    if len(bijie_positions) > 2:
        print(f"   - 比劫较多：花钱大方，需注意储蓄")
    else:
        print(f"   - 比劫适中：花钱有度")
    
    print(f"\n   【五行】")
    tu_count = wuxing_count.get('土', 0)
    huo_count = wuxing_count.get('火', 0)
    jin_count = wuxing_count.get('金', 0)
    print(f"   - 土（财星五行）：{tu_count}个")
    print(f"   - 火（生财之源）：{huo_count}个")
    print(f"   - 金（官杀）：{jin_count}个")
    
    # 理财特点
    print(f"\n2. 理财特点：")
    
    print(f"\n   【优势】")
    if zheng_cai_count > 0:
        print(f"   ✓ 有正财：稳定收入，勤俭持家")
    if pian_cai_count > 0:
        print(f"   ✓ 有偏财：投资眼光好，有偏财运")
    if len(cai_tou_gan) > 0:
        print(f"   ✓ 财星透出：理财能力可见，财运外显")
    if tu_count >= 2:
        print(f"   ✓ 土旺：财运扎实，有积蓄能力")
    if jin_count >= 2:
        print(f"   ✓ 金旺：有官杀护财，能守住财")
    
    print(f"\n   【需注意】")
    if zheng_cai_count + pian_cai_count == 0:
        print(f"   △ 财星不显：先天财运需大运补足")
    if len(bijie_positions) > 2:
        print(f"   △ 比劫较多：注意冲动消费和被借钱")
    
    # ========== 大运财运分析 ==========
    print(f"\n{'=' * 70}")
    print("【八、大运财运分析】")
    print("=" * 70)
    
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
    current_age = 29
    print(f"\n当前年龄：约{current_age}岁（2026年）")
    
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
        if '食' in dy_gan_shishen or '伤' in dy_gan_shishen:
            print(f"★ 当前是食伤运，适合发展赚钱能力！")
    
    # ========== 与女方对比 ==========
    print(f"\n{'=' * 70}")
    print("【九、与女方理财对比】")
    print("=" * 70)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    男方 vs 女方 理财能力对比                           │
├─────────────────────────────────────────────────────────────────────┤
│  项目          │  男方              │  女方              │  结论      │
├─────────────────────────────────────────────────────────────────────┤
│  财星数量      │  正财1+偏财2       │  正财2+偏财1       │  相当      │
│  财星透出      │  有（时支正财）    │  有（年干偏财）    │  相当      │
│  食伤数量      │  1个               │  4个               │  女方强    │
│  比劫数量      │  2个               │  3个               │  男方好    │
│  五行土（财）  │  3个（旺）         │  1个（弱）         │  男方强    │
│  五行金（护财）│  2个（有）         │  0个（缺）         │  男方强    │
├─────────────────────────────────────────────────────────────────────┤
│  赚钱能力      │  ★★★☆☆          │  ★★★★☆          │  女方强    │
│  存钱能力      │  ★★★★☆          │  ★★★☆☆          │  男方强    │
│  投资能力      │  ★★★☆☆          │  ★★★☆☆          │  相当      │
│  花钱习惯      │  ★★★★☆          │  ★★★☆☆          │  男方好    │
├─────────────────────────────────────────────────────────────────────┤
│  综合评分      │  ★★★★☆          │  ★★★☆☆          │  男方略强  │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    print(f"\n【理财特点对比】")
    print(f"\n男方特点：")
    print(f"   ✓ 土旺（3个）：财运扎实，有积蓄能力")
    print(f"   ✓ 有金（2个）：官杀护财，能守住财")
    print(f"   ✓ 财星多（3个）：理财意识强")
    print(f"   ✓ 比劫少（2个）：花钱有度")
    print(f"   → 男方更擅长：储蓄、稳健理财、守财")
    
    print(f"\n女方特点：")
    print(f"   ✓ 食伤旺（4个）：赚钱能力强，有创意")
    print(f"   ✓ 有正财偏财：收入来源多样")
    print(f"   △ 土弱（1个）：财运需培养")
    print(f"   △ 比劫多（3个）：花钱较大方")
    print(f"   → 女方更擅长：赚钱、创意理财、投资")
    
    print(f"\n【婚后理财建议】")
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                       婚后理财分工建议                                │
├─────────────────────────────────────────────────────────────────────┤
│  男方负责：                                                          │
│  ✓ 家庭储蓄、大额开支规划                                            │
│  ✓ 稳健投资（基金、债券、定期存款）                                    │
│  ✓ 把控家庭财务大方向                                                │
│  ✓ 防范风险、守住财富                                                │
├─────────────────────────────────────────────────────────────────────┤
│  女方负责：                                                          │
│  ✓ 日常开支管理                                                      │
│  ✓ 创意投资、副业发展                                                │
│  ✓ 家庭消费规划                                                      │
│  ✓ 寻找赚钱机会                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  共同决策：                                                          │
│  ✓ 大额投资（房产、车等）                                            │
│  ✓ 家庭财务规划                                                      │
│  ✓ 储蓄目标设定                                                      │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    # ========== 理财建议 ==========
    print(f"\n{'=' * 70}")
    print("【十、男方理财建议】")
    print("=" * 70)
    
    print(f"""
【理财特点总结】

1. 赚钱能力：★★★☆☆（中等）
   - 食伤较少，赚钱主要靠稳定工作
   - 适合：稳定职业、技术工作、管理岗位

2. 存钱能力：★★★★☆（较强）
   - 土旺：财运扎实，有积蓄能力
   - 有金：官杀护财，能守住财
   - 比劫少：花钱有度，不冲动

3. 投资能力：★★★☆☆（中等）
   - 有偏财：可以适度投资
   - 土旺：适合稳健投资（房产、基金定投）

4. 花钱习惯：★★★★☆（良好）
   - 比劫少：花钱有节制
   - 有正财：勤俭持家

【具体建议】

1. 收入来源：
   ✓ 主业收入：稳定工作最重要
   ✓ 兼职收入：可以利用专业技能
   ✓ 投资收入：稳健投资为主

2. 理财方式：
   ✓ 固定储蓄：每月存一定比例（建议30%以上）
   ✓ 基金定投：长期稳健投资
   ✓ 房产投资：土旺适合投资房产
   ✗ 高风险投资：不宜投入太多

3. 大运配合：
   ✓ 当前大运（己卯运）：偏财运，有偏财收入
   ✓ 2027年后（庚辰运）：正财运，收入稳定提升

4. 与女方配合：
   ✓ 男方擅守财，女方擅赚钱
   ✓ 男方管储蓄，女方管开支
   ✓ 优势互补，共同理财

【结论】

男方理财能力：★★★★☆（较强）

优势：
- 土旺：财运扎实，有积蓄能力
- 有金：官杀护财，能守住财
- 比劫少：花钱有度
- 财星多：理财意识强

适合：
- 稳健理财、储蓄、房产投资
- 家庭财务管理的主力

婚后建议：
- 与女方优势互补
- 男方把握财务大方向
- 女方负责日常开支和创意理财
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_wealth()
