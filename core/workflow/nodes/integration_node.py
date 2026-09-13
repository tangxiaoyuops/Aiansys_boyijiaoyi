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
        
        # 构建整合提示词
        prompt = self._build_integration_prompt(
            user_intent,
            wuxing_result,
            shishen_result,
            dayun_result,
            liunian_result
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
        liunian_result: Dict[str, Any]
    ) -> str:
        """构建整合提示词"""
        
        intent_focus = {
            "full_analysis": "全面分析命局",
            "career_analysis": "重点分析事业运势",
            "wealth_analysis": "重点分析财运",
            "marriage_analysis": "重点分析婚姻感情",
            "health_analysis": "重点分析健康",
            "year_analysis": "重点分析流年运势"
        }.get(user_intent, "全面分析")
        
        prompt = f"""你是八字分析报告整合专家，请将以下分析结果整合成一份完整、专业的分析报告。

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

## 整合要求
1. 按照用户需求重点突出相关内容
2. 逻辑清晰，层次分明
3. 语言通俗易懂，避免过于专业的术语
4. 给出实用、具体的建议
5. 确保各部分内容连贯，避免重复

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
