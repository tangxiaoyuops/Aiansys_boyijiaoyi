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
        from datetime import datetime
        parts = []
        
        # 四柱信息（含藏干）
        if context.sizhu:
            parts.append("【四柱八字】")
            zhu_names = {
                'nian_zhu': '年柱', 'yue_zhu': '月柱',
                'ri_zhu': '日柱', 'shi_zhu': '时柱'
            }
            for key, name in zhu_names.items():
                zhu = context.sizhu.get(key, {})
                if zhu:
                    gan = zhu.get('tian_gan', '?')
                    zhi = zhu.get('di_zhi', '?')
                    cang_gan = zhu.get('cang_gan', [])
                    cang_gan_str = f"（藏干: {'、'.join(cang_gan)}）" if cang_gan else ""
                    parts.append(f"{name}: {gan}{zhi}{cang_gan_str}")
            
            # 日主
            ri_gan = context.sizhu.get('ri_zhu_tiangan', '')
            if ri_gan:
                parts.append(f"日主: {ri_gan}")
            
            if context.sizhu.get('lunar_year'):
                parts.append(f"农历: {context.sizhu.get('lunar_year')}年{context.sizhu.get('lunar_month')}月{context.sizhu.get('lunar_day')}日")
            
            # 八字年份
            bazi_year = context.sizhu.get('bazi_year')
            if bazi_year:
                parts.append(f"八字年份: {bazi_year}年")
        
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
                
                # 五行详细分布（含藏干权重）
                wuxing_detail = data.get('wuxing_count_detail', {})
                if wuxing_detail:
                    parts.append(f"五行详细（含藏干）: 金{wuxing_detail.get('金', 0)}, 木{wuxing_detail.get('木', 0)}, 水{wuxing_detail.get('水', 0)}, 火{wuxing_detail.get('火', 0)}, 土{wuxing_detail.get('土', 0)}")
        
        # 五行喜忌
        try:
            from core.tools.bazi_calculator import calculate_wuxing_xi_ji
            wuxing_xi_ji = calculate_wuxing_xi_ji(context.sizhu, context.wuxing_analysis)
            if wuxing_xi_ji:
                parts.append("\n【五行喜忌】")
                parts.append(f"日主强弱: {'偏强' if wuxing_xi_ji.get('is_rizhu_qiang') else '偏弱'}")
                parts.append(f"喜用五行: {'、'.join(wuxing_xi_ji.get('xi_wuxing', []))}")
                parts.append(f"忌讳五行: {'、'.join(wuxing_xi_ji.get('ji_wuxing', []))}")
        except Exception:
            pass
        
        # 十神分析（含藏干十神）
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
                        # 藏干十神
                        cang_gan_shishen = zhu_data.get('zhi_cang_gan_shishen', [])
                        if cang_gan_shishen:
                            parts_str = [f"{item.get('cang_gan', '')}({item.get('shishen', '')})" for item in cang_gan_shishen]
                            parts.append(f"  藏干十神: {', '.join(parts_str)}")
        
        # 大运分析（标注当前大运）
        if context.dayun_analysis:
            dayun_list = context.dayun_analysis.get('dayun_list', [])
            if dayun_list:
                parts.append("\n【大运分析】")
                # 计算当前年龄
                current_year = datetime.now().year
                birth_info = context.birth_info or {}
                birth_year = birth_info.get('year', context.sizhu.get('bazi_year'))
                current_age = current_year - birth_year if birth_year else None
                
                for i, dy in enumerate(dayun_list[:8]):
                    gan = dy.get('gan', '?')
                    zhi = dy.get('zhi', '?')
                    start_age = dy.get('start_age', '?')
                    end_age = dy.get('end_age', '?')
                    start_year = dy.get('start_year', '')
                    end_year = dy.get('end_year', '')
                    
                    # 标注当前大运
                    is_current = ""
                    if current_age is not None:
                        try:
                            if float(start_age) <= current_age <= float(end_age):
                                is_current = " ← 当前大运"
                        except (ValueError, TypeError):
                            pass
                    
                    if start_year and end_year:
                        parts.append(f"第{i+1}步: {gan}{zhi} ({start_age}-{end_age}岁, {start_year}-{end_year}年){is_current}")
                    else:
                        parts.append(f"第{i+1}步: {gan}{zhi} ({start_age}-{end_age}岁){is_current}")
        
        # 流年分析
        if context.liunian_analysis:
            liunian_data = context.liunian_analysis.get('liunian_data', {})
            if liunian_data:
                parts.append("\n【流年分析】")
                current_year = datetime.now().year
                # 显示当前流年和未来几年
                for yr_str, liunian in liunian_data.items():
                    try:
                        yr = int(yr_str)
                        if current_year - 1 <= yr <= current_year + 2:
                            gan = liunian.get('gan', '')
                            zhi = liunian.get('zhi', '')
                            gan_zhi = liunian.get('gan_zhi', f"{gan}{zhi}")
                            is_current = " ← 当前流年" if yr == current_year else ""
                            parts.append(f"{yr}年: {gan_zhi}{is_current}")
                    except (ValueError, TypeError):
                        continue
        else:
            # 如果没有流年分析，计算当前流年
            try:
                from core.tools.bazi_calculator import calculate_liunian
                current_year = datetime.now().year
                parts.append("\n【流年分析】")
                for yr in range(current_year - 1, current_year + 3):
                    liunian = calculate_liunian(context.sizhu, yr)
                    gan = liunian.get('gan', '')
                    zhi = liunian.get('zhi', '')
                    is_current = " ← 当前流年" if yr == current_year else ""
                    parts.append(f"{yr}年: {gan}{zhi}{is_current}")
            except Exception:
                pass
        
        # 神煞分析
        if context.shensha_analysis:
            shensha_list = context.shensha_analysis.get('shensha_data', {}).get('shensha_list', [])
            if shensha_list:
                parts.append("\n【神煞分析】")
                for ss in shensha_list:
                    parts.append(f"{ss.get('name', '')} ({ss.get('position', '')}) - {ss.get('type', '')}")
        
        # 地支关系（用于判断流通阻塞）
        try:
            from core.tools.bazi_calculator import calculate_zhi_relations, calculate_gan_relations
            zhi_relations = calculate_zhi_relations(context.sizhu)
            gan_relations = calculate_gan_relations(context.sizhu)
            
            relation_parts = []
            if zhi_relations.get('liu_he'):
                relation_parts.append("六合: " + "、".join([r['desc'] for r in zhi_relations['liu_he']]))
            if zhi_relations.get('liu_chong'):
                relation_parts.append("六冲: " + "、".join([r['desc'] for r in zhi_relations['liu_chong']]))
            if zhi_relations.get('san_he'):
                relation_parts.append("三合: " + "、".join([r['desc'] for r in zhi_relations['san_he']]))
            if zhi_relations.get('san_xing'):
                relation_parts.append("三刑: " + "、".join([r['desc'] for r in zhi_relations['san_xing']]))
            if zhi_relations.get('liu_hai'):
                relation_parts.append("六害: " + "、".join([r['desc'] for r in zhi_relations['liu_hai']]))
            
            if gan_relations.get('tian_gan_he'):
                relation_parts.append("天干合: " + "、".join([r['desc'] for r in gan_relations['tian_gan_he']]))
            if gan_relations.get('tian_gan_chong'):
                relation_parts.append("天干冲: " + "、".join([r['desc'] for r in gan_relations['tian_gan_chong']]))
            
            if relation_parts:
                parts.append("\n【干支关系（格局流通参考）】")
                parts.extend(relation_parts)
        except Exception:
            pass
        
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
        # 气机流转核心分析框架（所有风格通用，每次对话都必须遵循）
        core_requirement = """

【⚠️ 核心分析要求 —— 气机流转分析法（每次回答必须遵循）】

你是精通"子平真诠"与"滴天髓"的实战派命理师。分析严禁使用模棱两可的形容词，必须遵循"气机流转"的物理法则。无论用户问什么，都必须先过以下三步推演，再回答具体问题：

## 第一步：定格局底色（气机分析）
- 先看地支六合、三合、三会局，判断命局的"稳定性"与"能量流向"
- 如果有合局，优先按"合化"论断，不要上来就论"冲克"
- 逐一说明：哪些五行因合而化（能量转化了）、哪些五行因无合而独立（能量直冲）
- 明确当前命局的气机是"流通"（生扶连贯）还是"阻塞"（克战阻断）

## 第二步：大运定调（天干表象 vs 地支实质）
- 明确大运天干地支对原局的"覆盖"与"引动"作用
- 天干为表象（外在环境、表面事件），地支为实质（内在根因、实际力量）
- 大运地支是否与原局地支形成新的合局或冲局？这决定气机走向
- 大运是"引动"了原局沉睡的能量，还是"覆盖"了原局本来的格局

## 第三步：流年断事逻辑链
1. 流年干支进入原局，先看"合"（贪合忘冲），再看"冲"
2. 通过十神定位"事件类型"：印星动=学习/换工作/文书，财星动=赚钱/父亲/妻子，官杀动=升迁/是非/健康，食伤动=投资/子女/表达，比劫动=竞争/破财/合作
3. 结合五行旺衰，判断事件的"吉凶程度"：是暴富还是小赚，是破产还是小亏

## 输出格式（必须按此结构）
**气机分析**：[能量如何流转——合化了什么、冲克了什么、流通还是阻塞]
**现象推导**：[基于气机推导的具体事件——十神定位+五行旺衰定程度]
**断语结论**：[一句话定性，不含糊]"""

        style_prompts = {
            'classic': """你是一位精通传统命理学的专业分析师，精通"子平真诠"与"滴天髓"的实战派命理师。
回答时：
1. 结合八字具体情况进行专业解读，使用传统命理术语并解释含义
2. 严格遵循气机流转分析法，先定格局底色再推大运流年
3. 给出实用的趋吉避凶建议
4. 回答条理清晰，逻辑严谨，断语明确不含糊""" + core_requirement,

            'simple': """你是一位亲切的八字解读师，擅长用通俗易懂的语言为普通人解读命理。
回答时：
1. 避免使用过多专业术语，用生活化的语言解释
2. 多用比喻和例子帮助理解（如把气机流转比作水流、把合局比作汇流）
3. 给出实际可行的建议
4. 语气亲切，像朋友聊天一样

注意：虽然语言通俗，但分析逻辑不能省略——要让用户明白"能量往哪里走""当前是顺势还是逆势""今年会发生什么事"，只是用通俗方式表达。""" + core_requirement,

            'life_guide': """你是一位人生规划顾问，擅长从八字角度给出人生方向的指导。
回答时：
1. 关注人生各个阶段的发展趋势
2. 分析事业、财运、感情、健康等方面
3. 给出具体的人生规划建议
4. 强调个人努力的重要性，积极正面

注意：建议必须建立在气机流转分析之上。要说明当前大运的气机走向是顺是逆、流年引动了什么十神、现在是行动的时机还是等待的时机，让建议有命理依据而非空泛之谈。""" + core_requirement,

            'business': """你是一位商业顾问，擅长从八字角度分析事业和财运。
回答时：
1. 重点关注事业发展和财富运势
2. 分析适合的行业、职业方向
3. 给出投资理财方面的建议
4. 实事求是，避免过于乐观或悲观

注意：商业判断必须遵循气机流转分析。先看原局财官格局的气机是否通畅，再看大运是否引动财星或官星，最后看流年是否是行动的触发点。要明确说明"现在财运气机是通是堵""流年财星是动还是静""该出手还是该观望"。""" + core_requirement,

            'emotion': """你是一位情感咨询师，擅长从八字角度分析感情和婚姻。
回答时：
1. 重点关注感情婚姻运势
2. 分析桃花、配偶特征等
3. 给出感情方面的建议
4. 语气温柔，给予鼓励和支持

注意：感情分析也要遵循气机流转。先看夫妻宫（日支）气机是否通畅、财官星（配偶星）是否被合化或冲克，再看大运引动了什么、流年是否触动了桃花或夫妻宫。让分析有时机感：什么时候感情会动、什么时候需要耐心等待。""" + core_requirement,
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