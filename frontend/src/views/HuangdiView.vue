<template>
  <div class="huangdi-view">
    <div class="view-header">
      <h1 class="page-title">
        <el-icon><Reading /></el-icon>
        黄帝内经
      </h1>
      <p class="page-subtitle">基于《黄帝内经》经典理论的知识查询、诊断建议与健康咨询</p>
    </div>

    <div class="main-layout">
      <el-tabs v-model="activeTab" class="function-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="知识查询" name="query">
          <template #label>
            <span class="tab-label">
              <el-icon><Search /></el-icon>
              知识查询
            </span>
          </template>
          <HuangdiQueryPanel />
        </el-tab-pane>

        <el-tab-pane label="诊断建议" name="diagnosis">
          <template #label>
            <span class="tab-label">
              <el-icon><FirstAidKit /></el-icon>
              诊断建议
            </span>
          </template>
          <HuangdiDiagnosisPanel />
        </el-tab-pane>

        <el-tab-pane label="健康咨询" name="consultation">
          <template #label>
            <span class="tab-label">
              <el-icon><Sunny /></el-icon>
              健康咨询
            </span>
          </template>
          <HuangdiConsultationPanel />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Reading, Search, FirstAidKit, Sunny } from '@element-plus/icons-vue';
import HuangdiQueryPanel from '../components/HuangdiQueryPanel.vue';
import HuangdiDiagnosisPanel from '../components/HuangdiDiagnosisPanel.vue';
import HuangdiConsultationPanel from '../components/HuangdiConsultationPanel.vue';

const activeTab = ref('query');

const handleTabChange = (name: string) => {
  console.log('切换到标签:', name);
};
</script>

<style scoped>
.huangdi-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef9e7 0%, #fff8dc 100%);
  padding: 24px;
}

.view-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #1b4332;
  margin: 0 0 12px 0;
  font-family: 'Noto Serif SC', 'SimSun', serif;
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.main-layout {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.function-tabs {
  min-height: 600px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.function-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background: #f9fafb;
  border-bottom: 2px solid #e5e7eb;
}

.function-tabs :deep(.el-tabs__nav-wrap) {
  &::after {
    display: none;
  }
}

.function-tabs :deep(.el-tabs__item) {
  padding: 20px 24px;
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.3s ease;
}

.function-tabs :deep(.el-tabs__item:hover) {
  color: #1b4332;
}

.function-tabs :deep(.el-tabs__item.is-active) {
  color: #1b4332;
  font-weight: 600;
}

.function-tabs :deep(.el-tabs__active-bar) {
  background: #1b4332;
  height: 3px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.function-tabs :deep(.el-tabs__content) {
  padding: 24px;
  min-height: 500px;
  max-height: calc(100vh - 250px);
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

/* 确保滚动条可见 */
.function-tabs :deep(.el-tabs__content)::-webkit-scrollbar {
  width: 10px;
}

.function-tabs :deep(.el-tabs__content)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 5px;
}

.function-tabs :deep(.el-tabs__content)::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 5px;
}

.function-tabs :deep(.el-tabs__content)::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .huangdi-view {
    padding: 12px;
  }

  .view-header {
    padding: 16px;
    margin-bottom: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .function-tabs :deep(.el-tabs__item) {
    padding: 16px 12px;
    font-size: 14px;
  }

  .function-tabs :deep(.el-tabs__content) {
    padding: 16px;
  }
}
</style>

