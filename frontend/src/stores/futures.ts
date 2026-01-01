import { defineStore } from 'pinia';
import type { FuturesAnalysisRequest } from '../api/futures';

export type MessageRole = 'user' | 'system';

export interface FuturesMessage {
  id: string;
  role: MessageRole;
  content: string;
  type?: string; // start/progress/result/detail/done/error
  meta?: Record<string, any>;
}

export interface FuturesState {
  messages: FuturesMessage[];
  loading: boolean;
  progress: {
    node: string;
    message: string;
    timestamp: number;
  }[];
  form: {
    futures_code: string;
    analysis_type: 'all' | 'game_theory' | 'risk' | 'spread' | 'fundamental';
    days: number;
  };
  // 分析结果数据
  analysisResults: {
    game_theory?: any;
    risk?: any;
    spread?: any;
    fundamental?: any;
    strategy?: any;
  };
  // 期货数据
  futuresData: {
    code: string;
    name: string;
    data: any[];
  } | null;
  sessionId: string | null;
}

const randomId = () => Math.random().toString(36).slice(2);

export const useFuturesStore = defineStore('futures', {
  state: (): FuturesState => ({
    messages: [],
    loading: false,
    progress: [],
    form: {
      futures_code: '',
      analysis_type: 'all', // 默认全部分析
      days: 180
    },
    analysisResults: {},
    futuresData: null,
    sessionId: null
  }),
  actions: {
    appendMessage(msg: Omit<FuturesMessage, 'id'>) {
      this.messages.push({ ...msg, id: randomId() });
    },
    setLoading(v: boolean) {
      this.loading = v;
    },
    reset() {
      this.messages = [];
      this.progress = [];
      this.analysisResults = {};
      this.futuresData = null;
      this.sessionId = null;
    },
    clearProgress() {
      this.progress = [];
    },
    addProgress(node: string | undefined, message: string | undefined) {
      if (!node && !message) return;
      const key = node || `${Date.now()}`;
      const idx = this.progress.findIndex((p) => p.node === key);
      if (idx >= 0) {
        this.progress[idx] = { node: key, message: message || key, timestamp: Date.now() };
      } else {
        this.progress.push({ node: key, message: message || key, timestamp: Date.now() });
      }
    },
    setAnalysisResults(results: any) {
      this.analysisResults = results;
    },
    setFuturesData(data: any) {
      this.futuresData = data;
    },
    setSessionId(id: string | null) {
      this.sessionId = id;
    },
    buildPayload(message: string): FuturesAnalysisRequest {
      // 如果未填代码，尝试从消息里提取期货代码（如 rb2501）
      let code = this.form.futures_code || undefined;
      if (!code) {
        const m = message.match(/\b([a-zA-Z]+\d{4})\b/);
        if (m) code = m[1];
      }
      return {
        message,
        futures_code: code,
        analysis_type: this.form.analysis_type,
        days: this.form.days,
        session_id: this.sessionId || undefined
      };
    }
  }
});

