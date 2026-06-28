import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export type MessageRole = 'user' | 'assistant';

export interface ZiweiChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  type?: string; // 'analysis' | 'content'
  timestamp: number;
}

export interface ZiweiContext {
  pan_data: Record<string, any> | null;
  si_hua_analysis: Record<string, any> | null;
  daxian_analysis: Record<string, any> | null;
  liunian_analysis: Record<string, any> | null;
  shensha_analysis: Record<string, any> | null;
  geju_analysis: Record<string, any> | null;
  llm_analysis: string | null;
  gender: string;
  birth_info: Record<string, any> | null;
}

const randomId = () => Math.random().toString(36).slice(2);

const defaultZiweiContext: ZiweiContext = {
  pan_data: null,
  si_hua_analysis: null,
  daxian_analysis: null,
  liunian_analysis: null,
  shensha_analysis: null,
  geju_analysis: null,
  llm_analysis: null,
  gender: '男',
  birth_info: null,
};

export const useZiweiChatStore = defineStore('ziweiChat', () => {
  // State
  const messages = ref<ZiweiChatMessage[]>([]);
  const loading = ref(false);
  const conversationId = ref<string | null>(null);
  const ziweiContext = ref<ZiweiContext>({ ...defaultZiweiContext });
  const progressMessage = ref('');
  
  // 分析状态：用于追踪深度分析是否已开始接收内容
  const analysisStarted = ref(false);

  // Getters
  const hasContext = computed(() => ziweiContext.value.pan_data !== null);
  const messageCount = computed(() => messages.value.length);
  const lastMessage = computed(() => messages.value.length > 0 ? messages.value[messages.value.length - 1] : null);
  const analysisMessage = computed(() => messages.value.find(m => m.role === 'assistant' && m.type === 'analysis') || null);
  
  // 获取分析消息的内容长度
  const analysisContentLength = computed(() => {
    const msg = messages.value.find(m => m.role === 'assistant' && m.type === 'analysis');
    return msg?.content?.length || 0;
  });

  // Actions
  function setZiweiContext(context: Partial<ZiweiContext>) {
    ziweiContext.value = {
      ...ziweiContext.value,
      ...context,
    };
  }

  function clearZiweiContext() {
    ziweiContext.value = { ...defaultZiweiContext };
  }

  function appendUserMessage(content: string) {
    messages.value.push({
      id: randomId(),
      role: 'user',
      content,
      type: 'content',
      timestamp: Date.now(),
    });
  }

  function appendAssistantMessage(content: string, type: string = 'content') {
    messages.value.push({
      id: randomId(),
      role: 'assistant',
      content,
      type,
      timestamp: Date.now(),
    });
    if (type === 'analysis') {
      analysisStarted.value = false; // 重置分析状态
    }
  }

  function updateFirstAssistantMessage(content: string, replace: boolean = false) {
    const idx = messages.value.findIndex(m => m.role === 'assistant' && m.type === 'analysis');
    
    if (idx >= 0) {
      if (replace) {
        // 替换内容（用于done事件）
        messages.value[idx] = {
          ...messages.value[idx],
          content: content,
          timestamp: Date.now(),
        };
      } else {
        // 追加内容（用于流式chunk）
        messages.value[idx].content += content;
        messages.value[idx].timestamp = Date.now();
      }
      
      // 标记分析已开始
      if (messages.value[idx].content.length > 0) {
        analysisStarted.value = true;
      }
    } else {
      // 如果没有分析消息，在开头插入
      const newMsg: ZiweiChatMessage = {
        id: randomId(),
        role: 'assistant',
        content,
        type: 'analysis',
        timestamp: Date.now(),
      };
      messages.value.unshift(newMsg);
      if (content.length > 0) {
        analysisStarted.value = true;
      }
    }
  }

  function updateLastAssistantMessage(content: string) {
    const lastIdx = messages.value.length - 1;
    if (lastIdx >= 0 && messages.value[lastIdx].role === 'assistant') {
      messages.value[lastIdx].content += content;
      messages.value[lastIdx].timestamp = Date.now();
    } else {
      appendAssistantMessage(content);
    }
  }

  function setLoading(value: boolean) {
    loading.value = value;
  }

  function setProgressMessage(message: string) {
    progressMessage.value = message;
  }

  function setConversationId(id: string | null) {
    conversationId.value = id;
  }

  function clearMessages() {
    messages.value = [];
    analysisStarted.value = false;
  }

  function reset() {
    messages.value = [];
    loading.value = false;
    conversationId.value = null;
    progressMessage.value = '';
    analysisStarted.value = false;
  }

  function fullReset() {
    reset();
    clearZiweiContext();
  }

  function buildPayload(message: string): Record<string, any> {
    return {
      message,
      conversation_id: conversationId.value,
      pan_data: ziweiContext.value.pan_data,
      si_hua_analysis: ziweiContext.value.si_hua_analysis,
      daxian_analysis: ziweiContext.value.daxian_analysis,
      liunian_analysis: ziweiContext.value.liunian_analysis,
      shensha_analysis: ziweiContext.value.shensha_analysis,
      geju_analysis: ziweiContext.value.geju_analysis,
      llm_analysis: ziweiContext.value.llm_analysis,
      gender: ziweiContext.value.gender,
      birth_info: ziweiContext.value.birth_info,
      chat_history: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        type: m.type || 'content'
      }))
    };
  }

  return {
    // State
    messages,
    loading,
    conversationId,
    ziweiContext,
    progressMessage,
    analysisStarted,
    analysisContentLength,
    // Getters
    hasContext,
    messageCount,
    lastMessage,
    analysisMessage,
    // Actions
    setZiweiContext,
    clearZiweiContext,
    appendUserMessage,
    appendAssistantMessage,
    updateFirstAssistantMessage,
    updateLastAssistantMessage,
    setLoading,
    setProgressMessage,
    setConversationId,
    clearMessages,
    reset,
    fullReset,
    buildPayload,
  };
});
