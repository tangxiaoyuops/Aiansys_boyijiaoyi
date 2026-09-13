"""
工作流编排器
协调整个工作流的执行过程
"""
from typing import Dict, Any, Optional
import logging
from .engine import WorkflowEngine, Workflow
from .router import get_workflow_router
from core.agents.bazi_dialogue_agent import BaziContext

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self):
        """初始化编排器"""
        self.engine = WorkflowEngine(max_workers=5)
        self.router = get_workflow_router()
        self.workflows = {}  # 缓存已加载的工作流
    
    def process_bazi_analysis(
        self,
        user_question: str,
        bazi_context: BaziContext,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        处理八字分析请求
        
        Args:
            user_question: 用户问题
            bazi_context: 八字上下文
            conversation_history: 对话历史
        
        Returns:
            分析结果
        """
        logger.info(f"开始处理八字分析请求: {user_question[:50]}...")
        
        # 第一步:意图识别
        intent_result = self._recognize_intent(
            user_question,
            conversation_history
        )
        
        # 第二步:路由决策
        workflow_name = self.router.route(intent_result, conversation_history)
        
        # 第三步:加载工作流
        workflow = self._load_workflow(workflow_name)
        
        # 第四步:准备输入数据
        input_data = self._prepare_input_data(
            user_question,
            bazi_context,
            conversation_history,
            intent_result
        )
        
        # 第五步:执行工作流
        results = self._execute_workflow(workflow, input_data)
        
        # 第六步:提取最终结果
        final_result = self._extract_final_result(results)
        
        logger.info("八字分析请求处理完成")
        
        return final_result
    
    def _recognize_intent(
        self,
        user_question: str,
        conversation_history: Optional[list]
    ) -> Dict[str, Any]:
        """意图识别"""
        # 创建意图识别节点的输入
        input_data = {
            'user_question': user_question,
            'conversation_history': conversation_history or []
        }
        
        # 加载意图识别工作流
        from .nodes import IntentNode
        intent_node = IntentNode('intent_recognition', {
            'model': 'gpt-4o',
            'timeout': 10
        })
        
        # 执行意图识别
        result = intent_node.run(input_data)
        
        return result
    
    def _load_workflow(self, workflow_name: str) -> Workflow:
        """加载工作流"""
        # 检查缓存
        if workflow_name in self.workflows:
            return self.workflows[workflow_name]
        
        # 加载配置文件
        config_path = self.router.get_workflow_config_path(workflow_name)
        workflow = self.engine.load_workflow(config_path)
        
        # 缓存
        self.workflows[workflow_name] = workflow
        
        return workflow
    
    def _prepare_input_data(
        self,
        user_question: str,
        bazi_context: BaziContext,
        conversation_history: Optional[list],
        intent_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """准备输入数据"""
        
        # 🔍 调试：打印BaziContext的内容
        print(f"[Orchestrator] ========== 准备输入数据 ==========")
        print(f"[Orchestrator] bazi_context.sizhu: {bazi_context.sizhu}")
        print(f"[Orchestrator] bazi_context.wuxing_analysis是否存在: {bazi_context.wuxing_analysis is not None}")
        print(f"[Orchestrator] bazi_context.shishen_analysis是否存在: {bazi_context.shishen_analysis is not None}")
        print(f"[Orchestrator] bazi_context.dayun_analysis是否存在: {bazi_context.dayun_analysis is not None}")
        
        input_data = {
            'user_question': user_question,
            'conversation_history': conversation_history or [],
            'intent': intent_result.get('intent', 'full_analysis'),
            
            # 完整的八字上下文对象(供对话节点使用)
            'bazi_context': {
                'sizhu': bazi_context.sizhu,
                'wuxing_analysis': bazi_context.wuxing_analysis,
                'shishen_analysis': bazi_context.shishen_analysis,
                'dayun_analysis': bazi_context.dayun_analysis,
                'liunian_analysis': bazi_context.liunian_analysis,
                'shensha_analysis': bazi_context.shensha_analysis,
                'llm_analysis': bazi_context.llm_analysis,
                'analysis_style': bazi_context.analysis_style,
                'gender': bazi_context.gender,
                'birth_info': bazi_context.birth_info
            },
            
            # 八字基础数据
            'sizhu': bazi_context.sizhu,
            'gender': bazi_context.gender,
            'birth_info': bazi_context.birth_info,
            
            # 五行数据
            'wuxing_data': bazi_context.wuxing_analysis.get('wuxing_data', {}) if bazi_context.wuxing_analysis else {},
            
            # 十神数据
            'shishen_data': bazi_context.shishen_analysis.get('shishen_data', {}) if bazi_context.shishen_analysis else {},
            
            # 大运数据
            'dayun_list': bazi_context.dayun_analysis.get('dayun_list', []) if bazi_context.dayun_analysis else [],
            'current_dayun': self._get_current_dayun(bazi_context),
            
            # 流年数据
            'liunian_data': bazi_context.liunian_analysis.get('liunian_data', {}) if bazi_context.liunian_analysis else {},
            
            # 神煞数据
            'shensha_data': bazi_context.shensha_analysis.get('shensha_data', {}) if bazi_context.shensha_analysis else {},
            
            # AI分析结果(如果有)
            'llm_analysis': bazi_context.llm_analysis
        }
        
        return input_data
    
    def _get_current_dayun(self, bazi_context: BaziContext) -> Dict[str, Any]:
        """获取当前大运"""
        if not bazi_context.dayun_analysis:
            return {}
        
        dayun_list = bazi_context.dayun_analysis.get('dayun_list', [])
        if not dayun_list:
            return {}
        
        # 计算当前年龄
        from datetime import datetime
        current_year = datetime.now().year
        birth_year = bazi_context.birth_info.get('year', bazi_context.sizhu.get('bazi_year'))
        
        if not birth_year:
            return {}
        
        current_age = current_year - birth_year
        
        # 查找当前大运
        for dy in dayun_list:
            start_age = dy.get('start_age')
            end_age = dy.get('end_age')
            
            try:
                if float(start_age) <= current_age <= float(end_age):
                    return dy
            except (ValueError, TypeError):
                continue
        
        return {}
    
    def _execute_workflow(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工作流"""
        # 判断是否可以并行执行
        can_parallel = self._can_execute_parallel(workflow)
        
        if can_parallel:
            logger.info("使用并行执行模式")
            return self.engine.execute_parallel(workflow, input_data)
        else:
            logger.info("使用顺序执行模式")
            return self.engine.execute_workflow(workflow, input_data)
    
    def _can_execute_parallel(self, workflow: Workflow) -> bool:
        """判断是否可以并行执行"""
        # 检查是否有多个无依赖的节点
        independent_count = 0
        for step in workflow.steps:
            if not step.get('depends_on'):
                independent_count += 1
        
        return independent_count > 1
    
    def _extract_final_result(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """提取最终结果"""
        # 如果有结果整合节点,返回整合结果
        if 'result_integration' in results:
            integration_result = results['result_integration']
            if integration_result.get('status') == 'success':
                return {
                    'success': True,
                    'report': integration_result.get('report', ''),
                    'results': results
                }
        
        # 如果有响应生成节点(对话流程),返回响应
        if 'response_generation' in results:
            response_result = results['response_generation']
            if response_result.get('status') == 'success':
                return {
                    'success': True,
                    'response': response_result.get('response', ''),
                    'results': results
                }
        
        # 如果有快速查询节点,返回查询结果
        if 'quick_query' in results:
            query_result = results['quick_query']
            if query_result.get('status') == 'success':
                return {
                    'success': True,
                    'result': query_result.get('analysis_result', {}).get('content', ''),
                    'results': results
                }
        
        # 默认返回所有结果
        return {
            'success': True,
            'results': results
        }


# 全局实例
_workflow_orchestrator = None

def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """获取工作流编排器实例"""
    global _workflow_orchestrator
    if _workflow_orchestrator is None:
        _workflow_orchestrator = WorkflowOrchestrator()
    return _workflow_orchestrator
