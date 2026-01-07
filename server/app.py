"""
FastAPI服务
集成LangGraph工作流，提供聊天机器人接口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import asyncio
import uuid
from core.graph.analysis_graph import compiled_graph
from core.models.state import AnalysisState
from core.graph.futures_analysis_graph import compiled_futures_graph
from core.models.futures_state import FuturesAnalysisState

app = FastAPI(title="博弈交易法分析系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单的内存会话存储（需要持久化时可替换为 Redis/数据库）
SESSIONS: Dict[str, Dict[str, Any]] = {}


def create_sse_response(generator):
    """创建 SSE 响应，包含必要的响应头"""
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "Content-Type": "text/event-stream; charset=utf-8",
        }
    )


def get_or_create_session(session_id: Optional[str]) -> (str, Dict[str, Any]):
    """
    获取或创建会话
    返回 (session_id, session_data)
    """
    if not session_id or session_id not in SESSIONS:
        new_id = session_id or str(uuid.uuid4())
        SESSIONS[new_id] = {
            "history": [],             # 对话历史 [{'role': 'user', 'content': '...'}, ...]
            "last_stock_code": None,   # 最近一次使用的股票代码
            "last_analysis_type": None # 最近一次分析类型
        }
        return new_id, SESSIONS[new_id]
    return session_id, SESSIONS[session_id]


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    stock_code: Optional[str] = None
    analysis_type: Optional[str] = "auto"  # auto/regular/game_theory
    days: Optional[int] = 180
    run_backtest: Optional[bool] = False
    session_id: Optional[str] = None       # 会话ID，前端多轮对话时传入


class IntentRequest(BaseModel):
    """意图识别请求模型"""
    message: str


@app.get("/")
async def root():
    """根路径"""
    return {"message": "博弈交易法分析系统 API", "version": "1.0.0"}


@app.get("/api/vnpy/status")
async def get_vnpy_status():
    """获取 vnpy 集成状态"""
    try:
        from core.tools.vnpy_integration import get_vnpy_status
        status = get_vnpy_status()
        return {
            "success": True,
            "status": status,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": {
                "available": False,
                "modules": {},
            },
        }


@app.post("/api/intent/recognize")
async def recognize_intent(request: IntentRequest):
    """意图识别接口"""
    from core.agents.intent_agent import recognize_intent, extract_stock_code
    
    message = request.message
    intent = recognize_intent(message)
    stock_code = extract_stock_code(message)
    
    return {
        "intent": intent,
        "stock_code": stock_code,
        "confidence": 0.8,
        "keywords": []
    }


@app.get("/api/chat/stream")
async def chat_stream(
    message: str,
    stock_code: Optional[str] = None,
    analysis_type: Optional[str] = "auto",
    days: Optional[int] = 180,
    run_backtest: Optional[bool] = False,
    session_id: Optional[str] = None,
):
    """
    聊天流式接口
    使用LangGraph工作流进行分析
    """
    
    async def generate():
        try:
            # 会话管理：获取或创建会话
            conv_id, session = get_or_create_session(session_id)
            history = session["history"]

            # 记录本轮用户消息到历史
            history.append({"role": "user", "content": message})

            # 如果没有提供股票代码，尝试从消息中提取
            if not stock_code:
                from core.agents.intent_agent import extract_stock_code
                extracted_code = extract_stock_code(message)
                if not extracted_code:
                    yield f"data: {json.dumps({'error': '请提供股票代码', 'session_id': conv_id}, ensure_ascii=False)}\n\n"
                    return
                final_stock_code = extracted_code
            else:
                final_stock_code = stock_code
            
            # 确定分析类型
            if analysis_type == "auto":
                from core.agents.intent_agent import recognize_intent
                final_analysis_type = recognize_intent(message)
            else:
                final_analysis_type = analysis_type

            # 把本次股票代码和分析类型存回会话（方便“继续”这种指令）
            session["last_stock_code"] = final_stock_code
            session["last_analysis_type"] = final_analysis_type
            
            # 初始化状态
            initial_state: AnalysisState = {
                "user_message": message,
                "stock_code": final_stock_code,
                "analysis_type": final_analysis_type if final_analysis_type != "auto" else None,
                "stock_data": None,
                "stage_result": None,
                "o_point_result": None,
                "washout_result": None,
                "distribution_result": None,
                "emotion_ratio_result": None,
                "anchor_result": None,
                "summary_result": None,
                "strategy_recommendation": None,
                "backtest_result": None,
                "regular_analysis_result": None,
                "final_report": None,
                "run_backtest": run_backtest,
                "days": days,
                "conversation_id": conv_id,
                "chat_history": history,
            }
            
            # 发送开始消息（带上session_id，前端可以保存用于后续多轮）
            yield f"data: {json.dumps({'type': 'start', 'message': '开始分析...', 'session_id': conv_id}, ensure_ascii=False)}\n\n"
            
            # 运行工作流
            final_state = None
            async for state in compiled_graph.astream(initial_state):
                # 获取当前节点名称（简化处理）
                current_node = list(state.keys())[0] if state else None
                
                # 发送进度更新
                if current_node:
                    node_messages = {
                        "intent_recognition": "识别分析意图...",
                        "data_fetch": "获取股票数据...",
                        "stage_analysis": "分析股票阶段...",
                        "o_point_analysis": "识别O点...",
                        "washout_analysis": "分析洗盘情况...",
                        "distribution_analysis": "分析出货情况...",
                        "emotion_ratio": "分析情绪比例关系...",
                        "anchor_analysis": "分析锚定情况...",
                        "summary": "生成分析总结...",
                        "regular_analysis": "进行常规技术分析...",
                        "strategy_recommendation": "生成交易策略...",
                        "backtest": "进行回溯测试...",
                        "final_report": "生成最终报告..."
                    }
                    
                    progress_msg = node_messages.get(current_node, f"执行 {current_node}...")
                    yield f"data: {json.dumps({'type': 'progress', 'message': progress_msg, 'node': current_node}, ensure_ascii=False)}\n\n"
                
                # 保存最终状态
                final_state = state
            
            # 获取最终结果
            if final_state:
                # 从最终状态中提取结果
                result_state = final_state.get(list(final_state.keys())[-1], {}) if final_state else {}
                
                # 发送最终报告
                final_report = result_state.get('final_report', '分析完成')

                # 把本轮回答加入会话历史
                history.append({"role": "assistant", "content": final_report})

                yield f"data: {json.dumps({'type': 'result', 'report': final_report, 'session_id': conv_id}, ensure_ascii=False)}\n\n"
                
                # 发送结构化详细结果（不给前端渲染JSON，只用于图表等组件）
                if result_state.get('analysis_type') == 'game_theory':
                    detail_payload = {
                        "stage": result_state.get("stage_result"),
                        "strategy": result_state.get("strategy_recommendation"),
                        "backtest": result_state.get("backtest_result"),
                    }
                else:
                    detail_payload = {
                        "regular": result_state.get("regular_analysis_result")
                    }

                yield f"data: {json.dumps({'type': 'detail', 'data': detail_payload}, ensure_ascii=False)}\n\n"
                
                # 发送完成消息
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '分析失败，未获取到结果'}, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
    
    return create_sse_response(generate())


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    聊天接口（非流式）
    """
    try:
        # 会话管理
        conv_id, session = get_or_create_session(request.session_id)
        history = session["history"]

        # 记录本轮用户消息
        history.append({"role": "user", "content": request.message})

        # 确定股票代码：本次参数优先，其次用会话里记住的
        stock_code = request.stock_code or session.get("last_stock_code")
        if not stock_code:
            from core.agents.intent_agent import extract_stock_code
            stock_code = extract_stock_code(request.message)
            if not stock_code:
                raise HTTPException(status_code=400, detail="请提供股票代码")
        
        # 确定分析类型：本次参数优先，其次用会话里记住的
        if request.analysis_type == "auto":
            from core.agents.intent_agent import recognize_intent
            analysis_type = recognize_intent(request.message)
        else:
            analysis_type = request.analysis_type

        # 更新会话中最近一次使用的股票与分析类型
        session["last_stock_code"] = stock_code
        session["last_analysis_type"] = analysis_type
        
        # 初始化状态（带上会话信息和历史）
        initial_state: AnalysisState = {
            "user_message": request.message,
            "stock_code": stock_code,
            "analysis_type": analysis_type if analysis_type != "auto" else None,
            "stock_data": None,
            "stage_result": None,
            "o_point_result": None,
            "washout_result": None,
            "distribution_result": None,
            "emotion_ratio_result": None,
            "anchor_result": None,
            "summary_result": None,
            "strategy_recommendation": None,
            "backtest_result": None,
            "regular_analysis_result": None,
            "final_report": None,
            "run_backtest": request.run_backtest,
            "days": request.days,
            "conversation_id": conv_id,
            "chat_history": history,
        }
        
        # 运行工作流
        final_state = None
        async for state in compiled_graph.astream(initial_state):
            final_state = state
        
        # 提取结果
        if final_state:
            result_state = final_state.get(list(final_state.keys())[-1], {}) if final_state else {}
            reply = result_state.get('final_report', '分析完成')

            # 把本轮回复加入历史
            history.append({"role": "assistant", "content": reply})

            return {
                "success": True,
                "session_id": conv_id,
                "report": reply,
                "data": {
                    "stage": result_state.get('stage_result'),
                    "strategy": result_state.get('strategy_recommendation'),
                    "regular": result_state.get('regular_analysis_result')
                }
            }
        else:
            raise HTTPException(status_code=500, detail="分析失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FuturesAnalysisRequest(BaseModel):
    """期货分析请求模型"""
    message: str
    futures_code: Optional[str] = None
    analysis_type: Optional[str] = "all"  # all/game_theory/risk/spread/fundamental
    days: Optional[int] = 180
    session_id: Optional[str] = None


@app.get("/api/futures/contracts")
async def get_futures_contracts():
    """获取可用期货合约列表（示例）"""
    # 这里可以返回常用合约列表，实际应该从数据库或配置文件读取
    contracts = [
        {"code": "rb2501", "name": "螺纹钢2501", "exchange": "SHFE"},
        {"code": "cu2501", "name": "铜2501", "exchange": "SHFE"},
        {"code": "i2501", "name": "铁矿石2501", "exchange": "DCE"},
        {"code": "j2501", "name": "焦炭2501", "exchange": "DCE"},
    ]
    return {"success": True, "contracts": contracts}


@app.get("/api/futures/data")
async def get_futures_data(
    futures_code: str,
    days: Optional[int] = 180
):
    """获取期货数据接口"""
    try:
        from core.tools.futures_data_fetcher import fetch_futures_data, get_futures_name
        from core.tools.vnpy_integration import get_futures_contract_info
        
        # 获取数据
        futures_data = fetch_futures_data(futures_code, days)
        futures_name = get_futures_name(futures_code)
        contract_info = get_futures_contract_info(futures_code)
        
        # 转换为JSON格式
        data_list = []
        for _, row in futures_data.iterrows():
            data_list.append({
                "date": row["日期"].strftime("%Y-%m-%d") if hasattr(row["日期"], "strftime") else str(row["日期"]),
                "open": float(row["开盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "close": float(row["收盘"]),
                "volume": float(row["成交量"]) if "成交量" in row else 0,
                "open_interest": float(row["持仓量"]) if "持仓量" in row else 0,
            })
        
        return {
            "success": True,
            "futures_code": futures_code,
            "futures_name": futures_name,
            "contract_info": contract_info,
            "data": data_list,
            "count": len(data_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/futures/analyze/stream")
async def futures_analyze_stream(
    message: str,
    futures_code: Optional[str] = None,
    analysis_type: Optional[str] = "all",
    days: Optional[int] = 180,
    session_id: Optional[str] = None,
):
    """
    期货分析流式接口
    使用LangGraph工作流进行分析
    """
    
    async def generate():
        try:
            print(f"[期货分析API] ========== 收到请求 ==========")
            print(f"[期货分析API] message={message}")
            print(f"[期货分析API] futures_code={futures_code}")
            print(f"[期货分析API] analysis_type={analysis_type}")
            print(f"[期货分析API] days={days}")
            
            # 会话管理
            conv_id, session = get_or_create_session(session_id)
            history = session.get("history", [])
            print(f"[期货分析API] session_id={conv_id}")

            # 记录本轮用户消息
            history.append({"role": "user", "content": message})

            # 如果没有提供期货代码，尝试从消息中提取
            if not futures_code:
                # 简单的代码提取逻辑（可以改进）
                import re
                code_match = re.search(r'[a-zA-Z]+\d{4}', message)
                if code_match:
                    final_futures_code = code_match.group()
                else:
                    yield f"data: {json.dumps({'error': '请提供期货合约代码', 'session_id': conv_id}, ensure_ascii=False)}\n\n"
                    return
            else:
                final_futures_code = futures_code
            
            # 初始化状态
            initial_state: FuturesAnalysisState = {
                "user_message": message,
                "futures_code": final_futures_code,
                "analysis_type": analysis_type,
                "futures_name": None,
                "exchange": None,
                "contract_month": None,
                "product_code": None,
                "futures_data": None,
                "open_interest": None,
                "basis_data": None,
                "related_contracts": None,
                "spread_data": None,
                "structured_data": None,
                "game_theory_result": None,
                "risk_analysis_result": None,
                "spread_analysis_result": None,
                "fundamental_analysis_result": None,
                "strategy_recommendation": None,
                "final_report": None,
                "days": days,
                "margin_rate": None,
                "contract_multiplier": None,
                "conversation_id": conv_id,
                "chat_history": history,
            }
            
            # 发送开始消息
            yield f"data: {json.dumps({'type': 'start', 'message': '开始期货分析...', 'session_id': conv_id}, ensure_ascii=False)}\n\n"
            
            # 运行工作流
            print(f"[期货分析API] 开始运行工作流: {final_futures_code}, 分析类型: {analysis_type}")
            final_state = None
            node_count = 0
            async for state in compiled_futures_graph.astream(initial_state):
                node_count += 1
                # 获取当前节点名称
                current_node = list(state.keys())[0] if state else None
                print(f"[期货分析API] 工作流执行节点 {node_count}: {current_node}")
                
                # 发送进度更新
                if current_node:
                    node_messages = {
                        "data_fetch": "获取期货数据...",
                        "game_theory_analysis": "进行博弈交易法分析...",
                        "risk_analysis": "进行风险管理分析...",
                        "spread_analysis": "进行价差分析...",
                        "fundamental_analysis": "进行基本面分析...",
                        "strategy_recommendation": "生成交易策略...",
                        "final_report": "生成最终报告...",
                    }
                    
                    progress_msg = node_messages.get(current_node, f"执行 {current_node}...")
                    yield f"data: {json.dumps({'type': 'progress', 'message': progress_msg, 'node': current_node}, ensure_ascii=False)}\n\n"
                
                # 保存最终状态
                final_state = state
            
            # 获取最终结果
            if final_state:
                result_state = final_state.get(list(final_state.keys())[-1], {}) if final_state else {}
                
                # 发送最终报告
                final_report = result_state.get('final_report', '分析完成')

                # 把本轮回答加入会话历史
                history.append({"role": "assistant", "content": final_report})

                yield f"data: {json.dumps({'type': 'result', 'report': final_report, 'session_id': conv_id}, ensure_ascii=False)}\n\n"
                
                # 发送结构化详细结果
                detail_payload = {
                    "game_theory": result_state.get("game_theory_result"),
                    "risk": result_state.get("risk_analysis_result"),
                    "spread": result_state.get("spread_analysis_result"),
                    "fundamental": result_state.get("fundamental_analysis_result"),
                    "strategy": result_state.get("strategy_recommendation"),
                }

                yield f"data: {json.dumps({'type': 'detail', 'data': detail_payload}, ensure_ascii=False)}\n\n"
                
                # 发送完成消息
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '分析失败，未获取到结果'}, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            error_msg = str(e)
            import traceback
            print(f"[期货分析API] 流式接口异常: {error_msg}")
            print(f"[期货分析API] 完整错误堆栈:")
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"
    
    return create_sse_response(generate())


@app.post("/api/futures/analyze")
async def futures_analyze(request: FuturesAnalysisRequest):
    """
    期货分析接口（非流式）
    """
    try:
        # 会话管理
        conv_id, session = get_or_create_session(request.session_id)
        history = session.get("history", [])

        # 记录本轮用户消息
        history.append({"role": "user", "content": request.message})

        # 确定期货代码
        futures_code = request.futures_code
        if not futures_code:
            import re
            code_match = re.search(r'[a-zA-Z]+\d{4}', request.message)
            if code_match:
                futures_code = code_match.group()
            else:
                raise HTTPException(status_code=400, detail="请提供期货合约代码")
        
        # 初始化状态
        initial_state: FuturesAnalysisState = {
            "user_message": request.message,
            "futures_code": futures_code,
            "analysis_type": request.analysis_type,
            "futures_name": None,
            "exchange": None,
            "contract_month": None,
            "product_code": None,
            "futures_data": None,
            "open_interest": None,
            "basis_data": None,
            "related_contracts": None,
            "spread_data": None,
            "structured_data": None,
            "game_theory_result": None,
            "risk_analysis_result": None,
            "spread_analysis_result": None,
            "fundamental_analysis_result": None,
            "strategy_recommendation": None,
            "final_report": None,
            "days": request.days,
            "margin_rate": None,
            "contract_multiplier": None,
            "conversation_id": conv_id,
            "chat_history": history,
        }
        
        # 运行工作流
        final_state = None
        async for state in compiled_futures_graph.astream(initial_state):
            final_state = state
        
        # 提取结果
        if final_state:
            result_state = final_state.get(list(final_state.keys())[-1], {}) if final_state else {}
            reply = result_state.get('final_report', '分析完成')

            # 把本轮回复加入历史
            history.append({"role": "assistant", "content": reply})

            return {
                "success": True,
                "session_id": conv_id,
                "report": reply,
                "data": {
                    "game_theory": result_state.get('game_theory_result'),
                    "risk": result_state.get('risk_analysis_result'),
                    "spread": result_state.get('spread_analysis_result'),
                    "fundamental": result_state.get('fundamental_analysis_result'),
                    "strategy": result_state.get('strategy_recommendation')
                }
            }
        else:
            raise HTTPException(status_code=500, detail="分析失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 紫微斗数API ====================

class ZiweiPanRequest(BaseModel):
    """紫微斗数排盘请求模型"""
    year: int
    month: int
    day: int
    hour: int  # 时辰（0-23）
    gender: str = '男'  # 性别：'男' 或 '女'
    include_daxian: bool = True  # 是否包含大限分析
    include_liunian: bool = False  # 是否包含流年分析
    include_liuyue: bool = False  # 是否包含流月分析
    include_shensha: bool = True  # 是否包含神煞分析
    include_geju: bool = True  # 是否包含格局分析
    include_llm: bool = False  # 是否包含LLM深度分析（默认关闭，需要用户明确勾选）
    target_year: Optional[int] = None  # 目标年份（用于流年流月分析）
    target_month: Optional[int] = None  # 目标月份（用于流月分析）


@app.post("/api/ziwei/pan")
async def ziwei_pan(request: ZiweiPanRequest):
    """
    紫微斗数排盘接口
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        print(f"[紫微斗数API] ========== 收到排盘请求 ==========")
        print(f"[紫微斗数API] 年份: {request.year}")
        print(f"[紫微斗数API] 月份: {request.month}")
        print(f"[紫微斗数API] 日期: {request.day}")
        print(f"[紫微斗数API] 时辰: {request.hour}")
        print(f"[紫微斗数API] 性别: {request.gender}")
        
        logger.info(f"收到紫微斗数排盘请求: {request.year}年{request.month}月{request.day}日{request.hour}时, 性别={request.gender}")
        
        # 参数验证
        if not (1900 <= request.year <= 2100):
            raise HTTPException(status_code=400, detail="年份必须在1900-2100之间")
        if not (1 <= request.month <= 12):
            raise HTTPException(status_code=400, detail="月份必须在1-12之间")
        if not (1 <= request.day <= 31):
            raise HTTPException(status_code=400, detail="日期必须在1-31之间")
        if not (0 <= request.hour <= 23):
            raise HTTPException(status_code=400, detail="时辰必须在0-23之间")
        if request.gender not in ['男', '女']:
            raise HTTPException(status_code=400, detail="性别必须是'男'或'女'")
        
        print(f"[紫微斗数API] 参数验证通过，开始调用完整分析函数...")
        print(f"[紫微斗数API] 分析选项: 大限={request.include_daxian}, 神煞={request.include_shensha}, 格局={request.include_geju}, LLM={request.include_llm}")
        
        # 调用完整分析函数
        from core.agents.ziwei_analysis_agent import ziwei_complete_analysis
        
        print(f"[紫微斗数API] 正在调用 ziwei_complete_analysis...")
        result = ziwei_complete_analysis(
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            gender=request.gender,
            include_daxian=request.include_daxian,
            include_liunian=request.include_liunian,
            include_liuyue=request.include_liuyue,
            include_shensha=request.include_shensha,
            include_geju=request.include_geju,
            include_llm=request.include_llm,
            target_year=request.target_year,
            target_month=request.target_month,
        )
        
        print(f"[紫微斗数API] 分析函数返回结果: success={result.get('success')}")
        
        if not result.get('success'):
            error_msg = result.get('error', '未知错误')
            print(f"[紫微斗数API] 分析失败: {error_msg}")
            logger.error(f"分析失败: {error_msg}")
            raise HTTPException(status_code=500, detail=f"分析失败: {error_msg}")
        
        print(f"[紫微斗数API] 分析成功，返回结果")
        print(f"[紫微斗数API] 包含的分析模块:")
        print(f"  - 命盘数据: {result.get('pan_data') is not None}")
        print(f"  - 四化分析: {result.get('si_hua_analysis') is not None}")
        print(f"  - 大限分析: {result.get('daxian_analysis') is not None}")
        print(f"  - 神煞分析: {result.get('shensha_analysis') is not None}")
        print(f"  - 格局分析: {result.get('geju_analysis') is not None}")
        print(f"  - LLM分析: {result.get('llm_analysis') is not None}")
        logger.info("完整分析成功")
        
        return {
            "success": True,
            "pan_data": result.get('pan_data'),
            "si_hua_analysis": result.get('si_hua_analysis', {}),
            "daxian_analysis": result.get('daxian_analysis'),
            "liunian_analysis": result.get('liunian_analysis'),
            "liuyue_analysis": result.get('liuyue_analysis'),
            "shensha_analysis": result.get('shensha_analysis'),
            "geju_analysis": result.get('geju_analysis'),
            "llm_analysis": result.get('llm_analysis'),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"[紫微斗数API] 发生异常: {error_msg}")
        import traceback
        print(f"[紫微斗数API] 异常堆栈:\n{traceback.format_exc()}")
        logger.error(f"排盘异常: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"排盘异常: {error_msg}")


# ==================== 八字排盘API ====================

class BaziPanRequest(BaseModel):
    """八字排盘请求模型"""
    year: int
    month: int
    day: int
    hour: int  # 时辰（0-23）
    gender: str = '男'  # 性别：'男' 或 '女'
    include_wuxing: bool = True  # 是否包含五行分析
    include_shishen: bool = True  # 是否包含十神分析
    include_dayun: bool = True  # 是否包含大运分析
    include_liunian: bool = False  # 是否包含流年分析
    include_shensha: bool = True  # 是否包含神煞分析
    include_llm: bool = False  # 是否包含LLM深度分析（默认关闭，需要用户明确勾选）
    target_year: Optional[int] = None  # 目标年份（用于流年分析）


@app.post("/api/bazi/pan")
async def bazi_pan(request: BaziPanRequest):
    """
    八字排盘接口
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        print(f"[八字排盘API] ========== 收到排盘请求 ==========")
        print(f"[八字排盘API] 年份: {request.year}")
        print(f"[八字排盘API] 月份: {request.month}")
        print(f"[八字排盘API] 日期: {request.day}")
        print(f"[八字排盘API] 时辰: {request.hour}")
        print(f"[八字排盘API] 性别: {request.gender}")
        
        logger.info(f"收到八字排盘请求: {request.year}年{request.month}月{request.day}日{request.hour}时, 性别={request.gender}")
        
        # 参数验证
        if not (1900 <= request.year <= 2100):
            raise HTTPException(status_code=400, detail="年份必须在1900-2100之间")
        if not (1 <= request.month <= 12):
            raise HTTPException(status_code=400, detail="月份必须在1-12之间")
        if not (1 <= request.day <= 31):
            raise HTTPException(status_code=400, detail="日期必须在1-31之间")
        if not (0 <= request.hour <= 23):
            raise HTTPException(status_code=400, detail="时辰必须在0-23之间")
        if request.gender not in ['男', '女']:
            raise HTTPException(status_code=400, detail="性别必须是'男'或'女'")
        
        print(f"[八字排盘API] 参数验证通过，开始调用完整分析函数...")
        print(f"[八字排盘API] 分析选项: 五行={request.include_wuxing}, 十神={request.include_shishen}, 大运={request.include_dayun}, 流年={request.include_liunian}, 神煞={request.include_shensha}, LLM={request.include_llm}")
        
        # 调用完整分析函数
        from core.agents.bazi_analysis_agent import bazi_complete_analysis
        
        print(f"[八字排盘API] 正在调用 bazi_complete_analysis...")
        result = bazi_complete_analysis(
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            gender=request.gender,
            include_wuxing=request.include_wuxing,
            include_shishen=request.include_shishen,
            include_dayun=request.include_dayun,
            include_liunian=request.include_liunian,
            include_shensha=request.include_shensha,
            include_llm=request.include_llm,
            target_year=request.target_year,
        )
        
        print(f"[八字排盘API] 分析函数返回结果: success={result.get('success')}")
        
        if not result.get('success'):
            error_msg = result.get('error', '未知错误')
            print(f"[八字排盘API] 分析失败: {error_msg}")
            logger.error(f"分析失败: {error_msg}")
            raise HTTPException(status_code=500, detail=f"分析失败: {error_msg}")
        
        print(f"[八字排盘API] 分析成功，返回结果")
        print(f"[八字排盘API] 包含的分析模块:")
        print(f"  - 四柱数据: {result.get('sizhu') is not None}")
        print(f"  - 五行分析: {result.get('wuxing_analysis') is not None}")
        print(f"  - 十神分析: {result.get('shishen_analysis') is not None}")
        print(f"  - 大运分析: {result.get('dayun_analysis') is not None}")
        print(f"  - 流年分析: {result.get('liunian_analysis') is not None}")
        print(f"  - 神煞分析: {result.get('shensha_analysis') is not None}")
        print(f"  - LLM分析: {result.get('llm_analysis') is not None}")
        logger.info("完整分析成功")
        
        return {
            "success": True,
            "sizhu": result.get('sizhu'),
            "wuxing_analysis": result.get('wuxing_analysis'),
            "shishen_analysis": result.get('shishen_analysis'),
            "dayun_analysis": result.get('dayun_analysis'),
            "liunian_analysis": result.get('liunian_analysis'),
            "shensha_analysis": result.get('shensha_analysis'),
            "llm_analysis": result.get('llm_analysis'),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"[八字排盘API] 发生异常: {error_msg}")
        import traceback
        print(f"[八字排盘API] 异常堆栈:\n{traceback.format_exc()}")
        logger.error(f"排盘异常: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"排盘异常: {error_msg}")


# ==================== 六爻卜卦API ====================

@app.get("/api/divination/test")
async def divination_test():
    """测试六爻卜卦API是否可用"""
    return {"message": "六爻卜卦API已就绪", "status": "ok"}


class DivinationRequest(BaseModel):
    """六爻卜卦请求模型"""
    coin_results: List[List[int]]  # 6次摇卦结果，每次3枚铜钱（0=反面，1=正面）
    question: str  # 用户问题
    include_llm: bool = True  # 是否调用LLM分析


@app.post("/api/divination/analyze")
async def divination_analyze(request: DivinationRequest):
    """
    六爻卜卦分析接口
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        print(f"[六爻卜卦API] ========== 收到卜卦请求 ==========")
        print(f"[六爻卜卦API] 问题: {request.question}")
        print(f"[六爻卜卦API] 摇卦结果数量: {len(request.coin_results)}")
        print(f"[六爻卜卦API] 调用LLM: {request.include_llm}")
        
        logger.info(f"收到六爻卜卦请求: 问题={request.question}, 摇卦次数={len(request.coin_results)}")
        
        # 参数验证
        if len(request.coin_results) != 6:
            raise HTTPException(status_code=400, detail="必须提供6次摇卦结果")
        
        for i, coins in enumerate(request.coin_results):
            if len(coins) != 3:
                raise HTTPException(status_code=400, detail=f"第{i+1}次摇卦必须提供3枚铜钱的结果")
            if not all(c in [0, 1] for c in coins):
                raise HTTPException(status_code=400, detail=f"第{i+1}次摇卦结果无效，必须为0或1")
        
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="必须提供问题")
        
        print(f"[六爻卜卦API] 参数验证通过，开始调用分析函数...")
        
        # 调用分析函数
        from core.agents.divination_agent import divination_complete_analysis
        
        print(f"[六爻卜卦API] 正在调用 divination_complete_analysis...")
        result = divination_complete_analysis(
            coin_results=request.coin_results,
            question=request.question,
            include_llm=request.include_llm,
        )
        
        print(f"[六爻卜卦API] 分析函数返回结果: success={result.get('success')}")
        
        if not result.get('success'):
            error_msg = result.get('error', '未知错误')
            print(f"[六爻卜卦API] 分析失败: {error_msg}")
            logger.error(f"分析失败: {error_msg}")
            raise HTTPException(status_code=500, detail=f"分析失败: {error_msg}")
        
        print(f"[六爻卜卦API] 分析成功，返回结果")
        logger.info("六爻卜卦分析成功")
        
        return {
            "success": True,
            "hexagram": result.get('hexagram'),
            "question": result.get('question'),
            "llm_analysis": result.get('llm_analysis'),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"[六爻卜卦API] 发生异常: {error_msg}")
        import traceback
        print(f"[六爻卜卦API] 异常堆栈:\n{traceback.format_exc()}")
        logger.error(f"六爻卜卦异常: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"六爻卜卦异常: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
