<template>
  <div class="bazi-chart">
    <svg :width="size" :height="size" class="chart-svg">
      <!-- 四柱显示 -->
      <g class="sizhu-group">
        <g v-for="(zhu, index) in sizhuList" :key="index" :transform="`translate(${size / 2}, ${getZhuY(index)})`">
          <!-- 天干 -->
          <text
            class="tiangan-text"
            :x="0"
            :y="0"
            text-anchor="middle"
            dominant-baseline="middle"
          >
            {{ zhu.gan }}
          </text>
          <!-- 地支 -->
          <text
            class="dizhi-text"
            :x="0"
            :y="20"
            text-anchor="middle"
            dominant-baseline="middle"
          >
            {{ zhu.zhi }}
          </text>
          <!-- 柱名称 -->
          <text
            class="zhu-name-text"
            :x="size / 2 - 60"
            :y="10"
            text-anchor="end"
            dominant-baseline="middle"
          >
            {{ zhu.name }}
          </text>
        </g>
      </g>

      <!-- 五行分布图 -->
      <g v-if="wuxingAnalysis" class="wuxing-group" :transform="`translate(${size / 2}, ${size - 100})`">
        <circle
          v-for="(item, index) in wuxingData"
          :key="item.name"
          :cx="getWuxingX(index)"
          :cy="0"
          :r="getWuxingRadius(item.value)"
          :fill="getWuxingColor(item.name)"
          :opacity="0.7"
          class="wuxing-circle"
        />
        <text
          v-for="(item, index) in wuxingData"
          :key="`${item.name}-label`"
          :x="getWuxingX(index)"
          :y="30"
          text-anchor="middle"
          dominant-baseline="middle"
          class="wuxing-label"
        >
          {{ item.name }}: {{ item.value }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  sizhu?: any;
  wuxingAnalysis?: any;
  shishenAnalysis?: any;
  size?: number;
}

const props = withDefaults(defineProps<Props>(), {
  size: 400,
});

const sizhuList = computed(() => {
  if (!props.sizhu) return [];
  
  return [
    {
      name: '年柱',
      gan: props.sizhu.nian_zhu?.tian_gan || '',
      zhi: props.sizhu.nian_zhu?.di_zhi || '',
    },
    {
      name: '月柱',
      gan: props.sizhu.yue_zhu?.tian_gan || '',
      zhi: props.sizhu.yue_zhu?.di_zhi || '',
    },
    {
      name: '日柱',
      gan: props.sizhu.ri_zhu?.tian_gan || '',
      zhi: props.sizhu.ri_zhu?.di_zhi || '',
    },
    {
      name: '时柱',
      gan: props.sizhu.shi_zhu?.tian_gan || '',
      zhi: props.sizhu.shi_zhu?.di_zhi || '',
    },
  ];
});

const wuxingData = computed(() => {
  if (!props.wuxingAnalysis?.wuxing_data) return [];
  
  const data = props.wuxingAnalysis.wuxing_data;
  return [
    { name: '金', value: data.jin || 0 },
    { name: '木', value: data.mu || 0 },
    { name: '水', value: data.shui || 0 },
    { name: '火', value: data.huo || 0 },
    { name: '土', value: data.tu || 0 },
  ].filter(item => item.value > 0);
});

const getZhuY = (index: number) => {
  const startY = 60;
  const spacing = 60;
  return startY + index * spacing;
};

const getWuxingX = (index: number) => {
  const total = wuxingData.value.length;
  const spacing = props.size / (total + 1);
  return (index + 1) * spacing - props.size / 2;
};

const getWuxingRadius = (value: number) => {
  const maxValue = Math.max(...wuxingData.value.map(item => item.value), 1);
  return 15 + (value / maxValue) * 20;
};

const getWuxingColor = (name: string) => {
  const colorMap: Record<string, string> = {
    '金': '#FFD700',
    '木': '#32CD32',
    '水': '#1E90FF',
    '火': '#FF4500',
    '土': '#8B4513',
  };
  return colorMap[name] || '#999';
};
</script>

<style scoped>
.bazi-chart {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.chart-svg {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.tiangan-text {
  font-size: 24px;
  font-weight: 600;
  fill: #333;
}

.dizhi-text {
  font-size: 20px;
  font-weight: 500;
  fill: #666;
}

.zhu-name-text {
  font-size: 14px;
  fill: #999;
}

.wuxing-circle {
  stroke: #333;
  stroke-width: 2;
}

.wuxing-label {
  font-size: 12px;
  fill: #333;
  font-weight: 500;
}
</style>


