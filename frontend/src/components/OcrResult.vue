<template>
  <div class="ocr-result">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在识别图片文字...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" :closable="false" />
    </div>
    
    <div v-else-if="result" class="result-container">
      <div class="image-section">
        <h4 class="section-title">
          <el-icon><Picture /></el-icon>
          原始图片
        </h4>
        <div class="image-wrapper">
          <img :src="imageUrl" alt="原始图片" class="result-image" />
        </div>
      </div>
      
      <div class="text-section">
        <div class="section-header">
          <h4 class="section-title">
            <el-icon><Document /></el-icon>
            识别结果
          </h4>
          <div class="actions">
            <el-button size="small" @click="copyText">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button size="small" @click="editText">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </div>
        
        <div v-if="!isEditing" class="text-content">
          <pre class="text-pre">{{ result.text }}</pre>
        </div>
        
        <div v-else class="text-editor">
          <el-input
            v-model="editedText"
            type="textarea"
            :rows="10"
            @blur="saveEdit"
          />
          <div class="editor-actions">
            <el-button size="small" type="primary" @click="saveEdit">保存</el-button>
            <el-button size="small" @click="cancelEdit">取消</el-button>
          </div>
        </div>
        
        <div v-if="result.model || result.elapsed_time" class="result-meta">
          <span v-if="result.model">模型: {{ result.model }}</span>
          <span v-if="result.elapsed_time">识别耗时: {{ result.elapsed_time.toFixed(2) }}秒</span>
        </div>
      </div>
      
      <div v-if="showAnalyzeButton" class="analyze-section">
        <el-button type="primary" @click="handleAnalyze">
          <el-icon><Search /></el-icon>
          分析此内容
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Picture, Document, CopyDocument, Edit, Loading, Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import type { OCRRecognizeResponse } from '../api/ocr';

const props = defineProps<{
  result?: OCRRecognizeResponse | null;
  imageUrl?: string;
  loading?: boolean;
  error?: string | null;
  showAnalyzeButton?: boolean;
}>();

const emit = defineEmits<{
  (e: 'analyze', text: string): void;
}>();

const isEditing = ref(false);
const editedText = ref('');

const result = computed(() => props.result);

const copyText = () => {
  if (!result.value?.text) return;
  
  navigator.clipboard.writeText(result.value.text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败');
  });
};

const editText = () => {
  editedText.value = result.value?.text || '';
  isEditing.value = true;
};

const saveEdit = () => {
  if (result.value) {
    result.value.text = editedText.value;
  }
  isEditing.value = false;
};

const cancelEdit = () => {
  editedText.value = result.value?.text || '';
  isEditing.value = false;
};

const handleAnalyze = () => {
  if (result.value?.text) {
    emit('analyze', result.value.text);
  }
};
</script>

<style scoped>
.ocr-result {
  width: 100%;
}

.loading-container,
.error-container {
  padding: 40px;
  text-align: center;
}

.loading-container .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.image-section,
.text-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1f2937;
}

.image-wrapper {
  display: flex;
  justify-content: center;
  background: white;
  border-radius: 4px;
  padding: 12px;
}

.result-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 4px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.text-content {
  background: white;
  border-radius: 4px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.text-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
}

.text-editor {
  background: white;
  border-radius: 4px;
  padding: 16px;
}

.editor-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.result-meta {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-size: 12px;
  color: #6b7280;
  display: flex;
  gap: 16px;
}

.analyze-section {
  display: flex;
  justify-content: center;
  padding: 16px;
}
</style>

