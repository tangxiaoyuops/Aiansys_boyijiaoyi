import { defineStore } from 'pinia';
import { ref, computed, reactive } from 'vue';

export type MessageRole = 'user' | 'assistant';

export interface BaziChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  type?: string; // 'analysis' | 'content'
  timestamp: number;
}

export interface BaziContext {
  name: string;  // 姓名（可选）
  sizhu: Record<string, any> | null;
  wuxing_analysis: Record<string, any> | null;
  shishen_analysis: Record<string, any> | null;
  dayun_analysis: Record<string, any> | null;
  liunian_analysis: Record<string, any> | null;
  shensha_analysis: Record<string, any> | null;
  extended_info: Record<string, any> | null;  // 扩展信息（纳音、空亡、命宫等）
  zhi_relations: Record<string, any> | null;  // 地支关系
  gan_relations: Record<string, any> | null;  // 天干关系
  wuxing_xi_ji: Record<string, any> | null;  // 五行喜忌
  llm_analysis: string | null;
  analysis_style: string;
  gender: string;
  birth_info: Record<string, any> | null;
}

// 合盘上下文
export interface HepanContext {
  hepan_type: 'couple' | 'business';
  // 命盘A
  name_a: string;  // 姓名（可选）
  pan_a: Record<string, any> | null;
  birth_info_a: Record<string, any> | null;
  gender_a: string;
  // 命盘B
  name_b: string;  // 姓名（可选）
  pan_b: Record<string, any> | null;
  birth_info_b: Record<string, any> | null;
  gender_b: string;
  // 合盘结果
  hepan_result: Record<string, any> | null;
  llm_analysis: string | null;
}

const randomId = () => Math.random().toString(36).slice(2);

const defaultBaziContext: BaziContext = {
  name: '',
  sizhu: null,
  wuxing_analysis: null,
  shishen_analysis: null,
  dayun_analysis: null,
  liunian_analysis: null,
  shensha_analysis: null,
  extended_info: null,
  zhi_relations: null,
  gan_relations: null,
  wuxing_xi_ji: null,
  llm_analysis: null,
  analysis_style: 'classic',
  gender: '男',
  birth_info: null,
};

const defaultHepanContext: HepanContext = {
  hepan_type: 'couple',
  name_a: '',
  pan_a: null,
  birth_info_a: null,
  gender_a: '男',
  name_b: '',
  pan_b: null,
  birth_info_b: null,
  gender_b: '女',
  hepan_result: null,
  llm_analysis: null,
};

export const useBaziChatStore = defineStore('baziChat', () => {
  // State
  const messages = ref<BaziChatMessage[]>([]);
  const loading = ref(false);
  const conversationId = ref<string | null>(null);
  const baziContext = ref<BaziContext>({ ...defaultBaziContext });
  const hepanContext = ref<HepanContext>({ ...defaultHepanContext });
  const progressMessage = ref('');
  
  // 分析状态：用于追踪深度分析是否已开始接收内容
  const analysisStarted = ref(false);

  // Getters
  const hasContext = computed(() => baziContext.value.sizhu !== null);
  const messageCount = computed(() => messages.value.length);
  const lastMessage = computed(() => messages.value.length > 0 ? messages.value[messages.value.length - 1] : null);
  const analysisMessage = computed(() => messages.value.find(m => m.role === 'assistant' && m.type === 'analysis') || null);
  
  // 获取分析消息的内容长度
  const analysisContentLength = computed(() => {
    const msg = messages.value.find(m => m.role === 'assistant' && m.type === 'analysis');
    return msg?.content?.length || 0;
  });

  // Actions
  function setBaziContext(context: Partial<BaziContext>) {
    baziContext.value = {
      ...baziContext.value,
      ...context,
    };
  }

  function clearBaziContext() {
    baziContext.value = { ...defaultBaziContext };
  }

  function setHepanContext(context: Partial<HepanContext>) {
    hepanContext.value = {
      ...hepanContext.value,
      ...context,
    };
  }

  function clearHepanContext() {
    hepanContext.value = { ...defaultHepanContext };
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
      const newMsg: BaziChatMessage = {
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
    clearBaziContext();
    clearHepanContext();
  }

  function buildPayload(message: string): Record<string, any> {
    return {
      message,
      conversation_id: conversationId.value,
      sizhu: baziContext.value.sizhu,
      wuxing_analysis: baziContext.value.wuxing_analysis,
      shishen_analysis: baziContext.value.shishen_analysis,
      dayun_analysis: baziContext.value.dayun_analysis,
      liunian_analysis: baziContext.value.liunian_analysis,
      shensha_analysis: baziContext.value.shensha_analysis,
      extended_info: baziContext.value.extended_info,
      zhi_relations: baziContext.value.zhi_relations,
      gan_relations: baziContext.value.gan_relations,
      wuxing_xi_ji: baziContext.value.wuxing_xi_ji,
      llm_analysis: baziContext.value.llm_analysis,
      analysis_style: baziContext.value.analysis_style,
      gender: baziContext.value.gender,
      birth_info: baziContext.value.birth_info,
      chat_history: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        type: m.type || 'content'
      }))
    };
  }

  // 构建合盘对话请求载荷
  function buildHepanPayload(message: string): Record<string, any> {
    return {
      message,
      conversation_id: conversationId.value,
      hepan_type: hepanContext.value.hepan_type,
      // 命盘A
      name_a: hepanContext.value.name_a,
      pan_a: hepanContext.value.pan_a,
      birth_info_a: hepanContext.value.birth_info_a,
      gender_a: hepanContext.value.birth_info_a?.gender || '男',
      // 命盘B
      name_b: hepanContext.value.name_b,
      pan_b: hepanContext.value.pan_b,
      birth_info_b: hepanContext.value.birth_info_b,
      gender_b: hepanContext.value.birth_info_b?.gender || '女',
      // 合盘结果
      hepan_result: hepanContext.value.hepan_result,
      llm_analysis: hepanContext.value.llm_analysis,
      // 历史消息
      chat_history: messages.value.map(m => ({
        role: m.role,
        content: m.content,
        type: m.type || 'content'
      }))
    };
  }

  // 是否有合盘上下文
  const hasHepanContext = computed(() => hepanContext.value.pan_a !== null && hepanContext.value.pan_b !== null);

  return {
    // State
    messages,
    loading,
    conversationId,
    baziContext,
    hepanContext,
    progressMessage,
    analysisStarted,
    analysisContentLength,
    // Getters
    hasContext,
    hasHepanContext,
    messageCount,
    lastMessage,
    analysisMessage,
    // Actions
    setBaziContext,
    clearBaziContext,
    setHepanContext,
    clearHepanContext,
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
    buildHepanPayload,
  };
});