<template>
  <div ref="chartContainer" class="selection-kline-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import * as echarts from 'echarts';

interface KlineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface BuySignal {
  buy_type: string;
  date: string;
  price: number;
  score: number;
  confidence: number;
  reasoning: string;
}

interface Props {
  klineData: KlineData[];
  buySignals?: BuySignal[];
}

const props = withDefaults(defineProps<Props>(), {
  buySignals: () => []
});

const chartContainer = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function initChart() {
  if (!chartContainer.value) return;
  
  chart = echarts.init(chartContainer.value);
  updateChart();
}

function updateChart() {
  if (!chart || !props.klineData || props.klineData.length === 0) return;
  
  // 准备K线数据 [开盘, 收盘, 最低, 最高]
  const klineSeries = props.klineData.map((d) => {
    const open = Number(d.open) || 0;
    const close = Number(d.close) || 0;
    const low = Number(d.low) || 0;
    const high = Number(d.high) || 0;
    
    return [open, close, low, high];
  });
  
  // 准备成交量数据
  const volumeSeries = props.klineData.map((d) => Number(d.volume) || 0);
  
  // 格式化日期数组
  const dates = props.klineData.map(d => {
    try {
      const date = new Date(d.date);
      if (isNaN(date.getTime())) {
        return String(d.date);
      }
      return `${date.getMonth() + 1}/${date.getDate()}`;
    } catch (e) {
      return String(d.date);
    }
  });
  
  // 辅助函数：将日期字符串统一转换为 YYYY-MM-DD 格式
  function normalizeDate(dateStr: string | Date): string | null {
    if (!dateStr) return null;
    
    // 如果已经是 YYYY-MM-DD 格式，直接返回
    if (typeof dateStr === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr;
    }
    
    try {
      const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
      if (isNaN(date.getTime())) {
        return null;
      }
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    } catch (e) {
      return null;
    }
  }
  
  // 创建日期映射表
  const dateMap = new Map<string, number>();
  props.klineData.forEach((k, index) => {
    const normalizedDate = normalizeDate(k.date);
    if (normalizedDate) {
      dateMap.set(normalizedDate, index);
    }
  });
  
  // 格式化买点类型
  function formatBuyType(type: string): string {
    const typeMap: Record<string, string> = {
      'panic_point': '恐慌点',
      'lowest_after_panic': '恐慌后最低',
      'o_point': 'O点',
      'washout_end': '洗盘结束',
      'buy_signal': '买入信号'
    };
    return typeMap[type] || type;
  }
  
  // 准备买点标记数据
  const buyPointMarks: any[] = [];
  
  if (props.buySignals && props.buySignals.length > 0) {
    console.log(`[选股K线图] 处理 ${props.buySignals.length} 个买入信号`);
    
    props.buySignals.forEach((signal, index) => {
      try {
        const pointDateStr = normalizeDate(signal.date);
        if (!pointDateStr) {
          console.warn(`[选股K线图] 信号 ${index} 日期无效:`, signal.date);
          return;
        }
        
        // 从映射表中查找
        let klineIndex = dateMap.get(pointDateStr);
        
        // 如果精确匹配失败，尝试找最接近的日期
        if (klineIndex === undefined) {
          const pointDate = new Date(signal.date);
          if (!isNaN(pointDate.getTime())) {
            const targetTime = new Date(pointDate.getFullYear(), pointDate.getMonth(), pointDate.getDate()).getTime();
            let minDiff = Infinity;
            let bestIndex = -1;
            
            props.klineData.forEach((k, idx) => {
              const kNormalized = normalizeDate(k.date);
              if (kNormalized) {
                const kDate = new Date(kNormalized);
                if (!isNaN(kDate.getTime())) {
                  const kDateOnly = new Date(kDate.getFullYear(), kDate.getMonth(), kDate.getDate());
                  const diff = Math.abs(kDateOnly.getTime() - targetTime);
                  if (diff < minDiff && diff <= 86400000) {
                    minDiff = diff;
                    bestIndex = idx;
                  }
                }
              }
            });
            
            if (bestIndex >= 0) {
              klineIndex = bestIndex;
            }
          }
        }
        
        if (klineIndex !== undefined && klineIndex < dates.length) {
          const dateStr = dates[klineIndex];
          
          // 使用不同颜色区分买点类型
          let color = '#10B981'; // 默认绿色
          if (signal.buy_type === 'panic_point') {
            color = '#EF4444'; // 恐慌点用红色
          } else if (signal.buy_type === 'o_point') {
            color = '#3B82F6'; // O点用蓝色
          } else if (signal.buy_type === 'washout_end') {
            color = '#F59E0B'; // 洗盘结束用橙色
          }
          
          const markPoint: any = {
            name: `${formatBuyType(signal.buy_type)} 评分${signal.score.toFixed(0)}`,
            coord: [dateStr, signal.price],
            value: signal.price,
            symbolSize: 25,
            symbol: 'triangle',
            symbolRotate: 180, // 三角形朝上表示买入
            itemStyle: {
              color: color,
              borderColor: '#ffffff',
              borderWidth: 2,
              shadowBlur: 4,
              shadowColor: 'rgba(0, 0, 0, 0.3)',
              shadowOffsetY: 2
            },
            label: {
              show: true,
              position: 'bottom',
              formatter: `${formatBuyType(signal.buy_type)}\n评分: ${signal.score.toFixed(0)}`,
              fontSize: 11,
              color: '#ffffff',
              backgroundColor: color,
              padding: [4, 8],
              borderRadius: 6,
              fontWeight: 'bold'
            }
          };
          
          buyPointMarks.push(markPoint);
          console.log(`[选股K线图] 添加买入标记: ${formatBuyType(signal.buy_type)} @ ${dateStr}, 价格: ${signal.price}`);
        } else {
          console.warn(`[选股K线图] 信号 ${index} 无法匹配到K线日期:`, signal.date);
        }
      } catch (e) {
        console.warn(`[选股K线图] 处理信号 ${index} 失败:`, signal, e);
      }
    });
    
    console.log(`[选股K线图] 共创建 ${buyPointMarks.length} 个买入标记`);
  }
  
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: '股票K线图与买点信号',
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
        type: 'cross'
      },
      formatter: (params: any) => {
        if (Array.isArray(params)) {
          let result = `<div style="margin-bottom: 4px;"><strong>${params[0].axisValue}</strong></div>`;
          
          params.forEach((p: any) => {
            if (p.seriesName === 'K线') {
              const data = p.data as number[];
              result += `
                <div style="margin: 2px 0;">
                  ${p.marker} ${p.seriesName}: 
                  <span style="color: #10B981;">开: ${data[1].toFixed(2)}</span> | 
                  <span style="color: #EF4444;">收: ${data[2].toFixed(2)}</span> | 
                  <span style="color: #6B7280;">高: ${data[4].toFixed(2)}</span> | 
                  <span style="color: #6B7280;">低: ${data[3].toFixed(2)}</span>
                </div>
              `;
            } else if (p.seriesName === '成交量') {
              result += `<div style="margin: 2px 0;">${p.marker} ${p.seriesName}: ${p.value.toLocaleString()}</div>`;
            }
          });
          
          return result;
        }
        return '';
      }
    },
    legend: {
      data: ['K线', '成交量', '买点信号'],
      top: 40,
      textStyle: { 
        color: '#4B5563',
        fontSize: 12
      },
      itemGap: 20
    },
    grid: [
      { left: '10%', right: '8%', top: '15%', bottom: '40%', containLabel: true },
      { left: '10%', right: '8%', top: '65%', bottom: '5%', containLabel: true }
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
        data: dates, 
        gridIndex: 0,
        boundaryGap: false,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          rotate: 45,
          interval: Math.max(1, Math.floor(dates.length / 10))
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        },
        splitLine: {
          show: false
        }
      },
      { 
        type: 'category', 
        data: dates, 
        gridIndex: 1,
        boundaryGap: false,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          rotate: 45,
          interval: Math.max(1, Math.floor(dates.length / 10))
        },
        axisLine: {
          lineStyle: { color: '#D1D5DB' }
        }
      }
    ],
    yAxis: [
      { 
        type: 'value', 
        name: '价格 (¥)', 
        gridIndex: 0,
        scale: true,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11,
          formatter: (value: number) => value.toFixed(2)
        },
        nameTextStyle: { 
          color: '#4B5563',
          fontSize: 12
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
        name: '成交量', 
        gridIndex: 1,
        axisLabel: { 
          color: '#6B7280',
          fontSize: 11
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
        name: 'K线',
        type: 'candlestick',
        data: klineSeries,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#10B981',  // 上涨颜色
          color0: '#EF4444',  // 下跌颜色
          borderColor: '#10B981',
          borderColor0: '#EF4444'
        },
        markPoint: {
          data: buyPointMarks,
          animation: true,
          animationDuration: 1000,
          animationEasing: 'elasticOut'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumeSeries,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: (params: any) => {
            const klinePoint = props.klineData[params.dataIndex];
            if (klinePoint && klinePoint.close >= klinePoint.open) {
              return 'rgba(16, 185, 129, 0.6)';
            } else {
              return 'rgba(239, 68, 68, 0.6)';
            }
          }
        }
      },
    ]
  };
  
  chart.setOption(option, true);
  setTimeout(() => {
    chart?.resize();
  }, 100);
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

watch(() => props.klineData, () => {
  updateChart();
}, { deep: true });

watch(() => props.buySignals, () => {
  updateChart();
}, { deep: true });
</script>

<style scoped>
.selection-kline-chart {
  width: 100%;
  min-height: 500px;
  height: 600px;
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .selection-kline-chart {
    height: 450px;
    padding: 12px;
  }
}
</style>