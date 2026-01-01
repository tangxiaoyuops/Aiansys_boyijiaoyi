<template>
  <div class="spread-panel card">
    <div class="panel-title">价差分析</div>
    <div v-if="!spreadData || spreadData.error" class="empty-state">
      {{ spreadData?.error || '暂无价差分析数据' }}
    </div>
    <div v-else class="spread-content">
      <!-- 跨期价差 -->
      <div v-if="spreadData.calendar_spread" class="section">
        <div class="section-title">跨期价差</div>
        <div class="spread-info">
          <div class="spread-pair">
            <span class="label">合约对：</span>
            <span class="value">
              {{ spreadData.calendar_spread.near_month || '--' }} vs
              {{ spreadData.calendar_spread.far_month || '--' }}
            </span>
          </div>
          <div v-if="spreadData.calendar_spread.analysis" class="analysis-info">
            <div class="info-item">
              <span class="label">当前价差：</span>
              <span class="value">{{ spreadData.calendar_spread.analysis.current_spread?.toFixed(2) || '--' }}</span>
            </div>
            <div class="info-item">
              <span class="label">价差均值：</span>
              <span class="value">{{ spreadData.calendar_spread.analysis.spread_mean?.toFixed(2) || '--' }}</span>
            </div>
            <div class="info-item">
              <span class="label">价差趋势：</span>
              <span :class="['trend', getTrendClass(spreadData.calendar_spread.analysis.trend)]">
                {{ spreadData.calendar_spread.analysis.trend || 'unknown' }}
              </span>
            </div>
          </div>
          <div v-if="spreadData.calendar_spread.arbitrage?.has_opportunity" class="arbitrage-opportunity">
            <div class="opportunity-badge">套利机会</div>
            <div class="info-item">
              <span class="label">机会类型：</span>
              <span class="value">{{ spreadData.calendar_spread.arbitrage.opportunity_type || '--' }}</span>
            </div>
            <div class="info-item">
              <span class="label">预期收益：</span>
              <span class="value positive">{{ spreadData.calendar_spread.arbitrage.expected_profit?.toFixed(2) || '--' }}</span>
            </div>
            <div class="info-item">
              <span class="label">置信度：</span>
              <span class="value">{{ ((spreadData.calendar_spread.arbitrage.confidence || 0) * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 套利机会列表 -->
      <div v-if="spreadData.arbitrage_opportunities && spreadData.arbitrage_opportunities.length > 0" class="section">
        <div class="section-title">套利机会列表</div>
        <ul class="opportunities-list">
          <li v-for="(opp, index) in spreadData.arbitrage_opportunities" :key="index" class="opportunity-item">
            <div class="opp-description">{{ opp.description || '--' }}</div>
            <div v-if="opp.type" class="opp-type">类型：{{ opp.type }}</div>
            <div v-if="opp.profit" class="opp-profit">预期收益：{{ opp.profit }}</div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  spreadData?: any;
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
</script>

<style scoped>
.spread-panel {
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
.spread-content {
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
.spread-info {
  padding: 8px;
  background-color: #f9fafb;
  border-radius: 4px;
}
.spread-pair {
  font-size: 12px;
  margin-bottom: 8px;
}
.label {
  color: #6b7280;
  margin-right: 4px;
}
.value {
  color: #1f2937;
  font-weight: 500;
}
.analysis-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e5e7eb;
}
.info-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  margin-bottom: 4px;
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
.arbitrage-opportunity {
  margin-top: 12px;
  padding: 8px;
  background-color: #fef3c7;
  border-left: 3px solid #f59e0b;
  border-radius: 4px;
}
.opportunity-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #f59e0b;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 8px;
}
.positive {
  color: #16a34a;
  font-weight: 600;
}
.opportunities-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.opportunity-item {
  padding: 8px;
  margin-bottom: 8px;
  background-color: #f9fafb;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
}
.opp-description {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  font-size: 12px;
}
.opp-type,
.opp-profit {
  font-size: 11px;
  color: #6b7280;
  margin-top: 2px;
}
</style>

