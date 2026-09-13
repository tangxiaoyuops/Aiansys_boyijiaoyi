"""
博弈交易法Agent - 流式响应API
实现实时推送每个分析节点的执行过程
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
import json
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
import numpy as np
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from core.agent_framework.agents.base import AgentState
from core.tools.llm_client import call_llm

router = APIRouter()


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器,处理Pandas、NumPy和datetime类型"""
    
    def default(self, obj):
        # 处理Pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        
        # 处理datetime和date
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # 处理NumPy类型
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # 处理Decimal
        if isinstance(obj, Decimal):
            return float(obj)
        
        # 处理Pandas DataFrame和Series
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict('records') if isinstance(obj, pd.DataFrame) else obj.to_dict()
        
        # 处理NaN和Infinity
        if isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
        
        # 其他类型尝试转换为字符串
        try:
            return str(obj)
        except:
            return super().default(obj)


def safe_json_dumps(obj, **kwargs):
    """安全的JSON序列化函数"""
    return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)


async def stream_workflow_execution(
    workflow_graph,
    initial_state: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """
    流式执行工作流,实时推送每个节点的执行过程
    
    Args:
        workflow_graph: LangGraph工作流图
        initial_state: 初始状态
        
    Yields:
        str: SSE格式的数据流
    """
    from langgraph.pregel import GraphRecursionError
    
    try:
        # 发送开始事件
        yield f"data: {safe_json_dumps({'type': 'start', 'message': '开始博弈交易法分析...'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 执行工作流的每个节点
        current_node = None
        node_count = 0
        
        # 使用stream模式执行
        async for event in workflow_graph.astream(initial_state):
            # event是一个字典: {node_name: node_output}
            for node_name, node_output in event.items():
                node_count += 1
                
                # 发送节点开始事件
                yield f"data: {safe_json_dumps({
                    'type': 'node_start',
                    'node': node_name,
                    'message': f'正在执行: {get_node_description(node_name)}',
                    'node_count': node_count
                })}\n\n"
                await asyncio.sleep(0.05)
                
                # 根据节点类型发送不同的详细信息
                if 'result' in node_output:
                    result_data = node_output['result']
                    
                    # 发送节点执行结果
                    yield f"data: {safe_json_dumps({
                        'type': 'node_result',
                        'node': node_name,
                        'result': result_data,
                        'summary': get_result_summary(node_name, result_data)
                    })}\n\n"
                    await asyncio.sleep(0.05)
        
        # 发送完成事件
        final_state = node_output if node_output else initial_state
        yield f"data: {safe_json_dumps({
            'type': 'complete',
            'message': '分析完成!',
            'total_nodes': node_count,
            'final_report': final_state.get('final_report', '分析完成')
        })}\n\n"
        
    except GraphRecursionError as e:
        yield f"data: {safe_json_dumps({
            'type': 'error',
            'message': f'工作流执行深度超限: {str(e)}'
        })}\n\n"
    except Exception as e:
        yield f"data: {safe_json_dumps({
            'type': 'error',
            'message': f'执行错误: {str(e)}',
            'error_type': type(e).__name__
        })}\n\n"


def get_node_description(node_name: str) -> str:
    """获取节点的中文描述"""
    descriptions = {
        'intent_recognition': '意图识别',
        'data_fetch': '数据获取',
        'route': '路由判断',
        'structured_data': '数据结构化处理',
        'llm_distribution_analysis': '出货分析',
        'llm_stage_analysis': '阶段分析',
        'llm_emotion_analysis': '情绪分析',
        'llm_trading_points_analysis': '买卖点分析',
        'summary': '分析总结',
        'strategy_recommendation': '策略推荐',
        'backtest': '回溯测试',
        'final_report': '生成报告',
        'dialogue': '对话处理',
        'regular_analysis': '常规技术分析'
    }
    return descriptions.get(node_name, node_name)


def get_result_summary(node_name: str, result: Dict[str, Any]) -> str:
    """获取结果的简要摘要"""
    summaries = {
        'llm_stage_analysis': f"阶段: {result.get('stage_name', '未知')}, 置信度: {result.get('confidence', 0):.0%}",
        'llm_distribution_analysis': f"出货规模: {result.get('overall_scale', 'none')}",
        'llm_emotion_analysis': f"情绪: {result.get('emotion_ratio', {}).get('direction', '中性')}, 锚定: {result.get('anchor', {}).get('type', '中性')}",
        'llm_trading_points_analysis': f"买入信号: {len(result.get('buy_signals', []))}个",
        'summary': f"分析完成,置信度: {result.get('confidence', 0):.0%}",
        'strategy_recommendation': f"操作建议: {result.get('operation', '观望')}"
    }
    return summaries.get(node_name, '执行完成')


class StreamAnalyzeRequest(BaseModel):
    """流式分析请求"""
    stock_code: str
    analysis_type: str = 'game_theory'
    run_backtest: bool = False
    context: Optional[Dict[str, Any]] = None


@router.post("/stream")
async def stream_analyze(request: StreamAnalyzeRequest):
    """
    流式分析API - 实时推送每个节点的执行过程
    
    使用Server-Sent Events (SSE)实现流式响应
    
    事件类型:
    - start: 开始分析
    - node_start: 节点开始执行
    - node_result: 节点执行结果
    - complete: 分析完成
    - error: 错误信息
    """
    from core.graph.analysis_graph import compiled_graph
    from core.models.state import AnalysisState
    
    try:
        # 构建初始状态
        initial_state: AnalysisState = {
            'stock_code': request.stock_code,
            'stock_name': '',  # 由data_fetch节点填充
            'analysis_type': request.analysis_type,
            'run_backtest': request.run_backtest,
            'context': request.context or {},
            'dialogue_mode': False
        }
        
        # 返回流式响应
        return StreamingResponse(
            stream_workflow_execution(compiled_graph, initial_state),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用nginx缓冲
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/stream-simple")
async def stream_analyze_simple(request: StreamAnalyzeRequest):
    """
    简化的流式分析API - 模拟流式响应
    适用于不支持异步流的场景
    """
    from core.graph.analysis_graph import compiled_graph
    from core.models.state import AnalysisState
    
    async def simple_stream():
        try:
            # 发送开始事件
            yield f"data: {safe_json_dumps({'type': 'start', 'message': '开始分析...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # 构建初始状态
            initial_state: AnalysisState = {
                'stock_code': request.stock_code,
                'stock_name': '',
                'analysis_type': request.analysis_type,
                'run_backtest': request.run_backtest,
                'context': request.context or {},
                'dialogue_mode': False
            }
            
            # 发送进度事件
            nodes = [
                ('data_fetch', '获取股票数据'),
                ('structured_data', '处理数据'),
                ('llm_distribution_analysis', '分析出货情况'),
                ('llm_stage_analysis', '判断当前阶段'),
                ('llm_emotion_analysis', '分析情绪比例'),
                ('llm_trading_points_analysis', '识别买卖点'),
                ('summary', '生成总结'),
                ('strategy_recommendation', '推荐策略'),
                ('final_report', '生成报告')
            ]
            
            for i, (node_name, description) in enumerate(nodes, 1):
                yield f"data: {safe_json_dumps({
                    'type': 'progress',
                    'node': node_name,
                    'message': description,
                    'progress': int(i / len(nodes) * 100)
                })}\n\n"
                await asyncio.sleep(0.3)
            
            # 同步执行工作流(实际场景)
            result = await compiled_graph.ainvoke(initial_state)
            
            # 发送完成事件
            yield f"data: {safe_json_dumps({
                'type': 'complete',
                'message': '分析完成!',
                'final_report': result.get('final_report', '分析完成')
            })}\n\n"
            
        except Exception as e:
            yield f"data: {safe_json_dumps({
                'type': 'error',
                'message': str(e)
            })}\n\n"
    
    return StreamingResponse(
        simple_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
