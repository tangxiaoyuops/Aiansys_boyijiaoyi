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

  // 处理baseURL：如果是开发环境且baseURL为空，使用相对路径（走代理）
  // 如果baseURL包含协议，确保协议正确（HTTP/HTTPS）
  let finalBaseURL = baseURL;
  if (!baseURL || baseURL === '') {
    // 开发环境，使用相对路径走Vite代理
    finalBaseURL = '';
  } else if (baseURL.startsWith('https://') && window.location.protocol === 'http:') {
    // 如果前端是HTTP但baseURL是HTTPS，改为HTTP
    console.warn('[SSE] 检测到协议不匹配，将HTTPS改为HTTP:', baseURL);
    finalBaseURL = baseURL.replace('https://', 'http://');
  }

  const url = new URL('/api/futures/analyze/stream', finalBaseURL || window.location.origin);
  url.searchParams.set('message', message);
  if (futures_code) url.searchParams.set('futures_code', futures_code);
  if (analysis_type) url.searchParams.set('analysis_type', analysis_type);
  if (days) url.searchParams.set('days', days.toString());
  if (session_id) url.searchParams.set('session_id', session_id);

  console.log('[SSE] 连接URL:', url.toString());
  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent(data);
    } catch (e) {
      console.error('解析SSE数据失败:', e);
    }
  };

  eventSource.onerror = (error: Event) => {
    console.error('SSE连接错误:', error);
    
    // 检查EventSource的状态
    let errorMessage = '连接错误';
    if (eventSource.readyState === EventSource.CLOSED) {
      errorMessage = '连接已关闭，可能是服务器错误或网络问题';
    } else if (eventSource.readyState === EventSource.CONNECTING) {
      errorMessage = '连接失败，无法连接到服务器';
    }
    
    // 尝试从错误事件中提取更多信息
    const target = error.target as EventSource;
    if (target) {
      console.error('EventSource状态:', {
        readyState: target.readyState,
        url: target.url,
        withCredentials: target.withCredentials
      });
    }
    
    eventSource.close();
    onEvent({ 
      type: 'error', 
      message: errorMessage,
      details: `URL: ${url.toString()}, ReadyState: ${eventSource.readyState}`
    });
  };

  return () => {
    eventSource.close();
  };
}
