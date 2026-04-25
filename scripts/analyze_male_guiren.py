"""
男方贵人分析
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shensha_agent import bazi_shensha_node

# 天乙贵人查法
TIANYI_MAP = {
    '甲': ['丑', '未'], '戊': ['丑', '未'],
    '乙': ['子', '申'], '己': ['子', '申'],
    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
    '壬': ['卯', '巳'], '癸': ['卯', '巳'],
    '庚': ['寅', '午'], '辛': ['寅', '午'],
}

# 太极贵人查法（以日干查）
TAIJI_MAP = {
    '甲': ['子', '午', '卯', '酉'], '乙': ['子', '午', '卯', '酉'],
    '丙': ['寅', '卯', '巳', '辰', '戌', '丑'], '丁': ['寅', '卯', '巳', '辰', '戌', '丑'],
    '戊': ['寅', '卯', '巳', '辰', '戌', '丑'], '己': ['寅', '卯', '巳', '辰', '戌', '丑'],
    '庚': ['申', '酉', '亥', '子', '辰', '丑'], '辛': ['申', '酉', '亥', '子', '辰', '丑'],
    '壬': ['申', '酉', '亥', '子', '辰', '丑'], '癸': ['申', '酉', '亥', '子', '辰', '丑'],
}

# 月德贵人查法（以月支查）
YUEDE_MAP = {
    '寅': '丙', '午': '丙', '戌': '丙',  # 寅午戌月见丙
    '申': '壬', '子': '壬', '辰': '壬',  # 申子辰月见壬
    '巳': '庚', '酉': '庚', '丑': '庚',  # 巳酉丑月见庚
    '亥': '甲', '卯': '甲', '未': '甲',  # 亥卯未月见甲
}

# 天德贵人查法（以月支查）
TIANDE_MAP = {
    '寅': '丁', '卯': '申', '辰': '壬', '巳': '辛',
    '午': '亥', '未': '甲', '申': '癸', '酉': '寅',
    '戌': '丙', '亥': '乙', '子': '庚', '丑': '己',
}

# 文昌贵人查法（以日干查）
WENCHANG_MAP = {
    '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
    '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
    '壬': '寅', '癸': '卯',
}

# 国印贵人查法（以日干查）
GUOYIN_MAP = {
    '甲': ['戌'], '乙': ['亥'], '丙': ['丑'], '丁': ['寅'],
    '戊': ['丑'], '己': ['寅'], '庚': ['辰'], '辛': ['巳'],
    '壬': ['未'], '癸': ['申'],
}


def analyze_male_guiren():
    """分析男方贵人"""
    
    print("=" * 70)
    print("男方贵人分析")
    print("出生：1997年1月3日 早上8点")
    print("=" * 70)
    
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
    
    nian_gan = nian_zhu['tian_gan']
    nian_zhi = nian_zhu['di_zhi']
    yue_zhi = yue_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    shi_zhi = shi_zhu['di_zhi']
    
    all_gan = [nian_zhu['tian_gan'], yue_zhu['tian_gan'], ri_zhu['tian_gan'], shi_zhu['tian_gan']]
    all_zhi = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    
    print(f"\n日干：{rizhu_gan}")
    print(f"年干：{nian_gan}")
    print(f"月支：{yue_zhi}")
    
    guiren_list = []
    
    # ========== 天乙贵人 ==========
    print(f"\n{'=' * 70}")
    print("【二、天乙贵人】（最重要的贵人）")
    print("=" * 70)
    
    print(f"\n天乙贵人查法：")
    print(f"  甲戊见牛羊（甲戊年/日干见丑未）")
    print(f"  乙己鼠猴乡（乙己年/日干见子申）")
    print(f"  丙丁猪鸡位（丙丁年/日干见亥酉）")
    print(f"  壬癸兔蛇藏（壬癸年/日干见卯巳）")
    print(f"  庚辛逢虎马（庚辛年/日干见寅午）")
    
    tianyi_by_nian = TIANYI_MAP.get(nian_gan, [])
    tianyi_by_ri = TIANYI_MAP.get(rizhu_gan, [])
    
    print(f"\n以年干{nian_gan}查天乙贵人：{tianyi_by_nian}")
    print(f"以日干{rizhu_gan}查天乙贵人：{tianyi_by_ri}")
    
    has_tianyi = False
    for zhi in tianyi_by_nian:
        if zhi in all_zhi:
            has_tianyi = True
            for i, z in enumerate(all_zhi):
                if z == zhi:
                    labels = ['年支', '月支', '日支', '时支']
                    guiren_list.append(f"天乙贵人（{labels[i]}{zhi}，以年干查）")
                    print(f"\n  ✓ {labels[i]}{zhi}为天乙贵人（以年干{nian_gan}查）")
    
    for zhi in tianyi_by_ri:
        if zhi in all_zhi:
            has_tianyi = True
            for i, z in enumerate(all_zhi):
                if z == zhi:
                    labels = ['年支', '月支', '日支', '时支']
                    guiren_list.append(f"天乙贵人（{labels[i]}{zhi}，以日干查）")
                    print(f"\n  ✓ {labels[i]}{zhi}为天乙贵人（以日干{rizhu_gan}查）")
    
    if not has_tianyi:
        print(f"\n  ✗ 命盘中无天乙贵人")
    
    print(f"\n天乙贵人含义：")
    print(f"  - 最大的吉星，逢凶化吉")
    print(f"  - 遇难成祥，有贵人相助")
    print(f"  - 一生多得贵人提携")
    
    # ========== 太极贵人 ==========
    print(f"\n{'=' * 70}")
    print("【三、太极贵人】")
    print("=" * 70)
    
    print(f"\n太极贵人查法：以日干查")
    print(f"  甲乙日见子午卯酉")
    print(f"  丙丁戊己日见寅卯巳辰戌丑")
    print(f"  庚辛壬癸日见申酉亥子辰丑")
    
    taiji_zhi = TAIJI_MAP.get(rizhu_gan, [])
    print(f"\n日干{rizhu_gan}的太极贵人：{taiji_zhi}")
    
    has_taiji = False
    for zhi in taiji_zhi:
        if zhi in all_zhi:
            has_taiji = True
            for i, z in enumerate(all_zhi):
                if z == zhi:
                    labels = ['年支', '月支', '日支', '时支']
                    guiren_list.append(f"太极贵人（{labels[i]}{zhi}）")
                    print(f"\n  ✓ {labels[i]}{zhi}为太极贵人")
    
    if not has_taiji:
        print(f"\n  ✗ 命盘中无太极贵人")
    
    print(f"\n太极贵人含义：")
    print(f"  - 主聪明、好学")
    print(f"  - 有特殊才能，喜欢研究")
    print(f"  - 与佛道有缘")
    
    # ========== 月德贵人 ==========
    print(f"\n{'=' * 70}")
    print("【四、月德贵人】")
    print("=" * 70)
    
    print(f"\n月德贵人查法：以月支查")
    print(f"  寅午戌月见丙")
    print(f"  申子辰月见壬")
    print(f"  巳酉丑月见庚")
    print(f"  亥卯未月见甲")
    
    yuede_gan = YUEDE_MAP.get(yue_zhi, '')
    print(f"\n月支{yue_zhi}的月德贵人：{yuede_gan}")
    
    has_yuede = False
    if yuede_gan and yuede_gan in all_gan:
        has_yuede = True
        for i, g in enumerate(all_gan):
            if g == yuede_gan:
                labels = ['年干', '月干', '日干', '时干']
                guiren_list.append(f"月德贵人（{labels[i]}{g}）")
                print(f"\n  ✓ {labels[i]}{g}为月德贵人")
    
    if not has_yuede:
        print(f"\n  ✗ 命盘中无月德贵人")
    
    print(f"\n月德贵人含义：")
    print(f"  - 逢凶化吉，遇难成祥")
    print(f"  - 性格温和，心地善良")
    print(f"  - 人缘好，多得贵人助")
    
    # ========== 天德贵人 ==========
    print(f"\n{'=' * 70}")
    print("【五、天德贵人】")
    print("=" * 70)
    
    print(f"\n天德贵人查法：以月支查")
    print(f"  正月见丁、二月见申、三月见壬、四月见辛")
    print(f"  五月见亥、六月见甲、七月见癸、八月见寅")
    print(f"  九月见丙、十月见乙、十一月见庚、十二月见己")
    
    tiande_gan = TIANDE_MAP.get(yue_zhi, '')
    print(f"\n月支{yue_zhi}的天德贵人：{tiande_gan}")
    
    has_tiande = False
    if tiande_gan and tiande_gan in all_gan:
        has_tiande = True
        for i, g in enumerate(all_gan):
            if g == tiande_gan:
                labels = ['年干', '月干', '日干', '时干']
                guiren_list.append(f"天德贵人（{labels[i]}{g}）")
                print(f"\n  ✓ {labels[i]}{g}为天德贵人")
    
    if not has_tiande:
        print(f"\n  ✗ 命盘中无天德贵人")
    
    print(f"\n天德贵人含义：")
    print(f"  - 逢凶化吉，化险为夷")
    print(f"  - 与月德贵人合称「天月二德」")
    print(f"  - 一生少病灾，贵人多助")
    
    # ========== 文昌贵人 ==========
    print(f"\n{'=' * 70}")
    print("【六、文昌贵人】")
    print("=" * 70)
    
    print(f"\n文昌贵人查法：以日干查")
    print(f"  甲见巳、乙见午、丙见申、丁见酉")
    print(f"  戊见申、己见酉、庚见亥、辛见子")
    print(f"  壬见寅、癸见卯")
    
    wenchang_zhi = WENCHANG_MAP.get(rizhu_gan, '')
    print(f"\n日干{rizhu_gan}的文昌贵人：{wenchang_zhi}")
    
    has_wenchang = False
    if wenchang_zhi and wenchang_zhi in all_zhi:
        has_wenchang = True
        for i, z in enumerate(all_zhi):
            if z == wenchang_zhi:
                labels = ['年支', '月支', '日支', '时支']
                guiren_list.append(f"文昌贵人（{labels[i]}{z}）")
                print(f"\n  ✓ {labels[i]}{z}为文昌贵人")
    
    if not has_wenchang:
        print(f"\n  ✗ 命盘中无文昌贵人")
    
    print(f"\n文昌贵人含义：")
    print(f"  - 主聪明、好学、有文采")
    print(f"  - 利于考试、升学")
    print(f"  - 适合从事文职、教育")
    
    # ========== 国印贵人 ==========
    print(f"\n{'=' * 70}")
    print("【七、国印贵人】")
    print("=" * 70)
    
    print(f"\n国印贵人查法：以日干查")
    print(f"  甲见戌、乙见亥、丙见丑、丁见寅")
    print(f"  戊见丑、己见寅、庚见辰、辛见巳")
    print(f"  壬见未、癸见申")
    
    guoyin_zhi = GUOYIN_MAP.get(rizhu_gan, [])
    print(f"\n日干{rizhu_gan}的国印贵人：{guoyin_zhi}")
    
    has_guoyin = False
    for zhi in guoyin_zhi:
        if zhi in all_zhi:
            has_guoyin = True
            for i, z in enumerate(all_zhi):
                if z == zhi:
                    labels = ['年支', '月支', '日支', '时支']
                    guiren_list.append(f"国印贵人（{labels[i]}{z}）")
                    print(f"\n  ✓ {labels[i]}{z}为国印贵人")
    
    if not has_guoyin:
        print(f"\n  ✗ 命盘中无国印贵人")
    
    print(f"\n国印贵人含义：")
    print(f"  - 主掌权、有官运")
    print(f"  - 适合从政、管理")
    print(f"  - 有威严、受人尊敬")
    
    # ========== 使用系统神煞分析 ==========
    print(f"\n{'=' * 70}")
    print("【八、系统神煞分析】")
    print("=" * 70)
    
    shensha_result = bazi_shensha_node(sizhu)
    if shensha_result.get('success'):
        shensha_list = shensha_result.get('shensha_list', [])
        print(f"\n命盘神煞：")
        if shensha_list:
            for ss in shensha_list:
                print(f"  ✓ {ss['name']}（{ss['position']}）")
        else:
            print(f"  无明显神煞")
    
    # ========== 总结 ==========
    print(f"\n{'=' * 70}")
    print("【九、贵人总结】")
    print("=" * 70)
    
    print(f"\n男方命盘贵人：")
    if guiren_list:
        for g in guiren_list:
            print(f"  ✓ {g}")
    else:
        print(f"  命盘中无明显贵人")
    
    print(f"\n贵人统计：")
    print(f"  天乙贵人：{'有' if has_tianyi else '无'}")
    print(f"  太极贵人：{'有' if has_taiji else '无'}")
    print(f"  月德贵人：{'有' if has_yuede else '无'}")
    print(f"  天德贵人：{'有' if has_tiande else '无'}")
    print(f"  文昌贵人：{'有' if has_wenchang else '无'}")
    print(f"  国印贵人：{'有' if has_guoyin else '无'}")
    
    # 分析贵人组合
    print(f"\n{'=' * 70}")
    print("【十、贵人组合分析】")
    print("=" * 70)
    
    if has_tianyi:
        print(f"\n★ 天乙贵人")
        print(f"  - 最大的贵人星")
        print(f"  - 逢凶化吉，遇难成祥")
        print(f"  - 一生多得贵人提携")
        print(f"  - 关键时刻总有人帮助")
    
    if has_taiji:
        print(f"\n★ 太极贵人")
        print(f"  - 主聪明、好学")
        print(f"  - 有特殊才能")
        print(f"  - 喜欢研究神秘事物")
        print(f"  - 可能对佛道感兴趣")
    
    if has_yuede and has_tiande:
        print(f"\n★ 天月二德俱全")
        print(f"  - 非常吉利")
        print(f"  - 一生少病灾")
        print(f"  - 贵人运极佳")
    elif has_yuede:
        print(f"\n★ 月德贵人")
        print(f"  - 性格温和")
        print(f"  - 人缘好")
    elif has_tiande:
        print(f"\n★ 天德贵人")
        print(f"  - 逢凶化吉")
        print(f"  - 化险为夷")
    
    print(f"\n{'=' * 70}")
    print("【结论】")
    print("=" * 70)
    
    guiren_count = len(guiren_list)
    
    if guiren_count >= 3:
        print(f"\n男方贵人运很好！共有{guiren_count}个贵人")
        print(f"一生多得贵人相助，关键时刻总能逢凶化吉")
    elif guiren_count >= 1:
        print(f"\n男方有贵人，共有{guiren_count}个贵人")
        print(f"关键时刻有贵人相助")
    else:
        print(f"\n男方命盘中无明显贵人")
        print(f"但可以通过后天的努力和积累来弥补")
    
    if has_tianyi:
        print(f"\n特别说明：")
        print(f"天乙贵人是最大的贵人星，有此贵人者：")
        print(f"  - 关键时刻总有人帮助")
        print(f"  - 遇到困难能逢凶化吉")
        print(f"  - 贵人运很强")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_guiren()
