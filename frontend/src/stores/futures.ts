import { defineStore } from 'pinia';

export interface FuturesMessage {
  id: string;
  role: 'user' | 'system';
  content: string;
  type?: string;
  meta?: any;
}

export interface FuturesState {
  messages: FuturesMessage[];
  loading: boolean;
  progress: Record<string, string>;
  form: {
    futures_code: string;
    analysis_type: string;
    days: number;
  };
}

export const useFuturesStore = defineStore('futures', {
  state: (): FuturesState => ({
    messages: [],
    loading: false,
    progress: {},
    form: {
      futures_code: '',
      analysis_type: 'all',
      days: 180,
    },
  }),
  actions: {
    appendMessage(message: Omit<FuturesMessage, 'id'>) {
      this.messages.push({
        ...message,
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      });
    },
    setLoading(loading: boolean) {
      this.loading = loading;
    },
    clearProgress() {
      this.progress = {};
    },
    addProgress(node: string, message: string) {
      this.progress[node] = message;
    },
    buildPayload(message: string) {
      return {
        message,
        futures_code: this.form.futures_code || undefined,
        analysis_type: this.form.analysis_type,
        days: this.form.days,
      };
    },
  },
});
