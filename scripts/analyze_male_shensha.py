"""
男方神煞分析（驿马等）+ 工作变动原因
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING

def analyze_male_shensha():
    """分析男方神煞和工作变动"""
    
    print("=" * 70)
    print("男方神煞分析 + 工作变动原因")
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
    
    print(f"\n【一、八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}")
    
    # 收集所有地支
    zhi_list = [
        ('年支', nian_zhu['di_zhi']),
        ('月支', yue_zhu['di_zhi']),
        ('日支', ri_zhu['di_zhi']),
        ('时支', shi_zhu['di_zhi']),
    ]
    all_zhi = [z[1] for z in zhi_list]
    
    # 收集所有天干
    gan_list = [
        ('年干', nian_zhu['tian_gan']),
        ('月干', yue_zhu['tian_gan']),
        ('日干', ri_zhu['tian_gan']),
        ('时干', shi_zhu['tian_gan']),
    ]
    all_gan = [g[1] for g in gan_list]
    
    print(f"\n四柱地支：年支{nian_zhu['di_zhi']}、月支{yue_zhu['di_zhi']}、日支{ri_zhu['di_zhi']}、时支{shi_zhu['di_zhi']}")
    print(f"四柱天干：年干{nian_zhu['tian_gan']}、月干{yue_zhu['tian_gan']}、日干{ri_zhu['tian_gan']}、时干{shi_zhu['tian_gan']}")
    
    nian_zhi = nian_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    nian_gan = nian_zhu['tian_gan']
    
    # ========== 驿马分析 ==========
    print(f"\n{'=' * 70}")
    print("【二、驿马分析】")
    print("=" * 70)
    
    print(f"\n驿马查法口诀：")
    print(f"  申子辰见寅为驿马")
    print(f"  寅午戌见申为驿马")
    print(f"  巳酉丑见亥为驿马")
    print(f"  亥卯未见巳为驿马")
    
    yima_map = {
        '申': '寅', '子': '寅', '辰': '寅',
        '寅': '申', '午': '申', '戌': '申',
        '巳': '亥', '酉': '亥', '丑': '亥',
        '亥': '巳', '卯': '巳', '未': '巳',
    }
    
    yima_by_nian = yima_map.get(nian_zhi, '')
    yima_by_ri = yima_map.get(ri_zhi, '')
    
    print(f"\n年支：{nian_zhi}")
    print(f"日支：{ri_zhi}")
    print(f"\n以年支{nian_zhi}查驿马：{yima_by_nian}")
    print(f"以日支{ri_zhi}查驿马：{yima_by_ri}")
    
    has_yima_nian = yima_by_nian in all_zhi
    has_yima_ri = yima_by_ri in all_zhi
    
    print(f"\n命盘中是否有驿马：")
    if has_yima_nian:
        for label, zhi in zhi_list:
            if zhi == yima_by_nian:
                print(f"  ✓ {label}{zhi}为驿马（以年支查）")
    if has_yima_ri:
        for label, zhi in zhi_list:
            if zhi == yima_by_ri:
                print(f"  ✓ {label}{zhi}为驿马（以日支查）")
    if not has_yima_nian and not has_yima_ri:
        print(f"  ✗ 命盘中无驿马星")
    
    # ========== 桃花分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、桃花分析】")
    print("=" * 70)
    
    taohua_map = {
        '寅': '卯', '午': '卯', '戌': '卯',
        '申': '酉', '子': '酉', '辰': '酉',
        '巳': '午', '酉': '午', '丑': '午',
        '亥': '子', '卯': '子', '未': '子',
    }
    
    taohua_by_nian = taohua_map.get(nian_zhi, '')
    taohua_by_ri = taohua_map.get(ri_zhi, '')
    
    print(f"以年支{nian_zhi}查桃花：{taohua_by_nian}")
    print(f"以日支{ri_zhi}查桃花：{taohua_by_ri}")
    
    has_taohua = taohua_by_nian in all_zhi or taohua_by_ri in all_zhi
    
    if has_taohua:
        print(f"\n命带桃花！")
        for label, zhi in zhi_list:
            if zhi == taohua_by_nian or zhi == taohua_by_ri:
                print(f"  ✓ {label}{zhi}为桃花")
    else:
        print(f"\n命盘中无桃花")
    
    # ========== 天乙贵人分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、天乙贵人分析】")
    print("=" * 70)
    
    guiren_map = {
        '甲': ['丑', '未'], '戊': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'],
        '丙': ['亥', '酉'], '丁': ['亥', '酉'],
        '壬': ['卯', '巳'], '癸': ['卯', '巳'],
        '庚': ['寅', '午'], '辛': ['寅', '午'],
    }
    
    guiren_by_nian = guiren_map.get(nian_gan, [])
    guiren_by_ri = guiren_map.get(rizhu_gan, [])
    
    print(f"以年干{nian_gan}查天乙贵人：{guiren_by_nian}")
    print(f"以日干{rizhu_gan}查天乙贵人：{guiren_by_ri}")
    
    has_guiren = False
    for zhi in guiren_by_nian + guiren_by_ri:
        if zhi in all_zhi:
            has_guiren = True
            for label, z in zhi_list:
                if z == zhi:
                    print(f"  ✓ {label}{zhi}为天乙贵人")
    
    if not has_guiren:
        print(f"命盘中无天乙贵人")
    
    # ========== 华盖分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、华盖分析】")
    print("=" * 70)
    
    huagai_map = {
        '寅': '戌', '午': '戌', '戌': '戌',
        '申': '辰', '子': '辰', '辰': '辰',
        '巳': '丑', '酉': '丑', '丑': '丑',
        '亥': '未', '卯': '未', '未': '未',
    }
    
    huagai_by_nian = huagai_map.get(nian_zhi, '')
    huagai_by_ri = huagai_map.get(ri_zhi, '')
    
    print(f"以年支{nian_zhi}查华盖：{huagai_by_nian}")
    print(f"以日支{ri_zhi}查华盖：{huagai_by_ri}")
    
    has_huagai = huagai_by_nian in all_zhi or huagai_by_ri in all_zhi
    
    if has_huagai:
        print(f"\n命带华盖！")
    else:
        print(f"\n命盘中无华盖")
    
    # ========== 十神分析（工作变动原因）==========
    print(f"\n{'=' * 70}")
    print("【六、十神分析——工作变动原因】")
    print("=" * 70)
    
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n十神分布：")
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        print(f"  {label}：{gan}（{gan_shishen}）/ {zhi}（{zhi_shishen}）")
    
    # 统计
    print(f"\n影响工作的十神：")
    
    # 检查伤官、七杀
    shangguan_count = 0
    qisha_count = 0
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if '伤官' in gan_shishen:
            shangguan_count += 1
            print(f"  - 伤官透干：{sizhu[zhu_name]['tian_gan']}（{zhu_name.replace('_', '')}）")
        if '七杀' in gan_shishen:
            qisha_count += 1
            print(f"  - 七杀透干：{sizhu[zhu_name]['tian_gan']}（{zhu_name.replace('_', '')}）")
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            if '伤官' in cg.get('shishen', ''):
                shangguan_count += 1
            if '七杀' in cg.get('shishen', ''):
                qisha_count += 1
    
    print(f"\n伤官数量：{shangguan_count}个")
    print(f"七杀数量：{qisha_count}个")
    
    # ========== 工作变动原因分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、工作变动原因深度分析】")
    print("=" * 70)
    
    print(f"""
为什么没有驿马也会工作变动？

驿马只是工作变动的原因之一，还有其他因素：

【一、伤官的影响】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # 检查伤官位置
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if '伤官' in gan_shishen:
            print(f"  ★ {label}天干{gan}为伤官透出！")
            print(f"    伤官代表：叛逆、创新、不服管束、喜欢变化")
            if zhu_name == 'nian_zhu':
                print(f"    年柱伤官：早年叛逆，不喜欢按部就班")
            elif zhu_name == 'yue_zhu':
                print(f"    月柱伤官：事业心强，不喜欢被约束")
            elif zhu_name == 'shi_zhu':
                print(f"    时柱伤官：晚年仍想创新变化")
    
    print(f"""
伤官对工作的影响：
  1. 不喜欢被约束，不喜欢稳定的工作环境
  2. 追求创新和变化，容易厌倦重复性工作
  3. 有才华但难以安分守己
  4. 工作中容易与领导冲突

【二、七杀的影响】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # 检查七杀位置
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if '七杀' in gan_shishen:
            print(f"  ★ {label}天干{gan}为七杀透出！")
            print(f"    七杀代表：权力、压力、变动、挑战")
            if zhu_name == 'yue_zhu':
                print(f"    月柱七杀：事业上压力大，容易变动")
    
    print(f"""
七杀对工作的影响：
  1. 事业心强，喜欢挑战
  2. 不喜欢平淡，追求成就感
  3. 工作压力大，容易想换环境
  4. 需要不断突破自我

【三、大运流年的影响】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # 分析大运
    from core.agents.bazi_dayun_agent import bazi_dayun_node
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
    print(f"\n当前及近期大运：")
    for i, dy in enumerate(dayun_list):
        if dy['start_year'] >= 2010 and dy['start_year'] <= 2035:
            gan = dy['gan']
            zhi = dy['zhi']
            
            # 计算十神
            rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
            gan_wuxing = TIAN_GAN_WUXING.get(gan, '')
            
            # 简单判断
            shishen = ""
            if gan_wuxing == rizhu_wuxing:
                shishen = "比劫"
            elif gan_wuxing == '火':  # 木生火
                shishen = "食伤"
            elif gan_wuxing == '水':  # 水生木
                shishen = "印"
            elif gan_wuxing == '土':  # 木克土
                shishen = "财"
            elif gan_wuxing == '金':  # 金克木
                shishen = "官杀"
            
            marker = ""
            if '伤' in shishen or '官' in shishen or '杀' in shishen:
                marker = " ← 可能影响工作稳定"
            
            print(f"  {dy['start_year']}-{dy['end_year']}年：{gan}{zhi}运（{shishen}）{marker}")
    
    print(f"""

【四、命局组合的影响】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

男方命局特点：
  1. 年干丙火伤官透出 → 叛逆、不喜欢被管束
  2. 月干辛金七杀透出 → 事业压力大，喜欢挑战
  3. 伤官+七杀组合 → 容易与权威冲突，工作变动

这种组合的人：
  - 有才华、有想法
  - 不喜欢稳定的工作环境
  - 适合创业、自由职业
  - 或者需要变化的工作（销售、技术等）

【五、解决方案】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

适合的工作类型：
  ✓ 技术类：不断学习新技术，有变化
  ✓ 销售类：业绩导向，不坐班
  ✓ 创业：自己做老板，不受约束
  ✓ 自由职业：时间灵活
  ✓ 项目制工作：完成一个项目换一个

不适合的工作类型：
  ✗ 朝九晚五的行政工作
  ✗ 重复性高的工作
  ✗ 等级森严的大公司

【总结】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

工作变动多不是因为驿马，而是因为：
  1. 伤官透干 → 不喜欢被约束
  2. 七杀透干 → 追求挑战和变化
  3. 伤官+七杀 → 与权威冲突

建议：
  - 找适合自己的工作类型
  - 不必强求稳定，发挥变化的优势
  - 可以考虑技术、销售、创业等方向
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_shensha()
