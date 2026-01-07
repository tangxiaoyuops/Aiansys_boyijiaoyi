<template>
  <div class="input-bar card">
    <div class="form-row">
      <el-input
        v-model="localMessage"
        type="textarea"
        rows="2"
        placeholder="请输入期货分析问题，例如：分析rb2501的博弈分析"
        :disabled="loading"
      />
    </div>
    <div class="form-row options">
      <el-input
        v-model="form.futures_code"
        placeholder="期货代码(可选)"
        style="max-width: 120px"
        :disabled="loading"
      />
      <el-select
        v-model="form.analysis_type"
        placeholder="分析类型"
        style="max-width: 140px"
        :disabled="loading"
      >
        <el-option label="全部" value="all" />
        <el-option label="博弈分析" value="game_theory" />
        <el-option label="风险分析" value="risk" />
        <el-option label="价差分析" value="spread" />
        <el-option label="基本面" value="fundamental" />
      </el-select>
      <el-input-number
        v-model="form.days"
        :min="30"
        :max="400"
        :step="10"
        :disabled="loading"
        controls-position="right"
      />
      <el-button type="primary" :loading="loading" @click="handleSend">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { useFuturesStore } from '../stores/futures';

const emit = defineEmits<{
  (e: 'send', message: string): void;
}>();

const props = defineProps<{
  loading: boolean;
}>();

const store = useFuturesStore();
const localMessage = ref('');
const form = reactive({ ...store.form });

watch(
  form,
  (v) => {
    store.form = { ...v };
  },
  { deep: true }
);

const handleSend = () => {
  if (!localMessage.value.trim()) return;
  emit('send', localMessage.value.trim());
  localMessage.value = '';
};
</script>

<style scoped>
/* 金融科技主题颜色变量 */
.input-bar {
  padding: 20px;
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.input-bar:hover {
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.form-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.form-row + .form-row {
  margin-top: 16px;
}

.options {
  align-items: center;
  flex-wrap: wrap;
}

/* 深度选择器：覆盖 Element Plus 默认样式 */
:deep(.el-textarea__inner) {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid rgba(139, 92, 246, 0.3) !important;
  border-radius: 8px !important;
  color: #F8FAFC !important;
  font-size: 14px !important;
  padding: 12px 16px !important;
  transition: all 0.3s ease !important;
  backdrop-filter: blur(10px) !important;
}

:deep(.el-textarea__inner::placeholder) {
  color: #64748B !important;
}

:deep(.el-textarea__inner:hover) {
  border-color: rgba(139, 92, 246, 0.5) !important;
}

:deep(.el-textarea__inner:focus) {
  border-color: #8B5CF6 !important;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
  background: rgba(15, 23, 42, 0.8) !important;
}

:deep(.el-input__inner) {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid rgba(139, 92, 246, 0.3) !important;
  border-radius: 6px !important;
  color: #F8FAFC !important;
  font-size: 13px !important;
  height: 36px !important;
  transition: all 0.3s ease !important;
  backdrop-filter: blur(10px) !important;
}

:deep(.el-input__inner::placeholder) {
  color: #64748B !important;
}

:deep(.el-input__inner:hover) {
  border-color: rgba(139, 92, 246, 0.5) !important;
}

:deep(.el-input__inner:focus) {
  border-color: #8B5CF6 !important;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1) !important;
}

:deep(.el-select .el-input__inner) {
  cursor: pointer !important;
}

:deep(.el-select__popper) {
  background: #1E293B !important;
  border: 1px solid rgba(139, 92, 246, 0.3) !important;
  border-radius: 8px !important;
}

:deep(.el-select-dropdown__item) {
  color: #F8FAFC !important;
  background: transparent !important;
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(139, 92, 246, 0.2) !important;
}

:deep(.el-select-dropdown__item.selected) {
  color: #8B5CF6 !important;
  background: rgba(139, 92, 246, 0.15) !important;
}

:deep(.el-input-number) {
  width: auto !important;
}

:deep(.el-input-number .el-input__inner) {
  width: 100px !important;
  text-align: center !important;
}

:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  background: rgba(139, 92, 246, 0.2) !important;
  border-color: rgba(139, 92, 246, 0.3) !important;
  color: #C4B5FD !important;
}

:deep(.el-input-number__decrease:hover),
:deep(.el-input-number__increase:hover) {
  background: rgba(139, 92, 246, 0.3) !important;
  color: #F8FAFC !important;
}

:deep(.el-button) {
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
  padding: 10px 24px !important;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #8B5CF6 0%, #F59E0B 100%) !important;
  border: none !important;
  color: #FFFFFF !important;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #9F7AEA 0%, #FBBF24 100%) !important;
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
  transform: translateY(-2px);
}

:deep(.el-button--primary:active) {
  transform: translateY(0);
}

:deep(.el-button.is-disabled) {
  background: rgba(100, 116, 139, 0.3) !important;
  color: #64748B !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .input-bar {
    padding: 16px;
  }

  .form-row {
    gap: 8px;
  }

  .options {
    flex-direction: column;
    align-items: stretch;
  }

  :deep(.el-input),
  :deep(.el-select) {
    width: 100% !important;
    max-width: 100% !important;
  }

  :deep(.el-button--primary) {
    width: 100%;
  }
}
</style>


