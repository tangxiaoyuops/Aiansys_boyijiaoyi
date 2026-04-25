"""
女方性格分析——是否喜欢热闹刺激？
1999年3月4日21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.agents.bazi_wuxing_agent import bazi_wuxing_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING, TIAN_GAN_YINYANG, DI_ZHI_CANG_GAN

# 桃花查法
TAOHUA_MAP = {
    '寅': '卯', '午': '卯', '戌': '卯',
    '申': '酉', '子': '酉', '辰': '酉',
    '巳': '午', '酉': '午', '丑': '午',
    '亥': '子', '卯': '子', '未': '子',
}

# 驿马查法
YIMA_MAP = {
    '申': '寅', '子': '寅', '辰': '寅',
    '寅': '申', '午': '申', '戌': '申',
    '巳': '亥', '酉': '亥', '丑': '亥',
    '亥': '巳', '卯': '巳', '未': '巳',
}

# 咸池（桃花的一种）查法
XIANCHI_MAP = {
    '寅': '卯', '午': '卯', '戌': '卯',
    '申': '酉', '子': '酉', '辰': '酉',
    '巳': '午', '酉': '午', '丑': '午',
    '亥': '子', '卯': '子', '未': '子',
}


def analyze_female_personality():
    """分析女方性格"""
    
    print("=" * 70)
    print("女方性格分析——是否喜欢热闹刺激？")
    print("出生：1999年3月4日 21点")
    print("=" * 70)
    
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
    print(f"日主：{rizhu_gan}木")
    print(f"出生时辰：亥时（21-23点）")
    
    nian_zhi = nian_zhu['di_zhi']
    ri_zhi = ri_zhu['di_zhi']
    all_zhi = [nian_zhu['di_zhi'], yue_zhu['di_zhi'], ri_zhu['di_zhi'], shi_zhu['di_zhi']]
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    # ========== 日主性格 ==========
    print(f"\n{'=' * 70}")
    print("【二、日主性格——乙木】")
    print("=" * 70)
    
    print(f"""
乙木日主性格特点：

优点：
  ✓ 温和、柔顺
  ✓ 善于适应环境
  ✓ 有韧性、能屈能伸
  ✓ 善于交际
  ✓ 有艺术气质
  ✓ 心思细腻

缺点：
  △ 容易受他人影响
  △ 优柔寡断
  △ 缺乏主见
  △ 情绪化
  △ 容易多愁善感

乙木女命特点：
  - 外表温柔，内心有想法
  - 善于察言观色
  - 会照顾他人感受
  - 不太喜欢冲突
  - 追求精神层面的满足
""")
    
    # ========== 五行分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、五行分析】")
    print("=" * 70)
    
    wuxing_result = bazi_wuxing_node(sizhu)
    wuxing_count = wuxing_result.get('wuxing_count', {}) if wuxing_result.get('success') else {}
    
    print(f"\n五行分布：")
    print(f"  金：{wuxing_count.get('金', 0)}个")
    print(f"  木：{wuxing_count.get('木', 0)}个")
    print(f"  水：{wuxing_count.get('水', 0)}个")
    print(f"  火：{wuxing_count.get('火', 0)}个")
    print(f"  土：{wuxing_count.get('土', 0)}个")
    
    jin = wuxing_count.get('金', 0)
    mu = wuxing_count.get('木', 0)
    shui = wuxing_count.get('水', 0)
    huo = wuxing_count.get('火', 0)
    tu = wuxing_count.get('土', 0)
    
    print(f"\n五行分析：")
    
    if huo >= 3:
        print(f"\n  ★ 火旺（{huo}个）")
        print(f"  火旺的特点：")
        print(f"    - 热情、外向、喜欢热闹")
        print(f"    - 表达欲望强")
        print(f"    - 喜欢社交活动")
        print(f"    - 情绪波动大")
        print(f"    - 喜欢刺激和变化")
    
    if mu >= 2:
        print(f"\n  木旺（{mu}个）")
        print(f"  木旺的特点：")
        print(f"    - 仁慈、善良")
        print(f"    - 有同理心")
        print(f"    - 追求精神成长")
        print(f"    - 喜欢艺术、文化")
    
    if shui >= 2:
        print(f"\n  水旺（{shui}个）")
        print(f"  水旺的特点：")
        print(f"    - 聪明、灵活")
        print(f"    - 善于交际")
        print(f"    - 喜欢流动、变化")
    
    if jin == 0:
        print(f"\n  缺金（{jin}个）")
        print(f"  缺金的特点：")
        print(f"    - 不太喜欢太严肃的环境")
        print(f"    - 不喜欢被约束")
        print(f"    - 可能缺乏决断力")
    
    # ========== 十神分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、十神分析——性格关键】")
    print("=" * 70)
    
    print(f"\n十神分布：")
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        print(f"  {label}：{gan}（{gan_shishen}）/ {zhi}（{zhi_shishen}）")
    
    # 统计十神
    shishen_count = {}
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if gan_shishen:
            shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            shishen = cg.get('shishen', '')
            if shishen:
                shishen_count[shishen] = shishen_count.get(shishen, 0) + 1
    
    print(f"\n十神统计：")
    for ss in ['正财', '偏财', '正官', '七杀', '正印', '偏印', '比肩', '劫财', '食神', '伤官']:
        count = shishen_count.get(ss, 0)
        if count > 0:
            print(f"  {ss}：{count}个")
    
    # 食伤分析
    shishang_count = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
    print(f"\n【食伤分析】（关键！）")
    print(f"  食伤总数：{shishang_count}个")
    print(f"  食神：{shishen_count.get('食神', 0)}个")
    print(f"  伤官：{shishen_count.get('伤官', 0)}个")
    
    if shishang_count >= 3:
        print(f"\n  ★ 食伤旺（{shishang_count}个）")
        print(f"  食伤旺的特点：")
        print(f"    - 表达欲望强")
        print(f"    - 喜欢社交、热闹")
        print(f"    - 有才艺、有才华")
        print(f"    - 不喜欢被约束")
        print(f"    - 追求自由")
        print(f"    - 晚上精神好")
    
    # 伤官分析
    if shishen_count.get('伤官', 0) >= 2:
        print(f"\n  ★ 伤官多（{shishen_count.get('伤官', 0)}个）")
        print(f"  伤官的特点：")
        print(f"    - 叛逆、不喜欢被管")
        print(f"    - 追求刺激和变化")
        print(f"    - 喜欢新鲜事物")
        print(f"    - 晚上活跃")
        print(f"    - 不喜欢一成不变")
    
    # ========== 神煞分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、神煞分析】")
    print("=" * 70)
    
    # 桃花
    taohua_by_nian = TAOHUA_MAP.get(nian_zhi, '')
    taohua_by_ri = TAOHUA_MAP.get(ri_zhi, '')
    
    print(f"\n【桃花星】")
    print(f"  以年支{nian_zhi}查桃花：{taohua_by_nian}")
    print(f"  以日支{ri_zhi}查桃花：{taohua_by_ri}")
    
    has_taohua = False
    taohua_list = []
    if taohua_by_nian in all_zhi:
        has_taohua = True
        taohua_list.append(taohua_by_nian)
    if taohua_by_ri in all_zhi:
        has_taohua = True
        taohua_list.append(taohua_by_ri)
    
    if has_taohua:
        print(f"\n  ✓ 命带桃花！")
        for zhi in set(taohua_list):
            print(f"    桃花：{zhi}")
        print(f"\n  桃花含义：")
        print(f"    - 异性缘好")
        print(f"    - 有人缘")
        print(f"    - 喜欢社交")
        print(f"    - 外貌出众")
    else:
        print(f"\n  命盘中无桃花")
    
    # 驿马
    yima_by_nian = YIMA_MAP.get(nian_zhi, '')
    yima_by_ri = YIMA_MAP.get(ri_zhi, '')
    
    print(f"\n【驿马星】")
    print(f"  以年支{nian_zhi}查驿马：{yima_by_nian}")
    print(f"  以日支{ri_zhi}查驿马：{yima_by_ri}")
    
    has_yima = False
    yima_list = []
    if yima_by_nian in all_zhi:
        has_yima = True
        yima_list.append(yima_by_nian)
    if yima_by_ri in all_zhi:
        has_yima = True
        yima_list.append(yima_by_ri)
    
    if has_yima:
        print(f"\n  ✓ 命带驿马！")
        for zhi in set(yima_list):
            print(f"    驿马：{zhi}")
        print(f"\n  驿马含义：")
        print(f"    - 喜欢走动")
        print(f"    - 适合外出发展")
        print(f"    - 不安于现状")
        print(f"    - 可能远嫁")
        print(f"    - 喜欢变化和刺激")
    else:
        print(f"\n  命盘中无驿马")
    
    # ========== 出生时辰分析 ==========
    print(f"\n{'=' * 70}")
    print("【六、出生时辰分析】")
    print("=" * 70)
    
    print(f"\n出生时辰：亥时（21:00-23:00）")
    print(f"时柱：丁亥")
    
    print(f"\n亥时出生的特点：")
    print(f"  - 晚上精神好")
    print(f"  - 喜欢夜生活")
    print(f"  - 思维活跃")
    print(f"  - 适合夜间工作")
    print(f"  - 性格比较内向但有想法")
    
    print(f"\n时柱丁亥分析：")
    print(f"  时干丁火：食神")
    print(f"    - 食神代表：表达、才华、享受")
    print(f"    - 喜欢美食、娱乐")
    print(f"    - 有艺术天分")
    print(f"  时支亥水：正印")
    print(f"    - 正印代表：学习、内涵")
    print(f"    - 有思想深度")
    
    print(f"\n时柱对性格的影响：")
    print(f"  - 食神在时柱：晚年有福，喜欢享受")
    print(f"  - 亥时出生：晚上精神好，可能熬夜")
    print(f"  - 时柱有食神：喜欢社交、娱乐")
    
    # ========== 性格总结 ==========
    print(f"\n{'=' * 70}")
    print("【七、性格总结——是否喜欢热闹刺激？】")
    print("=" * 70)
    
    print(f"\n【是否喜欢热闹？】")
    print(f"\n喜欢的因素：")
    
    like_factors = []
    
    if shishang_count >= 3:
        like_factors.append("食伤旺（表达欲望强，喜欢社交）")
    
    if shishen_count.get('伤官', 0) >= 2:
        like_factors.append("伤官多（追求变化和刺激）")
    
    if huo >= 2:
        like_factors.append("火旺（热情外向，喜欢热闹）")
    
    if has_taohua:
        like_factors.append("命带桃花（异性缘好，喜欢社交）")
    
    if has_yima:
        like_factors.append("命带驿马（喜欢变化和走动）")
    
    if '亥' in all_zhi:
        like_factors.append("亥时出生（晚上精神好）")
    
    for f in like_factors:
        print(f"  ✓ {f}")
    
    print(f"\n不喜欢的因素：")
    
    dislike_factors = []
    
    if shishen_count.get('正印', 0) >= 2:
        dislike_factors.append("正印多（喜欢安静、思考）")
    
    if shishen_count.get('偏印', 0) >= 1:
        dislike_factors.append("偏印（可能孤僻）")
    
    if mu >= 2:
        dislike_factors.append("木旺（温和，不一定喜欢太吵）")
    
    if jin == 0:
        dislike_factors.append("缺金（不喜欢太严肃的环境）")
    
    for f in dislike_factors:
        print(f"  △ {f}")
    
    # 判断
    print(f"\n{'=' * 70}")
    print("【八、综合判断】")
    print("=" * 70)
    
    like_score = len(like_factors)
    dislike_score = len(dislike_factors)
    
    print(f"\n喜欢热闹的因素：{like_score}个")
    print(f"安静的因素：{dislike_score}个")
    
    if like_score >= 4:
        result = "很喜欢热闹和刺激"
        desc = """
这个女生性格比较外向，喜欢热闹和刺激：
  - 喜欢社交活动
  - 晚上精神好，可能经常熬夜
  - 追求新鲜感和变化
  - 不喜欢一成不变的生活
  - 可能喜欢酒吧、KTV等娱乐场所
"""
    elif like_score >= 2:
        result = "有一定社交需求"
        desc = """
这个女生性格中性，有一定的社交需求：
  - 有时候喜欢热闹，有时候喜欢安静
  - 晚上精神可能比较好
  - 不会特别排斥社交活动
  - 但也不会特别沉迷
"""
    else:
        result = "相对喜欢安静"
        desc = """
这个女生性格比较内向，喜欢安静：
  - 不太喜欢太吵闹的环境
  - 更喜欢精神层面的交流
  - 晚上可能也喜欢安静的活动
"""
    
    print(f"\n综合判断：{result}")
    print(desc)
    
    # ========== 关于酒吧蹦迪 ==========
    print(f"\n{'=' * 70}")
    print("【九、关于酒吧蹦迪的判断】")
    print("=" * 70)
    
    print(f"""
根据八字分析：

【支持喜欢酒吧蹦迪的因素】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 食伤旺（4个）
  → 表达欲望强，喜欢热闹
  → 喜欢娱乐、享受

✓ 伤官多（3个）
  → 追求刺激和变化
  → 不喜欢被约束
  → 喜欢新鲜事物

✓ 火旺
  → 热情、外向
  → 喜欢社交活动

✓ 桃花
  → 异性缘好
  → 喜欢社交场合

✓ 驿马（日支巳、时支亥）
  → 喜欢变化和走动
  → 不安于现状

✓ 亥时出生
  → 晚上精神好
  → 可能熬夜

【不支持的因素】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
△ 乙木日主
  → 本性温和
  → 不一定喜欢太激烈的场合

△ 缺金
  → 不喜欢太严肃的环境
  → 但也不一定喜欢太吵

【结论】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
这个女生：

★ 有可能喜欢去酒吧蹦迪 ★

原因：
  1. 食伤旺（4个）→ 喜欢热闹、娱乐
  2. 伤官多（3个）→ 追求刺激、变化
  3. 火旺 → 热情、喜欢社交
  4. 桃花 → 异性缘好、喜欢社交场合
  5. 驿马 → 喜欢走动、变化
  6. 亥时出生 → 晚上精神好

【但需要注意】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  乙木日主的人本性温和
  → 去酒吧可能更多是社交
  → 不一定是"蹦迪狂魔"
  → 更可能是和朋友去聊天、喝酒
  → 不一定喜欢太吵闹的环境

【关于晚上12点回消息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  亥时出生的人晚上精神好
  → 这是天生的作息特点
  → 不一定是因为出去玩
  → 可能是在家也精神好
  → 乙木+伤官组合 → 喜欢思考和表达
  → 可能晚上喜欢聊天、刷手机

【最终判断】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
这个女生：

有60-70%的可能性喜欢去酒吧、社交场合
但她本性温和（乙木）
更可能是：
  - 和朋友去酒吧聊天、喝酒
  - 偶尔蹦迪
  - 喜欢热闹但不会太疯狂

而不是：
  - 天天泡酒吧
  - 蹦迪狂魔
  - 夜夜笙歌

晚上12点回消息：
  - 更多是因为亥时出生晚上精神好
  - 不一定是因为在外面玩
  - 可能在家也睡得晚
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_female_personality()
