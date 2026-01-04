<template>
  <div class="backtest-chart card">
    <div class="chart-title">回溯测试K线与操作点</div>
    <div ref="chartRef" class="chart-body"></div>
    <el-dialog
      v-model="dialogVisible"
      title="当日博弈分析结论"
      width="480px"
    >
      <div v-if="dialogAnalysis">
        <p><strong>阶段：</strong>{{ dialogAnalysis.stage_name }}（{{ dialogAnalysis.stage }}）</p>
        <p><strong>阶段说明：</strong>{{ dialogAnalysis.stage_description }}</p>
        <p><strong>操作建议：</strong>{{ dialogAnalysis.strategy_operation }}</p>
        <p><strong>仓位建议：</strong>{{ dialogAnalysis.strategy_position }}</p>
        <p v-if="dialogAnalysis.strategy_reason"><strong>理由：</strong>{{ dialogAnalysis.strategy_reason }}</p>
        <p v-if="dialogAnalysis.summary" style="margin-top: 8px;"><strong>当日总结：</strong>{{ dialogAnalysis.summary }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  backtest: any;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const dialogVisible = ref(false);
const dialogAnalysis = ref<any | null>(null);

const initChart = () => {
  const el = chartRef.value;
  if (!el || !props.backtest) return;

  const kline = props.backtest.kline || [];
  const trades = props.backtest.trade_log || [];
  if (!kline.length) return;

  // 使用真实日期作为 time 轴：series 数据格式为 [时间, 数值]
  const closeLine = kline.map((d: any) => [d['日期'], d['收盘']]);

  const buyPoints: any[] = [];
  const sellPoints: any[] = [];
  (trades as any[]).forEach((t) => {
    if (!t || t.trade_shares === 0) return;
    const point: any = {
      value: [t.date, t.close],
      symbolSize: 10,
      itemStyle: {
        color: t.trade_shares > 0 ? '#16a34a' : '#dc2626'
      },
      analysis: t.analysis || null
    };
    if (t.trade_shares > 0) {
      buyPoints.push(point);
    } else {
      sellPoints.push(point);
    }
  });

  if (!chart) {
    chart = echarts.init(el);
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        const date = p.value[0];
        const price = p.value[1];
        const seriesName = p.seriesName;
        let extra = '';
        if (p.data && p.data.analysis) {
          const a = p.data.analysis;
          extra =
            `<br/>阶段：${a.stage_name || ''}` +
            `<br/>操作：${a.strategy_operation || ''}` +
            (a.strategy_reason ? `<br/>理由：${a.strategy_reason}` : '');
        }
        return `日期：${date}<br/>价格：${price.toFixed(2)}<br/>${seriesName}${extra}`;
      }
    },
    legend: {
      data: ['收盘价', '成交量', '买入/加仓', '卖出/减仓']
    },
    grid: [
      { left: 40, right: 16, top: 40, height: '60%' },
      { left: 40, right: 16, top: '72%', height: '18%' }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        top: '92%',
        start: 50,
        end: 100
      }
    ],
    xAxis: [
      {
        type: 'time',
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#6b7280' } }
      },
      {
        type: 'time',
        gridIndex: 1,
        boundaryGap: false,
        axisTick: { show: false },
        axisLabel: { show: false },
        axisLine: { lineStyle: { color: '#6b7280' } }
      }
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { lineStyle: { color: '#6b7280' } }
      },
      {
        gridIndex: 1,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#6b7280' } }
      }
    ],
    series: [
      // 收盘价折线
      {
        name: '收盘价',
        type: 'line',
        data: closeLine,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#3b82f6',
          width: 1.5
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: kline.map((d: any) => [d['日期'], d['成交量'] ?? 0]),
        itemStyle: { color: '#60a5fa' }
      },
      {
        name: '买入/加仓',
        type: 'scatter',
        symbol: 'triangle',
        symbolRotate: 180,
        data: buyPoints
      },
      {
        name: '卖出/减仓',
        type: 'scatter',
        symbol: 'triangle',
        data: sellPoints
      }
    ]
  };

  chart.setOption(option);
  chart.resize();

  // 点击买卖点时，弹出当时的博弈分析结论
  chart.off('click');
  chart.on('click', (params: any) => {
    if (
      params.seriesName === '买入/加仓' ||
      params.seriesName === '卖出/减仓'
    ) {
      const data = params.data;
      if (data && data.analysis) {
        dialogAnalysis.value = data.analysis;
        dialogVisible.value = true;
      }
    }
  });
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => chart && chart.resize());
});

onBeforeUnmount(() => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
});

watch(
  () => props.backtest,
  () => {
    if (chart) {
      initChart();
    }
  },
  { deep: true }
);
</script>

<style scoped>
.backtest-chart {
  margin-top: 12px;
  padding: 8px 8px 4px;
}
.chart-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #374151;
}
.chart-body {
  width: 100%;
  height: 800px; /* 按你说的大约 800 像素高度 */
}
</style>



























