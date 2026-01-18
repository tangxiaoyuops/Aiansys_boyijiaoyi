<template>
  <div class="backtest-results">
    <el-card v-if="results" class="results-card">
      <template #header>
        <span>回测结果</span>
      </template>
      
      <!-- 关键指标卡片 -->
      <div class="metrics-cards">
        <div class="metric-card-wrapper">
          <div class="metric-card" :class="getReturnColorClass(results.metrics.total_return)">
            <div class="metric-icon">
              <el-icon v-if="results.metrics.total_return >= 0"><TrendCharts /></el-icon>
              <el-icon v-else><ArrowDown /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getReturnColor(results.metrics.total_return)">
                {{ formatPercent(results.metrics.total_return) }}
              </div>
              <div class="metric-label">总收益率</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card-wrapper">
          <div class="metric-card">
            <div class="metric-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getReturnColor(results.metrics.annual_return)">
                {{ formatPercent(results.metrics.annual_return) }}
              </div>
              <div class="metric-label">年化收益</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card-wrapper">
          <div class="metric-card" :class="getSharpeColorClass(results.metrics.sharpe_ratio)">
            <div class="metric-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="getSharpeColor(results.metrics.sharpe_ratio)">
                {{ formatNumber(results.metrics.sharpe_ratio, 2) }}
              </div>
              <div class="metric-label">夏普比率</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card-wrapper">
          <div class="metric-card danger-card">
            <div class="metric-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value danger">
                {{ formatPercent(results.metrics.max_drawdown) }}
              </div>
              <div class="metric-label">最大回撤</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card-wrapper">
          <div class="metric-card">
            <div class="metric-icon">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value" :class="results.metrics.win_rate >= 50 ? 'success' : 'warning'">
                {{ formatPercent(results.metrics.win_rate) }}
              </div>
              <div class="metric-label">胜率</div>
            </div>
          </div>
        </div>
        
        <div class="metric-card-wrapper">
          <div class="metric-card">
            <div class="metric-icon">
              <el-icon><ShoppingCart /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">
                {{ results.metrics.total_trades }}
              </div>
              <div class="metric-label">交易次数</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图表区域 -->
      <el-tabs v-model="activeTab" class="chart-tabs">
        <el-tab-pane label="权益曲线" name="equity">
          <EquityCurveChart
            :equity-curve="results.equity_curve"
            :drawdown="results.metrics.drawdown_series"
            :initial-capital="results.config.initial_capital"
          />
        </el-tab-pane>
        
        <el-tab-pane label="K线图" name="kline">
          <KlineChart
            v-if="results.kline_data && results.kline_data.length > 0"
            :kline-data="results.kline_data"
            :trade-log="results.trade_log"
          />
          <el-empty v-else description="暂无K线数据" />
        </el-tab-pane>
        
        <el-tab-pane label="交易日志" name="trades">
          <div class="trade-log-container">
            <el-table 
              :data="results.trade_log" 
              style="width: 100%"
              stripe
              border
              :default-sort="{ prop: 'time', order: 'descending' }"
              class="trade-table"
            >
            <el-table-column prop="time" label="时间" width="160" sortable>
              <template #default="{ row }">
                {{ formatTime(row.time) }}
              </template>
            </el-table-column>
            <el-table-column prop="operation_type" label="操作类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag 
                  :type="row.operation_type === '开仓' ? 'success' : 'warning'"
                  size="small"
                >
                  {{ row.operation_type || formatAction(row.action) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="shares" label="数量(股)" width="110" align="right">
              <template #default="{ row }">
                {{ formatNumber(row.shares || row.size, 0) }}
              </template>
            </el-table-column>
            <el-table-column prop="trade_price" label="成交价格" width="110" align="right">
              <template #default="{ row }">
                ¥{{ formatNumber(row.trade_price || row.price, 2) }}
              </template>
            </el-table-column>
            <el-table-column v-if="hasOpenPrice" prop="open_price" label="开仓价格" width="110" align="right">
              <template #default="{ row }">
                <span v-if="row.open_price">
                  ¥{{ formatNumber(row.open_price, 2) }}
                </span>
                <span v-else style="color: #9ca3af;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="pnl" label="盈亏金额" width="120" align="right">
              <template #default="{ row }">
                <span v-if="row.pnl !== undefined && row.pnl !== null" :style="{ color: row.pnl >= 0 ? '#10b981' : '#ef4444', fontWeight: '600' }">
                  {{ row.pnl >= 0 ? '+' : '' }}¥{{ formatNumber(row.pnl, 2) }}
                </span>
                <span v-else style="color: #9ca3af;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="pnl_pct" label="盈亏比例" width="100" align="right">
              <template #default="{ row }">
                <span v-if="row.pnl_pct !== undefined && row.pnl_pct !== null" :style="{ color: row.pnl_pct >= 0 ? '#10b981' : '#ef4444', fontWeight: '600' }">
                  {{ row.pnl_pct >= 0 ? '+' : '' }}{{ formatNumber(row.pnl_pct, 2) }}%
                </span>
                <span v-else style="color: #9ca3af;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="pnl_type" label="盈亏类型" width="90" align="center">
              <template #default="{ row }">
                <el-tag 
                  v-if="row.pnl_type"
                  :type="row.pnl_type === '止盈' ? 'success' : row.pnl_type === '止损' ? 'danger' : 'info'"
                  size="small"
                >
                  {{ row.pnl_type }}
                </el-tag>
                <span v-else style="color: #9ca3af;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="trade_amount" label="交易金额" width="120" align="right">
              <template #default="{ row }">
                <span v-if="row.trade_amount">
                  ¥{{ formatNumber(row.trade_amount, 2) }}
                </span>
                <span v-else style="color: #9ca3af;">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" min-width="180" show-overflow-tooltip />
          </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 详细指标 -->
      <el-card class="detailed-metrics">
        <template #header>
          <div class="detailed-header">
            <span>详细指标</span>
            <el-tag type="info" size="small">更多数据</el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border class="metrics-descriptions">
          <el-descriptions-item label="初始资金">
            <span style="font-weight: 600; color: #1f2937;">
              ¥{{ formatNumber(results.config.initial_capital, 2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="最终权益">
            <span :style="{ fontWeight: '600', color: results.metrics.final_equity >= results.config.initial_capital ? '#10b981' : '#ef4444' }">
              ¥{{ formatNumber(results.metrics.final_equity || 0, 2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="总盈亏">
            <span :style="{ fontWeight: '600', color: results.metrics.total_profit >= 0 ? '#10b981' : '#ef4444' }">
              {{ results.metrics.total_profit >= 0 ? '+' : '' }}¥{{ formatNumber(results.metrics.total_profit || 0, 2) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="波动率">
            {{ formatPercent(results.metrics.volatility || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="VaR (95%)">
            {{ formatPercent(results.metrics.var_95 || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="CVaR (95%)">
            {{ formatPercent(results.metrics.cvar_95 || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="索提诺比率">
            {{ formatNumber(results.metrics.sortino_ratio || 0, 2) }}
          </el-descriptions-item>
          <el-descriptions-item label="卡玛比率">
            {{ formatNumber(results.metrics.calmar_ratio || 0, 2) }}
          </el-descriptions-item>
          <el-descriptions-item label="盈亏比">
            {{ formatNumber(results.metrics.profit_factor || 0, 2) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { TrendCharts, ArrowDown, Calendar, DataAnalysis, Warning, Trophy, ShoppingCart } from '@element-plus/icons-vue';
import EquityCurveChart from '../charts/EquityCurveChart.vue';
import KlineChart from '../charts/KlineChart.vue';

interface Props {
  results: any;
}

const props = defineProps<Props>();
const activeTab = ref('equity');

// 检查是否有开仓价格字段，以决定是否显示开仓价格列
const hasOpenPrice = computed(() => {
  if (!props.results?.trade_log) return false;
  return props.results.trade_log.some((trade: any) => trade.open_price !== undefined && trade.open_price !== null);
});

function formatPercent(value: number): string {
  if (value === undefined || value === null || isNaN(value)) return '0.00%';
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

function formatNumber(value: number, decimals: number = 0): string {
  if (value === undefined || value === null || isNaN(value)) return '0';
  return value.toFixed(decimals);
}

function getReturnColor(value: number): string {
  return value >= 0 ? 'success' : 'danger';
}

function getReturnColorClass(value: number): string {
  return value >= 0 ? 'success-card' : 'danger-card';
}

function getSharpeColor(value: number): string {
  if (value >= 2) return 'success';
  if (value >= 1) return 'warning';
  return 'danger';
}

function getSharpeColorClass(value: number): string {
  if (value >= 2) return 'success-card';
  if (value >= 1) return 'warning-card';
  return 'danger-card';
}

function formatTime(time: string | Date): string {
  if (!time) return '-';
  try {
    const date = typeof time === 'string' ? new Date(time) : time;
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return String(time);
  }
}

function formatAction(action: string): string {
  const actionMap: Record<string, string> = {
    'OPEN_LONG': '开多',
    'OPEN_SHORT': '开空',
    'CLOSE_LONG': '平多',
    'CLOSE_SHORT': '平空',
    'CLOSE_ALL': '平仓'
  };
  return actionMap[action] || action;
}

function getActionType(action: string): string {
  if (action.includes('OPEN_LONG') || action.includes('CLOSE_SHORT')) {
    return 'success';
  } else if (action.includes('OPEN_SHORT') || action.includes('CLOSE_LONG') || action.includes('CLOSE_ALL')) {
    return 'danger';
  }
  return 'info';
}
</script>

<style scoped>
.backtest-results {
  padding: 0;
  width: 100%;
}

.results-card {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
  width: 100%;
}

@media (max-width: 1200px) {
  .metrics-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .metrics-cards {
    grid-template-columns: 1fr;
  }
}

.metric-card-wrapper {
  min-width: 0;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 100%;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-card.success-card {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-color: #10b981;
}

.metric-card.danger-card {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #ef4444;
}

.metric-card.warning-card {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-color: #f59e0b;
}

.metric-icon {
  font-size: 40px;
  margin-right: 20px;
  color: #6b7280;
  flex-shrink: 0;
  opacity: 0.8;
}

.metric-card.success-card .metric-icon {
  color: #10b981;
}

.metric-card.danger-card .metric-icon {
  color: #ef4444;
}

.metric-card.warning-card .metric-icon {
  color: #f59e0b;
}

.metric-content {
  flex: 1;
  min-width: 0;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 6px;
  line-height: 1.2;
  word-break: break-all;
  letter-spacing: -0.5px;
}

.metric-value.success {
  color: #10b981;
}

.metric-value.danger {
  color: #ef4444;
}

.metric-value.warning {
  color: #f59e0b;
}

.metric-label {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

.chart-tabs {
  margin-top: 32px;
}

.chart-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
}

.chart-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.chart-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 600;
  padding: 0 32px;
  height: 48px;
  line-height: 48px;
  color: #6b7280;
  transition: all 0.3s;
}

.chart-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
}

.chart-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
  font-weight: 700;
}

.chart-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 3px;
}

.detailed-metrics {
  margin-top: 32px;
  border-radius: 16px;
}

.detailed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metrics-descriptions {
  margin-top: 8px;
}

.detailed-metrics :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
  font-size: 14px;
  padding: 12px 16px;
}

.detailed-metrics :deep(.el-descriptions__content) {
  color: #1f2937;
  font-weight: 500;
  padding: 12px 16px;
  font-size: 14px;
}

.detailed-metrics :deep(.el-descriptions__table) {
  border-radius: 8px;
  overflow: hidden;
}

.detailed-metrics :deep(.el-descriptions__cell) {
  border-color: #e5e7eb;
}

.detailed-metrics :deep(.el-descriptions__cell:first-child) {
  border-left: none;
}

.detailed-metrics :deep(.el-descriptions__cell:last-child) {
  border-right: none;
}

.trade-log-container {
  padding: 8px 0;
}

.trade-table {
  border-radius: 8px;
  overflow: hidden;
}

.trade-table :deep(.el-table__header) {
  background: #f9fafb;
}

.trade-table :deep(.el-table__header th) {
  background: #f9fafb;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  border-color: #e5e7eb;
}

.trade-table :deep(.el-table__body tr:hover > td) {
  background: #f3f4f6;
}

.trade-table :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.trade-table :deep(.el-table td) {
  border-color: #e5e7eb;
  padding: 12px 0;
}

.trade-table :deep(.el-table--border) {
  border-color: #e5e7eb;
}

.trade-table :deep(.el-table--border::after) {
  background-color: #e5e7eb;
}

.trade-table :deep(.el-table--border::before) {
  background-color: #e5e7eb;
}
</style>

