<template>
  <div class="progress-panel card">
    <div class="title">执行进度</div>
    <div class="list">
      <div v-for="item in progress" :key="item.node + item.timestamp" class="step">
        <div class="step-name">{{ item.message || item.node }}</div>
        <div class="step-time">{{ formatTime(item.timestamp) }}</div>
      </div>
      <div v-if="!progress.length" class="empty">等待任务...</div>
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
.progress-panel {
  width: 220px;
  min-height: 200px;
  background: #0b1220;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 12px;
  position: sticky;
  top: 10px;
}
.title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.step {
  padding: 6px 8px;
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 6px;
}
.step-name {
  font-size: 13px;
  color: #e5e7eb;
}
.step-time {
  font-size: 12px;
  color: #9ca3af;
}
.empty {
  font-size: 12px;
  color: #9ca3af;
}
</style>



