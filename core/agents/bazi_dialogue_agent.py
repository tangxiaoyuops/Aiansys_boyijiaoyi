"""
八字对话Agent
简化版本：直接将八字上下文+问题+历史对话发给LLM，让大模型自己决定如何回答
"""
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, field
import json
import logging

from core.tools.llm_client import call_llm, call_llm_stream

logger = logging.getLogger(__name__)


@dataclass
class BaziContext:
    """八字上下文数据"""
    sizhu: Dict[str, Any] = field(default_factory=dict)
    wuxing_analysis: Optional[Dict] = None
    shishen_analysis: Optional[Dict] = None
    dayun_analysis: Optional[Dict] = None
    liunian_analysis: Optional[Dict] = None
    shensha_analysis: Optional[Dict] = None
    llm_analysis: Optional[str] = None
    analysis_style: str = 'classic'
    gender: str = '男'
    birth_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BaziDialogueState:
    """八字对话状态"""
    conversation_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    bazi_context: Optional[BaziContext] = None


class BaziDialogueAgent:
    """
    八字对话Agent - 简化版本
    
    核心流程：
    1. 接收用户问题 + 八字上下文 + 历史对话
    2. 构建包含完整信息的提示词
    3. 直接调用LLM生成回复
    4. 流式输出结果
    """
    
    def __init__(self):
        self.conversations: Dict[str, BaziDialogueState] = {}
    
    def get_or_create_conversation(self, conversation_id: str, bazi_context: Optional[BaziContext] = None) -> BaziDialogueState:
        """获取或创建对话状态"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = BaziDialogueState(
                conversation_id=conversation_id,
                bazi_context=bazi_context
            )
        elif bazi_context:
            self.conversations[conversation_id].bazi_context = bazi_context
        return self.conversations[conversation_id]
    
    def build_context_text(self, context: BaziContext) -> str:
        """构建八字上下文文本"""
        parts = []
        
        # 四柱信息
        if context.sizhu:
            parts.append("【四柱八字】")
            zhu_names = {
                'nian_zhu': '年柱', 'yue_zhu': '月柱',
                'ri_zhu': '日柱', 'shi_zhu': '时柱'
            }
            for key, name in zhu_names.items():
                zhu = context.sizhu.get(key, {})
                if zhu:
                    parts.append(f"{name}: {zhu.get('tian_gan', '?')}{zhu.get('di_zhi', '?')}")
            
            if context.sizhu.get('lunar_year'):
                parts.append(f"农历: {context.sizhu.get('lunar_year')}年{context.sizhu.get('lunar_month')}月{context.sizhu.get('lunar_day')}日")
        
        # 五行分析
        if context.wuxing_analysis:
            data = context.wuxing_analysis.get('wuxing_data', {})
            if data:
                parts.append("\n【五行分析】")
                wuxing_names = {'jin': '金', 'mu': '木', 'shui': '水', 'huo': '火', 'tu': '土'}
                for key, name in wuxing_names.items():
                    count = data.get(key, 0)
                    parts.append(f"{name}: {count}")
                if data.get('rizhu_wuxing'):
                    parts.append(f"日主五行: {data.get('rizhu_wuxing')}")
        
        # 十神分析
        if context.shishen_analysis:
            data = context.shishen_analysis.get('shishen_data', {})
            if data:
                parts.append("\n【十神分析】")
                zhu_names = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
                for key, name in zhu_names.items():
                    zhu_data = data.get(key, {})
                    if zhu_data:
                        gan = zhu_data.get('gan_shishen', '')
                        zhi = zhu_data.get('zhi_shishen', '')
                        parts.append(f"{name}: 天干{gan}, 地支{zhi}")
        
        # 大运分析
        if context.dayun_analysis:
            dayun_list = context.dayun_analysis.get('dayun_list', [])
            if dayun_list:
                parts.append("\n【大运分析】")
                for i, dy in enumerate(dayun_list[:8]):
                    parts.append(f"第{i+1}步: {dy.get('gan', '?')}{dy.get('zhi', '?')} ({dy.get('start_age', '?')}-{dy.get('end_age', '?')}岁)")
        
        # 神煞分析
        if context.shensha_analysis:
            shensha_list = context.shensha_analysis.get('shensha_data', {}).get('shensha_list', [])
            if shensha_list:
                parts.append("\n【神煞分析】")
                for ss in shensha_list:
                    parts.append(f"{ss.get('name', '')} ({ss.get('position', '')}) - {ss.get('type', '')}")
        
        # AI深度解析结果
        if context.llm_analysis:
            parts.append("\n【AI深度解析】")
            parts.append(context.llm_analysis)
        
        return "\n".join(parts)
    
    def build_history_text(self, messages: List[Dict[str, str]], is_first_assistant: bool = False) -> str:
        """构建历史对话文本"""
        if not messages:
            return "（无历史对话）"
        
        lines = []
        for i, msg in enumerate(messages):
            role = "用户" if msg.get("role") == "user" else "助手"
            content = msg.get("content", "")
            msg_type = msg.get("type", "content")
            
            # 第一条助手消息通常是深度分析，不截断
            if i == 0 and msg.get("role") == "assistant" and msg_type == "analysis":
                lines.append(f"【AI深度分析报告】\n{content}")
            else:
                # 后续对话，截断过长的内容
                if len(content) > 800:
                    content = content[:800] + "..."
                lines.append(f"{role}：{content}")
        
        return "\n".join(lines)
    
    def get_system_prompt(self, style: str = 'classic') -> str:
        """根据风格获取系统提示词"""
        style_prompts = {
            'classic': """你是一位专业的八字命理师，精通传统命理学，能够用专业术语进行深入分析。
回答时：
1. 结合八字具体情况进行专业解读
2. 使用传统命理术语，但也要适当解释含义
3. 给出实用的建议和指导
4. 回答要条理清晰，逻辑严谨""",

            'simple': """你是一位亲切的八字解读师，擅长用通俗易懂的语言为普通人解读命理。
回答时：
1. 避免使用过多专业术语，用生活化的语言解释
2. 多用比喻和例子帮助理解
3. 给出实际可行的建议
4. 语气亲切，像朋友聊天一样""",

            'life_guide': """你是一位人生规划顾问，擅长从八字角度给出人生方向的指导。
回答时：
1. 关注人生各个阶段的发展趋势
2. 分析事业、财运、感情、健康等方面
3. 给出具体的人生规划建议
4. 强调个人努力的重要性，积极正面""",

            'business': """你是一位商业顾问，擅长从八字角度分析事业和财运。
回答时：
1. 重点关注事业发展和财富运势
2. 分析适合的行业、职业方向
3. 给出投资理财方面的建议
4. 实事求是，避免过于乐观或悲观""",

            'emotion': """你是一位情感咨询师，擅长从八字角度分析感情和婚姻。
回答时：
1. 重点关注感情婚姻运势
2. 分析桃花、配偶特征等
3. 给出感情方面的建议
4. 语气温柔，给予鼓励和支持"""
        }
        
        return style_prompts.get(style, style_prompts['classic'])
    
    def process_message_stream(
        self,
        conversation_id: str,
        user_message: str,
        bazi_context: BaziContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        处理用户消息（流式输出）
        
        核心流程：
        1. 构建完整的提示词（八字上下文 + 历史对话 + 当前问题）
        2. 流式调用LLM
        3. 输出结果
        
        Args:
            conversation_id: 会话ID
            user_message: 用户消息
            bazi_context: 八字上下文
            chat_history: 前端传入的历史消息列表，格式: [{"role": "user/assistant", "content": "...", "type": "analysis/content"}]
        """
        state = self.get_or_create_conversation(conversation_id, bazi_context)
        
        # 如果前端传入了历史消息，使用前端的（包含深度分析）
        if chat_history:
            state.messages = chat_history.copy()
        
        # 添加用户消息到历史
        state.messages.append({"role": "user", "content": user_message, "type": "content"})
        
        # 发送开始信号
        yield {
            'type': 'start',
            'conversation_id': conversation_id
        }
        
        # 发送进度
        yield {
            'type': 'progress',
            'stage': 'building_context',
            'message': '正在准备回答...'
        }
        
        # 构建上下文
        context_text = self.build_context_text(bazi_context)
        history_text = self.build_history_text(state.messages[:-1])  # 不包括当前消息
        
        # 构建提示词
        system_prompt = self.get_system_prompt(bazi_context.analysis_style)
        
        user_prompt = f"""【用户八字信息】
{context_text}

【性别】
{bazi_context.gender}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

请根据用户的八字信息，回答用户的问题。如果问题涉及之前讨论的内容，请结合历史对话进行回答。"""

        # 发送进度
        yield {
            'type': 'progress',
            'stage': 'generating',
            'message': '正在生成回答...'
        }
        
        # 流式调用LLM
        full_response = ""
        try:
            for chunk in call_llm_stream(system_prompt, user_prompt, temperature=0.5):
                full_response += chunk
                yield {
                    'type': 'content',
                    'content': chunk
                }
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            # 降级为非流式
            try:
                full_response = call_llm(system_prompt, user_prompt, temperature=0.5)
                yield {
                    'type': 'content',
                    'content': full_response
                }
            except Exception as e2:
                logger.error(f"LLM非流式调用也失败: {e2}")
                yield {
                    'type': 'error',
                    'message': f'AI服务暂时不可用，请稍后重试'
                }
                return
        
        # 添加助手回复到历史
        state.messages.append({"role": "assistant", "content": full_response})
        
        # 发送完成信号
        yield {
            'type': 'done',
            'conversation_id': conversation_id
        }
    
    def process_message(
        self,
        conversation_id: str,
        user_message: str,
        bazi_context: BaziContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """处理用户消息（非流式）"""
        state = self.get_or_create_conversation(conversation_id, bazi_context)
        
        # 如果前端传入了历史消息，使用前端的（包含深度分析）
        if chat_history:
            state.messages = chat_history.copy()
        
        state.messages.append({"role": "user", "content": user_message, "type": "content"})
        
        context_text = self.build_context_text(bazi_context)
        history_text = self.build_history_text(state.messages[:-1])
        
        system_prompt = self.get_system_prompt(bazi_context.analysis_style)
        
        user_prompt = f"""【用户八字信息】
{context_text}

【性别】
{bazi_context.gender}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

请根据用户的八字信息，回答用户的问题。"""
        
        try:
            response = call_llm(system_prompt, user_prompt, temperature=0.5)
            state.messages.append({"role": "assistant", "content": response})
            
            return {
                'success': True,
                'response': response,
                'conversation_id': conversation_id
            }
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': '抱歉，AI服务暂时不可用，请稍后重试。',
                'conversation_id': conversation_id
            }
    
    def clear_conversation(self, conversation_id: str):
        """清除对话历史"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """获取对话历史"""
        state = self.conversations.get(conversation_id)
        if state:
            return state.messages.copy()
        return []


# 全局实例
_bazi_dialogue_agent = None

def get_bazi_dialogue_agent() -> BaziDialogueAgent:
    """获取八字对话Agent实例"""
    global _bazi_dialogue_agent
    if _bazi_dialogue_agent is None:
        _bazi_dialogue_agent = BaziDialogueAgent()
    return _bazi_dialogue_agent


# 便捷函数
def process_bazi_dialogue(
    conversation_id: str,
    user_message: str,
    bazi_context: BaziContext,
    stream: bool = True
):
    """处理八字对话的便捷函数"""
    agent = get_bazi_dialogue_agent()
    if stream:
        return agent.process_message_stream(conversation_id, user_message, bazi_context)
    else:
        return agent.process_message(conversation_id, user_message, bazi_context)