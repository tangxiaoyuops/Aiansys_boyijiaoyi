"""
对话节点
"""
from typing import Dict, Any
from .base_node import BaseNode


class DialogueNode(BaseNode):
    """对话节点"""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.node_subtype = config.get('node_subtype', 'context_understanding')
        self.prompt_file = config.get('prompt_file')
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行对话处理
        
        Args:
            input_data: 包含对话上下文的数据
        
        Returns:
            对话处理结果
        """
        # 根据子类型选择处理逻辑
        if self.node_subtype == 'context_understanding':
            return self._handle_context_understanding(input_data)
        elif self.node_subtype == 'dynamic_analysis':
            return self._handle_dynamic_analysis(input_data)
        elif self.node_subtype == 'response_generation':
            return self._handle_response_generation(input_data)
        else:
            return {
                "status": "error",
                "error": f"未知的对话节点子类型: {self.node_subtype}"
            }
    
    def _handle_context_understanding(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理上下文理解"""
        # 1. 加载提示词模板
        prompt_template = self._load_prompt_template()
        
        # 2. 构建上下文理解提示词
        conversation_history = input_data.get('conversation_history', [])
        user_question = input_data.get('user_question', '')
        bazi_context = input_data.get('bazi_context', {})
        
        prompt = self._build_context_prompt(
            prompt_template,
            conversation_history,
            user_question,
            bazi_context
        )
        
        # 3. 调用LLM
        result = self._call_llm(prompt)
        
        # 4. 解析结果
        parsed_result = self._parse_context_result(result)
        
        return {
            "context_understanding": parsed_result,
            "raw_response": result
        }
    
    def _handle_dynamic_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理动态分析"""
        # 根据上下文理解结果,选择合适的分析节点
        context = input_data.get('context_understanding_result', {})
        context_data = context.get('context_understanding', {})
        
        # 获取选择规则
        selection_rules = self.config.get('selection_rules', [])
        default_analysis = self.config.get('default', 'general_analysis')
        
        # 根据规则选择分析类型
        selected_analysis = default_analysis
        for rule in selection_rules:
            condition = rule.get('if', '')
            then_analysis = rule.get('then', default_analysis)
            
            # 简单的条件匹配(实际应该用更复杂的规则引擎)
            if self._match_condition(condition, context_data):
                selected_analysis = then_analysis
                break
        
        # TODO: 调用相应的分析节点
        # 这里简化处理,直接调用LLM生成分析
        prompt = f"根据用户上下文,进行{selected_analysis}分析。"
        result = self._call_llm(prompt)
        
        return {
            "analysis_type": selected_analysis,
            "analysis_result": result
        }
    
    def _handle_response_generation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理响应生成"""
        # 1. 加载提示词模板
        prompt_template = self._load_prompt_template()
        
        # 2. 准备数据
        context_understanding = input_data.get('context_understanding_result', {})
        analysis_results = input_data.get('dynamic_analysis_result', {})
        conversation_history = input_data.get('conversation_history', [])
        bazi_context = input_data.get('bazi_context', {})  # 获取八字上下文
        
        # 3. 构建响应生成提示词
        prompt = self._build_response_prompt(
            prompt_template,
            context_understanding,
            analysis_results,
            conversation_history,
            bazi_context  # 传递八字上下文
        )
        
        # 4. 调用LLM
        result = self._call_llm(prompt)
        
        return {
            "response": result
        }
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        if not self.prompt_file:
            return ""
        
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_path, self.prompt_file)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return ""
    
    def _build_context_prompt(
        self,
        template: str,
        conversation_history: list,
        user_question: str,
        bazi_context: dict
    ) -> str:
        """构建上下文理解提示词"""
        # 格式化历史对话
        history_text = self._format_conversation_history(conversation_history)
        
        # 格式化八字上下文 - 使用BaziDialogueAgent的方法
        context_text = self._build_bazi_context_text(bazi_context)
        
        # 替换模板变量
        prompt = template.replace('{conversation_history}', history_text)
        prompt = prompt.replace('{user_question}', user_question)
        prompt = prompt.replace('{bazi_context}', context_text)
        
        return prompt
    
    def _build_bazi_context_text(self, bazi_context: dict) -> str:
        """
        构建八字上下文文本 - 使用BaziDialogueAgent的方法
        
        Args:
            bazi_context: 包含sizhu、wuxing_analysis等数据的字典
            
        Returns:
            格式化的八字上下文文本
        """
        from core.agents.bazi_dialogue_agent import BaziContext
        
        # 🔍 调试：打印接收到的bazi_context
        print(f"[DialogueNode] ========== 构建八字上下文 ==========")
        print(f"[DialogueNode] bazi_context是否存在: {bazi_context is not None}")
        if bazi_context:
            print(f"[DialogueNode] sizhu是否存在: {bazi_context.get('sizhu') is not None}")
            print(f"[DialogueNode] wuxing_analysis是否存在: {bazi_context.get('wuxing_analysis') is not None}")
            print(f"[DialogueNode] shishen_analysis是否存在: {bazi_context.get('shishen_analysis') is not None}")
            print(f"[DialogueNode] dayun_analysis是否存在: {bazi_context.get('dayun_analysis') is not None}")
        
        # 将字典转换为BaziContext对象
        context = BaziContext(
            sizhu=bazi_context.get('sizhu', {}),
            wuxing_analysis=bazi_context.get('wuxing_analysis'),
            shishen_analysis=bazi_context.get('shishen_analysis'),
            dayun_analysis=bazi_context.get('dayun_analysis'),
            liunian_analysis=bazi_context.get('liunian_analysis'),
            shensha_analysis=bazi_context.get('shensha_analysis'),
            llm_analysis=bazi_context.get('llm_analysis'),
            analysis_style=bazi_context.get('analysis_style', 'classic'),
            gender=bazi_context.get('gender', '男'),
            birth_info=bazi_context.get('birth_info', {})
        )
        
        # 使用BaziDialogueAgent的方法构建上下文文本
        from core.agents.bazi_dialogue_agent import BaziDialogueAgent
        agent = BaziDialogueAgent()
        result = agent.build_context_text(context)
        
        print(f"[DialogueNode] 生成的上下文长度: {len(result)}")
        print(f"[DialogueNode] 上下文前100字符: {result[:100]}")
        
        return result
    
    def _build_response_prompt(
        self,
        template: str,
        context_understanding: dict,
        analysis_results: dict,
        conversation_history: list,
        bazi_context: dict = None
    ) -> str:
        """构建响应生成提示词"""
        # 格式化上下文理解
        context_text = str(context_understanding)
        
        # 格式化分析结果
        analysis_text = str(analysis_results)
        
        # 格式化历史对话
        history_text = self._format_conversation_history(conversation_history)
        
        # 格式化八字上下文(如果有)
        bazi_text = ""
        if bazi_context:
            bazi_text = self._build_bazi_context_text(bazi_context)
        
        # 替换模板变量
        prompt = template.replace('{context_understanding}', context_text)
        prompt = prompt.replace('{analysis_results}', analysis_text)
        prompt = prompt.replace('{conversation_history}', history_text)
        prompt = prompt.replace('{bazi_context}', bazi_text)
        
        return prompt
    
    def _format_conversation_history(self, conversation_history: list) -> str:
        """格式化对话历史"""
        if not conversation_history:
            return "无历史对话"
        
        parts = []
        for turn in conversation_history[-5:]:  # 最近5轮对话
            user = turn.get('user', '')
            assistant = turn.get('assistant', '')[:100]  # 限制长度
            parts.append(f"用户: {user}\n助手: {assistant}...")
        
        return "\n".join(parts)
    
    def _parse_context_result(self, result: str) -> Dict[str, Any]:
        """解析上下文理解结果"""
        import json
        import re
        
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # 返回原始内容
        return {"content": result}
    
    def _match_condition(self, condition: str, context_data: Dict) -> bool:
        """匹配条件"""
        # 简单的条件匹配实现
        # TODO: 实现更复杂的规则引擎
        if "contains" in condition:
            # 提取关键词
            import re
            match = re.search(r"contains\('(.+?)'\)", condition)
            if match:
                keyword = match.group(1)
                context_str = str(context_data)
                return keyword in context_str
        
        return False
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是一位专业的八字分析助手。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result
