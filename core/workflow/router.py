"""
路由决策器
根据意图识别结果,选择合适的工作流
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class WorkflowRouter:
    """工作流路由决策器"""
    
    def __init__(self):
        """初始化路由器"""
        self.intent_workflow_map = {
            'full_analysis': 'simplified_analysis',  # 使用简化版,提升速度
            'career_analysis': 'simplified_analysis',  # 使用简化版
            'wealth_analysis': 'simplified_analysis',  # 使用简化版
            'marriage_analysis': 'simplified_analysis',  # 使用简化版
            'health_analysis': 'simplified_analysis',  # 使用简化版
            'year_analysis': 'simplified_analysis',  # 使用简化版
            'follow_up': 'conversation',  # 多轮对话使用对话流程
            'quick_query': 'quick_query'  # 快速查询使用快速查询流程
        }
    
    def route(
        self,
        intent_result: Dict[str, Any],
        conversation_history: Optional[list] = None
    ) -> str:
        """
        根据意图识别结果路由到对应的工作流
        
        Args:
            intent_result: 意图识别结果,包含 intent, confidence, reason
            conversation_history: 对话历史
        
        Returns:
            工作流名称
        """
        intent = intent_result.get('intent', 'full_analysis')
        confidence = intent_result.get('confidence', 0.5)
        
        # 如果置信度太低,使用完整分析
        if confidence < 0.6:
            logger.warning(f"意图识别置信度过低({confidence}),使用完整分析")
            return 'full_analysis'
        
        # 根据意图映射到工作流
        workflow_name = self.intent_workflow_map.get(intent, 'full_analysis')
        
        # 🔧 关键修复：如果有对话历史，优先使用对话流程
        # 除非用户明确要求重新分析或专门分析某年
        if conversation_history and len(conversation_history) > 0:
            # 如果意图是follow_up或quick_query，强制使用conversation
            if intent in ['follow_up', 'quick_query']:
                workflow_name = 'conversation'
            # 如果意图是year_analysis，也使用conversation（因为是追问细节）
            elif intent == 'year_analysis':
                # 检查是否是追问性质
                workflow_name = 'conversation'
                logger.info(f"检测到对话历史，将year_analysis路由到conversation工作流")
        
        logger.info(f"意图'{intent}'路由到工作流'{workflow_name}'")
        
        return workflow_name
    
    def get_workflow_config_path(self, workflow_name: str) -> str:
        """
        获取工作流配置文件路径
        
        Args:
            workflow_name: 工作流名称
        
        Returns:
            配置文件路径
        """
        import os
        base_path = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(
            base_path,
            'config',
            'workflows',
            f'{workflow_name}.yaml'
        )
        
        return config_path


# 全局实例
_workflow_router = None

def get_workflow_router() -> WorkflowRouter:
    """获取工作流路由器实例"""
    global _workflow_router
    if _workflow_router is None:
        _workflow_router = WorkflowRouter()
    return _workflow_router
