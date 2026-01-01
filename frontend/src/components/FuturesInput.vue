<template>
  <div class="input-bar card">
    <div class="form-row">
      <el-input
        v-model="localMessage"
        type="textarea"
        rows="2"
        placeholder="请输入分析问题，例如：分析rb2501的期货分析"
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
        <el-option label="全部分析" value="all" />
        <el-option label="博弈分析" value="game_theory" />
        <el-option label="风险管理" value="risk" />
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
        placeholder="天数"
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
.input-bar {
  padding: 12px;
  border-top: 1px solid #1f2937;
}
.form-row {
  display: flex;
  gap: 8px;
}
.form-row + .form-row {
  margin-top: 10px;
}
.options {
  align-items: center;
}
</style>

