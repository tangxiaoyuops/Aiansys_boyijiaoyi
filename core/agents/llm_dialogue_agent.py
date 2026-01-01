"""
LLM 对话 Agent
用于处理常规对话 / 对历史结论的追问，或只重跑某个场景（阶段/出货/情绪/买卖点）的分析
"""
from typing import Dict, Any, List

from core.models.state import AnalysisState
from core.tools.llm_client import call_llm
from core.agents.llm_stage_agent import llm_stage_analysis_node
from core.agents.llm_emotion_agent import llm_emotion_analysis_node
from core.agents.llm_distribution_agent import llm_distribution_analysis_node
from core.agents.llm_trading_points_agent import llm_trading_points_analysis_node


def _run_scene_analysis_if_needed(state: AnalysisState) -> AnalysisState:
    """
    如果用户指定了 scene_type，则在对话前定向重跑对应的 Agent
    场景类型：
        - 'stage'：阶段分析（依赖 llm_distribution_result，可复用已有结果）
        - 'distribution'：出货分析
        - 'emotion'：情绪/锚定分析
        - 'trading'：买卖点分析（依赖 stage/emotion 等，可复用已有结果）
    """
    scene_type = state.get("scene_type")
    if not scene_type:
        return state

    # 如果缺少结构化数据，定向分析也无法进行，直接返回
    if not state.get("structured_data"):
        print("[LLM对话] scene_type 已设置，但缺少 structured_data，跳过定向分析")
        return state

    try:
        if scene_type == "distribution":
            state = llm_distribution_analysis_node(state)
        elif scene_type == "stage":
            # 阶段分析会读取 llm_distribution_result，如果没有也会自己兜底
            state = llm_stage_analysis_node(state)
        elif scene_type == "emotion":
            state = llm_emotion_analysis_node(state)
        elif scene_type == "trading":
            # 买卖点分析依赖前面的阶段/情绪/出货结果，但这里假设之前已经跑过；
            # 如果没有，对应 Agent 自己会在状态里写入 error 信息。
            state = llm_trading_points_analysis_node(state)
    except Exception as e:
        print(f"[LLM对话] 定向场景分析失败 scene_type={scene_type}: {e}")

    return state


def build_dialogue_prompt(state: AnalysisState) -> str:
    """
    构建对话提示词，将 chat_history、最近分析结论和本轮定向场景请求压缩进去
    """
    stock_code = state.get("stock_code", "")
    stock_name = state.get("stock_name", "") or ""
    user_message = state.get("user_message", "")
    chat_history: List[Dict[str, str]] = state.get("chat_history") or []
    scene_type = state.get("scene_type") or ""

    # 最近几轮对话
    history_text = ""
    if chat_history:
        for turn in chat_history[-8:]:
            role = "用户" if turn.get("role") == "user" else "助手"
            content = turn.get("content", "")
            history_text += f"{role}：{content}\n"
    else:
        history_text = "（无历史对话）"

    # 汇总最近一次分析的关键结论（如果有）
    summary_blocks: List[str] = []

    summary_result = state.get("summary_result") or {}
    if summary_result:
        summary_blocks.append("【上一轮分析总结】")
        summary_text = summary_result.get("summary") or ""
        if summary_text:
            summary_blocks.append(summary_text)

    strategy = state.get("strategy_recommendation") or {}
    if strategy:
        summary_blocks.append("【上一轮策略建议摘要】")
        op = strategy.get("operation")
        reason = strategy.get("reason")
        pos = strategy.get("position_suggestion")
        if op or reason or pos:
            line = []
            if op:
                line.append(f"操作：{op}")
            if pos:
                line.append(f"仓位：{pos}")
            if reason:
                line.append(f"理由：{reason}")
            summary_blocks.append("；".join(line))

    llm_trading = state.get("llm_trading_points_result") or {}
    if llm_trading:
        ts = llm_trading.get("trading_summary") or ""
        if ts:
            summary_blocks.append("【上一轮买卖点总结】")
            summary_blocks.append(ts)

    summary_text_all = "\n".join(summary_blocks) if summary_blocks else "（当前会话中还没有完整的分析结论）"

    # 当前这一轮是否有“定向场景分析”需求
    scene_map = {
        "stage": "阶段分析",
        "distribution": "出货分析",
        "emotion": "情绪/锚定分析",
        "trading": "买卖点分析",
    }
    scene_text = ""
    if scene_type:
        scene_text = f"【本轮用户特别指定要重点查看的分析场景】\n- {scene_map.get(scene_type, scene_type)}\n"

    prompt = f"""你是一个擅长博弈交易法和实战交易经验总结的智能助手。

【股票上下文】
- 股票代码：{stock_code or '（可能未指定）'}
- 股票名称：{stock_name or '（未知）'}

{scene_text}

【历史对话（从旧到新）】
{history_text}

【最近一次分析/买卖点结论（如有）】
{summary_text_all}

【用户当前最新一句话】
{user_message}

请你基于以上历史对话、最近的分析结论，以及“本轮指定的重点场景”（如果有），围绕用户当前的问题进行回答：
- 如果用户是在追问刚才的分析/买卖点，请先用简单语言概括之前的结论，再解释原因和逻辑；
- 如果用户指定了某个分析场景（如阶段分析/出货分析/情绪分析/买卖点分析），请优先结合本轮最新的那一块分析结果进行说明；
- 如果用户在问新的问题，但和当前股票/策略有关，请结合历史结论给出连续性的建议；
- 尽量用简洁、口语化的中文回答，不要重复贴很长的K线或JSON。
"""
    return prompt


def llm_dialogue_node(state: AnalysisState) -> AnalysisState:
    """
    对话节点：
    - 如果 scene_type 有值，先定向重跑对应 Agent，再用历史上下文+结论来回答
    - 如果没有 scene_type，就当作普通追问/总结来处理
    """
    # 1）如有需要，先做本轮定向场景分析
    state = _run_scene_analysis_if_needed(state)

    # 2）构建提示词
    user_prompt = build_dialogue_prompt(state)
    system_prompt = "你是一个交易助手，负责围绕已有分析结果和历史对话，回答用户的追问、总结需求，以及对某一类分析（阶段/出货/情绪/买卖点）的定向说明。"

    # 3）调用 LLM
    try:
        response = call_llm(system_prompt, user_prompt, temperature=0.4)
        # 将结果保存到对话结果和最终报告
        state["dialogue_result"] = {
            "answer": response
        }
        state["final_report"] = response
    except Exception as e:
        err = f"[LLM对话] 调用失败: {e}"
        print(err)
        state["dialogue_result"] = {
            "error": str(e)
        }
        state["final_report"] = "对话过程中出现错误，请稍后重试。"

    return state




