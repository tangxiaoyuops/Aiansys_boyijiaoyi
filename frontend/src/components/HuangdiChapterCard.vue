<template>
  <div class="huangdi-chapter-card" :class="{ expanded: isExpanded }">
    <div class="card-header" @click="toggleExpand">
      <div class="header-content">
        <div class="book-badge" :class="bookClass">
          {{ chapter.book }}
        </div>
        <h4 class="chapter-title">{{ chapter.chapter_title }}</h4>
      </div>
      <div class="header-meta">
        <el-tag v-if="chapter.relevance_score" size="small" type="success">
          相关性: {{ (chapter.relevance_score * 100).toFixed(0) }}%
        </el-tag>
        <el-icon class="expand-icon" :class="{ rotated: isExpanded }">
          <ArrowDown />
        </el-icon>
      </div>
    </div>
    
    <div v-if="chapter.themes && chapter.themes.length > 0" class="themes">
      <el-tag
        v-for="theme in chapter.themes"
        :key="theme"
        size="small"
        class="theme-tag"
      >
        {{ theme }}
      </el-tag>
    </div>
    
    <transition name="slide-fade">
      <div v-show="isExpanded" class="card-content">
        <div class="content-text" v-html="formatContent(chapter.content)"></div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ArrowDown } from '@element-plus/icons-vue';

interface Chapter {
  book: string;
  chapter_title: string;
  content: string;
  relevance_score?: number;
  themes?: string[];
}

interface Props {
  chapter: Chapter;
  defaultExpanded?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  defaultExpanded: false,
});

const isExpanded = ref(props.defaultExpanded);

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

const bookClass = computed(() => {
  return props.chapter.book === '素问' ? 'suwen' : 'lingshu';
});

const formatContent = (content: string) => {
  // 简单的文本格式化，可以高亮关键词等
  return content
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .join('<br/>');
};
</script>

<script lang="ts">
export default {
  name: 'HuangdiChapterCard',
};
</script>

<style scoped>
.huangdi-chapter-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  margin-bottom: 16px;
  cursor: pointer;
}

.huangdi-chapter-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #1b4332;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.header-content {
  flex: 1;
  min-width: 0;
}

.book-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  color: white;
}

.book-badge.suwen {
  background: linear-gradient(135deg, #1b4332 0%, #2d5016 100%);
}

.book-badge.lingshu {
  background: linear-gradient(135deg, #d4af37 0%, #f4a460 100%);
  color: #1b4332;
}

.chapter-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  line-height: 1.4;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.expand-icon {
  transition: transform 0.3s ease;
  color: #6b7280;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.themes {
  padding: 0 16px 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.theme-tag {
  background: #f3f4f6;
  color: #4b5563;
  border: none;
}

.card-content {
  padding: 0 16px 16px;
  border-top: 1px solid #e5e7eb;
  margin-top: 12px;
  padding-top: 16px;
}

.content-text {
  color: #374151;
  line-height: 1.8;
  font-size: 15px;
  white-space: pre-wrap;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

