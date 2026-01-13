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

        <!-- 图片消息 -->
        <div v-if="item.type === 'image' && item.imageUrl" class="image-message">
          <div v-if="item.content" class="image-description">
            {{ item.content }}
          </div>
          <img :src="item.imageUrl" alt="上传的图片" class="message-image" />
        </div>
        
        <!-- OCR加载中 -->
        <div v-if="item.type === 'ocr_loading'" class="ocr-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>{{ item.content }}</span>
        </div>
        
        <!-- OCR识别结果 -->
        <div v-if="item.type === 'ocr_result'" class="ocr-result-message">
          <div class="content" v-html="renderMarkdown(item.content)"></div>
          <el-button 
            v-if="item.ocrText" 
            size="small" 
            type="primary" 
            @click="copyOcrText(item.ocrText)"
            style="margin-top: 8px;"
          >
            <el-icon><CopyDocument /></el-icon>
            复制识别结果
          </el-button>
        </div>
        
        <!-- 普通文本消息 -->
        <div
          v-if="!item.type || (item.type !== 'image' && item.type !== 'ocr_loading' && item.type !== 'ocr_result')"
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
import { Loading, CopyDocument } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import MarkdownIt from 'markdown-it';
import type { ChatMessage } from '../stores/chat';
import BacktestChart from './BacktestChart.vue';

const props = defineProps<{
  messages: ChatMessage[];
}>();

const md = new MarkdownIt({ linkify: true, breaks: true });
const listRef = ref<HTMLDivElement | null>(null);

const renderMarkdown = (text: string) => md.render(text || '');

const copyOcrText = (text: string) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

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
  padding: 24px;
  scroll-behavior: smooth;
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.message-list::-webkit-scrollbar {
  width: 8px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 4px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}

.message-row {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.system {
  justify-content: flex-start;
}

.bubble {
  width: 100%;
  max-width: 75%;
  padding: 16px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.bubble.system {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  color: #F8FAFC;
}

.bubble.user {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #F8FAFC;
}

.meta {
  font-size: 12px;
  margin-bottom: 10px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.role {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
}

.bubble.system .role {
  color: #8B5CF6;
}

.bubble.user .role {
  color: #F59E0B;
}

.tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.bubble.system .tag {
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #C4B5FD;
}

.bubble.user .tag {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #FCD34D;
}

.content {
  line-height: 1.7;
  font-size: 14px;
}

.content :deep(p),
.content :deep(li) {
  margin: 0 0 10px 0;
  line-height: 1.7;
  font-size: 14px;
  color: #E2E8F0;
}

.content :deep(p:last-child) {
  margin-bottom: 0;
}

.content :deep(h1),
.content :deep(h2),
.content :deep(h3),
.content :deep(h4) {
  color: #F8FAFC;
  margin: 16px 0 8px;
  font-weight: 600;
  line-height: 1.4;
}

.content :deep(h1) {
  font-size: 20px;
  border-bottom: 2px solid rgba(139, 92, 246, 0.3);
  padding-bottom: 8px;
}

.content :deep(h2) {
  font-size: 18px;
}

.content :deep(h3) {
  font-size: 16px;
}

.content :deep(ul),
.content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.content :deep(li) {
  margin-bottom: 6px;
}

.content :deep(code) {
  background: rgba(0, 0, 0, 0.3);
  padding: 3px 6px;
  border-radius: 4px;
  color: #FBBF24;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.content :deep(pre) {
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.content :deep(pre code) {
  display: block;
  padding: 16px;
  overflow-x: auto;
  background: rgba(15, 23, 42, 0.8);
  color: #E2E8F0;
  border: none;
  font-size: 13px;
  line-height: 1.6;
}

.content :deep(blockquote) {
  border-left: 4px solid #8B5CF6;
  padding-left: 16px;
  margin: 12px 0;
  color: #CBD5E1;
  font-style: italic;
  background: rgba(139, 92, 246, 0.05);
  padding: 12px 16px;
  border-radius: 0 6px 6px 0;
}

.content :deep(a) {
  color: #8B5CF6;
  text-decoration: none;
  border-bottom: 1px solid rgba(139, 92, 246, 0.3);
  transition: all 0.2s ease;
}

.content :deep(a:hover) {
  color: #C4B5FD;
  border-bottom-color: #C4B5FD;
}

.content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
}

.content :deep(th),
.content :deep(td) {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid rgba(139, 92, 246, 0.2);
}

.content :deep(th) {
  background: rgba(139, 92, 246, 0.1);
  font-weight: 600;
  color: #C4B5FD;
}

.image-message {
  margin: 12px 0;
}

.image-description {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: rgba(139, 92, 246, 0.1);
  border-left: 3px solid #8B5CF6;
  border-radius: 4px;
  color: #E2E8F0;
  font-size: 14px;
  line-height: 1.5;
}

.message-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
  cursor: pointer;
  transition: transform 0.2s;
}

.message-image:hover {
  transform: scale(1.02);
}

.ocr-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8B5CF6;
  padding: 12px 0;
}

.ocr-loading .el-icon {
  font-size: 18px;
}

.ocr-result-message {
  margin: 12px 0;
}

.ocr-result-message .content {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}
</style>

