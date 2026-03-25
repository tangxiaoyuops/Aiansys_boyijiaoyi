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
    shensha_analysis: Optional[Dict[str, Any]],
    birth_year: Optional[int] = None,
    name: Optional[str] = None
) -> str:
    """
    构建八字分析的提示词（用户消息部分）
    
    Args:
        sizhu: 四柱数据
        wuxing_analysis: 五行分析结果
        shishen_analysis: 十神分析结果
        dayun_analysis: 大运分析结果
        shensha_analysis: 神煞分析结果
        birth_year: 出生年份（公历）
        name: 姓名（可选，用于个性化报告）
    
    Returns:
        提示词字符串
    """
    from datetime import datetime
    
    # 获取当前时间信息
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    current_date_str = now.strftime("%Y年%m月%d日")
    
    # 获取当前农历日期
    current_lunar_str = ""
    try:
        from zhdate import ZhDate
        lunar_now = ZhDate.from_datetime(now)
        current_lunar_str = f"（农历{lunar_now.lunar_year}年{lunar_now.lunar_month}月{lunar_now.lunar_day}日）"
    except Exception:
        pass
    
    lines = ["## 八字分析信息\n"]
    
    # 如果有名字，显示名字
    if name:
        lines.append(f"### 👤 命主姓名：{name}\n")
    
    # 当前时间信息（关键：让LLM知道现在是什么时候）
    lines.append("### ⏰ 当前时间参考")
    lines.append(f"**当前日期：{current_date_str}{current_lunar_str}**")
    
    # 获取八字年份（以立春为界，可能与公历年份不同）
    bazi_year = sizhu.get('bazi_year', birth_year)
    
    # 明确显示公历出生年份和八字年份
    if birth_year:
        lines.append(f"**公历出生年份：{birth_year}年**")
    
    # 计算年龄和大运阶段
    if bazi_year:
        approximate_age = current_year - bazi_year
        lines.append(f"**命主年龄：约 {approximate_age} 岁**（八字年份：{bazi_year}年）")
        
        # 如果八字年份与公历出生年份不同，说明是立春前出生
        if birth_year and bazi_year != birth_year:
            lines.append(f"**重要：命主公历出生于{birth_year}年，但因在立春前，八字年柱为{bazi_year}年**")
        
        # 判断当前大运阶段
        if dayun_analysis:
            dayun_list = dayun_analysis.get('dayun_list', [])
            current_dayun = None
            for dayun in dayun_list:
                start_age = dayun.get('start_age', 0)
                end_age = dayun.get('end_age', 0)
                if start_age <= approximate_age < end_age:
                    current_dayun = dayun
                    break
            
            if current_dayun:
                dayun_index = dayun_list.index(current_dayun) + 1
                lines.append(f"**当前大运：第{dayun_index}步大运 {current_dayun.get('gan', '')}{current_dayun.get('zhi', '')}（{current_dayun.get('start_age', 0)}-{current_dayun.get('end_age', 0)}岁，{current_dayun.get('start_year', '')}-{current_dayun.get('end_year', '')}年）**")
    else:
        lines.append(f"**命主年龄：未知（请根据年柱推算出生年份）**")
    
    lines.append("")
    
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
    
    # 农历信息
    if sizhu.get('lunar_year'):
        lines.append(f"农历: {sizhu.get('lunar_year')}年{sizhu.get('lunar_month')}月{sizhu.get('lunar_day')}日")
    
    lines.append(f"性别: {sizhu.get('gender', '男')}")
    lines.append("")
    
    # 五行信息
    if wuxing_analysis:
        wuxing_data = wuxing_analysis.get('wuxing_data', {})
        lines.append("### 五行分布")
        wuxing_count = wuxing_data.get('wuxing_count', {})
        if wuxing_count:
            lines.append(f"金: {wuxing_count.get('金', 0)}, 木: {wuxing_count.get('木', 0)}, 水: {wuxing_count.get('水', 0)}, 火: {wuxing_count.get('火', 0)}, 土: {wuxing_count.get('土', 0)}")
        else:
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
                gan = dayun.get('gan', '')
                zhi = dayun.get('zhi', '')
                start_age = dayun.get('start_age', 0)
                end_age = dayun.get('end_age', 0)
                start_year = dayun.get('start_year', '')
                end_year = dayun.get('end_year', '')
                if start_year and end_year:
                    lines.append(f"第{i}步大运: {gan}{zhi} ({start_age}-{end_age}岁, {start_year}-{end_year}年)")
                else:
                    lines.append(f"第{i}步大运: {gan}{zhi} ({start_age}-{end_age}岁)")
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
    
    lines.append("---")
    lines.append(f"**重要提示**：请根据以上八字信息，结合当前时间（{current_date_str}），分析命主当前所处的人生阶段和大运运势。")
    lines.append("")
    lines.append("**⚠️ 关键数据（请严格遵守）**：")
    if birth_year:
        lines.append(f"- 命主公历出生年份：{birth_year}年（这是确定的出生年份，请直接引用）")
    if bazi_year:
        lines.append(f"- 八字年柱年份：{bazi_year}年（因为立春前出生，八字年份与公历年份不同）")
    lines.append("- 以上所有信息（农历日期、四柱、大运等）都已精确计算，请直接引用")
    lines.append("- 绝对不要自行推算或编造任何年份、日期信息")
    lines.append("- 所有农历日期、节气、大运时间均以系统提供为准")
    lines.append("- 如果您的计算与上述信息不符，请以上述信息为准")
    lines.append("")
    
    return "\n".join(lines)


# ==================== 合盘专用提示词 ====================

HEPAN_PROMPTS = {
    'couple': """你是一位精通传统命理学的专业合婚分析师，拥有深厚的理论功底和丰富的实战经验。

请按照以下专业框架进行合婚分析：

## 一、命盘概览
- 双方四柱结构对比
- 日主五行分析

## 二、合盘匹配分析
- 地支六合六冲解读：六合代表缘分深厚，六冲需要磨合
- 天干合化影响：天干五合代表性格互补
- 五行互补情况：五行互补代表相互补益
- 日主关系详解：相生有情，相克需包容

## 三、婚姻运势分析
- 感情契合度：从性格、价值观角度分析
- 性格互补性：双方性格特点及互补点
- 沟通与相处：日常相处模式分析
- 家庭关系：与双方家庭的关系

## 四、子女运分析
- 子女缘分
- 子女性别倾向
- 教育方向

## 五、发展建议
- 优势与机遇：命盘契合的优势
- 需要注意的问题：需要磨合的方面
- 趋吉避凶建议：实用的调理建议

请使用专业术语，但需解释其含义。分析要全面深入，逻辑清晰，给出实用的建议。""",

    'business': """你是一位精通商业命理的专业顾问，擅长分析合作伙伴之间的命盘契合度。

请按照以下专业框架进行商业合盘分析：

## 一、命盘概览
- 双方四柱结构对比
- 日主五行分析

## 二、合作契合度分析
- 性格匹配度：性格是否互补或冲突
- 决策风格对比：决策风格是否一致
- 风险承受能力：双方风险偏好
- 五行互补情况：五行互补代表能力互补

## 三、财运分析
- 各自财运特点：正财、偏财情况
- 合财可能性：合作是否能带来财运
- 投资风格差异：投资理念的异同

## 四、事业发展
- 事业运势周期
- 最佳合作时机
- 事业方向建议

## 五、合作建议
- 优势互补点：能力互补分析
- 需要注意的问题：潜在风险
- 最佳合作方式：股权、分工建议
- 趋吉避凶建议：实用的调理建议

请使用专业术语，但需解释其含义。分析要客观理性，给出实用的商业建议。""",
}


def get_hepan_system_prompt(hepan_type: str = 'couple') -> str:
    """
    获取合盘分析的系统提示词
    
    Args:
        hepan_type: 合盘类型 ('couple' | 'business')
    
    Returns:
        系统提示词
    """
    return HEPAN_PROMPTS.get(hepan_type, HEPAN_PROMPTS['couple'])


def build_hepan_prompt(
    pan_a: Dict,
    pan_b: Dict,
    hepan_result: Dict,
    hepan_type: str = 'couple',
    birth_info_a: Optional[Dict] = None,
    birth_info_b: Optional[Dict] = None,
    name_a: Optional[str] = None,
    name_b: Optional[str] = None,
) -> str:
    """
    构建合盘分析的用户提示词
    
    Args:
        pan_a: 命盘A分析结果
        pan_b: 命盘B分析结果
        hepan_result: 合盘匹配分析结果
        hepan_type: 合盘类型
        birth_info_a: 命盘A出生信息
        birth_info_b: 命盘B出生信息
        name_a: 命盘A姓名（可选）
        name_b: 命盘B姓名（可选）
    
    Returns:
        提示词字符串
    """
    lines = ["## 八字合盘分析信息\n"]
    
    # 命盘A信息
    display_name_a = name_a if name_a else "命盘A"
    lines.append(f"### {display_name_a}")
    sizhu_a = pan_a.get('sizhu', {})
    nian_a = sizhu_a.get('nian_zhu', {})
    yue_a = sizhu_a.get('yue_zhu', {})
    ri_a = sizhu_a.get('ri_zhu', {})
    shi_a = sizhu_a.get('shi_zhu', {})
    
    lines.append(f"四柱: {nian_a.get('tian_gan', '')}{nian_a.get('di_zhi', '')}年 "
                f"{yue_a.get('tian_gan', '')}{yue_a.get('di_zhi', '')}月 "
                f"{ri_a.get('tian_gan', '')}{ri_a.get('di_zhi', '')}日 "
                f"{shi_a.get('tian_gan', '')}{shi_a.get('di_zhi', '')}时")
    lines.append(f"日主: {sizhu_a.get('ri_zhu_tiangan', '')}")
    lines.append(f"性别: {hepan_result.get('gender_a', '男')}")
    
    if birth_info_a:
        lines.append(f"出生: {birth_info_a.get('year', '')}年{birth_info_a.get('month', '')}月{birth_info_a.get('day', '')}日")
    
    if sizhu_a.get('lunar_year'):
        lines.append(f"农历: {sizhu_a.get('lunar_year')}年{sizhu_a.get('lunar_month')}月{sizhu_a.get('lunar_day')}日")
    
    # 五行分析
    wuxing_a = pan_a.get('wuxing_analysis', {}).get('wuxing_data', {})
    if wuxing_a:
        lines.append(f"五行: 金{wuxing_a.get('jin', 0)} 木{wuxing_a.get('mu', 0)} 水{wuxing_a.get('shui', 0)} "
                    f"火{wuxing_a.get('huo', 0)} 土{wuxing_a.get('tu', 0)}")
    lines.append("")
    
    # 命盘B信息
    display_name_b = name_b if name_b else "命盘B"
    lines.append(f"### {display_name_b}")
    sizhu_b = pan_b.get('sizhu', {})
    nian_b = sizhu_b.get('nian_zhu', {})
    yue_b = sizhu_b.get('yue_zhu', {})
    ri_b = sizhu_b.get('ri_zhu', {})
    shi_b = sizhu_b.get('shi_zhu', {})
    
    lines.append(f"四柱: {nian_b.get('tian_gan', '')}{nian_b.get('di_zhi', '')}年 "
                f"{yue_b.get('tian_gan', '')}{yue_b.get('di_zhi', '')}月 "
                f"{ri_b.get('tian_gan', '')}{ri_b.get('di_zhi', '')}日 "
                f"{shi_b.get('tian_gan', '')}{shi_b.get('di_zhi', '')}时")
    lines.append(f"日主: {sizhu_b.get('ri_zhu_tiangan', '')}")
    lines.append(f"性别: {hepan_result.get('gender_b', '女')}")
    
    if birth_info_b:
        lines.append(f"出生: {birth_info_b.get('year', '')}年{birth_info_b.get('month', '')}月{birth_info_b.get('day', '')}日")
    
    if sizhu_b.get('lunar_year'):
        lines.append(f"农历: {sizhu_b.get('lunar_year')}年{sizhu_b.get('lunar_month')}月{sizhu_b.get('lunar_day')}日")
    
    # 五行分析
    wuxing_b = pan_b.get('wuxing_analysis', {}).get('wuxing_data', {})
    if wuxing_b:
        lines.append(f"五行: 金{wuxing_b.get('jin', 0)} 木{wuxing_b.get('mu', 0)} 水{wuxing_b.get('shui', 0)} "
                    f"火{wuxing_b.get('huo', 0)} 土{wuxing_b.get('tu', 0)}")
    lines.append("")
    
    # 合盘匹配结果
    lines.append("### 合盘匹配分析")
    scores = hepan_result.get('scores', {})
    lines.append(f"**总评分: {scores.get('total', 0)}分 ({scores.get('grade', '')})**")
    lines.append(f"- 地支匹配: {scores.get('di_zhi', 0)}分 - {scores.get('di_zhi_desc', '')}")
    lines.append(f"- 五行互补: {scores.get('wuxing', 0)}分 - {scores.get('wuxing_desc', '')}")
    lines.append(f"- 日主关系: {scores.get('rizhu', 0)}分 - {scores.get('rizhu_desc', '')}")
    lines.append(f"- 天干合化: {scores.get('tian_gan', 0)}分 - {scores.get('tian_gan_desc', '')}")
    lines.append("")
    
    # 地支关系详情
    di_zhi = hepan_result.get('di_zhi_relation', {})
    if di_zhi.get('liu_he'):
        lines.append("**地支六合:**")
        for he in di_zhi['liu_he']:
            lines.append(f"- {he['desc']}")
    if di_zhi.get('san_he'):
        lines.append("**地支三合:**")
        for san_he in di_zhi['san_he']:
            lines.append(f"- {san_he['desc']}")
    if di_zhi.get('liu_chong'):
        lines.append("**地支六冲:**")
        for chong in di_zhi['liu_chong']:
            lines.append(f"- {chong['desc']}")
    lines.append("")
    
    # 天干合化详情
    tian_gan = hepan_result.get('tian_gan_relation', {})
    if tian_gan.get('wu_he'):
        lines.append("**天干五合:**")
        for he in tian_gan['wu_he']:
            lines.append(f"- {he['desc']}")
    lines.append("")
    
    # 日主关系详情
    rizhu = hepan_result.get('rizhu_relation', {})
    if rizhu.get('relations'):
        lines.append("**日主关系:**")
        for rel in rizhu['relations']:
            lines.append(f"- {rel['desc']}")
    lines.append("")
    
    # 夫妻星匹配详情（仅情侣合婚）
    if hepan_type == 'couple':
        spouse_star = hepan_result.get('spouse_star_match', {})
        if spouse_star and spouse_star.get('details'):
            lines.append("**夫妻星匹配:**")
            for detail in spouse_star['details']:
                lines.append(f"- {detail.get('desc', '')}")
            lines.append("")
    
    # 五行互补详情
    wuxing = hepan_result.get('wuxing_match', {})
    lines.append("**五行分布对比:**")
    lines.append(f"- 命盘A: 金{wuxing.get('wuxing_a', {}).get('金', 0)} 木{wuxing.get('wuxing_a', {}).get('木', 0)} "
                f"水{wuxing.get('wuxing_a', {}).get('水', 0)} 火{wuxing.get('wuxing_a', {}).get('火', 0)} "
                f"土{wuxing.get('wuxing_a', {}).get('土', 0)}")
    lines.append(f"- 命盘B: 金{wuxing.get('wuxing_b', {}).get('金', 0)} 木{wuxing.get('wuxing_b', {}).get('木', 0)} "
                f"水{wuxing.get('wuxing_b', {}).get('水', 0)} 火{wuxing.get('wuxing_b', {}).get('火', 0)} "
                f"土{wuxing.get('wuxing_b', {}).get('土', 0)}")
    if wuxing.get('complement'):
        lines.append("**五行互补:**")
        for c in wuxing['complement']:
            lines.append(f"- {c['desc']}")
    if wuxing.get('conflict'):
        lines.append("**五行冲突:**")
        for c in wuxing['conflict']:
            lines.append(f"- {c['desc']}")
    lines.append("")
    
    # 建议
    if hepan_result.get('suggestions'):
        lines.append("**系统建议:**")
        for sug in hepan_result['suggestions'][:5]:
            lines.append(f"- {sug}")
        lines.append("")
    
    lines.append("---")
    if hepan_type == 'couple':
        lines.append("请根据以上信息，进行专业的八字合婚分析，重点分析婚姻和谐度、性格互补、未来发展等。")
    else:
        lines.append("请根据以上信息，进行专业的商业合盘分析，重点分析合作契合度、财运互补、决策风格等。")
    
    return "\n".join(lines)