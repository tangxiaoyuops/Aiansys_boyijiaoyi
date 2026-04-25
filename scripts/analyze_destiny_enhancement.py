"""
分析命局特征和五行调节
1997年1月3日8时 男命
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.bazi_calculator import (
    calculate_sizhu, calculate_wuxing, calculate_shishen,
    calculate_dayun, calculate_shensha,
    TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_WUXING,
    WUXING_KE, WUXING_SHENG
)

def analyze_destiny():
    """分析命局"""
    
    # 您的八字
    year = 1997
    month = 1
    day = 3
    hour = 8
    gender = '男'
    
    sizhu = calculate_sizhu(year, month, day, hour)
    wuxing = calculate_wuxing(sizhu)
    shishen = calculate_shishen(sizhu, sizhu['ri_zhu_tiangan'])
    shensha = calculate_shensha(sizhu)
    dayun = calculate_dayun(year, month, day, hour, gender)
    
    rizhu = sizhu['ri_zhu_tiangan']
    rizhu_wuxing = TIAN_GAN_WUXING[rizhu]
    rizhu_yinyang = TIAN_GAN_YINYANG[rizhu]
    
    print("="*70)
    print("命局分析 - 1997年1月3日8时 男命")
    print("="*70)
    
    print(f"\n【八字排盘】")
    print(f"年柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}")
    print(f"月柱: {sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}")
    print(f"日柱: {sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}")
    print(f"时柱: {sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}")
    
    print(f"\n【日主分析】")
    print(f"日主: {rizhu} ({rizhu_wuxing}) - {'阳' if rizhu_yinyang == '阳' else '阴'}木")
    
    print(f"\n【五行分布】")
    print(f"金: {wuxing['jin']}  木: {wuxing['mu']}  水: {wuxing['shui']}  火: {wuxing['huo']}  土: {wuxing['tu']}")
    print(f"日主五行: {rizhu_wuxing}")
    
    # 分析日主强弱
    print(f"\n【日主强弱分析】")
    
    # 统计帮扶日主的力量
    # 帮扶日主的是：比劫（同我）、印星（生我）
    # 木日主：帮扶力量是木（比劫）和水（印星）
    
    help_count = wuxing['mu'] + wuxing['shui']  # 比劫 + 印星
    exhaust_count = wuxing['huo'] + wuxing['tu'] + wuxing['jin']  # 食伤 + 财 + 官杀
    
    print(f"帮扶力量（水+木）: {help_count}")
    print(f"耗泄力量（火+土+金）: {exhaust_count}")
    
    if help_count > exhaust_count:
        print(f"日主状态: 身旺（帮扶力量强）")
        rizhu_status = "身旺"
    elif help_count < exhaust_count:
        print(f"日主状态: 身弱（耗泄力量强）")
        rizhu_status = "身弱"
    else:
        print(f"日主状态: 中和")
        rizhu_status = "中和"
    
    print(f"\n【十神配置】")
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        zhu = sizhu.get(zhu_name, {})
        gan = zhu.get('tian_gan', '')
        zhi = zhu.get('di_zhi', '')
        ss = shishen.get(zhu_name, {})
        gan_ss = ss.get('gan_shishen', '')
        zhi_ss = ss.get('zhi_shishen', '')
        print(f"{zhu_name}: {gan}({gan_ss}) {zhi}({zhi_ss})")
    
    print(f"\n【神煞】")
    for ss in shensha.get('shensha_list', []):
        print(f"  {ss['name']} - 位置: {ss['position']}, 类型: {ss['type']}")
    
    print(f"\n【大运】")
    for i, dy in enumerate(dayun[:5]):
        print(f"  第{i+1}步: {dy['gan']}{dy['zhi']} ({dy['start_age']}-{dy['end_age']}岁)")
    
    # 分析命局特质
    print("\n" + "="*70)
    print("命局特质分析")
    print("="*70)
    
    print(f"""
【乙木日主的特质】

乙木 = 阴木，花草之木，藤蔓之木

性格特点：
┌─────────────────────────────────────────────────────────────────┐
│ 优点：                                                          │
│ ★ 温和柔顺 - 不像甲木那样刚直                                   │
│ ★ 适应力强 - 能屈能伸，像藤蔓一样                               │
│ ★ 善于合作 - 懂得借力，善于依附                                 │
│ ★ 心思细腻 - 考虑问题周全                                       │
│ ★ 仁慈善良 - 木主仁，心地好                                     │
│ ★ 有韧性 - 遇到困难能坚持                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 弱点：                                                          │
│ ★ 优柔寡断 - 想得太多，不够果断                                 │
│ ★ 缺乏魄力 - 不敢冒险，求稳为主                                 │
│ ★ 依赖性强 - 喜欢依附他人或环境                                 │
│ ★ 随波逐流 - 容易受环境影响                                     │
└─────────────────────────────────────────────────────────────────┘

【您的命局特点】
""")
    
    # 分析官杀
    guan_sha_count = 0
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        ss = shishen.get(zhu_name, {})
        if ss.get('gan_shishen') in ['正官', '偏官']:
            guan_sha_count += 1
        if ss.get('zhi_shishen') in ['正官', '偏官']:
            guan_sha_count += 1
    
    print(f"官杀力量: {guan_sha_count}处")
    
    # 分析财星
    cai_count = 0
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        ss = shishen.get(zhu_name, {})
        if ss.get('gan_shishen') in ['正财', '偏财']:
            cai_count += 1
        if ss.get('zhi_shishen') in ['正财', '偏财']:
            cai_count += 1
    
    print(f"财星力量: {cai_count}处")
    
    # 分析印星
    yin_count = 0
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        ss = shishen.get(zhu_name, {})
        if ss.get('gan_shishen') in ['正印', '偏印']:
            yin_count += 1
        if ss.get('zhi_shishen') in ['正印', '偏印']:
            yin_count += 1
    
    print(f"印星力量: {yin_count}处")
    
    print(f"""
【命局格局判断】

日主乙木，生于子月（冬月）：
- 水旺木相，有印星生扶
- 年支子、月支子、时支辰都有水
- 水多木漂，需要土来制水

命局特点：
1. 印星较旺（水多）= 学习能力强，有贵人相助
2. 财星透出（土）= 有财运，务实
3. 官杀有根（金）= 事业心，但不算太强

整体格局：身旺有财官，属于中上格局
""")
    
    # 分析如果增强金（官杀）的影响
    print("\n" + "="*70)
    print("如果增强'果断、拼搏'特质的影响分析")
    print("="*70)
    
    print(f"""
【问题核心】

"果断、拼搏"的特质对应五行中的【金】（官杀）

金克木，官杀克日主：
- 正官（阴金辛）= 约束、规范、责任
- 七杀（阳金庚）= 果断、魄力、拼搏

您命局中：
- 天干有庚金（月干、时干）= 有七杀力量
- 地支有酉金（未土藏干有辛金）= 有正官力量
- 整体官杀力量适中
""")
    
    # 判断身旺身弱对官杀的需求
    if rizhu_status == "身旺":
        print(f"""
【您的命局身旺，可以担官杀】

身旺 + 官杀 = 好事！

因为：
- 身旺 = 自身力量强，能承受压力
- 官杀 = 事业、责任、拼搏
- 身旺担官杀 = 有能力担当事业，能抗压

如果您增强"果断、拼搏"的特质：
┌─────────────────────────────────────────────────────────────────┐
│ 积极影响：                                                      │
│ ★ 事业发展更快 - 更有魄力做决策                                │
│ ★ 提升领导力 - 敢于承担责任                                    │
│ ★ 突破自我 - 不再优柔寡断                                      │
│ ★ 增加魅力 - 更有男子气概                                      │
│ ★ 把握机会 - 敢于冒险尝试                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 需要注意：                                                      │
│ ★ 不要过度 - 身旺但也有限度，过犹不及                          │
│ ★ 保持平衡 - 果断不等于鲁莽                                    │
│ ★ 注意健康 - 官杀过旺会克身，注意肝胆（木）                     │
└─────────────────────────────────────────────────────────────────┘
""")
    else:
        print(f"""
【您的命局身弱，增强官杀需要谨慎】

身弱 + 官杀增强 = 压力增大

因为：
- 身弱 = 自身力量不足
- 官杀增强 = 压力增大
- 身弱不胜官杀 = 可能承受不住压力

建议：先补足自身力量（水木），再增强官杀
""")
    
    print(f"""
【具体建议】

如果想让"果断、拼搏"特质增强：

1. 行为调整：
   - 有意识地快速做决定，不拖延
   - 设定明确目标，执行到位
   - 锻炼身体，增强体魄（木主肝，金主肺）
   - 接受挑战，主动承担责任

2. 环境调整：
   - 西方（金方）发展有利
   - 穿白色、金色衣物
   - 办公室摆放金属装饰

3. 职业选择：
   - 管理、决策类工作
   - 金融、法律、军警（金属性行业）
   - 需要果断决策的岗位

4. 时运配合：
   - 逢庚辛年、申酉年（金年）运势更旺
   - 秋季（金旺）做重要决策
""")
    
    # 分析对感情的影响
    print("\n" + "="*70)
    print("增强官杀对感情的影响")
    print("="*70)
    
    print(f"""
【对感情的影响】

您是乙木日主：
- 妻星 = 土（财星）
- 官杀 = 金（克制日主的力量）

增强官杀（果断、拼搏）后：

对感情的积极影响：
1. 更有担当 - 女性喜欢有魄力的男人
2. 更有主见 - 不再优柔寡断，让女方有安全感
3. 事业心更强 - 经济基础更稳固
4. 更有魅力 - "霸道总裁"的气质增加

可能的挑战：
1. 可能过于强势 - 需要注意给对方空间
2. 事业与家庭平衡 - 不要因为拼搏忽略感情
3. 沟通方式 - 果断不等于不讲道理

【对戊土女的影响】

戊土女需要：
- 官杀（木）= 夫星
- 您增强官杀 = 增强对她的"夫星"特质
- 这会让您更有"男人味"

但是：
- 您是乙木 = 她的正官（温和型）
- 如果您变得太强势 = 可能变成"类七杀"
- 这会让她觉得"不太像原来的你"

建议：
- 保持乙木的温和底色
- 在关键时刻果断
- 平时依然体贴温柔
- 这就是"刚柔并济"
""")
    
    # 总结
    print("\n" + "="*70)
    print("总结")
    print("="*70)
    
    print(f"""
【核心结论】

1. 您的命局【身旺】，可以担官杀
   → 增强"果断、拼搏"特质对您有利

2. 增强后影响：
   正面：事业提升、更有魅力、更担当
   注意：保持平衡、不过度、注意健康

3. 对感情的影响：
   → 增加男子气概，更有安全感
   → 但不要丢掉乙木的温和底色
   → "刚柔并济"才是最佳状态

4. 最佳策略：
   → 保持乙木的温和、善良
   → 在关键时刻展现果断
   → 平时温柔，大事有主见
   → 这比单纯的"变强势"更好

【一句话建议】

不用刻意"变强势"，而是在关键时刻"敢于拍板"。
温和是您的底色，果断是您的武器，两者结合才是王道。
""")


if __name__ == "__main__":
    analyze_destiny()
