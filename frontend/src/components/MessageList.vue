<template>

  <div class="message-list" ref="listRef">

    <div

      v-for="item in messages"

      :key="item.id"

      class="message-row"

      :class="item.role"

    >

      <div class="bubble card" :class="item.role">

        <div class="meta">

          <span class="role">{{ item.role === 'user' ? '我' : '系统' }}</span>

          <span v-if="item.type" class="tag">{{ item.type }}</span>

        </div>

        <div

          class="content"

          v-html="renderMarkdown(item.content)"

        />

        <!-- 如果是 detail 消息并且包含回测结果，则在文字下方展示K线图 -->
        <BacktestChart
          v-if="item.type === 'detail' && item.meta && item.meta.backtest"
          :backtest="item.meta.backtest"
        />

      </div>

    </div>

  </div>

</template>



<script setup lang="ts">
import { onMounted, onUpdated, ref } from 'vue';
import MarkdownIt from 'markdown-it';
import type { ChatMessage } from '../stores/chat';
import type { FuturesMessage } from '../stores/futures';
import BacktestChart from './BacktestChart.vue';

// 通用消息类型
type Message = ChatMessage | FuturesMessage;

const props = defineProps<{
  messages: Message[];
}>();

const md = new MarkdownIt({ linkify: true, breaks: true });
const listRef = ref<HTMLDivElement | null>(null);

const renderMarkdown = (text: string) => md.render(text || '');

const scrollToBottom = () => {
  const el = listRef.value;
  if (el) el.scrollTop = el.scrollHeight;
};

onMounted(scrollToBottom);
onUpdated(scrollToBottom);
</script>



<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-row {
  display: flex;
  margin-bottom: 12px;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.system {
  justify-content: flex-start;
}

.bubble {
  width: 100%;
  max-width: 1400px; /* 按你说的大约 1400 像素宽度 */
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
}

.bubble.system {
  background: #ffffff;
}

.bubble.user {
  background: #bfdbfe; /* 稍深的浅蓝色，文字更清晰 */
}

.meta {
  font-size: 12px;
  color: #4b5563;
  margin-bottom: 6px;
  display: flex;
  gap: 8px;
}

.role {
  font-weight: 500;
}

.tag {
  padding: 2px 6px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
}

.content :deep(p),
.content :deep(li) {
  margin: 0 0 6px 0;
  line-height: 1.6;
  font-size: 14px;
  color: #111827; /* 深色正文，提高对比度 */
}

.content :deep(h1),
.content :deep(h2),
.content :deep(h3) {
  color: #111827;
  margin: 8px 0 4px;
}

.content :deep(code) {
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
  color: #111827;
}

.content :deep(pre code) {
  display: block;
  padding: 10px;
  overflow-x: auto;
  background: #111827;
  color: #e5e7eb;
  border-radius: 6px;
}
</style>

