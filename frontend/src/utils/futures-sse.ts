import api from '../api';

export interface FuturesStreamParams {
  baseURL: string;
  message: string;
  futures_code?: string;
  analysis_type?: string;
  days?: number;
  session_id?: string;
  onEvent: (data: any) => void;
}

export function startFuturesStream(params: FuturesStreamParams) {
  const { baseURL, message, futures_code, analysis_type, days, session_id, onEvent } = params;

  // baseURL应该已经通过getBaseURL()处理过，确保协议正确
  const url = new URL('/api/futures/analyze/stream', baseURL);
  url.searchParams.set('message', message);
  if (futures_code) url.searchParams.set('futures_code', futures_code);
  if (analysis_type) url.searchParams.set('analysis_type', analysis_type);
  if (days) url.searchParams.set('days', days.toString());
  if (session_id) url.searchParams.set('session_id', session_id);

  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent(data);
    } catch (e) {
      console.error('解析SSE数据失败:', e);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE连接错误:', error);
    eventSource.close();
    onEvent({ type: 'error', message: '连接错误' });
  };

  return () => {
    eventSource.close();
  };
}
