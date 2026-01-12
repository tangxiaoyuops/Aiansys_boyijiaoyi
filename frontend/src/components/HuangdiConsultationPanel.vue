<template>
  <div class="huangdi-consultation-panel">
    <div class="input-section">
      <h3 class="section-title">
        <el-icon><Sunny /></el-icon>
        健康咨询
      </h3>
      
      <el-input
        v-model="userInfo"
        type="textarea"
        :rows="3"
        placeholder="请描述您的身体状况、生活习惯等，例如：平时容易疲劳，手脚比较凉"
        class="user-info-input"
      />

      <div class="context-form">
        <el-form :model="context" label-width="100px" size="default">
          <el-form-item label="季节">
            <el-select v-model="context.season" placeholder="选择季节（可选，默认自动检测）" clearable>
              <el-option label="春季" value="春" />
              <el-option label="夏季" value="夏" />
              <el-option label="秋季" value="秋" />
              <el-option label="冬季" value="冬" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="年龄">
            <el-input-number
              v-model="context.age"
              :min="1"
              :max="120"
              placeholder="年龄（可选）"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="体质">
            <el-checkbox-group v-model="context.constitution">
              <el-checkbox label="阳虚">阳虚</el-checkbox>
              <el-checkbox label="阴虚">阴虚</el-checkbox>
              <el-checkbox label="气虚">气虚</el-checkbox>
              <el-checkbox label="血虚">血虚</el-checkbox>
              <el-checkbox label="痰湿">痰湿</el-checkbox>
              <el-checkbox label="湿热">湿热</el-checkbox>
              <el-checkbox label="气郁">气郁</el-checkbox>
              <el-checkbox label="血瘀">血瘀</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
      </div>

      <div class="action-bar">
        <el-checkbox v-model="includeLLM">包含AI建议</el-checkbox>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleConsultation"
          :disabled="!userInfo.trim()"
        >
          <el-icon><Search /></el-icon>
          咨询
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="result-section">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="result" class="result-section">
      <HuangdiDisclaimer
        :text="result.disclaimer"
        variant="info"
        title="温馨提示"
      />

      <div v-if="result.season || result.age || result.constitution.length > 0" class="context-info">
        <h4 class="result-title">
          <el-icon><InfoFilled /></el-icon>
          咨询信息
        </h4>
        <div class="info-tags">
          <el-tag v-if="result.season" type="success" size="large">
            <el-icon><Sunny /></el-icon>
            {{ result.season }}季
          </el-tag>
          <el-tag v-if="result.age" type="info" size="large">
            {{ result.age }}岁
          </el-tag>
          <el-tag
            v-for="(item, index) in result.constitution"
            :key="index"
            type="warning"
            size="large"
          >
            {{ item }}
          </el-tag>
        </div>
      </div>

      <div v-if="result.relevant_theories && result.relevant_theories.length > 0" class="theories-section">
        <h4 class="result-title">
          <el-icon><Document /></el-icon>
          相关养生理论 ({{ result.relevant_theories.length }})
        </h4>
        <div class="theories-list">
          <HuangdiTheoryCard
            v-for="(theory, index) in result.relevant_theories"
            :key="index"
            :theory="theory"
          />
        </div>
      </div>

      <div v-if="result.llm_suggestions" class="llm-section">
        <h4 class="result-title">
          <el-icon><ChatLineRound /></el-icon>
          AI个性化建议
        </h4>
        <div class="llm-content-wrapper">
          <LLMContent :content="result.llm_suggestions" />
        </div>
      </div>

      <div v-if="!result.relevant_theories || result.relevant_theories.length === 0" class="empty-state">
        <el-empty description="未找到相关理论，请尝试更详细的描述" />
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="请输入您的身体状况并点击咨询" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';
import { Sunny, Search, InfoFilled, Document, ChatLineRound } from '@element-plus/icons-vue';
import { huangdiAnalyze, type HuangdiConsultationResponse } from '../api/huangdi';
import HuangdiTheoryCard from './HuangdiTheoryCard.vue';
import HuangdiDisclaimer from './HuangdiDisclaimer.vue';
import { ElMessage } from 'element-plus';
import LLMContent from './LLMContent.vue';

const userInfo = ref('');
const includeLLM = ref(true);
const loading = ref(false);
const result = ref<HuangdiConsultationResponse | null>(null);
const controller = ref<AbortController | null>(null);

const context = ref({
  season: '',
  age: undefined as number | undefined,
  constitution: [] as string[],
});

const handleConsultation = async () => {
  if (!userInfo.value.trim()) {
    ElMessage.warning('请描述您的身体状况');
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
      question: userInfo.value,
      query_type: 'consultation',
      include_llm: includeLLM.value,
      context: {
        season: context.value.season || undefined,
        age: context.value.age,
        constitution: context.value.constitution.length > 0 ? context.value.constitution : undefined,
      },
    }, { signal: controller.value.signal });

    if (response.data.success && response.data.query_type === 'consultation') {
      result.value = response.data;
    } else {
      ElMessage.error('咨询失败，请重试');
    }
  } catch (error: any) {
    if (error?.code === 'ERR_CANCELED') {
      return;
    }
    console.error('咨询失败:', error);
    ElMessage.error(error.response?.data?.detail || '咨询失败，请重试');
  } finally {
    loading.value = false;
    controller.value = null;
  }
};

onBeforeUnmount(() => {
  if (controller.value) {
    controller.value.abort();
  }
});
</script>

<style scoped>
.huangdi-consultation-panel {
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

.user-info-input {
  margin-bottom: 16px;
}

.context-form {
  margin-bottom: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
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

.context-info {
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

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.theories-section {
  margin-bottom: 24px;
}

.theories-list {
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

