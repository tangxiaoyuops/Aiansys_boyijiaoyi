"""
男方感情命理分析
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_CANG_GAN

# 桃花查法
TAOHUA_MAP = {
    '寅': '卯', '午': '卯', '戌': '卯',
    '申': '酉', '子': '酉', '辰': '酉',
    '巳': '午', '酉': '午', '丑': '午',
    '亥': '子', '卯': '子', '未': '子',
}

# 红艳煞查法（以日干查）
HONGYAN_MAP = {
    '甲': '午', '乙': '申', '丙': '寅', '丁': '未',
    '戊': '辰', '己': '辰', '庚': '戌', '辛': '酉',
    '壬': '子', '癸': '申',
}

# 红鸾查法（以年支查）
HONGLUAN_MAP = {
    '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
    '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
    '申': '未', '酉': '午', '戌': '巳', '亥': '辰',
}

# 天喜查法（以年支查）
TIANXI_MAP = {
    '子': '酉', '丑': '申', '寅': '未', '卯': '午',
    '辰': '巳', '巳': '辰', '午': '卯', '未': '寅',
    '申': '丑', '酉': '子', '戌': '亥', '亥': '戌',
}


def analyze_male_romance():
    """分析男方感情命理"""
    
    print("=" * 70)
    print("男方感情命理分析——是不是情种？")
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
    
    nian_zhi = nian_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    all_zhi = [nian_zhu['di_zhi'], yue_zhu['di_zhi'], ri_zhu['di_zhi'], shi_zhu['di_zhi']]
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n【二、妻星分析（男命看财星）】")
    print("=" * 70)
    
    print(f"\n日主：乙木")
    print(f"乙木克土为财，所以土是妻星")
    print(f"  - 阳土（戊土）= 正财 = 正妻")
    print(f"  - 阴土（己土）= 偏财 = 偏缘、桃花")
    
    # 找财星
    cai_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        if '财' in gan_shishen:
            cai_list.append({
                'position': f'{label}天干',
                'element': gan,
                'shishen': gan_shishen,
                'type': '透出'
            })
        
        for cg in zhi_cang_gan:
            if '财' in cg.get('shishen', ''):
                cai_list.append({
                    'position': f'{label}地支{zhi}',
                    'element': cg['cang_gan'],
                    'shishen': cg['shishen'],
                    'type': '藏干'
                })
    
    print(f"\n妻星（财星）分布：")
    if cai_list:
        for cai in cai_list:
            zheng_pian = '正财（正妻）' if '正财' in cai['shishen'] else '偏财（偏缘）'
            print(f"  - {cai['position']}：{cai['element']}（{cai['shishen']}，{zheng_pian}）")
    
    # 统计
    zheng_cai = [c for c in cai_list if '正财' in c['shishen']]
    pian_cai = [c for c in cai_list if '偏财' in c['shishen']]
    
    print(f"\n妻星统计：")
    print(f"  正财（正妻）：{len(zheng_cai)}个")
    print(f"  偏财（偏缘）：{len(pian_cai)}个")
    
    # 情种判断
    print(f"\n{'=' * 70}")
    print("【三、情种判断——看财星数量和位置】")
    print("=" * 70)
    
    print(f"\n情种的标准：")
    print(f"  1. 财星多（正财+偏财>=3个）")
    print(f"  2. 偏财多（偏缘多）")
    print(f"  3. 财星透干（异性缘明显）")
    print(f"  4. 财星混杂（正财偏财都有）")
    
    total_cai = len(cai_list)
    tou_gan = [c for c in cai_list if c['type'] == '透出']
    
    print(f"\n男方情况：")
    print(f"  - 财星总数：{total_cai}个 {'（较多）' if total_cai >= 3 else '（适中）'}")
    print(f"  - 偏财数量：{len(pian_cai)}个 {'（偏缘较多）' if len(pian_cai) >= 2 else ''}")
    print(f"  - 财星透干：{len(tou_gan)}个 {'（异性缘明显）' if len(tou_gan) > 0 else ''}")
    print(f"  - 财星混杂：{'是' if len(zheng_cai) > 0 and len(pian_cai) > 0 else '否'}")
    
    # 桃花星
    print(f"\n{'=' * 70}")
    print("【四、桃花星分析】")
    print("=" * 70)
    
    taohua_by_nian = TAOHUA_MAP.get(nian_zhi, '')
    taohua_by_ri = TAOHUA_MAP.get(ri_zhi, '')
    
    print(f"\n桃花查法：")
    print(f"  以年支{nian_zhi}查桃花：{taohua_by_nian}")
    print(f"  以日支{ri_zhi}查桃花：{taohua_by_ri}")
    
    taohua_list = []
    if taohua_by_nian in all_zhi:
        taohua_list.append(taohua_by_nian)
    if taohua_by_ri in all_zhi:
        taohua_list.append(taohua_by_ri)
    
    if taohua_list:
        print(f"\n✓ 命带桃花！")
        for zhi in set(taohua_list):
            for i, z in enumerate(all_zhi):
                if z == zhi:
                    labels = ['年支', '月支', '日支', '时支']
                    print(f"  - {labels[i]}{zhi}为桃花")
    else:
        print(f"\n✗ 命盘中无桃花星")
    
    # 红艳煞
    print(f"\n{'=' * 70}")
    print("【五、红艳煞分析】")
    print("=" * 70)
    
    hongyan_zhi = HONGYAN_MAP.get(rizhu_gan, '')
    print(f"\n红艳煞查法：以日干查")
    print(f"  日干{rizhu_gan}的红艳煞：{hongyan_zhi}")
    
    if hongyan_zhi in all_zhi:
        print(f"\n✓ 命带红艳煞！")
        for i, z in enumerate(all_zhi):
            if z == hongyan_zhi:
                labels = ['年支', '月支', '日支', '时支']
                print(f"  - {labels[i]}{hongyan_zhi}为红艳煞")
        print(f"\n  红艳煞含义：风流好色，异性缘极好")
    else:
        print(f"\n✗ 命盘中无红艳煞")
    
    # 红鸾天喜
    print(f"\n{'=' * 70}")
    print("【六、红鸾天喜分析】")
    print("=" * 70)
    
    hongluan_zhi = HONGLUAN_MAP.get(nian_zhi, '')
    tianxi_zhi = TIANXI_MAP.get(nian_zhi, '')
    
    print(f"\n红鸾查法：以年支查")
    print(f"  年支{nian_zhi}的红鸾：{hongluan_zhi}")
    print(f"  年支{nian_zhi}的天喜：{tianxi_zhi}")
    
    if hongluan_zhi in all_zhi:
        print(f"\n✓ 命带红鸾！主婚恋喜庆")
    else:
        print(f"\n✗ 命盘中无红鸾")
    
    if tianxi_zhi in all_zhi:
        print(f"✓ 命带天喜！主喜庆好事")
    else:
        print(f"✗ 命盘中无天喜")
    
    # 伤官分析（影响感情）
    print(f"\n{'=' * 70}")
    print("【七、伤官分析——影响感情的因素】")
    print("=" * 70)
    
    print(f"\n伤官对感情的影响：")
    print(f"  伤官代表：表达、才华、浪漫、但也可能花心")
    print(f"  男命伤官：会讨女人欢心、有浪漫情调")
    
    shangguan_list = []
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        
        if '伤官' in gan_shishen:
            shangguan_list.append({'position': f'{label}天干', 'element': gan})
        for cg in zhi_cang_gan:
            if '伤官' in cg.get('shishen', ''):
                shangguan_list.append({'position': f'{label}地支', 'element': cg['cang_gan']})
    
    if shangguan_list:
        print(f"\n命带伤官：")
        for sg in shangguan_list:
            print(f"  - {sg['position']}：{sg['element']}")
        print(f"\n  影响：")
        print(f"  - 会说话、会哄人、有浪漫情调")
        print(f"  - 但也可能花心、不安分")
    else:
        print(f"\n✗ 命盘中无伤官")
    
    # 综合判断
    print(f"\n{'=' * 70}")
    print("【八、综合判断——是不是情种？】")
    print("=" * 70)
    
    # 计算情种指数
    qingzhong_score = 0
    reasons = []
    
    # 财星数量
    if total_cai >= 3:
        qingzhong_score += 2
        reasons.append("财星多（妻缘旺）")
    elif total_cai >= 2:
        qingzhong_score += 1
        reasons.append("财星适中")
    
    # 偏财多
    if len(pian_cai) >= 2:
        qingzhong_score += 2
        reasons.append("偏财多（偏缘多）")
    elif len(pian_cai) >= 1:
        qingzhong_score += 1
        reasons.append("有偏财")
    
    # 桃花
    if len(taohua_list) > 0:
        qingzhong_score += 1
        reasons.append("命带桃花")
    
    # 红艳煞
    if hongyan_zhi in all_zhi:
        qingzhong_score += 2
        reasons.append("命带红艳煞（风流）")
    
    # 伤官
    if len(shangguan_list) > 0:
        qingzhong_score += 1
        reasons.append("命带伤官（会哄人）")
    
    # 财星透干
    if len(tou_gan) > 0:
        qingzhong_score += 1
        reasons.append("财星透干（异性缘明显）")
    
    print(f"\n情种指数：{qingzhong_score}分")
    print(f"\n情种特征：")
    for r in reasons:
        print(f"  ✓ {r}")
    
    print(f"\n判断标准：")
    print(f"  0-2分：不是情种，感情专一")
    print(f"  3-5分：有异性缘，但还算正常")
    print(f"  6-8分：情种苗子，异性缘好")
    print(f"  9分以上：典型情种，风流多情")
    
    if qingzhong_score >= 9:
        result = "典型情种"
        desc = "风流多情，异性缘极好，容易招惹桃花"
    elif qingzhong_score >= 6:
        result = "有情种潜质"
        desc = "异性缘好，会哄人，但还可以控制"
    elif qingzhong_score >= 3:
        result = "有异性缘"
        desc = "正常的异性缘，感情方面比较正常"
    else:
        result = "不是情种"
        desc = "感情专一，不花心"
    
    print(f"\n【结论】")
    print(f"  男方：{result}")
    print(f"  说明：{desc}")
    
    # 对感情的态度
    print(f"\n{'=' * 70}")
    print("【九、对感情的态度】")
    print("=" * 70)
    
    print(f"""
根据命盘分析：

【好的方面】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 有正财：重视婚姻，有责任心
  → 正财在时支辰：妻子在命盘中，重视家庭

✓ 有偏财：异性缘好，但有界限
  → 偏财在月支丑、日支未：有人缘，但不一定会出轨

✓ 时柱正官：对感情有责任感
  → 时干庚金正官：对家庭负责，有担当

✓ 天乙贵人：逢凶化吉
  → 年支子为天乙贵人：有贵人运

【需要注意的方面】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
△ 偏财较多：异性缘好，需要把握分寸
  → 月支丑、日支未都有偏财

△ 伤官透干：会说话、会哄人
  → 可能招蜂引蝶，需要自我约束

△ 七杀透干：事业心强
  → 可能因为事业忽略感情

【感情特点】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 异性缘：较好（财星多）
• 会哄人：是的（伤官透干）
• 浪漫程度：有（伤官+偏财）
• 专一程度：中等（有正财也有偏财）
• 责任感：有（时柱正官）

【最终判断】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
男方属于"有异性缘但不是花心大萝卜"类型

  - 有情调、会哄人（伤官）
  - 异性缘好（财星多）
  - 但有责任感（正官）
  - 对婚姻有承诺（正财）

总体评价：会疼人、有情趣、但需要把握好尺度
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_romance()
