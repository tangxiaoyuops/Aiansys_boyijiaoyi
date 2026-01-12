<template>
  <div class="huangdi-diagnosis-panel">
    <div class="input-section">
      <h3 class="section-title">
        <el-icon><FirstAidKit /></el-icon>
        诊断建议
      </h3>
      <el-input
        v-model="symptoms"
        type="textarea"
        :rows="4"
        placeholder="请输入症状描述，例如：头痛、发热、恶寒（多个症状用逗号分隔）"
        class="symptoms-input"
      />
      <div class="action-bar">
        <el-checkbox v-model="includeLLM">包含AI分析</el-checkbox>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleDiagnosis"
          :disabled="!symptoms.trim()"
        >
          <el-icon><Search /></el-icon>
          分析
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="result-section">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="result" class="result-section">
      <HuangdiDisclaimer
        :text="result.disclaimer"
        variant="warning"
        title="重要提示"
      />

      <div v-if="result.symptom_keywords && result.symptom_keywords.length > 0" class="keywords-section">
        <h4 class="result-title">
          <el-icon><CollectionTag /></el-icon>
          提取的症状关键词
        </h4>
        <div class="keywords-list">
          <el-tag
            v-for="(keyword, index) in result.symptom_keywords"
            :key="index"
            type="warning"
            size="large"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>

      <div v-if="result.relevant_theories && result.relevant_theories.length > 0" class="theories-section">
        <h4 class="result-title">
          <el-icon><Document /></el-icon>
          相关理论 ({{ result.relevant_theories.length }})
        </h4>
        <HuangdiTheoryCard
          v-for="(theory, index) in result.relevant_theories"
          :key="index"
          :theory="theory"
        />
      </div>

      <div v-if="result.llm_analysis" class="llm-section">
        <h4 class="result-title">
          <el-icon><ChatLineRound /></el-icon>
          AI理论分析
        </h4>
        <div class="llm-content-wrapper">
          <LLMContent :content="result.llm_analysis" />
        </div>
      </div>

      <div v-if="!result.relevant_theories || result.relevant_theories.length === 0" class="empty-state">
        <el-empty description="未找到相关理论，请尝试使用更通用的症状描述" />
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="请输入症状描述并点击分析" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';
import { FirstAidKit, Search, CollectionTag, Document, ChatLineRound } from '@element-plus/icons-vue';
import { huangdiAnalyze, type HuangdiDiagnosisResponse } from '../api/huangdi';
import HuangdiTheoryCard from './HuangdiTheoryCard.vue';
import HuangdiDisclaimer from './HuangdiDisclaimer.vue';
import { ElMessage } from 'element-plus';
import LLMContent from './LLMContent.vue';

const symptoms = ref('');
const includeLLM = ref(true);
const loading = ref(false);
const result = ref<HuangdiDiagnosisResponse | null>(null);
const controller = ref<AbortController | null>(null);

const handleDiagnosis = async () => {
  if (!symptoms.value.trim()) {
    ElMessage.warning('请输入症状描述');
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
      question: symptoms.value,
      query_type: 'diagnosis',
      include_llm: includeLLM.value,
    }, { signal: controller.value.signal });

    if (response.data.success && response.data.query_type === 'diagnosis') {
      result.value = response.data;
    } else {
      ElMessage.error('分析失败，请重试');
    }
  } catch (error: any) {
    if (error?.code === 'ERR_CANCELED') {
      return;
    }
    console.error('分析失败:', error);
    ElMessage.error(error.response?.data?.detail || '分析失败，请重试');
  } finally {
    loading.value = false;
    controller.value = null;
  }
};
onBeforeUnmount(() => {
  if (controller && controller.value) {
    controller.value.abort();
  }
});
</script>

<style scoped>
.huangdi-diagnosis-panel {
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

.symptoms-input {
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

.keywords-section {
  margin-bottom: 24px;
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

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  font-size: 14px;
  padding: 8px 16px;
}

.theories-section {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
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

