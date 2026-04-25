"""
女方神煞分析（驿马等）
1999年3月4日21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.tools.bazi_calculator import DI_ZHI

# 驿马查法
# 申子辰见寅为驿马
# 寅午戌见申为驿马
# 巳酉丑见亥为驿马
# 亥卯未见巳为驿马

# 桃花查法
# 寅午戌见卯为桃花
# 申子辰见酉为桃花
# 巳酉丑见午为桃花
# 亥卯未见子为桃花

# 天乙贵人查法
# 甲戊见牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，庚辛逢虎马

# 华盖查法
# 寅午戌见戌为华盖
# 申子辰见辰为华盖
# 巳酉丑见丑为华盖
# 亥卯未见未为华盖

def analyze_shensha():
    """分析女方神煞"""
    
    print("=" * 70)
    print("女方神煞分析")
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
    
    print(f"\n四柱地支：年支{nian_zhu['di_zhi']}、月支{yue_zhu['di_zhi']}、日支{ri_zhu['di_zhi']}、时支{shi_zhu['di_zhi']}")
    
    # ========== 驿马分析 ==========
    print(f"\n{'=' * 70}")
    print("【二、驿马分析】")
    print("=" * 70)
    
    print(f"\n驿马查法口诀：")
    print(f"  申子辰见寅为驿马")
    print(f"  寅午戌见申为驿马")
    print(f"  巳酉丑见亥为驿马")
    print(f"  亥卯未见巳为驿马")
    
    # 以年支或日支查驿马
    nian_zhi = nian_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    
    print(f"\n年支：{nian_zhi}")
    print(f"日支：{ri_zhi}")
    
    # 根据年支查驿马
    yima_map = {
        '申': '寅', '子': '寅', '辰': '寅',  # 申子辰见寅
        '寅': '申', '午': '申', '戌': '申',  # 寅午戌见申
        '巳': '亥', '酉': '亥', '丑': '亥',  # 巳酉丑见亥
        '亥': '巳', '卯': '巳', '未': '巳',  # 亥卯未见巳
    }
    
    yima_by_nian = yima_map.get(nian_zhi, '')
    yima_by_ri = yima_map.get(ri_zhi, '')
    
    print(f"\n以年支{nian_zhi}查驿马：{yima_by_nian}")
    print(f"以日支{ri_zhi}查驿马：{yima_by_ri}")
    
    # 检查命盘中是否有驿马
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
        print(f"  ✗ 命盘中无驿马")
    
    # 驿马含义
    print(f"\n驿马含义：")
    print(f"  驿马星主奔波、走动、远行、变化")
    print(f"  命带驿马：一生多走动，适合外出发展")
    print(f"  女命驿马：可能远嫁、工作变动多、喜欢旅游")
    
    if has_yima_nian or has_yima_ri:
        print(f"\n  ★ 女方命带驿马！")
        print(f"  可能表现：")
        print(f"  - 工作或生活中有较多变动")
        print(f"  - 适合外出发展，不宜困守一地")
        print(f"  - 可能远嫁或异地姻缘")
        print(f"  - 喜欢旅游、走动")
    else:
        print(f"\n  女方命不带驿马")
        print(f"  可能表现：")
        print(f"  - 生活相对稳定")
        print(f"  - 不太喜欢奔波")
        print(f"  - 适合本地发展")
    
    # ========== 桃花分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、桃花分析】")
    print("=" * 70)
    
    print(f"\n桃花查法口诀：")
    print(f"  寅午戌见卯为桃花")
    print(f"  申子辰见酉为桃花")
    print(f"  巳酉丑见午为桃花")
    print(f"  亥卯未见子为桃花")
    
    taohua_map = {
        '寅': '卯', '午': '卯', '戌': '卯',  # 寅午戌见卯
        '申': '酉', '子': '酉', '辰': '酉',  # 申子辰见酉
        '巳': '午', '酉': '午', '丑': '午',  # 巳酉丑见午
        '亥': '子', '卯': '子', '未': '子',  # 亥卯未见子
    }
    
    taohua_by_nian = taohua_map.get(nian_zhi, '')
    taohua_by_ri = taohua_map.get(ri_zhi, '')
    
    print(f"\n以年支{nian_zhi}查桃花：{taohua_by_nian}")
    print(f"以日支{ri_zhi}查桃花：{taohua_by_ri}")
    
    has_taohua_nian = taohua_by_nian in all_zhi
    has_taohua_ri = taohua_by_ri in all_zhi
    
    print(f"\n命盘中是否有桃花：")
    
    if has_taohua_nian:
        for label, zhi in zhi_list:
            if zhi == taohua_by_nian:
                print(f"  ✓ {label}{zhi}为桃花（以年支查）")
    
    if has_taohua_ri:
        for label, zhi in zhi_list:
            if zhi == taohua_by_ri:
                print(f"  ✓ {label}{zhi}为桃花（以日支查）")
    
    if not has_taohua_nian and not has_taohua_ri:
        print(f"  ✗ 命盘中无桃花")
    
    print(f"\n桃花含义：")
    print(f"  桃花星主异性缘、魅力、人缘")
    print(f"  命带桃花：异性缘好，有魅力")
    print(f"  女命桃花：漂亮、有魅力、异性缘好")
    
    if has_taohua_nian or has_taohua_ri:
        print(f"\n  ★ 女方命带桃花！")
    else:
        print(f"\n  女方命不带桃花")
    
    # ========== 天乙贵人分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、天乙贵人分析】")
    print("=" * 70)
    
    print(f"\n天乙贵人查法口诀：")
    print(f"  甲戊见牛羊（甲戊年/日见丑未）")
    print(f"  乙己鼠猴乡（乙己年/日见子申）")
    print(f"  丙丁猪鸡位（丙丁年/日见亥酉）")
    print(f"  壬癸兔蛇藏（壬癸年/日见卯巳）")
    print(f"  庚辛逢虎马（庚辛年/日见寅午）")
    
    guiren_map = {
        '甲': ['丑', '未'], '戊': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'],
        '丙': ['亥', '酉'], '丁': ['亥', '酉'],
        '壬': ['卯', '巳'], '癸': ['卯', '巳'],
        '庚': ['寅', '午'], '辛': ['寅', '午'],
    }
    
    nian_gan = nian_zhu['tian_gan']
    guiren_by_nian = guiren_map.get(nian_gan, [])
    guiren_by_ri = guiren_map.get(rizhu_gan, [])
    
    print(f"\n以年干{nian_gan}查天乙贵人：{guiren_by_nian}")
    print(f"以日干{rizhu_gan}查天乙贵人：{guiren_by_ri}")
    
    has_guiren = False
    print(f"\n命盘中是否有天乙贵人：")
    
    for zhi in guiren_by_nian:
        if zhi in all_zhi:
            has_guiren = True
            for label, z in zhi_list:
                if z == zhi:
                    print(f"  ✓ {label}{zhi}为天乙贵人（以年干查）")
    
    for zhi in guiren_by_ri:
        if zhi in all_zhi:
            has_guiren = True
            for label, z in zhi_list:
                if z == zhi:
                    print(f"  ✓ {label}{zhi}为天乙贵人（以日干查）")
    
    if not has_guiren:
        print(f"  ✗ 命盘中无天乙贵人")
    
    print(f"\n天乙贵人含义：")
    print(f"  天乙贵人是最大的吉星")
    print(f"  命带天乙贵人：逢凶化吉，贵人相助")
    
    # ========== 华盖分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、华盖分析】")
    print("=" * 70)
    
    print(f"\n华盖查法口诀：")
    print(f"  寅午戌见戌为华盖")
    print(f"  申子辰见辰为华盖")
    print(f"  巳酉丑见丑为华盖")
    print(f"  亥卯未见未为华盖")
    
    huagai_map = {
        '寅': '戌', '午': '戌', '戌': '戌',  # 寅午戌见戌
        '申': '辰', '子': '辰', '辰': '辰',  # 申子辰见辰
        '巳': '丑', '酉': '丑', '丑': '丑',  # 巳酉丑见丑
        '亥': '未', '卯': '未', '未': '未',  # 亥卯未见未
    }
    
    huagai_by_nian = huagai_map.get(nian_zhi, '')
    huagai_by_ri = huagai_map.get(ri_zhi, '')
    
    print(f"\n以年支{nian_zhi}查华盖：{huagai_by_nian}")
    print(f"以日支{ri_zhi}查华盖：{huagai_by_ri}")
    
    has_huagai = False
    print(f"\n命盘中是否有华盖：")
    
    if huagai_by_nian in all_zhi:
        has_huagai = True
        for label, zhi in zhi_list:
            if zhi == huagai_by_nian:
                print(f"  ✓ {label}{zhi}为华盖（以年支查）")
    
    if huagai_by_ri in all_zhi:
        has_huagai = True
        for label, zhi in zhi_list:
            if zhi == huagai_by_ri:
                print(f"  ✓ {label}{zhi}为华盖（以日支查）")
    
    if not has_huagai:
        print(f"  ✗ 命盘中无华盖")
    
    print(f"\n华盖含义：")
    print(f"  华盖星主艺术、宗教、孤独")
    print(f"  命带华盖：有艺术才华，喜欢玄学")
    
    # ========== 总结 ==========
    print(f"\n{'=' * 70}")
    print("【六、神煞总结】")
    print("=" * 70)
    
    print(f"\n女方命盘神煞：")
    
    shensha_list = []
    
    if has_yima_nian or has_yima_ri:
        yima_zhi = yima_by_nian if has_yima_nian else yima_by_ri
        shensha_list.append(f"驿马（{yima_zhi}）：奔波、走动、变化")
    
    if has_taohua_nian or has_taohua_ri:
        taohua_zhi = taohua_by_nian if has_taohua_nian else taohua_by_ri
        shensha_list.append(f"桃花（{taohua_zhi}）：异性缘、魅力")
    
    if has_guiren:
        shensha_list.append(f"天乙贵人：逢凶化吉、贵人相助")
    
    if has_huagai:
        huagai_zhi = huagai_by_nian if huagai_by_nian in all_zhi else huagai_by_ri
        shensha_list.append(f"华盖（{huagai_zhi}）：艺术、宗教、孤独")
    
    if shensha_list:
        for s in shensha_list:
            print(f"  ✓ {s}")
    else:
        print(f"  命盘中无明显神煞")
    
    # 三合局分析
    print(f"\n【七、三合局分析】")
    print("=" * 70)
    
    print(f"\n三合局：")
    print(f"  申子辰合水局")
    print(f"  亥卯未合木局")
    print(f"  寅午戌合火局")
    print(f"  巳酉丑合金局")
    
    print(f"\n女方四柱地支：{nian_zhu['di_zhi']}、{yue_zhu['di_zhi']}、{ri_zhu['di_zhi']}、{shi_zhu['di_zhi']}")
    
    # 检查三合
    san_he_list = [
        {'name': '水局', 'zhi': ['申', '子', '辰']},
        {'name': '木局', 'zhi': ['亥', '卯', '未']},
        {'name': '火局', 'zhi': ['寅', '午', '戌']},
        {'name': '金局', 'zhi': ['巳', '酉', '丑']},
    ]
    
    for sh in san_he_list:
        count = sum(1 for z in sh['zhi'] if z in all_zhi)
        if count >= 2:
            print(f"\n  有{sh['name']}（{sh['zhi']}）的组成部分：")
            for z in sh['zhi']:
                if z in all_zhi:
                    for label, zhi in zhi_list:
                        if zhi == z:
                            print(f"    - {label}{z}")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_shensha()
