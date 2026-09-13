"""
Agent基类和状态管理
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json


class AgentState(BaseModel):
    """Agent状态"""
    iteration: int = Field(default=0, description="当前迭代次数")
    max_iterations: int = Field(default=10, description="最大迭代次数")
    execution_history: List[Dict[str, Any]] = Field(default_factory=list, description="执行历史")
    collected_info: Dict[str, Any] = Field(default_factory=dict, description="已收集的信息")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="对话历史")
    current_task: str = Field(default="", description="当前任务")
    task_complete: bool = Field(default=False, description="任务是否完成")
    final_response: str = Field(default="", description="最终响应")
    current_thought: str = Field(default="", description="当前思考")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    
    class Config:
        arbitrary_types_allowed = True


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        tool_registry,
        llm_client: Any,
        max_iterations: int = 10
    ):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            tool_registry: 工具注册中心实例
            llm_client: LLM客户端实例
            max_iterations: 最大迭代次数
        """
        self.name = name
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.state = AgentState(max_iterations=max_iterations)
    
    def run(
        self, 
        user_input: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        运行Agent
        
        Args:
            user_input: 用户输入 {"task": "任务描述", ...其他参数}
            context: 执行上下文
        
        Returns:
            执行结果
        """
        # 初始化状态
        self._initialize_state(user_input, context)
        
        print(f"\n{'='*60}")
        print(f"[{self.name}] 开始执行任务")
        print(f"任务: {self.state.current_task}")
        print(f"最大迭代次数: {self.max_iterations}")
        print(f"{'='*60}\n")
        
        # ReAct循环
        while not self.state.task_complete and self.state.iteration < self.max_iterations:
            print(f"\n--- 迭代 {self.state.iteration + 1}/{self.max_iterations} ---")
            
            # 观察和思考
            decision = self._think()
            
            if not decision:
                print(f"[{self.name}] 思考失败,终止执行")
                break
            
            # 行动
            result = self._act(decision)
            
            # 更新状态
            self._update_state(decision, result)
            
            # 判断是否完成
            evaluation = decision.get("evaluation", {})
            self.state.task_complete = evaluation.get("task_complete", False)
            
            if self.state.task_complete:
                print(f"\n[{self.name}] 任务完成!")
                print(f"原因: {evaluation.get('reason', '已完成')}")
            
            self.state.iteration += 1
        
        # 检查是否达到最大迭代次数
        if self.state.iteration >= self.max_iterations and not self.state.task_complete:
            print(f"\n[{self.name}] 达到最大迭代次数({self.max_iterations}),强制结束")
        
        # 生成最终响应
        final_response = self._generate_final_response()
        
        print(f"\n{'='*60}")
        print(f"[{self.name}] 执行完成")
        print(f"总迭代次数: {self.state.iteration}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "response": final_response,
            "execution_trace": self.state.execution_history,
            "iterations": self.state.iteration,
            "collected_info": self.state.collected_info,
            "agent_name": self.name
        }
    
    @abstractmethod
    def _think(self) -> Dict[str, Any]:
        """
        思考阶段: 分析状态,决策下一步行动
        
        Returns:
            决策字典,格式:
            {
                "observation": "观察当前状态",
                "thinking": "思考下一步",
                "action": {
                    "tool": "工具名称",
                    "parameters": {...}
                },
                "evaluation": {
                    "task_complete": bool,
                    "reason": "原因"
                }
            }
        """
        pass
    
    @abstractmethod
    def _act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        行动阶段: 执行工具调用
        
        Args:
            decision: 思考阶段的决策
        
        Returns:
            执行结果
        """
        pass
    
    def _initialize_state(
        self, 
        user_input: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ):
        """初始化状态"""
        self.state = AgentState(max_iterations=self.max_iterations)
        self.state.current_task = user_input.get("task", "")
        
        if context:
            self.state.conversation_history = context.get("conversation_history", [])
            self.state.collected_info = context.get("collected_info", {})
    
    def _update_state(self, decision: Dict[str, Any], result: Dict[str, Any]):
        """更新状态"""
        # 记录执行历史
        self.state.execution_history.append({
            "iteration": self.state.iteration + 1,
            "decision": decision,
            "result": result,
            "timestamp": self._get_timestamp()
        })
        
        # 合并收集的信息
        if result.get("status") == "success":
            tool_name = result.get("tool_name", "unknown")
            tool_result = result.get("result", {})
            self.state.collected_info[tool_name] = tool_result
            
            print(f"\n[{self.name}] 工具执行成功")
            print(f"工具: {tool_name}")
            print(f"执行时间: {result.get('execution_time', 0):.2f}秒")
        else:
            error_msg = result.get("error", "未知错误")
            self.state.errors.append(error_msg)
            
            print(f"\n[{self.name}] 工具执行失败")
            print(f"错误: {error_msg}")
    
    @abstractmethod
    def _generate_final_response(self) -> str:
        """
        生成最终响应
        
        Returns:
            最终响应文本
        """
        pass
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """获取执行轨迹"""
        return self.state.execution_history
    
    def get_state(self) -> AgentState:
        """获取当前状态"""
        return self.state
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_execution_history(self, last_n: int = 5) -> str:
        """
        格式化执行历史
        
        Args:
            last_n: 只显示最后N轮
        
        Returns:
            格式化的执行历史文本
        """
        if not self.state.execution_history:
            return "无执行历史"
        
        history = self.state.execution_history[-last_n:]
        formatted = []
        
        for entry in history:
            iteration = entry.get("iteration", "?")
            decision = entry.get("decision", {})
            result = entry.get("result", {})
            
            thinking = decision.get("thinking", "")
            action = decision.get("action", {})
            tool_name = action.get("tool", "none") if action else "none"
            status = result.get("status", "unknown")
            
            formatted.append(
                f"第{iteration}轮:\n"
                f"  思考: {thinking[:100]}...\n"
                f"  行动: {tool_name}\n"
                f"  结果: {status}"
            )
        
        return "\n\n".join(formatted)
