<template>
  <div class="huangdi-theory-card">
    <div class="card-header">
      <div class="book-badge" :class="bookClass">
        {{ theory.book }}
      </div>
      <h4 class="theory-title">{{ theory.chapter_title }}</h4>
      <el-tag v-if="theory.relevance_score !== undefined" size="small" :type="scoreTagType" class="score-tag">
        {{ formatScore(theory.relevance_score) }}
      </el-tag>
    </div>
    
    <div class="card-content">
      <p class="theory-content" :class="{ expanded: isExpanded }">
        {{ theory.content }}
      </p>
      <div v-if="needsExpand" class="expand-controls">
        <el-button
          text
          type="primary"
          size="small"
          @click="toggleExpand"
        >
          {{ isExpanded ? '收起' : '展开全文' }}
          <el-icon>
            <ArrowDown v-if="!isExpanded" />
            <ArrowUp v-else />
          </el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue';

interface Theory {
  book: string;
  chapter_title: string;
  content: string;
  relevance_score?: number;
}

interface Props {
  theory: Theory;
}

const props = defineProps<Props>();

const isExpanded = ref(false);

const bookClass = computed(() => {
  return props.theory.book === '素问' ? 'suwen' : 'lingshu';
});

// 判断是否需要展开功能（内容超过3行）
const needsExpand = computed(() => {
  return props.theory.content && props.theory.content.length > 150;
});

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

// 格式化相关性分数
const formatScore = (score: number | undefined): string => {
  if (score === undefined) return '';
  // 如果是负数，可能是距离分数，转换为相似度
  const normalizedScore = score < 0 ? Math.abs(score) : score;
  return `${(normalizedScore * 100).toFixed(0)}%`;
};

// 根据分数确定标签类型
const scoreTagType = computed(() => {
  if (props.theory.relevance_score === undefined) return 'info';
  const score = Math.abs(props.theory.relevance_score);
  if (score >= 0.7) return 'success';
  if (score >= 0.5) return 'warning';
  return 'info';
});
</script>

<script lang="ts">
export default {
  name: 'HuangdiTheoryCard',
};
</script>

<style scoped>
.huangdi-theory-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.huangdi-theory-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #1b4332;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.book-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.book-badge.suwen {
  background: linear-gradient(135deg, #1b4332 0%, #2d5016 100%);
}

.book-badge.lingshu {
  background: linear-gradient(135deg, #d4af37 0%, #f4a460 100%);
  color: #1b4332;
}

.theory-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  flex: 1;
  min-width: 0;
}

.score-tag {
  flex-shrink: 0;
}

.card-content {
  color: #4b5563;
  line-height: 1.7;
  font-size: 14px;
}

.theory-content {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  white-space: pre-wrap;
  transition: all 0.3s ease;
}

.theory-content.expanded {
  display: block;
  -webkit-line-clamp: unset;
  line-clamp: unset;
  overflow: visible;
}

.expand-controls {
  margin-top: 8px;
  text-align: right;
}

.expand-controls .el-button {
  padding: 4px 8px;
  font-size: 12px;
}
</style>

