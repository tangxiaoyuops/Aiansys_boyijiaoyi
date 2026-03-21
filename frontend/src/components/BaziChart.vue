<template>
  <div class="bazi-chart-container" :class="{ 'compact-mode': compact }">
    <!-- 四柱八字主体 -->
    <div class="sizhu-wrapper">
      <div class="sizhu-grid">
        <!-- 年柱 -->
        <div class="zhu-column" v-if="sizhuList[0]">
          <div class="zhu-label">年柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[0].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[0].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[0].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[0].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[0].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[0].zhiWuxing }}</span>
            </div>
            <!-- 十神 -->
            <div v-if="getShishen(0)" class="shishen-tag">
              {{ getShishen(0) }}
            </div>
          </div>
        </div>

        <!-- 月柱 -->
        <div class="zhu-column" v-if="sizhuList[1]">
          <div class="zhu-label">月柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[1].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[1].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[1].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[1].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[1].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[1].zhiWuxing }}</span>
            </div>
            <div v-if="getShishen(1)" class="shishen-tag">
              {{ getShishen(1) }}
            </div>
          </div>
        </div>

        <!-- 日柱（日主） -->
        <div class="zhu-column rizhu" v-if="sizhuList[2]">
          <div class="zhu-label rizhu-label">日柱（日主）</div>
          <div class="zhu-body">
            <div 
              class="tiangan rizhu-tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[2].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[2].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[2].ganWuxing }}</span>
              <span class="rizhu-badge">日主</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[2].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[2].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[2].zhiWuxing }}</span>
            </div>
            <div v-if="getShishen(2)" class="shishen-tag">
              {{ getShishen(2) }}
            </div>
          </div>
        </div>

        <!-- 时柱 -->
        <div class="zhu-column" v-if="sizhuList[3]">
          <div class="zhu-label">时柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[3].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[3].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[3].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[3].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[3].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[3].zhiWuxing }}</span>
            </div>
            <div v-if="getShishen(3)" class="shishen-tag">
              {{ getShishen(3) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 五行统计 -->
    <div class="wuxing-stats" v-if="wuxingAnalysis">
      <h4 class="stats-title">五行分布</h4>
      <div class="wuxing-bars">
        <div 
          v-for="item in wuxingDataList" 
          :key="item.name" 
          class="wuxing-bar-item"
        >
          <div class="bar-header">
            <span class="bar-name" :style="{ color: getWuxingColor(item.name) }">{{ item.name }}</span>
            <span class="bar-value">{{ item.value }}</span>
          </div>
          <div class="bar-track">
            <div 
              class="bar-fill" 
              :style="{ 
                width: `${(item.value / maxWuxingValue) * 100}%`,
                background: getWuxingGradient(item.name)
              }"
            ></div>
          </div>
        </div>
      </div>
      <div class="rizhu-wuxing" v-if="wuxingAnalysis?.wuxing_data?.rizhu_wuxing">
        <span class="label">日主五行：</span>
        <span 
          class="value" 
          :style="{ color: getWuxingColor(wuxingAnalysis.wuxing_data.rizhu_wuxing) }"
        >
          {{ wuxingAnalysis.wuxing_data.rizhu_wuxing }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  sizhu?: any;
  wuxingAnalysis?: any;
  shishenAnalysis?: any;
  compact?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
});

// 天干五行映射
const tianganWuxing: Record<string, string> = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
};

// 地支五行映射
const dizhiWuxing: Record<string, string> = {
  '子': '水', '丑': '土',
  '寅': '木', '卯': '木',
  '辰': '土', '巳': '火',
  '午': '火', '未': '土',
  '申': '金', '酉': '金',
  '戌': '土', '亥': '水',
};

const sizhuList = computed(() => {
  if (!props.sizhu) return [];
  
  return [
    {
      name: '年柱',
      gan: props.sizhu.nian_zhu?.tian_gan || '',
      zhi: props.sizhu.nian_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.nian_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.nian_zhu?.di_zhi] || '',
    },
    {
      name: '月柱',
      gan: props.sizhu.yue_zhu?.tian_gan || '',
      zhi: props.sizhu.yue_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.yue_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.yue_zhu?.di_zhi] || '',
    },
    {
      name: '日柱',
      gan: props.sizhu.ri_zhu?.tian_gan || '',
      zhi: props.sizhu.ri_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.ri_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.ri_zhu?.di_zhi] || '',
    },
    {
      name: '时柱',
      gan: props.sizhu.shi_zhu?.tian_gan || '',
      zhi: props.sizhu.shi_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.shi_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.shi_zhu?.di_zhi] || '',
    },
  ];
});

const wuxingDataList = computed(() => {
  if (!props.wuxingAnalysis?.wuxing_data) return [];
  
  const data = props.wuxingAnalysis.wuxing_data;
  return [
    { name: '金', value: data.jin || 0 },
    { name: '木', value: data.mu || 0 },
    { name: '水', value: data.shui || 0 },
    { name: '火', value: data.huo || 0 },
    { name: '土', value: data.tu || 0 },
  ];
});

const maxWuxingValue = computed(() => {
  const values = wuxingDataList.value.map(item => item.value);
  return Math.max(...values, 1);
});

// 获取十神信息
const getShishen = (index: number) => {
  if (!props.shishenAnalysis?.shishen_data) return '';
  
  const keys = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu'];
  const key = keys[index];
  const shishen = props.shishenAnalysis.shishen_data[key];
  
  if (shishen && shishen.gan_shishen) {
    return shishen.gan_shishen;
  }
  return '';
};

// 五行颜色
const getWuxingColor = (wuxing: string): string => {
  const colorMap: Record<string, string> = {
    '金': '#D4AF37',
    '木': '#228B22',
    '水': '#1E90FF',
    '火': '#DC143C',
    '土': '#8B4513',
  };
  return colorMap[wuxing] || '#666';
};

// 五行渐变
const getWuxingGradient = (wuxing: string): string => {
  const gradientMap: Record<string, string> = {
    '金': 'linear-gradient(135deg, #FFE55C 0%, #D4AF37 50%, #B8860B 100%)',
    '木': 'linear-gradient(135deg, #90EE90 0%, #228B22 50%, #006400 100%)',
    '水': 'linear-gradient(135deg, #87CEEB 0%, #1E90FF 50%, #0066CC 100%)',
    '火': 'linear-gradient(135deg, #FF6B6B 0%, #DC143C 50%, #8B0000 100%)',
    '土': 'linear-gradient(135deg, #DEB887 0%, #8B4513 50%, #654321 100%)',
  };
  return gradientMap[wuxing] || 'linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%)';
};
</script>

<style scoped>
.bazi-chart-container {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(251, 250, 248, 0.95) 0%, rgba(248, 246, 242, 0.95) 100%);
  border-radius: 16px;
  border: 1px solid rgba(139, 90, 43, 0.15);
  box-shadow: 
    0 4px 20px rgba(139, 90, 43, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* 四柱网格布局 */
.sizhu-wrapper {
  margin-bottom: 24px;
}

.sizhu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.zhu-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.zhu-label {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  padding: 6px 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(245, 242, 235, 0.9) 100%);
  border-radius: 20px;
  border: 1px solid rgba(139, 90, 43, 0.2);
  box-shadow: 0 2px 8px rgba(139, 90, 43, 0.1);
}

.zhu-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 12px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(252, 250, 245, 0.95) 100%);
  border-radius: 12px;
  border: 2px solid rgba(139, 90, 43, 0.15);
  box-shadow: 
    0 4px 16px rgba(139, 90, 43, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 1);
  min-width: 90px;
}

/* 天干样式 */
.tiangan {
  width: 64px;
  height: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 2px 0 rgba(255, 255, 255, 0.3),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.tiangan:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 8px 20px rgba(0, 0, 0, 0.2),
    inset 0 2px 0 rgba(255, 255, 255, 0.3),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
}

.gan-char {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(255, 255, 255, 0.5);
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
  letter-spacing: 2px;
}

.wuxing-badge {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(0, 0, 0, 0.25);
  padding: 1px 6px;
  border-radius: 8px;
  margin-top: 2px;
  font-weight: 500;
}

/* 地支样式 */
.dizhi {
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: 
    0 3px 10px rgba(0, 0, 0, 0.12),
    inset 0 2px 0 rgba(255, 255, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.dizhi:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 6px 16px rgba(0, 0, 0, 0.18),
    inset 0 2px 0 rgba(255, 255, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.08);
}

.zhi-char {
  font-size: 30px;
  font-weight: 600;
  color: #fff;
  text-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.25),
    0 0 15px rgba(255, 255, 255, 0.4);
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
  letter-spacing: 1px;
}

/* 日主特殊样式 */
.rizhu .zhu-label {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.25) 100%);
  border-color: rgba(212, 175, 55, 0.4);
  color: #8B6914;
}

.rizhu .zhu-body {
  border-color: rgba(212, 175, 55, 0.4);
  box-shadow: 
    0 4px 20px rgba(212, 175, 55, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 1);
}

.rizhu-tiangan {
  position: relative;
}

.rizhu-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 9px;
  color: #fff;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(255, 165, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 十神标签 */
.shishen-tag {
  margin-top: 8px;
  padding: 4px 12px;
  font-size: 12px;
  color: #5D4E37;
  background: linear-gradient(135deg, rgba(139, 90, 43, 0.1) 0%, rgba(139, 90, 43, 0.05) 100%);
  border: 1px solid rgba(139, 90, 43, 0.2);
  border-radius: 12px;
  font-weight: 500;
}

/* 五行统计 */
.wuxing-stats {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.stats-title {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #D4AF37;
}

.wuxing-bars {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.wuxing-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bar-name {
  font-size: 14px;
  font-weight: 600;
}

.bar-value {
  font-size: 16px;
  font-weight: 700;
  color: #3D3D3D;
}

.bar-track {
  height: 8px;
  background: rgba(139, 90, 43, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.rizhu-wuxing {
  margin-top: 16px;
  text-align: center;
  padding: 10px;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 8px;
}

.rizhu-wuxing .label {
  font-size: 13px;
  color: #666;
  margin-right: 8px;
}

.rizhu-wuxing .value {
  font-size: 18px;
  font-weight: 700;
}

/* 响应式 */
@media (max-width: 600px) {
  .sizhu-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .wuxing-bars {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .wuxing-bar-item:nth-child(4),
  .wuxing-bar-item:nth-child(5) {
    grid-column: span 1;
  }
}

.compact-mode {
  padding: 12px;
}

.compact-mode .sizhu-wrapper {
  padding: 0;
}

.compact-mode .sizhu-grid {
  gap: 8px;
}

.compact-mode .zhu-column {
  padding: 6px;
}

.compact-mode .zhu-label {
  font-size: 11px;
  padding: 3px 8px;
  margin-bottom: 6px;
}

.compact-mode .zhu-body {
  padding: 6px;
  gap: 6px;
}

.compact-mode .tiangan,
.compact-mode .dizhi {
  width: 40px;
  height: 40px;
}

.compact-mode .gan-char {
  font-size: 24px;
}

.compact-mode .zhi-char {
  font-size: 20px;
}

.compact-mode .wuxing-badge {
  font-size: 8px;
  padding: 1px 4px;
}

.compact-mode .shishen-tag {
  font-size: 10px;
  padding: 2px 8px;
  margin-top: 4px;
}

.compact-mode .wuxing-section {
  display: none;
}
</style>