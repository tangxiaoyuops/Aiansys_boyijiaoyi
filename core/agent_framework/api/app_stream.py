"""
Agent框架 - 流式响应支持
实现实时推送每一步的执行过程
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, Any, AsyncGenerator
import asyncio
import json
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
import numpy as np


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理Pandas、NumPy和datetime类型"""
    
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
    return safe_json_dumps(obj, cls=CustomJSONEncoder, **kwargs)

async def stream_agent_execution(
    agent,
    user_input: Dict[str, Any],
    context: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """
    流式执行Agent,实时推送每一步
    
    Yields:
        str: SSE格式的数据
    """
    from core.agent_framework.agents.base import AgentState
    
    # 初始化状态
    agent._initialize_state(user_input, context)
    
    # 发送开始事件
    yield f"data: {safe_json_dumps({'type': 'start', 'message': '开始分析...'})}\n\n"
    
    iteration = 0
    while not agent.state.task_complete and iteration < agent.max_iterations:
        iteration += 1
        
        # 发送迭代开始事件
        yield f"data: {safe_json_dumps({'type': 'iteration_start', 'iteration': iteration})}\n\n"
        
        # 思考阶段
        yield f"data: {safe_json_dumps({'type': 'thinking', 'message': '正在思考...'})}\n\n"
        decision = agent._think()
        
        # 发送思考结果
        yield f"data: {safe_json_dumps({
            'type': 'thought',
            'iteration': iteration,
            'observation': decision.get('observation', ''),
            'thinking': decision.get('thinking', ''),
            'action': decision.get('action'),
            'evaluation': decision.get('evaluation', {})
        })}\n\n"
        
        # 等待一下,让前端有时间显示
        await asyncio.sleep(0.1)
        
        # 行动阶段
        if decision.get('action'):
            tool_name = decision['action'].get('tool', 'unknown')
            yield f"data: {safe_json_dumps({
                'type': 'action_start',
                'tool': tool_name,
                'parameters': decision['action'].get('parameters', {})
            })}\n\n"
            
            # 执行工具
            result = agent._act(decision)
            
            # 发送执行结果
            yield f"data: {safe_json_dumps({
                'type': 'action_result',
                'tool': tool_name,
                'status': result.get('status'),
                'result': result.get('result') if result.get('status') == 'success' else None,
                'error': result.get('error') if result.get('status') == 'error' else None,
                'execution_time': result.get('execution_time', 0)
            })}\n\n"
        else:
            result = {'status': 'success', 'message': '无工具调用'}
        
        # 更新状态
        agent._update_state(decision, result)
        
        # 判断是否完成
        evaluation = decision.get("evaluation", {})
        agent.state.task_complete = evaluation.get("task_complete", False)
        
        # 发送评估结果
        yield f"data: {safe_json_dumps({
            'type': 'evaluation',
            'task_complete': agent.state.task_complete,
            'reason': evaluation.get('reason', '')
        })}\n\n"
        
        await asyncio.sleep(0.1)
    
    # 生成最终响应
    final_response = agent._generate_final_response()
    
    # 发送完成事件
    yield f"data: {safe_json_dumps({
        'type': 'complete',
        'response': final_response,
        'iterations': iteration,
        'execution_trace': agent.state.execution_history,
        'collected_info': agent.state.collected_info
    })}\n\n"
