"""
八字意图识别Agent
支持可扩展的意图注册机制，用于识别用户追问的类型
"""
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentDefinition:
    """意图定义"""
    intent_type: str                    # 意图类型标识
    description: str                    # 意图描述
    keywords: List[str] = field(default_factory=list)  # 关键词列表
    patterns: List[str] = field(default_factory=list)  # 正则表达式模式
    priority: int = 0                   # 优先级，数字越大优先级越高
    detector: Optional[Callable[[str, Dict], bool]] = None  # 自定义检测函数


class IntentRegistry:
    """
    意图注册表 - 可扩展架构核心
    支持动态注册新的意图类型和识别规则
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._intents: Dict[str, IntentDefinition] = {}
            cls._instance._register_default_intents()
        return cls._instance
    
    def _register_default_intents(self):
        """注册默认的意图类型"""
        
        # 分析细节追问
        self.register(IntentDefinition(
            intent_type='detail',
            description='分析细节追问',
            keywords=[
                '为什么', '怎么理解', '啥意思', '什么意思', '解释一下',
                '详细说说', '展开讲讲', '详细一点', '具体说说',
                '怎么算的', '怎么来的', '为什么说', '怎么会',
                '五行', '十神', '神煞', '大运', '日主', '格局',
                '缺什么', '旺衰', '强弱', '喜用', '忌神'
            ],
            patterns=[
                r'为什么说.{0,10}(缺|旺|弱|强)',
                r'(五行|十神|神煞).{0,5}(怎么样|什么意思|解释)',
                r'这个.{0,5}(神煞|十神|五行).{0,5}(有|没)',
            ],
            priority=10
        ))
        
        # 人生方向咨询
        self.register(IntentDefinition(
            intent_type='life_guide',
            description='人生方向咨询',
            keywords=[
                '适合', '职业', '事业', '行业', '工作',
                '婚姻', '感情', '恋爱', '配偶', '对象',
                '财运', '赚钱', '投资', '理财',
                '健康', '身体', '运势', '运气',
                '性格', '特点', '优缺点', '天赋',
                '方位', '颜色', '数字', '贵人'
            ],
            patterns=[
                r'(适合|应该)(什么|哪个).{0,5}(行业|职业|工作|方向)',
                r'(婚姻|感情|恋爱).{0,5}(怎么样|如何|什么时候)',
                r'(财运|赚钱|投资).{0,5}(怎么样|如何)',
                r'(我|我的).{0,5}(贵人|桃花)',
            ],
            priority=15
        ))
        
        # 时间段解读
        self.register(IntentDefinition(
            intent_type='period',
            description='时间段解读',
            keywords=[
                '大运', '流年', '今年', '明年', '后年',
                '当前', '现在', '近期', '未来', '过去',
                '哪年', '什么时候', '几年', '年龄段',
                '转运', '转折', '关键'
            ],
            patterns=[
                r'(今年|明年|后年|\d{4}年).{0,5}(怎么样|运势|运气)',
                r'当前.{0,5}大运',
                r'(第|几).{0,3}步大运',
                r'(\d+岁|几岁).{0,5}(怎么样|运势)',
            ],
            priority=12
        ))
        
        # 重新分析请求
        self.register(IntentDefinition(
            intent_type='reanalysis',
            description='重新分析请求',
            keywords=[
                '重新', '再', '换个', '换一种', '换种',
                '详细', '完整', '全面', '深入',
                '风格', '方式', '角度'
            ],
            patterns=[
                r'(重新|再).{0,5}(分析|解读|看看|排盘)',
                r'换个.{0,5}(风格|方式|角度)',
                r'(用|按).{0,5}(风格|方式).{0,5}(分析|解读)',
            ],
            priority=8
        ))
        
        # 通用对话
        self.register(IntentDefinition(
            intent_type='general',
            description='通用对话',
            keywords=[],
            patterns=[],
            priority=0  # 最低优先级，作为默认
        ))
    
    def register(self, intent: IntentDefinition):
        """注册一个新的意图"""
        self._intents[intent.intent_type] = intent
        logger.debug(f"注册意图: {intent.intent_type} - {intent.description}")
    
    def unregister(self, intent_type: str) -> bool:
        """注销一个意图"""
        if intent_type in self._intents:
            del self._intents[intent_type]
            return True
        return False
    
    def get_intent(self, intent_type: str) -> Optional[IntentDefinition]:
        """获取意图定义"""
        return self._intents.get(intent_type)
    
    def list_intents(self) -> List[IntentDefinition]:
        """列出所有意图"""
        return sorted(self._intents.values(), key=lambda x: -x.priority)


class BaziIntentRecognizer:
    """
    八字意图识别器
    """
    
    def __init__(self):
        self.registry = IntentRegistry()
    
    def recognize(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        识别用户消息的意图
        
        Args:
            message: 用户消息
            context: 八字上下文（包含sizhu、分析结果等）
        
        Returns:
            {
                'intent_type': str,      # 意图类型
                'confidence': float,     # 置信度 0-1
                'matched_keywords': list,# 匹配的关键词
                'matched_patterns': list,# 匹配的正则
                'extracted_info': dict   # 提取的信息
            }
        """
        if context is None:
            context = {}
        
        message_lower = message.lower()
        results = []
        
        for intent in self.registry.list_intents():
            if intent.intent_type == 'general':
                continue  # 跳过默认意图，最后处理
            
            matched_keywords = []
            matched_patterns = []
            score = 0.0
            
            # 关键词匹配
            for keyword in intent.keywords:
                if keyword in message or keyword in message_lower:
                    matched_keywords.append(keyword)
                    score += 1.0
            
            # 正则模式匹配
            for pattern in intent.patterns:
                try:
                    if re.search(pattern, message):
                        matched_patterns.append(pattern)
                        score += 2.0  # 正则匹配权重更高
                except re.error:
                    continue
            
            # 自定义检测函数
            if intent.detector:
                try:
                    if intent.detector(message, context):
                        score += 3.0
                except Exception as e:
                    logger.warning(f"自定义检测函数执行失败: {e}")
            
            if score > 0 or intent.intent_type == 'general':
                # 计算置信度
                max_score = len(intent.keywords) + len(intent.patterns) * 2 + 3
                confidence = min(score / max(max_score, 1), 1.0) if max_score > 0 else 0.5
                
                results.append({
                    'intent_type': intent.intent_type,
                    'description': intent.description,
                    'confidence': confidence,
                    'matched_keywords': matched_keywords,
                    'matched_patterns': matched_patterns,
                    'priority': intent.priority
                })
        
        # 按优先级和置信度排序
        results.sort(key=lambda x: (-x['priority'], -x['confidence']))
        
        # 如果没有匹配到任何意图，返回通用对话
        if not results:
            results.append({
                'intent_type': 'general',
                'description': '通用对话',
                'confidence': 0.5,
                'matched_keywords': [],
                'matched_patterns': [],
                'priority': 0
            })
        
        best_match = results[0]
        
        # 提取额外信息
        extracted_info = self._extract_info(message, context)
        
        return {
            'intent_type': best_match['intent_type'],
            'description': best_match['description'],
            'confidence': best_match['confidence'],
            'matched_keywords': best_match['matched_keywords'],
            'matched_patterns': best_match['matched_patterns'],
            'extracted_info': extracted_info
        }
    
    def _extract_info(self, message: str, context: Dict) -> Dict[str, Any]:
        """
        从消息中提取额外信息
        """
        extracted = {}
        
        # 提取年份
        year_patterns = [
            r'(\d{4})年',
            r'(\d{4})',
        ]
        for pattern in year_patterns:
            match = re.search(pattern, message)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2100:
                    extracted['target_year'] = year
                    break
        
        # 提取年龄
        age_match = re.search(r'(\d+)(岁|年)', message)
        if age_match:
            extracted['target_age'] = int(age_match.group(1))
        
        # 提取大运序号
        dayun_match = re.search(r'第(\d+)(步|期)', message)
        if dayun_match:
            extracted['dayun_index'] = int(dayun_match.group(1))
        
        # 提取分析风格偏好
        style_keywords = {
            'classic': ['传统', '专业', '详细'],
            'simple': ['简单', '通俗', '易懂'],
            'life_guide': ['人生', '规划', '指导'],
            'business': ['事业', '商业', '财富', '财运'],
            'emotion': ['感情', '婚姻', '恋爱']
        }
        for style, keywords in style_keywords.items():
            if any(kw in message for kw in keywords):
                extracted['preferred_style'] = style
                break
        
        return extracted


def create_intent_detector(intent_type: str, detector_func: Callable[[str, Dict], bool]):
    """
    创建自定义意图检测器的工厂函数
    
    Args:
        intent_type: 要增强的意图类型
        detector_func: 检测函数
    
    Returns:
        注册函数
    """
    registry = IntentRegistry()
    intent = registry.get_intent(intent_type)
    if intent:
        intent.detector = detector_func
    return intent


# 导出便捷函数
def recognize_bazi_intent(message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    识别八字追问意图的便捷函数
    """
    recognizer = BaziIntentRecognizer()
    return recognizer.recognize(message, context)


# 意图识别节点（用于工作流）
def bazi_intent_recognition_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    八字意图识别节点
    """
    user_message = state.get('user_message', '')
    bazi_context = state.get('bazi_context', {})
    
    result = recognize_bazi_intent(user_message, bazi_context)
    
    state['intent_result'] = result
    state['intent_type'] = result['intent_type']
    state['extracted_info'] = result.get('extracted_info', {})
    
    logger.info(f"意图识别完成: {result['intent_type']} (置信度: {result['confidence']:.2f})")
    
    return state