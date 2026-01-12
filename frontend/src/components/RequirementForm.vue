<template>
  <div class="requirement-form">
    <div class="form-section">
      <h3 class="section-title">
        <el-icon><DocumentAdd /></el-icon>
        提交需求
      </h3>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入需求标题"
            :maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请详细描述您的需求..."
            :maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="联系方式" prop="contact">
          <el-input
            v-model="form.contact"
            placeholder="可选：邮箱、微信、QQ等"
            :maxlength="100"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            <el-icon><Check /></el-icon>
            提交需求
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="submitted" class="success-section">
      <el-result
        icon="success"
        title="需求提交成功"
        sub-title="感谢您的反馈，我们会尽快处理您的需求"
      >
        <template #extra>
          <el-button type="primary" @click="handleReset">继续提交</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { DocumentAdd, Check } from '@element-plus/icons-vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { submitRequirement, type RequirementRequest } from '../api/feedback';

const formRef = ref<FormInstance>();
const loading = ref(false);
const submitted = ref(false);

const form = reactive<RequirementRequest>({
  title: '',
  content: '',
  contact: ''
});

const rules: FormRules = {
  title: [
    { required: true, message: '请输入需求标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度应在2-200个字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入需求内容', trigger: 'blur' },
    { min: 10, max: 2000, message: '内容长度应在10-2000个字符之间', trigger: 'blur' }
  ]
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    loading.value = true;
    const result = await submitRequirement(form);
    
    ElMessage.success('需求提交成功！');
    submitted.value = true;
    
    // 清空表单
    formRef.value.resetFields();
    form.title = '';
    form.content = '';
    form.contact = '';
    
  } catch (error: any) {
    if (error?.fields) {
      // 表单验证失败
      return;
    }
    console.error('提交需求失败:', error);
    ElMessage.error(error?.response?.data?.detail || error?.message || '提交失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const handleReset = () => {
  submitted.value = false;
  formRef.value?.resetFields();
  form.title = '';
  form.content = '';
  form.contact = '';
};
</script>

<style scoped>
.requirement-form {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 24px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.success-section {
  margin-top: 24px;
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>

