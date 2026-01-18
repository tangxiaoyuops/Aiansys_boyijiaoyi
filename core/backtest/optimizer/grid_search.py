"""
网格搜索优化器
"""
from typing import Dict, Any, List, Callable, Optional
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

from ..engine import FuturesBacktestEngine, BacktestConfig


class GridSearchOptimizer:
    """网格搜索参数优化器"""
    
    def __init__(
        self,
        engine: FuturesBacktestEngine,
        strategy_class: type,
        param_space: Dict[str, List[Any]],
        objective: str = 'sharpe_ratio',
        n_jobs: int = -1
    ):
        """
        初始化优化器
        
        Args:
            engine: 回测引擎
            strategy_class: 策略类
            param_space: 参数空间，如 {'fast_ma': [5, 10, 15], 'slow_ma': [20, 30, 40]}
            objective: 优化目标（'sharpe_ratio', 'total_return', 'calmar_ratio'等）
            n_jobs: 并行数（-1表示使用所有CPU）
        """
        self.engine = engine
        self.strategy_class = strategy_class
        self.param_space = param_space
        self.objective = objective
        self.n_jobs = n_jobs if n_jobs > 0 else multiprocessing.cpu_count()
        
        # 生成所有参数组合
        self.param_combinations = self._generate_param_combinations()
    
    def _generate_param_combinations(self) -> List[Dict[str, Any]]:
        """生成所有参数组合"""
        keys = list(self.param_space.keys())
        values = list(self.param_space.values())
        
        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))
        
        return combinations
    
    def _run_single_backtest(self, params: Dict[str, Any], data_dict: Dict[str, Any], config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """运行单次回测（用于并行）"""
        try:
            import pandas as pd
            # 重建数据
            data = pd.DataFrame(data_dict)
            # 重建配置
            config = BacktestConfig(**config_dict)
            
            strategy = self.strategy_class()
            engine = FuturesBacktestEngine(config)
            result = engine.run_backtest(data, strategy, params)
            
            if result.get('success'):
                metrics = result.get('metrics', {})
                objective_value = metrics.get(self.objective, 0.0)
                return {
                    'params': params,
                    'result': result,
                    'objective_value': objective_value,
                    'success': True
                }
            else:
                return {
                    'params': params,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
        except Exception as e:
            return {
                'params': params,
                'success': False,
                'error': str(e)
            }
    
    def optimize(
        self,
        data,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        运行优化
        
        Args:
            data: 回测数据
            progress_callback: 进度回调函数 (current, total)
            
        Returns:
            优化结果 {
                'best_params': 最佳参数,
                'best_result': 最佳回测结果,
                'all_results': 所有结果列表,
                'optimization_summary': 优化摘要
            }
        """
        all_results = []
        total = len(self.param_combinations)
        
        # 准备数据（转换为可序列化格式）
        data_dict = data.to_dict('records')
        config_dict = {
            'initial_capital': self.engine.config.initial_capital,
            'commission_rate': self.engine.config.commission_rate,
            'slippage': self.engine.config.slippage,
            'margin_rate': self.engine.config.margin_rate,
            'contract_multiplier': self.engine.config.contract_multiplier,
            'max_position': self.engine.config.max_position,
            'max_margin_rate': self.engine.config.max_margin_rate,
            'stop_loss_ratio': self.engine.config.stop_loss_ratio,
            'take_profit_ratio': self.engine.config.take_profit_ratio
        }
        
        # 获取策略类名（用于序列化）
        strategy_class_name = f"{self.strategy_class.__module__}.{self.strategy_class.__name__}"
        
        # 简化：不使用并行，直接串行执行（避免序列化问题）
        # 如果需要并行，可以使用线程池或改进序列化方式
        all_results = []
        total = len(self.param_combinations)
        
        for i, params in enumerate(self.param_combinations):
            result = self._run_single_backtest(params, data_dict, config_dict, strategy_class_name)
            all_results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total)
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                all_results.append(result)
                
                if progress_callback:
                    progress_callback(completed, total)
        
        # 过滤成功的结果
        successful_results = [r for r in all_results if r.get('success', False)]
        
        if not successful_results:
            return {
                'success': False,
                'error': '所有参数组合都失败了',
                'all_results': all_results
            }
        
        # 按目标值排序
        successful_results.sort(key=lambda x: x.get('objective_value', 0), reverse=True)
        
        best_result = successful_results[0]
        
        return {
            'success': True,
            'best_params': best_result['params'],
            'best_result': best_result['result'],
            'best_objective_value': best_result['objective_value'],
            'all_results': successful_results,
            'total_combinations': total,
            'successful_combinations': len(successful_results),
            'optimization_summary': {
                'objective': self.objective,
                'best_value': best_result['objective_value'],
                'top_5': [
                    {
                        'params': r['params'],
                        'value': r['objective_value']
                    }
                    for r in successful_results[:5]
                ]
            }
        }

