<template>
  <div class="risk-panel card">
    <div class="panel-title">风险管理分析</div>
    <div v-if="!riskData || riskData.error" class="empty-state">
      {{ riskData?.error || '暂无风险管理分析数据' }}
    </div>
    <div v-else class="risk-content">
      <!-- 基本信息 -->
      <div class="section">
        <div class="section-title">基本信息</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">当前价格：</span>
            <span class="value">{{ riskData.current_price?.toFixed(2) || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="label">杠杆倍数：</span>
            <span class="value">{{ riskData.leverage?.toFixed(1) || '--' }}倍</span>
          </div>
          <div class="info-item">
            <span class="label">保证金率：</span>
            <span class="value">{{ ((riskData.margin_rate || 0) * 100).toFixed(1) }}%</span>
          </div>
          <div class="info-item">
            <span class="label">风险等级：</span>
            <span :class="['risk-level', getRiskLevelClass(riskData.risk_level)]">
              {{ riskData.risk_level || 'medium' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 风险指标 -->
      <div class="section">
        <div class="section-title">风险指标</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">波动率（20日）：</span>
            <span class="value">{{ riskData.volatility_20?.toFixed(2) || '--' }}%</span>
          </div>
          <div class="info-item">
            <span class="label">最大回撤（60日）：</span>
            <span class="value">{{ riskData.max_drawdown_60?.toFixed(2) || '--' }}%</span>
          </div>
        </div>
      </div>

      <!-- 风险管理建议 -->
      <div v-if="riskData.recommendations && riskData.recommendations.length > 0" class="section">
        <div class="section-title">风险管理建议</div>
        <ul class="recommendations-list">
          <li v-for="(rec, index) in riskData.recommendations" :key="index" class="recommendation-item">
            <div class="rec-suggestion">{{ rec.suggestion }}</div>
            <div class="rec-reason">{{ rec.reason }}</div>
          </li>
        </ul>
      </div>

      <!-- 止损建议 -->
      <div v-if="riskData.stop_loss" class="section">
        <div class="section-title">止损建议</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">止损价格：</span>
            <span class="value">{{ riskData.stop_loss.price?.toFixed(2) || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="label">止损幅度：</span>
            <span class="value">{{ riskData.stop_loss.percentage?.toFixed(2) || '--' }}%</span>
          </div>
          <div class="info-item full-width">
            <span class="label">理由：</span>
            <span class="value">{{ riskData.stop_loss.reason || '--' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  riskData?: any;
}>();

const getRiskLevelClass = (level: string) => {
  const levelMap: Record<string, string> = {
    low: 'risk-low',
    medium: 'risk-medium',
    high: 'risk-high'
  };
  return levelMap[level] || 'risk-medium';
};
</script>

<style scoped>
.risk-panel {
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
.risk-content {
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
.risk-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}
.risk-low {
  background-color: #d1fae5;
  color: #065f46;
}
.risk-medium {
  background-color: #fef3c7;
  color: #92400e;
}
.risk-high {
  background-color: #fee2e2;
  color: #991b1b;
}
.recommendations-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.recommendation-item {
  padding: 8px;
  margin-bottom: 8px;
  background-color: #f9fafb;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
}
.rec-suggestion {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
  font-size: 12px;
}
.rec-reason {
  font-size: 11px;
  color: #6b7280;
}
</style>

