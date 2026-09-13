"""
执行引擎
支持工具的并行和串行执行
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
import time


class ExecutionEngine:
    """执行引擎"""
    
    def __init__(self, max_workers: int = 5):
        """
        初始化执行引擎
        
        Args:
            max_workers: 最大并行工作线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.execution_log: List[Dict[str, Any]] = []
        self.max_workers = max_workers
    
    def execute_tool(
        self, 
        tool, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行单个工具
        
        Args:
            tool: 工具实例
            parameters: 工具参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        print(f"[ExecutionEngine] 开始执行工具: {tool.metadata.name}")
        
        result = tool.execute(parameters, context)
        
        execution_time = time.time() - start_time
        
        # 记录日志
        log_entry = {
            "tool_name": tool.metadata.name,
            "tool_type": tool.metadata.tool_type,
            "parameters": parameters,
            "result": result,
            "execution_time": execution_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.execution_log.append(log_entry)
        
        print(f"[ExecutionEngine] 工具执行完成: {tool.metadata.name} ({execution_time:.2f}s)")
        
        return result
    
    def execute_tools_parallel(
        self,
        tools_with_params: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        并行执行多个工具
        
        Args:
            tools_with_params: [{"tool": BaseTool, "parameters": dict}, ...]
            context: 执行上下文
        
        Returns:
            执行结果列表(顺序对应输入)
        """
        print(f"\n[ExecutionEngine] 开始并行执行 {len(tools_with_params)} 个工具")
        
        futures = []
        for item in tools_with_params:
            tool = item["tool"]
            parameters = item["parameters"]
            future = self.executor.submit(
                self.execute_tool, 
                tool, 
                parameters, 
                context
            )
            futures.append(future)
        
        # 等待所有任务完成
        results = []
        for i, future in enumerate(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"[ExecutionEngine] 工具 {i+1} 执行失败: {str(e)}")
                results.append({
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__
                })
        
        print(f"[ExecutionEngine] 并行执行完成\n")
        
        return results
    
    async def execute_tools_async(
        self,
        tools_with_params: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        异步并行执行多个工具
        
        Args:
            tools_with_params: [{"tool": BaseTool, "parameters": dict}, ...]
            context: 执行上下文
        
        Returns:
            执行结果列表
        """
        print(f"\n[ExecutionEngine] 开始异步并行执行 {len(tools_with_params)} 个工具")
        
        async def execute_single(tool, parameters, ctx):
            return await asyncio.to_thread(
                self.execute_tool,
                tool,
                parameters,
                ctx
            )
        
        tasks = [
            execute_single(item["tool"], item["parameters"], context)
            for item in tools_with_params
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[ExecutionEngine] 工具 {i+1} 执行失败: {str(result)}")
                processed_results.append({
                    "status": "error",
                    "error": str(result),
                    "error_type": type(result).__name__
                })
            else:
                processed_results.append(result)
        
        print(f"[ExecutionEngine] 异步并行执行完成\n")
        
        return processed_results
    
    def execute_tools_sequential(
        self,
        tools_with_params: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        顺序执行多个工具
        
        Args:
            tools_with_params: [{"tool": BaseTool, "parameters": dict}, ...]
            context: 执行上下文
        
        Returns:
            执行结果列表
        """
        print(f"\n[ExecutionEngine] 开始顺序执行 {len(tools_with_params)} 个工具")
        
        results = []
        for i, item in enumerate(tools_with_params, 1):
            tool = item["tool"]
            parameters = item["parameters"]
            
            print(f"[ExecutionEngine] 执行第 {i}/{len(tools_with_params)} 个工具")
            
            result = self.execute_tool(tool, parameters, context)
            results.append(result)
            
            # 更新上下文
            if result.get("status") == "success":
                context[f"{tool.metadata.name}_result"] = result.get("result")
        
        print(f"[ExecutionEngine] 顺序执行完成\n")
        
        return results
    
    def execute_dag(
        self,
        dag_nodes: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        按DAG依赖关系执行工具
        
        Args:
            dag_nodes: DAG节点列表,格式:
                [
                    {
                        "id": "step1",
                        "tool": BaseTool,
                        "parameters": dict,
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "tool": BaseTool,
                        "parameters": dict,
                        "depends_on": ["step1"]
                    }
                ]
            context: 执行上下文
        
        Returns:
            执行结果字典 {node_id: result}
        """
        print(f"\n[ExecutionEngine] 开始按DAG执行 {len(dag_nodes)} 个节点")
        
        results: Dict[str, Dict[str, Any]] = {}
        completed_nodes = set()
        
        # 构建依赖图
        dependency_graph = {}
        for node in dag_nodes:
            node_id = node["id"]
            depends_on = node.get("depends_on", [])
            dependency_graph[node_id] = {
                "node": node,
                "depends_on": depends_on
            }
        
        # 拓扑排序执行
        max_iterations = len(dag_nodes) * 2  # 防止死循环
        iteration = 0
        
        while len(completed_nodes) < len(dag_nodes) and iteration < max_iterations:
            iteration += 1
            
            # 找出所有依赖已满足的节点
            ready_nodes = []
            for node_id, info in dependency_graph.items():
                if node_id in completed_nodes:
                    continue
                
                depends_on = info["depends_on"]
                if all(dep in completed_nodes for dep in depends_on):
                    ready_nodes.append(info["node"])
            
            if not ready_nodes:
                print("[ExecutionEngine] 没有可执行的节点,可能存在循环依赖")
                break
            
            print(f"\n[ExecutionEngine] 第{iteration}轮: 执行 {len(ready_nodes)} 个节点")
            
            # 并行执行本轮节点
            tools_with_params = [
                {
                    "tool": node["tool"],
                    "parameters": node["parameters"]
                }
                for node in ready_nodes
            ]
            
            batch_results = self.execute_tools_parallel(tools_with_params, context)
            
            # 记录结果
            for node, result in zip(ready_nodes, batch_results):
                node_id = node["id"]
                results[node_id] = result
                completed_nodes.add(node_id)
                
                # 更新上下文
                if result.get("status") == "success":
                    context[f"{node_id}_result"] = result.get("result")
        
        print(f"\n[ExecutionEngine] DAG执行完成: {len(completed_nodes)}/{len(dag_nodes)} 个节点")
        
        return results
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """获取执行日志"""
        return self.execution_log
    
    def clear_log(self):
        """清空执行日志"""
        self.execution_log.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取执行统计
        
        Returns:
            统计数据
        """
        if not self.execution_log:
            return {
                "total_executions": 0,
                "total_time": 0,
                "average_time": 0
            }
        
        total_time = sum(log["execution_time"] for log in self.execution_log)
        
        return {
            "total_executions": len(self.execution_log),
            "total_time": total_time,
            "average_time": total_time / len(self.execution_log),
            "success_count": sum(1 for log in self.execution_log if log["result"].get("status") == "success"),
            "error_count": sum(1 for log in self.execution_log if log["result"].get("status") == "error")
        }
    
    def shutdown(self):
        """关闭执行引擎"""
        self.executor.shutdown(wait=True)
        print("[ExecutionEngine] 执行引擎已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
