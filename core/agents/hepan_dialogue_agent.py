"""
八字合盘对话Agent
支持合盘场景下的多轮对话和追问
"""
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, field
import json
import logging

from core.tools.llm_client import call_llm, call_llm_stream
from core.agents.bazi_prompt_styles import get_hepan_system_prompt, build_hepan_prompt

logger = logging.getLogger(__name__)


@dataclass
class HepanContext:
    """合盘上下文数据"""
    hepan_type: str = 'couple'  # 'couple' | 'business'
    # 命盘A
    name_a: Optional[str] = None  # 姓名（可选）
    pan_a: Dict[str, Any] = field(default_factory=dict)
    birth_info_a: Dict[str, Any] = field(default_factory=dict)
    gender_a: str = '男'
    # 命盘B
    name_b: Optional[str] = None  # 姓名（可选）
    pan_b: Dict[str, Any] = field(default_factory=dict)
    birth_info_b: Dict[str, Any] = field(default_factory=dict)
    gender_b: str = '女'
    # 合盘结果
    hepan_result: Dict[str, Any] = field(default_factory=dict)
    llm_analysis: Optional[str] = None


@dataclass
class HepanDialogueState:
    """合盘对话状态"""
    conversation_id: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    hepan_context: Optional[HepanContext] = None


class HepanDialogueAgent:
    """
    合盘对话Agent
    
    核心流程：
    1. 接收用户问题 + 合盘上下文 + 历史对话
    2. 构建包含完整信息的提示词
    3. 直接调用LLM生成回复
    4. 流式输出结果
    """
    
    def __init__(self):
        self.conversations: Dict[str, HepanDialogueState] = {}
    
    def get_or_create_conversation(self, conversation_id: str, hepan_context: Optional[HepanContext] = None) -> HepanDialogueState:
        """获取或创建对话状态"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = HepanDialogueState(
                conversation_id=conversation_id,
                hepan_context=hepan_context
            )
        elif hepan_context:
            self.conversations[conversation_id].hepan_context = hepan_context
        return self.conversations[conversation_id]
    
    def build_context_text(self, context: HepanContext) -> str:
        """构建合盘上下文文本"""
        parts = []
        
        # 命盘A信息
        if context.pan_a:
            sizhu_a = context.pan_a.get('sizhu', {})
            display_name_a = context.name_a if context.name_a else "命盘A"
            parts.append(f"【{display_name_a}】")
            parts.append(f"性别: {context.gender_a}")
            
            # 四柱
            zhu_names = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
            zhu_strs = []
            for key, name in zhu_names.items():
                zhu = sizhu_a.get(key, {})
                if zhu:
                    zhu_strs.append(f"{zhu.get('tian_gan', '?')}{zhu.get('di_zhi', '?')}")
            if zhu_strs:
                parts.append(f"四柱: {' '.join(zhu_strs)}")
            
            if sizhu_a.get('ri_zhu_tiangan'):
                parts.append(f"日主: {sizhu_a.get('ri_zhu_tiangan')}")
            
            # 五行
            wuxing_a = context.pan_a.get('wuxing_analysis', {}).get('wuxing_data', {})
            if wuxing_a:
                parts.append(f"五行: 金{wuxing_a.get('jin', 0)} 木{wuxing_a.get('mu', 0)} 水{wuxing_a.get('shui', 0)} 火{wuxing_a.get('huo', 0)} 土{wuxing_a.get('tu', 0)}")
        
        # 命盘B信息
        if context.pan_b:
            sizhu_b = context.pan_b.get('sizhu', {})
            display_name_b = context.name_b if context.name_b else "命盘B"
            parts.append(f"\n【{display_name_b}】")
            parts.append(f"性别: {context.gender_b}")
            
            # 四柱
            zhu_strs = []
            for key, name in zhu_names.items():
                zhu = sizhu_b.get(key, {})
                if zhu:
                    zhu_strs.append(f"{zhu.get('tian_gan', '?')}{zhu.get('di_zhi', '?')}")
            if zhu_strs:
                parts.append(f"四柱: {' '.join(zhu_strs)}")
            
            if sizhu_b.get('ri_zhu_tiangan'):
                parts.append(f"日主: {sizhu_b.get('ri_zhu_tiangan')}")
            
            # 五行
            wuxing_b = context.pan_b.get('wuxing_analysis', {}).get('wuxing_data', {})
            if wuxing_b:
                parts.append(f"五行: 金{wuxing_b.get('jin', 0)} 木{wuxing_b.get('mu', 0)} 水{wuxing_b.get('shui', 0)} 火{wuxing_b.get('huo', 0)} 土{wuxing_b.get('tu', 0)}")
        
        # 合盘匹配结果
        if context.hepan_result:
            parts.append("\n【合盘匹配分析】")
            scores = context.hepan_result.get('scores', {})
            parts.append(f"总评分: {scores.get('total', 0)}分 ({scores.get('grade', '')})")
            
            # 地支关系
            di_zhi = context.hepan_result.get('di_zhi_relation', {})
            if di_zhi.get('liu_he'):
                he_strs = [he['desc'] for he in di_zhi['liu_he']]
                parts.append(f"地支六合: {', '.join(he_strs)}")
            if di_zhi.get('san_he'):
                san_he_strs = [sh['desc'] for sh in di_zhi['san_he']]
                parts.append(f"地支三合: {', '.join(san_he_strs)}")
            if di_zhi.get('liu_chong'):
                chong_strs = [ch['desc'] for ch in di_zhi['liu_chong']]
                parts.append(f"地支六冲: {', '.join(chong_strs)}")
            
            # 日主关系
            rizhu = context.hepan_result.get('rizhu_relation', {})
            if rizhu.get('overall_desc'):
                parts.append(f"日主关系: {rizhu.get('overall_desc')}")
            
            # 五行互补
            wuxing_match = context.hepan_result.get('wuxing_match', {})
            if wuxing_match.get('complement'):
                comp_strs = [c['desc'] for c in wuxing_match['complement']]
                parts.append(f"五行互补: {', '.join(comp_strs)}")
            
            # 夫妻星匹配（情侣合婚）
            if context.hepan_type == 'couple':
                spouse_star = context.hepan_result.get('spouse_star_match', {})
                if spouse_star and spouse_star.get('details'):
                    spouse_strs = [d['desc'] for d in spouse_star['details']]
                    parts.append(f"夫妻星匹配: {', '.join(spouse_strs)}")
        
        # AI深度解析结果
        if context.llm_analysis:
            parts.append("\n【AI深度解析】")
            # 截断过长的分析结果
            analysis = context.llm_analysis
            if len(analysis) > 2000:
                analysis = analysis[:2000] + "..."
            parts.append(analysis)
        
        return "\n".join(parts)
    
    def build_history_text(self, messages: List[Dict[str, str]]) -> str:
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
                # 深度分析内容可能很长，截断
                if len(content) > 1500:
                    content = content[:1500] + "..."
                lines.append(f"【AI深度分析报告】\n{content}")
            else:
                # 后续对话，截断过长的内容
                if len(content) > 600:
                    content = content[:600] + "..."
                lines.append(f"{role}：{content}")
        
        return "\n".join(lines)
    
    def get_system_prompt(self, hepan_type: str = 'couple') -> str:
        """根据合盘类型获取系统提示词"""
        return get_hepan_system_prompt(hepan_type)
    
    def process_message_stream(
        self,
        conversation_id: str,
        user_message: str,
        hepan_context: HepanContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        处理用户消息（流式输出）
        
        Args:
            conversation_id: 会话ID
            user_message: 用户消息
            hepan_context: 合盘上下文
            chat_history: 前端传入的历史消息列表
        """
        state = self.get_or_create_conversation(conversation_id, hepan_context)
        
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
        context_text = self.build_context_text(hepan_context)
        history_text = self.build_history_text(state.messages[:-1])  # 不包括当前消息
        
        # 构建提示词
        system_prompt = self.get_system_prompt(hepan_context.hepan_type)
        
        # 根据合盘类型定制提示
        if hepan_context.hepan_type == 'couple':
            focus_hint = "请结合合盘匹配分析结果，重点解答关于婚姻、感情、相处等方面的问题。"
        else:
            focus_hint = "请结合合盘匹配分析结果，重点解答关于合作、事业、财运等方面的问题。"
        
        user_prompt = f"""【合盘分析信息】
{context_text}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

{focus_hint}
如果问题涉及之前讨论的内容，请结合历史对话进行回答。"""
        
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
        hepan_context: HepanContext,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """处理用户消息（非流式）"""
        state = self.get_or_create_conversation(conversation_id, hepan_context)
        
        # 如果前端传入了历史消息，使用前端的
        if chat_history:
            state.messages = chat_history.copy()
        
        state.messages.append({"role": "user", "content": user_message, "type": "content"})
        
        context_text = self.build_context_text(hepan_context)
        history_text = self.build_history_text(state.messages[:-1])
        
        system_prompt = self.get_system_prompt(hepan_context.hepan_type)
        
        if hepan_context.hepan_type == 'couple':
            focus_hint = "请结合合盘匹配分析结果，重点解答关于婚姻、感情、相处等方面的问题。"
        else:
            focus_hint = "请结合合盘匹配分析结果，重点解答关于合作、事业、财运等方面的问题。"
        
        user_prompt = f"""【合盘分析信息】
{context_text}

【历史对话】
{history_text}

【用户当前问题】
{user_message}

{focus_hint}"""
        
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
_hepan_dialogue_agent = None

def get_hepan_dialogue_agent() -> HepanDialogueAgent:
    """获取合盘对话Agent实例"""
    global _hepan_dialogue_agent
    if _hepan_dialogue_agent is None:
        _hepan_dialogue_agent = HepanDialogueAgent()
    return _hepan_dialogue_agent


# 便捷函数
def process_hepan_dialogue(
    conversation_id: str,
    user_message: str,
    hepan_context: HepanContext,
    stream: bool = True
):
    """处理合盘对话的便捷函数"""
    agent = get_hepan_dialogue_agent()
    if stream:
        return agent.process_message_stream(conversation_id, user_message, hepan_context)
    else:
        return agent.process_message(conversation_id, user_message, hepan_context)