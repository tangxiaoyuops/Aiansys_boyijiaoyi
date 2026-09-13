"""
八字分析配置检索Agent
根据分析需求动态检索相关配置，减少提示词长度
"""
from typing import Dict, Any, List, Optional
from core.config.bazi_analysis_config import (
    QIJI_FLOW_ANALYSIS_RULES,
    QIJI_FLOW_CORE_PROMPT,
    SHISHEN_DETAILED_CONFIG,
    HE_CHONG_CONFIG,
    SHENSHA_CONFIG,
    WUXING_STRENGTH_CRITERIA,
    ADVANCED_ANALYSIS_EXAMPLES
)


class BaziConfigAgent:
    """八字分析配置检索Agent"""
    
    def __init__(self):
        self.config_map = {
            "qiji_flow_rules": QIJI_FLOW_ANALYSIS_RULES,
            "core_prompt": QIJI_FLOW_CORE_PROMPT,
            "shishen_config": SHISHEN_DETAILED_CONFIG,
            "he_chong_config": HE_CHONG_CONFIG,
            "shensha_config": SHENSHA_CONFIG,
            "wuxing_strength": WUXING_STRENGTH_CRITERIA,
            "examples": ADVANCED_ANALYSIS_EXAMPLES
        }
    
    def get_analysis_step_config(self, step: str) -> str:
        """
        根据分析步骤获取对应的配置
        
        Args:
            step: 分析步骤（"step1", "step2", "step3"）
        
        Returns:
            对应步骤的配置文本
        """
        rules = QIJI_FLOW_ANALYSIS_RULES
        
        if step == "step1":
            # 提取第一步：定格局底色
            start = rules.find("## 第一步：定格局底色")
            end = rules.find("## 第二步：", start)
            if start != -1 and end != -1:
                return rules[start:end].strip()
        
        elif step == "step2":
            # 提取第二步：大运定调
            start = rules.find("## 第二步：大运定调")
            end = rules.find("## 第三步：", start)
            if start != -1 and end != -1:
                return rules[start:end].strip()
        
        elif step == "step3":
            # 提取第三步：流年断事逻辑链
            start = rules.find("## 第三步：流年断事逻辑链")
            if start != -1:
                return rules[start:].strip()
        
        return ""
    
    def get_shishen_info(self, shishen_type: str, strength: str = "strong") -> Dict[str, Any]:
        """
        获取十神信息
        
        Args:
            shishen_type: 十神类型（"印星", "官杀", "财星", "食伤", "比劫"）
            strength: 日主强弱（"strong" 或 "weak"）
        
        Returns:
            十神配置信息
        """
        if shishen_type not in SHISHEN_DETAILED_CONFIG:
            return {}
        
        config = SHISHEN_DETAILED_CONFIG[shishen_type]
        
        # 根据日主强弱调整解释
        result = {
            "type": shishen_type,
            "strength": strength,
            "details": config
        }
        
        # 如果是身强格，需要调整十神含义
        if strength == "strong":
            result["usage"] = self._get_shishen_usage_for_strong(shishen_type)
        else:
            result["usage"] = self._get_shishen_usage_for_weak(shishen_type)
        
        return result
    
    def _get_shishen_usage_for_strong(self, shishen_type: str) -> str:
        """获取身强格的十神用法"""
        usage_map = {
            "印星": "印星为忌，印动=麻烦、变动、换环境、心情烦躁",
            "官杀": "官杀为用，官杀动=升职、掌权、事业有成",
            "财星": "财星为用，财星动=财运亨通、事业突破",
            "食伤": "食伤为用，食伤动=才华展示、创作表达、突破创新",
            "比劫": "比劫为忌，比劫动=竞争激烈、破财、人际冲突"
        }
        return usage_map.get(shishen_type, "")
    
    def _get_shishen_usage_for_weak(self, shishen_type: str) -> str:
        """获取身弱格的十神用法"""
        usage_map = {
            "印星": "印星为用，印动=学习、考试、贵人相助、安稳",
            "官杀": "官杀为忌，官杀动=压力、疾病、是非",
            "财星": "财星为忌，财星动=破财、父亲健康、妻子问题",
            "食伤": "食伤为忌，食伤动=表达受阻、才华难展、子女操劳",
            "比劫": "比劫为用，比劫动=朋友相助、合作顺利"
        }
        return usage_map.get(shishen_type, "")
    
    def get_he_chong_info(self, he_chong_type: str, elements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取合局冲局信息
        
        Args:
            he_chong_type: 合局冲局类型（"天干五合", "地支六合", "地支三合局", "地支三会局", "地支六冲"）
            elements: 具体元素（如 ["乙", "庚"]）
        
        Returns:
            合局冲局信息
        """
        if he_chong_type not in HE_CHONG_CONFIG:
            return {}
        
        config = HE_CHONG_CONFIG[he_chong_type]
        
        # 如果提供了具体元素，返回该元素的详细信息
        if elements:
            for key in elements:
                if key in config:
                    return {
                        "type": he_chong_type,
                        "elements": elements,
                        "detail": config[key]
                    }
        
        return {
            "type": he_chong_type,
            "all_configs": config
        }
    
    def get_shensha_info(self, shensha_name: str) -> Dict[str, Any]:
        """
        获取神煞信息
        
        Args:
            shensha_name: 神煞名称
        
        Returns:
            神煞信息
        """
        # 在吉神和凶煞中查找
        for category in ["吉神", "凶煞"]:
            if shensha_name in SHENSHA_CONFIG.get(category, {}):
                return {
                    "name": shensha_name,
                    "category": category,
                    "detail": SHENSHA_CONFIG[category][shensha_name]
                }
        
        return {}
    
    def get_case_study(self, case_type: str) -> str:
        """
        获取案例分析
        
        Args:
            case_type: 案例类型（如 "身强印旺格", "子辰合水局", "合绊盖头" 等）
        
        Returns:
            案例文本
        """
        examples = ADVANCED_ANALYSIS_EXAMPLES
        
        # 根据关键词查找案例
        keywords_map = {
            "身强印旺": "案例8：身强印旺格的实战修正",
            "子辰合水": "案例1：子辰合水局的真假辨析",
            "进气退气": "案例2：进气退气对冲克的影响",
            "三合局": "案例3：三合局的化神透干判定",
            "合绊": "案例4：合绊与贪合忘冲",
            "冲稳定器": ["案例5", "案例6", "案例7"]
        }
        
        for keyword, case_title in keywords_map.items():
            if keyword in case_type:
                if isinstance(case_title, list):
                    # 多个案例
                    cases = []
                    for title in case_title:
                        start = examples.find(title)
                        if start != -1:
                            end = examples.find("### 案例", start + 1)
                            if end == -1:
                                end = examples.find("## 关键辨析要点", start)
                            if start != -1 and end != -1:
                                cases.append(examples[start:end].strip())
                    return "\n\n".join(cases)
                else:
                    # 单个案例
                    start = examples.find(case_title)
                    if start != -1:
                        end = examples.find("### 案例", start + 1)
                        if end == -1:
                            end = examples.find("## 关键辨析要点", start)
                        if start != -1 and end != -1:
                            return examples[start:end].strip()
        
        return ""
    
    def get_core_requirements(self) -> str:
        """
        获取核心分析要求（简化版）
        
        Returns:
            核心要求文本
        """
        return QIJI_FLOW_CORE_PROMPT
    
    def get_wuxing_strength_criteria(self) -> str:
        """
        获取五行旺衰判断标准
        
        Returns:
            五行旺衰标准文本
        """
        return WUXING_STRENGTH_CRITERIA
    
    def build_dynamic_prompt(self, analysis_context: Dict[str, Any]) -> str:
        """
        根据分析上下文动态构建提示词
        
        Args:
            analysis_context: 分析上下文，包含：
                - current_step: 当前分析步骤
                - shishen_involved: 涉及的十神
                - he_chong_involved: 涉及的合局冲局
                - shensha_involved: 涉及的神煞
                - need_examples: 是否需要案例
                - day_strength: 日主强弱
        
        Returns:
            动态构建的提示词
        """
        prompt_parts = []
        
        # 1. 添加核心要求（总是需要）
        prompt_parts.append("【核心分析要求】")
        prompt_parts.append(self.get_core_requirements())
        
        # 2. 根据当前步骤添加对应配置
        current_step = analysis_context.get("current_step")
        if current_step:
            prompt_parts.append(f"\n【{current_step} 配置】")
            prompt_parts.append(self.get_analysis_step_config(current_step))
        
        # 3. 添加涉及的十神信息
        shishen_involved = analysis_context.get("shishen_involved", [])
        day_strength = analysis_context.get("day_strength", "unknown")
        
        if shishen_involved:
            prompt_parts.append("\n【涉及的十神】")
            for shishen in shishen_involved:
                info = self.get_shishen_info(shishen, day_strength)
                if info:
                    prompt_parts.append(f"\n{shishen}：")
                    prompt_parts.append(f"  用法：{info.get('usage', '')}")
        
        # 4. 添加涉及的合局冲局信息
        he_chong_involved = analysis_context.get("he_chong_involved", [])
        if he_chong_involved:
            prompt_parts.append("\n【涉及的合局冲局】")
            for item in he_chong_involved:
                he_type = item.get("type")
                elements = item.get("elements")
                info = self.get_he_chong_info(he_type, elements)
                if info and "detail" in info:
                    prompt_parts.append(f"\n{he_type} {elements}：")
                    prompt_parts.append(f"  {info['detail']}")
        
        # 5. 添加涉及的神煞信息
        shensha_involved = analysis_context.get("shensha_involved", [])
        if shensha_involved:
            prompt_parts.append("\n【涉及的神煞】")
            for shensha in shensha_involved:
                info = self.get_shensha_info(shensha)
                if info:
                    prompt_parts.append(f"\n{shensha}（{info['category']}）：")
                    detail = info.get("detail", {})
                    prompt_parts.append(f"  含义：{detail.get('含义', '')}")
                    prompt_parts.append(f"  作用：{detail.get('作用', '')}")
        
        # 6. 如果需要案例，添加相关案例
        need_examples = analysis_context.get("need_examples", False)
        case_type = analysis_context.get("case_type", "")
        
        if need_examples and case_type:
            prompt_parts.append("\n【相关案例】")
            case_text = self.get_case_study(case_type)
            if case_text:
                prompt_parts.append(case_text)
        
        return "\n".join(prompt_parts)


# 使用示例
if __name__ == "__main__":
    agent = BaziConfigAgent()
    
    # 示例1：获取第一步配置
    print("=" * 80)
    print("示例1：获取第一步配置")
    print("=" * 80)
    step1_config = agent.get_analysis_step_config("step1")
    print(step1_config[:500])  # 只显示前500字符
    
    # 示例2：获取十神信息
    print("\n" + "=" * 80)
    print("示例2：获取印星信息（身强格）")
    print("=" * 80)
    shishen_info = agent.get_shishen_info("印星", "strong")
    print(f"印星用法：{shishen_info['usage']}")
    
    # 示例3：动态构建提示词
    print("\n" + "=" * 80)
    print("示例3：动态构建提示词")
    print("=" * 80)
    context = {
        "current_step": "step1",
        "shishen_involved": ["印星", "食伤"],
        "day_strength": "strong",
        "need_examples": True,
        "case_type": "身强印旺"
    }
    dynamic_prompt = agent.build_dynamic_prompt(context)
    print(f"动态提示词长度：{len(dynamic_prompt)} 字符")
    print(f"前500字符：\n{dynamic_prompt[:500]}")
