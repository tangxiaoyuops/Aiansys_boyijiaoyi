"""
五阶段分析Agent

使用LangChain和GPT-4实现智能化的阶段识别分析
"""

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime

from core.intelligent_system.agents.knowledge_base import get_knowledge_base
from core.intelligent_system.database.db_manager import get_db_manager

logger = logging.getLogger(__name__)


class PhaseAnalysisAgent:
    """
    五阶段分析Agent
    
    核心能力：
    1. 理解博弈理论中每个阶段的核心特征
    2. 多维度数据分析（价格、成交量、形态、情绪）
    3. 推理判断股票当前所处阶段
    4. 提供详细的分析依据和置信度
    """
    
    def __init__(
        self,
        openai_api_key: str,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7
    ):
        """
        初始化Agent
        
        Args:
            openai_api_key: OpenAI API密钥
            model_name: 模型名称
            temperature: 温度参数
        """
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model_name,
            temperature=temperature
        )
        
        # 获取知识库
        self.knowledge_base = get_knowledge_base()
        
        # 设置工具
        self.tools = self._setup_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        logger.info("PhaseAnalysisAgent初始化完成")
    
    def _setup_tools(self) -> List[Tool]:
        """设置Agent可用的工具"""
        
        tools = [
            Tool(
                name="query_knowledge",
                func=self._query_knowledge,
                description="查询博弈理论知识库，获取五阶段理论、洗盘理论、出货理论等核心知识"
            ),
            Tool(
                name="analyze_kline_pattern",
                func=self._analyze_kline_pattern,
                description="分析K线形态，识别关键形态（O点、洗盘、出货、锚定）"
            ),
            Tool(
                name="calculate_technical_indicators",
                func=self._calculate_technical_indicators,
                description="计算技术指标（均线、MACD、成交量等）"
            ),
            Tool(
                name="analyze_trend_strength",
                func=self._analyze_trend_strength,
                description="分析趋势强度，判断趋势是否存在"
            )
        ]
        
        return tools
    
    def _create_agent(self):
        """创建Agent"""
        
        system_prompt = """你是一位精通博弈交易法的专业分析师。

你的核心任务是：分析股票当前所处的阶段（一阶段至五阶段）。

## 博弈理论核心知识：

你可以通过query_knowledge工具查询以下知识：
- 五阶段理论（一阶段、二阶段、三阶段、四阶段、五阶段）
- 洗盘识别理论
- 出货识别理论
- O点理论
- 趋势理论
- 情绪比例关系
- 锚定理论

## 分析框架：

### 阶段判断流程：

1. **数据获取**：
   - 获取K线数据（至少60个交易日）
   - 计算技术指标
   - 分析成交量变化

2. **O点识别**：
   - 寻找最低点后不再创新低的位置
   - 确认O点的价格和日期
   - 验证成交量萎缩

3. **趋势分析**：
   - 判断趋势是否存在
   - 计算趋势强度
   - 评估趋势稳定性

4. **形态识别**：
   - 识别洗盘形态
   - 识别出货形态
   - 判断锚定类型

5. **情绪分析**：
   - 计算情绪比例关系
   - 评估恐惧程度
   - 评估焦虑程度

6. **综合判断**：
   - 结合博弈理论
   - 多维度推理
   - 给出阶段判断

## 分析要求：

你的分析结果必须包含：

1. **阶段判断**：明确指出当前处于哪个阶段
   - 一阶段：趋势形成初期
   - 二阶段：快速上涨阶段
   - 三阶段：疯狂阶段
   - 四阶段：猛烈下跌阶段
   - 五阶段：漫长阴跌阶段

2. **关键特征**：列出支撑判断的关键特征（至少3个）

3. **O点信息**：
   - O点价格
   - O点日期
   - 确认依据

4. **趋势状态**：
   - 趋势是否存在
   - 趋势强度（弱/中/强）
   - 趋势稳定性

5. **情绪比例**：
   - 出货好看程度（0-10分）
   - 洗盘难看程度（0-10分）
   - 情绪比例关系判断

6. **判断依据**：详细解释为什么做出这个判断（至少100字）

7. **置信度**：0-100%的置信度评分

8. **风险提示**：可能存在的误判风险

请使用工具获取数据，进行系统性分析，不要凭空猜测。

输出格式要求使用JSON。
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10
        )
    
    # ========== 工具函数 ==========
    
    def _query_knowledge(self, query: str) -> str:
        """查询知识库"""
        results = self.knowledge_base.query_knowledge(query, n_results=3)
        
        knowledge_text = ""
        for i, result in enumerate(results, 1):
            knowledge_text += f"\n【知识{i}】{result['metadata']['title']}\n"
            knowledge_text += f"{result['content']}\n"
        
        return knowledge_text
    
    def _analyze_kline_pattern(self, kline_data: str) -> str:
        """分析K线形态"""
        try:
            # 解析数据
            data = json.loads(kline_data)
            df = pd.DataFrame(data)
            
            # 识别关键形态
            patterns = {
                "highest_price": df['high'].max(),
                "lowest_price": df['low'].min(),
                "avg_volume": df['volume'].mean(),
                "price_change": (df['close'].iloc[0] - df['close'].iloc[-1]) / df['close'].iloc[-1] * 100
            }
            
            # 识别O点
            o_point_idx = df['low'].idxmin()
            o_point = {
                "price": df.loc[o_point_idx, 'low'],
                "date": df.loc[o_point_idx, 'time'],
                "volume": df.loc[o_point_idx, 'volume']
            }
            
            # 检查O点后是否创新低
            after_o_point = df.loc[o_point_idx:]
            new_low = after_o_point['low'].min() < o_point['price']
            
            patterns['o_point'] = o_point
            patterns['o_point_confirmed'] = not new_low
            
            return json.dumps(patterns, ensure_ascii=False)
            
        except Exception as e:
            return f"K线形态分析失败: {str(e)}"
    
    def _calculate_technical_indicators(self, kline_data: str) -> str:
        """计算技术指标"""
        try:
            data = json.loads(kline_data)
            df = pd.DataFrame(data)
            
            # 计算均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma60'] = df['close'].rolling(window=60).mean()
            
            # 计算成交量均线
            df['vol_ma5'] = df['volume'].rolling(window=5).mean()
            df['vol_ma10'] = df['volume'].rolling(window=10).mean()
            
            # 获取最新值
            latest = df.iloc[0]
            
            indicators = {
                "close": latest['close'],
                "ma5": latest['ma5'],
                "ma10": latest['ma10'],
                "ma20": latest['ma20'],
                "ma60": latest['ma60'],
                "volume": latest['volume'],
                "vol_ma5": latest['vol_ma5'],
                "vol_ma10": latest['vol_ma10'],
                "volume_ratio": latest['volume'] / latest['vol_ma5'] if latest['vol_ma5'] > 0 else 0,
                "price_position": "above_ma20" if latest['close'] > latest['ma20'] else "below_ma20"
            }
            
            return json.dumps(indicators, ensure_ascii=False)
            
        except Exception as e:
            return f"技术指标计算失败: {str(e)}"
    
    def _analyze_trend_strength(self, kline_data: str) -> str:
        """分析趋势强度"""
        try:
            data = json.loads(kline_data)
            df = pd.DataFrame(data)
            
            # 计算价格变化率
            df['return'] = df['close'].pct_change()
            
            # 计算趋势强度
            # 使用移动平均线的斜率
            df['ma20_slope'] = df['ma20'].diff() / df['ma20'].shift(1)
            
            # 平均斜率
            avg_slope = df['ma20_slope'].mean()
            
            # 趋势判断
            if avg_slope > 0.01:
                trend = "strong_up"
                strength = 80
            elif avg_slope > 0.005:
                trend = "up"
                strength = 60
            elif avg_slope > 0:
                trend = "weak_up"
                strength = 40
            elif avg_slope > -0.005:
                trend = "sideways"
                strength = 20
            else:
                trend = "down"
                strength = 0
            
            result = {
                "trend": trend,
                "strength": strength,
                "avg_slope": avg_slope,
                "volatility": df['return'].std()
            }
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            return f"趋势分析失败: {str(e)}"
    
    # ========== 主要分析接口 ==========
    
    async def analyze(
        self,
        stock_code: str,
        kline_data: List[Dict],
        additional_context: Dict = None
    ) -> Dict:
        """
        分析股票阶段
        
        Args:
            stock_code: 股票代码
            kline_data: K线数据列表
            additional_context: 额外上下文（大盘信息、板块信息等）
        
        Returns:
            分析结果字典
        """
        logger.info(f"开始分析股票 {stock_code}...")
        
        try:
            # 准备输入数据
            kline_json = json.dumps(kline_data, ensure_ascii=False)
            
            # 构建分析任务
            task = f"""
请分析股票 {stock_code} 当前所处的阶段。

K线数据（最近{len(kline_data)}个交易日）：
{kline_json[:5000]}  # 限制长度，避免超出token限制

市场背景：
{json.dumps(additional_context or {}, ensure_ascii=False)}

请按照以下步骤进行系统性分析：

1. 使用query_knowledge工具查询相关理论
2. 使用analyze_kline_pattern工具分析K线形态
3. 使用calculate_technical_indicators工具计算技术指标
4. 使用analyze_trend_strength工具分析趋势强度
5. 综合所有信息，进行阶段判断

请返回JSON格式的分析结果。
"""
            
            # Agent执行分析
            result = await self.agent.ainvoke({"input": task})
            
            # 解析结果
            output = result.get("output", "")
            
            # 尝试解析JSON
            try:
                analysis = json.loads(output)
            except:
                # 如果不是JSON，提取关键信息
                analysis = self._parse_analysis_result(output)
            
            # 保存到数据库
            db = await get_db_manager()
            await db.save_agent_analysis_result(
                stock_code=stock_code,
                analysis_type="phase_analysis",
                result=analysis,
                confidence=analysis.get('confidence', 0.0)
            )
            
            logger.info(f"分析完成: {stock_code} - {analysis.get('phase', '未知')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析失败 {stock_code}: {e}")
            return {
                "error": str(e),
                "phase": "分析失败",
                "confidence": 0
            }
    
    def _parse_analysis_result(self, output: str) -> Dict:
        """解析非JSON格式的分析结果"""
        
        # 简单的关键词提取
        phase = "未知"
        if "一阶段" in output:
            phase = "一阶段"
        elif "二阶段" in output:
            phase = "二阶段"
        elif "三阶段" in output:
            phase = "三阶段"
        elif "四阶段" in output:
            phase = "四阶段"
        elif "五阶段" in output:
            phase = "五阶段"
        
        return {
            "phase": phase,
            "confidence": 50,
            "reasoning": output,
            "raw_output": output
        }


# 创建全局Agent实例
_agent: Optional[PhaseAnalysisAgent] = None


async def get_phase_agent() -> PhaseAnalysisAgent:
    """获取Agent实例（单例）"""
    global _agent
    
    if _agent is None:
        from core.intelligent_system.config import settings
        _agent = PhaseAnalysisAgent(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE
        )
    
    return _agent
