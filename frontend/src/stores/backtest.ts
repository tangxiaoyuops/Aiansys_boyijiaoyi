/**
 * 回测状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { runBacktest, runStockBacktest, optimizeParameters, compareStrategies, type BacktestRequest, type StockBacktestRequest, type OptimizationRequest } from '../api/backtest';

export interface BacktestState {
  loading: boolean;
  results: any | null;
  error: string | null;
  history: any[];
}

export const useBacktestStore = defineStore('backtest', () => {
  const loading = ref(false);
  const results = ref<any | null>(null);
  const error = ref<string | null>(null);
  const history = ref<any[]>([]);

  /**
   * 运行回测
   */
  async function run(request: BacktestRequest | StockBacktestRequest, type: 'futures' | 'stock' = 'futures') {
    loading.value = true;
    error.value = null;
    
    try {
      const result = type === 'futures' 
        ? await runBacktest(request as BacktestRequest)
        : await runStockBacktest(request as StockBacktestRequest);
      
      if (result.success) {
        results.value = result.results;
        history.value.unshift({
          id: Date.now(),
          request,
          type,
          result: result.results,
          timestamp: new Date()
        });
      } else {
        error.value = result.error || '回测失败';
      }
    } catch (e: any) {
      error.value = e.message || '回测失败';
    } finally {
      loading.value = false;
    }
  }

  /**
   * 优化参数
   */
  async function optimize(request: OptimizationRequest) {
    loading.value = true;
    error.value = null;
    
    try {
      const result = await optimizeParameters(request);
      if (result.success) {
        return result.optimization;
      } else {
        error.value = result.error || '优化失败';
        return null;
      }
    } catch (e: any) {
      error.value = e.message || '优化失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 对比策略
   */
  async function compare(
    futures_code: string,
    strategies: Array<{ strategy_name: string; strategy_params: Record<string, any> }>,
    days: number = 180
  ) {
    loading.value = true;
    error.value = null;
    
    try {
      const result = await compareStrategies(futures_code, strategies, days);
      if (result.success) {
        return result.results;
      } else {
        error.value = result.error || '对比失败';
        return null;
      }
    } catch (e: any) {
      error.value = e.message || '对比失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 清除结果
   */
  function clear() {
    results.value = null;
    error.value = null;
  }

  return {
    loading,
    results,
    error,
    history,
    run,
    optimize,
    compare,
    clear
  };
});

