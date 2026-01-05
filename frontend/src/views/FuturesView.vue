<template>
  <div class="futures-view">
    <div class="sidebar">
      <ProgressPanel :progress="store.progress" />
    </div>
    <div class="content">
      <MessageList :messages="store.messages" />
      <div class="footer">
        <FuturesMessageInput :loading="store.loading" @send="handleSend" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFuturesStore } from '../stores/futures';
import MessageList from '../components/MessageList.vue';
import FuturesMessageInput from '../components/FuturesMessageInput.vue';
import ProgressPanel from '../components/ProgressPanel.vue';
import { startFuturesStream } from '../utils/futures-sse';

const store = useFuturesStore();
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
  stopStream = startFuturesStream({
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
        store.appendMessage({
          role: 'system',
          content: '',
          type: 'detail',
          meta: data,
        });
      } else if (type === 'error') {
        store.appendMessage({ role: 'system', content: `错误: ${data.message || '未知错误'}`, type: 'error' });
        store.setLoading(false);
      } else if (type === 'done') {
        store.setLoading(false);
      }
    },
  });
};
</script>

<style scoped>
.futures-view {
  display: flex;
  height: 100%;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  border-right: 1px solid #e5e7eb33;
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
