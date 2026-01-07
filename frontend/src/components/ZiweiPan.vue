<template>
  <div class="ziwei-pan-wrapper">
    <!-- 缩放控制按钮 -->
    <div class="zoom-controls">
      <el-button-group>
        <el-button @click="zoomIn" :icon="ZoomIn" size="small" circle />
        <el-button @click="zoomOut" :icon="ZoomOut" size="small" circle />
        <el-button @click="resetZoom" :icon="Refresh" size="small" circle />
      </el-button-group>
      <div class="zoom-level">{{ Math.round(scale * 100) }}%</div>
    </div>

    <!-- 命盘容器 - 支持缩放和平移 -->
    <div 
      class="ziwei-pan-container" 
      ref="containerRef"
      @wheel.prevent="handleWheel"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    >
      <div 
        class="pan-transform"
        :style="{
          transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
          transformOrigin: 'center center'
        }"
      >
        <svg 
          :width="baseSize" 
          :height="baseSize" 
          class="ziwei-pan-svg"
          :viewBox="`0 0 ${baseSize} ${baseSize}`"
          preserveAspectRatio="xMidYMid meet"
        >
          <!-- 定义渐变和滤镜 -->
          <defs>
            <!-- 宫位渐变 -->
            <linearGradient id="palace-gradient-normal" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" :style="{ stopColor: '#f8fafc', stopOpacity: 0.9 }" />
              <stop offset="100%" :style="{ stopColor: '#e2e8f0', stopOpacity: 0.95 }" />
            </linearGradient>
            <linearGradient id="palace-gradient-ming" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" :style="{ stopColor: '#dbeafe', stopOpacity: 1 }" />
              <stop offset="100%" :style="{ stopColor: '#bfdbfe', stopOpacity: 1 }" />
            </linearGradient>
            <linearGradient id="palace-gradient-shen" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" :style="{ stopColor: '#e9d5ff', stopOpacity: 1 }" />
              <stop offset="100%" :style="{ stopColor: '#ddd6fe', stopOpacity: 1 }" />
            </linearGradient>
            
            <!-- 3D阴影滤镜 -->
            <filter id="palace-shadow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
              <feOffset dx="2" dy="2" result="offsetblur"/>
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
              </feComponentTransfer>
              <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <!-- 高光滤镜 -->
            <filter id="palace-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <!-- 外圈十二宫位 -->
          <g v-for="(palace, index) in palaceData" :key="index" class="palace-group">
            <!-- 宫位多边形 - 3D效果 -->
            <polygon
              :points="getPalacePolygon(index)"
              :class="['palace-polygon', { 
                'ming-gong': palace.is_ming_gong, 
                'shen-gong': palace.is_shen_gong,
                'palace-hover': hoveredPalace === index
              }]"
              :fill="getPalaceGradientId(palace)"
              :stroke="getPalaceStrokeColor(palace)"
              :stroke-width="getPalaceStrokeWidth(palace)"
              :filter="palace.is_ming_gong || palace.is_shen_gong ? 'url(#palace-shadow)' : ''"
              @mouseenter="hoveredPalace = index"
              @mouseleave="hoveredPalace = -1"
              style="cursor: pointer; transition: all 0.3s ease;"
            />
        
            <!-- 宫位名称 - 立体效果 -->
            <text
              :x="getPalaceTextX(index)"
              :y="getPalaceTextY(index)"
              class="palace-name"
              :class="{ 'name-highlight': palace.is_ming_gong || palace.is_shen_gong }"
              text-anchor="middle"
              :filter="palace.is_ming_gong || palace.is_shen_gong ? 'url(#palace-glow)' : ''"
            >
              {{ palace.name }}
            </text>
            
            <!-- 主星 - 带背景圆 -->
            <g v-for="(star, starIndex) in palace.main_stars" :key="`main-${starIndex}`">
              <circle
                :cx="getStarX(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length)"
                :cy="getStarY(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length) - 2"
                r="12"
                class="star-background main-star-bg"
              />
              <text
                :x="getStarX(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length)"
                :y="getStarY(index, starIndex, palace.main_stars.length, 'main', palace.auxiliary_stars.length)"
                class="main-star"
                text-anchor="middle"
                dominant-baseline="middle"
              >
                {{ star }}
              </text>
            </g>
            
            <!-- 辅星 - 带背景 -->
            <g v-for="(star, starIndex) in palace.auxiliary_stars" :key="`aux-${starIndex}`">
              <circle
                :cx="getStarX(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length)"
                :cy="getStarY(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length) - 2"
                r="10"
                class="star-background aux-star-bg"
              />
              <text
                :x="getStarX(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length)"
                :y="getStarY(index, starIndex, palace.auxiliary_stars.length, 'aux', palace.main_stars.length)"
                class="auxiliary-star"
                text-anchor="middle"
                dominant-baseline="middle"
              >
                {{ star }}
              </text>
            </g>
            
            <!-- 四化标记 - 特殊样式 -->
            <g v-if="palace.si_hua">
              <rect
                :x="getSiHuaX(index, palace.main_stars.length, palace.auxiliary_stars.length) - 15"
                :y="getSiHuaY(index, palace.main_stars.length, palace.auxiliary_stars.length) - 10"
                width="30"
                height="20"
                rx="4"
                class="si-hua-bg"
              />
              <text
                :x="getSiHuaX(index, palace.main_stars.length, palace.auxiliary_stars.length)"
                :y="getSiHuaY(index, palace.main_stars.length, palace.auxiliary_stars.length)"
                class="si-hua-mark"
                text-anchor="middle"
                dominant-baseline="middle"
              >
                {{ palace.si_hua }}
              </text>
            </g>
          </g>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { ZoomIn, ZoomOut, Refresh } from '@element-plus/icons-vue';

const props = defineProps<{
  panData: any;
  size?: number;
}>();

const baseSize = computed(() => props.size || 900);
const center = computed(() => baseSize.value / 2);
const radius = computed(() => baseSize.value * 0.35);

// 缩放和平移状态
const scale = ref(1);
const translateX = ref(0);
const translateY = ref(0);
const containerRef = ref<HTMLDivElement | null>(null);
const hoveredPalace = ref(-1);

// 拖拽状态
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const lastTranslate = ref({ x: 0, y: 0 });

// 缩放限制
const MIN_SCALE = 0.5;
const MAX_SCALE = 3;
const SCALE_STEP = 0.1;

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

// 获取宫位渐变ID
const getPalaceGradientId = (palace: any): string => {
  if (palace.is_ming_gong) return 'url(#palace-gradient-ming)';
  if (palace.is_shen_gong) return 'url(#palace-gradient-shen)';
  return 'url(#palace-gradient-normal)';
};

// 获取宫位边框颜色
const getPalaceStrokeColor = (palace: any): string => {
  if (palace.is_ming_gong) return '#6366f1';
  if (palace.is_shen_gong) return '#8b5cf6';
  if (hoveredPalace.value >= 0) return 'rgba(99, 102, 241, 0.5)';
  return 'rgba(148, 163, 184, 0.3)';
};

// 获取宫位边框宽度
const getPalaceStrokeWidth = (palace: any): number => {
  if (palace.is_ming_gong || palace.is_shen_gong) return 3;
  if (hoveredPalace.value >= 0) return 2;
  return 1.5;
};

// 缩放功能
const zoomIn = () => {
  if (scale.value < MAX_SCALE) {
    scale.value = Math.min(scale.value + SCALE_STEP, MAX_SCALE);
  }
};

const zoomOut = () => {
  if (scale.value > MIN_SCALE) {
    scale.value = Math.max(scale.value - SCALE_STEP, MIN_SCALE);
  }
};

const resetZoom = () => {
  scale.value = 1;
  translateX.value = 0;
  translateY.value = 0;
  lastTranslate.value = { x: 0, y: 0 };
};

// 鼠标滚轮缩放
const handleWheel = (e: WheelEvent) => {
  if (!containerRef.value) return;
  
  const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
  const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale.value + delta));
  
  // 以鼠标位置为中心缩放
  const rect = containerRef.value.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;
  const containerCenterX = rect.width / 2;
  const containerCenterY = rect.height / 2;
  
  // 计算缩放后的偏移
  const scaleChange = newScale / scale.value;
  translateX.value = mouseX - (mouseX - translateX.value) * scaleChange;
  translateY.value = mouseY - (mouseY - translateY.value) * scaleChange;
  
  scale.value = newScale;
  lastTranslate.value = { x: translateX.value, y: translateY.value };
};

// 拖拽平移
const handleMouseDown = (e: MouseEvent) => {
  if (e.button === 0) { // 左键
    isDragging.value = true;
    dragStart.value = { x: e.clientX, y: e.clientY };
    if (containerRef.value) {
      containerRef.value.style.cursor = 'grabbing';
    }
  }
};

const handleMouseMove = (e: MouseEvent) => {
  if (isDragging.value) {
    const deltaX = e.clientX - dragStart.value.x;
    const deltaY = e.clientY - dragStart.value.y;
    translateX.value = lastTranslate.value.x + deltaX;
    translateY.value = lastTranslate.value.y + deltaY;
  }
};

const handleMouseUp = () => {
  if (isDragging.value) {
    isDragging.value = false;
    lastTranslate.value = { x: translateX.value, y: translateY.value };
    if (containerRef.value) {
      containerRef.value.style.cursor = scale.value > 1 ? 'grab' : 'default';
    }
  }
};

// 触摸设备支持
const handleTouchStart = (e: TouchEvent) => {
  if (e.touches.length === 1) {
    isDragging.value = true;
    dragStart.value = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  }
};

const handleTouchMove = (e: TouchEvent) => {
  if (isDragging.value && e.touches.length === 1) {
    const deltaX = e.touches[0].clientX - dragStart.value.x;
    const deltaY = e.touches[0].clientY - dragStart.value.y;
    translateX.value = lastTranslate.value.x + deltaX;
    translateY.value = lastTranslate.value.y + deltaY;
  }
};

const handleTouchEnd = () => {
  if (isDragging.value) {
    isDragging.value = false;
    lastTranslate.value = { x: translateX.value, y: translateY.value };
  }
};

onMounted(() => {
  if (containerRef.value) {
    containerRef.value.addEventListener('touchstart', handleTouchStart);
    containerRef.value.addEventListener('touchmove', handleTouchMove);
    containerRef.value.addEventListener('touchend', handleTouchEnd);
  }
});

onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('touchstart', handleTouchStart);
    containerRef.value.removeEventListener('touchmove', handleTouchMove);
    containerRef.value.removeEventListener('touchend', handleTouchEnd);
  }
});
</script>

<style scoped>
/* 命盘容器包装 */
.ziwei-pan-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600px;
}

/* 缩放控制按钮 */
.zoom-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.zoom-level {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6366f1;
  padding: 4px 8px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 6px;
}

/* 命盘容器 - 可缩放可拖拽 */
.ziwei-pan-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600px;
  overflow: hidden;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 24px;
  cursor: grab;
  touch-action: none;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.ziwei-pan-container:active {
  cursor: grabbing;
}

/* 变换容器 */
.pan-transform {
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease-out;
  will-change: transform;
}

/* SVG 样式 - 3D立体效果 */
.ziwei-pan-svg {
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-radius: 50%;
  filter: drop-shadow(0 20px 60px rgba(0, 0, 0, 0.15));
}

/* 宫位组 */
.palace-group {
  transition: transform 0.3s ease;
}

.palace-group:hover {
  transform: scale(1.02);
}

/* 宫位多边形 - 3D立体效果 */
.palace-polygon {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.95;
}

.palace-polygon.ming-gong {
  opacity: 1;
  stroke-width: 3;
  filter: url(#palace-shadow) url(#palace-glow);
  transform: translateZ(5px);
}

.palace-polygon.shen-gong {
  opacity: 1;
  stroke-width: 3;
  filter: url(#palace-shadow) url(#palace-glow);
  transform: translateZ(5px);
}

.palace-polygon.palace-hover {
  opacity: 1;
  filter: url(#palace-glow);
  transform: scale(1.05);
}

/* 宫位名称 - 立体文字 */
.palace-name {
  font-size: 18px;
  font-weight: 700;
  fill: #1e293b;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

.palace-name.name-highlight {
  fill: #6366f1;
  font-size: 20px;
  font-weight: 800;
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

/* 主星样式 - 带圆形背景 */
.main-star {
  font-size: 16px;
  font-weight: 700;
  fill: #f59e0b;
  pointer-events: none;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.main-star-bg {
  fill: rgba(245, 158, 11, 0.15);
  stroke: rgba(245, 158, 11, 0.3);
  stroke-width: 1.5;
  transition: all 0.3s ease;
}

.palace-group:hover .main-star-bg {
  fill: rgba(245, 158, 11, 0.25);
  stroke: rgba(245, 158, 11, 0.5);
  filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.4));
}

/* 辅星样式 */
.auxiliary-star {
  font-size: 14px;
  font-weight: 600;
  fill: #6366f1;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.aux-star-bg {
  fill: rgba(99, 102, 241, 0.12);
  stroke: rgba(99, 102, 241, 0.25);
  stroke-width: 1;
  transition: all 0.3s ease;
}

.palace-group:hover .aux-star-bg {
  fill: rgba(99, 102, 241, 0.2);
  stroke: rgba(99, 102, 241, 0.4);
  filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.3));
}

/* 四化标记 - 特殊背景 */
.si-hua-bg {
  fill: rgba(239, 68, 68, 0.15);
  stroke: rgba(239, 68, 68, 0.4);
  stroke-width: 1.5;
  transition: all 0.3s ease;
}

.palace-group:hover .si-hua-bg {
  fill: rgba(239, 68, 68, 0.25);
  stroke: rgba(239, 68, 68, 0.6);
  filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.4));
}

.si-hua-mark {
  font-size: 13px;
  font-weight: 700;
  fill: #dc2626;
  pointer-events: none;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .zoom-controls {
    top: 8px;
    right: 8px;
    padding: 6px;
  }
  
  .pan-transform {
    transition: none; /* 移动端禁用过渡，提升性能 */
  }
}
</style>

