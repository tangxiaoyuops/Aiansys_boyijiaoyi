<template>
  <div class="chat-view">
    <div class="sidebar">
      <ProgressPanel :progress="store.progress" />
    </div>
    <div class="content">
      <MessageList :messages="store.messages" />
      <div class="footer">
        <MessageInput :loading="store.loading" @send="handleSend" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../stores/chat';
import MessageList from '../components/MessageList.vue';
import MessageInput from '../components/MessageInput.vue';
import ProgressPanel from '../components/ProgressPanel.vue';
import { startChatStream } from '../utils/sse';

const store = useChatStore();
let stopStream: (() => void) | null = null;

import { getBaseURL } from '../api';
const baseURL = getBaseURL();

const handleSend = (msg: string) => {
  // 停止上一条流
  if (stopStream) stopStream();

  store.appendMessage({ role: 'user', content: msg });
  store.setLoading(true);
  store.clearProgress();

  const payload = store.buildPayload(msg);
  stopStream = startChatStream({
    baseURL,
    ...payload,
    onEvent: (data) => {
      const type = data.type || 'message';
      if (type === 'start') {
        store.appendMessage({ role: 'system', content: data.message || '开始分析...', type });
      } else if (type === 'progress') {
        store.addProgress(data.node, data.message || data.node);
      } else if (type === 'result') {
        store.appendMessage({ role: 'system', content: data.report || '', type });
      } else if (type === 'detail') {
        // 不再展示巨大的 JSON，只用于承载回测等结构化数据（给图表用）
        store.appendMessage({
          role: 'system',
          content: '',
          type,
          meta: data.data
        });
      } else if (type === 'error') {
        store.appendMessage({ role: 'system', content: `错误：${data.message || ''}`, type });
        store.setLoading(false);
      } else if (type === 'done') {
        store.appendMessage({ role: 'system', content: '分析完成', type });
        store.setLoading(false);
      }
    },
    onError: (err) => {
      store.appendMessage({ role: 'system', content: `流式连接错误：${err?.message || err}`, type: 'error' });
      store.setLoading(false);
    }
  });
};
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: row;
  height: 100%;
  overflow: hidden;
}
.sidebar {
  width: 240px;
  padding: 12px;
  border-right: 1px solid #e5e7eb33;
  flex-shrink: 0;
  overflow-y: auto;
}
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.footer {
  flex-shrink: 0;
  padding: 16px;
  border-top: 1px solid #e5e7eb33;
  background: #f9fafb;
}
</style>
