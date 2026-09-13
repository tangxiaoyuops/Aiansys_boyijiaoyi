"""
工作流引擎
"""
from typing import Dict, Any, List, Optional
import yaml
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .nodes import BaseNode, IntentNode, AnalysisNode, IntegrationNode

logger = logging.getLogger(__name__)


class Workflow:
    """工作流"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化工作流
        
        Args:
            config: 工作流配置
        """
        self.name = config.get('name', 'unnamed_workflow')
        self.description = config.get('description', '')
        self.steps = config.get('steps', [])
    
    def get_execution_order(self) -> List[Dict[str, Any]]:
        """
        获取执行顺序
        
        Returns:
            步骤列表（按依赖关系排序）
        """
        # 简单实现：按照配置顺序执行
        # TODO: 实现拓扑排序，处理复杂依赖关系
        return self.steps


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, max_workers: int = 5):
        """
        初始化工作流引擎
        
        Args:
            max_workers: 最大并行工作线程数
        """
        self.nodes = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._register_node_types()
    
    def _register_node_types(self):
        """注册节点类型"""
        from .nodes import (
            IntentNode, AnalysisNode, IntegrationNode, WuxingAnalysisNode,
            ShishenAnalysisNode, DayunAnalysisNode, LiunianAnalysisNode, DialogueNode
        )
        
        self.node_types = {
            'intent_node': IntentNode,
            'analysis_node': AnalysisNode,
            'integration_node': IntegrationNode,
            'wuxing_analysis_node': WuxingAnalysisNode,
            'shishen_analysis_node': ShishenAnalysisNode,
            'dayun_analysis_node': DayunAnalysisNode,
            'liunian_analysis_node': LiunianAnalysisNode,
            'dialogue_node': DialogueNode
        }
    
    def load_workflow(self, workflow_config_path: str) -> Workflow:
        """
        加载工作流配置
        
        Args:
            workflow_config_path: 工作流配置文件路径
        
        Returns:
            工作流对象
        """
        with open(workflow_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        workflow = Workflow(config)
        logger.info(f"加载工作流: {workflow.name}")
        
        return workflow
    
    def execute_workflow(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow: 工作流对象
            input_data: 输入数据
        
        Returns:
            执行结果
        """
        logger.info(f"开始执行工作流: {workflow.name}")
        
        results = {}
        execution_order = workflow.get_execution_order()
        
        for step in execution_order:
            step_id = step['id']
            step_type = step['type']
            step_config = step.get('config', {})
            depends_on = step.get('depends_on', [])
            
            logger.info(f"执行步骤: {step_id} ({step_type})")
            
            # 准备输入数据
            step_input = input_data.copy()
            
            # 添加依赖节点的结果
            for dep_id in depends_on:
                if dep_id in results:
                    dep_result = results[dep_id]
                    # 将依赖结果合并到输入数据
                    step_input[f"{dep_id}_result"] = dep_result
            
            # 创建并执行节点
            node = self._create_node(step_type, step_id, step_config)
            result = node.run(step_input)
            
            results[step_id] = result
            
            # 如果节点执行失败，记录错误但继续执行
            if result.get('status') == 'error':
                logger.error(f"步骤 {step_id} 执行失败: {result.get('error')}")
        
        logger.info(f"工作流执行完成: {workflow.name}")
        
        return results
    
    def _create_node(
        self,
        node_type: str,
        node_id: str,
        config: Dict[str, Any]
    ) -> BaseNode:
        """
        创建节点实例
        
        Args:
            node_type: 节点类型
            node_id: 节点ID
            config: 节点配置
        
        Returns:
            节点实例
        """
        node_class = self.node_types.get(node_type)
        
        if not node_class:
            raise ValueError(f"未知的节点类型: {node_type}")
        
        return node_class(node_id, config)
    
    def execute_parallel(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        并行执行工作流（无依赖节点并行执行）
        
        Args:
            workflow: 工作流对象
            input_data: 输入数据
        
        Returns:
            执行结果
        """
        logger.info(f"开始并行执行工作流: {workflow.name}")
        
        results = {}
        execution_order = workflow.get_execution_order()
        
        # 按依赖关系分组
        independent_steps = []
        dependent_steps = []
        
        for step in execution_order:
            if not step.get('depends_on'):
                independent_steps.append(step)
            else:
                dependent_steps.append(step)
        
        # 并行执行无依赖节点
        futures = {}
        for step in independent_steps:
            step_id = step['id']
            step_type = step['type']
            step_config = step.get('config', {})
            
            node = self._create_node(step_type, step_id, step_config)
            future = self.executor.submit(node.run, input_data.copy())
            futures[future] = step_id
        
        # 收集并行执行结果
        for future in as_completed(futures):
            step_id = futures[future]
            try:
                result = future.result()
                results[step_id] = result
                logger.info(f"步骤 {step_id} 执行完成")
            except Exception as e:
                logger.error(f"步骤 {step_id} 执行失败: {str(e)}")
                results[step_id] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 顺序执行有依赖节点
        for step in dependent_steps:
            step_id = step['id']
            step_type = step['type']
            step_config = step.get('config', {})
            depends_on = step.get('depends_on', [])
            
            # 准备输入数据
            step_input = input_data.copy()
            for dep_id in depends_on:
                if dep_id in results:
                    step_input[f"{dep_id}_result"] = results[dep_id]
            
            # 执行节点
            node = self._create_node(step_type, step_id, step_config)
            result = node.run(step_input)
            results[step_id] = result
        
        logger.info(f"工作流并行执行完成: {workflow.name}")
        
        return results
