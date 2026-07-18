<template>
  <!-- 悬浮反馈按钮 -->
  <div class="feedback-fab" @click="showDialog = true">
    <el-icon :size="20">
      <ChatDotRound />
    </el-icon>
    <span class="fab-text">反馈</span>
  </div>

  <!-- 反馈对话框 -->
  <el-dialog
    v-model="showDialog"
    title="问题反馈"
    width="500px"
    :close-on-click-modal="false"
    class="feedback-dialog"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      label-position="top"
    >
      <el-form-item label="反馈类型" prop="type">
        <el-radio-group v-model="form.type">
          <el-radio label="bug">功能问题</el-radio>
          <el-radio label="suggestion">功能建议</el-radio>
          <el-radio label="other">其他</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="问题描述" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="5"
          placeholder="请详细描述您遇到的问题或建议..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="联系方式" prop="contact">
        <el-input
          v-model="form.contact"
          placeholder="选填：手机号/邮箱/微信等"
          maxlength="100"
        />
      </el-form-item>

      <el-form-item label="截图上传" prop="screenshots">
        <el-upload
          v-model:file-list="fileList"
          action="#"
          :auto-upload="false"
          :limit="3"
          accept="image/*"
          list-type="picture-card"
          :on-exceed="handleExceed"
        >
          <el-icon><Plus /></el-icon>
          <template #tip>
            <div class="upload-tip">最多上传3张截图</div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          提交反馈
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadUserFile, UploadProps } from 'element-plus'
import axios from 'axios'

const showDialog = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const fileList = ref<UploadUserFile[]>([])

const form = reactive({
  type: 'bug',
  content: '',
  contact: '',
})

const rules: FormRules = {
  type: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请描述您的问题或建议', trigger: 'blur' },
    { min: 10, message: '描述内容至少10个字符', trigger: 'blur' }
  ],
}

const handleExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('最多只能上传3张截图')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 准备提交数据
      const payload = {
        type: form.type,
        content: form.content,
        contact: form.contact || undefined,
        // 截图暂时不上传，后续可以添加图片上传功能
        screenshots: fileList.value.map(f => f.name),
        // 自动收集环境信息
        metadata: {
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: new Date().toISOString(),
          screenSize: `${window.innerWidth}x${window.innerHeight}`,
        }
      }
      
      // 调用后端API
      const response = await axios.post('/api/feedback', payload)
      
      if (response.data.success) {
        ElMessage.success('感谢您的反馈！我们会尽快处理')
        showDialog.value = false
        // 重置表单
        formRef.value.resetFields()
        fileList.value = []
      } else {
        ElMessage.error(response.data.message || '提交失败，请稍后重试')
      }
    } catch (error: any) {
      console.error('提交反馈失败:', error)
      ElMessage.error(error.response?.data?.detail || '提交失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.feedback-fab {
  position: fixed;
  right: 20px;
  bottom: 80px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
}

.feedback-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.feedback-fab:active {
  transform: translateY(0);
}

.fab-text {
  font-size: 14px;
  font-weight: 500;
}

/* 对话框样式 */
:deep(.feedback-dialog) {
  border-radius: 12px;
}

:deep(.feedback-dialog .el-dialog__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.feedback-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.feedback-dialog .el-dialog__body) {
  padding: 24px 20px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式适配 */
@media (max-width: 767.98px) {
  .feedback-fab {
    right: 12px;
    bottom: 70px;
    padding: 10px 14px;
  }

  .fab-text {
    display: none;
  }

  .feedback-fab {
    border-radius: 50%;
    width: 44px;
    height: 44px;
    padding: 0;
    justify-content: center;
  }
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .feedback-fab {
    background: linear-gradient(135deg, #4c6ef5 0%, #7950f2 100%);
    box-shadow: 0 4px 12px rgba(76, 110, 245, 0.4);
  }
}
</style>
