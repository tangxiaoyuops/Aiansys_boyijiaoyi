import { api } from './index';

export interface ChatRequest {
  message: string;
  stock_code?: string;
  analysis_type?: 'auto' | 'regular' | 'game_theory';
  days?: number;
  run_backtest?: boolean;
  initial_capital?: number;
}

export function recognizeIntent(payload: { message: string }) {
  return api.post('/api/intent/recognize', payload);
}

export function chat(payload: ChatRequest) {
  return api.post('/api/chat', payload);
}


