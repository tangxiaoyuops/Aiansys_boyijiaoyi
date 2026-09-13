"""
ReAct Agent实现
基于观察-思考-行动-判断的循环
"""
import json
import re
from typing import Dict, Any
from datetime import datetime, date
from decimal import Decimal
import pandas as pd
import numpy as np
from .base import BaseAgent


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
    return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)


class ReActAgent(BaseAgent):
    """ReAct Agent - 自主规划Agent"""
    
    def _think(self) -> Dict[str, Any]:
        """
        思考阶段: 使用LLM生成决策
        
        Returns:
            决策字典
        """
        # 构建提示词
        prompt = self._build_react_prompt()
        
        print(f"\n[{self.name}] 正在思考...")
        
        try:
            # 调用LLM
            response = self.llm_client.generate(prompt)
            
            print(f"\n[{self.name}] LLM响应:\n{response[:200]}...")
            
            # 解析JSON决策
            decision = self._parse_llm_response(response)
            
            # 记录当前思考
            self.state.current_thought = decision.get("thinking", "")
            
            return decision
            
        except Exception as e:
            print(f"\n[{self.name}] 思考失败: {str(e)}")
            return {
                "observation": f"思考过程出错: {str(e)}",
                "thinking": "出现错误,尝试结束任务",
                "action": None,
                "evaluation": {
                    "task_complete": True,
                    "reason": f"思考过程出错: {str(e)}"
                }
            }
    
    def _act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        行动阶段: 执行工具调用
        
        Args:
            decision: 思考阶段的决策
        
        Returns:
            执行结果
        """
        action = decision.get("action")
        
        # 如果没有action,说明任务已完成
        if not action:
            return {
                "status": "success",
                "message": "无工具调用,任务完成",
                "tool_name": "none"
            }
        
        tool_name = action.get("tool")
        parameters = action.get("parameters", {})
        
        print(f"\n[{self.name}] 准备执行工具")
        print(f"工具: {tool_name}")
        print(f"参数: {safe_json_dumps(parameters)}")
        
        # 获取工具
        try:
            tool = self.tool_registry.get_tool(tool_name)
        except ValueError as e:
            print(f"\n[{self.name}] 工具不存在: {tool_name}")
            return {
                "status": "error",
                "error": f"工具不存在: {tool_name}",
                "error_type": "ToolNotFoundError",
                "tool_name": tool_name
            }
        
        # 执行工具
        context = {
            "collected_info": self.state.collected_info,
            "conversation_history": self.state.conversation_history,
            "current_task": self.state.current_task
        }
        
        print(f"\n[{self.name}] 开始执行工具: {tool_name}")
        result = tool.execute(parameters, context)
        
        return result
    
    def _build_react_prompt(self) -> str:
        """
        构建ReAct提示词
        
        Returns:
            提示词文本
        """
        # 获取工具描述
        tools_description = self.tool_registry.get_tools_description()
        
        # 格式化已收集信息
        collected_info_str = self._format_collected_info()
        
        # 格式化执行历史
        history_str = self._format_execution_history(last_n=3)
        
        prompt = f"""你是一个智能Agent,名为{self.name},能够自主规划并调用工具来完成任务。

# 可用工具列表
{tools_description}

# 当前任务
{self.state.current_task}

# 当前状态
- 迭代次数: {self.state.iteration + 1}/{self.max_iterations}
- 已获取信息:
{collected_info_str}

# 最近执行历史(最后3轮)
{history_str}

# 执行规则
1. 观察: 分析当前状态,识别还需要什么信息
2. 思考: 决定下一步行动,选择最合适的工具
3. 行动: 调用工具并说明参数
4. 判断: 确认任务是否完成

# 重要提示
- 一次只调用一个工具
- 如果信息已经足够,标记任务完成(task_complete: true)
- 最多迭代{self.max_iterations}次,当前第{self.state.iteration + 1}次
- 工具执行失败时,可以尝试其他工具或调整策略
- 不要重复执行已经成功且结果满意的工具

# 输出要求
请严格按照以下JSON格式输出(不要添加任何其他文字):

{{
  "observation": "观察当前状态,分析已有信息和缺失信息(50字以内)",
  "thinking": "思考下一步该做什么,为什么选择这个工具(50字以内)",
  "action": {{
    "tool": "工具名称",
    "parameters": {{
      "参数名": "参数值"
    }}
  }},
  "evaluation": {{
    "task_complete": false,
    "reason": "为什么完成/未完成(20字以内)"
  }}
}}

现在请输出你的决策(JSON格式):
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应,提取JSON决策
        
        Args:
            response: LLM响应文本
        
        Returns:
            决策字典
        """
        try:
            # 尝试直接解析JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON代码块
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 尝试提取裸JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 如果都失败了,返回默认决策
            print(f"\n[{self.name}] 警告: 无法解析LLM响应为JSON")
            return {
                "observation": "无法解析LLM响应",
                "thinking": "响应格式错误,标记任务完成",
                "action": None,
                "evaluation": {
                    "task_complete": True,
                    "reason": "LLM响应格式错误"
                }
            }
    
    def _format_collected_info(self) -> str:
        """格式化已收集信息"""
        if not self.state.collected_info:
            return "暂无已收集信息"
        
        formatted = []
        for tool_name, info in self.state.collected_info.items():
            # 简化显示,只显示关键信息
            if isinstance(info, dict):
                info_str = safe_json_dumps(info)
                if len(info_str) > 200:
                    info_str = info_str[:200] + "..."
                formatted.append(f"  {tool_name}: {info_str}")
            else:
                formatted.append(f"  {tool_name}: {str(info)[:200]}")
        
        return "\n".join(formatted)
    
    def _generate_final_response(self) -> str:
        """
        生成最终响应
        
        Returns:
            最终响应文本
        """
        # 如果有错误,包含错误信息
        if self.state.errors:
            error_info = "\n\n执行过程中的错误:\n" + "\n".join(
                f"- {err}" for err in self.state.errors
            )
        else:
            error_info = ""
        
        # 使用LLM生成最终响应
        prompt = f"""你已完成任务,请根据执行结果生成最终响应。

# 原始任务
{self.state.current_task}

# 已收集信息
{self._format_collected_info()}

# 执行轨迹
{self._format_execution_history(last_n=10)}
{error_info}

# 要求
1. 总结任务执行过程
2. 给出最终结论或答案
3. 语言简洁,重点突出
4. 如果有错误,说明如何处理

请生成最终响应(直接输出,不要JSON格式):
"""
        
        try:
            final_response = self.llm_client.generate(prompt)
            return final_response
        except Exception as e:
            # 如果LLM调用失败,返回基本信息
            return f"""
任务: {self.state.current_task}
状态: {'已完成' if self.state.task_complete else '未完成'}
迭代次数: {self.state.iteration}
收集信息数量: {len(self.state.collected_info)}
错误: {len(self.state.errors)}个
"""
