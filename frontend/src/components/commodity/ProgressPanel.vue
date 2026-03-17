<template>
  <div v-if="visible" class="progress-panel">
    <el-card class="progress-card">
      <div class="progress-header">
        <el-icon class="progress-icon" :size="24">
          <Loading />
        </el-icon>
        <span class="progress-title">分析进度</span>
      </div>

      <div class="progress-content">
        <el-progress
          :percentage="progress"
          :status="progressStatus"
          :stroke-width="18"
          :text-inside="true"
          class="progress-bar"
        />

        <div class="progress-info">
          <div class="info-item">
            <span class="info-label">当前步骤：</span>
            <span class="info-value">{{ currentStep }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">已用时间：</span>
            <span class="info-value">{{ formatTime(elapsedTime) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">预计时间：</span>
            <span class="info-value">{{ formatTime(estimatedTime) }}</span>
          </div>
        </div>
      </div>

      <el-button
        v-if="progress < 100"
        type="danger"
        @click="$emit('cancel')"
        class="cancel-btn"
      >
        取消分析
      </el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Loading } from '@element-plus/icons-vue';

const props = defineProps<{
  visible: boolean;
  progress: number;
  currentStep: string;
  elapsedTime: number;
  estimatedTime: number;
}>();

defineEmits<{
  'cancel': [];
}>();

const progressStatus = computed(() => {
  if (props.progress < 30) return 'exception';
  if (props.progress < 70) return 'warning';
  return 'success';
});

const formatTime = (seconds: number) => {
  if (seconds < 60) return `${seconds}秒`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}分${remainingSeconds}秒`;
};
</script>

<style scoped>
.progress-panel {
  margin-bottom: 20px;
}

.progress-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.progress-icon {
  color: var(--el-color-primary);
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-bar {
  margin-bottom: 10px;
}

:deep(.el-progress__text) {
  font-size: 14px;
  font-weight: 500;
}

.progress-info {
  background-color: #f9fafb;
  padding: 15px;
  border-radius: 6px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.info-label {
  color: #606266;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.cancel-btn {
  margin-top: 10px;
  width: 100%;
}
</style>
