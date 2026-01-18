<template>
  <div class="backtest-view">
    <div class="view-header">
      <h1>量化回测平台</h1>
      <p class="subtitle">专业的期货与股票策略回测与分析平台</p>
    </div>
    
    <div class="view-content">
      <div class="config-section">
        <BacktestConfig @run="handleRun" />
      </div>
      
      <el-alert
        v-if="backtestStore.error"
        :title="backtestStore.error"
        type="error"
        :closable="true"
        @close="backtestStore.clear()"
        class="error-alert"
      />
      
      <Transition name="fade-slide">
        <div v-if="backtestStore.results" class="results-section">
          <BacktestResults :results="backtestStore.results" />
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import BacktestConfig from '../components/backtest/BacktestConfig.vue';
import BacktestResults from '../components/backtest/BacktestResults.vue';
import { useBacktestStore } from '../stores/backtest';
import type { BacktestRequest, StockBacktestRequest } from '../api/backtest';

const backtestStore = useBacktestStore();

async function handleRun(config: BacktestRequest | StockBacktestRequest, type: 'futures' | 'stock') {
  await backtestStore.run(config, type);
}

onMounted(() => {
  // 初始化
});
</script>

<style scoped>
.backtest-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.view-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 24px;
  text-align: center;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.view-header h1 {
  margin: 0 0 8px 0;
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.view-header .subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.95;
  font-weight: 400;
}

.view-content {
  max-width: 1920px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 48px;
  min-height: calc(100vh - 200px);
}

.config-section {
  margin-bottom: 32px;
}

.error-alert {
  margin-bottom: 24px;
  border-radius: 8px;
}

.results-section {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-slide-enter-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

:deep(.el-card) {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
}

:deep(.el-card__header) {
  padding: 20px 28px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  background: #fafbfc;
}

:deep(.el-card__body) {
  padding: 32px;
}

/* 自定义滚动条样式 */
.backtest-view::-webkit-scrollbar {
  width: 12px;
}

.backtest-view::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 6px;
}

.backtest-view::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 6px;
  transition: background 0.3s;
}

.backtest-view::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

@media (max-width: 1920px) {
  .view-content {
    max-width: 100%;
    padding: 40px 32px;
  }
}

@media (max-width: 1440px) {
  .view-content {
    padding: 36px 24px;
  }
}

@media (max-width: 768px) {
  .view-header {
    padding: 24px 16px;
  }
  
  .view-header h1 {
    font-size: 28px;
  }
  
  .view-content {
    padding: 24px 16px;
  }
}
</style>

