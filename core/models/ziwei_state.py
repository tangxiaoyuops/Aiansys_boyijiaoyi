"""
紫微斗数数据模型定义模块
定义完整的命盘数据结构和分析结果结构
"""
from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime

# ==================== 基础数据结构 ====================

class BirthInfo(TypedDict, total=False):
    """出生信息"""
    year: int  # 公历年份
    month: int  # 公历月份
    day: int  # 公历日期
    hour: int  # 时辰（0-23）
    gender: str  # 性别（'男' 或 '女'）
    lunar_year: int  # 农历年份
    lunar_month: int  # 农历月份
    lunar_day: int  # 农历日期
    year_gan: str  # 年干
    year_zhi: str  # 年支
    month_zhi: str  # 月支
    shi_chen: str  # 时辰地支

class PalaceData(TypedDict, total=False):
    """宫位数据"""
    index: int  # 宫位索引（0-11）
    name: str  # 宫位名称
    main_stars: List[str]  # 主星列表
    auxiliary_stars: List[str]  # 辅星列表
    si_hua: List[str]  # 四化列表（化禄、化权、化科、化忌）
    shensha: List[str]  # 神煞列表
    brightness: Optional[str]  # 亮度（庙、旺、利、得、平、陷）
    is_ming_gong: bool  # 是否为命宫
    is_shen_gong: bool  # 是否为身宫

class ZiweiPanData(TypedDict, total=False):
    """紫微斗数命盘数据"""
    birth_info: BirthInfo  # 出生信息
    ming_gong: int  # 命宫索引
    shen_gong: int  # 身宫索引
    ziwei_palace: int  # 紫微星所在宫位
    palaces: List[PalaceData]  # 十二宫位数据
    main_stars: Dict[str, int]  # 主星位置（星名 -> 宫位索引）
    auxiliary_stars: Dict[str, int]  # 辅星位置（星名 -> 宫位索引）
    si_hua: Optional[Dict[str, Any]]  # 四化星数据
    shensha: Optional[Dict[str, int]]  # 神煞数据（神煞名 -> 宫位索引）
    geju: Optional[Dict[str, Any]]  # 格局数据

# ==================== 分析结果数据结构 ====================

class SiHuaAnalysis(TypedDict, total=False):
    """四化星分析结果"""
    statistics: Dict[str, int]  # 四化统计（化禄、化权、化科、化忌的数量）
    palace_analysis: List[Dict[str, Any]]  # 各宫位四化分析
    hua_ji_analysis: Dict[str, Any]  # 化忌分析
    hua_lu_analysis: Dict[str, Any]  # 化禄分析
    summary: str  # 四化分析总结

class DaxianAnalysis(TypedDict, total=False):
    """大限分析结果"""
    current_daxian: Dict[str, Any]  # 当前大限信息
    all_daxian: List[Dict[str, Any]]  # 所有大限列表
    palace: Dict[str, Any]  # 大限所在宫位
    analysis: Dict[str, Any]  # 大限影响分析
    summary: str  # 大限分析总结

class LiunianAnalysis(TypedDict, total=False):
    """流年分析结果"""
    liunian: Dict[str, Any]  # 流年基本信息
    taisui_analysis: Dict[str, Any]  # 流年太岁分析
    ming_gong_relation: Dict[str, Any]  # 与命宫关系
    si_hua_analysis: Dict[str, Any]  # 流年四化分析
    summary: str  # 流年分析总结

class LiuyueAnalysis(TypedDict, total=False):
    """流月分析结果"""
    liuyue: Dict[str, Any]  # 流月基本信息
    si_hua_analysis: Dict[str, Any]  # 流月四化分析
    summary: str  # 流月分析总结

class ShenshaAnalysis(TypedDict, total=False):
    """神煞分析结果"""
    shensha_data: Dict[str, int]  # 神煞数据
    analysis: Dict[str, Any]  # 各神煞分析
    summary: str  # 神煞分析总结

class GejuAnalysis(TypedDict, total=False):
    """格局分析结果"""
    detected_geju: Dict[str, Any]  # 检测到的格局
    geju_analysis: Dict[str, Any]  # 各格局分析
    ming_gong_triangular: Dict[str, Any]  # 命宫三方分析
    ming_gong_four_corners: Dict[str, Any]  # 命宫四正分析
    summary: str  # 格局分析总结

class ZiweiAnalysisResult(TypedDict, total=False):
    """紫微斗数完整分析结果"""
    pan_data: ZiweiPanData  # 命盘数据
    basic_analysis: Optional[str]  # 基础分析
    si_hua_analysis: Optional[SiHuaAnalysis]  # 四化分析
    daxian_analysis: Optional[DaxianAnalysis]  # 大限分析
    liunian_analysis: Optional[LiunianAnalysis]  # 流年分析
    liuyue_analysis: Optional[LiuyueAnalysis]  # 流月分析
    shensha_analysis: Optional[ShenshaAnalysis]  # 神煞分析
    geju_analysis: Optional[GejuAnalysis]  # 格局分析
    llm_analysis: Optional[Dict[str, Any]]  # LLM深度分析
    success: bool  # 是否成功
    error: Optional[str]  # 错误信息

