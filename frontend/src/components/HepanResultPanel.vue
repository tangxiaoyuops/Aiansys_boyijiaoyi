<template>
  <div class="hepan-result-panel">
    <!-- 匹配度分数 -->
    <div class="score-section">
      <div class="score-circle" :class="scoreClass">
        <div class="score-value">{{ hepanData?.scores?.total || 0 }}</div>
        <div class="score-label">匹配度</div>
      </div>
      <div class="score-grade">
        <span class="grade" :class="scoreClass">{{ hepanData?.scores?.grade || '计算中' }}</span>
        <span class="grade-desc">{{ hepanData?.scores?.grade_desc || '' }}</span>
      </div>
    </div>

    <!-- 分项评分 -->
    <div class="scores-detail">
      <div class="score-item">
        <span class="label">地支匹配</span>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: ((hepanData?.scores?.di_zhi || 0) / 25 * 100) + '%' }"></div>
        </div>
        <span class="value">{{ hepanData?.scores?.di_zhi || 0 }}/25</span>
      </div>
      <div class="score-item">
        <span class="label">五行互补</span>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: ((hepanData?.scores?.wuxing || 0) / 25 * 100) + '%' }"></div>
        </div>
        <span class="value">{{ hepanData?.scores?.wuxing || 0 }}/25</span>
      </div>
      <div class="score-item">
        <span class="label">日主关系</span>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: ((hepanData?.scores?.rizhu || 0) / 20 * 100) + '%' }"></div>
        </div>
        <span class="value">{{ hepanData?.scores?.rizhu || 0 }}/20</span>
      </div>
      <div class="score-item">
        <span class="label">天干合化</span>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: ((hepanData?.scores?.tian_gan || 0) / 15 * 100) + '%' }"></div>
        </div>
        <span class="value">{{ hepanData?.scores?.tian_gan || 0 }}/15</span>
      </div>
      <div class="score-item">
        <span class="label">十神配合</span>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: ((hepanData?.scores?.shishen || 0) / 15 * 100) + '%' }"></div>
        </div>
        <span class="value">{{ hepanData?.scores?.shishen || 0 }}/15</span>
      </div>
    </div>

    <!-- 关系分析 -->
    <div class="relations-section">
      <!-- 地支六合 -->
      <div v-if="hepanData?.di_zhi_relation?.liu_he?.length" class="relation-card he">
        <div class="relation-header">
          <el-icon><Connection /></el-icon>
          <span>地支六合</span>
          <el-tag size="small" type="success">吉</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(he, i) in hepanData.di_zhi_relation.liu_he" :key="i" class="relation-tag he-tag">
            {{ he.desc }}
          </span>
        </div>
      </div>

      <!-- 地支六冲 -->
      <div v-if="hepanData?.di_zhi_relation?.liu_chong?.length" class="relation-card chong">
        <div class="relation-header">
          <el-icon><Warning /></el-icon>
          <span>地支六冲</span>
          <el-tag size="small" type="warning">注意</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(chong, i) in hepanData.di_zhi_relation.liu_chong" :key="i" class="relation-tag chong-tag">
            {{ chong.desc }}
          </span>
        </div>
      </div>

      <!-- 地支三合 -->
      <div v-if="hepanData?.di_zhi_relation?.san_he?.length" class="relation-card san-he">
        <div class="relation-header">
          <el-icon><Star /></el-icon>
          <span>地支三合</span>
          <el-tag size="small" type="success">大吉</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(sanHe, i) in hepanData.di_zhi_relation.san_he" :key="i" class="relation-tag san-he-tag">
            {{ sanHe.desc }}
          </span>
        </div>
      </div>

      <!-- 天干五合 -->
      <div v-if="hepanData?.tian_gan_relation?.wu_he?.length" class="relation-card he">
        <div class="relation-header">
          <el-icon><Link /></el-icon>
          <span>天干五合</span>
          <el-tag size="small" type="success">吉</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(he, i) in hepanData.tian_gan_relation.wu_he" :key="i" class="relation-tag he-tag">
            {{ he.desc }}
          </span>
        </div>
      </div>

      <!-- 日主关系 -->
      <div v-if="hepanData?.rizhu_relation?.relations?.length" class="relation-card">
        <div class="relation-header">
          <el-icon><User /></el-icon>
          <span>日主关系</span>
        </div>
        <div class="relation-content">
          <span v-for="(rel, i) in hepanData.rizhu_relation.relations" :key="i" 
                class="relation-tag" :class="rel.type === 'sheng' ? 'sheng-tag' : rel.type === 'ke' ? 'ke-tag' : ''">
            {{ rel.desc }}
          </span>
        </div>
      </div>

      <!-- 五行互补 -->
      <div v-if="hepanData?.wuxing_match?.complement?.length" class="relation-card complement">
        <div class="relation-header">
          <el-icon><Star /></el-icon>
          <span>五行互补</span>
          <el-tag size="small" type="success">互补</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(c, i) in hepanData.wuxing_match.complement" :key="i" class="relation-tag complement-tag">
            {{ c.desc }}
          </span>
        </div>
      </div>

      <!-- 五行冲突 -->
      <div v-if="hepanData?.wuxing_match?.conflict?.length" class="relation-card conflict">
        <div class="relation-header">
          <el-icon><Warning /></el-icon>
          <span>五行冲突</span>
          <el-tag size="small" type="warning">需调节</el-tag>
        </div>
        <div class="relation-content">
          <span v-for="(c, i) in hepanData.wuxing_match.conflict" :key="i" class="relation-tag conflict-tag">
            {{ c.desc }}
          </span>
        </div>
      </div>
    </div>

    <!-- 建议 -->
    <div v-if="hepanData?.suggestions?.length" class="suggestions-section">
      <div class="section-title">
        <el-icon><ChatLineSquare /></el-icon>
        <span>建议</span>
      </div>
      <ul class="suggestions-list">
        <li v-for="(sug, i) in hepanData.suggestions" :key="i">{{ sug }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Connection, Warning, Link, User, Star, ChatLineSquare } from '@element-plus/icons-vue';

const props = defineProps<{
  hepanData: Record<string, any> | null;
}>();

const scoreClass = computed(() => {
  const total = props.hepanData?.scores?.total || 0;
  if (total >= 80) return 'excellent';
  if (total >= 65) return 'good';
  if (total >= 50) return 'medium';
  return 'low';
});
</script>

<style scoped>
.hepan-result-panel {
  padding: 16px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
  border: 3px solid;
}

.score-circle.excellent {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}
.score-circle.good {
  border-color: #409eff;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}
.score-circle.medium {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%);
}
.score-circle.low {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-grade {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.grade {
  font-size: 18px;
  font-weight: 600;
}
.grade.excellent { color: #67c23a; }
.grade.good { color: #409eff; }
.grade.medium { color: #e6a23c; }
.grade.low { color: #f56c6c; }

.grade-desc {
  font-size: 13px;
  color: #909399;
}

.scores-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-item .label {
  width: 80px;
  font-size: 13px;
  color: #606266;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #d4af37 0%, #f5d76e 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-item .value {
  width: 40px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.relations-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.relation-card {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  border-left: 3px solid #d4af37;
}

.relation-card.he { border-left-color: #67c23a; }
.relation-card.chong { border-left-color: #e6a23c; }
.relation-card.san-he { border-left-color: #9b59b6; }
.relation-card.complement { border-left-color: #409eff; }
.relation-card.conflict { border-left-color: #f56c6c; }

.relation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #303133;
}

.relation-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.relation-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: #f5f7fa;
  color: #606266;
}

.he-tag { background: #f0f9eb; color: #67c23a; }
.chong-tag { background: #fdf6ec; color: #e6a23c; }
.san-he-tag { background: #f4ecf7; color: #9b59b6; }
.sheng-tag { background: #f0f9eb; color: #67c23a; }
.ke-tag { background: #fef0f0; color: #f56c6c; }
.complement-tag { background: #ecf5ff; color: #409eff; }
.conflict-tag { background: #fef0f0; color: #f56c6c; }

.suggestions-section {
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 500;
  color: #303133;
}

.suggestions-list {
  margin: 0;
  padding-left: 20px;
}

.suggestions-list li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}
</style>