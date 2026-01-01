"""
意图识别Agent
识别用户是想做常规分析还是博弈交易法分析，并标记是否为对话/追问
"""
import re
from typing import Dict, Any, Optional
from core.models.state import AnalysisState


def extract_stock_code(message: str) -> str:
    """从消息中提取股票代码"""
    pattern = r'\b(\d{6})\b'
    matches = re.findall(pattern, message)
    if matches:
        return matches[0]
    return ""


def recognize_intent(message: str) -> str:
    """
    识别用户意图
    
    Returns:
        'game_theory' 或 'regular'
    """
    message_lower = message.lower()
    
    # 博弈交易法关键词
    game_theory_keywords = [
        '博弈', '阶段', '洗盘', '出货', '情绪比例', '锚定',
        '一阶段', '二阶段', '三阶段', '四阶段', '五阶段',
        'o点', '牛股结构', '多方锚定', '空方锚定',
        '波段洗盘', 'k线洗盘', '整体阶段', '趋势力量'
    ]
    
    # 常规分析关键词
    regular_keywords = [
        '技术分析', '指标', '均线', 'macd', 'rsi',
        '布林带', '支撑', '阻力', '技术'
    ]
    
    game_theory_count = sum(1 for keyword in game_theory_keywords if keyword in message_lower)
    regular_count = sum(1 for keyword in regular_keywords if keyword in message_lower)
    
    if game_theory_count > 0:
        return 'game_theory'
    if regular_count > 0:
        return 'regular'
    
    if '分析' in message:
        return 'regular'
    
    return 'regular'


def is_dialogue_message(message: str) -> bool:
    """
    判断是否是常规对话 / 对历史结论的追问
    不改变分析类型，只作为 route 的辅助信号
    """
    m = message.strip()
    ml = m.lower()

    # 明确的追问/续聊关键词
    followup_keywords = [
        "继续", "接着说", "再说说", "展开讲讲", "详细一点",
        "为啥", "为什么", "怎么看", "怎么理解",
        "上面那个", "刚才那个", "你刚才说的", "前面的结论",
        "总结一下", "帮我总结", "帮我解释", "再解释下",
        "这几个买点", "这几个卖点", "这个恐慌点", "这个卖点",
        "回顾一下", "整体说说", "再讲讲买点", "再讲讲卖点",
    ]
    if any(k in m for k in followup_keywords):
        return True

    # 很短的指令，通常是续聊
    if len(m) <= 6:
        return True

    # 没有代码且没有明显技术/博弈关键词，更偏向聊天/追问
    has_code = bool(extract_stock_code(m))
    tech_keywords = [
        '博弈', '阶段', '洗盘', '出货', '情绪比例', '锚定',
        '一阶段', '二阶段', '三阶段', '四阶段', '五阶段',
        'o点', '牛股结构', '多方锚定', '空方锚定',
        '技术分析', '均线', 'macd', 'rsi', '布林带', '支撑', '阻力'
    ]
    has_tech = any(k.lower() in ml for k in tech_keywords)
    if not has_code and not has_tech:
        return True

    return False


def detect_scene_type(message: str) -> Optional[str]:
    """
    识别用户是否在请求“只看某一类分析 / 重新做某一块”
    返回：
        'stage' / 'distribution' / 'emotion' / 'trading' / None
    """
    m = message.strip()

    # 阶段相关
    stage_keywords = [
        "阶段分析", "重新阶段", "重跑阶段", "只看阶段", "阶段再分析",
        "再做一遍阶段", "单独阶段"
    ]
    if any(k in m for k in stage_keywords):
        return "stage"

    # 出货相关
    dist_keywords = [
        "出货分析", "重新出货", "重跑出货", "只看出货", "出货再分析",
        "再做一遍出货", "单独出货", "分布分析", "分水岭分析"
    ]
    if any(k in m for k in dist_keywords):
        return "distribution"

    # 情绪相关
    emotion_keywords = [
        "情绪分析", "情绪比例", "重新情绪", "重跑情绪", "只看情绪",
        "情绪再分析", "锚定分析", "多空锚定"
    ]
    if any(k in m for k in emotion_keywords):
        return "emotion"

    # 买卖点相关
    trading_keywords = [
        "买卖点分析", "重新买卖点", "重跑买卖点", "只看买卖点",
        "恐慌点分析", "卖点分析", "买点分析"
    ]
    if any(k in m for k in trading_keywords):
        return "trading"

    return None


def intent_recognition_node(state: AnalysisState) -> AnalysisState:
    """意图识别节点"""
    user_message = state.get('user_message', '')
    
    # 提取股票代码
    stock_code = extract_stock_code(user_message)
    if not stock_code:
        stock_code = state.get('stock_code', '')
    
    # 识别分析类型
    analysis_type = recognize_intent(user_message)

    # 标记是否为对话/追问
    dialogue_mode = is_dialogue_message(user_message)

    # 检测是否为某个场景的定向分析请求
    scene_type = detect_scene_type(user_message)
    
    # 更新状态
    state['stock_code'] = stock_code
    state['analysis_type'] = analysis_type
    state['dialogue_mode'] = dialogue_mode
    state['scene_type'] = scene_type
    
    return state


