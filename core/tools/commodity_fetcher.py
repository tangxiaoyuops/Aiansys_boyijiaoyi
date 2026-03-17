"""
大宗商品数据采集工具
从公开网站/API获取供给、价格、新闻数据
"""
import time
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.models.commodity_models import SupplyNode, PricePoint, NewsItem, RawEvidence

# 尝试导入真实数据源
try:
    from core.tools.futures_data_fetcher import fetch_futures_data, get_futures_name
    REAL_DATA_AVAILABLE = True
    print(f"[数据采集] 真实数据源模块导入成功")
except ImportError as e:
    REAL_DATA_AVAILABLE = False
    print(f"[数据采集] 真实数据源模块导入失败: {e}，将使用模拟数据")


class CommodityFetcher:
    """大宗商品数据采集器"""
    
    def __init__(self):
        self.commodity_mapping = {
            "原油": "crude_oil",
            "布伦特": "brent",
            "WTI": "wti",
            "铜": "copper",
            "铝": "aluminum",
            "锌": "zinc",
            "铅": "lead",
            "镍": "nickel",
            "锡": "tin",
            "大豆": "soybean",
            "豆粕": "soybean_meal",
            "豆油": "soybean_oil",
            "玉米": "corn",
            "小麦": "wheat",
            "棉花": "cotton",
            "白糖": "sugar",
            "橡胶": "rubber",
            "铁矿": "iron_ore",
            "焦煤": "coking_coal",
            "焦炭": "coke",
            "螺纹钢": "rebar",
            "热卷": "hot_rolled_coil",
            "甲醇": "methanol",
            "PTA": "pta",
            "PP": "polypropylene",
            "PVC": "pvc",
            "乙二醇": "ethylene_glycol",
            "尿素": "urea",
            "纯碱": "soda_ash",
            "玻璃": "glass",
            "黄金": "gold",
            "白银": "silver",
            "原油产业链": "crude_oil_chain",
            "铜产业链": "copper_chain",
            "大豆产业链": "soybean_chain",
            "钢铁产业链": "steel_chain",
            "煤化工产业链": "coal_chemical_chain"
        }
    
    def fetch_commodity_data(
        self,
        commodity_or_chain: str,
        time_range: Optional[dict] = None
    ) -> RawEvidence:
        """
        采集大宗商品数据
        
        Args:
            commodity_or_chain: 品种或产业链名称
            time_range: 时间范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
        
        Returns:
            RawEvidence: 原始证据包
        """
        print(f"[数据采集] 开始采集数据: {commodity_or_chain}")
        
        try:
            supply_chain = self._fetch_supply_chain(commodity_or_chain)
            prices = self._fetch_prices(commodity_or_chain, time_range)
            news = self._fetch_news(commodity_or_chain, time_range)
            
            raw_evidence = RawEvidence(
                supply_chain=supply_chain,
                prices=prices,
                news=news,
                fetched_at=datetime.now().isoformat(),
                commodity_or_chain=commodity_or_chain,
                time_range=time_range
            )
            
            print(f"[数据采集] 采集完成: 供给链{len(supply_chain)}条, 价格{len(prices)}条, 新闻{len(news)}条")
            return raw_evidence
            
        except Exception as e:
            print(f"[数据采集] 采集失败: {str(e)}")
            raise
    
    def _fetch_supply_chain(self, commodity: str) -> List[SupplyNode]:
        """采集供给链数据"""
        print(f"[数据采集] 采集供给链数据: {commodity}")
        
        supply_chain = []
        
        try:
            supply_chain.append(SupplyNode(
                region="全球",
                commodity_id=commodity,
                capacity_or_output=self._get_mock_capacity(commodity),
                inventory=self._get_mock_inventory(commodity),
                trade_flow=self._get_mock_trade_flow(commodity),
                key_entities_ports=self._get_mock_entities(commodity),
                source_url="",
                source_name="模拟数据",
                as_of_date=datetime.now().strftime("%Y-%m-%d")
            ))
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[数据采集] 供给链采集失败: {str(e)}")
        
        return supply_chain
    
    def _fetch_prices(
        self,
        commodity: str,
        time_range: Optional[dict] = None
    ) -> List[PricePoint]:
        """采集价格数据"""
        print(f"[数据采集] 采集价格数据: {commodity}")
        
        prices = []
        
        try:
            # 优先使用真实数据源
            if REAL_DATA_AVAILABLE:
                print(f"[数据采集] 尝试使用真实数据源...")
                real_prices = self._fetch_real_prices(commodity, time_range)
                if real_prices:
                    print(f"[数据采集] 真实数据获取成功: {len(real_prices)} 条")
                    return real_prices
                else:
                    print(f"[数据采集] 真实数据获取失败，使用模拟数据")
            
            # 使用模拟数据作为备选
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            if time_range:
                start_date = datetime.strptime(time_range["start"], "%Y-%m-%d")
                end_date = datetime.strptime(time_range["end"], "%Y-%m-%d")
            
            current_date = start_date
            while current_date <= end_date:
                price = self._get_mock_price(commodity, current_date)
                prices.append(price)
                current_date += timedelta(days=1)
                
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[数据采集] 价格采集失败: {str(e)}")
        
        return prices
    
    def _fetch_real_prices(
        self,
        commodity: str,
        time_range: Optional[dict] = None
    ) -> Optional[List[PricePoint]]:
        """从真实数据源获取价格数据"""
        try:
            # 品种名称到期货合约代码的映射
            # 注意：使用主力连续合约代码（品种代码 + "0"）
            # 主力连续合约代码格式：SC0、RB0、MA0 等
            commodity_to_futures = {
                "原油": "SC0",      # 原油主力连续合约
                "甲醇": "MA0",      # 甲醇主力连续合约
                "PTA": "TA0",       # PTA主力连续合约
                "玉米": "C0",       # 玉米主力连续合约
                "螺纹钢": "RB0",    # 螺纹钢主力连续合约
                "铁矿": "I0",       # 铁矿石主力连续合约
                "铜": "CU0",        # 铜主力连续合约
                "铝": "AL0",        # 铝主力连续合约
                "锌": "ZN0",        # 锌主力连续合约
                "黄金": "AU0",      # 黄金主力连续合约
                "白银": "AG0",      # 白银主力连续合约
                "豆粕": "M0",       # 豆粕主力连续合约
                "豆油": "Y0",       # 豆油主力连续合约
                "大豆": "A0",       # 大豆主力连续合约
                "棉花": "CF0",      # 棉花主力连续合约
                "白糖": "SR0",      # 白糖主力连续合约
                "橡胶": "RU0",      # 橡胶主力连续合约
                "焦煤": "JM0",      # 焦煤主力连续合约
                "焦炭": "J0",       # 焦炭主力连续合约
                "热卷": "HC0",      # 热卷主力连续合约
                "PP": "PP0",        # PP主力连续合约
                "PVC": "V0",        # PVC主力连续合约
                "乙二醇": "EG0",    # 乙二醇主力连续合约
                "尿素": "UR0",      # 尿素主力连续合约
                "纯碱": "SA0",      # 纯碱主力连续合约
                "玻璃": "FG0",      # 玻璃主力连续合约
            }
            
            futures_code = commodity_to_futures.get(commodity)
            if not futures_code:
                print(f"[数据采集] 未找到品种 {commodity} 对应的期货合约代码")
                return None
            
            print(f"[数据采集] 尝试获取期货数据: {futures_code}")
            
            # 设置数据天数（增加到90天以包含更多数据）
            days = 90
            if time_range:
                start_date = datetime.strptime(time_range["start"], "%Y-%m-%d")
                end_date = datetime.strptime(time_range["end"], "%Y-%m-%d")
                # 将结束时间往后推5天，确保能获取到最新的交易日数据
                end_date_extended = end_date + timedelta(days=5)
                days = (end_date_extended - start_date).days + 1
                # 确保至少获取90天的数据
                days = max(days, 90)
                print(f"[数据采集] 用户设置的时间范围: {time_range['start']} 到 {time_range['end']}")
                print(f"[数据采集] 实际查询的时间范围: {time_range['start']} 到 {end_date_extended.strftime('%Y-%m-%d')} (往后推5天)")
            
            # 调用真实数据源
            df = fetch_futures_data(futures_code, days=days)
            
            # 如果主力合约代码失败，尝试查找当前主力合约
            if df is None or df.empty:
                print(f"[数据采集] 主力合约代码 {futures_code} 获取失败，尝试查找当前主力合约...")
                try:
                    import akshare as ak
                    # 获取主力合约列表
                    if hasattr(ak, 'futures_main_sina'):
                        main_contracts = ak.futures_main_sina()
                        if main_contracts is not None and not main_contracts.empty:
                            # 提取品种代码（去掉末尾的0）
                            product_code = futures_code[:-1] if futures_code.endswith('0') else futures_code[:2]
                            print(f"[数据采集] 查找品种 {product_code} 的主力合约...")
                            
                            # 匹配主力合约
                            matching = main_contracts[main_contracts['symbol'].str.contains(product_code, case=False, na=False)]
                            if not matching.empty:
                                main_symbol = matching.iloc[0]['symbol']
                                print(f"[数据采集] 找到主力合约: {main_symbol}")
                                df = fetch_futures_data(main_symbol, days=days)
                except Exception as e:
                    print(f"[数据采集] 查找主力合约失败: {e}")
            
            if df is None or df.empty:
                print(f"[数据采集] 真实数据源返回空数据")
                return None
            
            # 获取实际的数据截止时间
            actual_end_date = df['日期'].max()
            actual_start_date = df['日期'].min()
            print(f"[数据采集] 实际获取的数据范围: {actual_start_date.strftime('%Y-%m-%d')} 到 {actual_end_date.strftime('%Y-%m-%d')}")
            print(f"[数据采集] 数据条数: {len(df)}")
            
            # 转换为 PricePoint 格式
            prices = []
            for _, row in df.iterrows():
                date_str = row['日期'].strftime('%Y-%m-%d') if isinstance(row['日期'], datetime) else str(row['日期'])
                prices.append({
                    "commodity_id": commodity,
                    "market_or_contract": futures_code,
                    "price_type": "future",
                    "value": float(row['收盘']),
                    "high": float(row['最高']) if '最高' in row and pd.notna(row['最高']) else None,
                    "low": float(row['最低']) if '最低' in row and pd.notna(row['最低']) else None,
                    "open": float(row['开盘']) if '开盘' in row and pd.notna(row['开盘']) else None,
                    "volume": float(row['成交量']) if '成交量' in row and pd.notna(row['成交量']) else None,
                    "unit": "元/吨",
                    "as_of_date": date_str,
                    "source_url": "",
                    "source_name": "真实数据源"
                })
            
            print(f"[数据采集] 返回 {len(prices)} 条价格数据")
            if prices:
                latest = prices[-1]
                print(f"[数据采集] 最新数据: 日期={latest['as_of_date']}, 收盘={latest['value']}, 最高={latest.get('high')}, 最低={latest.get('low')}")
            return prices
            
        except Exception as e:
            print(f"[数据采集] 真实数据源获取失败: {str(e)}")
            import traceback
            print(f"[数据采集] 错误详情: {traceback.format_exc()}")
            return None
    
    def _fetch_news(
        self,
        commodity: str,
        time_range: Optional[dict] = None
    ) -> List[NewsItem]:
        """采集新闻数据"""
        print(f"[数据采集] 采集新闻数据: {commodity}")
        
        news_list = []
        
        try:
            news_items = self._get_mock_news(commodity)
            news_list.extend(news_items)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[数据采集] 新闻采集失败: {str(e)}")
        
        return news_list
    
    def _get_mock_capacity(self, commodity: str) -> float:
        """获取模拟产能数据（万吨/年）"""
        capacities = {
            # 能源化工
            "原油": 100000,  # 国内原油产量
            "甲醇": 9000,
            "PTA": 7000,
            "PP": 3500,
            "PVC": 2800,
            "乙二醇": 2000,
            "尿素": 7000,
            "纯碱": 3000,
            "玻璃": 100000,
            # 有色金属
            "铜": 1000,
            "铝": 4000,
            "锌": 600,
            "铅": 500,
            "镍": 100,
            "锡": 15,
            # 黑色系
            "铁矿": 100000,  # 国内产量
            "焦煤": 50000,
            "焦炭": 45000,
            "螺纹钢": 30000,
            # 农产品
            "大豆": 2000,  # 国内产量
            "玉米": 27000,
            "小麦": 13000,
            "棉花": 600,
            "白糖": 1000
        }
        return capacities.get(commodity, 10000)
    
    def _get_mock_inventory(self, commodity: str) -> float:
        """获取模拟库存数据（万吨）"""
        inventories = {
            # 能源化工
            "原油": 5000,
            "甲醇": 100,
            "PTA": 200,
            "PP": 50,
            "PVC": 30,
            "乙二醇": 80,
            "尿素": 150,
            "纯碱": 50,
            "玻璃": 3000,
            # 有色金属
            "铜": 20,
            "铝": 80,
            "锌": 15,
            "铅": 10,
            "镍": 2,
            "锡": 0.5,
            # 黑色系
            "铁矿": 12000,
            "焦煤": 800,
            "焦炭": 600,
            "螺纹钢": 500,
            # 农产品
            "大豆": 600,
            "玉米": 5000,
            "小麦": 3000,
            "棉花": 100,
            "白糖": 200
        }
        return inventories.get(commodity, 100)
    
    def _get_mock_trade_flow(self, commodity: str) -> str:
        """获取模拟贸易流向"""
        flows = {
            # 能源化工
            "原油": "中东→中国",
            "甲醇": "西北→华东",
            "PTA": "华东→全国",
            "PP": "西北→华东",
            "PVC": "西北→华东",
            "乙二醇": "华东港口→全国",
            "尿素": "山西→全国",
            "纯碱": "西北→华东",
            "玻璃": "华北→全国",
            # 有色金属
            "铜": "南美→中国",
            "铝": "西北→华东",
            "锌": "云南→全国",
            "铅": "河南→全国",
            "镍": "印尼→中国",
            "锡": "云南→全国",
            # 黑色系
            "铁矿": "澳大利亚→中国",
            "焦煤": "山西→河北",
            "焦炭": "山西→河北",
            "螺纹钢": "河北→全国",
            # 农产品
            "大豆": "南美→中国",
            "玉米": "东北→南方",
            "小麦": "华北→全国",
            "棉花": "新疆→全国",
            "白糖": "广西→全国"
        }
        return flows.get(commodity, "国内贸易")
    
    def _get_mock_entities(self, commodity: str) -> List[str]:
        """获取模拟主要企业/港口"""
        entities = {
            # 能源化工
            "原油": ["中石油", "中石化", "中海油"],
            "甲醇": ["神华集团", "兖矿集团", "久泰集团"],
            "PTA": ["恒力石化", "荣盛石化", "桐昆股份"],
            "PP": ["中石化", "神华集团", "中石油"],
            "PVC": ["中泰化学", "新疆天业", "君正集团"],
            "乙二醇": ["恒力石化", "荣盛石化", "浙石化"],
            "尿素": ["云天化", "阳煤化工", "华鲁恒升"],
            "纯碱": ["山东海化", "三友化工", "远兴能源"],
            "玻璃": ["信义玻璃", "旗滨集团", "南玻集团"],
            # 有色金属
            "铜": ["江西铜业", "铜陵有色", "云南铜业"],
            "铝": ["中国铝业", "神火股份", "云铝股份"],
            "锌": ["驰宏锌锗", "中金岭南", "株冶集团"],
            "铅": ["豫光金铅", "驰宏锌锗", "中金岭南"],
            "镍": ["青山集团", "金川集团", "中伟股份"],
            "锡": ["云南锡业", "广西华锡", "五矿稀土"],
            # 黑色系
            "铁矿": ["淡水河谷", "力拓", "必和必拓"],
            "焦煤": ["山西焦煤", "平煤股份", "开滦股份"],
            "焦炭": ["山西焦化", "美锦能源", "陕西黑猫"],
            "螺纹钢": ["宝钢", "河钢", "沙钢"],
            # 农产品
            "大豆": ["中粮集团", "益海嘉里", "九三集团"],
            "玉米": ["中粮集团", "北大荒", "象屿集团"],
            "小麦": ["中粮集团", "中储粮", "五得利"],
            "棉花": ["中棉集团", "新疆利华", "中华棉花"],
            "白糖": ["中粮糖业", "南宁糖业", "广东糖业"]
        }
        return entities.get(commodity, ["主要企业"])
    
    def _get_mock_price(self, commodity: str, date: datetime) -> PricePoint:
        """获取模拟价格数据"""
        # 基础价格配置（单位：元/吨 或 美元/桶）
        base_prices = {
            # 能源化工（元/吨）
            "原油": 5500.0,  # 国内原油期货
            "布伦特": 80.0,  # 美元/桶
            "WTI": 72.0,    # 美元/桶
            "甲醇": 2500.0,
            "PTA": 6000.0,
            "PP": 8000.0,
            "PVC": 6500.0,
            "乙二醇": 4500.0,
            "尿素": 2300.0,
            "纯碱": 1800.0,
            "玻璃": 1500.0,
            # 有色金属（元/吨）
            "铜": 68000.0,
            "铝": 18500.0,
            "锌": 22000.0,
            "铅": 16000.0,
            "镍": 130000.0,
            "锡": 210000.0,
            # 黑色系（元/吨）
            "铁矿": 900.0,
            "焦煤": 1800.0,
            "焦炭": 2400.0,
            "螺纹钢": 3800.0,
            "热卷": 3900.0,
            # 农产品（元/吨）
            "大豆": 5200.0,
            "豆粕": 3500.0,
            "豆油": 8500.0,
            "玉米": 2389.0,  # 使用用户提供的真实价格
            "小麦": 2800.0,
            "棉花": 15500.0,
            "白糖": 6200.0,
            "橡胶": 13000.0,
            # 贵金属（元/克）
            "黄金": 480.0,
            "白银": 6.0
        }
        
        # 单位配置
        unit_config = {
            # 美元/桶（国际原油）
            "布伦特": "美元/桶",
            "WTI": "美元/桶",
            # 元/克（贵金属）
            "黄金": "元/克",
            "白银": "元/克",
            # 其他品种默认元/吨
        }
        
        base_price = base_prices.get(commodity, 100.0)
        unit = unit_config.get(commodity, "元/吨")
        
        import random
        variation = random.uniform(-0.05, 0.05)
        price = base_price * (1 + variation)
        
        return PricePoint(
            commodity_id=commodity,
            market_or_contract="主力合约",
            price_type="future",
            value=round(price, 2),
            unit=unit,
            as_of_date=date.strftime("%Y-%m-%d"),
            source_url="",
            source_name="模拟数据"
        )
    
    def _get_mock_news(self, commodity: str) -> List[NewsItem]:
        """获取模拟新闻数据"""
        news_templates = {
            # 能源化工
            "原油": [
                "OPEC+会议讨论减产计划",
                "美国原油库存意外下降",
                "地缘政治紧张局势升级",
                "全球需求预期上调"
            ],
            "甲醇": [
                "甲醇装置检修计划公布",
                "下游MTO需求稳定",
                "港口库存小幅下降",
                "煤炭价格影响甲醇成本"
            ],
            "PTA": [
                "PTA装置开工率下降",
                "聚酯需求回暖",
                "原油价格波动影响成本",
                "新产能投放预期"
            ],
            # 有色金属
            "铜": [
                "智利铜矿产量下降",
                "中国制造业PMI超预期",
                "新能源需求推动铜价上涨",
                "全球铜供应紧张"
            ],
            "铝": [
                "电解铝产能受限",
                "汽车轻量化需求增加",
                "电力成本支撑铝价",
                "环保政策影响供应"
            ],
            # 黑色系
            "铁矿": [
                "澳大利亚发货量下降",
                "钢厂补库需求增加",
                "港口库存持续下降",
                "四大矿山产量调整"
            ],
            "螺纹钢": [
                "基建投资增速提升",
                "房地产政策放松",
                "钢厂利润改善",
                "环保限产影响供应"
            ],
            # 农产品
            "大豆": [
                "南美大豆产量预期下调",
                "中国大豆进口增加",
                "天气影响大豆种植",
                "大豆压榨利润改善"
            ],
            "玉米": [
                "东北地区玉米播种进度",
                "饲料需求稳定增长",
                "临储玉米拍卖成交",
                "深加工企业收购价格调整"
            ],
            # 贵金属
            "黄金": [
                "美联储加息预期降温",
                "避险需求推动金价",
                "美元指数走弱",
                "全球央行购金需求增加"
            ]
        }
        
        titles = news_templates.get(commodity, [
            f"{commodity}市场分析",
            f"{commodity}供需关系变化",
            f"{commodity}价格走势"
        ])
        
        news_list = []
        for i, title in enumerate(titles):
            news_list.append(NewsItem(
                title=title,
                summary=f"{title}，市场关注度较高。",
                source_name="财经新闻",
                source_url="",
                published_at=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                related_commodities=[commodity],
                related_regions=["全球"],
                tags=["supply_demand"]
            ))
        
        return news_list


def create_commodity_fetcher() -> CommodityFetcher:
    """创建商品数据采集器实例"""
    return CommodityFetcher()
