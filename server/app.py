"""
FastAPI服务
集成LangGraph工作流，提供聊天机器人接口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
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
    
    return StreamingResponse(generate(), media_type="text/event-stream")


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
    
    return StreamingResponse(generate(), media_type="text/event-stream")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
