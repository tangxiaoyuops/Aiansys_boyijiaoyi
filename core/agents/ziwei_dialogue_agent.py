"""
紫薇斗数对话Agent
简化版本：直接将命盘上下文+问题+历史对话发给LLM，让大模型自己决定如何回答
"""
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, field
import json
import logging

from core.tools.llm_client import call_llm, call_llm_stream

logger = logging.getLogger(__name__)


@dataclass
class ZiweiContext:
    """紫薇斗数上下文数据"""
    pan_data: Dict[str, Any] = field(default_factory=dict)
    si_hua_analysis: Optional[Dict] = None
    daxian_analysis: Optional[Dict] = None
    liunian_analysis: Optional[Dict] = None
    shensha_analysis: Optional[Dict] = None
    geju_analysis: Optional[Dict] = None
    llm_analysis: Optional[str] = None
    gender: str = '男'
    birth_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ZiweiDialogueState:
    """紫薇斗数对话状态"""
    conversation_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    ziwei_context: Optional[ZiweiContext] = None


class ZiweiDialogueAgent:
    """
    紫薇斗数对话Agent - 简化版本
    
    核心流程：
    1. 接收用户问题 + 命盘上下文 + 历史对话
    2. 构建包含完整信息的提示词
    3. 直接调用LLM生成回复
    4. 流式输出结果
    """
    
    def __init__(self):
        self.conversations: Dict[str, ZiweiDialogueState] = {}
    
    def get_or_create_conversation(self, conversation_id: str, ziwei_context: Optional[ZiweiContext] = None) -> ZiweiDialogueState:
        """获取或创建对话状态"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ZiweiDialogueState(
                conversation_id=conversation_id,
                ziwei_context=ziwei_context
            )
        elif ziwei_context:
            self.conversations[conversation_id].ziwei_context = ziwei_context
        return self.conversations[conversation_id]
    
    def build_context_text(self, context: ZiweiContext) -> str:
        """构建紫薇斗数上下文文本"""
        parts = []
        
        # 基础命盘信息
        if context.pan_data:
            parts.append("【命盘基础信息】")
            
            # 命宫身宫
            ming_gong = context.pan_data.get('ming_gong', 0)
            shen_gong = context.pan_data.get('shen_gong', 0)
            palace_names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母']
            parts.append(f"命宫: {palace_names[ming_gong] if ming_gong < 12 else '未知'}")
            parts.append(f"身宫: {palace_names[shen_gong] if shen_gong < 12 else '未知'}")
            
            # 出生信息
            birth_info = context.pan_data.get('birth_info', {})
            if birth_info:
                parts.append(f"出生: {birth_info.get('year', '')}年{birth_info.get('month', '')}月{birth_info.get('day', '')}日{birth_info.get('hour', '')}时")
                parts.append(f"年柱: {birth_info.get('year_gan', '')}{birth_info.get('year_zhi', '')}")
            
            # 主星分布
            main_stars = context.pan_data.get('main_stars', {})
            if main_stars:
                parts.append("\n【主星分布】")
                for star, pos in main_stars.items():
                    palace_name = palace_names[pos] if pos < 12 else f"宫位{pos}"
                    parts.append(f"{star}: {palace_name}")
            
            # 辅星分布
            auxiliary_stars = context.pan_data.get('auxiliary_stars', {})
            if auxiliary_stars:
                parts.append("\n【辅星分布】")
                for star, pos in auxiliary_stars.items():
                    palace_name = palace_names[pos] if pos < 12 else f"宫位{pos}"
                    parts.append(f"{star}: {palace_name}")
        
        # 四化分析
        if context.si_hua_analysis:
            si_hua = context.si_hua_analysis
            parts.append("\n【四化星分析】")
            
            # 统计信息
            stats = si_hua.get('statistics', {})
            if stats:
                parts.append(f"化禄: {stats.get('化禄_count', 0)}个")
                parts.append(f"化权: {stats.get('化权_count', 0)}个")
                parts.append(f"化科: {stats.get('化科_count', 0)}个")
                parts.append(f"化忌: {stats.get('化忌_count', 0)}个")
            
            # 汇总
            if si_hua.get('summary'):
                parts.append(si_hua['summary'])
            
            # 宫位分析
            palace_analysis = si_hua.get('palace_analysis', [])
            if palace_analysis:
                parts.append("\n各宫位四化:")
                for item in palace_analysis:
                    parts.append(f"{item.get('palace', '')}: {', '.join(item.get('si_hua', []))}")
        
        # 大限分析
        if context.daxian_analysis:
            daxian = context.daxian_analysis
            parts.append("\n【大限分析】")
            
            # 当前大限
            current = daxian.get('current_daxian') or daxian.get('daxian_analysis', {}).get('current_daxian')
            if current:
                parts.append(f"当前大限: 第{current.get('number', '')}大限, {current.get('start_age', '')}-{current.get('end_age', '')}岁")
            
            # 汇总
            summary = daxian.get('summary') or daxian.get('daxian_analysis', {}).get('summary')
            if summary:
                parts.append(summary)
        
        # 流年分析
        if context.liunian_analysis:
            liunian = context.liunian_analysis
            parts.append("\n【流年分析】")
            
            # 当前流年
            current = liunian.get('current_liunian') or liunian.get('liunian_analysis', {}).get('current_liunian')
            if current:
                parts.append(f"当前流年: {current.get('year', '')}年")
            
            # 汇总
            summary = liunian.get('summary') or liunian.get('liunian_analysis', {}).get('summary')
            if summary:
                parts.append(summary)
        
        # 神煞分析
        if context.shensha_analysis:
            shensha = context.shensha_analysis
            parts.append("\n【神煞分析】")
            
            # 汇总
            summary = shensha.get('summary') or shensha.get('shensha_analysis', {}).get('summary')
            if summary:
                parts.append(summary)
            
            # 神煞列表
            shensha_list = shensha.get('shensha_list') or shensha.get('shensha_analysis', {}).get('shensha_list', [])
            if shensha_list:
                for item in shensha_list[:10]:
                    parts.append(f"{item.get('name', '')}: {item.get('palace_name', '') or palace_names[item.get('palace', 0)] if item.get('palace', 0) < 12 else ''}")
        
        # 格局分析
        if context.geju_analysis:
            geju = context.geju_analysis
            parts.append("\n【格局分析】")
            
            # 汇总
            summary = geju.get('summary') or geju.get('geju_analysis', {}).get('summary')
            if summary:
                parts.append(summary)
            
            # 检测到的格局
            detected = geju.get('detected_geju') or geju.get('geju_analysis', {}).get('detected_geju', {})
            if detected:
                parts.append("检测到的格局:")
                for name, info in list(detected.items())[:5]:
                    parts.append(f"- {name}")
        
        # AI深度解析结果
        if context.llm_analysis:
            parts.append("\n【AI深度解析】")
            if isinstance(context.llm_analysis, dict):
                parts.append(context.llm_analysis.get('response', ''))
            else:
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
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位资深的紫微斗数命理分析专家，具有深厚的命理学知识和丰富的实践经验。

你的任务是：
1. 根据用户的命盘数据，回答用户的问题
2. 使用专业但易懂的语言进行分析，避免过于玄学的表述
3. 注重实用性和指导性，给出具体可行的建议
4. 如果问题涉及之前讨论的内容，请结合历史对话进行回答

回答时请注意：
- 结合命盘的具体星曜分布进行分析
- 考虑四化星的影响
- 关注大限流年对运势的影响
- 给出积极正面的指导建议
- 回答要条理清晰，逻辑严谨"""
    
    def process_message_stream(
        self,
        conversation_id: str,
        user_message: str,
        ziwei_context: ZiweiContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        处理用户消息（流式输出）
        
        核心流程：
        1. 构建完整的提示词（命盘上下文 + 历史对话 + 当前问题）
        2. 流式调用LLM
        3. 输出结果
        
        Args:
            conversation_id: 会话ID
            user_message: 用户消息
            ziwei_context: 紫薇斗数上下文
            chat_history: 前端传入的历史消息列表，格式: [{"role": "user/assistant", "content": "...", "type": "analysis/content"}]
        """
        state = self.get_or_create_conversation(conversation_id, ziwei_context)
        
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
        context_text = self.build_context_text(ziwei_context)
        history_text = self.build_history_text(state.messages[:-1])  # 不包括当前消息
        
        # 构建提示词
        system_prompt = self.get_system_prompt()
        
        user_prompt = f"""【用户命盘信息】
{context_text}

【性别】
{ziwei_context.gender}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

请根据用户的命盘信息，回答用户的问题。如果问题涉及之前讨论的内容，请结合历史对话进行回答。"""
        
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
        ziwei_context: ZiweiContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """处理用户消息（非流式）"""
        state = self.get_or_create_conversation(conversation_id, ziwei_context)
        
        # 如果前端传入了历史消息，使用前端的（包含深度分析）
        if chat_history:
            state.messages = chat_history.copy()
        
        state.messages.append({"role": "user", "content": user_message, "type": "content"})
        
        context_text = self.build_context_text(ziwei_context)
        history_text = self.build_history_text(state.messages[:-1])
        
        system_prompt = self.get_system_prompt()
        
        user_prompt = f"""【用户命盘信息】
{context_text}

【性别】
{ziwei_context.gender}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

请根据用户的命盘信息，回答用户的问题。"""
        
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
_ziwei_dialogue_agent = None

def get_ziwei_dialogue_agent() -> ZiweiDialogueAgent:
    """获取紫薇斗数对话Agent实例"""
    global _ziwei_dialogue_agent
    if _ziwei_dialogue_agent is None:
        _ziwei_dialogue_agent = ZiweiDialogueAgent()
    return _ziwei_dialogue_agent


# 便捷函数
def process_ziwei_dialogue(
    conversation_id: str,
    user_message: str,
    ziwei_context: ZiweiContext,
    stream: bool = True
):
    """处理紫薇斗数对话的便捷函数"""
    agent = get_ziwei_dialogue_agent()
    if stream:
        return agent.process_message_stream(conversation_id, user_message, ziwei_context)
    else:
        return agent.process_message(conversation_id, user_message, ziwei_context)
