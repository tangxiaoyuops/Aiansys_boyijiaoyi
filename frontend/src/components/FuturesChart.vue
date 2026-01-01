<template>
  <div class="futures-chart card">
    <div class="chart-title">{{ title || '期货K线图' }}</div>
    <div ref="chartRef" class="chart-body"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  data?: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    open_interest: number;
  }>;
  title?: string;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const initChart = () => {
  const el = chartRef.value;
  if (!el || !props.data || props.data.length === 0) return;

  // 准备K线数据
  const klineData = props.data.map((d) => [
    d.date,
    d.open,
    d.close,
    d.low,
    d.high
  ]);

  // 准备成交量数据
  const volumeData = props.data.map((d) => [d.date, d.volume]);

  // 准备持仓量数据
  const oiData = props.data.map((d) => [d.date, d.open_interest]);

  if (!chart) {
    chart = echarts.init(el);
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        if (!Array.isArray(params)) return '';
        const p = params[0];
        const date = p.value[0];
        const data = props.data?.find((d) => d.date === date);
        if (!data) return '';
        return `
          <div style="padding: 4px;">
            <div><strong>日期：</strong>${date}</div>
            <div><strong>开盘：</strong>${data.open.toFixed(2)}</div>
            <div><strong>收盘：</strong>${data.close.toFixed(2)}</div>
            <div><strong>最高：</strong>${data.high.toFixed(2)}</div>
            <div><strong>最低：</strong>${data.low.toFixed(2)}</div>
            <div><strong>成交量：</strong>${data.volume.toLocaleString()}</div>
            <div><strong>持仓量：</strong>${data.open_interest.toLocaleString()}</div>
          </div>
        `;
      }
    },
    legend: {
      data: ['K线', '成交量', '持仓量'],
      top: 10
    },
    grid: [
      { left: 40, right: 16, top: 60, height: '50%' },
      { left: 40, right: 16, top: '62%', height: '18%' },
      { left: 40, right: 16, top: '82%', height: '18%' }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        start: 50,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1, 2],
        top: '92%',
        start: 50,
        end: 100
      }
    ],
    xAxis: [
      {
        type: 'time',
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#6b7280' } },
        splitLine: { show: false }
      },
      {
        type: 'time',
        gridIndex: 1,
        boundaryGap: false,
        axisTick: { show: false },
        axisLabel: { show: false },
        axisLine: { lineStyle: { color: '#6b7280' } }
      },
      {
        type: 'time',
        gridIndex: 2,
        boundaryGap: false,
        axisTick: { show: false },
        axisLabel: { show: false },
        axisLine: { lineStyle: { color: '#6b7280' } }
      }
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { lineStyle: { color: '#6b7280' } },
        splitLine: { show: true, lineStyle: { color: '#e5e7eb' } }
      },
      {
        gridIndex: 1,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#6b7280' } },
        splitLine: { show: false }
      },
      {
        gridIndex: 2,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#6b7280' } },
        splitLine: { show: false }
      }
    ],
    series: [
      // K线图
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#16a34a', // 上涨颜色
          color0: '#dc2626', // 下跌颜色
          borderColor: '#16a34a',
          borderColor0: '#dc2626'
        }
      },
      // 成交量
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumeData,
        itemStyle: {
          color: (params: any) => {
            const data = props.data?.[params.dataIndex];
            if (!data) return '#60a5fa';
            return data.close >= data.open ? '#16a34a' : '#dc2626';
          }
        }
      },
      // 持仓量
      {
        name: '持仓量',
        type: 'line',
        xAxisIndex: 2,
        yAxisIndex: 2,
        data: oiData,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#f59e0b',
          width: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
            ]
          }
        }
      }
    ]
  };

  chart.setOption(option);
  chart.resize();
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
  () => props.data,
  () => {
    if (chart) {
      initChart();
    }
  },
  { deep: true }
);
</script>

<style scoped>
.futures-chart {
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
  height: 600px;
}
</style>

