import { defineStore } from 'pinia';
import type { ChatRequest } from '../api/chat';

export type MessageRole = 'user' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  type?: string; // start/progress/result/detail/done/error
  meta?: Record<string, any>;
}

export interface ChatState {
  messages: ChatMessage[];
  loading: boolean;
  progress: {
    node: string;
    message: string;
    timestamp: number;
  }[];
  form: {
    stock_code: string;
    analysis_type: 'auto' | 'regular' | 'game_theory';
    days: number;
    run_backtest: boolean;
    initial_capital: number;
  };
}

const randomId = () => Math.random().toString(36).slice(2);

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    messages: [],
    loading: false,
    progress: [],
    form: {
      stock_code: '',
      analysis_type: 'game_theory', // 默认走博弈分析
      days: 180,
      run_backtest: false,
      initial_capital: 100000
    }
  }),
  actions: {
    appendMessage(msg: Omit<ChatMessage, 'id'>) {
      this.messages.push({ ...msg, id: randomId() });
    },
    setLoading(v: boolean) {
      this.loading = v;
    },
    reset() {
      this.messages = [];
      this.progress = [];
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
    buildPayload(message: string): ChatRequest {
      // 如果未填代码，尝试从消息里提取6位数字
      let code = this.form.stock_code || undefined;
      if (!code) {
        const m = message.match(/\b(\d{6})\b/);
        if (m) code = m[1];
      }
      return {
        message,
        stock_code: code,
        analysis_type: this.form.analysis_type,
        days: this.form.days,
        run_backtest: this.form.run_backtest,
        initial_capital: this.form.initial_capital
      };
    }
  }
});

