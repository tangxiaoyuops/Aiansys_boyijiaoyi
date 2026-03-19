<template>
  <div class="bazi-view">
    <div class="main-layout">
      <!-- 左侧输入区域 -->
      <div class="left-panel">
        <div class="input-card">
          <h2 class="card-title">排盘信息</h2>
          <div class="form-hint">请输入公历日期</div>
          <el-form :model="form" label-width="90px" class="bazi-form">
            <el-form-item label="出生年份">
              <el-input-number v-model="form.year" :min="1900" :max="2100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="出生月份">
              <el-input-number v-model="form.month" :min="1" :max="12" style="width: 100%" />
            </el-form-item>
            <el-form-item label="出生日期">
              <el-input-number v-model="form.day" :min="1" :max="31" style="width: 100%" />
            </el-form-item>
            <el-form-item label="出生时辰">
              <el-select v-model="form.hour" placeholder="选择时辰" style="width: 100%">
                <el-option label="子时(23-1)" :value="23" />
                <el-option label="丑时(1-3)" :value="1" />
                <el-option label="寅时(3-5)" :value="3" />
                <el-option label="卯时(5-7)" :value="5" />
                <el-option label="辰时(7-9)" :value="7" />
                <el-option label="巳时(9-11)" :value="9" />
                <el-option label="午时(11-13)" :value="11" />
                <el-option label="未时(13-15)" :value="13" />
                <el-option label="申时(15-17)" :value="15" />
                <el-option label="酉时(17-19)" :value="17" />
                <el-option label="戌时(19-21)" :value="19" />
                <el-option label="亥时(21-23)" :value="21" />
              </el-select>
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-divider />
            <el-form-item label="解读风格">
              <el-select v-model="form.analysis_style" placeholder="选择解读风格" style="width: 100%">
                <el-option
                  v-for="style in analysisStyles"
                  :key="style.value"
                  :label="`${style.name}（${style.description}）`"
                  :value="style.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="分析选项">
              <el-checkbox v-model="form.include_wuxing">五行分析</el-checkbox>
              <el-checkbox v-model="form.include_shishen">十神分析</el-checkbox>
              <el-checkbox v-model="form.include_dayun">大运分析</el-checkbox>
              <el-checkbox v-model="form.include_shensha">神煞分析</el-checkbox>
              <el-checkbox v-model="form.include_llm">AI深度解析</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading || llmLoading" @click="handleAnalyze" style="width: 100%">
                <el-icon><MagicStick /></el-icon>
                开始排盘分析
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <div v-if="!result && !loading" class="empty-state">
          <el-empty description="请填写信息并点击排盘分析" />
        </div>

        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>

        <div v-if="result && !loading" class="result-container">
          <!-- 四柱信息 -->
          <div v-if="result.sizhu" class="result-card">
            <h3 class="section-title">
              <el-icon><Document /></el-icon>
              四柱八字
            </h3>
            <BaziChart :sizhu="result.sizhu" :wuxing-analysis="result.wuxing_analysis" :shishen-analysis="result.shishen_analysis" />
            <div class="sizhu-info">
              <div class="info-item">
                <span class="label">年柱：</span>
                <span class="value">{{ result.sizhu.nian_zhu?.tian_gan }}{{ result.sizhu.nian_zhu?.di_zhi }}</span>
              </div>
              <div class="info-item">
                <span class="label">月柱：</span>
                <span class="value">{{ result.sizhu.yue_zhu?.tian_gan }}{{ result.sizhu.yue_zhu?.di_zhi }}</span>
              </div>
              <div class="info-item">
                <span class="label">日柱：</span>
                <span class="value">{{ result.sizhu.ri_zhu?.tian_gan }}{{ result.sizhu.ri_zhu?.di_zhi }} (日主: {{ result.sizhu.ri_zhu_tiangan }})</span>
              </div>
              <div class="info-item">
                <span class="label">时柱：</span>
                <span class="value">{{ result.sizhu.shi_zhu?.tian_gan }}{{ result.sizhu.shi_zhu?.di_zhi }}</span>
              </div>
              <div v-if="result.sizhu.lunar_year" class="info-item">
                <span class="label">农历：</span>
                <span class="value">
                  {{ result.sizhu.lunar_year }}年{{ result.sizhu.lunar_month }}月{{ result.sizhu.lunar_day }}日
                </span>
              </div>
            </div>
          </div>

          <!-- 五行分析 -->
          <div v-if="result.wuxing_analysis" class="result-card">
            <h3 class="section-title">
              <el-icon><Star /></el-icon>
              五行分析
            </h3>
            <div class="analysis-content">
              <div class="wuxing-stats">
                <div class="wuxing-item">
                  <span class="wuxing-name">金：</span>
                  <span class="wuxing-value">{{ result.wuxing_analysis.wuxing_data?.jin || 0 }}</span>
                </div>
                <div class="wuxing-item">
                  <span class="wuxing-name">木：</span>
                  <span class="wuxing-value">{{ result.wuxing_analysis.wuxing_data?.mu || 0 }}</span>
                </div>
                <div class="wuxing-item">
                  <span class="wuxing-name">水：</span>
                  <span class="wuxing-value">{{ result.wuxing_analysis.wuxing_data?.shui || 0 }}</span>
                </div>
                <div class="wuxing-item">
                  <span class="wuxing-name">火：</span>
                  <span class="wuxing-value">{{ result.wuxing_analysis.wuxing_data?.huo || 0 }}</span>
                </div>
                <div class="wuxing-item">
                  <span class="wuxing-name">土：</span>
                  <span class="wuxing-value">{{ result.wuxing_analysis.wuxing_data?.tu || 0 }}</span>
                </div>
              </div>
              <div class="rizhu-info">
                <span class="label">日主五行：</span>
                <span class="value">{{ result.wuxing_analysis.wuxing_data?.rizhu_wuxing }}</span>
              </div>
            </div>
          </div>

          <!-- 十神分析 -->
          <div v-if="result.shishen_analysis" class="result-card">
            <h3 class="section-title">
              <el-icon><Grid /></el-icon>
              十神分析
            </h3>
            <div class="analysis-content">
              <div class="shishen-table">
                <div class="shishen-row" v-for="(shishen_info, zhu_name) in result.shishen_analysis.shishen_data" :key="zhu_name">
                  <div class="shishen-zhu">{{ zhuNameMap[zhu_name] || zhu_name }}：</div>
                  <div class="shishen-values">
                    <span v-if="shishen_info.gan_shishen" class="shishen-tag">{{ shishen_info.gan_shishen }}</span>
                    <span v-if="shishen_info.zhi_shishen" class="shishen-tag">{{ shishen_info.zhi_shishen }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 大运分析 -->
          <div v-if="result.dayun_analysis" class="result-card">
            <h3 class="section-title">
              <el-icon><Calendar /></el-icon>
              大运分析
            </h3>
            <div class="analysis-content">
              <div class="dayun-list">
                <div v-for="(dayun, index) in result.dayun_analysis.dayun_list" :key="index" class="dayun-item">
                  <span class="dayun-label">第{{ (index as number) + 1 }}步大运：</span>
                  <span class="dayun-value">{{ dayun.gan }}{{ dayun.zhi }}</span>
                  <span class="dayun-age">({{ dayun.start_age }}-{{ dayun.end_age }}岁)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 神煞分析 -->
          <div v-if="result.shensha_analysis" class="result-card">
            <h3 class="section-title">
              <el-icon><Sunny /></el-icon>
              神煞分析
            </h3>
            <div class="analysis-content">
              <div v-if="result.shensha_analysis.shensha_data?.shensha_list?.length > 0" class="shensha-list">
                <div v-for="(shensha, index) in result.shensha_analysis.shensha_data.shensha_list" :key="index" class="shensha-item">
                  <span class="shensha-name">{{ shensha.name }}</span>
                  <span class="shensha-position">({{ zhuNameMap[shensha.position] || shensha.position }})</span>
                  <span :class="['shensha-type', shensha.type === '吉' ? 'type-ji' : 'type-neutral']">{{ shensha.type }}</span>
                </div>
              </div>
              <div v-else class="no-shensha">暂无神煞</div>
            </div>
          </div>

          <!-- LLM深度分析 -->
          <div v-if="form.include_llm || llmLoading || llmText" class="result-card llm-card">
            <h3 class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              AI深度解析
            </h3>
            <div class="llm-content">
              <div v-if="llmLoading" class="llm-progress">
                <el-skeleton :rows="4" animated />
                <div class="llm-progress-text">{{ llmProgress || 'AI 正在深度分析，请稍候…' }}</div>
              </div>
              <div v-else>
                <div v-if="llmText" class="llm-text" v-html="formatLLMResponse(llmText)"></div>
                <div v-else-if="llmError" class="llm-error">
                  <el-alert :title="llmError" type="error" :closable="false" />
                </div>
                <div v-else class="llm-empty">
                  勾选左侧「AI深度解析」后，点击「开始排盘分析」即可生成解读。
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Document, Star, Calendar, Sunny, Grid, ChatLineRound } from '@element-plus/icons-vue';
import BaziChart from '../components/BaziChart.vue';

const loading = ref(false);
const result = ref<any>(null);

const analysisStyles = ref<Array<{ value: string; name: string; description: string }>>([
  {
    value: 'classic',
    name: '传统专业',
    description: '专业术语完整，分析深入全面',
  },
  {
    value: 'simple',
    name: '简明通俗',
    description: '语言生活化，适合零基础用户',
  },
  {
    value: 'life_guide',
    name: '人生指南',
    description: '更关注人生阶段与规划建议',
  },
  {
    value: 'business',
    name: '商业决策',
    description: '偏重事业与财富方向',
  },
  {
    value: 'emotion',
    name: '情感婚恋',
    description: '重点解读感情与婚姻',
  },
]);

const llmLoading = ref(false);
const llmProgress = ref('');
const llmText = ref('');
const llmError = ref('');

const form = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  day: new Date().getDate(),
  hour: 11,
  gender: '男',
  include_wuxing: true,
  include_shishen: true,
  include_dayun: true,
  include_shensha: true,
  include_llm: false,
  analysis_style: 'classic',
});

const zhuNameMap: Record<string, string> = {
  'nian_zhu': '年柱',
  'yue_zhu': '月柱',
  'ri_zhu': '日柱',
  'shi_zhu': '时柱',
};

onMounted(async () => {
  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/styles`);
    const data = await response.json();
    if (response.ok && data.success && Array.isArray(data.styles) && data.styles.length) {
      analysisStyles.value = data.styles;
    }
  } catch (e) {
    console.warn('获取八字风格列表失败，使用本地默认配置');
  }
});

const startLLMStream = async () => {
  llmLoading.value = true;
  llmProgress.value = '';
  llmText.value = '';
  llmError.value = '';

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/llm-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        year: form.year,
        month: form.month,
        day: form.day,
        hour: form.hour,
        gender: form.gender,
        analysis_style: form.analysis_style,
      }),
    });

    if (!response.body) {
      throw new Error('当前浏览器不支持流式输出');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split('\n\n');
      // 最后一段可能是不完整的，留在缓冲区
      buffer = parts.pop() || '';

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data:')) continue;
        const jsonStr = line.slice(5).trim();
        if (!jsonStr) continue;
        try {
          const payload = JSON.parse(jsonStr);
          if (payload.type === 'progress') {
            llmProgress.value = payload.message || '';
          } else if (payload.type === 'content') {
            if (payload.content) {
              llmText.value += payload.content;
            }
          } else if (payload.type === 'done') {
            if (payload.full_content && !llmText.value) {
              llmText.value = payload.full_content;
            }
          } else if (payload.type === 'error') {
            llmError.value = payload.message || 'AI解析失败';
          } else if (payload.type === 'data') {
            // 可选：更新前端结果中的基础数据（目前后端已在主接口返回，可忽略）
          }
        } catch {
          console.warn('解析LLM流式数据失败');
        }
      }
    }
  } catch (error: any) {
    console.error('LLM流式解析失败:', error);
    llmError.value = error.message || 'AI解析失败，请稍后重试';
  } finally {
    llmLoading.value = false;
  }
};

const handleAnalyze = async () => {
  if (!form.year || !form.month || !form.day) {
    ElMessage.warning('请填写完整的出生信息');
    return;
  }

  loading.value = true;
  result.value = null;
  llmText.value = '';
  llmError.value = '';
  llmProgress.value = '';

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/pan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        year: form.year,
        month: form.month,
        day: form.day,
        hour: form.hour,
        gender: form.gender,
        include_wuxing: form.include_wuxing,
        include_shishen: form.include_shishen,
        include_dayun: form.include_dayun,
        include_shensha: form.include_shensha,
        // 基础分析阶段不直接调用 LLM，避免页面长时间卡住
        include_llm: false,
        analysis_style: form.analysis_style,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.detail || data.error || '分析失败');
    }

    result.value = data;
    ElMessage.success('排盘分析完成');

    // 如果用户勾选了 AI 深度解析，则在基础结果加载完成后单独走流式 LLM
    if (form.include_llm) {
      startLLMStream();
    }
  } catch (error: any) {
    console.error('排盘失败:', error);
    ElMessage.error(error.message || '排盘失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const formatLLMResponse = (text: string) => {
  if (!text) return '';
  // 简单的文本格式化，将换行转换为<br>
  return text.replace(/\n/g, '<br>');
};
</script>

<style scoped>
/* 八字古典雅致主题 */
.bazi-view {
  --bazi-bg: linear-gradient(135deg, #FAF8F5 0%, #F5F0E8 50%, #FBF9F6 100%);
  --bazi-surface: rgba(255, 253, 250, 0.92);
  --bazi-surface-dark: rgba(250, 247, 240, 0.95);
  --bazi-primary: #8B6914;
  --bazi-secondary: #D4AF37;
  --bazi-accent: #C17F59;
  --bazi-glow: rgba(212, 175, 55, 0.3);
  --bazi-text: #3D3226;
  --bazi-text-light: #6B5D4D;
  --bazi-border: rgba(139, 90, 43, 0.2);
  --bazi-border-light: rgba(180, 150, 100, 0.25);
  --bazi-shadow: rgba(139, 90, 43, 0.12);
}

.bazi-view {
  height: 100%;
  overflow: auto;
  background: var(--bazi-bg);
  color: var(--bazi-text);
  position: relative;
}

/* 古典纹理背景 */
.bazi-view::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(ellipse at 20% 30%, rgba(212, 175, 55, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(193, 127, 89, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(139, 105, 20, 0.04) 0%, transparent 70%);
  animation: baziPulse 12s ease-in-out infinite;
  z-index: 0;
  pointer-events: none;
}

@keyframes baziPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

.main-layout {
  display: flex;
  gap: 28px;
  padding: 28px;
  max-width: 1600px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.left-panel {
  width: 360px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.right-panel {
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

/* 古典雅致卡片 */
.input-card {
  background: var(--bazi-surface);
  border-radius: 20px;
  padding: 28px;
  border: 1px solid var(--bazi-border-light);
  box-shadow: 
    0 8px 32px var(--bazi-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.input-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--bazi-primary), var(--bazi-secondary), var(--bazi-accent));
  opacity: 0.6;
}

.input-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 16px 48px var(--bazi-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  border-color: var(--bazi-secondary);
}

.card-title {
  margin: 0 0 24px 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--bazi-primary);
  position: relative;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--bazi-border-light);
}

.card-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, var(--bazi-secondary), var(--bazi-accent));
  border-radius: 2px;
}

.form-hint {
  margin-bottom: 16px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%);
  border-left: 3px solid var(--bazi-secondary);
  color: var(--bazi-text-light);
  font-size: 13px;
  border-radius: 0 8px 8px 0;
}

.bazi-form {
  margin-top: 16px;
}

.empty-state,
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--bazi-surface);
  border-radius: 20px;
  border: 1px solid var(--bazi-border-light);
  box-shadow: 0 8px 32px var(--bazi-shadow);
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 结果卡片 */
.result-card {
  background: var(--bazi-surface);
  border-radius: 20px;
  padding: 28px;
  border: 1px solid var(--bazi-border-light);
  box-shadow: 
    0 8px 32px var(--bazi-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  animation: resultEnter 0.6s ease-out;
}

@keyframes resultEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--bazi-primary), var(--bazi-secondary), var(--bazi-accent));
  opacity: 0.5;
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 16px 48px var(--bazi-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  border-color: rgba(212, 175, 55, 0.4);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--bazi-text);
  padding-bottom: 12px;
  border-bottom: 2px solid var(--bazi-border-light);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, var(--bazi-secondary), var(--bazi-accent));
  border-radius: 2px;
}

.sizhu-info {
  margin-top: 16px;
}

.info-item {
  margin-bottom: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.info-item .label {
  font-weight: 600;
  color: var(--bazi-text-light);
  margin-right: 8px;
  min-width: 60px;
}

.info-item .value {
  color: var(--bazi-text);
  font-weight: 500;
}

.analysis-content {
  line-height: 1.8;
  color: var(--bazi-text);
}

/* 五行统计样式 */
.wuxing-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.wuxing-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(212, 175, 55, 0.08);
  border-radius: 20px;
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.wuxing-name {
  font-weight: 600;
  color: var(--bazi-text-light);
}

.wuxing-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--bazi-primary);
}

.rizhu-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--bazi-border-light);
}

/* 十神表格样式 */
.shishen-table {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shishen-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(212, 175, 55, 0.05);
  border-radius: 10px;
  border: 1px solid var(--bazi-border-light);
}

.shishen-zhu {
  width: 60px;
  font-weight: 600;
  color: var(--bazi-text-light);
}

.shishen-values {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.shishen-tag {
  padding: 4px 14px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.08) 100%);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 16px;
  font-size: 13px;
  color: var(--bazi-primary);
  font-weight: 500;
}

/* 大运列表样式 */
.dayun-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dayun-item {
  padding: 12px 16px;
  background: rgba(212, 175, 55, 0.05);
  border-radius: 10px;
  font-size: 14px;
  border: 1px solid var(--bazi-border-light);
  transition: all 0.3s ease;
}

.dayun-item:hover {
  background: rgba(212, 175, 55, 0.1);
  border-color: rgba(212, 175, 55, 0.3);
}

.dayun-label {
  font-weight: 600;
  color: var(--bazi-text-light);
  margin-right: 8px;
}

.dayun-value {
  font-weight: 700;
  color: var(--bazi-primary);
  margin-right: 8px;
}

.dayun-age {
  color: var(--bazi-text-light);
}

/* 神煞列表样式 */
.shensha-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shensha-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(212, 175, 55, 0.05);
  border-radius: 10px;
  border: 1px solid var(--bazi-border-light);
}

.shensha-name {
  font-weight: 600;
  color: var(--bazi-text);
}

.shensha-position {
  color: var(--bazi-text-light);
  font-size: 13px;
}

.shensha-type {
  margin-left: auto;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.type-ji {
  background: linear-gradient(135deg, rgba(34, 139, 34, 0.15) 0%, rgba(34, 139, 34, 0.08) 100%);
  color: #228B22;
  border: 1px solid rgba(34, 139, 34, 0.3);
}

.type-neutral {
  background: linear-gradient(135deg, rgba(193, 127, 89, 0.15) 0%, rgba(193, 127, 89, 0.08) 100%);
  color: #A0522D;
  border: 1px solid rgba(193, 127, 89, 0.3);
}

.no-shensha {
  color: var(--bazi-text-light);
  text-align: center;
  padding: 24px;
  background: rgba(212, 175, 55, 0.03);
  border-radius: 10px;
}

/* LLM分析卡片 */
.llm-card {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.08) 0%, rgba(193, 127, 89, 0.05) 100%);
  border: 2px solid rgba(212, 175, 55, 0.25);
  box-shadow: 
    0 8px 32px var(--bazi-shadow),
    0 0 40px rgba(212, 175, 55, 0.1);
}

.llm-card .section-title {
  color: var(--bazi-text);
}

.llm-content {
  margin-top: 16px;
}

.llm-text {
  line-height: 1.9;
  color: var(--bazi-text);
  font-size: 15px;
}

.llm-error {
  margin-top: 16px;
}

.llm-progress {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.llm-progress-text {
  font-size: 13px;
  color: var(--bazi-text-light);
}

.llm-empty {
  font-size: 13px;
  color: var(--bazi-text-light);
}
</style>


