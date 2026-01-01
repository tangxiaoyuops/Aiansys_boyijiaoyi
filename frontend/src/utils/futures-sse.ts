export type FuturesStreamParams = {
  baseURL: string;
  message: string;
  futures_code?: string;
  analysis_type?: string;
  days?: number;
  session_id?: string;
  onEvent: (data: any) => void;
  onError: (err: any) => void;
};

export function startFuturesStream(params: FuturesStreamParams) {
  const url = new URL(`${params.baseURL}/api/futures/analyze/stream`);
  Object.entries({
    message: params.message,
    futures_code: params.futures_code || '',
    analysis_type: params.analysis_type || 'all',
    days: params.days ?? 180,
    session_id: params.session_id || ''
  }).forEach(([k, v]) => {
    if (v) {
      url.searchParams.append(k, String(v));
    }
  });

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

