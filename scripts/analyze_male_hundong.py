"""
男方婚动时间详细分析
1997年1月3日早上8点
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.agents.bazi_pan_agent import bazi_pan_node
from core.agents.bazi_dayun_agent import bazi_dayun_node
from core.tools.bazi_calculator import (
    TIAN_GAN, DI_ZHI, TIAN_GAN_WUXING, TIAN_GAN_YINYANG, 
    DI_ZHI_CANG_GAN, DI_ZHI_WUXING, WUXING_SHENG, WUXING_KE
)

def calculate_single_shishen(rizhu_gan, target_gan=None, target_zhi=None):
    """计算单个天干或地支的十神"""
    rizhu_wuxing = TIAN_GAN_WUXING.get(rizhu_gan, '')
    rizhu_yinyang = TIAN_GAN_YINYANG.get(rizhu_gan, '')
    
    if target_gan:
        target_wuxing = TIAN_GAN_WUXING.get(target_gan, '')
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
    
    if target_zhi and target_zhi in DI_ZHI_CANG_GAN:
        cang_gan = DI_ZHI_CANG_GAN[target_zhi][0]
        cang_gan_wuxing = TIAN_GAN_WUXING.get(cang_gan, '')
        cang_gan_yinyang = TIAN_GAN_YINYANG.get(cang_gan, '')
        
        if cang_gan_wuxing == rizhu_wuxing:
            return '比肩' if cang_gan_yinyang == rizhu_yinyang else '劫财'
        elif WUXING_SHENG.get(rizhu_wuxing) == cang_gan_wuxing:
            return '食神' if cang_gan_yinyang == rizhu_yinyang else '伤官'
        elif WUXING_SHENG.get(cang_gan_wuxing) == rizhu_wuxing:
            return '偏印' if cang_gan_yinyang == rizhu_yinyang else '正印'
        elif WUXING_KE.get(rizhu_wuxing) == cang_gan_wuxing:
            return '偏财' if cang_gan_yinyang == rizhu_yinyang else '正财'
        elif WUXING_KE.get(cang_gan_wuxing) == rizhu_wuxing:
            return '七杀' if cang_gan_yinyang == rizhu_yinyang else '正官'
    
    return ''


def check_liuhe(zhi1, zhi2):
    """六合"""
    liuhe = {
        '子': '丑', '丑': '子',
        '寅': '亥', '亥': '寅',
        '卯': '戌', '戌': '卯',
        '辰': '酉', '酉': '辰',
        '巳': '申', '申': '巳',
        '午': '未', '未': '午',
    }
    return liuhe.get(zhi1) == zhi2


def check_liuchong(zhi1, zhi2):
    """六冲"""
    chong = {
        '子': '午', '午': '子',
        '丑': '未', '未': '丑',
        '寅': '申', '申': '寅',
        '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰',
        '巳': '亥', '亥': '巳',
    }
    return chong.get(zhi1) == zhi2


def analyze_male_hundong():
    """分析男方婚动时间"""
    
    print("=" * 70)
    print("男方婚动时间详细分析")
    print("出生：1997年1月3日 早上8点")
    print("=" * 70)
    
    # 男方命盘
    year, month, day, hour, gender = 1997, 1, 3, 8, '男'
    
    pan_result = bazi_pan_node(year, month, day, hour, gender)
    sizhu = pan_result['sizhu']
    
    nian_zhu = sizhu['nian_zhu']
    yue_zhu = sizhu['yue_zhu']
    ri_zhu = sizhu['ri_zhu']
    shi_zhu = sizhu['shi_zhu']
    rizhu_gan = sizhu['ri_zhu_tiangan']
    
    print(f"\n【一、男方命盘】")
    print(f"年柱：{nian_zhu['tian_gan']}{nian_zhu['di_zhi']}")
    print(f"月柱：{yue_zhu['tian_gan']}{yue_zhu['di_zhi']}")
    print(f"日柱：{ri_zhu['tian_gan']}{ri_zhu['di_zhi']}（日主）")
    print(f"时柱：{shi_zhu['tian_gan']}{shi_zhu['di_zhi']}")
    print(f"日主：{rizhu_gan}木")
    
    # 日支（夫妻宫）
    ri_zhi = ri_zhu['di_zhi']
    print(f"\n日支（夫妻宫）：{ri_zhi}")
    
    # 大运
    dayun_result = bazi_dayun_node(sizhu, year, month, day, hour, gender)
    dayun_list = dayun_result.get('dayun_list', [])
    
    print(f"\n{'=' * 70}")
    print("【二、婚动的判断标准】")
    print("=" * 70)
    print("""
男命婚动的主要标志：
1. 大运见财星（妻星运）—— 10年大运
2. 流年见财星（妻星年）—— 该年有感情机会
3. 流年与日支相合（合夫妻宫）—— 婚动信号
4. 流年为桃花年 —— 感情机会
5. 流年与命局形成三合 —— 缘分到
""")
    
    # 大运分析
    print(f"\n{'=' * 70}")
    print("【三、大运分析（当前及未来）】")
    print("=" * 70)
    
    for i, dy in enumerate(dayun_list):
        dy_gan = dy['gan']
        dy_zhi = dy['zhi']
        dy_gan_shishen = calculate_single_shishen(rizhu_gan, dy_gan)
        dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, dy_zhi)
        
        is_cai_yun = '财' in dy_gan_shishen or '财' in dy_zhi_shishen
        
        marker = " ★ 财星运（婚运）" if is_cai_yun else ""
        
        print(f"\n第{i+1}步：{dy_gan}{dy_zhi}运（{dy['start_age']}-{dy['end_age']}岁，{dy['start_year']}-{dy['end_year']}年）{marker}")
        print(f"   天干{dy_gan}：{dy_gan_shishen}")
        print(f"   地支{dy_zhi}：{dy_zhi_shishen}")
        
        if is_cai_yun:
            print(f"   >>> 这是婚恋运强的大运！")
    
    # 当前大运
    current_age = 29  # 2026年
    print(f"\n{'=' * 70}")
    print(f"【四、当前状态（2026年，{current_age}岁）】")
    print("=" * 70)
    
    current_dayun = None
    for dy in dayun_list:
        if dy['start_age'] <= current_age <= dy['end_age']:
            current_dayun = dy
            break
    
    if current_dayun:
        print(f"\n当前大运：{current_dayun['gan']}{current_dayun['zhi']}运")
        print(f"年龄范围：{current_dayun['start_age']}-{current_dayun['end_age']}岁")
        print(f"年份范围：{current_dayun['start_year']}-{current_dayun['end_year']}年")
        
        dy_gan_shishen = calculate_single_shishen(rizhu_gan, current_dayun['gan'])
        dy_zhi_shishen = calculate_single_shishen(rizhu_gan, None, current_dayun['zhi'])
        
        print(f"天干{current_dayun['gan']}：{dy_gan_shishen}")
        print(f"地支{current_dayun['zhi']}：{dy_zhi_shishen}")
        
        if '财' in dy_gan_shishen or '财' in dy_zhi_shishen:
            print(f"\n★ 当前大运是财星运！")
            print(f"★ 男命财星=妻星，这正是婚运期！")
    
    # 流年分析
    print(f"\n{'=' * 70}")
    print("【五、流年婚动分析（2024-2035年）】")
    print("=" * 70)
    
    print(f"\n日支（夫妻宫）：{ri_zhi}")
    print(f"年支（属相）：{nian_zhu['di_zhi']}")
    
    print(f"\n年份分析：")
    
    for target_year in range(2024, 2036):
        age = target_year - year
        base_year = 1984
        gan_index = (target_year - base_year) % 10
        zhi_index = (target_year - base_year) % 12
        liunian_gan = TIAN_GAN[gan_index]
        liunian_zhi = DI_ZHI[zhi_index]
        
        gan_shishen = calculate_single_shishen(rizhu_gan, liunian_gan)
        zhi_shishen = calculate_single_shishen(rizhu_gan, None, liunian_zhi)
        
        # 检查婚动信号
        signals = []
        
        # 1. 财星年
        if '财' in gan_shishen:
            signals.append(f"天干{liunian_gan}为{gan_shishen}（妻星）")
        if '财' in zhi_shishen:
            signals.append(f"地支{liunian_zhi}为{zhi_shishen}（妻星）")
        
        # 2. 与日支相合
        if check_liuhe(ri_zhi, liunian_zhi):
            signals.append(f"流年{liunian_zhi}与日支{ri_zhi}相合（婚动！）")
        
        # 3. 与日支相冲
        if check_liuchong(ri_zhi, liunian_zhi):
            signals.append(f"流年{liunian_zhi}与日支{ri_zhi}相冲（注意）")
        
        # 4. 桃花年
        taohua_map = {
            '寅': '卯', '午': '卯', '戌': '卯',
            '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午',
            '亥': '子', '卯': '子', '未': '子',
        }
        if taohua_map.get(nian_zhu['di_zhi']) == liunian_zhi:
            signals.append(f"流年{liunian_zhi}为桃花年")
        
        # 5. 与命局三合
        san_he_list = [
            {'申', '子', '辰'},
            {'寅', '午', '戌'},
            {'巳', '酉', '丑'},
            {'亥', '卯', '未'},
        ]
        all_zhi = [nian_zhu['di_zhi'], yue_zhu['di_zhi'], ri_zhu['di_zhi'], shi_zhu['di_zhi']]
        for san_he in san_he_list:
            existing = set(all_zhi) & san_he
            if liunian_zhi in san_he and len(existing) >= 2:
                signals.append(f"流年{liunian_zhi}与命局形成三合")
                break
        
        # 打印结果
        if signals:
            print(f"\n【{target_year}年（{age}岁）】{liunian_gan}{liunian_zhi}年 ★ 婚动年 ★")
            for s in signals:
                print(f"   • {s}")
    
    # 重点年份分析
    print(f"\n{'=' * 70}")
    print("【六、重点婚动年份详解】")
    print("=" * 70)
    
    print("""
【2026年 丙午年（29岁）】★★★ 强婚动 ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 大运：己卯运（20-30岁）—— 己土为偏财（妻星运）
• 流年：丙午年
• 关键信号：午未相合！
  - 流年地支「午」与日支「未」相合
  - 这是合夫妻宫，是最强的婚动信号！
• 结论：2026年是婚动年，感情缘分到，适合认识、发展感情

【2027年 丁未年（30岁）】★★ 婚运强 ★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 大运：换运年，进入庚辰运
• 流年：丁未年
• 地支未土：偏财（妻星）
• 日支伏吟：流年未与日支未相同
• 结论：感情稳定发展，适合加深关系

【2028年 戊申年（31岁）】★★★ 最佳结婚年 ★★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 大运：庚辰运（30-40岁）—— 辰土为正财（妻星运）
• 流年：戊申年
• 天干戊土：正财（正妻星透出）
• 大运流年双财星：婚运极强
• 结论：这是最适合结婚的年份！

【2030年 庚戌年（33岁）】★★ 备选婚期 ★★
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 流年：庚戌年
• 地支戌土：正财（妻星）
• 结论：也是适合结婚的好年份
""")
    
    # 总结
    print(f"\n{'=' * 70}")
    print("【七、婚动时间线总结】")
    print("=" * 70)
    
    print("""
时间线：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  2024    2025    2026    2027    2028    2029    2030
    │       │       │       │       │       │       │
    │       │       ▼       │       ▼       │       │
    │       │    ★婚动★    │    ★结婚★    │       │
    │       │   午未合     换大运   正财年    │      备选
    │       │   认识发展   庚辰运   戊申年    │
    │       │              财星运             │
    ▼       ▼       ▼       ▼       ▼       ▼       ▼
 感情期   感情期  婚动期  稳定期  结婚期  感情稳  备选期

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

关键节点：

1. 2017-2027年：己卯运（偏财运）
   → 正是婚运期，财星=妻星

2. 2026年（丙午年）：午未相合
   → 合夫妻宫，最强婚动信号
   → 年初认识正是好时机！

3. 2027-2037年：庚辰运（正财运）
   → 正财=正妻，感情稳定
   → 大运财星，婚运持续

4. 2028年（戊申年）：正财透出
   → 天干戊土正财=正妻
   → 最佳结婚年份

结论：2026年初认识，时机完美！
      2028年适合结婚！
""")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    analyze_male_hundong()
