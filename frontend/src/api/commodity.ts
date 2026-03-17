/**
 * 大宗商品分析API接口
 */
import request from '@/utils/request';

const API_BASE = '/commodity';

export interface AnalyzeRequest {
  commodity_or_chain: string;
  time_range?: { start: string; end: string };
  user_question?: string;
  strategy_type?: string;
  enable_backtest?: boolean;
  max_rounds?: number;
}

export interface StrategyRequest {
  commodity: string;
  strategy_type: string;
  parameters?: Record<string, any>;
  time_range?: { start: string; end: string };
}

export interface BacktestRequest {
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital?: number;
  commission?: number;
}

export interface AnalyzeResponse {
  success: boolean;
  message?: string;
  data?: {
    report: string;
    structured: StructuredData;
    strategies: Strategy[];
    backtest_results: BacktestResult[];
    rounds_used: number;
    total_duration: number;
  };
}

export interface StrategyResponse {
  success: boolean;
  message?: string;
  data?: {
    strategies: Strategy[];
    technical_indicators: TechnicalIndicators;
    market_state: string;
  };
}

export interface BacktestResponse {
  success: boolean;
  message?: string;
  data?: {
    backtest_result: BacktestResult;
    equity_curve: number[];
    drawdown_curve: number[];
    trade_list: Trade[];
  };
}

export interface StrategiesResponse {
  success: boolean;
  data?: {
    strategies: Strategy[];
    total: number;
  };
}

export interface StructuredData {
  commodity_or_chain?: string;
  time_range?: { start: string; end: string };
  market_state?: string;
  structured_analysis?: {
    summary?: string;
    classification?: string;
    key_drivers?: string[];
    supply_chain_summary?: string;
    price_summary?: string;
    confidence?: number;
  };
  technical_indicators?: {
    ma_short?: number;
    ma_medium?: number;
    ma_long?: number;
    macd_dif?: number;
    macd_dea?: number;
    macd_bar?: number;
    rsi?: number;
    bollinger_upper?: number;
    bollinger_middle?: number;
    bollinger_lower?: number;
    atr?: number;
  };
  strategy_signals?: Strategy[];
  risk_metrics?: RiskMetrics;
  backtest_results?: BacktestResult[];
}

export interface Strategy {
  strategy_type: string;
  commodity_id: string;
  contract: string;
  direction: 'long' | 'short';
  entry_price: number;
  target_price: number;
  stop_loss: number;
  position_size: number;
  confidence: number;
  time_horizon: string;
  reasoning: string;
  risk_reward_ratio: number;
  indicators: TechnicalIndicators;
  fundamental_factors: string[];
  generated_at: string;
}

export interface TechnicalIndicators {
  ma_short?: number;
  ma_medium?: number;
  ma_long?: number;
  macd_dif?: number;
  macd_dea?: number;
  macd_bar?: number;
  rsi?: number;
  bollinger_upper?: number;
  bollinger_middle?: number;
  bollinger_lower?: number;
  atr?: number;
  obv?: number;
  adx?: number;
  cci?: number;
  kdj_k?: number;
  kdj_d?: number;
  kdj_j?: number;
}

export interface BacktestResult {
  strategy_id: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  annual_return: number;
  volatility: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  win_rate: number;
  profit_factor: number;
  trade_count: number;
  avg_trade_duration: number;
  best_trade: number;
  worst_trade: number;
  equity_curve: number[];
  drawdown_curve: number[];
  trades?: Trade[];
}

export interface Trade {
  entry_time: string;
  exit_time: string;
  direction: 'long' | 'short';
  entry_price: number;
  exit_price: number;
  position_size: number;
  pnl: number;
  commission: number;
}

export interface RiskMetrics {
  var_95: number;
  var_99: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  volatility: number;
  beta?: number;
  alpha?: number;
  information_ratio?: number;
  risk_assessment?: string;
  risk_recommendations?: string[];
}

export const commodityApi = {
  analyze: (params: AnalyzeRequest): Promise<AnalyzeResponse> => {
    return request.post(`${API_BASE}/analyze`, params);
  },

  generateStrategy: (params: StrategyRequest): Promise<StrategyResponse> => {
    return request.post(`${API_BASE}/strategy`, params);
  },

  backtestStrategy: (params: BacktestRequest): Promise<BacktestResponse> => {
    return request.post(`${API_BASE}/backtest`, params);
  },

  listStrategies: (params: {
    commodity?: string;
    strategy_type?: string;
    limit?: number;
  } = {}): Promise<StrategiesResponse> => {
    return request.get(`${API_BASE}/strategies`, { params });
  },

  healthCheck: (): Promise<{ status: string; service: string }> => {
    return request.get(`${API_BASE}/health`);
  }
};
