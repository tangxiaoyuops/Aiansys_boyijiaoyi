"""
意图识别节点
"""
from typing import Dict, Any
from core.tools.llm_client import call_llm
from .base_node import BaseNode
import json
import re


class IntentNode(BaseNode):
    """意图识别节点"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行意图识别
        
        Args:
            input_data: 包含用户问题和历史对话的数据
        
        Returns:
            意图识别结果
        """
        user_question = input_data.get('user_question', '')
        conversation_history = input_data.get('conversation_history', [])
        
        # 构建提示词
        prompt = self._build_intent_prompt(user_question, conversation_history)
        
        # 调用LLM
        llm_response = self._call_llm(prompt)
        
        # 解析意图
        intent_result = self._parse_intent(llm_response)
        
        return {
            "intent": intent_result['intent'],
            "confidence": intent_result['confidence'],
            "reason": intent_result['reason'],
            "raw_response": llm_response
        }
    
    def _build_intent_prompt(self, user_question: str, conversation_history: list) -> str:
        """构建意图识别提示词"""
        history_text = ""
        has_deep_analysis = False
        
        if conversation_history:
            recent_history = conversation_history[-3:]  # 最近3轮对话
            history_text = "\n".join([
                f"用户: {turn.get('user', '')}\n助手: {turn.get('assistant', '')[:100]}..."
                for turn in recent_history
            ])
            # 检查是否已有深度分析
            has_deep_analysis = len(conversation_history) > 0
        
        # 如果有对话历史，倾向于认为是追问
        context_hint = ""
        if has_deep_analysis:
            context_hint = """
【重要提示】
检测到已有对话历史，用户很可能是在进行多轮追问（follow_up）。
除非用户明确要求"重新分析"或"分析XX年"，否则应该识别为follow_up意图。
"""
        
        prompt = f"""你是一个八字分析意图识别专家。请分析用户的意图。

用户问题: {user_question}

历史对话:
{history_text if history_text else '无'}
{context_hint}

请判断用户意图，从以下选项中选择最合适的一个：
1. full_analysis - 完整八字分析（用户要求全面分析）
2. career_analysis - 事业运势分析（用户询问事业、工作）
3. wealth_analysis - 财运分析（用户询问财运、投资）
4. marriage_analysis - 婚姻感情分析（用户询问感情、婚姻）
5. health_analysis - 健康分析（用户询问健康）
6. year_analysis - 流年分析（用户明确要求分析某年运势，如"分析一下2025年"）
7. follow_up - 多轮对话追问（用户基于之前分析继续提问、质疑、询问细节）
8. quick_query - 快速查询（简单问题，如"我今年运势如何"）

输出格式（JSON）:
{{
  "intent": "意图类型",
  "confidence": 0.95,
  "reason": "判断理由（简短说明为什么选择这个意图）"
}}

只输出JSON，不要其他内容。"""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        # 使用统一的LLM客户端
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是一位专业的八字分析专家。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result
    
    def _parse_intent(self, llm_response: str) -> Dict[str, Any]:
        """解析LLM返回的意图"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[^}]+\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "intent": result.get('intent', 'full_analysis'),
                    "confidence": result.get('confidence', 0.8),
                    "reason": result.get('reason', '')
                }
        except Exception as e:
            pass
        
        # 默认返回
        return {
            "intent": "full_analysis",
            "confidence": 0.6,
            "reason": "无法解析意图，使用默认分析"
        }
