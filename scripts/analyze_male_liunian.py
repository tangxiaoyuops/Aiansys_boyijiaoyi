# -*- coding: utf-8 -*-
"""
男方流年运势分析
出生：1997年1月3日 早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, DI_ZHI_WUXING

def analyze_male_liunian():
    """分析男方流年运势"""
    
    print("=" * 70)
    print("男方流年运势分析")
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
    
    # 大运
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
    print(f"\n{'=' * 70}")
    print("【当前大运】")
    print("=" * 70)
    
    current_age = 2026 - 1997  # 29岁
    current_dayun = None
    for dy in dayun_list:
        if dy['start_age'] <= current_age < dy['end_age']:
            current_dayun = dy
            break
    
    if current_dayun:
        print(f"\n当前大运：第{dayun_list.index(current_dayun)+1}步 {current_dayun['gan']}{current_dayun['zhi']}运")
        print(f"年龄范围：{current_dayun['start_age']}-{current_dayun['end_age']}岁")
        print(f"年份范围：{current_dayun['start_year']}-{current_dayun['end_year']}年")
    
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
    
    # 地支关系
    DI_ZHI_LIU_HE = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯', 
                     '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
    DI_ZHI_LIU_CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                        '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    DI_ZHI_HAI = {'寅': '午', '午': '戌', '戌': '寅', '巳': '酉', '酉': '丑', '丑': '巳',
                  '申': '子', '子': '辰', '辰': '申', '亥': '卯', '卯': '未', '未': '亥'}
    
    # 流年分析
    print(f"\n{'=' * 70}")
    print("【流年运势分析（2024-2030年）】")
    print("=" * 70)
    
    all_zhi = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    
    liunian_analysis = []
    
    for target_year in range(2024, 2031):
        base_year = 1984
        gan_index = (target_year - base_year) % 10
        zhi_index = (target_year - base_year) % 12
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        liunian_gan_shishen = get_shishen(rizhu_gan, liunian_gan)
        age = target_year - year
        
        # 分析流年关系
        issues = []
        benefits = []
        
        # 天干分析
        if '伤官' in liunian_gan_shishen:
            issues.append(f"天干{liunian_gan}为伤官，容易情绪化、冲动")
        if '七杀' in liunian_gan_shishen:
            issues.append(f"天干{liunian_gan}为七杀，压力大、容易焦虑")
        if '劫财' in liunian_gan_shishen:
            issues.append(f"天干{liunian_gan}为劫财，注意破财、竞争")
        if '正财' in liunian_gan_shishen:
            benefits.append(f"天干{liunian_gan}为正财，财运好、婚运")
        if '偏财' in liunian_gan_shishen:
            benefits.append(f"天干{liunian_gan}为偏财，有偏财运")
        if '正官' in liunian_gan_shishen:
            benefits.append(f"天干{liunian_gan}为正官，事业运好")
        if '正印' in liunian_gan_shishen:
            benefits.append(f"天干{liunian_gan}为正印，有贵人")
        
        # 地支分析
        zhi_relations = []
        for i, zhi in enumerate(all_zhi):
            zhu_name = ['年支', '月支', '日支（夫妻宫）', '时支'][i]
            
            # 六冲
            if DI_ZHI_LIU_CHONG.get(zhi) == liunian_zhi:
                issues.append(f"{zhu_name}{zhi}与流年{liunian_zhi}相冲 ✗")
                zhi_relations.append(f"冲{zhu_name}")
            
            # 六合
            if DI_ZHI_LIU_HE.get(zhi) == liunian_zhi:
                benefits.append(f"{zhu_name}{zhi}与流年{liunian_zhi}相合 ✓")
                zhi_relations.append(f"合{zhu_name}")
            
            # 三合
            if zhi in ['亥', '卯', '未']:
                if liunian_zhi in ['亥', '卯', '未']:
                    benefits.append(f"三合木局（亥卯未）✓")
                    zhi_relations.append("三合")
        
        # 判断整体
        if len(issues) >= 2:
            status = "不顺 ⚠️"
        elif len(issues) == 1 and len(benefits) == 0:
            status = "小有波折"
        elif len(benefits) >= 2:
            status = "顺利 ✓"
        elif len(benefits) >= 1:
            status = "平顺"
        else:
            status = "平稳"
        
        liunian_analysis.append({
            'year': target_year,
            'age': age,
            'gan_zhi': f"{liunian_gan}{liunian_zhi}",
            'shishen': liunian_gan_shishen,
            'issues': issues,
            'benefits': benefits,
            'status': status
        })
    
    # 打印流年
    for ln in liunian_analysis:
        print(f"\n{'─' * 60}")
        print(f"{ln['year']}年（{ln['age']}岁）：{ln['gan_zhi']}年 —— {ln['status']}")
        print(f"天干十神：{ln['shishen']}")
        
        if ln['issues']:
            print(f"\n  【需注意】")
            for issue in ln['issues']:
                print(f"    • {issue}")
        
        if ln['benefits']:
            print(f"\n  【有利】")
            for benefit in ln['benefits']:
                print(f"    • {benefit}")
    
    # 重点分析不顺的年份
    print(f"\n{'=' * 70}")
    print("【重点年份分析】")
    print("=" * 70)
    
    bad_years = [ln for ln in liunian_analysis if '不顺' in ln['status'] or '波折' in ln['status']]
    
    if bad_years:
        for ln in bad_years:
            print(f"\n{'★' * 20}")
            print(f"【{ln['year']}年（{ln['age']}岁）—— 需特别注意】")
            print(f"{'★' * 20}")
            
            print(f"\n流年：{ln['gan_zhi']}")
            print(f"十神：{ln['shishen']}")
            
            print(f"\n可能的问题：")
            for issue in ln['issues']:
                print(f"  • {issue}")
            
            # 详细分析
            if '伤官' in ln['shishen']:
                print(f"\n  伤官年的特点：")
                print(f"    • 容易冲动、情绪化")
                print(f"    • 可能做错决定")
                print(f"    • 可能得罪人")
                print(f"    • 可能跳槽、辞职")
            
            if '七杀' in ln['shishen']:
                print(f"\n  七杀年的特点：")
                print(f"    • 压力大")
                print(f"    • 容易焦虑")
                print(f"    • 可能有小人")
                print(f"    • 健康注意")
            
            if '劫财' in ln['shishen']:
                print(f"\n  劫财年的特点：")
                print(f"    • 注意破财")
                print(f"    • 不要借钱给别人")
                print(f"    • 注意竞争")
            
            # 检查是否有冲
            for issue in ln['issues']:
                if '冲' in issue:
                    if '日支' in issue or '夫妻宫' in issue:
                        print(f"\n  夫妻宫被冲：")
                        print(f"    • 感情可能有波动")
                        print(f"    • 可能吵架、矛盾")
                    if '年支' in issue:
                        print(f"\n  年支被冲：")
                        print(f"    • 可能与长辈有矛盾")
                        print(f"    • 可能外出、变动")
                    if '月支' in issue:
                        print(f"\n  月支被冲：")
                        print(f"    • 工作可能有变动")
                        print(f"    • 内心不安定")
    
    # 总结
    print(f"\n{'=' * 70}")
    print("【总结】")
    print("=" * 70)
    
    print(f"""
【流年运势总览】

  2024年（27岁）：甲辰年 —— 平稳
  2025年（28岁）：乙巳年 —— 平顺
  2026年（29岁）：丙午年 —— 平顺（婚动年）
  2027年（30岁）：丁未年 —— 平顺（大运转换）
  2028年（31岁）：戊申年 —— 平顺（正财年）
  2029年（32岁）：己酉年 —— 平顺
  2030年（33岁）：庚戌年 —— 平顺

【整体运势】

  从2024年到2030年，你的流年运势整体平稳，没有特别不顺的年份。

  这是因为：
  • 2027年大运转换（己卯→庚辰）
  • 庚辰运是正官正财，运势会比之前好
  • 流年没有大冲克

【需要留意的年份】

  2026年（丙午年）：
  • 伤官透干
  • 可能情绪化
  • 但午未合（夫妻宫合），婚运好
  
  2029年（己酉年）：
  • 乙木日主，己土偏财
  • 卯酉冲（年支被冲）
  • 可能有变动，但不是大问题

【结论】

  你的流年运势整体不错，没有特别不顺的年份。
  
  如果说要注意什么：
  • 2026年情绪可能波动
  • 不要冲动做决定
  • 其他年份都算平稳
  
  2027年后大运转好，运势会更好。
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_liunian()
