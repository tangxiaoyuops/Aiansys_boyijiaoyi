# -*- coding: utf-8 -*-
"""
紫微斗数分析 - 男命
出生：1997年1月3日 早上8点
"""
import sys
import os

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

from core.tools.ziwei_calculator import create_pan, get_palace_name
from core.tools.ziwei_si_hua import apply_si_hua_to_pan, analyze_si_hua_impact

def analyze_male_ziwei():
    """分析男命紫微斗数命盘"""
    
    print("=" * 70)
    print("紫微斗数命盘分析 - 男命")
    print("出生：1997年1月3日 早上8点（辰时）")
    print("=" * 70)
    
    # 1997年1月3日 早上8点（辰时：7-9点，对应地支辰）
    year = 1997
    month = 1
    day = 3
    hour = 8  # 辰时
    gender = '男'
    
    try:
        # 创建命盘
        print("\n正在排盘...")
        pan_data = create_pan(year, month, day, hour, gender)
        
        # 应用四化
        year_gan = pan_data['birth_info']['year_gan']
        pan_data = apply_si_hua_to_pan(pan_data, year_gan)
        
        # 分析四化影响
        si_hua_analysis = analyze_si_hua_impact(pan_data)
        
        # 打印基础信息
        print("\n" + "=" * 70)
        print("【一、基础信息】")
        print("=" * 70)
        
        birth_info = pan_data.get('birth_info', {})
        print(f"\n公历：{birth_info.get('year', '')}年{birth_info.get('month', '')}月{birth_info.get('day', '')}日 {birth_info.get('hour', '')}时")
        print(f"农历：{birth_info.get('lunar_year', '')}年{birth_info.get('lunar_month', '')}月{birth_info.get('lunar_day', '')}日")
        print(f"年柱：{birth_info.get('year_gan', '')}{birth_info.get('year_zhi', '')}")
        print(f"性别：{pan_data.get('gender', '男')}")
        
        ming_gong = pan_data.get('ming_gong', 0)
        shen_gong = pan_data.get('shen_gong', 0)
        ziwei_palace = pan_data.get('ziwei_palace', 0)
        
        print(f"\n命宫位置：{get_palace_name(ming_gong)}（第{ming_gong + 1}宫）")
        print(f"身宫位置：{get_palace_name(shen_gong)}（第{shen_gong + 1}宫）")
        print(f"紫微星位置：{get_palace_name(ziwei_palace)}（第{ziwei_palace + 1}宫）")
        
        # 打印十二宫
        print("\n" + "=" * 70)
        print("【二、十二宫主星分布】")
        print("=" * 70)
        
        palaces = pan_data.get('palaces', [])
        palace_names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母']
        
        for i, palace in enumerate(palaces):
            palace_name = palace_names[i] if i < len(palace_names) else f"宫位{i}"
            main_stars = palace.get('main_stars', [])
            other_stars = palace.get('other_stars', [])
            si_hua = palace.get('si_hua', [])
            
            # 标注命宫和身宫
            markers = []
            if ming_gong == i:
                markers.append("【命宫】")
            if shen_gong == i:
                markers.append("【身宫】")
            
            marker_str = " ".join(markers)
            
            print(f"\n{palace_name}：{marker_str}")
            if main_stars:
                print(f"  主星：{', '.join(main_stars)}")
            else:
                print(f"  主星：无（借对宫主星）")
            if other_stars:
                print(f"  辅星：{', '.join(other_stars)}")
            if si_hua:
                print(f"  四化：{', '.join(si_hua)}")
        
        # 打印四化
        print("\n" + "=" * 70)
        print("【三、四化星】")
        print("=" * 70)
        
        print(f"\n年干：{year_gan}")
        if si_hua_analysis:
            print(f"\n{si_hua_analysis.get('summary', '')}")
            
            impacts = si_hua_analysis.get('impacts', [])
            if impacts:
                print("\n四化影响：")
                for impact in impacts[:10]:  # 只显示前10条
                    print(f"  - {impact}")
        
        # 重点分析
        print("\n" + "=" * 70)
        print("【四、重点宫位解读】")
        print("=" * 70)
        
        # 命宫分析
        print("\n【命宫分析】")
        ming_palace = palaces[ming_gong] if ming_gong < len(palaces) else {}
        ming_main_stars = ming_palace.get('main_stars', [])
        print(f"命宫主星：{', '.join(ming_main_stars) if ming_main_stars else '无主星（借对宫）'}")
        
        # 夫妻宫分析
        print("\n【夫妻宫分析】")
        fuqi_gong_index = 2  # 夫妻宫是第3个宫位（索引2）
        fuqi_palace = palaces[fuqi_gong_index] if fuqi_gong_index < len(palaces) else {}
        fuqi_main_stars = fuqi_palace.get('main_stars', [])
        print(f"夫妻宫主星：{', '.join(fuqi_main_stars) if fuqi_main_stars else '无主星（借对宫）'}")
        
        # 官禄宫分析
        print("\n【官禄宫分析】")
        guanlu_gong_index = 8  # 官禄宫是第9个宫位（索引8）
        guanlu_palace = palaces[guanlu_gong_index] if guanlu_gong_index < len(palaces) else {}
        guanlu_main_stars = guanlu_palace.get('main_stars', [])
        print(f"官禄宫主星：{', '.join(guanlu_main_stars) if guanlu_main_stars else '无主星（借对宫）'}")
        
        # 财帛宫分析
        print("\n【财帛宫分析】")
        caibo_gong_index = 4  # 财帛宫是第5个宫位（索引4）
        caibo_palace = palaces[caibo_gong_index] if caibo_gong_index < len(palaces) else {}
        caibo_main_stars = caibo_palace.get('main_stars', [])
        print(f"财帛宫主星：{', '.join(caibo_main_stars) if caibo_main_stars else '无主星（借对宫）'}")
        
        # 迁移宫分析
        print("\n【迁移宫分析】")
        qianyi_gong_index = 6  # 迁移宫是第7个宫位（索引6）
        qianyi_palace = palaces[qianyi_gong_index] if qianyi_gong_index < len(palaces) else {}
        qianyi_main_stars = qianyi_palace.get('main_stars', [])
        print(f"迁移宫主星：{', '.join(qianyi_main_stars) if qianyi_main_stars else '无主星（借对宫）'}")
        
        # 福德宫分析
        print("\n【福德宫分析】")
        fude_gong_index = 10  # 福德宫是第11个宫位（索引10）
        fude_palace = palaces[fude_gong_index] if fude_gong_index < len(palaces) else {}
        fude_main_stars = fude_palace.get('main_stars', [])
        print(f"福德宫主星：{', '.join(fude_main_stars) if fude_main_stars else '无主星（借对宫）'}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n排盘失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_male_ziwei()
