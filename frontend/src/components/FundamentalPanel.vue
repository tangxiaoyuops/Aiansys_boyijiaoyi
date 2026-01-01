<template>
  <div class="fundamental-panel card">
    <div class="panel-title">基本面分析</div>
    <div v-if="!fundamentalData || fundamentalData.error" class="empty-state">
      {{ fundamentalData?.error || '暂无基本面分析数据' }}
    </div>
    <div v-else class="fundamental-content">
      <!-- 持仓量分析 -->
      <div v-if="fundamentalData.open_interest" class="section">
        <div class="section-title">持仓量分析</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">趋势：</span>
            <span :class="['trend', getTrendClass(fundamentalData.open_interest.trend)]">
              {{ fundamentalData.open_interest.trend || 'unknown' }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">变化：</span>
            <span :class="getChangeClass(fundamentalData.open_interest.change_pct)">
              {{ fundamentalData.open_interest.change_pct > 0 ? '+' : '' }}{{ fundamentalData.open_interest.change_pct?.toFixed(2) || '--' }}%
            </span>
          </div>
          <div class="info-item full-width">
            <span class="label">分析：</span>
            <span class="value">{{ fundamentalData.open_interest.analysis || '--' }}</span>
          </div>
        </div>
      </div>

      <!-- 成交量分析 -->
      <div v-if="fundamentalData.volume" class="section">
        <div class="section-title">成交量分析</div>
        <div class="info-item full-width">
          <span class="value">{{ fundamentalData.volume.analysis || '--' }}</span>
        </div>
      </div>

      <!-- 价量关系 -->
      <div v-if="fundamentalData.price_oi_relationship" class="section">
        <div class="section-title">价量关系</div>
        <div class="info-item full-width">
          <span class="value">{{ fundamentalData.price_oi_relationship.relationship || '--' }}</span>
        </div>
        <div v-if="fundamentalData.price_oi_relationship.analysis" class="info-item full-width" style="margin-top: 4px;">
          <span class="value" style="font-size: 11px; color: #6b7280;">
            {{ fundamentalData.price_oi_relationship.analysis }}
          </span>
        </div>
      </div>

      <!-- 基本面总结 -->
      <div v-if="fundamentalData.summary" class="section">
        <div class="section-title">基本面总结</div>
        <div class="summary-content">
          {{ fundamentalData.summary }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  fundamentalData?: any;
}>();

const getTrendClass = (trend: string) => {
  const trendMap: Record<string, string> = {
    up: 'trend-up',
    down: 'trend-down',
    stable: 'trend-stable',
    unknown: 'trend-unknown'
  };
  return trendMap[trend] || 'trend-unknown';
};

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-up';
  if (change < 0) return 'change-down';
  return '';
};
</script>

<style scoped>
.fundamental-panel {
  padding: 12px;
  margin-bottom: 12px;
}
.panel-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}
.empty-state {
  padding: 20px;
  text-align: center;
  color: #6b7280;
  font-size: 13px;
}
.fundamental-content {
  padding-top: 8px;
}
.section {
  margin-bottom: 16px;
}
.section:last-child {
  margin-bottom: 0;
}
.section-title {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.info-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}
.info-item.full-width {
  grid-column: 1 / -1;
}
.label {
  color: #6b7280;
  margin-right: 4px;
}
.value {
  color: #1f2937;
  font-weight: 500;
}
.trend {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}
.trend-up {
  background-color: #d1fae5;
  color: #065f46;
}
.trend-down {
  background-color: #fee2e2;
  color: #991b1b;
}
.trend-stable {
  background-color: #e0e7ff;
  color: #3730a3;
}
.trend-unknown {
  background-color: #f3f4f6;
  color: #6b7280;
}
.change-up {
  color: #16a34a;
  font-weight: 500;
}
.change-down {
  color: #dc2626;
  font-weight: 500;
}
.summary-content {
  padding: 8px;
  background-color: #f9fafb;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
  font-size: 12px;
  color: #1f2937;
  line-height: 1.6;
}
</style>

