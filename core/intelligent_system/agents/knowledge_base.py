"""
博弈理论知识库模块

存储和管理博弈交易法的核心知识，包括：
- 五阶段理论
- 洗盘识别理论
- 出货识别理论
- 历史案例
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
import json

logger = logging.getLogger(__name__)


class BoyiKnowledgeBase:
    """
    博弈理论知识库
    
    使用ChromaDB作为向量数据库，存储和检索博弈理论知识
    """
    
    def __init__(self, persist_dir: str = "./data/chroma"):
        """
        初始化知识库
        
        Args:
            persist_dir: ChromaDB数据持久化目录
        """
        self.persist_dir = persist_dir
        
        # 初始化向量数据库
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="boyi_knowledge",
            metadata={"description": "博弈交易法知识库"}
        )
        
        # 初始化核心知识
        self._initialize_knowledge()
        
        logger.info(f"知识库初始化完成，当前包含 {self.collection.count()} 条知识")
    
    def _initialize_knowledge(self):
        """初始化博弈理论核心知识"""
        
        # 如果知识库为空，则初始化
        if self.collection.count() == 0:
            logger.info("初始化博弈理论核心知识...")
            
            knowledge_docs = [
                # ===== 一阶段知识 =====
                {
                    "id": "phase_1_definition",
                    "type": "阶段理论",
                    "title": "一阶段：趋势形成初期",
                    "content": """
一阶段是趋势形成初期，具有以下核心特征：

1. 起始点：始于O点（原始低点），O点是上一轮熊市结束时的最低点

2. 价格特征：
   - 缓慢且隐蔽的上涨
   - 偶有大阳线或涨停，但出现后必须立刻掉头猛跌
   - 整体形态难看，消磨散户意志

3. 情绪比例关系：
   - 较为好看的出货 + 非常难看的洗盘
   - 洗盘效果要好，让散户感到恐惧和绝望

4. 作用：
   - 消磨散户的持股意志
   - 产生极度悲观的情绪
   - 让散户不敢买入

5. 操作要领：
   - 杀跌入场，谨防破位，严禁追高
   - 分仓操作：最多买入三分之一仓位
   - 长期持有，避免高抛低吸
   - 一阶段结束时加仓

6. 一阶段结束标志：
   - 连续出现洗盘高点
   - 创新高
   - 情绪比例关系合格

7. 牛股结构判断：
   - O点确认明确
   - 情绪比例关系合格后继续洗盘
   - 形态形成后大概率上涨
""",
                    "keywords": ["一阶段", "趋势形成", "O点", "缓慢上涨", "洗盘"]
                },
                
                # ===== 二阶段知识 =====
                {
                    "id": "phase_2_definition",
                    "type": "阶段理论",
                    "title": "二阶段：快速上涨阶段",
                    "content": """
二阶段是市场上涨幅度最大的阶段，具有以下核心特征：

1. 价格特征：
   - 突然大幅拉升，使散户错过低位布局机会
   - 高位运行，趋势结束前不会再现低位价格
   - 快速上涨并在高位长期维持
   - 伴随持续洗盘

2. 洗盘特征：
   - 上涨过程中散户买的少，场内散户数量稀少
   - 形态难看，但上涨持续
   - 洗盘出货比例关系合理（牛股结构）

3. 操作策略：
   - 在洗盘时入场
   - 上涨-洗盘-再上涨-再洗盘的循环模式
   - 洗盘时加仓，上涨时持有

4. 牛股结构判断：
   - 上涨过程中没有明显的大规模出货高点
   - 上涨过程中没有形成多方锚定
   - 下跌过程中形成了空方锚定
   - 严格控制上涨时的憧憬情绪，洗盘时制造绝望情绪

5. 关键指标：
   - 洗盘效果评分
   - 场内散户数量估计
   - 多空锚定判断
""",
                    "keywords": ["二阶段", "快速上涨", "洗盘", "牛股结构", "空方锚定"]
                },
                
                # ===== 三阶段知识 =====
                {
                    "id": "phase_3_definition",
                    "type": "阶段理论",
                    "title": "三阶段：疯狂阶段",
                    "content": """
三阶段是疯狂上涨阶段，具有以下核心特征：

1. 价格特征：
   - 利用散户的贪婪和冲动情绪
   - 持续时间短，通常不超过三个月
   - 伴随象征性洗盘（浮皮潦草）
   - 必须借助大盘的上攻走势

2. 与二阶段的区别：
   - 二阶段有洗盘，三阶段没有或只有象征性洗盘
   - 二阶段持续时间长，三阶段持续时间短
   - 二阶段可以不借助大盘，三阶段必须借助大盘
   - 二阶段散户恐惧，三阶段散户贪婪

3. 操作策略：
   - 及时止盈离场，避免深套
   - 一旦确认三阶段，开始减仓
   - 不要追高买入

4. 风险提示：
   - 散户情绪高涨，贪婪心理主导
   - 洗盘失效，股价上涨乏力
   - 随时可能进入四阶段猛烈下跌
""",
                    "keywords": ["三阶段", "疯狂上涨", "散户贪婪", "无洗盘", "大盘配合"]
                },
                
                # ===== 四五阶段知识 =====
                {
                    "id": "phase_4_5_definition",
                    "type": "阶段理论",
                    "title": "四阶段和五阶段：下跌阶段",
                    "content": """
四阶段和五阶段是下跌阶段：

【四阶段：猛烈下跌】
1. 特征：
   - 猛烈下跌，套住散户
   - 下跌速度快且幅度大
   - 散户账面浮亏最多

2. 作用：
   - 主力通过散户高位买入低位卖出实现盈利

3. 操作策略：
   - 立即止损离场
   - 空仓观望，不抄底
   - 保留资金等待下一轮机会

【五阶段：漫长阴跌】
1. 特征：
   - 长期阴跌
   - 消磨投资者意志
   - 散户群体一致看跌

2. 作用：
   - 让抄底者再次被套
   - 消磨场内投资者的意志
   - 使散户不敢轻易入场做反弹

3. 操作策略：
   - 不抄底，不补仓
   - 等待新的O点出现
   - 资金退出市场或做短线
""",
                    "keywords": ["四阶段", "五阶段", "猛烈下跌", "阴跌", "止损"]
                },
                
                # ===== 洗盘理论 =====
                {
                    "id": "washing_theory",
                    "type": "洗盘理论",
                    "title": "洗盘识别理论",
                    "content": """
洗盘定义：主力通过控制股票走势，使散户止盈或止损离场。

核心目标：里面的散户都出去，外面的散户别进来。

【洗盘公式】
洗盘效果 = f(恐惧程度, 焦虑程度, 场内散户数量)

1. 恐惧程度：
   - K线形态的难看程度
   - 下跌幅度和速度
   - 破位次数
   - 媒体负面情绪

2. 焦虑程度：
   - 洗盘持续时间越长，焦虑越大
   - 反复震荡次数
   - 反复跌破支撑位

3. 场内散户数量：
   - 成交量萎缩
   - 持仓集中度提高

【洗盘类型】

1. K线组合洗盘：
   - 第一根K线：明确告诉散户上涨有压力
   - 第二根K线：继续提醒上涨有阻力
   - 第三根K线：确认上涨乏力

2. 波段洗盘：
   - 没有分水岭的高点作为洗盘开端
   - 下跌过程中没有钩子
   - 需要借助大盘下跌

【洗盘结束信号】
- 成交量萎缩到极致
- 跌幅收敛，不再创新低
- 出现止跌形态（十字星、锤子线）
- 资金流向开始改善
- 大盘配合转好
""",
                    "keywords": ["洗盘", "恐惧程度", "焦虑程度", "K线组合", "波段洗盘"]
                },
                
                # ===== 出货理论 =====
                {
                    "id": "distribution_theory",
                    "type": "出货理论",
                    "title": "出货识别理论",
                    "content": """
出货定义：主力在高位将筹码卖给散户，实现盈利。

【大规模出货】
1. 特征：
   - 洗盘时间：一年以上
   - 必须打广告，吸引所有散户投资者
   - 针对：五大门派（突破派、抄底派、激进派、趋势派、博弈派）

2. 操作建议：
   - 识别后一年内不做中线和长线投资
   - 仅做短线操作

【中等规模出货】
1. 特征：
   - 洗盘时间：三至六个月
   - 不考虑所有散户，只针对突破派

2. 操作建议：
   - 洗盘三个月后直接上涨
   - 入场5%资金作为底仓
   - 等待下跌后加仓10%-15%

【小规模出货】
1. 特征：
   - 洗盘时间：三个月以内
   - 买入的人少且种类少

2. 操作建议：
   - 在洗盘过程中逐步买入
   - 持续加仓

【出货识别方法】
1. 形态特征：高位横盘或震荡，成交量持续放大，出现漂亮的K线形态
2. 资金流向：主力资金持续流出，散户资金持续流入
3. 情绪指标：媒体正面报道增多，散户讨论热度高涨
4. 博弈逻辑：洗盘时间长短，广告效应明显度
""",
                    "keywords": ["出货", "大规模出货", "中等出货", "小规模出货", "五大门派"]
                },
                
                # ===== O点理论 =====
                {
                    "id": "o_point_theory",
                    "type": "核心概念",
                    "title": "O点（原始低点）理论",
                    "content": """
O点定义：上一轮熊市结束时的最低点，本轮上升趋势的原始低点。

【识别方法】
1. 前期持续下跌后的最低点
2. 成交量明显萎缩
3. 之后股价不再创新低

【特征】
1. 趋势力量在O点初现时微弱，仅能防止股价跌破
2. O点是趋势的起点
3. O点确认后，股票进入一阶段

【操作意义】
1. 中线建仓的起点
2. 止损位参考
3. 趋势判断的基准点

【注意事项】
1. O点需要时间确认，不是最低点当天就能确定
2. 需要观察后续走势是否不再创新低
3. 成交量配合是重要验证
""",
                    "keywords": ["O点", "原始低点", "趋势起点", "熊市终点"]
                },
                
                # ===== 趋势理论 =====
                {
                    "id": "trend_theory",
                    "type": "核心概念",
                    "title": "趋势理论",
                    "content": """
趋势定义：一种无形的力量，推动市场或股票长期朝着某个方向运行。
趋势本质：推动K线上涨的力量。

【趋势五种特性】

1. 隐蔽性：
   - 无法直接看到，只能通过K线长期走势判断
   - 需要长期观察确认

2. 周期性：
   - 一至五阶段循环往复
   - 如同一年四季

3. 长期性：
   - 一旦来临就会持续一段时间
   - 不急于下车

4. 稳定性：
   - 一旦存在，不会轻易结束
   - 趋势中坚定持有

5. 嵌套性：
   - 大周期套小周期
   - 完整牛熊轮中包含更小级别的趋势

【趋势判断应用】

短线投资者：
- 有趋势时：扩大盈利预期
- 无趋势时：缩小盈利预期

中长线投资者：
- 有趋势时：操作
- 无趋势时：休息
""",
                    "keywords": ["趋势", "隐蔽性", "周期性", "长期性", "稳定性", "嵌套性"]
                },
                
                # ===== 情绪比例关系 =====
                {
                    "id": "emotion_ratio",
                    "type": "核心概念",
                    "title": "情绪比例关系",
                    "content": """
情绪比例关系定义：股票的涨跌波动过程可以改变事先判定的结果，过程比结果更重要。

【核心原则】
过程可以改变结果，注重过程比注重结果更重要。

【应用原则】

1. 看涨信号：
   - 较为好看的出货 + 非常难看的洗盘
   - 散户在出货时愿意买入，在洗盘时恐慌卖出

2. 看跌信号：
   - 较为难看的洗盘 + 非常好看的出货
   - 散户在洗盘时恐慌卖出，在出货时愿意买入

【重要性】
情绪比例关系是精英投资者与普通高手的差别所在。

【判断标准】
1. 出货的"好看程度"：
   - K线形态漂亮
   - 涨幅诱人
   - 媒体正面报道

2. 洗盘的"难看程度"：
   - K线形态恐怖
   - 跌幅大
   - 媒体负面报道
""",
                    "keywords": ["情绪比例关系", "出货好看", "洗盘难看", "过程比结果重要"]
                },
                
                # ===== 锚定理论 =====
                {
                    "id": "anchoring_theory",
                    "type": "核心概念",
                    "title": "多方锚定与空方锚定",
                    "content": """
【多方锚定】
定义：主力在拉升过程中，通过特定的K线形态和走势，将散户思维锚定在多头阵营。

特征：
- 散户投资者一致看多
- 阳线个头越来越大
- 散户越来越愿意买入

应用：
- 多方锚定形成后：买入信号
- 多方锚定被破坏后：朝空头方向运行时加仓信号

【空方锚定】
定义：将散户投资者思维固定在空方阵营，在上涨行情中保持散户空头思维。

方法：
- 下跌初期恐怖性下跌
- 持续补空锚，使散户回想起上一轮下跌的恐惧感

应用：
- 空方锚定形成后，主力可能在酝酿大行情
- 在空方锚定期间买入，等待主力拉升

【锚定与牛股结构】
- 二阶段牛股结构：上涨不形成多方锚定，下跌形成空方锚定
- 这样可以保持散户空头思维，便于后续拉升
""",
                    "keywords": ["多方锚定", "空方锚定", "散户思维", "牛股结构"]
                }
            ]
            
            # 批量添加知识
            for doc in knowledge_docs:
                self.add_knowledge(
                    knowledge_id=doc["id"],
                    knowledge_type=doc["type"],
                    title=doc["title"],
                    content=doc["content"],
                    keywords=doc["keywords"]
                )
            
            logger.info(f"初始化完成，添加了 {len(knowledge_docs)} 条核心知识")
    
    def add_knowledge(
        self,
        knowledge_id: str,
        knowledge_type: str,
        title: str,
        content: str,
        keywords: List[str] = None
    ):
        """
        添加知识到知识库
        
        Args:
            knowledge_id: 知识ID
            knowledge_type: 知识类型（阶段理论/洗盘理论/出货理论/核心概念）
            title: 知识标题
            content: 知识内容
            keywords: 关键词列表
        """
        # 生成嵌入向量
        embedding = self.embedding_model.encode(content).tolist()
        
        # 添加到向量数据库
        self.collection.add(
            ids=[knowledge_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "type": knowledge_type,
                "title": title,
                "keywords": json.dumps(keywords or [], ensure_ascii=False)
            }]
        )
        
        logger.info(f"添加知识: {title}")
    
    def query_knowledge(
        self,
        query_text: str,
        n_results: int = 3
    ) -> List[Dict]:
        """
        查询相关知识
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
        
        Returns:
            相关知识列表
        """
        # 生成查询向量
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        # 向量相似度搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # 格式化结果
        knowledge_list = []
        for i in range(len(results['ids'][0])):
            knowledge_list.append({
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return knowledge_list
    
    def get_knowledge_by_type(self, knowledge_type: str) -> List[Dict]:
        """
        按类型获取知识
        
        Args:
            knowledge_type: 知识类型
        
        Returns:
            该类型的知识列表
        """
        results = self.collection.get(
            where={"type": knowledge_type}
        )
        
        knowledge_list = []
        for i in range(len(results['ids'])):
            knowledge_list.append({
                "id": results['ids'][i],
                "content": results['documents'][i],
                "metadata": results['metadatas'][i]
            })
        
        return knowledge_list


# 创建全局知识库实例
_knowledge_base: Optional[BoyiKnowledgeBase] = None


def get_knowledge_base() -> BoyiKnowledgeBase:
    """获取知识库实例（单例）"""
    global _knowledge_base
    
    if _knowledge_base is None:
        from core.intelligent_system.config import settings
        _knowledge_base = BoyiKnowledgeBase(
            persist_dir=settings.CHROMA_PERSIST_DIR
        )
    
    return _knowledge_base
