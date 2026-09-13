<template>
  <div class="agent-message" :class="message.type">
    <!-- 用户消息 -->
    <div v-if="message.role === 'user'" class="user-message">
      <div class="message-avatar">
        <el-icon><User /></el-icon>
      </div>
      <div class="message-content">
        <div class="message-text">{{ message.content }}</div>
      </div>
    </div>

    <!-- 系统消息 -->
    <div v-else class="system-message">
      <div class="message-avatar">
        <el-icon v-if="message.type === 'error'"><WarningFilled /></el-icon>
        <el-icon v-else-if="message.type === 'loading'"><Loading /></el-icon>
        <el-icon v-else><Promotion /></el-icon>
      </div>
      
      <div class="message-content">
        <!-- 加载状态 -->
        <div v-if="message.type === 'loading'" class="loading-state">
          <div class="loading-text">{{ message.content }}</div>
          <el-progress 
            v-if="message.details?.progress"
            :percentage="message.details.progress"
            :show-text="false"
            :stroke-width="3"
          />
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="message.type === 'error'" class="error-content">
          <div class="error-text">{{ message.content }}</div>
        </div>
        
        <!-- 正常消息 -->
        <div v-else class="normal-content">
          <div class="message-text" v-html="formatContent(message.content)"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { User, Promotion, Loading, WarningFilled } from '@element-plus/icons-vue';
import { marked } from 'marked';

interface Props {
  message: {
    role: string;
    content: string;
    type?: string;
    details?: {
      iterations?: number;
      executionTrace?: any[];
      collectedInfo?: any;
      progress?: number;
    };
  };
}

const props = defineProps<Props>();

// 格式化内容(支持Markdown)
const formatContent = (content: string) => {
  if (!content) return '';
  
  try {
    return marked(content, {
      breaks: true,
      gfm: true
    });
  } catch (error) {
    return content;
  }
};
</script>

<style scoped>
.agent-message {
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

/* 用户消息 */
.user-message {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 12px;
}

.user-message .message-avatar {
  order: 2;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.user-message .message-content {
  order: 1;
  max-width: 70%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  border-radius: 12px 12px 0 12px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.user-message .message-text {
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 系统消息 */
.system-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.system-message .message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.system-message .message-content {
  flex: 1;
  max-width: 85%;
}

/* 加载状态 */
.loading-state {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 12px 16px;
}

.loading-text {
  color: #0284c7;
  margin-bottom: 8px;
  font-size: 14px;
}

/* 错误状态 */
.error-content {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px 16px;
}

.error-text {
  color: #dc2626;
  font-size: 14px;
}

/* 正常消息 */
.normal-content {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.message-text {
  line-height: 1.8;
  color: #374151;
  font-size: 14px;
}

/* Markdown样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4) {
  margin-top: 16px;
  margin-bottom: 12px;
  color: #1f2937;
  font-weight: 600;
}

.message-text :deep(h1) { font-size: 20px; }
.message-text :deep(h2) { font-size: 18px; }
.message-text :deep(h3) { font-size: 16px; }
.message-text :deep(h4) { font-size: 15px; }

.message-text :deep(p) {
  margin: 12px 0;
  line-height: 1.8;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.message-text :deep(li) {
  margin: 6px 0;
  line-height: 1.6;
}

.message-text :deep(strong) {
  color: #dc2626;
  font-weight: 600;
}

.message-text :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.message-text :deep(pre) {
  background: #1f2937;
  color: #e5e7eb;
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.message-text :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.message-text :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  padding-left: 16px;
  margin: 12px 0;
  color: #6b7280;
}

.message-text :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid #d1d5db;
  padding: 8px 12px;
  text-align: left;
}

.message-text :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}

/* 配置/欢迎消息特殊样式 */
.agent-message.config .normal-content,
.agent-message.welcome .normal-content {
  background: linear-gradient(135deg, #e0e7ff 0%, #f0e7ff 100%);
  border-color: #c7d2fe;
}
</style>
