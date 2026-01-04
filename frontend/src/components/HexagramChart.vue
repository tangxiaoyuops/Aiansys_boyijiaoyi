<template>
  <div class="hexagram-chart-container">
    <svg :width="size" :height="size" class="hexagram-chart-svg">
      <!-- 绘制六个爻（从下往上） -->
      <g v-for="(yao, index) in yaos" :key="index" :class="['yao-group', { 'dong-yao': isDongYao(index) }]">
        <!-- 阳爻：一条实线，阴爻：两段实线（中间有间隔） -->
        <template v-if="yao.is_yang">
          <!-- 阳爻：一条完整的实线 -->
          <line
            :x1="lineStartX"
            :y1="getYaoY(index)"
            :x2="lineEndX"
            :y2="getYaoY(index)"
            :class="['yao-line', 'yang-yao']"
            :stroke-width="lineWidth"
          />
        </template>
        <template v-else>
          <!-- 阴爻：两段实线，中间有间隔 -->
          <line
            :x1="lineStartX"
            :y1="getYaoY(index)"
            :x2="lineStartX + lineLength * 0.4"
            :y2="getYaoY(index)"
            :class="['yao-line', 'yin-yao']"
            :stroke-width="lineWidth"
          />
          <line
            :x1="lineEndX - lineLength * 0.4"
            :y1="getYaoY(index)"
            :x2="lineEndX"
            :y2="getYaoY(index)"
            :class="['yao-line', 'yin-yao']"
            :stroke-width="lineWidth"
          />
        </template>
        
        <!-- 爻标签（小尺寸时隐藏） -->
        <text
          v-if="size >= 200"
          :x="labelX"
          :y="getYaoY(index) + 5"
          class="yao-label"
          text-anchor="middle"
        >
          {{ getYaoLabel(index) }}
        </text>
      </g>
      
      <!-- 卦名显示（小尺寸时隐藏） -->
      <text
        v-if="size >= 200"
        :x="centerX"
        :y="size - 40"
        class="hexagram-name"
        text-anchor="middle"
      >
        {{ hexagramName }}
      </text>
      
      <!-- 内卦和外卦标识（小尺寸时隐藏） -->
      <text
        v-if="size >= 200"
        :x="centerX"
        :y="size - 20"
        class="trigram-info"
        text-anchor="middle"
      >
        {{ trigramInfo }}
      </text>
    </svg>
    
    <!-- 变卦显示（如果有） -->
    <div v-if="bianHexagram" class="bian-hexagram-section">
      <h4 class="section-title">变卦</h4>
      <div class="bian-hexagram-name">{{ bianHexagram.full_name }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  hexagramData: any;
  size?: number;
}

const props = withDefaults(defineProps<Props>(), {
  size: 400,
});

const size = computed(() => props.size);
const centerX = computed(() => size.value / 2);
const lineLength = computed(() => size.value >= 200 ? 160 : size.value * 0.6);
const lineStartX = computed(() => centerX.value - lineLength.value / 2);
const lineEndX = computed(() => centerX.value + lineLength.value / 2);
const labelX = computed(() => centerX.value);
const lineWidth = computed(() => size.value >= 200 ? 10 : 8); // 增加线条宽度，更粗更美观
const yaoSpacing = computed(() => (size.value - (size.value >= 200 ? 100 : 60)) / 6);

const yaos = computed(() => {
  // 确保数组顺序正确：从下往上（初爻、二爻、三爻、四爻、五爻、上爻）
  const yaosArray = props.hexagramData?.yaos || [];
  // 如果数组是空的或者长度不对，返回空数组
  if (!yaosArray || yaosArray.length !== 6) {
    return [];
  }
  // 直接返回，假设后端已经按照从下往上的顺序排列
  return yaosArray;
});

const hexagramName = computed(() => {
  return props.hexagramData?.ben_hexagram?.full_name || '未知卦';
});

const trigramInfo = computed(() => {
  const inner = props.hexagramData?.inner_trigram?.name || '未知';
  const outer = props.hexagramData?.outer_trigram?.name || '未知';
  return `${outer}上${inner}下`;
});

const bianHexagram = computed(() => {
  return props.hexagramData?.bian_hexagram || null;
});

const dongYaoIndices = computed(() => {
  return props.hexagramData?.dong_yaos || [];
});

function getYaoY(index: number): number {
  // 从下往上排列（第0个爻=初爻在最下面，第5个爻=上爻在最上面）
  // SVG 坐标系：y 值越大越靠下
  const topMargin = size.value >= 200 ? 40 : 20;
  const bottomMargin = size.value >= 200 ? 100 : 60;
  const availableHeight = size.value - topMargin - bottomMargin;
  
  // index 0 (初爻) 在最下面（y值最大），index 5 (上爻) 在最上面（y值最小）
  // 从下往上：初爻在最下面，所以 y = size - bottomMargin - 0 * spacing
  // 上爻在最上面，所以 y = size - bottomMargin - 5 * spacing
  return size.value - bottomMargin - index * yaoSpacing.value;
}

function getYaoLabel(index: number): string {
  // 爻名数组：从下往上（初、二、三、四、五、上）
  const yaoNames = ['初', '二', '三', '四', '五', '上'];
  const yao = yaos.value[index];
  if (!yao) return '';
  
  const yaoName = yaoNames[index];
  const yaoType = yao.is_yang ? '九' : '六';
  const dongMark = yao.is_dong ? '（动）' : '';
  return `${yaoName}${yaoType}${dongMark}`;
}

function isDongYao(index: number): boolean {
  return dongYaoIndices.value.includes(index);
}
</script>

<style scoped>
.hexagram-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.hexagram-chart-svg {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.yao-group {
  transition: all 0.3s;
}

.yao-line {
  stroke: #e5e7eb;
}

.yang-yao {
  stroke: #3b82f6;
  stroke-dasharray: none;
  stroke-linecap: round; /* 圆角端点，更美观 */
}

.yin-yao {
  stroke: #9ca3af;
  stroke-dasharray: none; /* 不再使用虚线，改为两段实线 */
  stroke-linecap: round; /* 圆角端点，更美观 */
}

.dong-yao .yao-line {
  stroke: #ef4444;
  stroke-width: 5;
  filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.5));
}

.yao-label {
  font-size: 14px;
  fill: #e5e7eb;
  font-weight: 500;
}

.dong-yao .yao-label {
  fill: #ef4444;
  font-weight: bold;
}

.hexagram-name {
  font-size: 24px;
  font-weight: bold;
  fill: #3b82f6;
}

.trigram-info {
  font-size: 14px;
  fill: #9ca3af;
}

.bian-hexagram-section {
  text-align: center;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  min-width: 200px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #ef4444;
  margin: 0 0 8px 0;
}

.bian-hexagram-name {
  font-size: 20px;
  color: #e5e7eb;
  font-weight: 500;
}
</style>

