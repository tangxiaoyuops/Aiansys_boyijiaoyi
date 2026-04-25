"""
男方命盘深度分析：与女方契合度 + 婚运时间
1997年1月3日早上8点男生
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
    DI_ZHI_CANG_GAN, WUXING_SHENG, WUXING_KE
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


def analyze_male_destiny():
    """分析男方命盘"""
    
    print("=" * 70)
    print("男方命盘深度分析：与女方契合度 + 婚运时间")
    print("=" * 70)
    
    # 男方：1997年1月3日 早上8点
    year = 1997
    month = 1
    day = 3
    hour = 8
    gender = '男'
    
    # 排盘
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    if not pan_result.get('success'):
        print(f"排盘失败: {pan_result.get('error')}")
        return
    
    sizhu = pan_result['sizhu']
    
    # 获取各柱信息
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【一、男方八字命盘】")
    print(f"出生：1997年1月3日 早上8点")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']} (日主)")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    
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
    
    # 五行分析
    wuxing_result = bazi_wuxing_node(sizhu)
    wuxing_count = wuxing_result.get('wuxing_count', {}) if wuxing_result.get('success') else {}
    
    print(f"\n【三、五行分布】")
    print(f"金：{wuxing_count.get('金', 0)}  木：{wuxing_count.get('木', 0)}  水：{wuxing_count.get('水', 0)}  火：{wuxing_count.get('火', 0)}  土：{wuxing_count.get('土', 0)}")
    
    # ========== 男命妻星分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、男命妻星分析（男命以财星为妻星）】")
    print("=" * 70)
    
    # 找财星（正财、偏财）
    cai_positions = []
    pian_cai_positions = []
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        zhu_label = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        
        if gan_shishen == '正财':
            cai_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': sizhu[zhu_name]['tian_gan'],
            })
        if gan_shishen == '偏财':
            pian_cai_positions.append({
                'position': zhu_name,
                'label': f'{zhu_label[zhu_name]}天干',
                'gan': sizhu[zhu_name]['tian_gan'],
            })
        
        for cg in zhi_cang_gan:
            if cg.get('shishen') == '正财':
                cai_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': sizhu[zhu_name]['di_zhi'],
                    'cang_gan': cg.get('cang_gan'),
                })
            if cg.get('shishen') == '偏财':
                pian_cai_positions.append({
                    'position': zhu_name,
                    'label': f'{zhu_label[zhu_name]}地支',
                    'zhi': sizhu[zhu_name]['di_zhi'],
                    'cang_gan': cg.get('cang_gan'),
                })
    
    print(f"\n正财（妻星）：")
    if cai_positions:
        for pos in cai_positions:
            if 'gan' in pos:
                print(f"   - {pos['label']}：{pos['gan']}")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}")
    else:
        print("   命盘中无正财")
    
    print(f"\n偏财（偏妻星）：")
    if pian_cai_positions:
        for pos in pian_cai_positions:
            if 'gan' in pos:
                print(f"   - {pos['label']}：{pos['gan']}")
            else:
                print(f"   - {pos['label']}：{pos['zhi']}藏{pos['cang_gan']}")
    else:
        print("   命盘中无偏财")
    
    # ========== 大运分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、男方大运与婚运】")
    print("=" * 70)
    
    from core.agents.bazi_dayun_agent import bazi_dayun_node
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    
    if dayun_result.get('success'):
        dayun_list = dayun_result.get('dayun_list', [])
        print(f"\n大运排列：")
        for i, dy in enumerate(dayun_list):
            dy_gan_shishen = calculate_single_shishen(rizhu_gan, dy['gan'])
            dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, dy['zhi'])
            print(f"   第{i+1}步：{dy['gan']}{dy['zhi']} 运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）")
            print(f"         天干{dy['gan']}为{dy_gan_shishen}，地支{dy['zhi']}为{dy_zhi_shishen}")
        
        # 当前大运
        current_age = 29  # 2026年，1997年出生，29岁
        print(f"\n当前年龄：约{current_age}岁（2026年）")
        
        current_dayun = None
        for dy in dayun_list:
            if dy['start_age'] <= current_age <= dy['end_age']:
                current_dayun = dy
                break
        
        if current_dayun:
            dy_gan_shishen = calculate_single_shishen(rizhu_gan, current_dayun['gan'])
            dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, current_dayun['zhi'])
            print(f"\n当前大运：{current_dayun['gan']}{current_dayun['zhi']} 运（{current_dayun['start_age']}-{current_dayun['end_age']}岁）")
            print(f"   大运天干：{current_dayun['gan']}（{dy_gan_shishen}）")
            print(f"   大运地支：{current_dayun['zhi']}（{dy_zhi_shishen}）")
            
            # 检查是否财星大运
            if '财' in dy_gan_shishen or '财' in dy_zhi_shishen:
                print(f"   ★ 大运见财星，是婚恋运势较强的时期！")
        
        # 找财星大运
        print(f"\n财星大运（婚运较强的大运）：")
        for i, dy in enumerate(dayun_list):
            dy_gan_shishen = calculate_single_shishen(rizhu_gan, dy['gan'])
            dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, dy['zhi'])
            
            if '财' in dy_gan_shishen or '财' in dy_zhi_shishen:
                print(f"   第{i+1}步：{dy['gan']}{dy['zhi']} 运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）")
    
    # ========== 流年分析 ==========
    print(f"\n{'=' * 70}")
    print("【六、近年流年婚运分析】")
    print("=" * 70)
    
    liunian_list = []
    for year_offset in range(2025 - 1997, 2035 - 1997 + 1):
        target_year = 1997 + year_offset
        base_year = 1984
        gan_index = (target_year - base_year) % 10
        zhi_index = (target_year - base_year) % 12
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
        
        # 检查是否为财星年（男命妻星）
        if '财' in ln['gan_shishen']:
            is_hunyun = True
            reasons.append(f"天干{ln['gan']}为{ln['gan_shishen']}（妻星）")
        if '财' in ln['zhi_shishen']:
            is_hunyun = True
            reasons.append(f"地支{ln['zhi']}为{ln['zhi_shishen']}（妻星）")
        
        # 检查是否与日支相合
        ri_zhi = ri_zhu['di_zhi']
        if check_liuhe(ri_zhi, ln['zhi']):
            is_hunyun = True
            reasons.append(f"流年{ln['zhi']}与日支{ri_zhi}相合（婚动）")
        
        # 检查桃花年
        if check_taohua(nian_zhu['di_zhi'], ln['zhi']):
            is_hunyun = True
            reasons.append(f"流年{ln['zhi']}为桃花年")
        
        if is_hunyun:
            print(f"\n   {ln['year']}年（{ln['age']}岁）：{ln['gan']}{ln['zhi']}年 ★ 婚运强 ★")
            for r in reasons:
                print(f"      - {r}")
    
    # ========== 与女方契合度分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、与女方契合度深度分析】")
    print("=" * 70)
    
    print(f"\n1. 命盘对比：")
    print(f"\n   男方（1997年）：丙子年 辛丑月 乙未日 庚辰时")
    print(f"   女方（1999年）：己卯年 丙寅月 乙巳日 丁亥时")
    
    print(f"\n2. 夫妻星互见分析：")
    print(f"\n   【男方看女方】")
    print(f"   男方日主：乙木")
    print(f"   女方年干己土 = 男方的偏财（妻星）✓")
    print(f"   → 男方在女方年柱看到妻星")
    
    print(f"\n   【女方看男方】")
    print(f"   女方日主：乙木")
    print(f"   男方时干庚金 = 女方的正官（夫星）✓")
    print(f"   男方月干辛金 = 女方的七杀（偏夫星）✓")
    print(f"   → 女方在男方命盘看到正官和七杀，官杀双见")
    
    print(f"\n3. 日主关系：")
    print(f"   男方日主：乙木（阴木）")
    print(f"   女方日主：乙木（阴木）")
    print(f"   → 日主相同，性格相近，价值观相似")
    
    print(f"\n4. 地支关系：")
    print(f"   ★ 亥卯未三合木局：女方亥 + 女方卯 + 男方未 = 三合")
    print(f"   → 这是最高级别的地支组合，缘分非常深！")
    print(f"   → 三合局代表能量互助、关系稳固")
    
    print(f"\n5. 天干关系：")
    print(f"   ★ 庚乙合：男方时干庚金与双方日主乙木相合")
    print(f"   ★ 辛丙合：男方月干辛金与女方月干丙火相合")
    print(f"   → 天干多合，感情中有相互吸引、心有灵犀")
    
    print(f"\n6. 五行互补：")
    print(f"   男方五行：金2、木1、水1、火1、土3")
    print(f"   女方五行：金0、木3、水1、火3、土1")
    print(f"   ★ 女方缺金，男方有金 → 男方可补女方夫星")
    print(f"   ★ 男方缺火、木少，女方火木旺 → 女方可补男方")
    print(f"   → 五行互补性很强！")
    
    # ========== 2026年分析 ==========
    print(f"\n{'=' * 70}")
    print("【八、2026年（丙午年）详细分析】")
    print("=" * 70)
    
    print(f"\n男方2026年（29岁）：")
    print(f"   流年：丙午")
    print(f"   天干丙火：{calculate_single_shishen(rizhu_gan, '丙')}")
    print(f"   地支午火：{calculate_single_shishen(rizhu_gan, None, '午')}")
    print(f"   → 伤官+食神年，主感情表达、桃花")
    
    print(f"\n女方2026年（27岁）：")
    print(f"   流年：丙午")
    print(f"   天干丙火：伤官")
    print(f"   地支午火：食神")
    print(f"   → 同样是伤官+食神年")
    
    print(f"\n2026年双方契合：")
    print(f"   ★ 同步的流年运势")
    print(f"   ★ 伤官主表达、食神主享受，适合感情发展")
    print(f"   ★ 年初认识正是好时机")
    
    # ========== 最佳婚期 ==========
    print(f"\n{'=' * 70}")
    print("【九、最佳婚期建议】")
    print("=" * 70)
    
    print(f"\n基于双方命盘分析：")
    print(f"\n   2026年（丙午年）：")
    print(f"   - 感情发展期，适合加深了解")
    print(f"   - 年初认识是好兆头")
    
    print(f"\n   2028年（戊申年）★ 最佳婚期 ★")
    print(f"   - 女方：流年申金正官 + 巳申合（婚动）")
    print(f"   - 男方：流年申金正官（男命的官代表事业稳定）")
    print(f"   - 双方都适合在这一年结婚")
    
    print(f"\n   2030年（庚戌年）：")
    print(f"   - 女方：流年庚金正官透出")
    print(f"   - 男方：流年庚金正官")
    print(f"   - 也是适合结婚的好年份")
    
    print(f"\n{'=' * 70}")
    print("分析完成")
    print("=" * 70)


if __name__ == "__main__":
    analyze_male_destiny()
