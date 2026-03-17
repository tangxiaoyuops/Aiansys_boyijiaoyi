<template>
  <div class="analysis-form">
    <el-form :model="modelValue" label-width="100px" @submit.prevent="handleSubmit">
      <el-form-item label="品种/产业链" required>
        <el-select
          v-model="modelValue.commodity"
          placeholder="请选择品种或产业链"
          filterable
          clearable
          style="width: 100%"
          @change="handleCommodityChange"
        >
          <el-option
            v-for="item in commodityList"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="时间范围">
        <div class="time-range-wrapper">
          <el-radio-group v-model="timeRangeType" @change="handleTimeRangeChange" class="time-range-group">
            <el-radio-button label="7">7天</el-radio-button>
            <el-radio-button label="30">30天</el-radio-button>
            <el-radio-button label="90">90天</el-radio-button>
            <el-radio-button label="custom">自定义</el-radio-button>
          </el-radio-group>

          <div v-if="timeRangeType === 'custom'" class="custom-date-range">
            <el-date-picker
              v-model="modelValue.timeRange.start"
              type="date"
              placeholder="开始日期"
              value-format="YYYY-MM-DD"
              :clearable="false"
              style="flex: 1"
            />
            <span class="date-separator">至</span>
            <el-date-picker
              v-model="modelValue.timeRange.end"
              type="date"
              placeholder="结束日期"
              value-format="YYYY-MM-DD"
              :clearable="false"
              style="flex: 1"
            />
          </div>
        </div>
      </el-form-item>

      <el-form-item label="策略类型">
        <el-select
          v-model="modelValue.strategyType"
          placeholder="请选择策略类型"
          style="width: 100%"
        >
          <el-option label="趋势跟踪" value="trend" />
          <el-option label="套利" value="arbitrage" />
          <el-option label="套期保值" value="hedge" />
          <el-option label="事件驱动" value="event_driven" />
        </el-select>
      </el-form-item>

      <el-form-item label="用户问题">
        <el-input
          v-model="modelValue.userQuestion"
          type="textarea"
          :rows="3"
          placeholder="例如：关注OPEC会议对供给的影响"
          resize="none"
        />
      </el-form-item>

      <el-divider style="margin: 16px 0" />

      <el-form-item label="分析选项">
        <div class="options-wrapper">
          <el-checkbox v-model="modelValue.enableBacktest" size="large">
            启用回测
          </el-checkbox>
          <div class="max-rounds-wrapper">
            <span class="label-text">最大轮次：</span>
            <el-input-number
              v-model="modelValue.maxRounds"
              :min="1"
              :max="5"
              :step="1"
              controls-position="right"
              style="width: 120px"
            />
          </div>
        </div>
      </el-form-item>

      <el-form-item class="button-group">
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!canSubmit"
          @click="handleSubmit"
          size="large"
          class="submit-btn"
        >
          <el-icon v-if="!loading"><DataAnalysis /></el-icon>
          {{ loading ? '分析中...' : '开始分析' }}
        </el-button>
        <el-button @click="handleReset" size="large" class="reset-btn">
          <el-icon><RefreshLeft /></el-icon>
          清空
        </el-button>
        <el-button @click="handleSave" :disabled="!hasChanges" size="large" class="save-btn">
          <el-icon><DocumentCopy /></el-icon>
          保存配置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { DataAnalysis, RefreshLeft, DocumentCopy } from '@element-plus/icons-vue';
import { useCommodityStore } from '@/stores/commodity';

const props = defineProps<{
  modelValue: {
    commodity: string;
    timeRange: { start: string; end: string };
    strategyType: string;
    userQuestion: string;
    enableBacktest: boolean;
    maxRounds: number;
  };
  loading?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: any];
  'submit': [];
  'reset': [];
  'save': [];
}>();

const commodityStore = useCommodityStore();

const timeRangeType = ref('30');

const commodityList = computed(() => commodityStore.commodityList);
const canSubmit = computed(() => props.modelValue.commodity && !props.loading);
const hasChanges = computed(() => {
  return props.modelValue.commodity !== '' || 
         props.modelValue.userQuestion !== '' ||
         props.modelValue.strategyType !== 'trend' ||
         props.modelValue.maxRounds !== 2;
});

const handleCommodityChange = (value: string) => {
  emit('update:modelValue', { ...props.modelValue, commodity: value });
};

const handleTimeRangeChange = (type: string) => {
  timeRangeType.value = type;
  if (type !== 'custom') {
    const days = parseInt(type);
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);
    
    emit('update:modelValue', {
      ...props.modelValue,
      timeRange: {
        start: formatDate(start),
        end: formatDate(end)
      }
    });
  }
};

const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const handleSubmit = () => {
  if (!canSubmit.value) return;
  emit('submit');
};

const handleReset = () => {
  emit('reset');
};

const handleSave = () => {
  emit('save');
};
</script>

<style scoped>
.analysis-form {
  padding: 20px;
}

.analysis-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.analysis-form :deep(.el-form-item__label) {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  padding-bottom: 8px;
}

.time-range-wrapper {
  width: 100%;
}

.time-range-group {
  width: 100%;
}

.time-range-group :deep(.el-radio-button) {
  flex: 1;
}

.time-range-group :deep(.el-radio-button__inner) {
  width: 100%;
  padding: 10px 0;
  font-size: 14px;
  border: 1px solid #dcdfe6;
}

.time-range-group :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
  color: white;
}

.custom-date-range {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.date-separator {
  color: #909399;
  font-size: 14px;
  margin: 0 4px;
}

.options-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.options-wrapper :deep(.el-checkbox) {
  display: flex;
  align-items: center;
}

.options-wrapper :deep(.el-checkbox__label) {
  font-size: 14px;
  color: #303133;
}

.max-rounds-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.max-rounds-wrapper .label-text {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.button-group {
  margin-top: 32px;
}

.button-group :deep(.el-form-item__content) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.submit-btn .el-icon {
  margin-right: 8px;
}

.reset-btn,
.save-btn {
  width: 100%;
  height: 44px;
}

.reset-btn .el-icon,
.save-btn .el-icon {
  margin-right: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 4px 12px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
  padding: 12px;
}

:deep(.el-input-number) {
  border-radius: 8px;
}

:deep(.el-input-number .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-divider) {
  border-color: #e4e7ed;
  margin: 24px 0;
}
</style>
