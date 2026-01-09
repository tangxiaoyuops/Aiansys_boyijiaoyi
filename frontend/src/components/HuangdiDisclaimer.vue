<template>
  <div class="huangdi-disclaimer" :class="variant">
    <el-icon class="disclaimer-icon">
      <Warning />
    </el-icon>
    <div class="disclaimer-content">
      <div class="disclaimer-title">{{ title }}</div>
      <div class="disclaimer-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning } from '@element-plus/icons-vue';

interface Props {
  title?: string;
  text: string;
  variant?: 'warning' | 'info' | 'error';
}

withDefaults(defineProps<Props>(), {
  title: '重要提示',
  variant: 'warning',
});
</script>

<script lang="ts">
export default {
  name: 'HuangdiDisclaimer',
};
</script>

<style scoped>
.huangdi-disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  border-left: 4px solid;
}

.huangdi-disclaimer.warning {
  background: #fff7ed;
  border-color: #ff8c00;
  color: #9a3412;
}

.huangdi-disclaimer.info {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
}

.huangdi-disclaimer.error {
  background: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.disclaimer-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.disclaimer-content {
  flex: 1;
}

.disclaimer-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.disclaimer-text {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.9;
}
</style>

