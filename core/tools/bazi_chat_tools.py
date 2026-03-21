"""
八字追问工具集
包含处理各种追问类型的具体工具实现
"""
from typing import Dict, Any, List, Optional
from core.agents.bazi_tool_selector import BaziTool, BaziContext, register_bazi_tool, ToolRegistry
from core.tools.llm_client import call_llm
import logging

logger = logging.getLogger(__name__)


# ==================== 工具实现 ====================

class DetailAnalysisTool(BaziTool):
    """
    分析细节追问工具
    处理用户对五行、十神、神煞等具体分析内容的追问
    """
    
    name = "detail_analysis"
    description = "分析细节追问工具 - 解答五行、十神、神煞等具体问题"
    intent_types = ['detail']
    priority = 10
    
    def execute(
        self, 
        context: BaziContext, 
        user_message: str, 
        extracted_info: Dict, 
        **kwargs
    ) -> str:
        """执行细节分析"""
        
        # 构建上下文信息
        context_text = self.get_prompt_context(context)
        
        # 构建提示词
        system_prompt = """你是一位专业的八字命理师，擅长用通俗易懂的语言解释八字分析中的各种概念和结论。
当用户追问具体分析细节时：
1. 先用简单的话解释专业术语的含义
2. 结合用户的具体八字情况说明为什么会得出这样的结论
3. 给出实际生活层面的解读和建议
4. 如果用户问的是缺失的五行，解释缺失的影响和补益方法"""

        user_prompt = f"""用户八字信息：
{context_text}

用户的问题：{user_message}

请详细解答用户的问题，注意：
- 解释专业术语时要通俗易懂
- 结合八字具体情况分析
- 给出实用的建议"""

        response = call_llm(system_prompt, user_prompt, temperature=0.5)
        return response


class LifeGuideTool(BaziTool):
    """
    人生方向咨询工具
    处理事业、婚姻、财运、健康等人生方向问题
    """
    
    name = "life_guide"
    description = "人生方向咨询工具 - 解答事业、婚姻、财运、健康等问题"
    intent_types = ['life_guide']
    priority = 15
    
    def execute(
        self, 
        context: BaziContext, 
        user_message: str, 
        extracted_info: Dict, 
        **kwargs
    ) -> str:
        """执行人生指导分析"""
        
        context_text = self.get_prompt_context(context)
        
        system_prompt = """你是一位专业的八字命理师，擅长根据八字分析人生各方面的发展趋势。
在回答人生方向问题时：
1. 先分析八字中与问题相关的五行、十神、神煞
2. 给出趋势性的判断（有利/不利/平稳）
3. 提供具体可行的建议
4. 涉及时间的问题要结合大运流年分析
注意：回答要积极正面，避免过于消极的判断，强调个人努力的重要性。"""

        user_prompt = f"""用户八字信息：
{context_text}
性别：{context.gender}

用户的问题：{user_message}

请根据八字信息，详细分析并回答用户的问题："""

        response = call_llm(system_prompt, user_prompt, temperature=0.5)
        return response


class PeriodAnalysisTool(BaziTool):
    """
    时间段解读工具
    处理大运、流年、特定年份的运势分析
    """
    
    name = "period_analysis"
    description = "时间段解读工具 - 分析大运、流年、特定年份运势"
    intent_types = ['period']
    priority = 12
    
    def execute(
        self, 
        context: BaziContext, 
        user_message: str, 
        extracted_info: Dict, 
        **kwargs
    ) -> str:
        """执行时间段分析"""
        
        context_text = self.get_prompt_context(context)
        extra_info = ""
        
        # 处理提取的信息
        target_year = extracted_info.get('target_year')
        target_age = extracted_info.get('target_age')
        dayun_index = extracted_info.get('dayun_index')
        
        if target_year:
            extra_info = f"\n用户询问的目标年份：{target_year}年"
            # 如果有流年分析，添加到上下文
            if context.liunian_analysis:
                liunian_data = context.liunian_analysis.get('liunian_data', {})
                if str(target_year) in liunian_data:
                    extra_info += f"\n该年流年信息：{liunian_data[str(target_year)]}"
        
        if target_age:
            extra_info += f"\n用户询问的目标年龄：{target_age}岁"
        
        if dayun_index:
            extra_info += f"\n用户询问第{dayun_index}步大运"
            if context.dayun_analysis:
                dayun_list = context.dayun_analysis.get('dayun_list', [])
                if 0 < dayun_index <= len(dayun_list):
                    dy = dayun_list[dayun_index - 1]
                    extra_info += f"：{dy.get('gan', '?')}{dy.get('zhi', '?')} ({dy.get('start_age', '?')}-{dy.get('end_age', '?')}岁)"
        
        system_prompt = """你是一位专业的八字命理师，擅长分析大运、流年等时间周期对人生运势的影响。
在分析时间段运势时：
1. 先解释该时间段对应的大运/流年是什么
2. 分析该时期的五行属性与命局的关系
3. 判断该时期在各方面的运势（事业、财运、感情、健康等）
4. 给出该时期需要注意的事项和建议
注意：时间分析要客观，强调顺应时势、趋吉避凶。"""

        user_prompt = f"""用户八字信息：
{context_text}
{extra_info}

用户的问题：{user_message}

请根据八字和时间信息，详细分析用户询问的时间段运势："""

        response = call_llm(system_prompt, user_prompt, temperature=0.5)
        return response


class ReanalysisTool(BaziTool):
    """
    重新分析请求工具
    处理用户希望换风格、重新分析等请求
    """
    
    name = "reanalysis"
    description = "重新分析请求工具 - 处理换风格重新解读的请求"
    intent_types = ['reanalysis']
    priority = 8
    
    def execute(
        self, 
        context: BaziContext, 
        user_message: str, 
        extracted_info: Dict, 
        **kwargs
    ) -> str:
        """执行重新分析"""
        
        context_text = self.get_prompt_context(context)
        
        # 检查是否有偏好的风格
        preferred_style = extracted_info.get('preferred_style', context.analysis_style)
        
        # 风格对应的提示词调整
        style_prompts = {
            'classic': "请用传统专业的方式解读，使用完整的命理术语，分析深入全面。",
            'simple': "请用通俗易懂的方式解读，避免专业术语，让零基础的人也能理解。",
            'life_guide': "请从人生规划和指导的角度解读，关注人生阶段和发展建议。",
            'business': "请从事业和财富的角度解读，重点分析财运和事业发展的机遇与挑战。",
            'emotion': "请从情感和婚恋的角度解读，重点分析感情婚姻方面的趋势和建议。"
        }
        
        style_instruction = style_prompts.get(preferred_style, style_prompts['classic'])
        
        system_prompt = f"""你是一位专业的八字命理师，能够根据不同的风格要求进行八字解读。
{style_prompts.get(preferred_style, style_prompts['classic'])}
在重新分析时：
1. 给出完整的八字排盘信息
2. 按照用户要求的风格进行解读
3. 提供具体、有针对性的分析
4. 给出实用建议"""

        user_prompt = f"""用户八字信息：
{context_text}

用户的需求：{user_message}
解读风格偏好：{preferred_style}

请按照{style_instruction}进行完整解读："""

        response = call_llm(system_prompt, user_prompt, temperature=0.5)
        return response


class GeneralDialogueTool(BaziTool):
    """
    通用对话工具
    处理一般性的对话和追问
    """
    
    name = "general_dialogue"
    description = "通用对话工具 - 处理一般性追问和对话"
    intent_types = ['general', 'detail', 'life_guide', 'period', 'reanalysis']
    priority = 1  # 最低优先级，作为兜底
    
    def execute(
        self, 
        context: BaziContext, 
        user_message: str, 
        extracted_info: Dict, 
        **kwargs
    ) -> str:
        """执行通用对话"""
        
        context_text = self.get_prompt_context(context)
        chat_history = kwargs.get('chat_history', [])
        
        # 构建历史对话
        history_text = ""
        if chat_history:
            for turn in chat_history[-6:]:  # 最近6轮
                role = "用户" if turn.get("role") == "user" else "助手"
                content = turn.get("content", "")
                history_text += f"{role}：{content}\n"
        
        system_prompt = """你是一位专业的八字命理师，同时也是一位亲切的对话伙伴。
在回答用户问题时：
1. 结合用户的八字信息给出有针对性的回答
2. 如果用户的问题与八字关系不大，也可以进行一般性的交流
3. 回答要简洁明了，不要过于冗长
4. 保持专业但亲切的语气"""

        user_prompt = f"""用户八字信息：
{context_text}

历史对话：
{history_text if history_text else '（无历史对话）'}

用户的问题：{user_message}

请回答用户的问题："""

        response = call_llm(system_prompt, user_prompt, temperature=0.5)
        return response


# ==================== 工具注册 ====================

def register_default_tools():
    """注册默认工具"""
    registry = ToolRegistry()
    
    # 注册所有工具
    registry.register(DetailAnalysisTool())
    registry.register(LifeGuideTool())
    registry.register(PeriodAnalysisTool())
    registry.register(ReanalysisTool())
    registry.register(GeneralDialogueTool())
    
    logger.info(f"已注册 {len(registry.list_tools())} 个八字追问工具")


# 自动注册默认工具
register_default_tools()


# ==================== 导出 ====================

__all__ = [
    'DetailAnalysisTool',
    'LifeGuideTool', 
    'PeriodAnalysisTool',
    'ReanalysisTool',
    'GeneralDialogueTool',
    'register_default_tools'
]