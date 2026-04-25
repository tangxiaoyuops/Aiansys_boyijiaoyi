# -*- coding: utf-8 -*-
"""
女生2026年8月流月分析
出生：1999年3月4日 21点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING

def analyze_female_2026_august():
    """分析女生2026年8月流月"""
    
    print("=" * 70)
    print("女生2026年8月流月分析")
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
    ri_zhi = ri_zhu['di_zhi']
    
    print(f"\n【八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}")
    print(f"日支（夫妻宫）：{ri_zhi}")
    
    # 2026年流年
    print(f"\n{'=' * 70}")
    print("【一、2026年流年分析】")
    print("=" * 70)
    
    # 2026年是丙午年
    liunian_year = 2026
    base_year = 1984
    gan_index = (liunian_year - base_year) % 10
    zhi_index = (liunian_year - base_year) % 12
    liunian_gan = TIAN_GAN[gan_index]  # 丙
    liunian_zhi = DI_ZHI[zhi_index]    # 午
    
    print(f"\n2026年：{liunian_gan}{liunian_zhi}年")
    print(f"天干：{liunian_gan}（火）")
    print(f"地支：{liunian_zhi}（火）")
    
    # 计算十神
    def get_shishen(rizhu_gan, target_gan):
        rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
        target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
        
        WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '木'}
        TIAN_GAN_YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
        
        rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
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
        return ''
    
    liunian_gan_shishen = get_shishen(rizhu_gan, liunian_gan)
    print(f"流年天干{liunian_gan}对日主{rizhu_gan}：{liunian_gan_shishen}")
    
    # 流年地支关系
    print(f"\n流年地支{liunian_zhi}与命盘的关系：")
    
    # 地支关系
    DI_ZHI_LIU_HE = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯', 
                     '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
    DI_ZHI_LIU_CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                        '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    DI_ZHI_HAI = {'寅': '午', '午': '戌', '戌': '寅', '巳': '酉', '酉': '丑', '丑': '巳',
                  '申': '子', '子': '辰', '辰': '申', '亥': '卯', '卯': '未', '未': '亥'}
    
    all_zhi = [nian_zhu['di_zhi'], yue_zhu['di_zhi'], ri_zhu['di_zhi'], shi_zhu['di_zhi']]
    
    for i, zhi in enumerate(all_zhi):
        zhu_name = ['年支', '月支', '日支（夫妻宫）', '时支'][i]
        
        # 六合
        if DI_ZHI_LIU_HE.get(zhi) == liunian_zhi:
            print(f"  {zhu_name}{zhi} 与流年{liunian_zhi}相合 ✓")
        
        # 六冲
        if DI_ZHI_LIU_CHONG.get(zhi) == liunian_zhi:
            print(f"  {zhu_name}{zhi} 与流年{liunian_zhi}相冲 ✗")
        
        # 三合
        if zhi in ['寅', '午', '戌']:
            if liunian_zhi in ['寅', '午', '戌']:
                print(f"  {zhu_name}{zhi} 与流年{liunian_zhi}三合（寅午戌火局）✓")
    
    # 8月流月
    print(f"\n{'=' * 70}")
    print("【二、2026年8月流月分析】")
    print("=" * 70)
    
    # 2026年8月是丙申月
    # 公历8月对应农历七月左右
    # 2026年立秋是8月7日，所以8月主要是丙申月
    
    liuyue_gan = '丙'
    liuyue_zhi = '申'
    
    print(f"\n2026年8月（立秋后）：{liuyue_gan}{liuyue_zhi}月")
    print(f"天干：{liuyue_gan}（火）")
    print(f"地支：{liuyue_zhi}（金）")
    
    liuyue_gan_shishen = get_shishen(rizhu_gan, liuyue_gan)
    print(f"\n流月天干{liuyue_gan}对日主{rizhu_gan}：{liuyue_gan_shishen}")
    
    # 流月地支关系
    print(f"\n流月地支{liuyue_zhi}与命盘的关系：")
    
    for i, zhi in enumerate(all_zhi):
        zhu_name = ['年支', '月支', '日支（夫妻宫）', '时支'][i]
        
        # 六合
        if DI_ZHI_LIU_HE.get(zhi) == liuyue_zhi:
            print(f"  {zhu_name}{zhi} 与流月{liuyue_zhi}相合 ✓")
        
        # 六冲
        if DI_ZHI_LIU_CHONG.get(zhi) == liuyue_zhi:
            print(f"  {zhu_name}{zhi} 与流月{liuyue_zhi}相冲 ✗ ✗ ✗")
        
        # 巳申合
        if zhi == '巳' and liuyue_zhi == '申':
            print(f"  {zhu_name}{zhi} 与流月{liuyue_zhi}相合（巳申合）✓")
    
    # 分析8月的问题
    print(f"\n{'=' * 70}")
    print("【三、2026年8月的问题分析】")
    print("=" * 70)
    
    print(f"""
【流月情况】

丙申月（2026年8月）：

天干丙火 = 伤官
地支申金 = 正官（夫星）藏于其中

【关键点】

1. 巳申关系
   ─────────────────────────────────────────────
   女方日支（夫妻宫）：巳
   流月地支：申
   
   巳申的关系：
   • 巳申合（六合）→ 表面看是合
   • 但巳中丙火，申中庚金，火克金
   • 这叫"合中带克"
   
   含义：
   • 感情上有合的机会
   • 但内部有矛盾
   • 表面和谐，实际有摩擦

2. 伤官透干
   ─────────────────────────────────────────────
   流月天干丙火 = 伤官
   
   伤官对女命的影响：
   • 伤官克官（夫星）
   • 伤官旺时，容易对感情不满
   • 可能挑剔、抱怨
   • 情绪波动大
   
   伤官月的问题：
   • 容易和另一半吵架
   • 容易对感情产生质疑
   • 情绪不稳定

3. 夫星出现但被克
   ─────────────────────────────────────────────
   申金藏庚金（正官、夫星）
   
   但是：
   • 流月天干丙火（伤官）克申金
   • 巳火也克申金
   • 夫星出现，但被伤官克
   
   含义：
   • 有感情机会
   • 但容易被破坏
   • 可能是自己作没的
   • 或者情绪导致问题

【可能的状况】

1. 感情上
   ─────────────────────────────────────────────
   • 和对象发生争执
   • 对感情产生怀疑
   • 觉得不合适
   • 情绪化做决定
   • 可能说伤人的话

2. 情绪上
   ─────────────────────────────────────────────
   • 情绪波动大
   • 容易烦躁
   • 容易抱怨
   • 看什么都不顺眼

3. 行为上
   ─────────────────────────────────────────────
   • 可能出去玩得更多
   • 可能冷暴力
   • 可能说分手（但未必是真心的）
   • 可能冲动做决定
""")
    
    # 对男方的影响
    print(f"\n{'=' * 70}")
    print("【四、对你（男方）的影响】")
    print("=" * 70)
    
    print(f"""
如果你们还在接触中，2026年8月可能是：

【风险】

1. 她可能突然冷淡
   ─────────────────────────────────────────────
   • 伤官月，情绪不稳定
   • 可能突然觉得"不想聊了"
   • 或者突然觉得"你不适合"
   • 但这可能是情绪化的

2. 可能发生争执
   ─────────────────────────────────────────────
   • 她的伤官被激发
   • 可能对你挑剔
   • 可能说伤人的话
   • 你需要忍耐

3. 可能冲动做决定
   ─────────────────────────────────────────────
   • 伤官月容易冲动
   • 可能突然说"不合适"
   • 但过了这个月可能又后悔

【应对建议】

如果8月出现问题：

1. 不要太当真
   ─────────────────────────────────────────────
   • 伤官月的情绪是暂时的
   • 她说的话，可能不是真心
   • 不要被她的情绪带跑

2. 不要和她吵
   ─────────────────────────────────────────────
   • 伤官月的人，越吵越上头
   • 你越解释，她越烦
   • 让她发泄，不要对抗

3. 给她空间
   ─────────────────────────────────────────────
   • 伤官月需要发泄
   • 让她自己调整
   • 过了这个月会好

4. 不要做重大决定
   ─────────────────────────────────────────────
   • 8月不适合确定关系
   • 也不适合说分手
   • 等过了这个月再说

【时间线】

2026年8月（丙申月）：可能波动
2026年9月（丁酉月）：会好转
2026年10月（戊戌月）：稳定

如果8月有波动，不要急着下结论，
等过了这个月再看。
""")
    
    print(f"\n{'=' * 70}")
    print("【五、总结】")
    print("=" * 70)
    
    print(f"""
【2026年8月的情况】

  流月：丙申月
  
  天干丙火 = 伤官（克夫星）
  地支申金 = 藏庚金（夫星）
  
  问题：
  • 伤官透干，克夫星
  • 情绪不稳定
  • 容易对感情产生质疑
  • 可能冲动做决定

【是不是感情动荡？】

  是的，有可能。
  
  但不一定是坏事：
  • 可能是小矛盾
  • 可能是情绪波动
  • 可能过了就好
  
  关键是：
  • 不要被她的情绪带跑
  • 不要在8月做重大决定
  • 给她空间和时间

【最终建议】

  如果8月有问题，等9月再看。
  伤官月的波动，很多时候是暂时的。
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_female_2026_august()
