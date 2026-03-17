"""
大宗商品数据模型
定义供给、价格、新闻等数据实体
"""
from typing import TypedDict, List, Optional
from datetime import datetime


class SupplyNode(TypedDict):
    """供给节点"""
    region: str  # 产地/地区
    commodity_id: str  # 品种ID
    capacity_or_output: Optional[float]  # 产能或产量
    inventory: Optional[float]  # 库存
    trade_flow: Optional[str]  # 贸易流向
    key_entities_ports: Optional[List[str]]  # 主要企业/港口
    source_url: Optional[str]  # 数据来源URL
    source_name: Optional[str]  # 数据来源名称
    as_of_date: Optional[str]  # 数据日期


class PricePoint(TypedDict):
    """价格点"""
    commodity_id: str  # 品种ID
    market_or_contract: str  # 市场/合约
    price_type: str  # 价格类型：spot/future/index/spread
    value: float  # 价格值（收盘价）
    high: Optional[float]  # 最高价
    low: Optional[float]  # 最低价
    open: Optional[float]  # 开盘价
    volume: Optional[float]  # 成交量
    unit: str  # 单位
    as_of_date: str  # 数据日期
    source_url: Optional[str]  # 数据来源URL
    source_name: Optional[str]  # 数据来源名称


class NewsItem(TypedDict):
    """新闻项"""
    title: str  # 标题
    summary: str  # 摘要
    source_name: str  # 来源名称
    source_url: str  # 来源URL
    published_at: str  # 发布时间
    related_commodities: Optional[List[str]]  # 关联品种
    related_regions: Optional[List[str]]  # 关联地区
    tags: Optional[List[str]]  # 标签：policy/weather/geopolitics/supply_demand


class RawEvidence(TypedDict):
    """原始证据包"""
    supply_chain: List[SupplyNode]  # 供给链数据
    prices: List[PricePoint]  # 价格数据
    news: List[NewsItem]  # 新闻数据
    fetched_at: str  # 采集时间
    commodity_or_chain: str  # 品种或产业链
    time_range: Optional[dict]  # 时间范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
