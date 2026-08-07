<template>
  <div class="divination-view">
    <!-- 太极背景动画 -->
    <TaijiBackground 
      :intensity="0.5" 
      :is-shaking="isShaking" 
      :shake-level="currentYaoIndex"
      :yao-results="yaoResults"
    />
    
    <div class="main-layout">
      <!-- 左侧输入区域 -->
      <div class="left-panel">
        <div class="input-card">
          <h2 class="card-title">六爻卜卦</h2>
          
          <!-- 提示语 -->
          <div class="divination-tips">
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>事在人为，卜卦戒为先</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>顺天道自然，元亨利贞</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>卦象仅供参考，决策需谨慎</span>
            </div>
          </div>
          
          <!-- 用户问题输入 -->
          <el-form :model="form" label-width="90px" class="divination-form">
            <el-form-item label="问题">
              <el-input
                v-model="form.question"
                type="textarea"
                :rows="3"
                placeholder="请输入您要问的问题..."
                style="width: 100%"
              />
            </el-form-item>
            
            <el-divider />
            
            <!-- 摇卦区域 -->
            <div class="coin-toss-section">
              <div class="section-title">摇卦区域（从下往上：初爻→上爻）</div>
              
              <!-- 一键摇卦按钮 -->
              <div v-if="!allYaoComplete" class="auto-toss-area">
                <el-button 
                  type="primary" 
                  size="large" 
                  :loading="isAutoTossing"
                  :disabled="isAutoTossing || isAnalyzing"
                  @click="handleAutoToss"
                  class="auto-toss-btn"
                >
                  <el-icon v-if="!isAutoTossing"><Star /></el-icon>
                  {{ isAutoTossing ? `正在摇第${currentYaoIndex + 1}爻...` : '点击摇卦' }}
                </el-button>
                <div class="toss-hint">点击按钮，自动完成六爻摇卦</div>
              </div>
              
              <!-- 六爻结果展示 -->
              <div class="yao-results-list">
                <div
                  v-for="(yaoResult, index) in yaoResults"
                  :key="index"
                  :class="['yao-toss-item', { active: currentYaoIndex === index && isAutoTossing }]"
                >
                  <div class="yao-label">第{{ index + 1 }}爻（{{ getYaoName(index) }}爻）</div>
                  <div v-if="yaoResult" class="yao-result-display">
                    <span class="yao-symbol-large">{{ yaoResult.symbol }}</span>
                    <span class="yao-desc">{{ yaoResult.description }}</span>
                  </div>
                  <div v-else class="yao-placeholder">
                    <span class="placeholder-text">等待摇卦</span>
                  </div>
                </div>
              </div>
            </div>
            
            <el-divider />
            
            <!-- 操作按钮 -->
            <el-form-item>
              <div style="display: flex; gap: 10px; flex-direction: column;">
                <div style="display: flex; gap: 10px;">
                  <el-button 
                    type="warning" 
                    @click="handleReset" 
                    :disabled="isAnalyzing"
                  >
                    重新摇卦
                  </el-button>
                  <el-button
                    type="primary"
                    :loading="isAnalyzing"
                    :disabled="!canAnalyze"
                    @click="handleAnalyze"
                    style="flex: 1"
                  >
                    <el-icon><MagicStick /></el-icon>
                    开始解卦
                  </el-button>
                </div>
                <!-- 调试信息 -->
                <div v-if="!canAnalyze" style="font-size: 12px; color: #fca5a5; margin-top: 8px;">
                  <span v-if="!form.question.trim()">⚠️ 请输入问题</span>
                  <span v-else-if="!allYaoComplete">⚠️ 请完成6次摇卦</span>
                </div>
              </div>
            </el-form-item>
            
            <!-- 分析选项 -->
            <el-form-item label="分析选项">
              <el-checkbox v-model="form.include_llm">AI深度分析</el-checkbox>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <DivinationResult 
          :result="result" 
          :is-analyzing="isAnalyzing"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, InfoFilled, Star } from '@element-plus/icons-vue';
import api from '../api';
import TaijiBackground from '../components/TaijiBackground.vue';
import DivinationResult from '../components/DivinationResult.vue';

const isAnalyzing = ref(false);
const result = ref<any>(null);

// 摇卦动画状态
const isShaking = ref(false);
const currentYaoIndex = ref(0);
const isAutoTossing = ref(false);

const form = reactive({
  question: '',
  include_llm: true,
});

const yaoResults = ref<(any | null)[]>(Array(6).fill(null));

// 谦卦数据（地山谦）- 从下往上：初六、六二、九三、六四、六五、上六
const qianHexagram = {
  yaos: [
    { is_yang: false, is_dong: false, description: '初六' }, // 初六
    { is_yang: false, is_dong: false, description: '六二' }, // 六二
    { is_yang: true, is_dong: false, description: '九三' },  // 九三
    { is_yang: false, is_dong: false, description: '六四' }, // 六四
    { is_yang: false, is_dong: false, description: '六五' }, // 六五
    { is_yang: false, is_dong: false, description: '上六' }, // 上六
  ],
  ben_hexagram: { full_name: '地山谦' },
  inner_trigram: { name: '艮' },
  outer_trigram: { name: '坤' },
  dong_yaos: [],
};

// 泰卦数据（地天泰）- 从下往上：初九、九二、九三、六四、六五、上六
const taiHexagram = {
  yaos: [
    { is_yang: true, is_dong: false, description: '初九' },  // 初九
    { is_yang: true, is_dong: false, description: '九二' },  // 九二
    { is_yang: true, is_dong: false, description: '九三' },  // 九三
    { is_yang: false, is_dong: false, description: '六四' }, // 六四
    { is_yang: false, is_dong: false, description: '六五' }, // 六五
    { is_yang: false, is_dong: false, description: '上六' }, // 上六
  ],
  ben_hexagram: { full_name: '地天泰' },
  inner_trigram: { name: '乾' },
  outer_trigram: { name: '坤' },
  dong_yaos: [],
};

const canAnalyze = computed(() => {
  return (
    form.question.trim() &&
    yaoResults.value.every(yao => yao !== null)
  );
});

const allYaoComplete = computed(() => {
  return yaoResults.value.every(yao => yao !== null);
});

const yaoNames = ['初', '二', '三', '四', '五', '上'];

function getYaoName(index: number): string {
  return yaoNames[index];
}

// 随机生成一爻的结果
function generateYaoResult(): { coins: [number, number, number], yaoType: string, yaoNumber: number } {
  const coins: [number, number, number] = [
    Math.random() < 0.5 ? 0 : 1,
    Math.random() < 0.5 ? 0 : 1,
    Math.random() < 0.5 ? 0 : 1,
  ];
  
  const headsCount = coins.reduce((sum, coin) => sum + coin, 0);
  
  if (headsCount === 3) {
    return { coins, yaoType: '老阳', yaoNumber: 9 };
  } else if (headsCount === 0) {
    return { coins, yaoType: '老阴', yaoNumber: 6 };
  } else if (headsCount === 2) {
    return { coins, yaoType: '少阳', yaoNumber: 7 };
  } else {
    return { coins, yaoType: '少阴', yaoNumber: 8 };
  }
}

// 一键摇卦
async function handleAutoToss() {
  if (isAutoTossing.value || isAnalyzing.value) return;
  
  isAutoTossing.value = true;
  isShaking.value = true;
  
  for (let i = 0; i < 6; i++) {
    currentYaoIndex.value = i;
    
    // 摇卦动画等待时间
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // 生成结果
    const yaoData = generateYaoResult();
    yaoResults.value[i] = {
      symbol: yaoData.yaoType.includes('阳') ? '⚊' : '⚋',
      description: yaoData.yaoType,
      yaoNumber: yaoData.yaoNumber,
      coins: yaoData.coins,
      isYang: yaoData.yaoType.includes('阳'),
      isDong: yaoData.yaoType.includes('老'),
    };
  }
  
  isAutoTossing.value = false;
  isShaking.value = false;
  currentYaoIndex.value = 6;
}

function handleReset() {
  yaoResults.value = Array(6).fill(null);
  result.value = null;
  form.question = '';
  isShaking.value = false;
  currentYaoIndex.value = 0;
}

async function handleAnalyze() {
  if (!canAnalyze.value) {
    ElMessage.warning('请填写问题并完成6次摇卦');
    return;
  }
  
  try {
    isAnalyzing.value = true;
    result.value = null;
    
    // 构建请求数据
    const coinResults = yaoResults.value.map(yao => yao.coins);
    
    const response = await api.post('/api/divination/analyze', {
      coin_results: coinResults,
      question: form.question,
      include_llm: form.include_llm,
    });
    
    if (response.data.success) {
      result.value = response.data;
      ElMessage.success('解卦分析完成');
    } else {
      ElMessage.error(response.data.error || '解卦分析失败');
    }
  } catch (error: any) {
    console.error('解卦分析错误:', error);
    ElMessage.error(error.response?.data?.detail || error.message || '解卦分析失败');
  } finally {
    isAnalyzing.value = false;
  }
}

function formatLLMResponse(text: string): string {
  if (!text) return '';
  // 将换行符转换为HTML换行
  return text.split('\n').map(line => {
    if (line.trim() === '') return '<br/>';
    return `<p>${line}</p>`;
  }).join('');
}
</script>

<style scoped>
.divination-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
  color: #e5e7eb;
  overflow: hidden;
  position: relative;
}

.main-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.left-panel {
  width: 400px;
  flex-shrink: 0;
  overflow-y: auto;
}

.right-panel {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}

.input-card {
  background: rgba(17, 24, 39, 0.85);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.card-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #3b82f6;
}

.divination-form {
  margin-top: 16px;
}

.coin-toss-section {
  margin: 20px 0;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #9ca3af;
}

.yao-toss-item {
  margin-bottom: 12px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.yao-toss-item.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  transform: scale(1.02);
}

.yao-label {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 8px;
  font-weight: 500;
}

.yao-placeholder {
  padding: 8px 0;
}

.placeholder-text {
  color: #6b7280;
  font-size: 13px;
}

.auto-toss-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.auto-toss-btn {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.toss-hint {
  margin-top: 12px;
  color: #9ca3af;
  font-size: 13px;
}

.yao-results-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.yao-result-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
}

.yao-symbol-large {
  font-size: 32px;
  font-weight: bold;
}

.yao-desc {
  font-size: 14px;
  color: #e5e7eb;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.hexagram-display {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
  padding: 30px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.hexagram-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.hexagram-title {
  font-size: 20px;
  font-weight: bold;
  color: #3b82f6;
  text-align: center;
}

.hexagram-subtitle {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
  margin-top: -8px;
}

.empty-tips {
  margin-top: 30px;
  padding: 20px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  max-width: 500px;
}

.tip-text {
  margin: 8px 0;
  color: #9ca3af;
  font-size: 14px;
  line-height: 1.6;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-card {
  background: rgba(17, 24, 39, 0.85);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.result-card .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #3b82f6;
}

.analysis-content {
  line-height: 1.8;
}

.info-section {
  margin-bottom: 20px;
}

.info-label {
  font-weight: bold;
  color: #9ca3af;
  margin-bottom: 8px;
}

.info-value {
  color: #e5e7eb;
  font-size: 16px;
  line-height: 1.8;
}

.yao-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.yao-item {
  padding: 16px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.yao-item.dong-yao {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.yao-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.yao-name {
  font-weight: bold;
  color: #3b82f6;
  font-size: 16px;
}

.yao-symbol {
  font-size: 24px;
  font-weight: bold;
}

.dong-badge {
  background: #ef4444;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.yao-text {
  color: #d1d5db;
  font-size: 14px;
  line-height: 1.6;
  margin-top: 8px;
}

.llm-card {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.3);
}

.llm-content {
  line-height: 1.8;
}

.llm-text {
  color: #e5e7eb;
  font-size: 15px;
  white-space: pre-wrap;
}

.llm-text :deep(p) {
  margin: 0 0 12px 0;
}

.error-card {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.error-content {
  color: #ef4444;
}

.divination-reminder {
  margin-top: 20px;
}

.reminder-content {
  padding: 16px;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 8px;
  border-left: 4px solid #fbbf24;
}

.reminder-title {
  font-weight: bold;
  color: #fbbf24;
  margin: 0 0 8px 0;
  font-size: 15px;
}

.reminder-text {
  color: #d1d5db;
  font-size: 13px;
  line-height: 1.8;
  margin: 4px 0;
}

/* 滚动条样式 */
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 8px;
}

.left-panel::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: rgba(31, 41, 55, 0.5);
  border-radius: 4px;
}

.left-panel::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.5);
  border-radius: 4px;
}

.left-panel::-webkit-scrollbar-thumb:hover,
.right-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.7);
}

/* ========== 移动端响应式样式 ========== */
@media (max-width: 991.98px) {
  .main-layout {
    gap: 16px;
    padding: 16px;
  }

  .left-panel {
    width: 340px;
  }
}

@media (max-width: 767.98px) {
  .divination-view {
    overflow-y: auto;
  }

  .main-layout {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    min-height: auto;
    height: auto;
  }

  .left-panel {
    width: 100%;
    flex-shrink: 1;
    overflow-y: visible;
  }

  .right-panel {
    min-height: 300px;
  }

  .input-card {
    padding: 16px;
    border-radius: 10px;
  }

  .card-title {
    font-size: 20px;
    margin-bottom: 16px;
  }

  .divination-tips {
    padding: 12px;
    margin-bottom: 16px;
  }

  .tip-item {
    font-size: 13px;
    padding: 8px 0;
  }

  .coin-toss-section {
    margin: 16px 0;
  }

  .section-title {
    font-size: 14px;
    margin-bottom: 12px;
  }

  .yao-toss-item {
    margin-bottom: 16px;
    padding: 12px;
  }

  .yao-label {
    font-size: 13px;
    margin-bottom: 10px;
  }

  .yao-symbol-large {
    font-size: 24px;
  }

  .empty-state {
    min-height: 300px;
    padding: 16px;
  }

  .hexagram-display {
    flex-direction: column;
    gap: 24px;
    padding: 20px;
    margin-bottom: 24px;
  }

  .hexagram-item {
    gap: 8px;
  }

  .hexagram-title {
    font-size: 18px;
  }

  .empty-tips {
    padding: 16px;
    max-width: 100%;
  }

  .result-card {
    padding: 16px;
    border-radius: 10px;
  }

  .result-card .section-title {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .yao-list {
    gap: 12px;
  }

  .yao-item {
    padding: 12px;
  }

  .yao-name {
    font-size: 14px;
  }

  .yao-symbol {
    font-size: 20px;
  }

  .llm-text {
    font-size: 14px;
  }
}

@media (max-width: 575.98px) {
  .main-layout {
    padding: 8px;
    gap: 10px;
  }

  .input-card {
    padding: 12px;
    border-radius: 8px;
  }

  .card-title {
    font-size: 18px;
    margin-bottom: 12px;
  }

  .divination-tips {
    padding: 10px;
  }

  .tip-item {
    font-size: 12px;
    padding: 6px 0;
  }

  .yao-toss-item {
    margin-bottom: 12px;
    padding: 10px;
  }

  .empty-state {
    min-height: 200px;
  }

  .hexagram-display {
    padding: 16px;
    margin-bottom: 16px;
  }

  .result-card {
    padding: 12px;
  }

  .result-card .section-title {
    font-size: 16px;
    margin-bottom: 12px;
  }
}

/* 横屏模式优化 */
@media (max-height: 500px) and (orientation: landscape) {
  .main-layout {
    flex-direction: row;
    gap: 16px;
  }

  .left-panel {
    width: 320px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
  }

  .right-panel {
    flex: 1;
  }
}
</style>

