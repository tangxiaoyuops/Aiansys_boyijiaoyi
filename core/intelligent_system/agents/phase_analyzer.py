"""
五阶段分析Agent

使用LangChain和GPT-4实现智能化的阶段识别分析
适配LangChain 1.x版本
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_agent
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime

from core.intelligent_system.agents.knowledge_base import get_knowledge_base

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
        temperature: float = 0.7,
        base_url: Optional[str] = None
    ):
        """
        初始化Agent

        Args:
            openai_api_key: OpenAI API密钥
            model_name: 模型名称
            temperature: 温度参数
            base_url: 自定义API地址（兼容京东云等代理）
        """
        # 初始化LLM
        llm_kwargs = {
            "api_key": openai_api_key,
            "model": model_name,
            "temperature": temperature,
        }
        if base_url:
            llm_kwargs["base_url"] = base_url

        self.llm = ChatOpenAI(**llm_kwargs)

        # 获取知识库
        self.knowledge_base = get_knowledge_base()

        # 设置工具
        self.tools = self._setup_tools()

        # 创建Agent
        self.agent = self._create_agent()

        logger.info("PhaseAnalysisAgent初始化完成")

    def _setup_tools(self) -> List:
        """设置Agent可用的工具"""

        # 使用@tool装饰器定义工具
        @tool
        def query_knowledge(query: str) -> str:
            """查询博弈理论知识库，获取五阶段理论、洗盘理论、出货理论等核心知识。输入应该是查询关键词。"""
            results = self.knowledge_base.query_knowledge(query, n_results=3)

            knowledge_text = ""
            for i, result in enumerate(results, 1):
                knowledge_text += f"\n【知识{i}】{result['metadata']['title']}\n"
                knowledge_text += f"{result['content']}\n"

            return knowledge_text if knowledge_text else "未找到相关知识"

        @tool
        def analyze_kline_pattern(kline_data: str) -> str:
            """分析K线形态，识别关键形态（O点、洗盘、出货、锚定）。输入是JSON格式的K线数据。"""
            try:
                data = json.loads(kline_data)
                df = pd.DataFrame(data)

                # 确保数据按时间正序
                df = df.sort_values('time')

                # 识别关键形态
                patterns = {
                    "highest_price": float(df['high'].max()),
                    "lowest_price": float(df['low'].min()),
                    "avg_volume": float(df['volume'].mean()),
                    "latest_close": float(df['close'].iloc[-1]),
                    "price_change_pct": float(
                        (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                    )
                }

                # 识别O点
                o_point_idx = df['low'].idxmin()
                o_point = {
                    "price": float(df.loc[o_point_idx, 'low']),
                    "date": str(df.loc[o_point_idx, 'time']),
                    "volume": float(df.loc[o_point_idx, 'volume'])
                }

                # 检查O点后是否创新低
                after_o_point = df.loc[o_point_idx:]
                new_low = after_o_point['low'].min() < o_point['price']

                patterns['o_point'] = o_point
                patterns['o_point_confirmed'] = not new_low

                # 识别洗盘（简化版：跌幅超过5%的回调）
                df['pct_change'] = df['close'].pct_change()
                significant_drops = df[df['pct_change'] < -0.05]
                patterns['washing_count'] = len(significant_drops)
                patterns['max_drop'] = float(df['pct_change'].min() * 100)

                return json.dumps(patterns, ensure_ascii=False)

            except Exception as e:
                return f"K线形态分析失败: {str(e)}"

        @tool
        def calculate_technical_indicators(kline_data: str) -> str:
            """计算技术指标（均线、成交量等）。输入是JSON格式的K线数据。"""
            try:
                data = json.loads(kline_data)
                df = pd.DataFrame(data)
                df = df.sort_values('time')

                # 计算均线
                df['ma5'] = df['close'].rolling(window=5).mean()
                df['ma10'] = df['close'].rolling(window=10).mean()
                df['ma20'] = df['close'].rolling(window=20).mean()
                df['ma60'] = df['close'].rolling(window=60).mean()

                # 计算成交量均线
                df['vol_ma5'] = df['volume'].rolling(window=5).mean()
                df['vol_ma10'] = df['volume'].rolling(window=10).mean()

                # 获取最新值
                latest = df.iloc[-1]

                indicators = {
                    "close": float(latest['close']),
                    "ma5": float(latest['ma5']) if pd.notna(latest['ma5']) else None,
                    "ma10": float(latest['ma10']) if pd.notna(latest['ma10']) else None,
                    "ma20": float(latest['ma20']) if pd.notna(latest['ma20']) else None,
                    "ma60": float(latest['ma60']) if pd.notna(latest['ma60']) else None,
                    "volume": float(latest['volume']),
                    "vol_ma5": float(latest['vol_ma5']) if pd.notna(latest['vol_ma5']) else None,
                    "volume_ratio": float(latest['volume'] / latest['vol_ma5']) if pd.notna(latest['vol_ma5']) and latest['vol_ma5'] > 0 else 0,
                    "price_above_ma20": bool(latest['close'] > latest['ma20']) if pd.notna(latest['ma20']) else False
                }

                return json.dumps(indicators, ensure_ascii=False)

            except Exception as e:
                return f"技术指标计算失败: {str(e)}"

        @tool
        def analyze_trend_strength(kline_data: str) -> str:
            """分析趋势强度，判断趋势是否存在。输入是JSON格式的K线数据。"""
            try:
                data = json.loads(kline_data)
                df = pd.DataFrame(data)
                df = df.sort_values('time')

                # 计算价格变化率
                df['return'] = df['close'].pct_change()

                # 计算MA20斜率
                df['ma20'] = df['close'].rolling(window=20).mean()
                df['ma20_slope'] = df['ma20'].diff() / df['ma20'].shift(1)

                # 平均斜率
                avg_slope = float(df['ma20_slope'].mean())

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
                    "volatility": float(df['return'].std())
                }

                return json.dumps(result, ensure_ascii=False)

            except Exception as e:
                return f"趋势分析失败: {str(e)}"

        return [query_knowledge, analyze_kline_pattern, calculate_technical_indicators, analyze_trend_strength]

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

1. 数据获取：获取K线数据，计算技术指标，分析成交量变化
2. O点识别：寻找最低点后不再创新低的位置，确认O点的价格和日期
3. 趋势分析：判断趋势是否存在，计算趋势强度
4. 形态识别：识别洗盘形态、出货形态、判断锚定类型
5. 情绪分析：计算情绪比例关系，评估恐惧程度和焦虑程度
6. 综合判断：结合博弈理论，多维度推理，给出阶段判断

## 五阶段特征：

- 一阶段：趋势形成初期，始于O点，缓慢隐蔽上涨，偶有大阳线后立刻下跌，形态难看
- 二阶段：快速上涨阶段，大幅拉升，高位运行，伴随持续洗盘，牛股结构
- 三阶段：疯狂阶段，散户贪婪，持续时间短（<3个月），无洗盘，借助大盘
- 四阶段：猛烈下跌，下跌速度快且幅度大
- 五阶段：漫长阴跌，消磨意志，散户一致看跌

## 输出要求：

你的分析结果必须包含以下JSON格式：

{
    "phase": "阶段名称",
    "confidence": 置信度(0-100),
    "o_point": {
        "price": O点价格,
        "date": "O点日期",
        "confirmed": true/false
    },
    "trend": {
        "exists": true/false,
        "strength": "弱/中/强",
        "stability": "差/一般/好"
    },
    "emotion_ratio": {
        "distribution_beauty": 出货好看程度(0-10),
        "washing_ugliness": 洗盘难看程度(0-10),
        "qualified": true/false
    },
    "key_features": ["特征1", "特征2", "特征3"],
    "reasoning": "详细解释为什么做出这个判断（至少100字）",
    "risks": ["风险1", "风险2"],
    "operation_advice": "操作建议"
}

请使用工具获取数据，进行系统性分析，不要凭空猜测。
"""

        # 使用新版create_agent创建Agent
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt
        )

        return agent

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
            # 准备输入数据（限制长度避免超出token限制）
            kline_json = json.dumps(kline_data, ensure_ascii=False, default=str)

            # 构建分析任务
            task = f"""请分析股票 {stock_code} 当前所处的阶段。

K线数据（最近{len(kline_data)}个交易日）：
{kline_json[:5000]}

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
            result = await self.agent.ainvoke({"messages": [{"role": "user", "content": task}]})

            # 提取最终回复
            output = ""
            if hasattr(result, 'messages'):
                # 获取最后一条AI消息
                for msg in reversed(result.messages):
                    if hasattr(msg, 'content') and msg.type == 'ai':
                        output = msg.content
                        break

            # 尝试解析JSON
            try:
                # 尝试直接解析
                analysis = json.loads(output)
            except json.JSONDecodeError:
                # 尝试从markdown代码块中提取JSON
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group(1))
                    except:
                        analysis = self._parse_analysis_result(output)
                else:
                    analysis = self._parse_analysis_result(output)

            # 尝试保存到数据库（如果可用）
            try:
                from core.intelligent_system.database.db_manager import get_db_manager
                db = await get_db_manager()
                await db.save_agent_analysis_result(
                    stock_code=stock_code,
                    analysis_type="phase_analysis",
                    result=analysis,
                    confidence=analysis.get('confidence', 0.0)
                )
            except Exception as db_err:
                logger.warning(f"数据库保存失败（不影响分析结果）: {db_err}")

            logger.info(f"分析完成: {stock_code} - {analysis.get('phase', '未知')}")

            return analysis

        except Exception as e:
            logger.error(f"分析失败 {stock_code}: {e}")
            import traceback
            traceback.print_exc()
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
        # 优先使用QWEN_MODEL，如果没有则使用OPENAI_MODEL
        model_name = settings.QWEN_MODEL or settings.OPENAI_MODEL
        _agent = PhaseAnalysisAgent(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name=model_name,
            temperature=settings.OPENAI_TEMPERATURE,
            base_url=settings.OPENAI_BASE_URL
        )

    return _agent
