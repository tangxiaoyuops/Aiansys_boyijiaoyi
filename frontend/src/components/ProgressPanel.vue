<template>
  <div class="progress-panel">
    <div class="list">
      <div 
        v-for="(item, index) in progress" 
        :key="item.node + item.timestamp" 
        class="step"
        :class="{ 'step-active': index === progress.length - 1 }"
      >
        <div class="step-indicator">
          <div class="step-icon">
            <svg v-if="index < progress.length - 1" width="12" height="12" viewBox="0 0 12 12" fill="none">
              <circle cx="6" cy="6" r="5" fill="#10B981" stroke="#10B981" stroke-width="2"/>
              <path d="M4 6L5.5 7.5L8 5" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div v-else class="step-spinner"></div>
          </div>
          <div v-if="index < progress.length - 1" class="step-line"></div>
        </div>
        <div class="step-content">
          <div class="step-name">{{ item.message || item.node }}</div>
          <div class="step-time">{{ formatTime(item.timestamp) }}</div>
        </div>
      </div>
      <div v-if="!progress.length" class="empty">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
        <span>等待任务开始...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  progress: { node: string; message: string; timestamp: number }[];
}>();

const formatTime = (t: number) => {
  const d = new Date(t);
  return d.toLocaleTimeString();
};
</script>

<style scoped>
/* 金融科技主题颜色（与FuturesView保持一致） */
.progress-panel {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.progress-panel::-webkit-scrollbar {
  width: 6px;
}

.progress-panel::-webkit-scrollbar-track {
  background: transparent;
}

.progress-panel::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.progress-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}

.step {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  position: relative;
  transition: all 0.3s ease;
  opacity: 0.7;
}

.step-active {
  opacity: 1;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  position: relative;
}

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.step-line {
  flex: 1;
  width: 2px;
  min-height: 32px;
  background: linear-gradient(180deg, #10B981 0%, rgba(139, 92, 246, 0.3) 100%);
  margin-top: 4px;
  border-radius: 1px;
}

.step:last-child .step-line {
  display: none;
}

.step-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: #8B5CF6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-name {
  font-size: 13px;
  font-weight: 500;
  color: #F8FAFC;
  margin-bottom: 4px;
  line-height: 1.4;
  word-wrap: break-word;
}

.step-active .step-name {
  color: #F59E0B;
  font-weight: 600;
}

.step-time {
  font-size: 11px;
  color: #94A3B8;
  font-weight: 400;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 16px;
  color: #64748B;
  text-align: center;
}

.empty svg {
  opacity: 0.5;
}

.empty span {
  font-size: 13px;
  color: #64748B;
}
</style>



