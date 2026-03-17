<template>
  <el-card class="strategy-card" :class="directionClass">
      <div class="card-header">
        <el-tag
          :type="strategyTypeTag"
          size="large"
          effect="dark"
        >
          {{ strategyTypeText }}
        </el-tag>
        <el-tag
          :type="directionTag"
          size="large"
          effect="dark"
        >
          {{ directionText }}
        </el-tag>
        <div class="confidence-badge">
          <el-tooltip :content="`置信度: ${confidence}%`">
            <el-progress
              type="circle"
              :percentage="confidence"
              :width="50"
              :stroke-width="6"
              :show-text="false"
            />
          </el-tooltip>
        </div>
      </div>

      <div class="card-body">
        <div class="price-info">
          <div class="price-item">
            <span class="label">入场价</span>
            <span class="value entry-price">${{ entryPrice.toFixed(2) }}</span>
          </div>
          <div class="price-item">
            <span class="label">目标价</span>
            <span class="value target-price">${{ targetPrice.toFixed(2) }}</span>
          </div>
          <div class="price-item">
            <span class="label">止损价</span>
            <span class="value stop-loss">${{ stopLoss.toFixed(2) }}</span>
          </div>
        </div>

        <div class="metrics-info">
          <div class="metric-item">
            <span class="label">仓位规模</span>
            <span class="value">{{ positionSize }}手</span>
          </div>
          <div class="metric-item">
            <span class="label">风险收益比</span>
            <span class="value">{{ riskRewardRatio.toFixed(2) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">时间周期</span>
            <span class="value">{{ timeHorizonText }}</span>
          </div>
        </div>

        <div class="reasoning-section">
          <div class="reasoning-title">策略逻辑</div>
          <div class="reasoning-content">{{ reasoning }}</div>
        </div>

        <div v-if="showActions" class="actions-section">
          <el-button
            type="primary"
            size="small"
            @click="$emit('view-backtest')"
          >
            查看回测
          </el-button>
          <el-button
            size="small"
            @click="$emit('edit-strategy')"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="$emit('delete-strategy')"
          >
            删除
          </el-button>
        </div>
      </div>
    </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TrendCharts, Edit, Delete, View } from '@element-plus/icons-vue';

const props = defineProps<{
  strategy: {
    strategy_type: string;
    commodity_id: string;
    contract: string;
    direction: 'long' | 'short';
    entry_price: number;
    target_price: number;
    stop_loss: number;
    position_size: number;
    confidence: number;
    time_horizon: string;
    reasoning: string;
    risk_reward_ratio: number;
  };
  showActions?: boolean;
}>();

defineEmits<{
  'view-backtest': [];
  'edit-strategy': [];
  'delete-strategy': [];
}>();

const directionClass = computed(() => {
  return props.strategy.direction === 'long' ? 'long-card' : 'short-card';
});

const strategyTypeTag = computed(() => {
  const typeMap: Record<string, string> = {
    'trend': 'primary',
    'arbitrage': 'success',
    'hedge': 'warning',
    'event_driven': 'danger'
  };
  return typeMap[props.strategy.strategy_type] || 'primary';
});

const directionTag = computed(() => {
  return props.strategy.direction === 'long' ? 'success' : 'danger';
});

const strategyTypeText = computed(() => {
  const textMap: Record<string, string> = {
    'trend': '趋势跟踪',
    'arbitrage': '套利',
    'hedge': '套期保值',
    'event_driven': '事件驱动'
  };
  return textMap[props.strategy.strategy_type] || '趋势跟踪';
});

const directionText = computed(() => {
  return props.strategy.direction === 'long' ? '做多' : '做空';
});

const entryPrice = computed(() => props.strategy.entry_price);
const targetPrice = computed(() => props.strategy.target_price);
const stopLoss = computed(() => props.strategy.stop_loss);
const positionSize = computed(() => props.strategy.position_size);
const confidence = computed(() => props.strategy.confidence);
const riskRewardRatio = computed(() => props.strategy.risk_reward_ratio);
const reasoning = computed(() => props.strategy.reasoning);

const timeHorizonText = computed(() => {
  const textMap: Record<string, string> = {
    'short_term': '短期',
    'medium_term': '中期',
    'long_term': '长期'
  };
  return textMap[props.strategy.time_horizon] || '中期';
});
</script>

<style scoped>
.strategy-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.strategy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.long-card {
  border-left: 4px solid #10b981;
}

.short-card {
  border-left: 4px solid #ef4444;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.confidence-badge {
  display: flex;
  align-items: center;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.price-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 15px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.price-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.price-item .label {
  font-size: 12px;
  color: #909399;
}

.price-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.value.entry-price {
  color: #10b981;
}

.value.target-price {
  color: #67c23a;
}

.value.stop-loss {
  color: #ef4444;
}

.metrics-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.metric-item {
  display: flex;
  justify-content: space-between;
}

.metric-item .label {
  font-size: 12px;
  color: #909399;
}

.metric-item .value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.reasoning-section {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.reasoning-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.reasoning-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.actions-section {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .price-info {
    grid-template-columns: 1fr;
  }
  
  .metrics-info {
    grid-template-columns: 1fr;
  }
}
</style>
