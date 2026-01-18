<template>
  <div ref="chartContainer" class="equity-curve-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import * as echarts from 'echarts';

interface Props {
  equityCurve: number[];
  drawdown?: number[];
  initialCapital?: number;
  dates?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  drawdown: () => [],
  initialCapital: 100000,
  dates: () => []
});

const chartContainer = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function initChart() {
  if (!chartContainer.value) return;
  
  chart = echarts.init(chartContainer.value);
  updateChart();
}

function updateChart() {
  if (!chart) return;
  
  const dates = props.dates.length > 0 
    ? props.dates 
    : props.equityCurve.map((_, i) => `Day ${i}`);
  
  // 处理drawdown数据：如果是百分比格式（>1），需要除以100
  let drawdownData = props.drawdown.length > 0 
    ? props.drawdown 
    : calculateDrawdown(props.equityCurve);
  
  // 检查drawdown数据格式，如果是百分比（>1或<-1），转换为小数
  if (drawdownData.length > 0) {
    const firstValue = Math.abs(drawdownData[0]);
    if (firstValue > 1) {
      // 是百分比格式，转换为小数
      drawdownData = drawdownData.map(d => d / 100);
    }
  }
  
  // 格式化日期显示（如果是日期字符串）
  const formattedDates = dates.map((d, i) => {
    if (typeof d === 'string' && d.includes('-')) {
      // 日期格式，只显示月-日
      const date = new Date(d);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }
    return `D${i}`;
  });
  
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: '权益曲线',
      left: 'center',
      top: 10,
      textStyle: { 
        color: '#1F2937',
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { 
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: {
        color: '#fff'
      },
      formatter: (params: any) => {
        if (Array.isArray(params)) {
          let result = `<div style="margin-bottom: 4px;"><strong>${params[0].axisValue}</strong></div>`;
          params.forEach((p: any) => {
            if (p.seriesName === '权益') {
              result += `<div style="margin: 2px 0;">${p.marker} ${p.seriesName}: <span style="color: #10B981; font-weight: bold;">¥${Number(p.value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></div>`;
            } else if (p.seriesName === '回撤') {
              result += `<div style="margin: 2px 0;">${p.marker} ${p.seriesName}: <span style="color: #EF4444; font-weight: bold;">${Number(p.value).toFixed(2)}%</span></div>`;
            }
          });
          return result;
        }
        return '';
      }
    },
    legend: {
      data: ['权益', '回撤'],
      top: 40,
      textStyle: { 
        color: '#4B5563',
        fontSize: 12
      },
      itemGap: 20
    },
    grid: [
      { left: '8%', right: '8%', top: '20%', bottom: '35%', containLabel: true },
      { left: '8%', right: '8%', top: '70%', bottom: '5%', containLabel: true }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        bottom: 10,
        height: 20,
        handleStyle: {
          color: '#4B5563'
        },
        textStyle: {
          color: '#6B7280'
        }
      }
    ],
    xAxis: [
      { 
        type: 'category', 
        data: formattedDates, 
        gridIndex: 0,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          rotate: 45,
          interval: 'auto'
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        },
        splitLine: {
          show: true,
          lineStyle: { color: '#E5E7EB', type: 'dashed' }
        }
      },
      { 
        type: 'category', 
        data: formattedDates, 
        gridIndex: 1,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          rotate: 45,
          interval: 'auto'
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        }
      }
    ],
    yAxis: [
      { 
        type: 'value', 
        name: '权益 (¥)', 
        gridIndex: 0,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          formatter: (value: number) => {
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + '万';
            }
            return value.toFixed(0);
          }
        },
        nameTextStyle: { 
          color: '#4B5563',
          fontSize: 12,
          padding: [0, 0, 0, 10]
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        },
        splitLine: {
          lineStyle: { color: '#E5E7EB', type: 'dashed' }
        }
      },
      { 
        type: 'value', 
        name: '回撤 (%)', 
        gridIndex: 1,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          formatter: (value: number) => value.toFixed(1) + '%'
        },
        nameTextStyle: { 
          color: '#4B5563',
          fontSize: 12
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '权益',
        type: 'line',
        data: props.equityCurve,
        smooth: true,
        symbol: 'none',
        lineStyle: { 
          color: '#10B981', 
          width: 3 
        },
        areaStyle: { 
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
            ]
          }
        },
        xAxisIndex: 0,
        yAxisIndex: 0,
        emphasis: {
          focus: 'series',
          lineStyle: {
            width: 4
          }
        }
      },
      {
        name: '回撤',
        type: 'line',
        data: drawdownData.map(d => {
          // 确保是百分比格式
          const value = typeof d === 'number' ? d : parseFloat(d);
          return value * 100;
        }),
        smooth: true,
        symbol: 'none',
        lineStyle: { 
          color: '#EF4444', 
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
              { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
              { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
            ]
          }
        },
        xAxisIndex: 1,
        yAxisIndex: 1,
        emphasis: {
          focus: 'series'
        }
      }
    ]
  };
  
  chart.setOption(option, true);
  // 确保图表自适应大小
  setTimeout(() => {
    chart?.resize();
  }, 100);
}

function calculateDrawdown(equity: number[]): number[] {
  const drawdown: number[] = [];
  let peak = equity[0];
  
  for (let i = 0; i < equity.length; i++) {
    if (equity[i] > peak) {
      peak = equity[i];
    }
    drawdown.push((equity[i] - peak) / peak);
  }
  
  return drawdown;
}

const handleResize = () => {
  if (chart) {
    chart.resize();
  }
};

onMounted(() => {
  nextTick(() => {
    initChart();
    window.addEventListener('resize', handleResize);
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (chart) {
    chart.dispose();
    chart = null;
  }
});

watch(() => props.equityCurve, () => {
  updateChart();
}, { deep: true });

watch(() => props.drawdown, () => {
  updateChart();
}, { deep: true });
</script>

<style scoped>
.equity-curve-chart {
  width: 100%;
  min-height: 500px;
  height: 700px;
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .equity-curve-chart {
    height: 500px;
    padding: 12px;
  }
}
</style>

