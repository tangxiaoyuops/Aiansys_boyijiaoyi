"""
八字分析逻辑Agent
智能识别分析场景，动态调用配置
"""
from typing import Dict, Any, List, Optional
from core.agents.bazi_config_agent import BaziConfigAgent


class BaziAnalysisAgent:
    """八字分析逻辑Agent"""
    
    def __init__(self):
        self.config_agent = BaziConfigAgent()
    
    def analyze_situation(self, sizhu: Dict, wuxing: Dict, shishen: Dict, dayun: Dict, liunian: Dict) -> Dict[str, Any]:
        """
        分析命局情况，识别关键信息
        
        Args:
            sizhu: 四柱数据
            wuxing: 五行分析
            shishen: 十神分析
            dayun: 大运数据
            liunian: 流年数据
        
        Returns:
            分析上下文
        """
        context = {
            "current_step": None,
            "shishen_involved": [],
            "he_chong_involved": [],
            "shensha_involved": [],
            "need_examples": False,
            "case_type": "",
            "day_strength": "unknown"
        }
        
        # 1. 判断日主强弱
        context["day_strength"] = self._determine_day_strength(sizhu, wuxing, dayun)
        
        # 2. 识别涉及的十神
        context["shishen_involved"] = self._identify_shishen_involved(shishen, liunian)
        
        # 3. 识别合局冲局
        context["he_chong_involved"] = self._identify_he_chong(sizhu, dayun, liunian)
        
        # 4. 识别神煞
        context["shensha_involved"] = self._identify_shensha(sizhu)
        
        # 5. 判断是否需要案例
        context["need_examples"], context["case_type"] = self._determine_case_need(
            context["day_strength"],
            context["he_chong_involved"]
        )
        
        return context
    
    def _determine_day_strength(self, sizhu: Dict, wuxing: Dict, dayun: Dict) -> str:
        """
        判断日主强弱
        
        Returns:
            "strong" 或 "weak"
        """
        # 获取日主信息
        ri_gan = sizhu.get('ri_zhu', {}).get('tian_gan', '')
        ri_zhi = sizhu.get('ri_zhu', {}).get('di_zhi', '')
        
        # 获取月令
        yue_zhi = sizhu.get('yue_zhu', {}).get('di_zhi', '')
        
        # 获取五行数据
        wuxing_data = wuxing.get('wuxing_data', {})
        wuxing_count = wuxing_data.get('wuxing_count', {})
        
        # 判断根气
        has_root = False
        root_strength = 0
        
        # 检查地支是否有根
        di_zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        ri_zhi_index = di_zhi_list.index(ri_zhi) if ri_zhi in di_zhi_list else -1
        
        # 简化判断：如果有强根（禄、刃、长生、帝旺），则身强
        # 这里需要更详细的逻辑，暂时简化
        if ri_zhi in ['寅', '卯', '巳', '午', '申', '酉', '亥', '子']:
            has_root = True
            root_strength = 1
        
        # 检查天干生扶
        tian_gan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        ri_gan_index = tian_gan_list.index(ri_gan) if ri_gan in tian_gan_list else -1
        
        # 检查其他天干是否有生扶
        has_support = False
        for zhu in ['nian_zhu', 'yue_zhu', 'shi_zhu']:
            gan = sizhu.get(zhu, {}).get('tian_gan', '')
            if gan:
                # 检查是否生扶日主
                # 这里需要更详细的逻辑
                pass
        
        # 检查大运
        current_dayun = dayun.get('current_dayun', {})
        dayun_gan = current_dayun.get('gan', '')
        dayun_zhi = current_dayun.get('zhi', '')
        
        # 简化判断：如果有强根 + 大运印比，则身强
        if has_root and root_strength >= 1:
            return "strong"
        
        return "weak"
    
    def _identify_shishen_involved(self, shishen: Dict, liunian: Dict) -> List[str]:
        """
        识别涉及的十神
        
        Returns:
            十神列表
        """
        shishen_list = []
        
        # 检查流年引动的十神
        liunian_gan = liunian.get('gan', '')
        liunian_zhi = liunian.get('zhi', '')
        
        # 检查流年天干对应的十神
        for zhu_name, shishen_info in shishen.get('shishen_data', {}).items():
            gan_shishen = shishen_info.get('gan_shishen', '')
            if gan_shishen and gan_shishen not in shishen_list:
                # 简化：只添加主要十神
                for main_shishen in ['印星', '官杀', '财星', '食伤', '比劫']:
                    if main_shishen in gan_shishen and main_shishen not in shishen_list:
                        shishen_list.append(main_shishen)
        
        return shishen_list
    
    def _identify_he_chong(self, sizhu: Dict, dayun: Dict, liunian: Dict) -> List[Dict]:
        """
        识别合局冲局
        
        Returns:
            合局冲局列表
        """
        he_chong_list = []
        
        # 获取地支
        di_zhi_list = []
        for zhu in ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu']:
            zhi = sizhu.get(zhu, {}).get('di_zhi', '')
            if zhi:
                di_zhi_list.append(zhi)
        
        # 检查六合
        liu_he_pairs = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]
        
        for pair in liu_he_pairs:
            if pair[0] in di_zhi_list and pair[1] in di_zhi_list:
                he_chong_list.append({
                    "type": "地支六合",
                    "elements": [pair[0], pair[1]]
                })
        
        # 检查六冲
        liu_chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        
        # 检查流年地支是否与原局地支相冲
        liunian_zhi = liunian.get('zhi', '')
        if liunian_zhi:
            for zhi in di_zhi_list:
                for pair in liu_chong_pairs:
                    if liunian_zhi in pair and zhi in pair:
                        he_chong_list.append({
                            "type": "地支六冲",
                            "elements": [liunian_zhi, zhi]
                        })
        
        # 检查三合局
        san_he_groups = [
            ('申', '子', '辰'),
            ('寅', '午', '戌'),
            ('巳', '酉', '丑'),
            ('亥', '卯', '未')
        ]
        
        for group in san_he_groups:
            count = sum(1 for zhi in group if zhi in di_zhi_list)
            if count >= 2:
                he_chong_list.append({
                    "type": "地支三合局",
                    "elements": [zhi for zhi in group if zhi in di_zhi_list]
                })
        
        return he_chong_list
    
    def _identify_shensha(self, sizhu: Dict) -> List[str]:
        """
        识别神煞
        
        Returns:
            神煞列表
        """
        # 这里简化处理，实际需要计算神煞
        return []
    
    def _determine_case_need(self, day_strength: str, he_chong_involved: List[Dict]) -> tuple:
        """
        判断是否需要案例
        
        Returns:
            (是否需要, 案例类型)
        """
        # 如果是身强印旺格，需要案例
        if day_strength == "strong":
            for item in he_chong_involved:
                if item.get("type") == "地支三合局":
                    return True, "身强印旺"
        
        # 如果有合局冲局，提供相应案例
        for item in he_chong_involved:
            if "子" in str(item.get("elements", [])) and "辰" in str(item.get("elements", [])):
                return True, "子辰合水"
            
            if item.get("type") == "地支六合":
                return True, "合绊"
        
        return False, ""
    
    def get_step_guidance(self, step: int, context: Dict[str, Any]) -> str:
        """
        获取指定步骤的指导
        
        Args:
            step: 步骤编号（1, 2, 3）
            context: 分析上下文
        
        Returns:
            步骤指导文本
        """
        context["current_step"] = f"step{step}"
        return self.config_agent.build_dynamic_prompt(context)
    
    def get_quick_reference(self, topic: str) -> str:
        """
        获取快速参考信息
        
        Args:
            topic: 主题（如 "身强格十神", "合局判断", "微象判断" 等）
        
        Returns:
            快速参考文本
        """
        if "身强" in topic and "十神" in topic:
            return self._get_strong_shishen_reference()
        elif "身弱" in topic and "十神" in topic:
            return self._get_weak_shishen_reference()
        elif "合局" in topic or "冲局" in topic:
            return self._get_he_chong_reference()
        elif "微象" in topic:
            return self._get_weixiang_reference()
        else:
            return ""
    
    def _get_strong_shishen_reference(self) -> str:
        """获取身强格十神快速参考"""
        return """
【身强格十神快速参考】

印星为忌：麻烦、变动、换环境、心情烦躁
官杀为用：升职、掌权、事业有成
财星为用：财运亨通、事业突破
食伤为用：才华展示、创作表达、突破创新
比劫为忌：竞争激烈、破财、人际冲突
"""
    
    def _get_weak_shishen_reference(self) -> str:
        """获取身弱格十神快速参考"""
        return """
【身弱格十神快速参考】

印星为用：学习、考试、贵人相助、安稳
官杀为忌：压力、疾病、是非
财星为忌：破财、父亲健康、妻子问题
食伤为忌：表达受阻、才华难展、子女操劳
比劫为用：朋友相助、合作顺利
"""
    
    def _get_he_chong_reference(self) -> str:
        """获取合局冲局快速参考"""
        return """
【合局冲局快速参考】

先看合，后看冲：
- 流年地支若与原局有"合局"，不论冲，论"合绊"
- 合绊主"停滞、拖延、原地踏步、想动动不了"

天干压制（盖头）：
- 若流年天干被大运天干克制，这叫"盖头"
- 地支即使有冲，也被天干的压制力抵消
- 表象："想动动不了，最后没变化"

双重压制：
- 合绊+盖头=双重压制=完全停滞
"""
    
    def _get_weixiang_reference(self) -> str:
        """获取微象判断快速参考"""
        return """
【微象判断快速参考】

日主强旺：冲则动，必主大变动（搬家、换工作、破大财）
日主衰弱：冲则震，主念头、小摩擦、局部调整（想搬家未果、换宿舍）

财星（土）受冲：环境与物质层面变动
印星（水）受冲：心态与契约层面变动
官杀（金）受冲：职位与权威层面变动
食伤（木）受冲：表达与子女层面变动
比劫（火）受冲：竞争与合作层面变动
"""


# 使用示例
if __name__ == "__main__":
    agent = BaziAnalysisAgent()
    
    # 示例：分析一个命局
    print("=" * 80)
    print("八字分析Agent示例")
    print("=" * 80)
    
    # 模拟数据
    sizhu = {
        'ri_zhu': {'tian_gan': '乙', 'di_zhi': '卯'},
        'yue_zhu': {'tian_gan': '丁', 'di_zhi': '亥'},
        'nian_zhu': {'tian_gan': '乙', 'di_zhi': '亥'},
        'shi_zhu': {'tian_gan': '己', 'di_zhi': '卯'}
    }
    
    wuxing = {
        'wuxing_data': {
            'wuxing_count': {'金': 0, '木': 4, '水': 2, '火': 1, '土': 1}
        }
    }
    
    shishen = {
        'shishen_data': {
            'ri_zhu': {'gan_shishen': '比肩'}
        }
    }
    
    dayun = {
        'current_dayun': {'gan': '癸', 'zhi': '卯'}
    }
    
    liunian = {
        'gan': '庚',
        'zhi': '子'
    }
    
    # 分析情况
    context = agent.analyze_situation(sizhu, wuxing, shishen, dayun, liunian)
    
    print(f"日主强弱：{context['day_strength']}")
    print(f"涉及的十神：{context['shishen_involved']}")
    print(f"合局冲局：{context['he_chong_involved']}")
    print(f"是否需要案例：{context['need_examples']}")
    print(f"案例类型：{context['case_type']}")
    
    # 获取第一步指导
    print("\n" + "=" * 80)
    print("获取第一步指导（前500字符）")
    print("=" * 80)
    guidance = agent.get_step_guidance(1, context)
    print(guidance[:500])
