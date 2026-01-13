<template>
  <div class="image-upload">
    <div
      class="upload-area"
      :class="{ 'dragover': isDragging, 'disabled': loading }"
      @drop="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/jpg"
        style="display: none"
        @change="handleFileSelect"
      />
      
      <div v-if="!previewImage && !loading" class="upload-placeholder">
        <el-icon class="upload-icon"><Picture /></el-icon>
        <p class="upload-text">点击或拖拽图片到此处上传</p>
        <p class="upload-hint">支持 JPG、PNG、WebP 格式，最大 10MB</p>
      </div>
      
      <div v-if="previewImage && !loading" class="preview-container">
        <img :src="previewImage" alt="预览图片" class="preview-image" />
        <div class="preview-actions">
          <el-button size="small" @click.stop="removeImage">重新选择</el-button>
        </div>
      </div>
      
      <div v-if="loading" class="upload-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>上传中...</p>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" :closable="false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Picture, Loading } from '@element-plus/icons-vue';
import { uploadImage } from '../api/ocr';

const emit = defineEmits<{
  (e: 'uploaded', imageId: string, previewUrl: string): void;
  (e: 'error', error: string): void;
}>();

const props = defineProps<{
  loading?: boolean;
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const previewImage = ref<string | null>(null);
const error = ref<string | null>(null);
const loading = ref(false);
const currentFile = ref<File | null>(null);

const triggerFileInput = () => {
  if (props.loading || loading.value) return;
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    processFile(file);
  }
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = false;
  
  if (props.loading || loading.value) return;
  
  const file = event.dataTransfer?.files[0];
  if (file) {
    processFile(file);
  }
};

const processFile = async (file: File) => {
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    error.value = `不支持的文件类型: ${file.type}，仅支持 JPG、PNG、WebP 格式`;
    return;
  }
  
  // 验证文件大小（10MB）
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    error.value = `文件大小超过限制: ${(file.size / 1024 / 1024).toFixed(2)}MB，最大支持 10MB`;
    return;
  }
  
  error.value = null;
  currentFile.value = file;
  
  // 显示预览
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
  
  // 上传文件
  try {
    loading.value = true;
    const result = await uploadImage(file);
    emit('uploaded', result.image_id, result.preview_url);
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || '上传失败';
    error.value = errorMsg;
    emit('error', errorMsg);
  } finally {
    loading.value = false;
  }
};

const removeImage = () => {
  previewImage.value = null;
  currentFile.value = null;
  error.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

// 支持粘贴图片
const handlePaste = (event: ClipboardEvent) => {
  if (props.loading || loading.value) return;
  
  const items = event.clipboardData?.items;
  if (!items) return;
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile();
      if (file) {
        processFile(file);
        event.preventDefault();
        break;
      }
    }
  }
};

onMounted(() => {
  window.addEventListener('paste', handlePaste);
});

onUnmounted(() => {
  window.removeEventListener('paste', handlePaste);
});
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9fafb;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover:not(.disabled) {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.upload-area.dragover {
  border-color: #3b82f6;
  background-color: #dbeafe;
}

.upload-area.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 48px;
  color: #9ca3af;
}

.upload-text {
  font-size: 16px;
  color: #374151;
  margin: 0;
}

.upload-hint {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.preview-container {
  position: relative;
  width: 100%;
  max-width: 100%;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}

.preview-actions {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.upload-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-loading .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.error-message {
  margin-top: 12px;
}
</style>

