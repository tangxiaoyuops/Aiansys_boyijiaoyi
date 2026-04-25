"""
女方八字十神详细分析
1999年3月4日21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import DI_ZHI_CANG_GAN, TIAN_GAN_WUXING, TIAN_GAN_YINYANG, WUXING_SHENG, WUXING_KE

def analyze_shishen_detail():
    """详细分析女方十神"""
    
    print("=" * 70)
    print("女方八字十神详细分析")
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
    print(f"\n日主：{rizhu_gan}（乙木）")
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n{'=' * 70}")
    print("【二、十神分布详解】")
    print("=" * 70)
    
    # 详细打印每一柱的十神
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        zhu = sizhu[zhu_name]
        gan = zhu['tian_gan']
        zhi = zhu['di_zhi']
        
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        print(f"\n【{label}】{gan}{zhi}")
        print(f"  天干：{gan} → {gan_shishen}")
        print(f"  地支：{zhi}")
        print(f"    本气十神：{zhi_shishen}")
        if zhi_cang_gan:
            print(f"    藏干十神：")
            for cg in zhi_cang_gan:
                print(f"      - {zhi}藏{cg['cang_gan']} → {cg['shishen']}")
    
    # 统计十神
    print(f"\n{'=' * 70}")
    print("【三、十神统计】")
    print("=" * 70)
    
    shishen_count = {}
    
    # 统计天干十神
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:  # 不包括日柱天干
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if gan_shishen:
            shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
    
    # 统计地支十神（包括藏干）
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        if zhi_shishen:
            shishen_count[zhi_shishen] = shishen_count.get(zhi_shishen, 0) + 1
        
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            shishen = cg.get('shishen', '')
            if shishen:
                shishen_count[shishen] = shishen_count.get(shishen, 0) + 1
    
    print(f"\n十神数量统计：")
    for shishen in ['正财', '偏财', '正官', '七杀', '正印', '偏印', '比肩', '劫财', '食神', '伤官']:
        count = shishen_count.get(shishen, 0)
        if count > 0:
            print(f"  {shishen}：{count}个")
    
    # 分别统计天干和藏干
    print(f"\n【四、天干十神（明透）】")
    print("=" * 70)
    
    gan_shishen_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if gan_shishen:
            gan_shishen_list.append({'gan': gan, 'shishen': gan_shishen, 'label': label})
            print(f"  {label}天干 {gan}：{gan_shishen}")
    
    print(f"\n天干十神总结：")
    for item in gan_shishen_list:
        print(f"  {item['shishen']}：{item['gan']}（{item['label']}）")
    
    print(f"\n【五、地支藏干十神】")
    print("=" * 70)
    
    cang_gan_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        zhi = sizhu[zhu_name]['di_zhi']
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            cang_gan_list.append({
                'zhi': zhi,
                'cang_gan': cg['cang_gan'],
                'shishen': cg['shishen'],
                'label': label
            })
    
    for item in cang_gan_list:
        print(f"  {item['label']}地支{item['zhi']}藏{item['cang_gan']}：{item['shishen']}")
    
    print(f"\n地支藏干十神总结：")
    shishen_cang = {}
    for item in cang_gan_list:
        shishen = item['shishen']
        if shishen not in shishen_cang:
            shishen_cang[shishen] = []
        shishen_cang[shishen].append(f"{item['zhi']}藏{item['cang_gan']}（{item['label']}）")
    
    for shishen, positions in shishen_cang.items():
        print(f"  {shishen}：{len(positions)}个")
        for pos in positions:
            print(f"    - {pos}")
    
    # 财星详细分析
    print(f"\n{'=' * 70}")
    print("【六、财星详细分析】")
    print("=" * 70)
    
    print(f"\n日主：乙木")
    print(f"乙木克土为财，所以土是财星")
    print(f"  - 阳土（戊土）= 正财")
    print(f"  - 阴土（己土）= 偏财")
    
    # 检查命盘中的土
    print(f"\n命盘中的土（财星）：")
    
    # 天干
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        gan_wuxing = TIAN_GAN_WUXING.get(gan, '')
        if gan_wuxing == '土':
            gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
            print(f"  {label}天干 {gan}：{gan_wuxing} → {gan_shishen}")
    
    # 地支藏干中的土
    print(f"\n地支藏干中的土（财星）：")
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        zhi = sizhu[zhu_name]['di_zhi']
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            cang_gan = cg['cang_gan']
            cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
            if cang_gan_wuxing == '土':
                print(f"  {label}地支{zhi}藏{cang_gan}：{cang_gan_wuxing} → {cg['shishen']}")
    
    # 手动计算
    print(f"\n{'=' * 70}")
    print("【七、手动核对】")
    print("=" * 70)
    
    print(f"\n年柱：己卯")
    print(f"  天干己土：乙木克己土，己为阴土 → 偏财 ✓")
    print(f"  地支卯：藏乙木（本气） → 比肩")
    
    print(f"\n月柱：丙寅")
    print(f"  天干丙火：木生火，为食伤 → 伤官")
    print(f"  地支寅：藏甲丙戊")
    print(f"    - 甲木：比肩")
    print(f"    - 丙火：伤官")
    print(f"    - 戊土：乙木克戊土，戊为阳土 → 正财")
    
    print(f"\n日柱：乙巳")
    print(f"  天干乙木：日主")
    print(f"  地支巳：藏丙戊庚")
    print(f"    - 丙火：伤官")
    print(f"    - 戊土：乙木克戊土，戊为阳土 → 正财")
    print(f"    - 庚金：金克木，为官杀 → 正官")
    
    print(f"\n时柱：丁亥")
    print(f"  天干丁火：木生火，为食伤 → 食神")
    print(f"  地支亥：藏壬甲")
    print(f"    - 壬水：水生木，为印 → 正印")
    print(f"    - 甲木：劫财")
    
    # 最终统计
    print(f"\n{'=' * 70}")
    print("【八、最终十神统计】")
    print("=" * 70)
    
    print(f"\n【天干十神（明透）】")
    print(f"  年干己土：偏财")
    print(f"  月干丙火：伤官")
    print(f"  时干丁火：食神")
    
    print(f"\n【地支藏干十神】")
    print(f"  年支卯藏乙：比肩")
    print(f"  月支寅藏甲：劫财")
    print(f"  月支寅藏丙：伤官")
    print(f"  月支寅藏戊：正财")
    print(f"  日支巳藏丙：伤官")
    print(f"  日支巳藏戊：正财")
    print(f"  日支巳藏庚：正官")
    print(f"  时支亥藏壬：正印")
    print(f"  时支亥藏甲：劫财")
    
    print(f"\n【十神总计】")
    print(f"  正财：2个（寅藏戊、巳藏戊）")
    print(f"  偏财：1个（年干己）")
    print(f"  正官：1个（巳藏庚）")
    print(f"  正印：1个（亥藏壬）")
    print(f"  比肩：1个（卯藏乙）")
    print(f"  劫财：2个（寅藏甲、亥藏甲）")
    print(f"  食神：1个（时干丁）")
    print(f"  伤官：3个（月干丙、寅藏丙、巳藏丙）")
    
    print(f"\n您之前说的对！女方十神分布是：")
    print(f"  - 正印：1个")
    print(f"  - 劫财：2个（不是1个）")
    print(f"  - 偏财：1个")
    print(f"\n  但还有：")
    print(f"  - 正财：2个")
    print(f"  - 正官：1个")
    print(f"  - 比肩：1个")
    print(f"  - 食神：1个")
    print(f"  - 伤官：3个")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_shishen_detail()
