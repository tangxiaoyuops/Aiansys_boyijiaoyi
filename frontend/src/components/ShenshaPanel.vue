<template>
  <div class="shensha-panel">
    <h4 class="panel-title">神煞分析</h4>
    
    <!-- 神煞分类展示 -->
    <div class="shensha-categories">
      <!-- 吉神 -->
      <div class="shensha-category" v-if="jishen.length > 0">
        <div class="category-header ji">
          <span class="category-icon">✦</span>
          <span class="category-name">吉神</span>
          <span class="category-count">{{ jishen.length }}</span>
        </div>
        <div class="shensha-list">
          <div 
            v-for="(ss, index) in jishen" 
            :key="'ji-' + index"
            class="shensha-item ji"
          >
            <span class="shensha-name">{{ ss.name }}</span>
            <span class="shensha-position" v-if="ss.position && ss.position !== '全局'">
              {{ getZhuLabel(ss.position) }}
            </span>
            <span class="shensha-zhi" v-if="ss.zhi">{{ ss.zhi }}</span>
          </div>
        </div>
      </div>

      <!-- 凶煞 -->
      <div class="shensha-category" v-if="xiongsha.length > 0">
        <div class="category-header xiong">
          <span class="category-icon">✗</span>
          <span class="category-name">凶煞</span>
          <span class="category-count">{{ xiongsha.length }}</span>
        </div>
        <div class="shensha-list">
          <div 
            v-for="(ss, index) in xiongsha" 
            :key="'xiong-' + index"
            class="shensha-item xiong"
          >
            <span class="shensha-name">{{ ss.name }}</span>
            <span class="shensha-position" v-if="ss.position && ss.position !== '全局'">
              {{ getZhuLabel(ss.position) }}
            </span>
            <span class="shensha-zhi" v-if="ss.zhi">{{ ss.zhi }}</span>
          </div>
        </div>
      </div>

      <!-- 中性神煞 -->
      <div class="shensha-category" v-if="zhongxing.length > 0">
        <div class="category-header zhong">
          <span class="category-icon">○</span>
          <span class="category-name">中性</span>
          <span class="category-count">{{ zhongxing.length }}</span>
        </div>
        <div class="shensha-list">
          <div 
            v-for="(ss, index) in zhongxing" 
            :key="'zhong-' + index"
            class="shensha-item zhong"
          >
            <span class="shensha-name">{{ ss.name }}</span>
            <span class="shensha-position" v-if="ss.position && ss.position !== '全局'">
              {{ getZhuLabel(ss.position) }}
            </span>
            <span class="shensha-zhi" v-if="ss.zhi">{{ ss.zhi }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 神煞详解 -->
    <div class="shensha-details" v-if="shenshaList && shenshaList.length > 0">
      <h5 class="details-title">神煞详解</h5>
      <div class="details-grid">
        <div 
          v-for="(ss, index) in shenshaList" 
          :key="index"
          class="detail-item"
          :class="'type-' + ss.type"
        >
          <div class="detail-header">
            <span class="detail-name">{{ ss.name }}</span>
            <span class="detail-type" :class="ss.type">{{ ss.type }}</span>
          </div>
          <div class="detail-info">
            <span v-if="ss.position && ss.position !== '全局'">
              位置：{{ getZhuLabel(ss.position) }}
            </span>
            <span v-if="ss.zhi">地支：{{ ss.zhi }}</span>
            <span v-if="ss.gan">天干：{{ ss.gan }}</span>
          </div>
          <div class="detail-desc" v-if="getShenshaDesc(ss.name)">
            {{ getShenshaDesc(ss.name) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface ShenshaItem {
  name: string;
  position?: string;
  zhi?: string;
  gan?: string;
  type: string; // '吉', '凶', '中性'
}

interface Props {
  shenshaList?: ShenshaItem[];
}

const props = withDefaults(defineProps<Props>(), {
  shenshaList: () => [],
});

// 柱位映射
const zhuLabels: Record<string, string> = {
  'nian_zhu': '年柱',
  'yue_zhu': '月柱',
  'ri_zhu': '日柱',
  'shi_zhu': '时柱',
};

// 神煞解释
const shenshaDescriptions: Record<string, string> = {
  '天乙贵人': '最吉之神，主解厄扶危，遇事有人相助，一生多贵人扶持。',
  '桃花': '主异性缘、魅力、人缘，也主风流韵事，需看整体配置。',
  '驿马': '主奔波、出行、变动，适合外出发展，不宜静守。',
  '华盖': '主孤独、清高、艺术才华，喜静不喜动，有宗教缘。',
  '文昌': '主聪明好学、文采出众，利于学业考试，适合文职。',
  '学堂': '主学习能力强，利于进修求学，知识渊博。',
  '天医': '主健康、医药缘分，宜从事医疗行业，身体多康健。',
  '天德': '吉星，主逢凶化吉，遇难呈祥，一生少灾厄。',
  '月德': '吉星，主化解灾厄，与天德同见更佳，性格仁慈。',
  '太极贵人': '主贵人运，但需八字配合，多主事业有成。',
  '将星': '主领导才能，有权威，适合管理岗位。',
  '羊刃': '凶星，主刚烈、冲动，需注意血光之灾，宜修身养性。',
  '禄神': '吉星，主福禄、财运，一生衣食无忧。',
  '孤辰': '主孤独，性格孤僻，婚姻不顺，宜晚婚。',
  '寡宿': '主孤独，不利婚姻，女命尤甚，宜修身养性。',
  '红鸾': '主婚姻喜庆，利婚恋，多主婚姻美满。',
  '天喜': '主喜庆之事，与红鸾同见主婚姻美满。',
};

const getZhuLabel = (position: string): string => {
  return zhuLabels[position] || position;
};

const getShenshaDesc = (name: string): string => {
  return shenshaDescriptions[name] || '';
};

// 分类神煞
const jishen = computed(() => {
  return props.shenshaList.filter(ss => ss.type === '吉');
});

const xiongsha = computed(() => {
  return props.shenshaList.filter(ss => ss.type === '凶');
});

const zhongxing = computed(() => {
  return props.shenshaList.filter(ss => ss.type === '中性');
});
</script>

<style scoped>
.shensha-panel {
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

/* 神煞分类 */
.shensha-categories {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shensha-category {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(139, 90, 43, 0.1);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 14px;
}

.category-header.ji {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(103, 194, 58, 0.05) 100%);
  color: #67c23a;
}

.category-header.xiong {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.15) 0%, rgba(245, 108, 108, 0.05) 100%);
  color: #f56c6c;
}

.category-header.zhong {
  background: linear-gradient(135deg, rgba(144, 147, 153, 0.15) 0%, rgba(144, 147, 153, 0.05) 100%);
  color: #909399;
}

.category-icon {
  font-size: 12px;
}

.category-count {
  margin-left: auto;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  font-size: 12px;
}

.shensha-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
}

.shensha-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
}

.shensha-item.ji {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.shensha-item.xiong {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.shensha-item.zhong {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.shensha-name {
  font-weight: 600;
}

.shensha-position, .shensha-zhi {
  font-size: 11px;
  opacity: 0.8;
}

.shensha-position::before {
  content: '(';
}

.shensha-position::after {
  content: ')';
}

/* 神煞详解 */
.shensha-details {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.details-title {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  margin: 0 0 12px 0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(139, 90, 43, 0.1);
}

.detail-item.type-吉 {
  border-left: 3px solid #67c23a;
}

.detail-item.type-凶 {
  border-left: 3px solid #f56c6c;
}

.detail-item.type-中性 {
  border-left: 3px solid #909399;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-name {
  font-size: 15px;
  font-weight: 600;
  color: #3D3226;
}

.detail-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.detail-type.吉 {
  background: rgba(103, 194, 58, 0.15);
  color: #67c23a;
}

.detail-type.凶 {
  background: rgba(245, 108, 108, 0.15);
  color: #f56c6c;
}

.detail-type.中性 {
  background: rgba(144, 147, 153, 0.15);
  color: #909399;
}

.detail-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #8B7355;
}

.detail-info span {
  padding: 2px 6px;
  background: rgba(139, 90, 43, 0.05);
  border-radius: 4px;
}

.detail-desc {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: #666;
}

/* 响应式 */
@media (max-width: 600px) {
  .details-grid {
    grid-template-columns: 1fr;
  }

  .shensha-list {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
