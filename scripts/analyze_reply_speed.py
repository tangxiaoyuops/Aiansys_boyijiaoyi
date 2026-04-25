"""
女方回消息慢的原因——八字分析
1999年3月4日21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_shishen_agent import bazi_shishen_node
from core.tools.bazi_calculator import TIAN_GAN_WUXING, DI_ZHI_CANG_GAN

def analyze_reply_speed():
    """分析女方回消息慢的原因"""
    
    print("=" * 70)
    print("女方回消息慢的原因——八字分析")
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
    
    # 十神分析
    shishen_result = bazi_shishen_node(sizhu)
    shishen_data = shishen_result.get('shishen_data', {})
    
    print(f"\n十神分布：")
    for zhu_name, label in [('nian_zhu', '年柱'), ('yue_zhu', '月柱'), ('ri_zhu', '日柱'), ('shi_zhu', '时柱')]:
        gan = sizhu[zhu_name]['tian_gan']
        zhi = sizhu[zhu_name]['di_zhi']
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        zhi_shishen = shishen_data.get(zhu_name, {}).get('zhi_shishen', '')
        print(f"  {label}：{gan}（{gan_shishen}）/ {zhi}（{zhi_shishen}）")
    
    # ========== 日主性格 ==========
    print(f"\n{'=' * 70}")
    print("【二、日主性格——乙木】")
    print("=" * 70)
    
    print(f"""
乙木日主的特点：

【性格特点】
  ✓ 温和、柔顺
  ✓ 善于适应环境
  ✓ 有韧性
  ✓ 心思细腻
  ✓ 善于察言观色

【沟通特点】
  △ 不喜欢冲突
  △ 不喜欢直接拒绝
  △ 可能犹豫不决
  △ 想很多再回复
  △ 容易受他人影响
  △ 需要时间消化信息

【对消息的态度】
  → 不是不回，是要想好再回
  → 可能同时在想别的事
  → 乙木人容易分心
  → 可能看到了但不知道怎么回
""")
    
    # ========== 食伤分析 ==========
    print(f"\n{'=' * 70}")
    print("【三、食伤分析——影响沟通的关键】")
    print("=" * 70)
    
    # 统计食伤
    shishang_count = 0
    shangguan_count = 0
    shishen_count = 0
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if '食神' in gan_shishen:
            shishen_count += 1
        if '伤官' in gan_shishen:
            shangguan_count += 1
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            if '食神' in cg.get('shishen', ''):
                shishen_count += 1
            if '伤官' in cg.get('shishen', ''):
                shangguan_count += 1
    
    shishang_count = shishen_count + shangguan_count
    
    print(f"\n食神数量：{shishen_count}个")
    print(f"伤官数量：{shangguan_count}个")
    print(f"食伤总数：{shishang_count}个")
    
    print(f"""
【食伤旺的影响】

食伤旺的人沟通特点：

✓ 表达欲望强
  → 想说的话很多
  → 可能同时在和多人聊天
  → 信息量大，需要时间处理

✓ 思维活跃
  → 想法多，容易分心
  → 可能看到消息在想别的
  → 不是故意不回

✓ 追求完美表达
  → 想要回复得完美
  → 可能想了很久还是不知道怎么回
  → 可能打了字又删掉

【伤官多的特别影响】
伤官{shangguan_count}个 → 
  → 不喜欢被约束
  → 可能觉得"为什么要马上回"
  → 有自己的节奏
  → 不喜欢被催促
""")
    
    # ========== 印星分析 ==========
    print(f"\n{'=' * 70}")
    print("【四、印星分析——思考深度】")
    print("=" * 70)
    
    # 统计印星
    yin_count = 0
    pianyin_count = 0
    zhengyin_count = 0
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
        gan_shishen = shishen_data.get(zhu_name, {}).get('gan_shishen', '')
        if '正印' in gan_shishen:
            zhengyin_count += 1
        if '偏印' in gan_shishen:
            pianyin_count += 1
    
    for zhu_name in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
        zhi_cang_gan = shishen_data.get(zhu_name, {}).get('zhi_cang_gan_shishen', [])
        for cg in zhi_cang_gan:
            if '正印' in cg.get('shishen', ''):
                zhengyin_count += 1
            if '偏印' in cg.get('shishen', ''):
                pianyin_count += 1
    
    yin_count = zhengyin_count + pianyin_count
    
    print(f"\n正印数量：{zhengyin_count}个")
    print(f"偏印数量：{pianyin_count}个")
    print(f"印星总数：{yin_count}个")
    
    print(f"""
【印星的影响】

印星代表思考、学习、内涵：

时支亥水藏壬水（正印）：
  → 有思想深度
  → 想得多
  → 可能看了消息在想
  → 思考后才回复

正印的特点：
  → 比较谨慎
  → 说话前会考虑
  → 不会随便回复

【印星 + 食伤组合】
食伤旺 + 有印星：
  → 想表达的很多（食伤）
  → 但又想很久（印星）
  → 结果就是回复慢
""")
    
    # ========== 五行分析 ==========
    print(f"\n{'=' * 70}")
    print("【五、五行分析——思维速度】")
    print("=" * 70)
    
    print(f"""
【五行分布】
木（日主）：旺
火（食伤）：旺
水（印星）：有
金（官杀）：缺
土（财星）：有

【关键分析】

火旺（食伤旺）：
  → 思维活跃
  → 想法多
  → 容易分心
  → 可能同时在想很多事情

水有（印星）：
  → 有思想深度
  → 会思考
  → 不是冲动型

缺金：
  → 决断力不足
  → 可能犹豫不决
  → 不知道怎么回复

【木火旺 + 缺金】
  → 想得多（木火）
  → 做得慢（缺金）
  → 看到消息 → 想 → 再想 → 然后忘了回
""")
    
    # ========== 时辰分析 ==========
    print(f"\n{'=' * 70}")
    print("【六、时辰分析——亥时】")
    print("=" * 70)
    
    print(f"""
出生时辰：亥时（21:00-23:00）
时柱：丁亥

【亥时出生的特点】

亥时（21-23点）出生的人：
  → 晚上精神好
  → 晚上是他们的活跃时间
  → 白天可能比较困
  → 作息和一般人相反

【对回消息的影响】

晚上（亥时活跃期）：
  → 晚上精神好，可能会回得快
  → 但可能在忙别的事（娱乐、社交）

白天：
  → 可能比较困
  → 反应慢
  → 可能看到了但没精力回

【作息特点】
亥时出生的人：
  → 可能睡得晚
  → 早上起得晚
  → 中午才醒
  → 下午才活跃
  → 晚上最活跃

如果你在她不活跃的时间发消息：
  → 她可能看到了
  → 但没精力回
  → 想等有空再回
  → 结果忘了
""")
    
    # ========== 具体原因分析 ==========
    print(f"\n{'=' * 70}")
    print("【七、回消息慢的具体原因】")
    print("=" * 70)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    回消息慢的命理原因                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. 【乙木日主】—— 想很多再回                                  │
│     ─────────────────────────────────────────────────────────────  │
│     乙木人：                                                      │
│     → 温和、敏感                                                 │
│     → 看到消息会想很多                                           │
│     → 不知道怎么回合适                                           │
│     → 想了想就算了                                               │
│                                                                   │
│  2. 【食伤旺（4个）】—— 想法太多                               │
│     ─────────────────────────────────────────────────────────────  │
│     食伤旺：                                                      │
│     → 表达欲望强                                                 │
│     → 想说的太多，不知道从哪说起                                 │
│     → 可能同时在想别的事                                         │
│     → 分心了                                                     │
│                                                                   │
│  3. 【伤官多（3个）】—— 不喜欢被约束                           │
│     ─────────────────────────────────────────────────────────────  │
│     伤官多：                                                      │
│     → 有自己的节奏                                               │
│     → 不喜欢被催                                                 │
│     → 想回的时候再回                                             │
│     → 可能觉得"不用马上回吧"                                    │
│                                                                   │
│  4. 【有印星】—— 想很久                                        │
│     ─────────────────────────────────────────────────────────────  │
│     有印星：                                                      │
│     → 会思考                                                     │
│     → 不是不回，是想怎么回                                       │
│     → 可能想了很久还是不知道怎么回                               │
│                                                                   │
│  5. 【缺金】—— 决断力不足                                      │
│     ─────────────────────────────────────────────────────────────  │
│     缺金：                                                        │
│     → 犹豫不决                                                   │
│     → 不知道选哪个回复                                           │
│     → 最后拖着拖着就忘了                                         │
│                                                                   │
│  6. 【亥时出生】—— 作息不同                                    │
│     ─────────────────────────────────────────────────────────────  │
│     亥时：                                                        │
│     → 晚上精神，白天困                                           │
│     → 可能在你发消息时她在睡觉                                   │
│     → 或者她在忙别的事                                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    # ========== 应对建议 ==========
    print(f"\n{'=' * 70}")
    print("【八、应对建议】")
    print("=" * 70)
    
    print(f"""
【理解她】

她回消息慢不是因为不在意，而是因为：
  ✓ 乙木人想很多
  ✓ 食伤旺，想法多，容易分心
  ✓ 有印星，会思考很久
  ✓ 缺金，决断力不足
  ✓ 亥时出生，作息不同

【建议】

1. 不要催
   ─────────────────────────────────────────────
   伤官多的人不喜欢被催
   越催越不回
   给她空间，她想回的时候会回

2. 发有趣的内容
   ─────────────────────────────────────────────
   食伤旺的人喜欢有趣的东西
   发一些好玩的内容
   她会更有回复的欲望

3. 选择合适的时间
   ─────────────────────────────────────────────
   她亥时出生，晚上精神好
   晚上发消息可能回得快
   白天可能她在睡觉或没精神

4. 理解她的思考方式
   ─────────────────────────────────────────────
   她看到消息会想很久
   可能打了又删
   最后就懒得回了
   这是她的性格，不是不在意

5. 不要太频繁发消息
   ─────────────────────────────────────────────
   食伤旺的人容易分心
   消息太多她会不知道回哪个
   简单直接可能更好

【她回复的特点】

当她回复时：
  → 可能会回很长
  → 因为食伤旺，表达欲望强
  → 一旦想好怎么说，会说得很多
  → 可能一次回好几条

【总结】

她回消息慢是性格使然，不是不在意你
  ✓ 乙木日主 → 想很多
  ✓ 食伤旺 → 想法多
  ✓ 有印星 → 思考久
  ✓ 缺金 → 犹豫
  ✓ 亥时 → 作息不同

理解她的特点，给她空间
不要催，不要急
她会在想好的时候回复你
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_reply_speed()
