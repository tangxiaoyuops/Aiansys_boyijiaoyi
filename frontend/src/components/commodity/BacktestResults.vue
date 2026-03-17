<template>
  <div v-if="backtestData" class="backtest-results">
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon" :size="20">
            <DataAnalysis />
          </el-icon>
          <span class="header-title">回测结果</span>
        </div>
      </template>

      <div class="results-content">
        <div class="summary-section">
          <div class="summary-title">回测概览</div>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="item-label">回测期间</span>
              <span class="item-value">{{ backtestData.start_date }} 至 {{ backtestData.end_date }}</span>
            </div>
            <div class="summary-item">
              <span class="item-label">初始资金</span>
              <span class="item-value">${{ formatNumber(backtestData.initial_capital) }}</span>
            </div>
            <div class="summary-item">
              <span class="item-label">最终资金</span>
              <span class="item-value" :class="getReturnClass(backtestData.total_return)">
                ${{ formatNumber(backtestData.final_capital) }}
              </span>
            </div>
            <div class="summary-item">
              <span class="item-label">总收益率</span>
              <span class="item-value" :class="getReturnClass(backtestData.total_return)">
                {{ formatPercent(backtestData.total_return) }}
              </span>
            </div>
            <div class="summary-item">
              <span class="item-label">年化收益率</span>
              <span class="item-value" :class="getReturnClass(backtestData.annual_return)">
                {{ formatPercent(backtestData.annual_return) }}
              </span>
            </div>
            <div class="summary-item">
              <span class="item-label">交易次数</span>
              <span class="item-value">{{ backtestData.trade_count }}</span>
            </div>
          </div>
        </div>

        <div class="charts-section">
          <div class="chart-title">净值曲线</div>
          <div ref="equityChartRef" class="chart-container" style="height: 300px;"></div>
          
          <div class="chart-title">回撤曲线</div>
          <div ref="drawdownChartRef" class="chart-container" style="height: 200px;"></div>
        </div>

        <div class="metrics-section">
          <div class="metrics-title">回测指标</div>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">夏普比率</div>
              <div class="metric-value">{{ formatDecimal(backtestData.sharpe_ratio, 2) }}</div>
              <el-tag :type="getSharpeClass(backtestData.sharpe_ratio)" size="small">
                {{ getSharpeText(backtestData.sharpe_ratio) }}
              </el-tag>
            </div>

            <div class="metric-card">
              <div class="metric-label">最大回撤</div>
              <div class="metric-value">{{ formatPercent(backtestData.max_drawdown) }}</div>
              <el-tag :type="getDrawdownClass(backtestData.max_drawdown)" size="small">
                {{ getDrawdownText(backtestData.max_drawdown) }}
              </el-tag>
            </div>

            <div class="metric-card">
              <div class="metric-label">胜率</div>
              <div class="metric-value">{{ formatPercent(backtestData.win_rate) }}</div>
              <el-tag :type="getWinRateClass(backtestData.win_rate)" size="small">
                {{ getWinRateText(backtestData.win_rate) }}
              </el-tag>
            </div>

            <div class="metric-card">
              <div class="metric-label">盈亏比</div>
              <div class="metric-value">{{ formatDecimal(backtestData.profit_factor, 2) }}</div>
              <el-tag type="info" size="small">
                {{ getProfitFactorText(backtestData.profit_factor) }}
              </el-tag>
            </div>

            <div class="metric-card">
              <div class="metric-label">平均持仓</div>
              <div class="metric-value">{{ formatDecimal(backtestData.avg_trade_duration, 1) }}天</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">最佳交易</div>
              <div class="metric-value positive">${{ formatNumber(backtestData.best_trade) }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-label">最差交易</div>
              <div class="metric-value negative">${{ formatNumber(backtestData.worst_trade) }}</div>
            </div>
          </div>
        </div>

        <div class="trades-section">
          <div class="section-header">
            <span class="section-title">交易记录</span>
            <el-button
              type="primary"
              size="small"
              @click="exportTrades"
              :icon="Download"
            >
              导出CSV
            </el-button>
          </div>
          <el-table :data="backtestData.trades || []" style="width: 100%">
            <el-table-column prop="entry_time" label="入场时间" width="150" />
            <el-table-column prop="direction" label="方向" width="80">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'long' ? 'success' : 'danger'" size="small">
                  {{ row.direction === 'long' ? '做多' : '做空' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="entry_price" label="入场价" width="100">
              <template #default="{ row }">
                ${{ formatDecimal(row.entry_price, 2) }}
              </template>
            </el-table-column>
            <el-table-column prop="exit_price" label="出场价" width="100">
              <template #default="{ row }">
                ${{ formatDecimal(row.exit_price, 2) }}
              </template>
            </el-table-column>
            <el-table-column prop="position_size" label="仓位" width="80">
              <template #default="{ row }">
                {{ row.position_size || 0 }}手
              </template>
            </el-table-column>
            <el-table-column prop="pnl" label="盈亏" width="100">
              <template #default="{ row }">
                <span :class="row.pnl > 0 ? 'positive' : 'negative'">
                  ${{ formatDecimal(row.pnl, 2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="commission" label="手续费" width="100">
              <template #default="{ row }">
                ${{ formatDecimal(row.commission, 2) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { Download, DataAnalysis } from '@element-plus/icons-vue';
import type { BacktestResult } from '@/api/commodity';

const props = defineProps<{
  backtestData: BacktestResult;
  showDetails?: boolean;
}>();

const emit = defineEmits<{
  'export': [];
}>();

const equityChartRef = ref<HTMLElement>();
const drawdownChartRef = ref<HTMLElement>();

const formatNumber = (num: number | undefined | null) => {
  if (num === undefined || num === null || isNaN(num)) {
    return '0.00';
  }
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatDecimal = (num: number | undefined | null, digits: number = 2) => {
  if (num === undefined || num === null || isNaN(num)) {
    return '0.' + '0'.repeat(digits);
  }
  return num.toFixed(digits);
};

const formatPercent = (value: number | undefined | null) => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const getReturnClass = (value: number | undefined | null) => {
  if (value === undefined || value === null || isNaN(value)) {
    return 'neutral';
  }
  return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
};

const getSharpeClass = (value: number) => {
  if (value >= 2) return 'success';
  if (value >= 1) return 'primary';
  if (value >= 0) return 'warning';
  return 'danger';
};

const getSharpeText = (value: number) => {
  if (value >= 2) return '优秀';
  if (value >= 1) return '良好';
  if (value >= 0) return '一般';
  return '较差';
};

const getDrawdownClass = (value: number) => {
  const absValue = Math.abs(value);
  if (absValue <= 5) return 'success';
  if (absValue <= 10) return 'primary';
  if (absValue <= 20) return 'warning';
  return 'danger';
};

const getDrawdownText = (value: number) => {
  const absValue = Math.abs(value);
  if (absValue <= 5) return '可接受';
  if (absValue <= 10) return '一般';
  if (absValue <= 20) return '较大';
  return '过大';
};

const getWinRateClass = (value: number) => {
  if (value >= 60) return 'success';
  if (value >= 50) return 'primary';
  if (value >= 40) return 'warning';
  return 'danger';
};

const getWinRateText = (value: number) => {
  if (value >= 60) return '优秀';
  if (value >= 50) return '良好';
  if (value >= 40) return '一般';
  return '较差';
};

const getProfitFactorText = (value: number) => {
  if (value >= 2) return '优秀';
  if (value >= 1.5) return '良好';
  if (value >= 1) return '一般';
  return '较差';
};

const initEquityChart = () => {
  if (!equityChartRef.value || !props.backtestData.equity_curve) return;
  
  const chart = echarts.init(equityChartRef.value);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const value = params[0]?.data ?? 0;
        return `净值: $${formatDecimal(value, 2)}`;
      }
    },
    xAxis: {
      type: 'category',
      data: props.backtestData.equity_curve.map((_, i) => `交易${i + 1}`)
    },
    yAxis: {
      type: 'value',
      name: '净值',
      axisLabel: {
        formatter: (value: number) => `$${formatDecimal(value, 0)}`
      }
    },
    series: [{
      name: '净值',
      type: 'line',
      data: props.backtestData.equity_curve,
      smooth: true,
      lineStyle: {
        color: '#10b981',
        width: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
          { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
        ])
      }
    }]
  };
  
  chart.setOption(option);
};

const initDrawdownChart = () => {
  if (!drawdownChartRef.value || !props.backtestData.drawdown_curve) return;
  
  const chart = echarts.init(drawdownChartRef.value);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const value = params[0]?.data ?? 0;
        return `回撤: ${formatDecimal(value, 2)}%`;
      }
    },
    xAxis: {
      type: 'category',
      data: props.backtestData.drawdown_curve.map((_, i) => `交易${i + 1}`)
    },
    yAxis: {
      type: 'value',
      name: '回撤',
      axisLabel: {
        formatter: (value: number) => `${formatDecimal(value, 1)}%`
      }
    },
    series: [{
      name: '回撤',
      type: 'line',
      data: props.backtestData.drawdown_curve,
      smooth: true,
      lineStyle: {
        color: '#ef4444',
        width: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
          { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
        ])
      }
    }]
  };
  
  chart.setOption(option);
};

const exportTrades = () => {
  emit('export');
};

onMounted(async () => {
  await nextTick();
  initEquityChart();
  initDrawdownChart();
});
</script>

<style scoped>
.backtest-results {
  margin-bottom: 20px;
}

.results-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.header-icon {
  color: var(--el-color-primary);
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-section,
.charts-section,
.metrics-section,
.trades-section {
  background-color: #f9fafb;
  padding: 15px;
  border-radius: 6px;
}

.summary-title,
.chart-title,
.metrics-title,
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #ffffff;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.item-label {
  color: #909399;
  font-size: 13px;
}

.item-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.item-value.positive {
  color: #10b981;
}

.item-value.negative {
  color: #ef4444;
}

.chart-container {
  background-color: #ffffff;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric-card {
  background-color: #ffffff;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  text-align: center;
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
}

.metric-value.positive {
  color: #10b981;
}

.metric-value.negative {
  color: #ef4444;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
