"""
分析节点基类
"""
from typing import Dict, Any
from .base_node import BaseNode
from core.agents.bazi_config_agent import BaziConfigAgent
import os


class AnalysisNode(BaseNode):
    """分析节点基类"""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.prompt_file = config.get('prompt_file')
        self.config_agent = BaziConfigAgent()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行分析
        
        Args:
            input_data: 分析输入数据
        
        Returns:
            分析结果
        """
        # 1. 加载提示词模板
        prompt_template = self._load_prompt_template()
        
        # 2. 构建动态提示词
        dynamic_prompt = self._build_dynamic_prompt(prompt_template, input_data)
        
        # 3. 调用LLM
        result = self._call_llm(dynamic_prompt)
        
        # 4. 解析结果
        parsed_result = self._parse_result(result)
        
        return {
            "analysis_result": parsed_result,
            "raw_response": result
        }
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        if not self.prompt_file:
            return ""
        
        # 构建完整路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_path, self.prompt_file)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        return ""
    
    def _build_dynamic_prompt(self, template: str, input_data: Dict[str, Any]) -> str:
        """构建动态提示词"""
        # 使用配置Agent动态构建
        context = self._build_context(input_data)
        
        # 获取动态配置
        if context.get('current_step'):
            dynamic_config = self.config_agent.get_analysis_step_config(context['current_step'])
        else:
            dynamic_config = self.config_agent.build_dynamic_prompt(context)
        
        # 合并模板和动态配置
        if template:
            return f"{template}\n\n{dynamic_config}"
        
        return dynamic_config
    
    def _build_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建分析上下文"""
        context = {
            "current_step": input_data.get('current_step', ''),
            "shishen_involved": input_data.get('shishen_involved', []),
            "day_strength": input_data.get('day_strength', 'unknown'),
            "need_examples": input_data.get('need_examples', False),
            "case_type": input_data.get('case_type', '')
        }
        
        return context
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是一位精通'子平真诠'与'滴天髓'的实战派命理师。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result
    
    def _parse_result(self, result: str) -> Dict[str, Any]:
        """解析结果"""
        return {
            "content": result,
            "length": len(result)
        }
