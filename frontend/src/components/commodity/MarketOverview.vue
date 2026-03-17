<template>
  <div v-if="data" class="market-overview">
    <el-card class="overview-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon" :size="20">
            <TrendCharts />
          </el-icon>
          <span class="header-title">市场概况</span>
        </div>
      </template>

      <div class="overview-content">
        <div class="info-section">
          <div class="info-row">
            <span class="info-label">品种：</span>
            <span class="info-value">{{ data.commodity }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">时间范围：</span>
            <span class="info-value">{{ formatTimeRange(data.timeRange) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">市场状态：</span>
            <el-tag
              :type="getMarketStateType(data.marketState)"
              effect="dark"
              size="large"
            >
              {{ getMarketStateText(data.marketState) }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="info-label">分析时间：</span>
            <span class="info-value">{{ data.analysisTime }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">总耗时：</span>
            <span class="info-value">{{ formatDuration(data.totalDuration) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">分析轮次：</span>
            <span class="info-value">{{ data.roundsUsed }}轮</span>
          </div>
        </div>

        <div class="metrics-section">
          <div class="metrics-title">关键指标</div>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">当前价格</div>
              <div class="metric-value">{{ formatPrice(data.currentPrice) }}</div>
              <div class="metric-change" :class="getChangeClass(data.priceChange)">
                <el-icon>
                  <component :is="getChangeIcon(data.priceChange)" />
                </el-icon>
                {{ formatChange(data.priceChange) }}
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-label">涨跌幅</div>
              <div class="metric-value" :class="getChangeClass(data.priceChange)">
                {{ formatPercent(data.priceChange) }}
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-label">波动率</div>
              <div class="metric-value">{{ formatPercent(data.volatility) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">成交量</div>
              <div class="metric-value">{{ formatNumber(data.volume) }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { TrendCharts, ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue';

const props = defineProps<{
  data: {
    commodity: string;
    timeRange?: { start: string; end: string };
    marketState: string;
    analysisTime: string;
    totalDuration: number;
    roundsUsed: number;
    currentPrice: number;
    priceChange: number;
    volatility: number;
    volume: number;
  };
}>();

const formatTimeRange = (range?: { start: string; end: string }) => {
  if (!range) return '未指定';
  return `${range.start} 至 ${range.end}`;
};

const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${Math.floor(seconds)}秒`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}分${remainingSeconds}秒`;
};

const formatPrice = (price: number) => {
  return `$${price.toFixed(2)}`;
};

const formatPercent = (value: number) => {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const formatChange = (change: number) => {
  return formatPercent(change);
};

const formatNumber = (num: number) => {
  return num.toLocaleString();
};

const getMarketStateType = (state: string) => {
  if (state === 'uptrend' || state === 'uptrend_weak') return 'success';
  if (state === 'downtrend' || state === 'downtrend_weak') return 'danger';
  if (state === 'overbought') return 'warning';
  if (state === 'oversold') return 'info';
  return 'primary';
};

const getMarketStateText = (state: string) => {
  const stateMap: Record<string, string> = {
    'uptrend': '上涨趋势',
    'uptrend_weak': '上涨趋势（弱）',
    'downtrend': '下跌趋势',
    'downtrend_weak': '下跌趋势（弱）',
    'overbought': '超买',
    'oversold': '超卖',
    'range': '震荡',
    'unknown': '未知'
  };
  return stateMap[state] || '未知';
};

const getChangeClass = (change: number) => {
  if (change > 0) return 'positive';
  if (change < 0) return 'negative';
  return 'neutral';
};

const getChangeIcon = (change: number) => {
  if (change > 0) return ArrowUp;
  if (change < 0) return ArrowDown;
  return Minus;
};
</script>

<style scoped>
.market-overview {
  margin-bottom: 20px;
}

.overview-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  color: var(--el-color-primary);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.overview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background-color: #f9fafb;
  padding: 15px;
  border-radius: 6px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
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

.metrics-section {
  background-color: #ffffff;
  padding: 15px;
  border-radius: 6px;
}

.metrics-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric-card {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 500;
}

.metric-change.positive {
  color: #10b981;
}

.metric-change.negative {
  color: #ef4444;
}

.metric-change.neutral {
  color: #909399;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
