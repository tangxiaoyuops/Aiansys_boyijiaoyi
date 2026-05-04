<template>
  <div class="dayun-panel">
    <h4 class="panel-title">大运分析</h4>
    
    <!-- 起运信息 -->
    <div class="qiyun-info" v-if="dayunList && dayunList.length > 0">
      <span class="qiyun-label">起运年龄：</span>
      <span class="qiyun-value">{{ dayunList[0].start_age }}岁</span>
      <span class="qiyun-direction" v-if="isShun">（顺行）</span>
      <span class="qiyun-direction" v-else>（逆行）</span>
    </div>

    <!-- 大运时间轴 -->
    <div class="dayun-timeline">
      <div 
        v-for="(dayun, index) in dayunList" 
        :key="index"
        class="dayun-item"
        :class="{ 
          'current': isCurrentDayun(dayun),
          'past': isPastDayun(dayun),
          'future': isFutureDayun(dayun)
        }"
      >
        <!-- 年龄范围 -->
        <div class="age-range">
          <span class="age-start">{{ dayun.start_age }}</span>
          <span class="age-separator">-</span>
          <span class="age-end">{{ dayun.end_age }}</span>
          <span class="age-unit">岁</span>
        </div>
        
        <!-- 干支 -->
        <div class="dayun-ganzhi">
          <div 
            class="dayun-gan"
            :style="{ background: getWuxingGradient(getGanWuxing(dayun.gan)) }"
          >
            {{ dayun.gan }}
          </div>
          <div 
            class="dayun-zhi"
            :style="{ background: getWuxingGradient(getZhiWuxing(dayun.zhi)) }"
          >
            {{ dayun.zhi }}
          </div>
        </div>

        <!-- 年份范围 -->
        <div class="year-range">
          {{ dayun.start_year }}-{{ dayun.end_year }}年
        </div>

        <!-- 当前标记 -->
        <div v-if="isCurrentDayun(dayun)" class="current-badge">
          当前大运
        </div>
      </div>
    </div>

    <!-- 大运解读 -->
    <div class="dayun-interpretation" v-if="interpretation">
      <h5 class="interpretation-title">大运解读</h5>
      <div class="interpretation-content" v-html="interpretation"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

interface DayunItem {
  gan: string;
  zhi: string;
  start_age: number;
  end_age: number;
  start_year: number;
  end_year: number;
}

interface Props {
  dayunList?: DayunItem[];
  birthYear?: number;
  currentAge?: number;
  interpretation?: string;
  isShun?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  dayunList: () => [],
  isShun: true,
});

// 天干五行映射
const ganWuxing: Record<string, string> = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
};

// 地支五行映射
const zhiWuxing: Record<string, string> = {
  '子': '水', '丑': '土',
  '寅': '木', '卯': '木',
  '辰': '土', '巳': '火',
  '午': '火', '未': '土',
  '申': '金', '酉': '金',
  '戌': '土', '亥': '水',
};

const currentYear = new Date().getFullYear();
const currentAgeValue = computed(() => {
  if (props.currentAge) return props.currentAge;
  if (props.birthYear) return currentYear - props.birthYear;
  return 0;
});

const getGanWuxing = (gan: string): string => {
  return ganWuxing[gan] || '';
};

const getZhiWuxing = (zhi: string): string => {
  return zhiWuxing[zhi] || '';
};

const isCurrentDayun = (dayun: DayunItem): boolean => {
  return currentAgeValue.value >= dayun.start_age && currentAgeValue.value <= dayun.end_age;
};

const isPastDayun = (dayun: DayunItem): boolean => {
  return currentAgeValue.value > dayun.end_age;
};

const isFutureDayun = (dayun: DayunItem): boolean => {
  return currentAgeValue.value < dayun.start_age;
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
.dayun-panel {
  padding: 20px;
  background: linear-gradient(180deg, rgba(251, 250, 248, 0.95) 0%, rgba(248, 246, 242, 0.95) 100%);
  border-radius: 12px;
  border: 1px solid rgba(139, 90, 43, 0.15);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #5D4E37;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #D4AF37;
}

/* 起运信息 */
.qiyun-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 8px;
  margin-bottom: 20px;
}

.qiyun-label {
  font-size: 14px;
  color: #666;
}

.qiyun-value {
  font-size: 18px;
  font-weight: 700;
  color: #D4AF37;
}

.qiyun-direction {
  font-size: 13px;
  color: #8B7355;
}

/* 大运时间轴 */
.dayun-timeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.dayun-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  border: 2px solid rgba(139, 90, 43, 0.15);
  transition: all 0.3s ease;
  position: relative;
}

.dayun-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(139, 90, 43, 0.15);
}

.dayun-item.current {
  border-color: #D4AF37;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
  box-shadow: 0 4px 16px rgba(212, 175, 55, 0.2);
}

.dayun-item.past {
  opacity: 0.7;
}

.dayun-item.future {
  opacity: 0.85;
}

/* 年龄范围 */
.age-range {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.age-start, .age-end {
  font-size: 16px;
  font-weight: 700;
  color: #5D4E37;
}

.age-separator {
  font-size: 12px;
  color: #8B7355;
}

.age-unit {
  font-size: 12px;
  color: #8B7355;
  margin-left: 2px;
}

/* 干支 */
.dayun-ganzhi {
  display: flex;
  gap: 4px;
}

.dayun-gan, .dayun-zhi {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 年份范围 */
.year-range {
  font-size: 11px;
  color: #8B7355;
}

/* 当前标记 */
.current-badge {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  padding: 2px 10px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(255, 165, 0, 0.4);
  white-space: nowrap;
}

/* 大运解读 */
.dayun-interpretation {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.interpretation-title {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  margin: 0 0 12px 0;
}

.interpretation-content {
  font-size: 14px;
  line-height: 1.8;
  color: #3D3226;
}

/* 响应式 */
@media (max-width: 768px) {
  .dayun-timeline {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .dayun-timeline {
    grid-template-columns: 1fr;
  }

  .dayun-item {
    flex-direction: row;
    justify-content: flex-start;
    gap: 16px;
  }

  .dayun-gan, .dayun-zhi {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
}
</style>
