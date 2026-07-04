<template>
  <div class="selection-view">
    <div class="view-header">
      <h1 class="view-title">博弈交易选股策略</h1>
      <p class="view-desc">基于博弈理论自动识别买点,智能筛选推荐股票</p>
    </div>

    <!-- 配置选择 -->
    <div class="config-section">
      <div class="section-title">
        <span class="title-icon">⚙️</span>
        策略配置
      </div>
      
      <div class="config-options">
        <div 
          class="config-option"
          :class="{ active: configType === 'standard' }"
          @click="configType = 'standard'"
        >
          <div class="option-header">
            <span class="option-icon">📊</span>
            <span class="option-title">标准配置</span>
          </div>
          <div class="option-desc">平衡风险和收益,适合大多数投资者</div>
          <div class="option-params">
            <div class="param">最大持仓: 10只</div>
            <div class="param">单只仓位: ≤20%</div>
            <div class="param">止损: 8%</div>
          </div>
        </div>

        <div 
          class="config-option"
          :class="{ active: configType === 'conservative' }"
          @click="configType = 'conservative'"
        >
          <div class="option-header">
            <span class="option-icon">🛡️</span>
            <span class="option-title">保守型配置</span>
          </div>
          <div class="option-desc">更低风险,适合稳健型投资者</div>
          <div class="option-params">
            <div class="param">最大持仓: 5只</div>
            <div class="param">单只仓位: ≤15%</div>
            <div class="param">止损: 5%</div>
          </div>
        </div>

        <div 
          class="config-option"
          :class="{ active: configType === 'aggressive' }"
          @click="configType = 'aggressive'"
        >
          <div class="option-header">
            <span class="option-icon">⚡</span>
            <span class="option-title">激进型配置</span>
          </div>
          <div class="option-desc">更高风险,适合激进型投资者</div>
          <div class="option-params">
            <div class="param">最大持仓: 15只</div>
            <div class="param">单只仓位: ≤25%</div>
            <div class="param">止损: 10%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 股票池选择 -->
    <div class="pool-section">
      <div class="section-title">
        <span class="title-icon">📦</span>
        股票池
        <span class="title-badge">必选</span>
      </div>

      <div class="pool-helper">
        <div class="helper-icon">💡</div>
        <div class="helper-content">
          <div class="helper-title">如何设置股票池?</div>
          <div class="helper-text">
            手动输入股票代码,或选择预设股票池。建议分析5-30只股票,获得更好的选股效果。
          </div>
        </div>
      </div>

      <div class="pool-tabs">
        <button 
          class="pool-tab"
          :class="{ active: poolMode === 'manual' }"
          @click="poolMode = 'manual'"
        >
          手动输入
        </button>
        <button 
          class="pool-tab"
          :class="{ active: poolMode === 'preset' }"
          @click="poolMode = 'preset'"
        >
          预设股票池
        </button>
      </div>

      <!-- 手动输入 -->
      <div v-if="poolMode === 'manual'" class="pool-manual">
        <div class="input-wrapper">
          <textarea 
            v-model="manualCodes"
            placeholder="输入股票代码,多个代码用逗号或换行分隔&#10;例如: 600519, 000001, 600036&#10;&#10;💡 提示: 建议输入5-20只股票进行分析"
            rows="4"
            class="code-input"
          ></textarea>
          <div class="input-tip">
            <span class="tip-text">已输入 {{ parsedCodes.length }} 个股票代码</span>
            <button v-if="parsedCodes.length === 0" class="quick-fill-btn" @click="fillDefaultCodes">
              快速填充测试股票
            </button>
          </div>
        </div>
      </div>

      <!-- 预设股票池 -->
      <div v-if="poolMode === 'preset'" class="pool-preset">
        <div class="preset-options">
          <div 
            class="preset-option"
            :class="{ active: selectedPool === 'hs300' }"
            @click="selectPool('hs300')"
          >
            <span class="preset-icon">📈</span>
            <span class="preset-name">沪深300</span>
            <span class="preset-count">300只</span>
          </div>

          <div 
            class="preset-option"
            :class="{ active: selectedPool === 'custom' }"
            @click="selectPool('custom')"
          >
            <span class="preset-icon">⭐</span>
            <span class="preset-name">自选股</span>
            <span class="preset-count">{{ customPoolCodes.length }}只</span>
          </div>

          <div 
            class="preset-option"
            :class="{ active: selectedPool === 'test' }"
            @click="selectPool('test')"
          >
            <span class="preset-icon">🧪</span>
            <span class="preset-name">测试股票池</span>
            <span class="preset-count">10只</span>
          </div>
        </div>

        <div v-if="selectedPool" class="pool-preview">
          <div class="preview-title">股票池预览</div>
          <div class="preview-codes">
            <span v-for="code in previewCodes" :key="code" class="code-tag">
              {{ code }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-section">
      <button 
        class="action-btn primary"
        :disabled="isLoading || stockCodes.length === 0"
        @click="runSelection"
      >
        <span v-if="isLoading" class="loading-icon">⏳</span>
        <span v-else class="btn-icon">🔍</span>
        <span class="btn-text">{{ isLoading ? '正在选股...' : '开始选股' }}</span>
      </button>

      <button 
        class="action-btn secondary"
        :disabled="isLoading"
        @click="clearResult"
      >
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">清空结果</span>
      </button>
    </div>

    <!-- 选股结果 -->
    <div v-if="selectionResult" class="result-section">
      <div class="section-title">
        <span class="title-icon">✨</span>
        选股结果
        <span class="result-summary">
          扫描 {{ selectionResult.total_candidates }}只 → 
          合格 {{ selectionResult.qualified_candidates }}只 → 
          推荐 {{ selectionResult.top_candidates.length }}只
        </span>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-value">{{ selectionResult.total_candidates }}</div>
          <div class="stat-label">扫描股票</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ selectionResult.qualified_candidates }}</div>
          <div class="stat-label">合格股票</div>
        </div>
        <div class="stat-card highlight">
          <div class="stat-value">{{ selectionResult.top_candidates.length }}</div>
          <div class="stat-label">推荐股票</div>
        </div>
      </div>

      <!-- 无推荐提示 -->
      <div v-if="selectionResult.top_candidates.length === 0" class="no-result-tip">
        <div class="tip-icon">📊</div>
        <div class="tip-title">暂无推荐股票</div>
        <div class="tip-desc">
          当前股票池中没有符合买点条件的股票,建议:
        </div>
        <div class="tip-suggestions">
          <div class="suggestion-item">• 扩大股票池范围(建议10-30只股票)</div>
          <div class="suggestion-item">• 尝试不同的配置类型(保守型/激进型)</div>
          <div class="suggestion-item">• 等待更好的买入时机</div>
          <div class="suggestion-item">• 关注大盘环境,顺势而为</div>
        </div>
      </div>

      <!-- 推荐股票列表 -->
      <div v-if="selectionResult.top_candidates.length > 0" class="candidates-list">
        <div 
          v-for="(candidate, index) in selectionResult.top_candidates"
          :key="candidate.code"
          class="candidate-card"
          :class="{ expanded: expandedCandidate === candidate.code }"
          @click="toggleCandidate(candidate.code)"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="card-rank">{{ index + 1 }}</div>
            <div class="card-info">
              <div class="card-name">{{ candidate.name }}</div>
              <div class="card-code">{{ candidate.code }}</div>
            </div>
            <div class="card-score">
              <div class="score-value">{{ candidate.overall_score.toFixed(1) }}</div>
              <div class="score-label">综合评分</div>
            </div>
            <div class="card-badge" :class="`stage-${candidate.stage}`">
              {{ candidate.stage }}阶段
            </div>
          </div>

          <!-- 卡片简要信息 -->
          <div class="card-summary">
            <div class="summary-item">
              <span class="item-label">买入信号:</span>
              <span class="item-value">{{ candidate.buy_signals ? candidate.buy_signals.length : 0 }}个</span>
            </div>
            <div class="summary-item">
              <span class="item-label">当前价格:</span>
              <span class="item-value price">{{ candidate.current_price.toFixed(2) }}</span>
            </div>
            <div class="summary-item">
              <span class="item-label">建议仓位:</span>
              <span class="item-value">{{ (candidate.suggested_position_pct * 100).toFixed(1) }}%</span>
            </div>
            <div class="summary-item">
              <span class="item-label">建议买入:</span>
              <span class="item-value">{{ candidate.suggested_shares }}股</span>
            </div>
          </div>

          <!-- 卡片详细信息 -->
          <div v-if="expandedCandidate === candidate.code" class="card-details">
            <div class="details-title">详细信息</div>
            
            <!-- 买点信息 -->
            <div class="details-section">
              <div class="section-label">买入信号列表</div>
              <div v-if="candidate.buy_signals && candidate.buy_signals.length > 0" class="signals-list">
                <div 
                  v-for="(signal, sigIdx) in candidate.buy_signals.slice(0, 5)" 
                  :key="sigIdx"
                  class="signal-item"
                >
                  <div class="signal-header">
                    <span class="signal-date">{{ signal.date }}</span>
                    <span class="signal-price">价格: {{ signal.price.toFixed(2) }}</span>
                  </div>
                  <div class="signal-reason">{{ signal.reason }}</div>
                </div>
              </div>
              <div v-else class="no-signals">暂无买入信号</div>
            </div>

            <!-- 最新买入信号 -->
            <div v-if="candidate.best_signal" class="details-section">
              <div class="section-label">最新买入信号</div>
              <div class="best-signal-info">
                <div class="info-row">
                  <span class="row-label">信号日期:</span>
                  <span class="row-value">{{ candidate.best_signal.date }}</span>
                </div>
                <div class="info-row">
                  <span class="row-label">买入价格:</span>
                  <span class="row-value">{{ candidate.best_signal.price.toFixed(2) }}</span>
                </div>
                <div class="info-row">
                  <span class="row-label">买入理由:</span>
                  <span class="row-value">{{ candidate.best_signal.reason }}</span>
                </div>
              </div>
            </div>

            <!-- 仓位建议 -->
            <div class="details-section">
              <div class="section-label">仓位建议</div>
              <div class="position-info">
                <div class="position-item">
                  <span class="item-label">建议仓位:</span>
                  <span class="item-value">{{ (candidate.suggested_position_pct * 100).toFixed(1) }}%</span>
                </div>
                <div class="position-item">
                  <span class="item-label">建议股数:</span>
                  <span class="item-value">{{ candidate.suggested_shares }}股</span>
                </div>
                <div class="position-item">
                  <span class="item-label">建议金额:</span>
                  <span class="item-value">{{ candidate.suggested_amount.toFixed(2) }}元</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="selectionResult.errors && selectionResult.errors.length > 0" class="errors-section">
        <div class="section-title">
          <span class="title-icon">⚠️</span>
          错误信息
        </div>
        <div class="error-list">
          <div v-for="error in selectionResult.errors" :key="error.code" class="error-item">
            <span class="error-code">{{ error.code }}</span>
            <span class="error-message">{{ error.error }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 单只股票分析 -->
    <div class="analysis-section">
      <div class="section-title">
        <span class="title-icon">🔎</span>
        单只股票分析
      </div>

      <div class="analysis-input">
        <input 
          v-model="analysisCode"
          placeholder="输入股票代码,例如: 600519"
          class="code-input-small"
        />
        <button 
          class="analysis-btn"
          :disabled="!analysisCode || isAnalyzing"
          @click="analyzeStock"
        >
          <span v-if="isAnalyzing">分析中...</span>
          <span v-else>分析</span>
        </button>
      </div>

      <!-- 分析结果 -->
      <div v-if="analysisResult" class="analysis-result">
        <div class="result-header">
          <div class="stock-name">{{ analysisResult.name }}</div>
          <div class="stock-code">{{ analysisResult.code }}</div>
          <div class="stock-stage" :class="`stage-${analysisResult.stage}`">
            {{ analysisResult.stage_name }}
          </div>
        </div>

        <!-- K线图展示 -->
        <div v-if="analysisResult.kline_data && analysisResult.kline_data.length > 0" class="kline-section">
          <SelectionKlineChart
            :kline-data="analysisResult.kline_data"
            :buy-signals="analysisResult.buy_signals"
          />
        </div>

        <div class="buy-points-list">
          <div class="list-title">
            检测到 {{ analysisResult.buy_signals.length }} 个买入信号
          </div>
          
          <div 
            v-for="(signal, index) in analysisResult.buy_signals"
            :key="index"
            class="buy-point-card"
          >
            <div class="point-header">
              <span class="point-type">买入信号 #{{ index + 1 }}</span>
              <span class="point-date">{{ signal.date }}</span>
            </div>
            <div class="point-info">
              <div class="info-item">
                <span class="label">价格:</span>
                <span class="value">{{ signal.price.toFixed(2) }}</span>
              </div>
              <div class="info-item">
                <span class="label">评分:</span>
                <span class="value">{{ signal.score.toFixed(1) }}</span>
              </div>
              <div class="info-item">
                <span class="label">置信度:</span>
                <span class="value">{{ (signal.confidence * 100).toFixed(0) }}%</span>
              </div>
            </div>
            <div class="point-reason">{{ signal.reasoning }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用提示 -->
    <div class="tips-section">
      <div class="section-title">
        <span class="title-icon">💡</span>
        使用提示
      </div>
      <div class="tips-list">
        <div class="tip-item">
          <span class="tip-icon">1️⃣</span>
          <span class="tip-text">选择适合自己风险偏好的配置类型</span>
        </div>
        <div class="tip-item">
          <span class="tip-icon">2️⃣</span>
          <span class="tip-text">输入或选择要分析的股票池</span>
        </div>
        <div class="tip-item">
          <span class="tip-icon">3️⃣</span>
          <span class="tip-text">点击"开始选股"执行选股策略</span>
        </div>
        <div class="tip-item">
          <span class="tip-icon">4️⃣</span>
          <span class="tip-text">查看推荐股票列表和详细信息</span>
        </div>
        <div class="tip-item">
          <span class="tip-icon">5️⃣</span>
          <span class="tip-text">点击股票卡片展开查看完整分析</span>
        </div>
        <div class="tip-item warning">
          <span class="tip-icon">⚠️</span>
          <span class="tip-text">本系统仅供参考,不构成投资建议。股市有风险,投资需谨慎!</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import SelectionKlineChart from '../components/charts/SelectionKlineChart.vue';

// === 状态管理 ===
const configType = ref('standard'); // 配置类型
const poolMode = ref('manual'); // 股票池模式
const manualCodes = ref(''); // 手动输入的代码
const selectedPool = ref(''); // 选中的预设股票池

const isLoading = ref(false); // 选股加载状态
const isAnalyzing = ref(false); // 分析加载状态
const expandedCandidate = ref(''); // 展开的候选股票

const selectionResult = ref<any>(null); // 选股结果
const analysisCode = ref(''); // 分析的股票代码
const analysisResult = ref<any>(null); // 分析结果

// === 预设股票池 ===
const customPoolCodes = ref(['600519', '000001', '600036', '000333', '600030']);
const testPoolCodes = ['600519', '000001', '600036', '000333', '600030', '000651', '601318', '600000', '000002', '600016'];

// === 计算属性 ===
// 解析手动输入的代码
const parsedCodes = computed(() => {
  if (!manualCodes.value) return [];
  
  // 支持逗号、空格、换行分隔
  const codes = manualCodes.value
    .split(/[,\s\n]+/)
    .map(code => code.trim())
    .filter(code => code.length > 0);
  
  return codes;
});

// 最终要分析的股票代码
const stockCodes = computed(() => {
  if (poolMode.value === 'manual') {
    return parsedCodes.value;
  } else if (poolMode.value === 'preset') {
    if (selectedPool.value === 'hs300') {
      // 沪深300暂时返回测试数据(实际应该从API获取)
      return testPoolCodes;
    } else if (selectedPool.value === 'custom') {
      return customPoolCodes.value;
    } else if (selectedPool.value === 'test') {
      return testPoolCodes;
    }
  }
  return [];
});

// 预览的股票代码(最多显示20个)
const previewCodes = computed(() => {
  return stockCodes.value.slice(0, 20);
});

// === 方法 ===
// 选择预设股票池
const selectPool = (pool: string) => {
  selectedPool.value = pool;
};

// 快速填充默认测试股票
const fillDefaultCodes = () => {
  manualCodes.value = testPoolCodes.join(', ');
  ElMessage.success('已填充10只测试股票');
};

// 执行选股
const runSelection = async () => {
  if (stockCodes.value.length === 0) {
    ElMessage.warning('请先输入或选择股票代码');
    return;
  }

  isLoading.value = true;
  selectionResult.value = null;

  try {
    // 准备策略参数
    const strategyParams: any = {
      max_stocks: configType === 'conservative' ? 5 : configType === 'aggressive' ? 15 : 10,
      max_position_per_stock: configType === 'conservative' ? 0.15 : configType === 'aggressive' ? 0.25 : 0.2,
      initial_capital: 1000000,
      data_days: 250
    };

    const response = await axios.post('/api/selection/select', {
      codes: stockCodes.value,
      strategy_params: strategyParams
    });

    if (response.data.success) {
      selectionResult.value = response.data;
      ElMessage.success(`选股完成!推荐${response.data.top_candidates.length}只股票`);
    } else {
      ElMessage.error('选股失败');
    }
  } catch (error: any) {
    console.error('选股失败:', error);
    ElMessage.error(error.response?.data?.detail || '选股失败,请稍后重试');
  } finally {
    isLoading.value = false;
  }
};

// 分析单只股票
const analyzeStock = async () => {
  if (!analysisCode.value) {
    ElMessage.warning('请输入股票代码');
    return;
  }

  isAnalyzing.value = true;
  analysisResult.value = null;

  try {
    const response = await axios.post('/api/selection/analyze', {
      code: analysisCode.value.trim(),
      days: 250
    });

    if (response.data.success) {
      analysisResult.value = response.data;
      ElMessage.success(`分析完成!检测到${response.data.buy_signals.length}个买点`);
    } else {
      ElMessage.error('分析失败');
    }
  } catch (error: any) {
    console.error('分析失败:', error);
    ElMessage.error(error.response?.data?.detail || '分析失败,请稍后重试');
  } finally {
    isAnalyzing.value = false;
  }
};

// 清空结果
const clearResult = () => {
  selectionResult.value = null;
  expandedCandidate.value = '';
};

// 展开/收起候选股票详情
const toggleCandidate = (code: string) => {
  if (expandedCandidate.value === code) {
    expandedCandidate.value = '';
  } else {
    expandedCandidate.value = code;
  }
};

// 格式化买点类型
const formatBuyType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'panic_point': '恐慌点买入',
    'lowest_after_panic': '恐慌点后最低价',
    'o_point': 'O点买入',
    'washout_end': '洗盘结束买入'
  };
  return typeMap[type] || type;
};

// 格式化筛选条件名称
const formatFilterName = (name: string): string => {
  const nameMap: Record<string, string> = {
    'stage_filter': '阶段过滤',
    'trend_filter': '趋势过滤',
    'confidence_filter': '置信度过滤',
    'data_filter': '数据完整性',
    'emotion_filter': '情绪比例'
  };
  return nameMap[name] || name;
};
</script>

<style scoped>
.selection-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* === 视图头部 === */
.view-header {
  margin-bottom: 32px;
  text-align: center;
}

.view-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.view-desc {
  font-size: 14px;
  color: #6b7280;
}

/* === 区块标题 === */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.title-icon {
  font-size: 20px;
}

.title-badge {
  padding: 4px 8px;
  background: #ef4444;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
}

.pool-helper {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #eff6ff;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  margin-bottom: 16px;
}

.helper-icon {
  font-size: 24px;
}

.helper-content {
  flex: 1;
}

.helper-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 4px;
}

.helper-text {
  font-size: 13px;
  color: #3b82f6;
}

/* === 配置选择 === */
.config-section {
  margin-bottom: 32px;
}

.config-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.config-option {
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.config-option:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.config-option.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.option-icon {
  font-size: 24px;
}

.option-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.option-desc {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 12px;
}

.option-params {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.param {
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 4px;
  font-size: 12px;
  color: #4b5563;
}

/* === 股票池选择 === */
.pool-section {
  margin-bottom: 32px;
}

.pool-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.pool-tab {
  padding: 8px 16px;
  border: none;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pool-tab:hover {
  background: #e5e7eb;
}

.pool-tab.active {
  background: #3b82f6;
  color: white;
}

.pool-manual .input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.code-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
}

.code-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.input-tip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #6b7280;
}

.quick-fill-btn {
  padding: 4px 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-fill-btn:hover {
  background: #2563eb;
}

.pool-preset .preset-options {
  display: flex;
  gap: 12px;
}

.preset-option {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.preset-option:hover {
  background: #f9fafb;
}

.preset-option.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.preset-icon {
  font-size: 24px;
}

.preset-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.preset-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.pool-preview {
  margin-top: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.preview-codes {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.code-tag {
  padding: 4px 8px;
  background: #e5e7eb;
  border-radius: 4px;
  font-size: 12px;
  color: #4b5563;
}

/* === 操作按钮 === */
.action-section {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #3b82f6;
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: #2563eb;
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #6b7280;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon, .loading-icon {
  font-size: 18px;
}

/* === 选股结果 === */
.result-section {
  margin-bottom: 32px;
}

.result-summary {
  font-size: 14px;
  color: #6b7280;
  margin-left: 8px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
}

.stat-card.highlight {
  background: #eff6ff;
  border-color: #3b82f6;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-card.highlight .stat-value {
  color: #3b82f6;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.candidate-card {
  padding: 20px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.candidate-card:hover {
  border-color: #d1d5db;
}

.candidate-card.expanded {
  border-color: #3b82f6;
  background: #eff6ff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.card-rank {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #3b82f6;
}

.card-info {
  flex: 1;
}

.card-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.card-code {
  font-size: 14px;
  color: #6b7280;
}

.card-score {
  text-align: right;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.score-label {
  font-size: 12px;
  color: #6b7280;
}

.card-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.card-badge.stage-1 {
  background: #dbeafe;
  color: #1e40af;
}

.card-badge.stage-2 {
  background: #d1fae5;
  color: #065f46;
}

.card-badge.stage-5 {
  background: #fee2e2;
  color: #991b1b;
}

.card-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.summary-item {
  display: flex;
  gap: 8px;
}

.item-label {
  font-size: 13px;
  color: #6b7280;
}

.item-value {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.item-value.price {
  color: #3b82f6;
}

.card-details {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.details-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.details-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.buy-point-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  gap: 8px;
}

.row-label {
  font-size: 13px;
  color: #6b7280;
}

.row-value {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.buy-reason {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.reason-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.reason-text {
  font-size: 13px;
  color: #374151;
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-name {
  width: 80px;
  font-size: 13px;
  color: #6b7280;
}

.item-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
}

.bar-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s;
}

.position-info {
  display: flex;
  gap: 16px;
}

.position-item {
  display: flex;
  gap: 8px;
}

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
}

.filter-item.passed {
  background: #d1fae5;
}

.filter-icon {
  font-size: 16px;
}

.filter-name {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.filter-reason {
  font-size: 12px;
  color: #6b7280;
}

.errors-section {
  margin-top: 24px;
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-item {
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  display: flex;
  gap: 12px;
}

.error-code {
  font-weight: 600;
  color: #991b1b;
}

.error-message {
  color: #7f1d1d;
}

/* === 无推荐提示 === */
.no-result-tip {
  padding: 40px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  text-align: center;
}

.tip-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.tip-title {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.tip-desc {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 20px;
}

.tip-suggestions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.suggestion-item {
  font-size: 13px;
  color: #4b5563;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
}

.signals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signal-item {
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.signal-date {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.signal-price {
  font-size: 13px;
  color: #6b7280;
}

.signal-reason {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
}

.no-signals {
  padding: 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}

.best-signal-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* === 单只股票分析 === */
.analysis-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #f9fafb;
  border-radius: 12px;
}

.analysis-input {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.code-input-small {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.code-input-small:focus {
  outline: none;
  border-color: #3b82f6;
}

.analysis-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.analysis-btn:hover:not(:disabled) {
  background: #2563eb;
}

.analysis-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analysis-result {
  margin-top: 24px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stock-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.stock-code {
  font-size: 14px;
  color: #6b7280;
}

.stock-stage {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

  .kline-section {
    margin-top: 24px;
    margin-bottom: 24px;
  }

  .buy-points-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .list-title {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 12px;
  }

.buy-point-card {
  padding: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.point-type {
  font-size: 15px;
  font-weight: 600;
  color: #3b82f6;
}

.point-score {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.point-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  gap: 4px;
}

.label {
  font-size: 13px;
  color: #6b7280;
}

.value {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.point-reason {
  font-size: 13px;
  color: #374151;
  padding: 8px;
  background: #f9fafb;
  border-radius: 4px;
}

/* === 使用提示 === */
.tips-section {
  padding: 24px;
  background: #fef3c7;
  border-radius: 12px;
  border: 1px solid #fcd34d;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip-icon {
  font-size: 16px;
}

.tip-text {
  font-size: 14px;
  color: #78350f;
}

.tip-item.warning {
  font-weight: 600;
}

/* === 响应式 === */
@media (max-width: 767px) {
  .selection-view {
    padding: 16px;
  }

  .view-title {
    font-size: 24px;
  }

  .config-options {
    grid-template-columns: 1fr;
  }

  .pool-preset .preset-options {
    flex-direction: column;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .card-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-header {
    flex-wrap: wrap;
  }

  .card-score {
    order: 4;
    width: 100%;
    text-align: left;
    margin-top: 8px;
  }
}
</style>