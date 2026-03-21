import { defineStore } from 'pinia';

export type MessageRole = 'user' | 'assistant';

export interface BaziChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  type?: string;
  timestamp: number;
}

export interface BaziContext {
  sizhu: Record<string, any> | null;
  wuxing_analysis: Record<string, any> | null;
  shishen_analysis: Record<string, any> | null;
  dayun_analysis: Record<string, any> | null;
  liunian_analysis: Record<string, any> | null;
  shensha_analysis: Record<string, any> | null;
  llm_analysis: string | null;
  analysis_style: string;
  gender: string;
  birth_info: Record<string, any> | null;
}

export interface BaziChatState {
  messages: BaziChatMessage[];
  loading: boolean;
  conversationId: string | null;
  baziContext: BaziContext;
  progressMessage: string;
}

const randomId = () => Math.random().toString(36).slice(2);

const defaultBaziContext: BaziContext = {
  sizhu: null,
  wuxing_analysis: null,
  shishen_analysis: null,
  dayun_analysis: null,
  liunian_analysis: null,
  shensha_analysis: null,
  llm_analysis: null,
  analysis_style: 'classic',
  gender: '男',
  birth_info: null,
};

export const useBaziChatStore = defineStore('baziChat', {
  state: (): BaziChatState => ({
    messages: [],
    loading: false,
    conversationId: null,
    baziContext: { ...defaultBaziContext },
    progressMessage: '',
  }),

  getters: {
    hasContext: (state): boolean => {
      return state.baziContext.sizhu !== null;
    },
    
    messageCount: (state): number => {
      return state.messages.length;
    },
    
    lastMessage: (state): BaziChatMessage | null => {
      return state.messages.length > 0 ? state.messages[state.messages.length - 1] : null;
    },
  },

  actions: {
    setBaziContext(context: Partial<BaziContext>) {
      this.baziContext = {
        ...this.baziContext,
        ...context,
      };
    },

    clearBaziContext() {
      this.baziContext = { ...defaultBaziContext };
    },

    appendUserMessage(content: string) {
      this.messages.push({
        id: randomId(),
        role: 'user',
        content,
        timestamp: Date.now(),
      });
    },

    appendAssistantMessage(content: string, type: string = 'content') {
      this.messages.push({
        id: randomId(),
        role: 'assistant',
        content,
        type,
        timestamp: Date.now(),
      });
    },

    updateLastAssistantMessage(content: string) {
      const lastIdx = this.messages.length - 1;
      if (lastIdx >= 0 && this.messages[lastIdx].role === 'assistant') {
        this.messages[lastIdx].content += content;
        this.messages[lastIdx].timestamp = Date.now();
      } else {
        this.appendAssistantMessage(content);
      }
    },

    setLoading(loading: boolean) {
      this.loading = loading;
    },

    setProgressMessage(message: string) {
      this.progressMessage = message;
    },

    setConversationId(id: string | null) {
      this.conversationId = id;
    },

    clearMessages() {
      this.messages = [];
    },

    reset() {
      this.messages = [];
      this.loading = false;
      this.conversationId = null;
      this.progressMessage = '';
    },

    fullReset() {
      this.reset();
      this.clearBaziContext();
    },

    buildPayload(message: string): Record<string, any> {
      return {
        message,
        conversation_id: this.conversationId,
        sizhu: this.baziContext.sizhu,
        wuxing_analysis: this.baziContext.wuxing_analysis,
        shishen_analysis: this.baziContext.shishen_analysis,
        dayun_analysis: this.baziContext.dayun_analysis,
        liunian_analysis: this.baziContext.liunian_analysis,
        shensha_analysis: this.baziContext.shensha_analysis,
        llm_analysis: this.baziContext.llm_analysis,
        analysis_style: this.baziContext.analysis_style,
        gender: this.baziContext.gender,
        birth_info: this.baziContext.birth_info,
      };
    },
  },
});