<template>
  <div class="liuyue-panel">
    <div class="panel-header">
      <h3 class="panel-title">
        <el-icon><Calendar /></el-icon>
        流月推演（未来{{ monthsCount }}个月）
      </h3>
      <div class="summary-bar">
        <span class="summary-item ji">
          <span class="dot"></span>吉月: {{ summary.ji_count }}
        </span>
        <span class="summary-item ping">
          <span class="dot"></span>平月: {{ summary.ping_count }}
        </span>
        <span class="summary-item xiong">
          <span class="dot"></span>凶月: {{ summary.xiong_count }}
        </span>
      </div>
    </div>

    <!-- 计算说明 -->
    <div class="calculation-note" v-if="calculationNote">
      <el-icon><InfoFilled /></el-icon>
      <span>{{ calculationNote }}</span>
    </div>

    <div class="liuyue-grid">
      <div
        v-for="item in liuyueList"
        :key="`${item.year}-${item.month}`"
        class="liuyue-card"
        :class="getCardClass(item)"
      >
        <div class="card-header">
          <span class="month-label">{{ item.year }}年{{ item.month }}月</span>
          <span class="level-badge" :class="getLevelClass(item)">
            {{ getAuspiciousLevel(item) }}
          </span>
        </div>
        <div class="card-body">
          <div class="ganzhi">{{ item.gan_zhi }}</div>
          <div class="wuxing">
            <span class="wuxing-tag" :class="getWuxingClass(item.wuxing?.gan)">
              {{ item.wuxing?.gan }}
            </span>
            <span class="wuxing-tag" :class="getWuxingClass(item.wuxing?.zhi)">
              {{ item.wuxing?.zhi }}
            </span>
          </div>
          <div class="shishen">
            <span class="shishen-label">天干:</span>
            <span class="shishen-value">{{ item.shishen_to_rizhu?.gan_shishen || '-' }}</span>
            <span class="shishen-label">地支:</span>
            <span class="shishen-value">{{ item.shishen_to_rizhu?.zhi_shishen || '-' }}</span>
          </div>
        </div>
        <div class="card-footer" v-if="item.auspicious?.suggestions?.length">
          <el-tooltip
            :content="item.auspicious.suggestions.join('; ')"
            placement="top"
          >
            <el-icon class="info-icon"><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>

    <div class="wuxing-xiji" v-if="wuxingXiJi">
      <h4>五行喜忌参考</h4>
      <div class="xiji-content">
        <div class="xiji-item">
          <span class="label">喜用五行:</span>
          <span class="wuxing-list">
            <span
              v-for="wx in wuxingXiJi.xi_wuxing"
              :key="wx"
              class="wuxing-badge xi"
              :class="getWuxingClass(wx)"
            >{{ wx }}</span>
          </span>
        </div>
        <div class="xiji-item">
          <span class="label">忌讳五行:</span>
          <span class="wuxing-list">
            <span
              v-for="wx in wuxingXiJi.ji_wuxing"
              :key="wx"
              class="wuxing-badge ji"
              :class="getWuxingClass(wx)"
            >{{ wx }}</span>
          </span>
        </div>
      </div>
    </div>

    <div class="llm-analysis" v-if="llmAnalysis">
      <h4>AI 综合解读</h4>
      <div class="analysis-content" v-html="formatMarkdown(llmAnalysis)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Calendar, InfoFilled } from '@element-plus/icons-vue';

interface LiuyueItem {
  year: number;
  month: number;
  gan_zhi: string;
  gan: string;
  zhi: string;
  wuxing?: {
    gan: string;
    zhi: string;
  };
  shishen_to_rizhu?: {
    gan_shishen: string;
    zhi_shishen: string;
  };
  auspicious?: {
    level: string;
    score: number;
    suggestions: string[];
  };
}

interface Props {
  liuyueList: LiuyueItem[];
  monthsCount?: number;
  wuxingXiJi?: {
    xi_wuxing: string[];
    ji_wuxing: string[];
    is_rizhu_qiang: boolean;
  } | null;
  llmAnalysis?: string;
  calculationDay?: number;         // 农历计算日期
  includeCurrentMonth?: boolean;  // 是否包含当月
  solarDate?: string;             // 公历日期
  lunarDate?: string;             // 农历日期
}

const props = withDefaults(defineProps<Props>(), {
  liuyueList: () => [],
  monthsCount: 6,
  wuxingXiJi: null,
  llmAnalysis: '',
  calculationDay: 0,
  includeCurrentMonth: false,
  solarDate: '',
  lunarDate: '',
});

const calculationNote = computed(() => {
  if (props.calculationDay === 0) return '';
  const dateInfo = props.solarDate && props.lunarDate 
    ? `公历${props.solarDate}，农历${props.lunarDate}。` 
    : '';
  if (props.includeCurrentMonth) {
    return `${dateInfo}农历${props.calculationDay}日（15日及之前），已包含当月运势`;
  } else {
    return `${dateInfo}农历${props.calculationDay}日（16日及之后），从下月开始推演`;
  }
});

const summary = computed(() => {
  let ji_count = 0;
  let xiong_count = 0;
  let ping_count = 0;

  props.liuyueList.forEach(item => {
    const level = item.auspicious?.level || '平';
    if (['大吉', '中吉'].includes(level)) {
      ji_count++;
    } else if (['大凶', '中凶'].includes(level)) {
      xiong_count++;
    } else {
      ping_count++;
    }
  });

  return { ji_count, xiong_count, ping_count };
});

const getCardClass = (item: LiuyueItem) => {
  const level = item.auspicious?.level || '平';
  if (['大吉', '中吉'].includes(level)) return 'card-ji';
  if (['大凶', '中凶'].includes(level)) return 'card-xiong';
  return 'card-ping';
};

const getLevelClass = (item: LiuyueItem) => {
  const level = item.auspicious?.level || '平';
  if (['大吉', '中吉'].includes(level)) return 'level-ji';
  if (['大凶', '中凶'].includes(level)) return 'level-xiong';
  return 'level-ping';
};

const getAuspiciousLevel = (item: LiuyueItem) => {
  return item.auspicious?.level || '平';
};

const getWuxingClass = (wuxing: string | undefined) => {
  if (!wuxing) return '';
  const classMap: Record<string, string> = {
    '金': 'wuxing-jin',
    '木': 'wuxing-mu',
    '水': 'wuxing-shui',
    '火': 'wuxing-huo',
    '土': 'wuxing-tu',
  };
  return classMap[wuxing] || '';
};

const formatMarkdown = (text: string) => {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h5>$1</h5>')
    .replace(/^#### (.*$)/gim, '<h6>$1</h6>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
};
</script>

<style scoped>
.liuyue-panel {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.calculation-note {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #fdf6ec;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #e6a23c;
  border: 1px solid #faecd8;
}

.calculation-note .el-icon {
  font-size: 16px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.summary-bar {
  display: flex;
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.summary-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.summary-item.ji .dot { background: #67c23a; }
.summary-item.ping .dot { background: #909399; }
.summary-item.xiong .dot { background: #f56c6c; }

.liuyue-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.liuyue-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.liuyue-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.liuyue-card.card-ji {
  background: linear-gradient(135deg, #f0f9eb 0%, #fff 100%);
  border-color: #c2e7b0;
}

.liuyue-card.card-xiong {
  background: linear-gradient(135deg, #fef0f0 0%, #fff 100%);
  border-color: #fbc4c4;
}

.liuyue-card.card-ping {
  background: linear-gradient(135deg, #f4f4f5 0%, #fff 100%);
  border-color: #d3d4d6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.month-label {
  font-size: 12px;
  color: #909399;
}

.level-badge {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.level-badge.level-ji {
  background: #67c23a;
  color: #fff;
}

.level-badge.level-xiong {
  background: #f56c6c;
  color: #fff;
}

.level-badge.level-ping {
  background: #909399;
  color: #fff;
}

.card-body {
  text-align: center;
}

.ganzhi {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 6px;
}

.wuxing {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 8px;
}

.wuxing-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
}

.wuxing-jin { background: #e6a23c; }
.wuxing-mu { background: #67c23a; }
.wuxing-shui { background: #409eff; }
.wuxing-huo { background: #f56c6c; }
.wuxing-tu { background: #909399; }

.shishen {
  font-size: 11px;
  color: #909399;
  line-height: 1.6;
}

.shishen-label {
  margin-right: 4px;
}

.shishen-value {
  color: #606266;
  margin-right: 8px;
}

.card-footer {
  text-align: center;
  padding-top: 8px;
  border-top: 1px dashed #ebeef5;
  margin-top: 8px;
}

.info-icon {
  color: #909399;
  cursor: pointer;
}

.info-icon:hover {
  color: #409eff;
}

.wuxing-xiji {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.wuxing-xiji h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.xiji-content {
  display: flex;
  gap: 24px;
}

.xiji-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.xiji-item .label {
  font-size: 13px;
  color: #606266;
}

.wuxing-list {
  display: flex;
  gap: 6px;
}

.wuxing-badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
  color: #fff;
}

.wuxing-badge.xi { opacity: 1; }
.wuxing-badge.ji { opacity: 0.7; }

.llm-analysis {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.llm-analysis h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.analysis-content {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
}

.analysis-content :deep(h5) {
  margin: 16px 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.analysis-content :deep(h6) {
  margin: 12px 0 6px 0;
  font-size: 13px;
  color: #606266;
}

.analysis-content :deep(strong) {
  color: #303133;
}
</style>