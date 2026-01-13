<template>

  <div class="input-bar card">

    <div class="form-row">
      <div class="input-wrapper">
        <el-input
          ref="textareaRef"
          v-model="localMessage"
          type="textarea"
          :rows="3"
          :autosize="{ minRows: 3, maxRows: 6 }"
          placeholder="请输入分析问题或图片说明，例如：分析000001的博弈分析（支持粘贴图片，粘贴后可添加说明再发送）"
          :disabled="loading"
          @paste="handlePaste"
          class="message-textarea"
        />
        <el-button
          class="image-button"
          :icon="Picture"
          circle
          :disabled="loading"
          @click="triggerFileInput"
          title="上传图片"
        />
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/jpg"
        style="display: none"
        @change="handleFileSelect"
      />
    </div>
    
    <!-- 图片预览区域 -->
    <div v-if="pendingImage" class="image-preview-row">
      <div class="image-preview">
        <img :src="pendingImagePreview" alt="预览图片" class="preview-thumbnail" />
        <div class="preview-info">
          <span class="preview-text">已选择图片，可在上方输入说明后点击发送</span>
          <el-button size="small" type="danger" text @click="removePendingImage">移除</el-button>
        </div>
      </div>
    </div>

    <div class="form-row options">

      <el-input

        v-model="form.stock_code"

        placeholder="股票代码(可选)"

        style="max-width: 120px"

        :disabled="loading"

      />

      <el-select

        v-model="form.analysis_type"

        placeholder="分析类型"

        style="max-width: 140px"

        :disabled="loading"

      >

        <el-option label="自动" value="auto" />

        <el-option label="常规分析" value="regular" />

        <el-option label="博弈分析" value="game_theory" />

      </el-select>

      <el-input-number

        v-model="form.days"

        :min="30"

        :max="400"

        :step="10"

        :disabled="loading"

        controls-position="right"

      />

      <el-input-number

        v-model="form.initial_capital"

        :min="10000"

        :step="10000"

        :disabled="loading"

        controls-position="right"

        placeholder="初始资金"

        style="max-width: 160px"

      />

      <el-switch

        v-model="form.run_backtest"

        active-text="回测"

        :disabled="loading"

      />

      <el-button type="primary" :loading="loading" @click="handleSend">

        发送

      </el-button>

    </div>

  </div>

</template>



<script setup lang="ts">

import { reactive, ref, watch, onMounted, onUnmounted } from 'vue';
import { Picture } from '@element-plus/icons-vue';
import { useChatStore } from '../stores/chat';
import { uploadImage } from '../api/ocr';
import { ElMessage } from 'element-plus';



const emit = defineEmits<{

  (e: 'send', message: string): void;
  (e: 'image-uploaded', imageId: string, previewUrl: string, file: File, description?: string): void;

}>();



const props = defineProps<{

  loading: boolean;

}>();



const store = useChatStore();

const localMessage = ref('');
const form = reactive({ ...store.form });
const fileInput = ref<HTMLInputElement | null>(null);
const textareaRef = ref<any>(null);

// 待发送的图片（粘贴或选择后暂存，等用户点击发送时再上传）
const pendingImage = ref<File | null>(null);
const pendingImagePreview = ref<string | null>(null);



watch(

  form,

  (v) => {

    store.form = { ...v };

  },

  { deep: true }

);



const handleSend = async () => {
  // 如果有待发送的图片，先上传图片
  if (pendingImage.value) {
    const description = localMessage.value.trim();
    await processImageFile(pendingImage.value, description);
    // 清空待发送图片
    pendingImage.value = null;
    pendingImagePreview.value = null;
    // 如果有说明文字，说明已经通过图片发送了，不需要再发送文本
    if (description) {
      localMessage.value = '';
      return;
    }
  }
  
  // 如果没有图片，或者图片没有说明，发送文本消息
  if (localMessage.value.trim()) {
    emit('send', localMessage.value.trim());
    localMessage.value = '';
  }
};

const triggerFileInput = () => {
  if (props.loading) return;
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    setPendingImage(file);
  }
  // 清空input，以便可以重复选择同一文件
  if (target) {
    target.value = '';
  }
};

const handlePaste = (event: ClipboardEvent) => {
  if (props.loading) return;
  
  const items = event.clipboardData?.items;
  if (!items) return;
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile();
      if (file) {
        event.preventDefault();
        setPendingImage(file);
        ElMessage.info('图片已粘贴，可在输入框中添加说明后点击发送');
        break;
      }
    }
  }
};

// 设置待发送的图片（只预览，不上传）
const setPendingImage = (file: File) => {
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error(`不支持的文件类型: ${file.type}，仅支持 JPG、PNG、WebP 格式`);
    return;
  }
  
  // 验证文件大小（10MB）
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    ElMessage.error(`文件大小超过限制: ${(file.size / 1024 / 1024).toFixed(2)}MB，最大支持 10MB`);
    return;
  }
  
  // 保存文件并生成预览
  pendingImage.value = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    pendingImagePreview.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
};

// 移除待发送的图片
const removePendingImage = () => {
  pendingImage.value = null;
  pendingImagePreview.value = null;
};

// 处理图片上传（实际上传到服务器）
const processImageFile = async (file: File, description?: string) => {
  try {
    ElMessage.info('正在上传图片...');
    const result = await uploadImage(file);
    ElMessage.success('图片上传成功，正在识别...');
    // 传递图片和用户的说明文字
    emit('image-uploaded', result.image_id, result.preview_url, file, description);
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || '上传失败';
    ElMessage.error(`图片上传失败: ${errorMsg}`);
    throw err; // 抛出错误，让调用方知道上传失败
  }
};

</script>



<style scoped>

.input-bar {

  padding: 12px;

  border-top: 1px solid #1f2937;

}

.form-row {

  display: flex;

  gap: 8px;
  width: 100%;

}

.form-row + .form-row {

  margin-top: 10px;

}

.input-wrapper {
  display: flex;
  flex: 1;
  gap: 8px;
  align-items: flex-start;
  width: 100%;
}

.message-textarea {
  flex: 1;
  width: 100%;
}

.message-textarea :deep(.el-textarea__inner) {
  width: 100%;
  min-height: 80px;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px;
  resize: vertical;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #E5E7EB;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.message-textarea :deep(.el-textarea__inner):focus {
  border-color: rgba(139, 92, 246, 0.5);
  background-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.message-textarea :deep(.el-textarea__inner)::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.image-button {
  flex-shrink: 0;
  margin-top: 0;
  width: 40px;
  height: 40px;
  background-color: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #A78BFA;
  transition: all 0.3s ease;
}

.image-button:hover {
  background-color: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.5);
  color: #C4B5FD;
}

.image-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.options {

  align-items: center;
  flex-wrap: wrap;

}

.image-preview-row {
  margin-top: 8px;
  padding: 8px;
  background: rgba(139, 92, 246, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.image-preview {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.preview-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-text {
  font-size: 13px;
  color: #CBD5E1;
}

</style>





