"""
八字分析提示词风格系统
提供多种分析风格，满足不同用户的需求
"""
from typing import Dict, Any, Optional
from enum import Enum


class AnalysisStyle(str, Enum):
    """分析风格枚举"""
    CLASSIC = "classic"           # 传统专业风格
    SIMPLE = "simple"             # 简明通俗风格
    LIFE_GUIDE = "life_guide"     # 人生指南风格
    BUSINESS = "business"         # 商业决策风格
    EMOTION = "emotion"           # 情感婚恋风格


# 风格名称映射
STYLE_NAMES: Dict[str, str] = {
    AnalysisStyle.CLASSIC: "传统专业",
    AnalysisStyle.SIMPLE: "简明通俗",
    AnalysisStyle.LIFE_GUIDE: "人生指南",
    AnalysisStyle.BUSINESS: "商业决策",
    AnalysisStyle.EMOTION: "情感婚恋",
}

# 风格描述
STYLE_DESCRIPTIONS: Dict[str, str] = {
    AnalysisStyle.CLASSIC: "专业术语完整，适合有一定基础的爱好者，分析深入全面",
    AnalysisStyle.SIMPLE: "语言通俗易懂，适合初学者，用生活化的语言解释专业概念",
    AnalysisStyle.LIFE_GUIDE: "侧重人生规划建议，从性格、事业、健康等角度给出实用指导",
    AnalysisStyle.BUSINESS: "侧重商业决策参考，分析财运、事业运、人际关系等",
    AnalysisStyle.EMOTION: "侧重情感婚恋分析，解读桃花、姻缘、家庭关系等",
}


def get_system_prompt(style: str) -> str:
    """
    根据风格获取系统提示词
    
    Args:
        style: 分析风格
    
    Returns:
        系统提示词
    """
    prompts = {
        # 传统专业风格
        AnalysisStyle.CLASSIC: """你是一位精通传统命理学的专业分析师，拥有深厚的理论功底和丰富的实战经验。

请按照以下专业框架进行分析：

## 一、四柱结构分析
- 年柱：祖上根基、童年运势
- 月柱：父母兄弟、青年运势
- 日柱：自身配偶、中年运势
- 时柱：子女晚辈、晚年运势

## 二、五行旺衰分析
- 各五行的强弱分布
- 日主旺衰判断
- 用神喜忌推导

## 三、十神格局解读
- 正印偏印、正官偏官、正财偏财等十神含义
- 格局高低判断

## 四、大运流年趋势
- 当前所处大运阶段
- 未来运势走向

## 五、综合建议
- 优势与机遇
- 劣势与风险
- 趋吉避凶建议

请使用专业术语，但需解释其含义。分析要全面深入，逻辑清晰。""",

        # 简明通俗风格
        AnalysisStyle.SIMPLE: """你是一位善于用简单语言解释复杂概念的分析师，擅长把专业术语转化为普通人能理解的表述。

请按照以下方式进行分析：

**你的核心性格特点是什么？**
用3-5个关键词描述这个人的性格，并举一个生活中的例子说明。

**你最大的优势在哪里？**
说出2-3个天生擅长的领域或能力，比如"你很适合做..."这类具体的建议。

**你需要注意什么？**
坦诚地说出可能遇到的困难或弱点，但要用温和的方式表达，并给出应对建议。

**你的人生发展节奏是怎样的？**
用简单的时间线说明什么时候是积累期，什么时候是收获期。

**给你的实用建议**
给出3条具体、可操作的生活建议。

注意事项：
- 避免使用专业术语，如果必须用要解释
- 多用生活中的例子来类比
- 语言要积极正面，即使说缺点也要有建设性
- 篇幅控制在800字以内""",

        # 人生指南风格
        AnalysisStyle.LIFE_GUIDE: """你是一位睿智的人生规划师，善于从命理角度给出人生发展建议。

请从以下几个维度进行分析：

【性格底色】
用温暖的语言描述这个人的核心性格特质，包括：
- 内在驱动力是什么
- 情绪模式是怎样的
- 与人相处的方式

【事业发展】
分析事业发展方向：
- 适合从事的行业类型
- 事业发展节奏（早成/晚成）
- 需要注意的职场问题

【财富运势】
财富方面的分析：
- 财富积累方式
- 理财投资倾向
- 需要注意的财务风险

【健康状况】
健康养生建议：
- 需要关注的身体部位
- 养生保健建议
- 生活作息建议

【人际关系】
人际社交分析：
- 与家人的关系
- 朋友社交的特点
- 贵人运如何

【人生阶段规划】
给出人生阶段性建议：
- 当前阶段重点
- 未来5-10年规划
- 人生重要节点提示

请用温暖、正向的语言，给出具体可行的建议。""",

        # 商业决策风格
        AnalysisStyle.BUSINESS: """你是一位专注商业决策的分析顾问，从命理角度为商业决策提供参考视角。

请按照以下商业框架进行分析：

■ 创业/职业方向
- 最适合创业还是打工
- 推荐的行业领域（列出3-5个）
- 职业发展的最佳路径

■ 财运分析
- 正财（固定收入）运势
- 偏财（投资/副业）运势
- 财富积累周期判断

■ 合作伙伴
- 适合的合作伙伴类型
- 合作中需要注意的问题
- 用人的策略建议

■ 投资理财
- 投资风格倾向（激进/稳健）
- 适合的投资方向
- 需要规避的风险

■ 决策时机
- 当前是否适合做重大决策
- 未来有利的时间节点
- 需要观望的时期

■ 商业风险提示
- 可能遇到的主要风险
- 风险应对策略

请保持客观理性，分析要有数据支撑的逻辑，避免过于玄学的表述。用商业语言而非命理语言表达。""",

        # 情感婚恋风格
        AnalysisStyle.EMOTION: """你是一位情感婚恋咨询师，从命理角度解读感情运势，帮助人们更好地理解和经营感情。

请从以下几个方面分析：

♡ 性格与爱情观
- 在感情中的性格特点
- 理想伴侣的画像
- 感情中的优点和需要改进的地方

♡ 桃花运势
- 桃花类型（正桃花/烂桃花）
- 异性缘如何
- 吸引什么类型的人

♡ 婚姻运势
- 婚姻运势高低
- 适合结婚的年龄段
- 婚姻中需要注意的问题

♡ 感情发展节奏
- 感情空窗期和收获期
- 重要感情节点提示
- 感情发展趋势

♡ 伴侣特质分析
- 理想伴侣的性格特质
- 适合的生肖/五行属性
- 共同成长的方向

♡ 情感建议
- 如何提升感情运势
- 经营感情的方法
- 需要避免的感情雷区

请用温暖、体贴的语言，给出真诚的建议。要兼顾现实考量，不要给出过于理想化的建议。""",
    }
    
    return prompts.get(style, prompts[AnalysisStyle.CLASSIC])


def get_style_display_name(style: str) -> str:
    """获取风格显示名称"""
    return STYLE_NAMES.get(style, "传统专业")


def get_style_description(style: str) -> str:
    """获取风格描述"""
    return STYLE_DESCRIPTIONS.get(style, "专业术语完整，适合有一定基础的爱好者")


def get_all_styles() -> list:
    """获取所有可用风格列表"""
    return [
        {
            "value": AnalysisStyle.CLASSIC,
            "name": STYLE_NAMES[AnalysisStyle.CLASSIC],
            "description": STYLE_DESCRIPTIONS[AnalysisStyle.CLASSIC],
        },
        {
            "value": AnalysisStyle.SIMPLE,
            "name": STYLE_NAMES[AnalysisStyle.SIMPLE],
            "description": STYLE_DESCRIPTIONS[AnalysisStyle.SIMPLE],
        },
        {
            "value": AnalysisStyle.LIFE_GUIDE,
            "name": STYLE_NAMES[AnalysisStyle.LIFE_GUIDE],
            "description": STYLE_DESCRIPTIONS[AnalysisStyle.LIFE_GUIDE],
        },
        {
            "value": AnalysisStyle.BUSINESS,
            "name": STYLE_NAMES[AnalysisStyle.BUSINESS],
            "description": STYLE_DESCRIPTIONS[AnalysisStyle.BUSINESS],
        },
        {
            "value": AnalysisStyle.EMOTION,
            "name": STYLE_NAMES[AnalysisStyle.EMOTION],
            "description": STYLE_DESCRIPTIONS[AnalysisStyle.EMOTION],
        },
    ]


def build_bazi_prompt(
    sizhu: Dict[str, Any],
    wuxing_analysis: Optional[Dict[str, Any]],
    shishen_analysis: Optional[Dict[str, Any]],
    dayun_analysis: Optional[Dict[str, Any]],
    shensha_analysis: Optional[Dict[str, Any]]
) -> str:
    """
    构建八字分析的提示词（用户消息部分）
    
    Args:
        sizhu: 四柱数据
        wuxing_analysis: 五行分析结果
        shishen_analysis: 十神分析结果
        dayun_analysis: 大运分析结果
        shensha_analysis: 神煞分析结果
    
    Returns:
        提示词字符串
    """
    lines = ["## 八字分析信息\n"]
    
    # 四柱信息
    lines.append("### 四柱信息")
    nian_zhu = sizhu.get('nian_zhu', {})
    yue_zhu = sizhu.get('yue_zhu', {})
    ri_zhu = sizhu.get('ri_zhu', {})
    shi_zhu = sizhu.get('shi_zhu', {})
    lines.append(f"年柱: {nian_zhu.get('tian_gan', '')}{nian_zhu.get('di_zhi', '')}")
    lines.append(f"月柱: {yue_zhu.get('tian_gan', '')}{yue_zhu.get('di_zhi', '')}")
    lines.append(f"日柱: {ri_zhu.get('tian_gan', '')}{ri_zhu.get('di_zhi', '')} (日主: {sizhu.get('ri_zhu_tiangan', '')})")
    lines.append(f"时柱: {shi_zhu.get('tian_gan', '')}{shi_zhu.get('di_zhi', '')}")
    lines.append(f"性别: {sizhu.get('gender', '男')}")
    lines.append("")
    
    # 五行信息
    if wuxing_analysis:
        wuxing_data = wuxing_analysis.get('wuxing_data', {})
        lines.append("### 五行分布")
        lines.append(f"金: {wuxing_data.get('jin', 0)}, 木: {wuxing_data.get('mu', 0)}, 水: {wuxing_data.get('shui', 0)}, 火: {wuxing_data.get('huo', 0)}, 土: {wuxing_data.get('tu', 0)}")
        lines.append(f"日主五行: {wuxing_data.get('rizhu_wuxing', '')}")
        lines.append("")
    
    # 十神信息
    if shishen_analysis:
        shishen_data = shishen_analysis.get('shishen_data', {})
        lines.append("### 十神关系")
        zhu_names = {'nian_zhu': '年柱', 'yue_zhu': '月柱', 'ri_zhu': '日柱', 'shi_zhu': '时柱'}
        for zhu_name, shishen_info in shishen_data.items():
            gan_shishen = shishen_info.get('gan_shishen', '')
            zhi_shishen = shishen_info.get('zhi_shishen', '')
            if gan_shishen or zhi_shishen:
                display_name = zhu_names.get(zhu_name, zhu_name)
                lines.append(f"{display_name}: 天干十神={gan_shishen}, 地支十神={zhi_shishen}")
        lines.append("")
    
    # 大运信息
    if dayun_analysis:
        dayun_list = dayun_analysis.get('dayun_list', [])
        if dayun_list:
            lines.append("### 大运信息")
            for i, dayun in enumerate(dayun_list[:8], 1):
                lines.append(f"第{i}步大运: {dayun.get('gan', '')}{dayun.get('zhi', '')} ({dayun.get('start_age', 0)}-{dayun.get('end_age', 0)}岁)")
            lines.append("")
    
    # 神煞信息
    if shensha_analysis:
        shensha_data = shensha_analysis.get('shensha_data', {})
        shensha_list = shensha_data.get('shensha_list', [])
        if shensha_list:
            lines.append("### 神煞信息")
            for shensha in shensha_list:
                lines.append(f"{shensha.get('name', '')}: 位于{shensha.get('position', '')} ({shensha.get('type', '')}神)")
            lines.append("")
    
    lines.append("请根据以上八字信息，按照你的分析框架进行详细解读。")
    
    return "\n".join(lines)