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
  // 处理baseURL：如果是开发环境且baseURL为空，使用相对路径（走代理）
  let finalBaseURL = params.baseURL;
  if (!finalBaseURL || finalBaseURL === '') {
    // 开发环境，使用相对路径走Vite代理
    finalBaseURL = '';
  } else if (finalBaseURL.startsWith('https://') && window.location.protocol === 'http:') {
    // 如果前端是HTTP但baseURL是HTTPS，改为HTTP
    console.warn('[SSE] 检测到协议不匹配，将HTTPS改为HTTP:', finalBaseURL);
    finalBaseURL = finalBaseURL.replace('https://', 'http://');
  }

  const url = new URL(`${finalBaseURL || window.location.origin}/api/chat/stream`);
  Object.entries({
    message: params.message,
    stock_code: params.stock_code || '',
    analysis_type: params.analysis_type || 'auto',
    days: params.days ?? 180,
    run_backtest: params.run_backtest ?? false,
    initial_capital: params.initial_capital ?? 100000
  }).forEach(([k, v]) => url.searchParams.append(k, String(v)));

  console.log('[SSE] 连接URL:', url.toString());
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


