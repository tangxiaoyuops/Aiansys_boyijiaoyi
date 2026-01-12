<template>
  <div class="huangdi-query-panel">
    <div class="input-section">
      <h3 class="section-title">
        <el-icon><Search /></el-icon>
        知识查询
      </h3>
      <el-input
        v-model="question"
        type="textarea"
        :rows="4"
        placeholder="请输入您想查询的问题，例如：什么是阴阳？如何理解五行？"
        class="question-input"
      />
      <div class="action-bar">
        <el-checkbox v-model="includeLLM">包含AI解释</el-checkbox>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleQuery"
          :disabled="!question.trim()"
        >
          <el-icon><Search /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="result-section">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="result" class="result-section">
      <div v-if="result.relevant_chapters && result.relevant_chapters.length > 0" class="chapters-list">
        <h4 class="result-title">
          <el-icon><Document /></el-icon>
          相关章节 ({{ result.total_results }})
        </h4>
        <HuangdiChapterCard
          v-for="(chapter, index) in result.relevant_chapters"
          :key="index"
          :chapter="chapter"
          :default-expanded="index === 0"
        />
      </div>

      <div v-if="result.llm_explanation" class="llm-section">
        <h4 class="result-title">
          <el-icon><ChatLineRound /></el-icon>
          AI智能解释
        </h4>
        <div class="llm-content-wrapper">
          <LLMContent :content="result.llm_explanation" />
        </div>
      </div>

      <div v-if="!result.relevant_chapters || result.relevant_chapters.length === 0" class="empty-state">
        <el-empty description="未找到相关章节，请尝试使用更通用的关键词" />
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="请输入问题并点击查询" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';
import { Search, Document, ChatLineRound } from '@element-plus/icons-vue';
import { huangdiAnalyze, type HuangdiQueryResponse } from '../api/huangdi';
import HuangdiChapterCard from './HuangdiChapterCard.vue';
import { ElMessage } from 'element-plus';
import LLMContent from './LLMContent.vue';

const question = ref('');
const includeLLM = ref(true);
const loading = ref(false);
const result = ref<HuangdiQueryResponse | null>(null);
const controller = ref<AbortController | null>(null);

const handleQuery = async () => {
  if (!question.value.trim()) {
    ElMessage.warning('请输入查询问题');
    return;
  }

  loading.value = true;
  result.value = null;
  if (controller.value) {
    controller.value.abort();
  }
  controller.value = new AbortController();

  try {
    const response = await huangdiAnalyze({
      question: question.value,
      query_type: 'query',
      include_llm: includeLLM.value,
    }, { signal: controller.value.signal });

    if (response.data.success && response.data.query_type === 'query') {
      result.value = response.data;
    } else {
      ElMessage.error('查询失败，请重试');
    }
  } catch (error: any) {
    if (error?.code === 'ERR_CANCELED') {
      // 请求已取消，不提示
      return;
    }
    console.error('查询失败:', error);
    ElMessage.error(error?.response?.data?.detail || '查询失败，请重试');
  } finally {
    loading.value = false;
    controller.value = null;
  }
};

// 使用 LLMContent 进行安全渲染
onBeforeUnmount(() => {
  if (controller.value) {
    controller.value.abort();
  }
});
</script>

<style scoped>
.huangdi-query-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.input-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #1b4332;
  margin: 0 0 16px 0;
}

.question-input {
  margin-bottom: 16px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-section {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  max-width: 100%;
  padding-right: 8px;
}

/* 滚动条样式 */
.result-section::-webkit-scrollbar {
  width: 8px;
}

.result-section::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.result-section::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.result-section::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.chapters-list {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.llm-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.llm-content-wrapper {
  max-height: none;
  overflow: visible;
}

.llm-content {
  color: #374151;
  line-height: 2;
  font-size: 15px;
  word-break: break-word;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.llm-content :deep(h4) {
  color: #1b4332;
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.llm-content :deep(h4:first-child) {
  margin-top: 0;
}

.llm-content :deep(p) {
  margin: 12px 0;
  text-indent: 2em;
}

.llm-content :deep(p:first-of-type) {
  text-indent: 0;
  font-weight: 500;
  color: #1f2937;
}

.llm-content :deep(ul),
.llm-content :deep(ol) {
  margin: 12px 0;
  padding-left: 2em;
}

.llm-content :deep(li) {
  margin: 8px 0;
  line-height: 1.8;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}
</style>

