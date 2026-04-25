"""
深入分析女方命盘：七杀格局与婚运时间
1999年3月4日21点女生
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
    calculate_sizhu, calculate_shishen, calculate_wuxing, 
    TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_CANG_GAN,
    WUXING_SHENG, WUXING_KE
)

def analyze_qisha_pattern():
    """分析女方七杀格局"""
    
    print("=" * 70)
    print("女方命盘深度分析：七杀格局与婚运")
    print("=" * 70)
    
    # 女方：1999年3月4日 21点
    year = 1999
    month = 3
    day = 4
    hour = 21
    gender = '女'
    
    # 排盘
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    if not pan_result.get('success'):
        print(f"排盘失败: {pan_result.get('error')}")
        return
    
    sizhu = pan_result['sizhu']
    
    # 获取各柱信息
    nian_zhu = sizhu['nian_zhu']  # 年柱
    yue_zhu = sizhu['yue_zhu']    # 月柱
    ri_zhu = sizhu['ri_zhu']      # 日柱
    shi_zhu = sizhu['shi_zhu']    # 时柱
    rizhu_gan = sizhu['ri_zhu_tiangan']  # 日主
    
    print(f"\n【一、八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']} (日主)")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    
    # 日主信息
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    print(f"\n日主：{rizhu_gan}（{rizhu_yinyang}{rizhu_wuxing}）")
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n【二、十神分析】")
    print(f"年柱：{shishen_data.get('nian_zhu', {}).get('gan_shishen', '')}（天干）/{shishen_data.get('nian_zhu', {}).get('zhi_shishen', '')}（地支）")
    print(f"月柱：{shishen_data.get('yue_zhu', {}).get('gan_shishen', '')}（天干）/{shishen_data.get('yue_zhu', {}).get('zhi_shishen', '')}（地支）")
    print(f"日柱：日主/{shishen_data.get('ri_zhu', {}).get('zhi_shishen', '')}（地支）")
    print(f"时柱：{shishen_data.get('shi_zhu', {}).get('gan_shishen', '')}（天干）/{shishen_data.get('shi_zhu', {}).get('zhi_shishen', '')}（地支）")
    
    # 检查地支藏干十神
    print(f"\n地支藏干十神：")
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi = sizhu[zhu_name]['di_zhi']
        cang_gan_shishen = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        if cang_gan_shishen:
            zhu_label = {'nian_zhu': '年支', 'yue_zhu': '月支', 'ri_zhu': '日支', 'shi_zhu': '时支'}
            print(f"  {zhu_label[zhu_name]}{zhi}：{cang_gan_shishen}")
    
    # 五行分析
    wuxing_result = bazi_wuxing_node(sizhu)
    wuxing_count = wuxing_result.get('wuxing_count', {}) if wuxing_result.get('success') else {}
    
    print(f"\n【三、五行分布】")
    print(f"金：{wuxing_count.get('金', 0)}  木：{wuxing_count.get('木', 0)}  水：{wuxing_count.get('水', 0)}  火：{wuxing_count.get('火', 0)}  土：{wuxing_count.get('土', 0)}")
    
    # ========== 七杀分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、七杀格局深度分析】")
    print("=" * 70)
    
    # 找七杀位置
    qisha_positions = []
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if gan_shishen == '七杀':
            qisha_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': sizhu[zhu_name]['tian_gan'],
                'type': '天干'
            })
        if zhi_shishen == '七杀':
            qisha_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}地支本气',
                'zhi': sizhu[zhu_name]['di_zhi'],
                'type': '地支本气'
            })
        for cg in zhi_cang_gan:
            if cg.get('shishen') == '七杀':
                qisha_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支藏干',
                    'zhi': sizhu[zhu_name]['di_zhi'],
                    'cang_gan': cg.get('cang_gan'),
                    'type': '地支藏干'
                })
    
    print(f"\n1. 七杀位置：")
    if qisha_positions:
        for pos in qisha_positions:
            if pos['type'] == '天干':
                print(f"   - {pos['label']}：{pos['gan']}（七杀）")
            elif pos['type'] == '地支本气':
                print(f"   - {pos['label']}：{pos['zhi']}（本气七杀）")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}（七杀）")
    else:
        print("   命盘中无明显七杀")
    
    # ========== 夫星分析（女命看官杀）==========
    print(f"\n2. 夫星分析（女命以官杀为夫星）：")
    
    # 找正官和偏官（七杀）
    guan_positions = []
    sha_positions = []
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if gan_shishen == '正官':
            guan_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': sizhu[zhu_name]['tian_gan'],
            })
        if gan_shishen == '七杀':
            sha_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': sizhu[zhu_name]['tian_gan'],
            })
        
        for cg in zhi_cang_gan:
            if cg.get('shishen') == '正官':
                guan_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': sizhu[zhu_name]['di_zhi'],
                    'cang_gan': cg.get('cang_gan'),
                })
            if cg.get('shishen') == '七杀':
                sha_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': sizhu[zhu_name]['di_zhi'],
                    'cang_gan': cg.get('cang_gan'),
                })
    
    print(f"\n   正官（夫星）：")
    if guan_positions:
        for pos in guan_positions:
            if 'gan' in pos:
                print(f"      - {pos['label']}：{pos['gan']}")
            else:
                print(f"      - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}")
    else:
        print("      命盘中无正官")
    
    print(f"\n   七杀（偏夫星）：")
    if sha_positions:
        for pos in sha_positions:
            if 'gan' in pos:
                print(f"      - {pos['label']}：{pos['gan']}")
            else:
                print(f"      - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}")
    else:
        print("      命盘中无七杀")
    
    # ========== 分析是否七杀格 ==========
    print(f"\n3. 是否为七杀格：")
    
    # 七杀格的条件：月支藏干有七杀，或月干为七杀且月支生助
    yue_zhi = yue_zhu['di_zhi']
    yue_gan = yue_zhu['tian_gan']
    yue_gan_shishen = shishen_data.get('yue_zhu', {}).get('gan_shishen', '')
    yue_zhi_cang_gan = shishen_data.get('yue_zhu', {}).get('zhi_cang_gan_shishen', [])
    
    is_qisha_ge = False
    qisha_ge_reason = ""
    
    # 检查月干是否为七杀
    if yue_gan_shishen == '七杀':
        is_qisha_ge = True
        qisha_ge_reason = f"月干{yue_gan}为七杀"
    
    # 检查月支藏干是否有七杀
    for cg in yue_zhi_cang_gan:
        if cg.get('shishen') == '七杀':
            is_qisha_ge = True
            qisha_ge_reason = f"月支{yue_zhi}藏干{cg.get('cang_gan')}为七杀"
            break
    
    if is_qisha_ge:
        print(f"   是七杀格！原因：{qisha_ge_reason}")
    else:
        print(f"   不是典型的七杀格")
    
    # ========== 七杀夫命的判断 ==========
    print(f"\n4. 是否为「七杀夫命」：")
    
    # 判断标准：
    # 1. 命局中七杀明显（天干透出或多处藏干）
    # 2. 正官弱或无
    # 3. 可能倾向找有个性、强势或年龄差距大的伴侣
    
    total_sha = len(sha_positions)
    total_guan = len(guan_positions)
    
    if total_sha > 0 and total_guan == 0:
        print(f"   命局有七杀无正官，确实是偏七杀型夫命")
        print(f"   - 七杀数量：{total_sha}")
        print(f"   - 正官数量：{total_guan}")
        print(f"   特点：感情上可能更吸引有个性、有主见、强势或有年龄差的异性")
    elif total_sha > total_guan:
        print(f"   命局七杀多于正官，偏七杀型")
        print(f"   - 七杀数量：{total_sha}")
        print(f"   - 正官数量：{total_guan}")
    elif total_guan > 0:
        print(f"   命局有正官，为官杀混杂或正官型")
        print(f"   - 七杀数量：{total_sha}")
        print(f"   - 正官数量：{total_guan}")
    
    # ========== 是否需要甲木？==========
    print(f"\n{'=' * 70}")
    print("【五、是否需要甲木？——用神分析】")
    print("=" * 70)
    
    # 日主乙木，分析身强身弱
    # 生扶乙木的五行：水（印）生木，木（比劫）同我
    # 克泄耗乙木的五行：金（官杀）克我，火（食伤）我生，土（财）我克
    
    mu_count = wuxing_count.get('木', 0)  # 比劫
    shui_count = wuxing_count.get('水', 0)  # 印星
    huo_count = wuxing_count.get('火', 0)  # 食伤
    tu_count = wuxing_count.get('土', 0)  # 财星
    jin_count = wuxing_count.get('金', 0)  # 官杀
    
    # 生扶力量
    sheng_fu = mu_count + shui_count
    # 克泄耗力量
    ke_xie_hao = jin_count + huo_count + tu_count
    
    print(f"\n1. 身强身弱判断：")
    print(f"   日主：乙木")
    print(f"   生扶力量（水+木）：{sheng_fu}")
    print(f"   克泄耗力量（金+火+土）：{ke_xie_hao}")
    
    if sheng_fu >= ke_xie_hao:
        print(f"   判断：身强或中和偏强")
        is_shen_qiang = True
    else:
        print(f"   判断：身弱")
        is_shen_qiang = False
    
    print(f"\n2. 五行强弱分析：")
    print(f"   木（比劫）：{mu_count} - {'旺' if mu_count >= 2 else '中和' if mu_count >= 1 else '弱'}")
    print(f"   水（印星）：{shui_count} - {'旺' if shui_count >= 2 else '中和' if shui_count >= 1 else '弱'}")
    print(f"   火（食伤）：{huo_count} - {'旺' if huo_count >= 2 else '中和' if huo_count >= 1 else '弱'}")
    print(f"   土（财星）：{tu_count} - {'旺' if tu_count >= 2 else '中和' if tu_count >= 1 else '弱'}")
    print(f"   金（官杀）：{jin_count} - {'旺' if jin_count >= 2 else '中和' if jin_count >= 1 else '弱'}")
    
    print(f"\n3. 用神分析：")
    
    if is_shen_qiang:
        print(f"   身强喜泄耗克：")
        print(f"   - 喜用：火（食伤泄秀）、土（财星耗身）、金（官杀克制）")
        if jin_count == 0:
            print(f"   - 命局缺金（官杀），需要金来制身")
            print(f"   - 甲木为比劫，身强不宜再用甲木")
    else:
        print(f"   身弱喜生扶：")
        print(f"   - 喜用：水（印星生身）、木（比劫帮身）")
        if shui_count < 2:
            print(f"   - 水弱需要水来生木")
        print(f"   - 甲木（比劫）可以帮身，但需要看情况")
    
    # 特殊：命局缺金
    print(f"\n4. 关于「需要甲木」的问题：")
    print(f"   命局金（官杀）数量：{jin_count}")
    
    if jin_count == 0:
        print(f"   命局完全缺金（官杀）！")
        print(f"   解读：")
        print(f"   - 官杀代表女命的夫星和约束力")
        print(f"   - 命局缺官杀，可能感情缘分来得晚或不稳定")
        print(f"   - 需要通过大运、流年来补官杀")
        print(f"   - 甲木是比劫，对乙木来说是帮身或争夫的关系")
        print(f"   - 如果身弱，甲木可以帮身；如果身强，甲木反而竞争")
    else:
        print(f"   命局有金（官杀），夫星存在")
    
    # ========== 大运分析 ==========
    print(f"\n{'=' * 70}")
    print("【六、大运与婚运时间分析】")
    print("=" * 70)
    
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    
    if dayun_result.get('success'):
        dayun_list = dayun_result.get('dayun_list', [])
        print(f"\n大运排列：")
        for i, dy in enumerate(dayun_list):
            print(f"   第{i+1}步：{dy['gan']}{dy['zhi']} 运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）")
        
        # 分析当前大运
        current_age = 26  # 假设当前2025年，1999年出生，26岁
        print(f"\n当前年龄：约{current_age}岁（2025年）")
        
        current_dayun = None
        for dy in dayun_list:
            if dy['start_age'] <= current_age <= dy['end_age']:
                current_dayun = dy
                break
        
        if current_dayun:
            print(f"\n当前大运：{current_dayun['gan']}{current_dayun['zhi']} 运（{current_dayun['start_age']}-{current_dayun['end_age']}岁）")
            
            # 分析当前大运的十神
            dy_gan_shishen = calculate_single_shishen(rizhu_gan, current_dayun['gan'])
            dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, current_dayun['zhi'])
            
            print(f"   大运天干：{current_dayun['gan']}（{dy_gan_shishen}）")
            print(f"   大运地支：{current_dayun['zhi']}（{dy_zhi_shishen}）")
            
            if '官' in dy_gan_shishen or '官' in dy_zhi_shishen or '杀' in dy_gan_shishen or '杀' in dy_zhi_shishen:
                print(f"   ★ 大运见官杀，是婚恋运势较强的时期！")
        
        # 找官杀大运
        print(f"\n官杀大运（婚运较强的大运）：")
        for i, dy in enumerate(dayun_list):
            dy_gan_shishen = calculate_single_shishen(rizhu_gan, dy['gan'])
            dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, dy['zhi'])
            
            if '官' in dy_gan_shishen or '官' in dy_zhi_shishen or '杀' in dy_gan_shishen or '杀' in dy_zhi_shishen:
                print(f"   第{i+1}步：{dy['gan']}{dy['zhi']} 运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）")
                print(f"         天干{dy['gan']}为{dy_gan_shishen}，地支{dy['zhi']}为{dy_zhi_shishen}")
    
    # ========== 近年流年分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、近年流年婚运分析】")
    print("=" * 70)
    
    liunian_list = []
    for year_offset in range(2025 - 1999, 2035 - 1999 + 1):
        target_year = 1999 + year_offset
        liunian_gan = None
        liunian_zhi = None
        
        # 计算流年干支
        base_year = 1984
        gan_index = (target_year - base_year) % 10
        zhi_index = (target_year - base_year) % 12
        from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        liunian_list.append({
            'year': target_year,
            'age': year_offset,
            'gan': liunian_gan,
            'zhi': liunian_zhi,
            'gan_shishen': calculate_single_shishen(rizhu_gan, liunian_gan),
            'zhi_shishen': calculate_single_shishen(rizhu_gan, None, liunian_zhi),
        })
    
    print(f"\n流年婚运分析（2025-2035年）：")
    for ln in liunian_list:
        is_hunyun = False
        reasons = []
        
        # 检查是否为官杀年
        if '官' in ln['gan_shishen'] or '杀' in ln['gan_shishen']:
            is_hunyun = True
            reasons.append(f"天干{ln['gan']}为{ln['gan_shishen']}")
        if '官' in ln['zhi_shishen'] or '杀' in ln['zhi_shishen']:
            is_hunyun = True
            reasons.append(f"地支{ln['zhi']}为{ln['zhi_shishen']}")
        
        # 检查是否与日支相合（婚动）
        ri_zhi = ri_zhu['di_zhi']
        if check_liuhe(ri_zhi, ln['zhi']):
            is_hunyun = True
            reasons.append(f"流年{ln['zhi']}与日支{ri_zhi}相合（婚动）")
        
        # 检查是否为桃花年
        if check_taohua(nian_zhu['di_zhi'], ln['zhi']):
            is_hunyun = True
            reasons.append(f"流年{ln['zhi']}为桃花年")
        
        if is_hunyun:
            print(f"\n   {ln['year']}年（{ln['age']}岁）：{ln['gan']}{ln['zhi']}年 ★ 婚运强 ★")
            for r in reasons:
                print(f"      - {r}")
    
    # ========== 与男方合盘回顾 ==========
    print(f"\n{'=' * 70}")
    print("【八、与男方合盘要点回顾】")
    print("=" * 70)
    
    print(f"\n男方（1997年1月3日早上8点）：")
    print(f"   年柱：丙子  月柱：辛丑  日柱：乙未  时柱：庚辰")
    print(f"   日主：乙木")
    
    print(f"\n女方（1999年3月4日21点）：")
    print(f"   年柱：己卯  月柱：丙寅  日柱：乙巳  时柱：丁亥")
    print(f"   日主：乙木")
    
    print(f"\n关键匹配：")
    print(f"   1. 日主相同：双方都是乙木日主，性格相近")
    print(f"   2. 男方有金（庚、辛）：可补女方命局缺金")
    print(f"   3. 亥卯未三合木局：女方亥+卯 + 男方未 = 三合，缘分深")
    print(f"   4. 庚乙合：男方时干庚金与女方日主乙木相合")
    print(f"   5. 辛丙合：男方月干辛金与女方月干丙火相合")
    
    print(f"\n关于「七杀夫命需要甲木」的解答：")
    print(f"   1. 女方日主乙木，命局缺金（官杀），不是典型的七杀格")
    print(f"   2. 男方日主也是乙木，不是甲木")
    print(f"   3. 女方命局缺金，男方有庚辛金，可以互补")
    print(f"   4. 双方日主同为乙木，并非「需要甲木」的情况")
    print(f"   5. 男方的庚金正好是女方的正官（夫星），这是很好的匹配！")
    
    print(f"\n{'=' * 70}")
    print("分析完成")
    print("=" * 70)


def calculate_single_shishen(rizhu_gan, target_gan=None, target_zhi=None):
    """计算单个天干或地支的十神"""
    from core.tools.bazi_calculator import (
        TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_CANG_GAN,
        WUXING_SHENG, WUXING_KE
    )
    
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


def check_liuhe(zhi1, zhi2):
    """检查两个地支是否六合"""
    liuhe_map = {
        '子': '丑', '丑': '子',
        '寅': '亥', '亥': '寅',
        '卯': '戌', '戌': '卯',
        '辰': '酉', '酉': '辰',
        '巳': '申', '申': '巳',
        '午': '未', '未': '午',
    }
    return liuhe_map.get(zhi1) == zhi2


def check_taohua(nian_zhi, liunian_zhi):
    """检查流年是否为桃花年"""
    taohua_map = {
        '寅': '卯', '午': '卯', '戌': '卯',
        '申': '酉', '子': '酉', '辰': '酉',
        '巳': '午', '酉': '午', '丑': '午',
        '亥': '子', '卯': '子', '未': '子',
    }
    return taohua_map.get(nian_zhi) == liunian_zhi


if __name__ == "__main__":
    analyze_qisha_pattern()
