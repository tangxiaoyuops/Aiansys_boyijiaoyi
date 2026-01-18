<template>
  <div ref="chartContainer" class="kline-chart"></div>
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
  open_interest?: number;
}

interface TradeLog {
  time: string;
  action: string;
  price: number;
  size: number;
  reason?: string;
}

interface Props {
  klineData: KlineData[];
  tradeLog?: TradeLog[];
}

const props = withDefaults(defineProps<Props>(), {
  tradeLog: () => []
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
  
  // 数据验证：检查K线数据的有效性
  let invalidDataCount = 0;
  const validationErrors: string[] = [];
  
  props.klineData.forEach((d, index) => {
    const open = Number(d.open) || 0;
    const close = Number(d.close) || 0;
    const high = Number(d.high) || 0;
    const low = Number(d.low) || 0;
    
    // 检查价格是否有效（>0）
    if (open <= 0 || close <= 0 || high <= 0 || low <= 0) {
      invalidDataCount++;
      if (validationErrors.length < 5) {  // 最多记录5个错误
        validationErrors.push(`第${index + 1}条数据价格无效（open:${open}, close:${close}, high:${high}, low:${low}）`);
      }
    }
    
    // 检查OHLC逻辑关系
    if (high < low || high < open || high < close || low > open || low > close) {
      invalidDataCount++;
      if (validationErrors.length < 5) {
        validationErrors.push(`第${index + 1}条数据OHLC逻辑错误（high:${high}, low:${low}, open:${open}, close:${close}）`);
      }
    }
  });
  
  // 如果无效数据过多（超过20%），显示错误提示
  if (invalidDataCount > props.klineData.length * 0.2) {
    console.error('[K线图] 数据验证失败:', {
      invalidCount: invalidDataCount,
      totalCount: props.klineData.length,
      errors: validationErrors
    });
    
    // 清空图表并显示错误信息（可以通过修改组件支持显示错误信息）
    chart.clear();
    chart.setOption({
      title: {
        text: 'K线数据异常',
        subtext: `检测到${invalidDataCount}/${props.klineData.length}条无效数据`,
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#EF4444',
          fontSize: 16
        },
        subtextStyle: {
          color: '#6B7280',
          fontSize: 12
        }
      }
    });
    return;
  }
  
  // 如果有少量无效数据，只记录警告
  if (invalidDataCount > 0) {
    console.warn(`[K线图] 检测到${invalidDataCount}条无效数据，将使用默认值`, validationErrors.slice(0, 3));
  }
  
  // 准备K线数据 [开盘, 收盘, 最低, 最高] - 对于category类型的xAxis，不需要索引
  const klineSeries = props.klineData.map((d) => {
    const open = Number(d.open) || 0;
    const close = Number(d.close) || 0;
    const low = Number(d.low) || 0;
    const high = Number(d.high) || 0;
    
    // 如果数据无效，使用前一条数据或默认值
    if (open <= 0 || close <= 0 || high <= 0 || low <= 0) {
      // 尝试使用收盘价作为默认值
      const defaultPrice = close > 0 ? close : (open > 0 ? open : 1);
      return [defaultPrice, defaultPrice, defaultPrice, defaultPrice];
    }
    
    return [open, close, low, high];
  });
  
  // 准备成交量数据 - 直接是数值数组
  const volumeSeries = props.klineData.map((d) => Number(d.volume) || 0);
  
  // 先格式化日期数组（用于xAxis）
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
  
  // 辅助函数：将日期字符串统一转换为 YYYY-MM-DD 格式（使用本地时间，忽略时区）
  function normalizeDate(dateStr: string | Date): string | null {
    if (!dateStr) return null;
    
    // 如果已经是 YYYY-MM-DD 格式，直接返回
    if (typeof dateStr === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr;
    }
    
    try {
      // 解析日期字符串，但使用本地日期部分（忽略时区）
      const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
      if (isNaN(date.getTime())) {
        return null;
      }
      
      // 使用本地日期部分（而不是UTC），避免时区偏移导致的日期差异
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    } catch (e) {
      console.warn('日期格式化失败:', dateStr, e);
      return null;
    }
  }
  
  // 创建日期映射表，用于快速查找（使用统一的日期格式）
  const dateMap = new Map<string, number>();
  props.klineData.forEach((k, index) => {
    const normalizedDate = normalizeDate(k.date);
    if (normalizedDate) {
      dateMap.set(normalizedDate, index);
    }
  });
  
  // 格式化交易动作
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
  
  // 准备交易标记点数据（使用markPoint）
  const tradeMarkPoints: any[] = [];
  
  if (props.tradeLog && props.tradeLog.length > 0) {
    console.log(`[K线图] 开始处理 ${props.tradeLog.length} 条交易记录`);
    
    props.tradeLog.forEach((trade, tradeIndex) => {
      try {
        // 使用统一的日期格式化函数
        const tradeDateStr = normalizeDate(trade.time);
        if (!tradeDateStr) {
          console.warn(`[K线图] 交易记录 ${tradeIndex} 日期无效:`, trade.time);
          return;
        }
        
        // 直接从映射表中查找
        let klineIndex = dateMap.get(tradeDateStr);
        
        // 如果精确匹配失败，尝试找最接近的日期（前后1天）
        if (klineIndex === undefined) {
          const tradeDate = new Date(trade.time);
          if (!isNaN(tradeDate.getTime())) {
            const targetTime = new Date(tradeDate.getFullYear(), tradeDate.getMonth(), tradeDate.getDate()).getTime();
            let minDiff = Infinity;
            let bestIndex = -1;
            
            props.klineData.forEach((k, idx) => {
              const kNormalized = normalizeDate(k.date);
              if (kNormalized) {
                const kDate = new Date(kNormalized);
                if (!isNaN(kDate.getTime())) {
                  const kDateOnly = new Date(kDate.getFullYear(), kDate.getMonth(), kDate.getDate());
                  const diff = Math.abs(kDateOnly.getTime() - targetTime);
                  if (diff < minDiff && diff <= 86400000) { // 1天内的差异
                    minDiff = diff;
                    bestIndex = idx;
                  }
                }
              }
            });
            
            if (bestIndex >= 0) {
              klineIndex = bestIndex;
              console.log(`[K线图] 交易记录 ${tradeIndex} 使用最接近的日期匹配:`, trade.time, `(${tradeDateStr})`, '->', props.klineData[bestIndex].date);
            }
          }
        } else {
          // 添加调试日志
          console.log(`[K线图] 交易记录 ${tradeIndex} 日期匹配成功:`, trade.time, `(${tradeDateStr})`, '-> 索引', klineIndex, 'K线日期:', props.klineData[klineIndex]?.date);
        }
        
        if (klineIndex !== undefined && klineIndex < dates.length) {
          const klinePoint = props.klineData[klineIndex];
          const isBuy = trade.action.includes('OPEN_LONG') || trade.action.includes('CLOSE_SHORT');
          
          // 使用日期字符串作为coord的x值，因为xAxis是category类型
          const dateStr = dates[klineIndex];
          const markPoint: any = {
            name: `${formatAction(trade.action)} ${trade.size}手`,
            coord: [dateStr, trade.price],
            value: trade.price,
            symbolSize: 20,
            symbol: isBuy ? 'triangle' : 'triangle',
            symbolRotate: isBuy ? 180 : 0,
            itemStyle: {
              color: isBuy ? '#10B981' : '#EF4444',
              borderColor: '#ffffff',
              borderWidth: 2
            },
            label: {
              show: true,
              position: isBuy ? 'bottom' : 'top',
              formatter: `${formatAction(trade.action)}\n${trade.size}手`,
              fontSize: 10,
              color: '#ffffff',
              backgroundColor: isBuy ? '#10B981' : '#EF4444',
              padding: [4, 6],
              borderRadius: 4,
              borderWidth: 0
            }
          };
          
          tradeMarkPoints.push(markPoint);
          console.log(`[K线图] 添加交易标记点: ${formatAction(trade.action)} @ ${dateStr}, 价格: ${trade.price}`);
        } else {
          console.warn(`[K线图] 交易记录 ${tradeIndex} 无法匹配到K线日期:`, trade.time, '可用日期数量:', dates.length);
        }
      } catch (e) {
        console.warn(`[K线图] 处理交易记录 ${tradeIndex} 失败:`, trade, e);
      }
    });
    
    console.log(`[K线图] 共创建 ${tradeMarkPoints.length} 个交易标记点`);
  } else {
    console.log('[K线图] 没有交易记录或交易记录为空');
  }
  
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    title: {
      text: 'K线图与交易记录',
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
      data: ['K线', '成交量'],
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
          data: tradeMarkPoints,
          animation: true
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
            const data = params.data;
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

watch(() => props.tradeLog, () => {
  updateChart();
}, { deep: true });
</script>

<style scoped>
.kline-chart {
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
  .kline-chart {
    height: 500px;
    padding: 12px;
  }
}
</style>

