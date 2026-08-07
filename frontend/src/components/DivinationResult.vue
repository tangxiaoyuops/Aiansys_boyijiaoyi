<template>
  <div class="divination-result">
    <!-- 动画效果 -->
    <transition name="fade-slide" mode="out-in">
      <div v-if="isAnalyzing" class="analyzing-container">
        <div class="analyzing-animation">
          <div class="taiji-loader"></div>
          <div class="analyzing-text">
            <div class="text-line">正在推演卦象...</div>
            <div class="text-line small">天机不可泄露，但可推演一二</div>
          </div>
        </div>
      </div>
      
      <div v-else-if="result" class="result-wrapper">
        <!-- 卦象标题 -->
        <div class="hexagram-header">
          <div class="hexagram-title-area">
            <div class="main-hexagram">
              <div class="hexagram-name">{{ result.hexagram?.ben_hexagram?.full_name || '未知卦' }}</div>
              <div class="hexagram-subtitle">本卦</div>
            </div>
            
            <div v-if="result.hexagram?.bian_hexagram" class="hexagram-arrow">
              <div class="arrow-icon">→</div>
              <div class="change-label">变</div>
            </div>
            
            <div v-if="result.hexagram?.bian_hexagram" class="changed-hexagram">
              <div class="hexagram-name">{{ result.hexagram.bian_hexagram.full_name }}</div>
              <div class="hexagram-subtitle">变卦</div>
            </div>
          </div>
          
          <div class="hexagram-chart-container">
            <HexagramChart :hexagram-data="result.hexagram" :size="300" />
          </div>
        </div>
        
        <!-- 卦辞 -->
        <div class="gua-ci-section">
          <div class="section-label">卦辞</div>
          <div class="gua-ci-text">
            {{ result.hexagram?.ben_hexagram?.guaci || '暂无卦辞' }}
          </div>
        </div>
        
        <!-- 爻辞列表 -->
        <div class="yao-ci-section">
          <div class="section-label">爻辞</div>
          <div class="yao-list">
            <div
              v-for="(yao, index) in result.hexagram?.yaos"
              :key="index"
              :class="['yao-item', { 'dong-yao': yao.is_dong }]"
            >
              <div class="yao-left">
                <div class="yao-symbol">{{ yao.symbol }}</div>
                <div class="yao-info">
                  <div class="yao-name">{{ getYaoName(index) }}爻</div>
                  <div class="yao-type">{{ yao.description }}</div>
                </div>
                <div v-if="yao.is_dong" class="dong-tag">
                  <span class="dong-icon">⚡</span>
                  <span>动爻</span>
                </div>
              </div>
              <div v-if="getYaoCi(index)" class="yao-ci">
                {{ getYaoCi(index) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 变卦卦辞 -->
        <div v-if="result.hexagram?.bian_hexagram?.guaci" class="bian-gua-section">
          <div class="section-label">变卦卦辞</div>
          <div class="gua-ci-text">
            {{ result.hexagram.bian_hexagram.guaci }}
          </div>
        </div>
        
        <!-- AI深度解析 -->
        <div v-if="result.llm_analysis?.response" class="ai-analysis-section">
          <div class="section-header">
            <div class="section-label">AI深度解析</div>
            <div class="ai-badge">
              <span class="ai-icon">🤖</span>
              <span>智能分析</span>
            </div>
          </div>
          <div class="ai-content">
            <div class="ai-text" v-html="formatLLMResponse(result.llm_analysis.response)"></div>
          </div>
        </div>
        
        <!-- AI分析错误 -->
        <div v-if="result.llm_analysis?.error" class="error-section">
          <div class="section-label">⚠️ 分析提示</div>
          <div class="error-message">{{ result.llm_analysis.error }}</div>
        </div>
        
        <!-- 解卦提醒 -->
        <div class="reminder-section">
          <div class="reminder-icon">📜</div>
          <div class="reminder-content">
            <div class="reminder-title">解卦提醒</div>
            <div class="reminder-text">
              事在人为，卜卦戒为先；顺天道自然，元亨利贞。
            </div>
            <div class="reminder-text">
              卦象仅供参考，重要决策需结合实际情况，谨慎为之。
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import HexagramChart from './HexagramChart.vue';

interface Props {
  result: any;
  isAnalyzing: boolean;
}

const props = defineProps<Props>();

const yaoNames = ['初', '二', '三', '四', '五', '上'];

function getYaoName(index: number): string {
  return yaoNames[index];
}

function getYaoCi(index: number): string {
  if (!props.result?.hexagram?.ben_hexagram?.yaoci) return '';
  return props.result.hexagram.ben_hexagram.yaoci[String(index + 1)] || '';
}

function formatLLMResponse(text: string): string {
  if (!text) return '';
  return text.split('\n').map(line => {
    if (line.trim() === '') return '<br/>';
    return `<p>${line}</p>`;
  }).join('');
}
</script>

<style scoped>
.divination-result {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

/* 分析中动画 */
.analyzing-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  padding: 40px;
}

.analyzing-animation {
  text-align: center;
}

.taiji-loader {
  width: 120px;
  height: 120px;
  margin: 0 auto 30px;
  border-radius: 50%;
  background: linear-gradient(45deg, #fff 50%, #111 50%);
  animation: rotate 2s linear infinite;
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.analyzing-text {
  color: #e5e7eb;
}

.text-line {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
  animation: pulse 1.5s ease-in-out infinite;
}

.text-line.small {
  font-size: 14px;
  color: #9ca3af;
  font-weight: normal;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 结果展示 */
.result-wrapper {
  padding: 20px;
  animation: fadeIn 0.5s ease-in-out;
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

/* 卦象标题 */
.hexagram-header {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  backdrop-filter: blur(10px);
}

.hexagram-title-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.main-hexagram,
.changed-hexagram {
  text-align: center;
}

.hexagram-name {
  font-size: 32px;
  font-weight: bold;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b9d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.hexagram-subtitle {
  font-size: 14px;
  color: #9ca3af;
}

.hexagram-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.arrow-icon {
  font-size: 28px;
  color: #ffd700;
  font-weight: bold;
}

.change-label {
  font-size: 12px;
  color: #ff6b9d;
  background: rgba(255, 107, 157, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
}

.hexagram-chart-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* 卦辞 */
.gua-ci-section,
.bian-gua-section {
  background: rgba(17, 24, 39, 0.6);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-label {
  font-size: 18px;
  font-weight: 600;
  color: #3b82f6;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.gua-ci-text {
  color: #e5e7eb;
  line-height: 1.8;
  font-size: 15px;
}

/* 爻辞 */
.yao-ci-section {
  background: rgba(17, 24, 39, 0.6);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.yao-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.yao-item {
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.yao-item:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.yao-item.dong-yao {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.4);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
}

.yao-left {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.yao-symbol {
  font-size: 28px;
  color: #ffd700;
  font-weight: bold;
}

.yao-info {
  flex: 1;
}

.yao-name {
  font-size: 14px;
  color: #e5e7eb;
  font-weight: 600;
}

.yao-type {
  font-size: 12px;
  color: #9ca3af;
}

.dong-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.dong-icon {
  font-size: 14px;
}

.yao-ci {
  color: #d1d5db;
  font-size: 14px;
  line-height: 1.6;
  padding-left: 40px;
  margin-top: 8px;
}

/* AI分析 */
.ai-analysis-section {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.ai-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.ai-icon {
  font-size: 16px;
}

.ai-content {
  color: #e5e7eb;
}

.ai-text {
  line-height: 1.8;
  font-size: 15px;
}

.ai-text :deep(p) {
  margin-bottom: 12px;
}

/* 错误提示 */
.error-section {
  background: rgba(239, 68, 68, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.error-message {
  color: #fca5a5;
  font-size: 14px;
  line-height: 1.6;
}

/* 提醒 */
.reminder-section {
  background: rgba(251, 191, 36, 0.1);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(251, 191, 36, 0.3);
  display: flex;
  gap: 16px;
}

.reminder-icon {
  font-size: 32px;
}

.reminder-content {
  flex: 1;
}

.reminder-title {
  font-size: 16px;
  font-weight: 600;
  color: #fbbf24;
  margin-bottom: 8px;
}

.reminder-text {
  color: #d1d5db;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 4px;
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
