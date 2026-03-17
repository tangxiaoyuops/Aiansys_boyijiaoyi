<template>
  <div class="commodity-analysis">
    <el-container>
      <el-row :gutter="24">
        <el-col :span="24" :md="12" :lg="12" :xl="12">
          <el-card class="form-card" shadow="never">
            <template #header>
              <div class="card-header">
                <el-icon :size="22" class="header-icon">
                  <DataAnalysis />
                </el-icon>
                <span class="header-title">大宗商品分析</span>
              </div>
            </template>

            <AnalysisForm
              :model-value="form"
              :loading="analysis.loading"
              @submit="handleStartAnalysis"
              @reset="handleResetForm"
              @save="handleSaveForm"
              @update:modelValue="handleFormChange"
            />
          </el-card>
        </el-col>

        <el-col :span="24" :md="12" :lg="12" :xl="12">
          <ProgressPanel
            v-if="analysis.loading"
            :visible="true"
            :progress="analysis.progress"
            :currentStep="analysis.currentStep"
            :elapsedTime="analysis.elapsedTime"
            :estimatedTime="analysis.estimatedTime"
            @cancel="handleCancelAnalysis"
          />

          <div v-if="hasResult" class="results-container">
            <el-tabs v-model="activeTab" type="border-card">
              <el-tab-pane label="市场概况" name="overview">
                <MarketOverview
                  v-if="result.marketOverview"
                  :data="result.marketOverview"
                />
              </el-tab-pane>

              <el-tab-pane label="买卖策略" name="strategies">
                <div class="strategies-grid">
                  <StrategyCard
                    v-for="strategy in result.strategies"
                    :key="`${strategy.commodity_id}_${strategy.direction}_${strategy.generated_at}`"
                    :strategy="strategy"
                    :showActions="true"
                    @view-backtest="handleViewBacktest"
                    @edit-strategy="handleEditStrategy"
                    @delete-strategy="handleDeleteStrategy"
                  />
                </div>

                <el-empty
                  v-if="!result.strategies || result.strategies.length === 0"
                  description="暂无策略信号"
                />
              </el-tab-pane>

              <el-tab-pane label="回测结果" name="backtest">
                <BacktestResults
                  v-if="result.backtest"
                  :backtestData="result.backtest"
                  :showDetails="true"
                />

                <el-empty
                  v-if="!result.backtest"
                  description="暂无回测结果"
                />
              </el-tab-pane>

              <el-tab-pane label="完整报告" name="report">
                <el-card class="report-card">
                  <div class="report-content">
                    <div v-html="formatReport(result.report)"></div>
                  </div>
                  <div class="report-actions">
                    <el-button type="primary" @click="handleDownloadReport">
                      <el-icon><Download /></el-icon>
                      下载PDF
                    </el-button>
                    <el-button @click="handleCopyReport">
                      <el-icon><DocumentCopy /></el-icon>
                      复制文本
                    </el-button>
                    <el-button @click="handleShareReport">
                      <el-icon><Share /></el-icon>
                      分享
                    </el-button>
                  </div>
                </el-card>
              </el-tab-pane>
            </el-tabs>
          </div>

          <div v-if="!hasResult && !analysis.loading" class="empty-state">
            <el-card class="empty-card" shadow="never">
              <div class="empty-content">
                <el-icon :size="120" color="#dcdfe6" class="empty-icon">
                  <DataAnalysis />
                </el-icon>
                <h3 class="empty-title">开始大宗商品分析</h3>
                <p class="empty-text">选择品种、设置时间范围和策略类型，然后点击"开始分析"按钮</p>
                <div class="empty-tips">
                  <div class="tip-item">
                    <el-icon class="tip-icon"><TrendCharts /></el-icon>
                    <span>支持多种大宗商品品种分析</span>
                  </div>
                  <div class="tip-item">
                    <el-icon class="tip-icon"><DataLine /></el-icon>
                    <span>提供技术指标和基本面分析</span>
                  </div>
                  <div class="tip-item">
                    <el-icon class="tip-icon"><Document /></el-icon>
                    <span>生成买卖策略和回测结果</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { DataAnalysis, Download, DocumentCopy, Share, TrendCharts, DataLine, Document } from '@element-plus/icons-vue';
import { useCommodityStore } from '@/stores/commodity';
import AnalysisForm from '@/components/commodity/AnalysisForm.vue';
import ProgressPanel from '@/components/commodity/ProgressPanel.vue';
import MarketOverview from '@/components/commodity/MarketOverview.vue';
import StrategyCard from '@/components/commodity/StrategyCard.vue';
import BacktestResults from '@/components/commodity/BacktestResults.vue';

const commodityStore = useCommodityStore();

const activeTab = ref('overview');

const form = computed(() => commodityStore.form);
const analysis = computed(() => commodityStore.analysis);
const result = computed(() => commodityStore.result);
const hasResult = computed(() => {
  const hasReport = result.value.report !== '';
  console.log('[CommodityAnalysis] hasResult计算:', hasReport, 'report内容:', result.value.report);
  return hasReport;
});

const handleStartAnalysis = async () => {
  try {
    await commodityStore.startAnalysis();
    ElMessage.success('分析已启动');
  } catch (error: any) {
    ElMessage.error(`分析启动失败: ${error.message}`);
  }
};

const handleCancelAnalysis = () => {
  commodityStore.cancelAnalysis();
  ElMessage.info('分析已取消');
};

const handleResetForm = () => {
  commodityStore.resetForm();
  ElMessage.success('表单已重置');
};

const handleSaveForm = () => {
  commodityStore.saveForm();
  ElMessage.success('配置已保存');
};

const handleFormChange = (newForm: any) => {
  commodityStore.setForm(newForm);
};

const handleViewBacktest = (strategy: any) => {
  ElMessageBox.alert(
    `策略回测功能正在开发中，敬请期待！\n\n策略信息：\n方向: ${strategy.direction}\n入场价: $${strategy.entry_price}\n目标价: $${strategy.target_price}\n止损价: $${strategy.stop_loss}`,
    '查看回测',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  );
};

const handleEditStrategy = (strategy: any) => {
  ElMessageBox.alert(
    `策略编辑功能正在开发中，敬请期待！\n\n策略信息：\n方向: ${strategy.direction}\n入场价: $${strategy.entry_price}`,
    '编辑策略',
    {
      confirmButtonText: '确定',
      type: 'info'
    }
  );
};

const handleDeleteStrategy = (strategy: any) => {
  ElMessageBox.confirm(
    '确定要删除此策略吗？',
    '删除策略',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('策略已删除');
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

const handleDownloadReport = () => {
  ElMessage.info('PDF下载功能正在开发中');
};

const handleCopyReport = () => {
  if (result.value.report) {
    navigator.clipboard.writeText(result.value.report);
    ElMessage.success('报告已复制到剪贴板');
  }
};

const handleShareReport = () => {
  ElMessage.info('分享功能正在开发中');
};

const formatReport = (report: string) => {
  if (!report) return '';
  
  let formatted = report;
  
  formatted = formatted.replace(/^### (.*$)/gm, '<h4>$1</h4>');
  formatted = formatted.replace(/^## (.*$)/gm, '<h3>$1</h3>');
  formatted = formatted.replace(/^# (.*$)/gm, '<h2>$1</h2>');
  
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  formatted = formatted.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  
  formatted = formatted.replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>');
  
  formatted = formatted.replace(/^- (.*$)/gm, '<li>$1</li>');
  formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
  
  formatted = formatted.replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
  
  formatted = formatted.replace(/\n\n/g, '</p><p>');
  formatted = formatted.replace(/\n/g, '<br>');
  
  formatted = '<p>' + formatted + '</p>';
  
  formatted = formatted.replace(/<p><\/p>/g, '');
  formatted = formatted.replace(/<p>(<h[234]>)/g, '$1');
  formatted = formatted.replace(/(<\/h[234]>)<\/p>/g, '$1');
  formatted = formatted.replace(/<p>(<ul>)/g, '$1');
  formatted = formatted.replace(/(<\/ul>)<\/p>/g, '$1');
  formatted = formatted.replace(/<p>(<blockquote>)/g, '$1');
  formatted = formatted.replace(/(<\/blockquote>)<\/p>/g, '$1');
  
  console.log('[formatReport] 格式化后的报告:', formatted);
  
  return formatted;
};

onMounted(() => {
  // commodityStore.loadForm(); // 暂时禁用缓存，确保用户每次都重新选择品种
});
</script>

<style scoped>
.commodity-analysis {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.form-card {
  position: sticky;
  top: 24px;
  z-index: 10;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.header-icon {
  color: var(--el-color-primary);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.results-container {
  margin-top: 24px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  padding: 24px;
}

:deep(.el-tabs--border-card) {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.el-tabs__header) {
  background-color: #fafafa;
  border-radius: 12px 12px 0 0;
}

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.report-card {
  background-color: #ffffff;
  border-radius: 8px;
}

.report-content {
  padding: 24px;
  background-color: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
  line-height: 1.8;
  font-size: 14px;
  color: #303133;
}

.report-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-top: 24px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e4e7ed;
}

.report-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-top: 20px;
  margin-bottom: 15px;
}

.report-content :deep(h4) {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-top: 16px;
  margin-bottom: 10px;
}

.report-content :deep(p) {
  margin-bottom: 12px;
  line-height: 1.8;
}

.report-content :deep(ul) {
  list-style-type: disc;
  padding-left: 24px;
  margin-bottom: 16px;
}

.report-content :deep(li) {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
}

.report-content :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
  color: #606266;
  font-style: italic;
}

.report-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.report-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.report-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #e83e8c;
}

.report-content :deep(.inline-code) {
  background-color: #fff5f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #e83e8c;
  border: 1px solid #ffe0e0;
}

.report-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.report-content :deep(th) {
  background-color: #f5f7fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border: 1px solid #e4e7ed;
}

.report-content :deep(td) {
  padding: 12px;
  border: 1px solid #e4e7ed;
}

.report-content :deep(br) {
  line-height: 1.8;
}

.report-actions {
  display: flex;
  gap: 12px;
  padding: 24px;
  background-color: #ffffff;
  border-radius: 8px;
}

@media (max-width: 992px) {
  .commodity-analysis {
    padding: 16px;
  }

  .form-card {
    position: static;
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .strategies-grid {
    grid-template-columns: 1fr;
  }

  .report-actions {
    flex-direction: column;
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 700px;
  padding: 40px 20px;
}

.empty-card {
  width: 100%;
  border-radius: 12px;
}

.empty-content {
  text-align: center;
  padding: 60px 40px;
}

.empty-icon {
  margin-bottom: 32px;
  opacity: 0.6;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 40px;
}

.empty-tips {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 400px;
  margin: 0 auto;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
}

.tip-item:hover {
  background-color: #e6f4ff;
  transform: translateX(4px);
}

.tip-icon {
  font-size: 20px;
  color: #409eff;
}
</style>
