/**
 * 回测相关API
 */
import axios from 'axios';
import { API_BASE_URL } from './index';

export interface BacktestRequest {
  futures_code: string;
  strategy_name: string;
  strategy_params: Record<string, any>;
  days?: number;
  initial_capital?: number;
  commission_rate?: number;
  slippage?: number;
  margin_rate?: number;
  contract_multiplier?: number;
  max_position?: number;
  max_margin_rate?: number;
  stop_loss_ratio?: number;
  take_profit_ratio?: number;
}

export interface StockBacktestRequest {
  stock_code: string;
  strategy_name: string;
  strategy_params: Record<string, any>;
  days?: number;
  initial_capital?: number;
  commission_rate?: number;
  slippage?: number;
  stamp_tax_rate?: number;
  min_commission?: number;
  max_position?: number;
  stop_loss_ratio?: number;
  take_profit_ratio?: number;
}

export interface OptimizationRequest {
  futures_code: string;
  strategy_name: string;
  param_space: Record<string, any[]>;
  days?: number;
  objective?: string;
  initial_capital?: number;
  commission_rate?: number;
  slippage?: number;
  margin_rate?: number;
}

export interface BacktestResult {
  success: boolean;
  results?: {
    equity_curve: number[];
    trade_log: any[];
    daily_stats: any[];
    metrics: {
      total_return: number;
      annual_return: number;
      max_drawdown: number;
      sharpe_ratio: number;
      win_rate: number;
      [key: string]: any;
    };
    config: any;
  };
  error?: string;
}

/**
 * 运行期货回测
 */
export async function runBacktest(request: BacktestRequest): Promise<BacktestResult> {
  const response = await axios.post(`${API_BASE_URL}/api/backtest/run`, request);
  return response.data;
}

/**
 * 运行股票回测
 */
export async function runStockBacktest(request: StockBacktestRequest): Promise<BacktestResult> {
  const response = await axios.post(`${API_BASE_URL}/api/backtest/stock/run`, request);
  return response.data;
}

/**
 * 优化策略参数
 */
export async function optimizeParameters(request: OptimizationRequest): Promise<any> {
  const response = await axios.post(`${API_BASE_URL}/api/backtest/optimize`, request);
  return response.data;
}

/**
 * 对比多个策略
 */
export async function compareStrategies(
  futures_code: string,
  strategies: Array<{ strategy_name: string; strategy_params: Record<string, any> }>,
  days: number = 180
): Promise<any> {
  const response = await axios.post(`${API_BASE_URL}/api/backtest/compare`, {
    futures_code,
    strategies,
    days
  });
  return response.data;
}

