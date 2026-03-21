<template>
  <div class="bazi-chat-panel">
    <!-- 标题栏 -->
    <div class="chat-header">
      <div class="header-title">
        <el-icon><ChatDotRound /></el-icon>
        <span>AI 解读与对话</span>
      </div>
      <div class="header-actions">
        <el-tooltip content="清空对话" placement="bottom">
          <el-button 
            v-if="store.messages.length > 0 || hasInitialContent"
            :icon="Delete" 
            circle 
            size="small" 
            @click="handleClearChat"
          />
        </el-tooltip>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="chat-messages" ref="messagesRef">
      <!-- AI深度解析初始消息 -->
      <div v-if="hasInitialContent && !store.messages.length" class="initial-analysis">
        <div class="message-item assistant">
          <div class="message-avatar">
            <el-avatar :size="36" class="assistant">AI</el-avatar>
          </div>
          <div class="message-content full-width">
            <div class="message-meta">
              <span class="role-name">AI 解读</span>
              <span class="message-time">八字分析报告</span>
            </div>
            <div v-if="loading" class="loading-content">
              <el-skeleton :rows="8" animated />
              <div class="loading-text">{{ progress || 'AI 正在分析...' }}</div>
            </div>
            <div v-else class="message-text analysis-content" v-html="renderMarkdown(initialMessage)"></div>
          </div>
        </div>
      </div>

      <!-- 对话消息列表 -->
      <div 
        v-for="message in store.messages" 
        :key="message.id"
        class="message-item"
        :class="message.role"
      >
        <div class="message-avatar">
          <el-avatar :size="32" :class="message.role">
            {{ message.role === 'user' ? '我' : 'AI' }}
          </el-avatar>
        </div>
        <div class="message-content">
          <div class="message-meta">
            <span class="role-name">{{ message.role === 'user' ? '我' : 'AI助手' }}</span>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
          <div 
            class="message-text" 
            :class="{ 'streaming': message.role === 'assistant' && store.loading && isLastMessage(message) }"
            v-html="renderMarkdown(message.content)"
          />
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="store.loading" class="loading-indicator">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
        <span>{{ store.progressMessage || '思考中...' }}</span>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        :placeholder="inputPlaceholder"
        :disabled="store.loading || !store.hasContext"
        @keydown.enter.ctrl="handleSend"
        resize="none"
      />
      <div class="input-actions">
        <div class="quick-questions" v-if="store.hasContext && !store.loading">
          <el-tag 
            v-for="(q, i) in quickQuestions" 
            :key="i" 
            size="small" 
            class="quick-tag"
            @click="handleQuickQuestion(q)"
          >
            {{ q }}
          </el-tag>
        </div>
        <el-button 
          type="primary" 
          :loading="store.loading"
          :disabled="!inputMessage.trim() || !store.hasContext"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { ElMessageBox } from 'element-plus';
import { ChatDotRound, Delete } from '@element-plus/icons-vue';
import MarkdownIt from 'markdown-it';
import { useBaziChatStore } from '../stores/baziChat';
import { startBaziChatStream } from '../api/baziChat';

const props = defineProps<{
  initialMessage?: string;
  loading?: boolean;
  progress?: string;
}>();

const emit = defineEmits<{
  clear: [];
}>();

const store = useBaziChatStore();
const messagesRef = ref<HTMLDivElement | null>(null);
const inputMessage = ref('');
const stopStream = ref<(() => void) | null>(null);

const md = new MarkdownIt({ linkify: true, breaks: true, html: false });

const quickQuestions = ['五行缺什么？', '适合什么行业？', '大运走势如何？', '婚姻运势'];

const hasInitialContent = computed(() => !!props.initialMessage || props.loading);

const inputPlaceholder = computed(() => {
  if (!store.hasContext) return '请先进行八字排盘分析';
  return '输入问题，按 Ctrl+Enter 发送';
});

const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const renderMarkdown = (text: string): string => {
  if (!text) return '';
  return md.render(text);
};

const isLastMessage = (message: any): boolean => {
  return store.messages.length > 0 && store.messages[store.messages.length - 1].id === message.id;
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
};

const handleSend = async () => {
  const message = inputMessage.value.trim();
  if (!message || store.loading || !store.hasContext) return;

  inputMessage.value = '';
  store.appendUserMessage(message);
  store.setLoading(true);
  store.setProgressMessage('正在思考...');

  if (stopStream.value) stopStream.value();

  const payload = store.buildPayload(message);
  store.appendAssistantMessage('', 'content');

  stopStream.value = startBaziChatStream(
    payload,
    (event) => handleStreamEvent(event),
    (error) => {
      console.error('Stream error:', error);
      store.setLoading(false);
    }
  );

  scrollToBottom();
};

const handleStreamEvent = (event: any) => {
  switch (event.type) {
    case 'start':
      if (event.conversation_id) store.setConversationId(event.conversation_id);
      break;
    case 'progress':
      if (event.message) store.setProgressMessage(event.message);
      break;
    case 'content':
      if (event.content) {
        store.updateLastAssistantMessage(event.content);
        scrollToBottom();
      }
      break;
    case 'done':
      store.setLoading(false);
      store.setProgressMessage('');
      scrollToBottom();
      break;
    case 'error':
      store.setLoading(false);
      store.setProgressMessage('');
      store.updateLastAssistantMessage(`\n\n**错误：${event.message || '未知错误'}**`);
      break;
  }
};

const handleQuickQuestion = (q: string) => {
  inputMessage.value = q;
  handleSend();
};

const handleClearChat = async () => {
  try {
    await ElMessageBox.confirm('确定要清空对话记录吗？', '确认', { type: 'warning' });
    store.reset();
    emit('clear');
  } catch {}
};

watch(() => store.messages.length, () => scrollToBottom());
watch(() => props.initialMessage, () => scrollToBottom());
onMounted(() => scrollToBottom());
</script>

<style scoped>
.bazi-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bazi-surface, rgba(255, 253, 250, 0.95));
  overflow: hidden;
}

.chat-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(193, 127, 89, 0.08) 100%);
  border-bottom: 1px solid var(--bazi-border-light, rgba(180, 150, 100, 0.25));
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: var(--bazi-primary, #8B6914);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

/* 初始分析消息 */
.initial-analysis {
  margin-bottom: 20px;
}

.message-item {
  display: flex;
  gap: 14px;
  margin-bottom: 18px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.assistant {
  align-items: flex-start;
}

.message-avatar .el-avatar {
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-avatar .el-avatar.user {
  background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
  color: #1e40af;
}

.message-avatar .el-avatar.assistant {
  background: linear-gradient(135deg, var(--bazi-secondary, #D4AF37) 0%, var(--bazi-accent, #C17F59) 100%);
  color: white;
}

.message-content {
  max-width: 85%;
  min-width: 100px;
}

.message-content.full-width {
  max-width: 95%;
}

.message-item.user .message-content {
  text-align: right;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--bazi-text-light, #6B5D4D);
}

.message-item.user .message-meta {
  justify-content: flex-end;
}

.role-name {
  font-weight: 600;
}

.message-text {
  padding: 14px 18px;
  border-radius: 14px;
  line-height: 1.8;
  font-size: 15px;
  text-align: left;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 100%);
  color: #1e40af;
  border-bottom-right-radius: 4px;
}

.message-item.assistant .message-text {
  background: rgba(212, 175, 55, 0.06);
  border: 1px solid var(--bazi-border-light, rgba(180, 150, 100, 0.2));
  color: var(--bazi-text, #3D3226);
  border-bottom-left-radius: 4px;
}

.analysis-content {
  background: rgba(255, 255, 255, 0.9);
  padding: 20px 24px;
  border-radius: 16px;
  max-width: 100%;
  font-size: 15px;
  line-height: 1.9;
}

.loading-content {
  padding: 20px;
}

.loading-text {
  margin-top: 12px;
  color: var(--bazi-text-light, #6B5D4D);
  font-size: 14px;
}

.message-text.streaming::after {
  content: '▌';
  animation: blink 1s infinite;
  color: var(--bazi-secondary, #D4AF37);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  color: var(--bazi-text-light, #6B5D4D);
  font-size: 14px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: var(--bazi-secondary, #D4AF37);
  border-radius: 50%;
  animation: dotPulse 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 输入区域 */
.chat-input-area {
  flex-shrink: 0;
  padding: 14px 20px;
  border-top: 1px solid var(--bazi-border-light, rgba(180, 150, 100, 0.25));
  background: rgba(250, 248, 245, 0.6);
}

.chat-input-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: var(--bazi-border-light, rgba(180, 150, 100, 0.25));
  font-size: 15px;
  line-height: 1.6;
}

.chat-input-area :deep(.el-textarea__inner:focus) {
  border-color: var(--bazi-secondary, #D4AF37);
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  gap: 10px;
}

.quick-questions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
}

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: var(--bazi-secondary, #D4AF37);
  color: white;
  border-color: var(--bazi-secondary, #D4AF37);
}

.input-actions .el-button {
  border-radius: 20px;
  padding: 10px 28px;
  flex-shrink: 0;
}

/* Markdown样式 - 优化长文本阅读 */
.message-text :deep(p) { 
  margin: 0 0 12px 0; 
  line-height: 1.8;
}
.message-text :deep(p:last-child) { margin-bottom: 0; }
.message-text :deep(ul), .message-text :deep(ol) { 
  margin: 12px 0; 
  padding-left: 24px; 
}
.message-text :deep(li) { 
  margin-bottom: 8px; 
  line-height: 1.7; 
}
.message-text :deep(strong) { 
  color: var(--bazi-primary, #8B6914); 
}
.message-text :deep(h1), .message-text :deep(h2), .message-text :deep(h3) { 
  margin: 20px 0 12px; 
  color: var(--bazi-text, #3D3226);
  line-height: 1.4;
}
.message-text :deep(h1) { font-size: 22px; }
.message-text :deep(h2) { 
  font-size: 18px; 
  border-bottom: 1px solid var(--bazi-border-light); 
  padding-bottom: 8px; 
}
.message-text :deep(h3) { font-size: 16px; }
.message-text :deep(code) { 
  background: rgba(0, 0, 0, 0.05); 
  padding: 2px 8px; 
  border-radius: 4px; 
  font-size: 14px; 
}
.message-text :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 18px;
  border-left: 4px solid var(--bazi-secondary, #D4AF37);
  background: rgba(212, 175, 55, 0.08);
  border-radius: 0 10px 10px 0;
  font-style: italic;
}
.message-text :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
}
.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid var(--bazi-border-light);
  padding: 8px 12px;
  text-align: left;
}
.message-text :deep(th) {
  background: rgba(212, 175, 55, 0.1);
  font-weight: 600;
}
</style>