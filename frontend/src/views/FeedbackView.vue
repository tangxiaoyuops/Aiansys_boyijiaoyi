<template>
  <div class="feedback-view">
    <div class="view-header">
      <h2 class="view-title">反馈中心</h2>
      <p class="view-subtitle">提交需求、报告问题或支持我们</p>
    </div>

    <el-tabs v-model="activeTab" class="feedback-tabs">
      <el-tab-pane label="提需求" name="requirement">
        <template #label>
          <span class="tab-label">
            <el-icon><DocumentAdd /></el-icon>
            提需求
          </span>
        </template>
        <div class="tab-content">
          <RequirementForm />
        </div>
      </el-tab-pane>

      <el-tab-pane label="报问题" name="issue">
        <template #label>
          <span class="tab-label">
            <el-icon><WarningFilled /></el-icon>
            报问题
          </span>
        </template>
        <div class="tab-content">
          <IssueForm />
        </div>
      </el-tab-pane>

      <el-tab-pane label="打赏" name="reward">
        <template #label>
          <span class="tab-label">
            <el-icon><Money /></el-icon>
            打赏
          </span>
        </template>
        <div class="tab-content">
          <RewardPanel />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { DocumentAdd, WarningFilled, Money } from '@element-plus/icons-vue';
import RequirementForm from '../components/RequirementForm.vue';
import IssueForm from '../components/IssueForm.vue';
import RewardPanel from '../components/RewardPanel.vue';

const activeTab = ref('requirement');
</script>

<style scoped>
.feedback-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f3f4f6;
}

.view-header {
  padding: 24px 24px 16px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.view-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.view-subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.feedback-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
  margin: 0 24px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feedback-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.feedback-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.feedback-tabs :deep(.el-tabs__item) {
  padding: 16px 24px;
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
}

.feedback-tabs :deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}

.feedback-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-content {
  padding: 24px;
  min-height: 100%;
}
</style>

