<template>
  <div class="chat-view">
    <div class="sidebar">
      <ProgressPanel :progress="store.progress" />
    </div>
    <div class="content">
      <MessageList :messages="store.messages" />
      <div class="footer">
        <MessageInput 
          :loading="store.loading" 
          @send="handleSend"
          @image-uploaded="handleImageUploaded"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../stores/chat';
import MessageList from '../components/MessageList.vue';
import MessageInput from '../components/MessageInput.vue';
import ProgressPanel from '../components/ProgressPanel.vue';
import { startChatStream } from '../utils/sse';
import { analyzeImage, getImagePreviewUrl, type OCRRecognizeResponse } from '../api/ocr';

const store = useChatStore();
let stopStream: (() => void) | null = null;

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const handleSend = (msg: string) => {
  // 停止上一条流
  if (stopStream) stopStream();

  store.appendMessage({ role: 'user', content: msg });
  store.setLoading(true);
  store.clearProgress();

  const payload = store.buildPayload(msg);
  stopStream = startChatStream({
    baseURL,
    ...payload,
    onEvent: (data) => {
      const type = data.type || 'message';
      if (type === 'start') {
        store.appendMessage({ role: 'system', content: data.message || '开始分析...', type });
      } else if (type === 'progress') {
        store.addProgress(data.node, data.message || data.node);
      } else if (type === 'result') {
        store.appendMessage({ role: 'system', content: data.report || '', type });
      } else if (type === 'detail') {
        // 不再展示巨大的 JSON，只用于承载回测等结构化数据（给图表用）
        store.appendMessage({
          role: 'system',
          content: '',
          type,
          meta: data.data
        });
      } else if (type === 'error') {
        store.appendMessage({ role: 'system', content: `错误：${data.message || ''}`, type });
        store.setLoading(false);
      } else if (type === 'done') {
        store.appendMessage({ role: 'system', content: '分析完成', type });
        store.setLoading(false);
      }
    },
    onError: (err) => {
      store.appendMessage({ role: 'system', content: `流式连接错误：${err?.message || err}`, type: 'error' });
      store.setLoading(false);
    }
  });
};

// OCR相关处理函数
const handleImageUploaded = async (imageId: string, previewUrl: string, imageFile?: File, description?: string) => {
  // 先显示图片消息（如果有说明，一起显示）
  const imageUrl = previewUrl.startsWith('http') ? previewUrl : `${baseURL}${previewUrl}`;
  store.appendMessage({ 
    role: 'user', 
    content: description || '',
    type: 'image',
    imageUrl: imageUrl,
    imageId: imageId
  });
  
  // 自动识别图片
  const loadingMessage = description 
    ? `正在识别图片并处理您的问题：${description}...`
    : '正在识别图片中的文字...';
  store.appendMessage({ 
    role: 'system', 
    content: loadingMessage,
    type: 'ocr_loading'
  });
  
  try {
    console.log('[前端OCR] 开始调用OCR API, imageId:', imageId, 'description:', description);
    const startTime = Date.now();
    
    // 构建context：结合用户的说明和默认提示
    let context = '这是一张股票相关的图片，可能是K线图、财报或公告';
    if (description) {
      context = `${description}\n\n${context}`;
    }
    
    const result = await analyzeImage({
      image_id: imageId,
      context: context
    });
    
    const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log('[前端OCR] API调用完成，耗时:', elapsedTime, '秒', '结果:', result);
    
    if (result.success && result.text) {
      // 显示识别结果，包含耗时信息
      const resultText = result.text.trim();
      const timeInfo = result.elapsed_time ? `（识别耗时: ${result.elapsed_time.toFixed(2)}秒）` : '';
      const modelInfo = result.model ? `（模型: ${result.model}）` : '';
      
      store.appendMessage({ 
        role: 'system', 
        content: `图片识别结果${timeInfo}${modelInfo}：\n\n${resultText}`,
        type: 'ocr_result',
        ocrText: resultText
      });
      
      // 根据是否有用户说明，决定如何发送分析请求
      setTimeout(() => {
        if (description) {
          // 如果有用户说明，将说明和识别结果一起发送
          handleSend(`${description}\n\n图片识别内容：\n${resultText}`);
        } else {
          // 如果没有说明，使用默认提示
          handleSend(`请分析以下从图片中识别的内容：\n\n${resultText}`);
        }
      }, 500);
    } else {
      const errorMsg = result.error || '未知错误';
      console.error('[前端OCR] 识别失败:', errorMsg);
      store.appendMessage({ 
        role: 'system', 
        content: `识别失败：${errorMsg}${result.elapsed_time ? `（耗时: ${result.elapsed_time.toFixed(2)}秒）` : ''}`,
        type: 'error'
      });
    }
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || '识别失败';
    console.error('[前端OCR] 异常:', err);
    store.appendMessage({ 
      role: 'system', 
      content: `识别失败：${errorMsg}`,
      type: 'error'
    });
  }
};
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: row;
  height: 100%;
  overflow: hidden;
}
.sidebar {
  width: 240px;
  padding: 12px;
  border-right: 1px solid #e5e7eb33;
  flex-shrink: 0;
  overflow-y: auto;
}
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.footer {
  flex-shrink: 0;
  padding: 16px;
  border-top: 1px solid #e5e7eb33;
  background: #f9fafb;
}
</style>
