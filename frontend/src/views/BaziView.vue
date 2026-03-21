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
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleAnalyze" style="width: 100%">
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

        <div v-if="result && !loading" class="result-wrapper">
          <!-- 上方：基础分析结果 -->
          <div class="basic-result-section" :style="{ height: basicResultHeight + 'px' }">
            <!-- 四柱信息 -->
            <div v-if="result.sizhu" class="result-card compact-card">
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
                  <span class="value">{{ result.sizhu.ri_zhu?.tian_gan }}{{ result.sizhu.ri_zhu?.di_zhi }} (日主)</span>
                </div>
                <div class="info-item">
                  <span class="label">时柱：</span>
                  <span class="value">{{ result.sizhu.shi_zhu?.tian_gan }}{{ result.sizhu.shi_zhu?.di_zhi }}</span>
                </div>
              </div>
            </div>

            <!-- 五行+十神+神煞 横向排列 -->
            <div class="analysis-row">
              <!-- 五行分析 -->
              <div v-if="result.wuxing_analysis" class="result-card compact-card">
                <h3 class="section-title">
                  <el-icon><Star /></el-icon>
                  五行
                </h3>
                <div class="wuxing-mini">
                  <span v-for="(count, name) in getWuxingData(result.wuxing_analysis)" :key="name" class="wx-item">
                    {{ name }}: {{ count }}
                  </span>
                </div>
              </div>

              <!-- 十神分析 -->
              <div v-if="result.shishen_analysis" class="result-card compact-card">
                <h3 class="section-title">
                  <el-icon><Grid /></el-icon>
                  十神
                </h3>
                <div class="shishen-mini">
                  <span v-for="(info, zhu) in result.shishen_analysis.shishen_data" :key="zhu" class="ss-item">
                    {{ zhuNameMap[zhu] }}: {{ info.gan_shishen || '-' }}/{{ info.zhi_shishen || '-' }}
                  </span>
                </div>
              </div>

              <!-- 大运分析 -->
              <div v-if="result.dayun_analysis" class="result-card compact-card">
                <h3 class="section-title">
                  <el-icon><Calendar /></el-icon>
                  大运
                </h3>
                <div class="dayun-mini">
                  <span v-for="(dy, i) in (result.dayun_analysis.dayun_list || []).slice(0, 4)" :key="i" class="dy-item">
                    {{ dy.gan }}{{ dy.zhi }}
                  </span>
                  <span v-if="result.dayun_analysis.dayun_list?.length > 4" class="dy-more">...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 可拖拽分割条 -->
          <div 
            class="resize-handle" 
            @mousedown="startResize"
            :class="{ 'resizing': isResizing }"
          >
            <div class="resize-line"></div>
            <div class="resize-hint">
              <el-icon><DCaret /></el-icon>
              拖拽调整
            </div>
          </div>

          <!-- 下方：聊天面板（AI深度解析 + 追问对话） -->
          <div class="chat-section" :style="{ height: `calc(100% - ${basicResultHeight + RESIZE_HANDLE_HEIGHT}px)` }">
            <BaziChatPanel 
              ref="chatPanelRef"
              :initial-message="llmText"
              :loading="llmLoading"
              :progress="llmProgress"
              @clear="handleClearChat"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Document, Star, Calendar, Grid, DCaret } from '@element-plus/icons-vue';
import BaziChart from '../components/BaziChart.vue';
import BaziChatPanel from '../components/BaziChatPanel.vue';
import { useBaziChatStore } from '../stores/baziChat';

const baziChatStore = useBaziChatStore();
const chatPanelRef = ref<any>(null);

const loading = ref(false);
const result = ref<any>(null);

const analysisStyles = ref<Array<{ value: string; name: string; description: string }>>([
  { value: 'classic', name: '传统专业', description: '专业术语完整，分析深入全面' },
  { value: 'simple', name: '简明通俗', description: '语言生活化，适合零基础用户' },
  { value: 'life_guide', name: '人生指南', description: '更关注人生阶段与规划建议' },
  { value: 'business', name: '商业决策', description: '偏重事业与财富方向' },
  { value: 'emotion', name: '情感婚恋', description: '重点解读感情与婚姻' },
]);

const llmLoading = ref(false);
const llmProgress = ref('');
const llmText = ref('');

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
  analysis_style: 'classic',
});

const zhuNameMap: Record<string, string> = {
  'nian_zhu': '年', 'yue_zhu': '月', 'ri_zhu': '日', 'shi_zhu': '时',
};

const getWuxingData = (wuxing: any) => {
  const data = wuxing?.wuxing_data || {};
  return {
    '金': data.jin || 0,
    '木': data.mu || 0,
    '水': data.shui || 0,
    '火': data.huo || 0,
    '土': data.tu || 0,
  };
};

// 拖拽调整大小相关
const RESIZE_HANDLE_HEIGHT = 24;
const basicResultHeight = ref(200); // 默认基础结果高度
const isResizing = ref(false);
const startY = ref(0);
const startHeight = ref(0);

const startResize = (e: MouseEvent) => {
  isResizing.value = true;
  startY.value = e.clientY;
  startHeight.value = basicResultHeight.value;
  document.addEventListener('mousemove', onResize);
  document.addEventListener('mouseup', stopResize);
  document.body.style.cursor = 'ns-resize';
  document.body.style.userSelect = 'none';
};

const onResize = (e: MouseEvent) => {
  if (!isResizing.value) return;
  const delta = e.clientY - startY.value;
  const newHeight = startHeight.value + delta;
  // 限制最小和最大高度
  basicResultHeight.value = Math.max(150, Math.min(500, newHeight));
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

onUnmounted(() => {
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
});

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

const handleAnalyze = async () => {
  if (!form.year || !form.month || !form.day) {
    ElMessage.warning('请填写完整的出生信息');
    return;
  }

  loading.value = true;
  result.value = null;
  llmText.value = '';
  llmProgress.value = '';
  baziChatStore.reset();

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/pan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        year: form.year, month: form.month, day: form.day, hour: form.hour,
        gender: form.gender,
        include_wuxing: form.include_wuxing, include_shishen: form.include_shishen,
        include_dayun: form.include_dayun, include_shensha: form.include_shensha,
        include_llm: false, analysis_style: form.analysis_style,
      }),
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.detail || data.error || '分析失败');
    }

    result.value = data;
    updateChatContext(data);
    ElMessage.success('排盘分析完成');

    // 自动开始AI深度解析
    startLLMStream();

  } catch (error: any) {
    console.error('排盘失败:', error);
    ElMessage.error(error.message || '排盘失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const startLLMStream = async () => {
  llmLoading.value = true;
  llmProgress.value = '';

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/llm-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        year: form.year, month: form.month, day: form.day, hour: form.hour,
        gender: form.gender, analysis_style: form.analysis_style,
      }),
    });

    if (!response.body) throw new Error('当前浏览器不支持流式输出');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data:')) continue;
        const jsonStr = line.slice(5).trim();
        if (!jsonStr) continue;
        try {
          const payload = JSON.parse(jsonStr);
          if (payload.type === 'progress') llmProgress.value = payload.message || '';
          else if (payload.type === 'content' && payload.content) llmText.value += payload.content;
          else if (payload.type === 'done' && payload.full_content && !llmText.value) llmText.value = payload.full_content;
        } catch { console.warn('解析LLM流式数据失败'); }
      }
    }

    baziChatStore.setBaziContext({ llm_analysis: llmText.value });

  } catch (error: any) {
    console.error('LLM流式解析失败:', error);
  } finally {
    llmLoading.value = false;
  }
};

const updateChatContext = (data: any) => {
  baziChatStore.setBaziContext({
    sizhu: data.sizhu || null,
    wuxing_analysis: data.wuxing_analysis || null,
    shishen_analysis: data.shishen_analysis || null,
    dayun_analysis: data.dayun_analysis || null,
    liunian_analysis: data.liunian_analysis || null,
    shensha_analysis: data.shensha_analysis || null,
    analysis_style: form.analysis_style,
    gender: form.gender,
    birth_info: { year: form.year, month: form.month, day: form.day, hour: form.hour },
  });
};

const handleClearChat = () => {
  llmText.value = '';
  baziChatStore.reset();
};

watch(llmText, (newText) => {
  if (newText && result.value) {
    baziChatStore.setBaziContext({ llm_analysis: newText });
  }
});
</script>

<style scoped>
.bazi-view {
  --bazi-bg: linear-gradient(135deg, #FAF8F5 0%, #F5F0E8 50%, #FBF9F6 100%);
  --bazi-surface: rgba(255, 253, 250, 0.92);
  --bazi-primary: #8B6914;
  --bazi-secondary: #D4AF37;
  --bazi-text: #3D3226;
  --bazi-text-light: #6B5D4D;
  --bazi-border-light: rgba(180, 150, 100, 0.25);
  --bazi-shadow: rgba(139, 90, 43, 0.12);
}

.bazi-view {
  height: 100%;
  overflow: hidden;
  background: var(--bazi-bg);
  color: var(--bazi-text);
}

.main-layout {
  display: flex;
  gap: 20px;
  padding: 20px;
  max-width: 1800px;
  margin: 0 auto;
  height: calc(100vh - 40px);
}

.left-panel {
  width: 320px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.input-card {
  background: var(--bazi-surface);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid var(--bazi-border-light);
  box-shadow: 0 8px 32px var(--bazi-shadow);
}

.card-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--bazi-primary);
  padding-bottom: 12px;
  border-bottom: 2px solid var(--bazi-border-light);
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

.empty-state, .loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: var(--bazi-surface);
  border-radius: 16px;
  border: 1px solid var(--bazi-border-light);
}

/* 结果区域布局 */
.result-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bazi-surface);
  border-radius: 16px;
  border: 1px solid var(--bazi-border-light);
  overflow: hidden;
}

.basic-result-section {
  flex-shrink: 0;
  overflow-y: auto;
  padding: 16px;
  min-height: 150px;
}

.result-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--bazi-border-light);
}

.compact-card {
  padding: 12px 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--bazi-text);
}

.sizhu-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 10px;
}

.info-item {
  font-size: 14px;
}

.info-item .label {
  color: var(--bazi-text-light);
  margin-right: 4px;
}

.info-item .value {
  font-weight: 600;
  color: var(--bazi-primary);
}

.analysis-row {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.analysis-row .result-card {
  flex: 1;
}

.wuxing-mini, .shishen-mini, .dayun-mini {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.wx-item, .ss-item, .dy-item {
  padding: 3px 8px;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 10px;
  font-size: 12px;
}

.dy-more {
  padding: 3px 6px;
  color: var(--bazi-text-light);
  font-size: 12px;
}

/* 可拖拽分割条 */
.resize-handle {
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, rgba(212, 175, 55, 0.1) 100%);
  cursor: ns-resize;
  user-select: none;
  position: relative;
  transition: background 0.2s;
}

.resize-handle:hover, .resize-handle.resizing {
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.1) 0%, rgba(212, 175, 55, 0.2) 100%);
}

.resize-line {
  position: absolute;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--bazi-secondary);
  border-radius: 1px;
  opacity: 0.5;
}

.resize-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--bazi-text-light);
  opacity: 0;
  transition: opacity 0.2s;
}

.resize-handle:hover .resize-hint {
  opacity: 1;
}

/* 聊天区域 */
.chat-section {
  flex: 1;
  min-height: 200px;
  overflow: hidden;
}

.chat-section :deep(.bazi-chat-panel) {
  height: 100%;
}
</style>