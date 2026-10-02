"""
结果整合节点
"""
from typing import Dict, Any, List
from .base_node import BaseNode


class IntegrationNode(BaseNode):
    """结果整合节点"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行结果整合
        
        Args:
            input_data: 包含各节点分析结果的数据
        
        Returns:
            整合后的分析报告
        """
        user_intent = input_data.get('intent', 'full_analysis')
        wuxing_result = input_data.get('wuxing_result', {})
        shishen_result = input_data.get('shishen_result', {})
        dayun_result = input_data.get('dayun_result', {})
        liunian_result = input_data.get('liunian_result', {})
        # 修复：获取命盘与性别（此前未传递导致性别乱用、命盘缺失）
        sizhu = input_data.get('sizhu', {})
        gender = input_data.get('gender', '男')
        birth_info = input_data.get('birth_info', {})
        user_question = input_data.get('user_question', '')
        conversation_history = input_data.get('conversation_history', [])
        llm_analysis = input_data.get('llm_analysis')

        # 构建整合提示词
        prompt = self._build_integration_prompt(
            user_intent,
            wuxing_result,
            shishen_result,
            dayun_result,
            liunian_result,
            sizhu=sizhu,
            gender=gender,
            birth_info=birth_info,
            user_question=user_question,
            conversation_history=conversation_history,
            llm_analysis=llm_analysis
        )
        
        # 调用LLM整合
        integrated_result = self._call_llm(prompt)
        
        return {
            "report": integrated_result,
            "user_intent": user_intent
        }
    
    def _build_integration_prompt(
        self,
        user_intent: str,
        wuxing_result: Dict[str, Any],
        shishen_result: Dict[str, Any],
        dayun_result: Dict[str, Any],
        liunian_result: Dict[str, Any],
        sizhu: Dict[str, Any] = None,
        gender: str = '男',
        birth_info: Dict[str, Any] = None,
        user_question: str = '',
        conversation_history: list = None,
        llm_analysis: str = None
    ) -> str:
        """构建整合提示词"""
        sizhu = sizhu or {}
        birth_info = birth_info or {}
        conversation_history = conversation_history or []

        # 格式化命盘
        zhu_names = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        sizhu_lines = []
        for key, name in zhu_names.items():
            zhu = sizhu.get(key, {})
            if zhu:
                gan = zhu.get('tian_gan', '?')
                zhi = zhu.get('di_zhi', '?')
                cang = zhu.get('cang_gan', [])
                cang_str = f"（藏干:{'、'.join(cang)}）" if cang else ""
                sizhu_lines.append(f"{name}: {gan}{zhi}{cang_str}")
        if not sizhu_lines:
            sizhu_text = "（无命盘数据）"
        else:
            ri_gan = sizhu.get('ri_zhu_tiangan', '')
            if ri_gan:
                sizhu_lines.append(f"日主: {ri_gan}")
            sizhu_text = "\n".join(sizhu_lines)

        # 格式化历史（最近5轮）
        history_lines = []
        for i, msg in enumerate(conversation_history[-5:], 1):
            role = "用户" if msg.get('role') == 'user' else "命理师"
            content = msg.get('content', '')[:150]
            history_lines.append(f"第{i}轮 {role}: {content}")
        history_text = "\n".join(history_lines) if history_lines else "（无历史对话，这是首次分析）"

        intent_focus = {
            "full_analysis": "全面分析命局",
            "career_analysis": "重点分析事业运势",
            "wealth_analysis": "重点分析财运",
            "marriage_analysis": "重点分析婚姻感情",
            "health_analysis": "重点分析健康",
            "year_analysis": "重点分析流年运势"
        }.get(user_intent, "全面分析")

        prompt = f"""你是八字分析报告整合专家，请将以下分析结果整合成一份完整、专业的分析报告。

## 用户命盘（必须以此为准，严禁篡改）
{sizhu_text}

## 命主性别（所有配偶星/婚姻断语必须以此性别为准）
{gender}

## 出生信息
{str(birth_info) if birth_info else '（未提供）'}

## 用户当前问题
{user_question if user_question else '（未提供）'}

## 对话历史（多轮追问须承接上一轮）
{history_text}

## 用户需求
{intent_focus}

## 五行分析结果
{wuxing_result.get('analysis_result', {}).get('content', '无')}

## 十神分析结果
{shishen_result.get('analysis_result', {}).get('content', '无')}

## 大运分析结果
{dayun_result.get('analysis_result', {}).get('content', '无')}

## 流年分析结果
{liunian_result.get('analysis_result', {}).get('content', '无')}

{'## 此前AI深度分析摘要\n' + llm_analysis if llm_analysis else ''}

## 整合要求
1. 按照用户需求重点突出相关内容
2. 逻辑清晰，层次分明
3. 语言通俗易懂，避免过于专业的术语
4. 给出实用、具体的建议
5. 确保各部分内容连贯，避免重复

【⚠️ 铁律——必须严格遵守】
1. 命主性别为【{gender}】：男命以财星为妻星、以官杀为事业；女命以官杀为夫星、以食伤为子女。严禁按相反性别分析。
2. 必须严格基于上方【用户命盘】作答，严禁编造、替换任何干支、日主、五行、十神。数据缺失则明确说明，绝不虚构。
3. 若存在【对话历史】，本次是后续追问：先承接上一轮已给出的结论，再针对当前问题深入，不要重复整套分析框架。
4. 若用户此前纠正过你（如流年应事与判断不符），必须承认偏差并重新校准推导，给出修正后的答案。

## 输出格式
# 八字分析报告

## 一、命局概览
[综合五行、十神分析，给出命局总体特征]

## 二、运势分析
[大运、流年走势分析]

## 三、专项分析
[根据用户意图展开详细分析]

## 四、综合建议
[实用性建议，分点列出]

请直接输出报告内容，不要包含其他说明。"""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是专业的八字分析报告撰写专家。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result
