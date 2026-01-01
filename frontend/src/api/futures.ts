import { api } from './index';

export interface FuturesAnalysisRequest {
  message: string;
  futures_code?: string;
  analysis_type?: 'all' | 'game_theory' | 'risk' | 'spread' | 'fundamental';
  days?: number;
  session_id?: string;
}

export interface FuturesContract {
  code: string;
  name: string;
  exchange: string;
}

export interface FuturesDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  open_interest: number;
}

export interface FuturesDataResponse {
  success: boolean;
  futures_code: string;
  futures_name: string;
  contract_info: any;
  data: FuturesDataPoint[];
  count: number;
}

/**
 * 获取可用期货合约列表
 */
export function getFuturesContracts() {
  return api.get<{ success: boolean; contracts: FuturesContract[] }>('/api/futures/contracts');
}

/**
 * 获取期货数据
 */
export function getFuturesData(futures_code: string, days: number = 180) {
  return api.get<FuturesDataResponse>('/api/futures/data', {
    params: { futures_code, days }
  });
}

/**
 * 期货分析接口（非流式）
 */
export function analyzeFutures(payload: FuturesAnalysisRequest) {
  return api.post<{
    success: boolean;
    session_id: string;
    report: string;
    data: {
      game_theory?: any;
      risk?: any;
      spread?: any;
      fundamental?: any;
      strategy?: any;
    };
  }>('/api/futures/analyze', payload);
}

