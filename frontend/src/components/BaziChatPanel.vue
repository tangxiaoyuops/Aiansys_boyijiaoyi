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
            v-if="messages.length > 0"
            :icon="Delete" 
            circle 
            size="small" 
            @click="handleClearChat"
          />
        </el-tooltip>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="chat-messages" ref="messagesRef" @scroll="handleScroll" @wheel="handleWheel">
      <!-- 无消息时的空状态 -->
      <div v-if="messages.length === 0" class="empty-state">
        <el-icon :size="48" color="#d4af37"><ChatDotRound /></el-icon>
        <p>{{ emptyStateText }}</p>
      </div>

      <!-- 消息列表 -->
      <div 
        v-for="(message, index) in messages" 
        :key="message.id"
        class="message-item"
        :class="[message.role, { 'analysis': message.type === 'analysis' }]"
      >
        <div class="message-avatar">
          <el-avatar :size="message.type === 'analysis' ? 36 : 32" :class="message.role">
            {{ message.role === 'user' ? '我' : 'AI' }}
          </el-avatar>
        </div>
        <div class="message-content" :class="{ 'full-width': message.type === 'analysis' }">
          <div class="message-meta">
            <span class="role-name">{{ message.role === 'user' ? '我' : (message.type === 'analysis' ? 'AI 解读' : 'AI助手') }}</span>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
          
          <!-- 深度分析消息：内容为空时显示loading -->
          <template v-if="message.type === 'analysis'">
            <div v-if="!message.content || message.content.length === 0" class="loading-content">
              <el-skeleton :rows="8" animated />
              <div class="loading-text">{{ progressMessage || 'AI 正在分析...' }}</div>
            </div>
            <div 
              v-else
              class="message-text analysis-content"
              v-html="renderMarkdown(message.content)"
            />
          </template>
          
          <!-- 普通消息 -->
          <div 
            v-else
            class="message-text" 
            :class="{ 'streaming': message.role === 'assistant' && loading && index === messages.length - 1 }"
            v-html="renderMarkdown(message.content || '')"
          />
        </div>
      </div>

      <!-- 追问时的加载状态 -->
      <div v-if="loading && hasAnyContent" class="loading-indicator">
        <div class="loading-dots"><span></span><span></span><span></span></div>
        <span>{{ progressMessage || '思考中...' }}</span>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        :placeholder="inputPlaceholder"
        :disabled="loading || !hasValidContext"
        @keydown.enter.ctrl="handleSend"
        resize="none"
      />
      <div class="input-actions">
        <div class="quick-questions" v-if="hasValidContext && !loading">
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
          :loading="loading"
          :disabled="!inputMessage.trim() || !hasValidContext"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue';
import { ElMessageBox } from 'element-plus';
import { ChatDotRound, Delete } from '@element-plus/icons-vue';
import MarkdownIt from 'markdown-it';
import { useBaziChatStore } from '../stores/baziChat';
import { startBaziChatStream, startHepanChatStream } from '../api/baziChat';
import { storeToRefs } from 'pinia';

const props = defineProps<{
  llmLoading?: boolean;
  llmProgress?: string;
  mode?: 'single' | 'hepan';  // 单人分析或合盘分析
}>();

const store = useBaziChatStore();
const { messages, loading, progressMessage, hasContext, hasHepanContext } = storeToRefs(store);

const messagesRef = ref<HTMLDivElement | null>(null);
const inputMessage = ref('');
const stopStream = ref<(() => void) | null>(null);

// 用户是否在底部附近（用于智能滚动）
const isNearBottom = ref(true);
// 是否应该自动滚动
const shouldAutoScroll = ref(true);

const md = new MarkdownIt({ linkify: true, breaks: true, html: false });

// 根据模式使用不同的快捷问题
const quickQuestions = computed(() => {
  if (props.mode === 'hepan') {
    return ['感情走势如何？', '性格互补吗？', '需要注意什么？', '未来发展建议'];
  }
  return ['五行缺什么？', '适合什么行业？', '大运走势如何？', '婚姻运势'];
});

// 根据模式检查是否有上下文
const hasValidContext = computed(() => {
  if (props.mode === 'hepan') {
    return hasHepanContext.value;
  }
  return hasContext.value;
});

const inputPlaceholder = computed(() => {
  if (!hasValidContext.value) {
    return props.mode === 'hepan' ? '请先进行合盘分析' : '请先进行八字排盘分析';
  }
  return '输入问题，按 Ctrl+Enter 发送';
});

// 空状态提示文本
const emptyStateText = computed(() => {
  if (props.mode === 'hepan') {
    return '请先进行双人合盘分析';
  }
  return '请先进行八字排盘分析';
});

// 是否有任何消息有内容
const hasAnyContent = computed(() => {
  return messages.value.some(m => m.content && m.content.length > 0);
});

const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const renderMarkdown = (text: string): string => {
  if (!text) return '';
  return md.render(text);
};

// 检查用户是否在底部附近（距离底部100px以内）
const checkIfNearBottom = () => {
  if (messagesRef.value) {
    const { scrollTop, scrollHeight, clientHeight } = messagesRef.value;
    isNearBottom.value = scrollHeight - scrollTop - clientHeight < 100;
  }
};

// 智能滚动：只有在用户位于底部附近时才自动滚动
const scrollToBottomIfNear = () => {
  nextTick(() => {
    if (messagesRef.value && isNearBottom.value && shouldAutoScroll.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
};

// 强制滚动到底部（用于发送新消息时）
const scrollToBottom = () => {
  shouldAutoScroll.value = true;
  isNearBottom.value = true;
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
};

// 监听滚动事件，更新用户位置
const handleScroll = () => {
  checkIfNearBottom();
  // 如果用户手动滚动到底部，恢复自动滚动
  if (isNearBottom.value) {
    shouldAutoScroll.value = true;
  }
};

// 用户向上滚动时，禁用自动滚动
const handleWheel = (e: WheelEvent) => {
  if (e.deltaY < 0) {
    // 向上滚动
    shouldAutoScroll.value = false;
  }
};

const handleSend = async () => {
  const message = inputMessage.value.trim();
  if (!message || loading.value || !hasValidContext.value) return;

  inputMessage.value = '';
  store.appendUserMessage(message);
  store.setLoading(true);
  store.setProgressMessage('正在思考...');

  if (stopStream.value) stopStream.value();

  // 根据模式选择不同的 API
  if (props.mode === 'hepan') {
    // 合盘对话
    const payload = store.buildHepanPayload(message);
    store.appendAssistantMessage('', 'content');

    stopStream.value = startHepanChatStream(
      payload,
      (event) => handleStreamEvent(event),
      (error) => {
        console.error('Stream error:', error);
        store.setLoading(false);
      }
    );
  } else {
    // 单人八字对话
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
  }

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
        scrollToBottomIfNear(); // 智能滚动
      }
      break;
    case 'done':
      store.setLoading(false);
      store.setProgressMessage('');
      scrollToBottomIfNear();
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
  } catch {}
};

// 强制刷新视图
const forceUpdateKey = ref(0);
watch(
  () => messages.value.map(m => m.content?.length || 0).join(','),
  () => {
    forceUpdateKey.value++;
    // 只在深度分析内容变化时智能滚动
    const analysisMsg = messages.value.find(m => m.type === 'analysis');
    if (analysisMsg?.content) {
      scrollToBottomIfNear();
    }
  }
);

onMounted(() => {
  scrollToBottom();
  if (messagesRef.value) {
    messagesRef.value.addEventListener('scroll', handleScroll);
    messagesRef.value.addEventListener('wheel', handleWheel);
  }
});

onUnmounted(() => {
  if (messagesRef.value) {
    messagesRef.value.removeEventListener('scroll', handleScroll);
    messagesRef.value.removeEventListener('wheel', handleWheel);
  }
});
</script>

<style scoped>
.bazi-chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(255, 253, 250, 0.95);
  overflow: hidden;
}

.chat-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(193, 127, 89, 0.08) 100%);
  border-bottom: 1px solid rgba(180, 150, 100, 0.25);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #8B6914;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6B5D4D;
}

.empty-state p { margin-top: 16px; font-size: 14px; }

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

.message-item.analysis {
  margin-bottom: 24px;
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
  background: linear-gradient(135deg, #D4AF37 0%, #C17F59 100%);
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
  color: #6B5D4D;
}

.message-item.user .message-meta {
  justify-content: flex-end;
}

.role-name { font-weight: 600; }

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
  border: 1px solid rgba(180, 150, 100, 0.2);
  color: #3D3226;
  border-bottom-left-radius: 4px;
}

.analysis-content {
  background: rgba(255, 255, 255, 0.9);
  padding: 20px 24px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.9;
  border: 1px solid rgba(180, 150, 100, 0.25);
}

.loading-content {
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  border: 1px solid rgba(180, 150, 100, 0.25);
  width: 100%;
}

.loading-text {
  margin-top: 12px;
  color: #6B5D4D;
  font-size: 14px;
}

.message-text.streaming::after {
  content: '▌';
  animation: blink 1s infinite;
  color: #D4AF37;
}

@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  color: #6B5D4D;
  font-size: 14px;
}

.loading-dots { display: flex; gap: 4px; }
.loading-dots span {
  width: 6px;
  height: 6px;
  background: #D4AF37;
  border-radius: 50%;
  animation: dotPulse 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

.chat-input-area {
  flex-shrink: 0;
  padding: 14px 20px;
  border-top: 1px solid rgba(180, 150, 100, 0.25);
  background: rgba(250, 248, 245, 0.6);
}

.chat-input-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: rgba(180, 150, 100, 0.25);
  font-size: 15px;
  line-height: 1.6;
}

.chat-input-area :deep(.el-textarea__inner:focus) {
  border-color: #D4AF37;
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  gap: 10px;
}

.quick-questions { display: flex; gap: 8px; flex-wrap: wrap; flex: 1; }

.quick-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: #D4AF37;
  color: white;
  border-color: #D4AF37;
}

.input-actions .el-button {
  border-radius: 20px;
  padding: 10px 28px;
  flex-shrink: 0;
}

/* Markdown样式 */
.message-text :deep(p) { margin: 0 0 12px 0; line-height: 1.8; }
.message-text :deep(p:last-child) { margin-bottom: 0; }
.message-text :deep(ul), .message-text :deep(ol) { margin: 12px 0; padding-left: 24px; }
.message-text :deep(li) { margin-bottom: 8px; line-height: 1.7; }
.message-text :deep(strong) { color: #8B6914; }
.message-text :deep(h1), .message-text :deep(h2), .message-text :deep(h3) { 
  margin: 20px 0 12px; color: #3D3226; line-height: 1.4; 
}
.message-text :deep(h1) { font-size: 22px; }
.message-text :deep(h2) { font-size: 18px; border-bottom: 1px solid rgba(180, 150, 100, 0.25); padding-bottom: 8px; }
.message-text :deep(h3) { font-size: 16px; }
.message-text :deep(code) { background: rgba(0, 0, 0, 0.05); padding: 2px 8px; border-radius: 4px; font-size: 14px; }
.message-text :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 18px;
  border-left: 4px solid #D4AF37;
  background: rgba(212, 175, 55, 0.08);
  border-radius: 0 10px 10px 0;
}
</style>