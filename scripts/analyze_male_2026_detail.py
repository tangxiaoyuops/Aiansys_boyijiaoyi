# -*- coding: utf-8 -*-
"""
男方2026年详细分析
出生：1997年1月3日 早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING, DI_ZHI_CANG_GAN

def analyze_2026_detail():
    """详细分析2026年"""
    
    print("=" * 70)
    print("男方2026年详细分析")
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
    ri_zhi = ri_zhu['di_zhi']
    nian_zhi = nian_zhu['di_zhi']
    yue_zhi = yue_zhu['di_zhi']
    shi_zhi = shi_zhu['di_zhi']
    
    print(f"\n【八字命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}")
    print(f"日支（夫妻宫）：{ri_zhi}")
    print(f"年支：{nian_zhi}")
    print(f"月支：{yue_zhi}")
    print(f"时支：{shi_zhi}")
    
    # 大运
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
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
    
    # 当前大运
    current_dayun = None
    for dy in dayun_list:
        if dy['start_year'] <= 2026 < dy['end_year']:
            current_dayun = dy
            break
    
    print(f"\n{'=' * 70}")
    print("【当前大运】")
    print("=" * 70)
    
    if current_dayun:
        dy_gan = current_dayun['gan']
        dy_zhi = current_dayun['zhi']
        dy_shishen = get_shishen(rizhu_gan, dy_gan)
        print(f"\n大运：{dy_gan}{dy_zhi}运（{current_dayun['start_year']}-{current_dayun['end_year']}年）")
        print(f"大运天干：{dy_gan}（{dy_shishen}）")
        print(f"大运地支：{dy_zhi}")
        print(f"年龄：{2026 - 1997}岁")
        print(f"大运尾端！2027年转入庚辰运")
    
    # 2026年流年
    print(f"\n{'=' * 70}")
    print("【2026年流年分析】")
    print("=" * 70)
    
    liunian_gan = '丙'
    liunian_zhi = '午'
    
    print(f"\n2026年：{liunian_gan}{liunian_zhi}年")
    print(f"天干：{liunian_gan}（火）")
    print(f"地支：{liunian_zhi}（火）")
    
    liunian_shishen = get_shishen(rizhu_gan, liunian_gan)
    print(f"流年天干十神：{liunian_shishen}")
    
    # 地支关系
    print(f"\n【流年地支与命盘的关系】")
    
    DI_ZHI_LIU_HE = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯', 
                     '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
    DI_ZHI_LIU_CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                        '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    
    all_zhi = [('年支', nian_zhi), ('月支', yue_zhi), ('日支（夫妻宫）', ri_zhi), ('时支', shi_zhi)]
    
    he_count = 0
    chong_count = 0
    
    for zhu_name, zhi in all_zhi:
        # 六冲
        if DI_ZHI_LIU_CHONG.get(zhi) == liunian_zhi:
            print(f"  {zhu_name}{zhi} 与流年{liunian_zhi}相冲 ✗ ✗ ✗")
            chong_count += 1
        
        # 六合
        if DI_ZHI_LIU_HE.get(zhi) == liunian_zhi:
            print(f"  {zhu_name}{zhi} 与流年{liunian_zhi}相合 ✓ ✓ ✓")
            he_count += 1
    
    # 三合
    print(f"\n【三合检查】")
    print(f"  命盘地支：子、丑、未、辰")
    print(f"  流年地支：午")
    
    # 亥卯未三合木局 - 命盘有未
    print(f"\n  亥卯未三合木局：")
    print(f"  • 命盘有未（日支）")
    print(f"  • 流年午不是亥或卯")
    print(f"  → 不成三合")
    
    # 寅午戌三合火局
    print(f"\n  寅午戌三合火局：")
    print(f"  • 流年是午")
    print(f"  • 命盘没有寅、戌")
    print(f"  → 不成三合")
    
    # 关键分析
    print(f"\n{'=' * 70}")
    print("【2026年关键问题分析】")
    print("=" * 70)
    
    print(f"""
【一、子午冲（年支被冲）】

  年支：子（水）
  流年：午（火）
  
  子午相冲！
  
  年支代表：
  • 祖辈、长辈
  • 出身地、老家
  • 早年运
  
  子午冲的影响：
  ─────────────────────────────────────────────
  • 与长辈可能有矛盾
  • 可能外出、离家
  • 可能变动大
  • 内心不安定

【二、午未合（夫妻宫合）】

  日支（夫妻宫）：未
  流年：午
  
  午未相合！
  
  夫妻宫被合：
  ─────────────────────────────────────────────
  • 婚动信号
  • 感情有进展
  • 可能确定关系
  • 感情上有好事

【三、伤官透干】

  流年天干丙火 = 伤官
  
  伤官年的特点：
  ─────────────────────────────────────────────
  • 容易情绪化
  • 容易冲动
  • 可能做错决定
  • 可能得罪人
  • 不想被管

【四、大运尾端】

  2026年是己卯运最后一年
  2027年转入庚辰运
  
  大运尾端的影响：
  ─────────────────────────────────────────────
  • 变动多
  • 可能在等待
  • 心态上不稳定

【综合判断】
""")
    
    # 综合评分
    print(f"\n{'=' * 70}")
    print("【2026年综合评分】")
    print("=" * 70)
    
    print(f"""
【好的方面】

  1. 午未合（夫妻宫合）★★★★★
     • 婚动年
     • 感情上有机会
     • 这是今年最大的吉星

  2. 大运转好
     • 2027年庚辰运（正官正财）
     • 运势会更好
     • 今年是转折点

【不好的方面】

  1. 子午冲（年支被冲）★★☆☆☆
     • 与长辈可能有矛盾
     • 可能外出变动
     • 但影响不算很大

  2. 伤官透干 ★★★☆☆
     • 容易情绪化
     • 容易冲动
     • 需要稳住自己

  3. 大运尾端 ★★☆☆☆
     • 变动期
     • 心态不稳定

【整体评分】

  事业：★★★☆☆（变动期，但不是坏事）
  感情：★★★★★（婚动年，机会很好）
  财运：★★★☆☆（平稳）
  人际：★★★☆☆（注意情绪）

【2026年不是"不顺"】

  虽然有子午冲 + 伤官，但：
  
  • 午未合（夫妻宫合）是大利好
  • 大运转好
  • 整体是转折年，不是坏年
  
  需要注意：
  • 稳住情绪
  • 不要冲动做决定
  • 感情上抓住机会
""")
    
    # 流月分析
    print(f"\n{'=' * 70}")
    print("【2026年流月分析】")
    print("=" * 70)
    
    liuyue_list = [
        ('庚寅', '正月'), ('辛卯', '二月'), ('壬辰', '三月'), 
        ('癸巳', '四月'), ('甲午', '五月'), ('乙未', '六月'),
        ('丙申', '七月'), ('丁酉', '八月'), ('戊戌', '九月'),
        ('己亥', '十月'), ('庚子', '十一月'), ('辛丑', '十二月')
    ]
    
    print(f"\n2026年各月份特点：")
    
    for i, (gan_zhi, month_name) in enumerate(liuyue_list):
        liuyue_gan = gan_zhi[0]
        liuyue_zhi = gan_zhi[1]
        liuyue_shishen = get_shishen(rizhu_gan, liuyue_gan)
        
        issues = []
        benefits = []
        
        # 地支关系
        if liuyue_zhi == '午':
            benefits.append("午月，与日支未相合（婚动）")
        if liuyue_zhi == '子':
            issues.append("子月，与流年午相冲")
        if liuyue_zhi == '丑':
            benefits.append("丑月，与流年午相害（小问题）")
        
        # 天干关系
        if liuyue_shishen == '伤官':
            issues.append(f"天干{liuyue_gan}伤官（情绪化）")
        if liuyue_shishen == '正财':
            benefits.append(f"天干{liuyue_gan}正财（财运）")
        if liuyue_shishen == '七杀':
            issues.append(f"天干{liuyue_gan}七杀（压力）")
        if liuyue_shishen == '正官':
            benefits.append(f"天干{liuyue_gan}正官（事业）")
        
        if issues and not benefits:
            status = "注意 ⚠️"
        elif benefits and not issues:
            status = "顺利 ✓"
        elif issues and benefits:
            status = "好坏参半"
        else:
            status = "平稳"
        
        print(f"\n  {month_name}（{gan_zhi}月）：{liuyue_shishen} —— {status}")
        for issue in issues:
            print(f"    ⚠️ {issue}")
        for benefit in benefits:
            print(f"    ✓ {benefit}")
    
    # 总结
    print(f"\n{'=' * 70}")
    print("【总结】")
    print("=" * 70)
    
    print(f"""
【2026年运势总结】

  整体：转折年，不是坏年

【关键点】

  1. 子午冲（年支被冲）
     • 与长辈可能有矛盾
     • 可能外出变动
     • 影响中等

  2. 午未合（夫妻宫合）★★★★★
     • 婚动年
     • 感情上有机会
     • 这是今年的亮点

  3. 伤官透干
     • 容易情绪化
     • 稳住自己就好

  4. 大运尾端
     • 2027年转入庚辰运
     • 运势会更好

【2026年建议】

  • 感情：抓住机会，今年是婚动年
  • 事业：稳住，等大运转好
  • 情绪：不要冲动做决定
  • 人际：注意说话，不要得罪人
  • 财运：平稳，不要冲动投资

【最重要】

  虽然有冲，但午未合（夫妻宫合）是大吉。
  感情上今年有机会，不要错过。
  其他方面稳住就好。
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_2026_detail()
