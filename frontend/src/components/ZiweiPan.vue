<template>
  <div class="ziwei-pan-container">
    <svg :width="size" :height="size" class="ziwei-pan-svg">
      <!-- 外圈十二宫位 -->
      <g v-for="(palace, index) in palaceData" :key="index">
        <!-- 宫位多边形 -->
        <polygon
          :points="getPalacePolygon(index)"
          :class="['palace-polygon', { 'ming-gong': palace.is_ming_gong, 'shen-gong': palace.is_shen_gong }]"
          :fill="getPalaceColor(palace)"
          :stroke="palace.is_ming_gong || palace.is_shen_gong ? '#3b82f6' : '#4a5568'"
          stroke-width="2"
        />
        
        <!-- 宫位名称 -->
        <text
          :x="getPalaceTextX(index)"
          :y="getPalaceTextY(index)"
          class="palace-name"
          text-anchor="middle"
        >
          {{ palace.name }}
        </text>
        
        <!-- 主星 -->
        <text
          v-for="(star, starIndex) in palace.main_stars"
          :key="`main-${starIndex}`"
          :x="getStarX(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length)"
          :y="getStarY(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length)"
          class="main-star"
          text-anchor="middle"
        >
          {{ star }}
        </text>
        
        <!-- 辅星 -->
        <text
          v-for="(star, starIndex) in palace.auxiliary_stars"
          :key="`aux-${starIndex}`"
          :x="getStarX(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length)"
          :y="getStarY(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length)"
          class="auxiliary-star"
          text-anchor="middle"
        >
          {{ star }}
        </text>
        
        <!-- 四化标记 -->
        <text
          v-if="palace.si_hua"
          :x="getSiHuaX(index, palace.main_stars.length, palace.auxiliary_stars.length)"
          :y="getSiHuaY(index, palace.main_stars.length, palace.auxiliary_stars.length)"
          class="si-hua-mark"
          text-anchor="middle"
        >
          {{ palace.si_hua }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  panData: any;
  size?: number;
}>();

const size = computed(() => props.size || 900);
const center = computed(() => size.value / 2);
const radius = computed(() => size.value * 0.35);

// 十二宫位名称
const PALACE_NAMES = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母'];

// 构建宫位数据
const palaceData = computed(() => {
  if (!props.panData || !props.panData.palaces) {
    return [];
  }
  
  const palaces = props.panData.palaces || [];
  const mainStars = props.panData.main_stars || {};
  const auxiliaryStars = props.panData.auxiliary_stars || {};
  const siHua = props.panData.si_hua || {};
  const mingGong = props.panData.ming_gong || 0;
  const shenGong = props.panData.shen_gong || 0;
  
  return palaces.map((palace: any, index: number) => {
    // 找出这个宫位的主星
    const mainStarsList: string[] = [];
    Object.entries(mainStars).forEach(([star, pos]) => {
      if (pos === index) {
        mainStarsList.push(star);
      }
    });
    
    // 找出这个宫位的辅星
    const auxiliaryStarsList: string[] = [];
    Object.entries(auxiliaryStars).forEach(([star, pos]) => {
      if (pos === index) {
        auxiliaryStarsList.push(star);
      }
    });
    
    // 找出这个宫位的四化（从palace数据中获取）
    let siHuaMark = '';
    if (palace.si_hua && Array.isArray(palace.si_hua)) {
      siHuaMark = palace.si_hua.join('');
    } else if (palace.si_hua) {
      siHuaMark = String(palace.si_hua);
    }
    
    return {
      name: palace.name || PALACE_NAMES[index],
      main_stars: mainStarsList,
      auxiliary_stars: auxiliaryStarsList,
      si_hua: siHuaMark,
      is_ming_gong: index === mingGong,
      is_shen_gong: index === shenGong,
    };
  });
});

// 计算宫位多边形顶点
const getPalacePolygon = (index: number): string => {
  const angle = (index * 30 - 90) * (Math.PI / 180); // 每个宫位30度，从上方开始
  const innerRadius = radius.value * 0.6;
  const outerRadius = radius.value;
  
  const x1 = center.value + innerRadius * Math.cos(angle - Math.PI / 12);
  const y1 = center.value + innerRadius * Math.sin(angle - Math.PI / 12);
  const x2 = center.value + outerRadius * Math.cos(angle - Math.PI / 12);
  const y2 = center.value + outerRadius * Math.sin(angle - Math.PI / 12);
  const x3 = center.value + outerRadius * Math.cos(angle + Math.PI / 12);
  const y3 = center.value + outerRadius * Math.sin(angle + Math.PI / 12);
  const x4 = center.value + innerRadius * Math.cos(angle + Math.PI / 12);
  const y4 = center.value + innerRadius * Math.sin(angle + Math.PI / 12);
  
  return `${x1},${y1} ${x2},${y2} ${x3},${y3} ${x4},${y4}`;
};

// 计算宫位名称位置
const getPalaceTextX = (index: number): number => {
  const angle = (index * 30 - 90) * (Math.PI / 180);
  const textRadius = radius.value * 0.85;
  return center.value + textRadius * Math.cos(angle);
};

const getPalaceTextY = (index: number): number => {
  const angle = (index * 30 - 90) * (Math.PI / 180);
  const textRadius = radius.value * 0.85;
  return center.value + textRadius * Math.sin(angle) + 5;
};

// 计算星曜位置（优化版本，避免重叠）
const getStarX = (
  palaceIndex: number,
  starIndex: number,
  totalStars: number,
  type: 'main' | 'aux',
  otherTypeCount: number
): number => {
  const angle = (palaceIndex * 30 - 90) * (Math.PI / 180);
  const starRadius = radius.value * 0.72;
  
  // 水平偏移：星曜沿切线方向分布
  // 根据星曜数量动态调整间距，单字宽度约18px，留出足够间距
  const baseSpacing = 22; // 基础间距（像素）
  const offset = totalStars > 1 
    ? (starIndex - (totalStars - 1) / 2) * baseSpacing
    : 0;
  
  // 沿切线方向偏移（垂直于半径方向）
  const baseX = center.value + starRadius * Math.cos(angle);
  const offsetX = offset * Math.sin(angle);
  
  return baseX + offsetX;
};

const getStarY = (
  palaceIndex: number,
  starIndex: number,
  totalStars: number,
  type: 'main' | 'aux',
  otherTypeCount: number
): number => {
  const angle = (palaceIndex * 30 - 90) * (Math.PI / 180);
  const starRadius = radius.value * 0.72;
  
  // 垂直偏移：主星在上，辅星在下，分层显示
  // 每层内的星曜垂直间距也要考虑
  let verticalOffset = 0;
  const baseSpacing = 22; // 水平偏移基础间距
  const offset = totalStars > 1 
    ? (starIndex - (totalStars - 1) / 2) * baseSpacing
    : 0;
  
  if (type === 'main') {
    // 主星层：在中心线偏上
    // 如果有多个主星，垂直方向也稍微错开
    verticalOffset = -12; // 基础偏移
    if (totalStars > 1) {
      // 多个主星时，垂直方向也错开一些
      verticalOffset += (starIndex - (totalStars - 1) / 2) * 3;
    }
  } else {
    // 辅星层：在中心线偏下，且要考虑主星的高度
    const mainStarHeight = otherTypeCount > 0 ? 20 : 0; // 如果有主星，需要为它们留出空间
    verticalOffset = mainStarHeight + 12; // 基础偏移
    if (totalStars > 1) {
      // 多个辅星时，垂直方向也错开一些
      verticalOffset += (starIndex - (totalStars - 1) / 2) * 3;
    }
  }
  
  const baseY = center.value + starRadius * Math.sin(angle);
  // 沿半径方向也要考虑水平偏移的影响
  const offsetY = -offset * Math.cos(angle);
  
  return baseY + verticalOffset + offsetY;
};

// 计算四化标记位置（避免与星曜重叠）
const getSiHuaX = (palaceIndex: number, mainStarCount: number, auxStarCount: number): number => {
  const angle = (palaceIndex * 30 - 90) * (Math.PI / 180);
  const textRadius = radius.value * 0.75;
  return center.value + textRadius * Math.cos(angle);
};

const getSiHuaY = (palaceIndex: number, mainStarCount: number, auxStarCount: number): number => {
  const angle = (palaceIndex * 30 - 90) * (Math.PI / 180);
  const textRadius = radius.value * 0.75;
  const baseY = center.value + textRadius * Math.sin(angle);
  
  // 根据星曜数量调整四化标记位置，避免重叠
  const totalStars = mainStarCount + auxStarCount;
  let offset = 25; // 基础偏移
  if (totalStars > 3) {
    offset = 35; // 星曜多时，四化标记再往下移
  } else if (totalStars > 1) {
    offset = 30;
  }
  
  return baseY + offset;
};

// 获取宫位颜色
const getPalaceColor = (palace: any): string => {
  if (palace.is_ming_gong) return '#1e3a8a';
  if (palace.is_shen_gong) return '#7c3aed';
  return '#1f2937';
};
</script>

<style scoped>
.ziwei-pan-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #111827;
  border-radius: 12px;
}

.ziwei-pan-svg {
  background: #0f172a;
  border-radius: 50%;
}

.palace-polygon {
  opacity: 0.8;
}

.palace-polygon.ming-gong {
  opacity: 1;
  stroke-width: 3;
}

.palace-polygon.shen-gong {
  opacity: 1;
  stroke-width: 3;
}

.palace-name {
  font-size: 17px;
  font-weight: 600;
  fill: #e5e7eb;
}

.main-star {
  font-size: 15px;
  font-weight: 600;
  fill: #fbbf24;
}

.auxiliary-star {
  font-size: 13px;
  fill: #60a5fa;
}

.si-hua-mark {
  font-size: 14px;
  font-weight: 600;
  fill: #f87171;
}
</style>

