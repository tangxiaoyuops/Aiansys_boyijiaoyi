export type ChatStreamParams = {
  baseURL: string;
  message: string;
  stock_code?: string;
  analysis_type?: string;
  days?: number;
  run_backtest?: boolean;
  initial_capital?: number;
  onEvent: (data: any) => void;
  onError: (err: any) => void;
};

export function startChatStream(params: ChatStreamParams) {
  // baseURL应该已经通过getBaseURL()处理过，确保协议正确
  const url = new URL(`${params.baseURL}/api/chat/stream`);
  Object.entries({
    message: params.message,
    stock_code: params.stock_code || '',
    analysis_type: params.analysis_type || 'auto',
    days: params.days ?? 180,
    run_backtest: params.run_backtest ?? false,
    initial_capital: params.initial_capital ?? 100000
  }).forEach(([k, v]) => url.searchParams.append(k, String(v)));

  const es = new EventSource(url.toString());

  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      params.onEvent(data);
      if (data.type === 'done' || data.type === 'error') {
        es.close();
      }
    } catch (err) {
      params.onError(err);
      es.close();
    }
  };

  es.onerror = (err) => {
    params.onError(err);
    es.close();
  };

  return () => es.close();
}


