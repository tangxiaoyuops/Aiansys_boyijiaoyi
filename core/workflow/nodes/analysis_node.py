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
        """构建分析上下文（含命盘、性别、对话历史等真实数据）"""
        context = {
            "current_step": input_data.get('current_step', ''),
            "shishen_involved": input_data.get('shishen_involved', []),
            "day_strength": input_data.get('day_strength', 'unknown'),
            "need_examples": input_data.get('need_examples', False),
            "case_type": input_data.get('case_type', ''),
            # 真实八字数据（修复：此前未传递导致LLM编造命盘/性别）
            "sizhu": input_data.get('sizhu', {}),
            "gender": input_data.get('gender', '男'),
            "birth_info": input_data.get('birth_info', {}),
            "user_question": input_data.get('user_question', ''),
            "conversation_history": input_data.get('conversation_history', []),
            "wuxing_data": input_data.get('wuxing_data', {}),
            "shishen_data": input_data.get('shishen_data', {}),
            "dayun_list": input_data.get('dayun_list', []),
            "liunian_data": input_data.get('liunian_data', {}),
            "shensha_data": input_data.get('shensha_data', {}),
            "llm_analysis": input_data.get('llm_analysis'),
        }
        return context

    def _format_sizhu_text(self, sizhu: Dict[str, Any]) -> str:
        """将sizhu字典格式化为易读文本"""
        if not sizhu:
            return "（无命盘数据）"
        zhu_names = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        parts = []
        for key, name in zhu_names.items():
            zhu = sizhu.get(key, {})
            if zhu:
                gan = zhu.get('tian_gan', '?')
                zhi = zhu.get('di_zhi', '?')
                cang = zhu.get('cang_gan', [])
                cang_str = f"（藏干:{'、'.join(cang)}）" if cang else ""
                parts.append(f"{name}: {gan}{zhi}{cang_str}")
        ri_gan = sizhu.get('ri_zhu_tiangan', '')
        if ri_gan:
            parts.append(f"日主: {ri_gan}")
        return "\n".join(parts) if parts else "（命盘数据为空）"

    def _format_history_text(self, history: list) -> str:
        """格式化对话历史"""
        if not history:
            return "（无历史对话，这是首次分析）"
        lines = []
        for i, msg in enumerate(history[-5:], 1):
            role = "用户" if msg.get('role') == 'user' else "命理师"
            content = msg.get('content', '')[:200]
            lines.append(f"第{i}轮 {role}: {content}")
        return "\n".join(lines)

    def _build_dynamic_prompt(self, template: str, input_data: Dict[str, Any]) -> str:
        """构建动态提示词（真正替换模板占位符）"""
        context = self._build_context(input_data)

        # 格式化真实数据
        sizhu_text = self._format_sizhu_text(context['sizhu'])
        gender = context.get('gender', '男')
        history_text = self._format_history_text(context.get('conversation_history', []))
        user_question = context.get('user_question', '')

        # 统一替换模板占位符（修复：此前占位符从未被替换）
        if template:
            replacements = {
                '{sizhu}': sizhu_text,
                '{wuxing_data}': str(context.get('wuxing_data', {})),
                '{rizhu}': context.get('sizhu', {}).get('ri_zhu_tiangan', '未知'),
                '{gender}': gender,
                '{birth_info}': str(context.get('birth_info', {})),
                '{conversation_history}': history_text,
                '{user_question}': user_question,
                '{shishen_data}': str(context.get('shishen_data', {})),
                '{dayun_list}': str(context.get('dayun_list', [])),
                '{liunian_data}': str(context.get('liunian_data', {})),
                '{shensha_data}': str(context.get('shensha_data', {})),
                '{llm_analysis}': str(context.get('llm_analysis', '')),
            }
            for key, value in replacements.items():
                template = template.replace(key, value)

        # 获取动态配置
        dynamic_config = self.config_agent.build_dynamic_prompt(context)

        # 组合：模板 + 基础约束 + 动态配置
        base_constraint = (
            "\n\n【⚠️ 铁律——必须严格遵守】\n"
            f"1. 本命盘性别为【{gender}】，所有关于配偶星（男命看财星/女命看官星）、大运、十神断语都必须以此性别为准，严禁按相反性别分析。\n"
            "2. 必须严格基于上方给定的四柱命盘数据作答，严禁编造、替换或臆想任何干支、日主、五行。如果数据缺失，明确说明缺失，不得虚构。\n"
            f"3. 用户问题：{user_question}\n"
            "4. 如存在【对话历史】，回答须承接上一轮内容，不要重复已说过的整套分析，针对当前追问深入。"
        )
        if template:
            return f"{template}\n{base_constraint}\n{dynamic_config}"
        return f"{base_constraint}\n{dynamic_config}"

    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        from core.tools.llm_client import call_llm

        result = call_llm(
            system_prompt=("你是精通'子平真诠'与'滴天髓'的实战派命理师。"
                           "回答必须严格基于用户提供的命盘和性别，严禁编造命盘、严禁按错误性别分析。"
                           "若为多轮追问，必须先承接上一轮对话结论再深入作答。"),
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
