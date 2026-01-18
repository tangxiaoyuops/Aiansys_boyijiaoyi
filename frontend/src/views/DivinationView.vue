<template>
  <div class="divination-view">
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
              <div
                v-for="(yaoResult, index) in yaoResults"
                :key="index"
                class="yao-toss-item"
              >
                <div class="yao-label">第{{ index + 1 }}爻（{{ getYaoName(index) }}爻）</div>
                <CoinToss
                  v-if="!yaoResult"
                  @result="handleYaoResult(index, $event)"
                  :disabled="isAnalyzing"
                />
                <div v-else class="yao-result-display">
                  <span class="yao-symbol-large">{{ yaoResult.symbol }}</span>
                  <span class="yao-desc">{{ yaoResult.description }}</span>
                </div>
              </div>
            </div>
            
            <el-divider />
            
            <!-- 操作按钮 -->
            <el-form-item>
              <el-button type="warning" @click="handleReset" :disabled="isAnalyzing" style="margin-right: 10px">
                重新摇卦
              </el-button>
              <el-button
                type="primary"
                :loading="isAnalyzing"
                :disabled="!canAnalyze"
                @click="handleAnalyze"
                style="width: calc(100% - 120px)"
              >
                <el-icon><MagicStick /></el-icon>
                开始解卦
              </el-button>
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
        <div v-if="!result && !isAnalyzing" class="empty-state">
          <!-- 谦卦和泰卦展示 -->
          <div class="hexagram-display">
            <div class="hexagram-item">
              <div class="hexagram-title">谦卦</div>
              <HexagramChart :hexagram-data="qianHexagram" :size="180" />
              <div class="hexagram-subtitle">地山谦</div>
            </div>
            <div class="hexagram-item">
              <div class="hexagram-title">泰卦</div>
              <HexagramChart :hexagram-data="taiHexagram" :size="180" />
              <div class="hexagram-subtitle">地天泰</div>
            </div>
          </div>
          <el-empty description="请填写问题并摇卦，然后点击开始解卦" />
          <div class="empty-tips">
            <p class="tip-text">💡 提示：</p>
            <p class="tip-text">• 事在人为，卜卦戒为先</p>
            <p class="tip-text">• 顺天道自然，元亨利贞</p>
            <p class="tip-text">• 卦象仅供参考，决策需谨慎</p>
          </div>
        </div>
        
        <div v-if="isAnalyzing" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>
        
        <div v-if="result && !isAnalyzing" class="result-container">
          <!-- 卦象显示 -->
          <div v-if="result.hexagram" class="result-card">
            <h3 class="section-title">
              <el-icon><Grid /></el-icon>
              卦象
            </h3>
            <HexagramChart :hexagram-data="result.hexagram" :size="400" />
          </div>
          
          <!-- 本卦信息 -->
          <div v-if="result.hexagram?.ben_hexagram" class="result-card">
            <h3 class="section-title">
              <el-icon><Document /></el-icon>
              本卦：{{ result.hexagram.ben_hexagram.full_name }}
            </h3>
            <div class="analysis-content">
              <div class="info-section">
                <div class="info-label">卦辞：</div>
                <div class="info-value">{{ result.hexagram.ben_hexagram.guaci }}</div>
              </div>
              
              <div class="yao-list">
                <div
                  v-for="(yao, index) in result.hexagram.yaos"
                  :key="index"
                  :class="['yao-item', { 'dong-yao': yao.is_dong }]"
                >
                  <div class="yao-header">
                    <span class="yao-name">{{ getYaoName(index) }}爻</span>
                    <span class="yao-symbol">{{ yao.symbol }}</span>
                    <span v-if="yao.is_dong" class="dong-badge">动爻</span>
                  </div>
                  <div v-if="result.hexagram.ben_hexagram.yaoci && result.hexagram.ben_hexagram.yaoci[String(index + 1)]" class="yao-text">
                    {{ result.hexagram.ben_hexagram.yaoci[String(index + 1)] }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 变卦信息 -->
          <div v-if="result.hexagram?.bian_hexagram" class="result-card">
            <h3 class="section-title">
              <el-icon><RefreshRight /></el-icon>
              变卦：{{ result.hexagram.bian_hexagram.full_name }}
            </h3>
            <div class="analysis-content">
              <div class="info-section">
                <div class="info-label">变卦卦辞：</div>
                <div class="info-value">{{ result.hexagram.bian_hexagram.guaci }}</div>
              </div>
            </div>
          </div>
          
          <!-- AI深度分析 -->
          <div v-if="result.llm_analysis?.response" class="result-card llm-card">
            <h3 class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              AI深度解析
            </h3>
            <div class="llm-content">
              <div class="llm-text" v-html="formatLLMResponse(result.llm_analysis.response)"></div>
            </div>
            <!-- 解卦提示语 -->
            <div class="divination-reminder">
              <el-divider />
              <div class="reminder-content">
                <p class="reminder-title">📜 解卦提醒</p>
                <p class="reminder-text">事在人为，卜卦戒为先；顺天道自然，元亨利贞。</p>
                <p class="reminder-text">卦象仅供参考，重要决策需结合实际情况，谨慎为之。</p>
              </div>
            </div>
          </div>
          
          <!-- AI分析错误 -->
          <div v-if="result.llm_analysis?.error" class="result-card error-card">
            <h3 class="section-title">
              <el-icon><Warning /></el-icon>
              AI分析错误
            </h3>
            <div class="error-content">
              <p>{{ result.llm_analysis.error }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Document, Grid, ChatLineRound, RefreshRight, Warning, InfoFilled } from '@element-plus/icons-vue';
import api from '../api';
import CoinToss from '../components/CoinToss.vue';
import HexagramChart from '../components/HexagramChart.vue';

const isAnalyzing = ref(false);
const result = ref<any>(null);

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

const yaoNames = ['初', '二', '三', '四', '五', '上'];

function getYaoName(index: number): string {
  return yaoNames[index];
}

function handleYaoResult(index: number, yaoData: any) {
  yaoResults.value[index] = {
    symbol: yaoData.yaoType.includes('阳') ? '⚊' : '⚋',
    description: yaoData.yaoType,
    yaoNumber: yaoData.yaoNumber,
    coins: yaoData.coins,
  };
}

function handleReset() {
  yaoResults.value = Array(6).fill(null);
  result.value = null;
  form.question = '';
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
  background: #111827;
  color: #e5e7eb;
  overflow: hidden;
}

.main-layout {
  display: flex;
  flex: 1;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
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
  background: rgba(31, 41, 55, 0.8);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.yao-label {
  font-size: 14px;
  color: #9ca3af;
  margin-bottom: 12px;
  font-weight: 500;
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
  background: rgba(31, 41, 55, 0.8);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
</style>

