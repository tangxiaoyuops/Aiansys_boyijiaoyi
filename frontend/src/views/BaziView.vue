<template>
  <div class="bazi-view">
    <div class="main-layout">
      <!-- 左侧输入区域 -->
      <div class="left-panel">
        <div class="input-card">
          <!-- 模式切换 -->
          <div class="mode-switch">
            <el-radio-group v-model="analysisMode" size="large">
              <el-radio-button label="single">单人分析</el-radio-button>
              <el-radio-button label="hepan">双人合盘</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 单人模式表单 -->
          <template v-if="analysisMode === 'single'">
            <h2 class="card-title">排盘信息</h2>
            <div class="form-hint">请输入公历日期</div>
            <el-form :model="form" label-width="90px" class="bazi-form">
            <el-form-item label="姓名">
              <el-input v-model="form.name" placeholder="可选，用于个性化报告" clearable />
            </el-form-item>
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
            <el-divider content-position="left">流月推演（可选）</el-divider>
            <el-form-item>
              <el-checkbox v-model="form.include_liuyue">启用流月推演</el-checkbox>
            </el-form-item>
            <el-form-item v-if="form.include_liuyue" label="推演月数">
              <el-input-number v-model="form.liuyue_months" :min="1" :max="24" style="width: 120px" />
              <span style="margin-left: 10px; color: #909399;">个月</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleAnalyze" style="width: 100%">
                <el-icon><MagicStick /></el-icon>
                开始排盘分析
              </el-button>
            </el-form-item>
          </el-form>
          </template>

          <!-- 双人合盘模式表单 -->
          <template v-else>
            <el-collapse v-model="activePanels" class="hepan-collapse">
              <el-collapse-item name="A">
                <template #title>
                  <span class="pan-title">
                    {{ hepanForm.name_a || '命盘A' }} ({{ hepanForm.gender_a }}) - {{ hepanForm.year_a }}年{{ hepanForm.month_a }}月{{ hepanForm.day_a }}日
                  </span>
                </template>
                <el-form :model="hepanForm" label-width="80px" class="hepan-form">
                  <el-form-item label="姓名">
                    <el-input v-model="hepanForm.name_a" placeholder="可选" clearable />
                  </el-form-item>
                  <el-form-item label="出生年份">
                    <el-input-number v-model="hepanForm.year_a" :min="1900" :max="2100" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生月份">
                    <el-input-number v-model="hepanForm.month_a" :min="1" :max="12" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生日期">
                    <el-input-number v-model="hepanForm.day_a" :min="1" :max="31" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生时辰">
                    <el-select v-model="hepanForm.hour_a" placeholder="选择时辰" style="width: 100%">
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
                    <el-radio-group v-model="hepanForm.gender_a">
                      <el-radio label="男">男</el-radio>
                      <el-radio label="女">女</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-form>
              </el-collapse-item>

              <el-collapse-item name="B">
                <template #title>
                  <span class="pan-title">
                    {{ hepanForm.name_b || '命盘B' }} ({{ hepanForm.gender_b }}) - {{ hepanForm.year_b }}年{{ hepanForm.month_b }}月{{ hepanForm.day_b }}日
                  </span>
                </template>
                <el-form :model="hepanForm" label-width="80px" class="hepan-form">
                  <el-form-item label="姓名">
                    <el-input v-model="hepanForm.name_b" placeholder="可选" clearable />
                  </el-form-item>
                  <el-form-item label="出生年份">
                    <el-input-number v-model="hepanForm.year_b" :min="1900" :max="2100" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生月份">
                    <el-input-number v-model="hepanForm.month_b" :min="1" :max="12" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生日期">
                    <el-input-number v-model="hepanForm.day_b" :min="1" :max="31" style="width: 100%" />
                  </el-form-item>
                  <el-form-item label="出生时辰">
                    <el-select v-model="hepanForm.hour_b" placeholder="选择时辰" style="width: 100%">
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
                    <el-radio-group v-model="hepanForm.gender_b">
                      <el-radio label="男">男</el-radio>
                      <el-radio label="女">女</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-form>
              </el-collapse-item>
            </el-collapse>

            <div class="hepan-options">
              <el-form-item label="合盘类型">
                <el-radio-group v-model="hepanForm.hepan_type">
                  <el-radio label="couple">情侣合婚</el-radio>
                  <el-radio label="business">商业合作</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="hepanLoading" @click="handleHepanAnalyze" style="width: 100%">
                  <el-icon><Connection /></el-icon>
                  开始合盘分析
                </el-button>
              </el-form-item>
            </div>
          </template>
        </div>
      </div>

      <!-- 右侧结果区域 -->
      <div class="right-panel">
        <!-- 单人模式空状态 -->
        <div v-if="analysisMode === 'single' && !result && !loading" class="empty-state">
          <el-empty description="请填写信息并点击排盘分析" />
        </div>

        <!-- 合盘模式空状态 -->
        <div v-if="analysisMode === 'hepan' && !hepanResult && !hepanLoading" class="empty-state">
          <el-empty description="请填写双方信息并点击合盘分析" />
        </div>

        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>

        <div v-if="hepanLoading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>

        <!-- 单人模式结果 -->
        <div v-if="analysisMode === 'single' && result && !loading" class="result-wrapper">
          <!-- 标签页切换 -->
          <el-tabs v-model="activeResultTab" class="result-tabs">
            <!-- 基础分析标签 -->
            <el-tab-pane label="命盘分析" name="basic">
              <div class="basic-result-content">
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
                  <div v-if="result.wuxing_analysis" class="result-card compact-card">
                    <h3 class="section-title"><el-icon><Star /></el-icon>五行</h3>
                    <div class="wuxing-mini">
                      <span v-for="(count, name) in getWuxingData(result.wuxing_analysis)" :key="name" class="wx-item">
                        {{ name }}: {{ count }}
                      </span>
                    </div>
                  </div>
                  <div v-if="result.shishen_analysis" class="result-card compact-card">
                    <h3 class="section-title"><el-icon><Grid /></el-icon>十神</h3>
                    <div class="shishen-mini">
                      <span v-for="(info, zhu) in result.shishen_analysis.shishen_data" :key="zhu" class="ss-item">
                        {{ zhuNameMap[zhu] }}: {{ info.gan_shishen || '-' }}/{{ info.zhi_shishen || '-' }}
                      </span>
                    </div>
                  </div>
                  <div v-if="result.shensha_analysis?.shensha_data?.shensha_list?.length" class="result-card compact-card">
                    <h3 class="section-title"><el-icon><MagicStick /></el-icon>神煞</h3>
                    <div class="shensha-mini">
                      <span v-for="(ss, i) in result.shensha_analysis.shensha_data.shensha_list" :key="i"
                            class="ss-item" :class="'shensha-' + ss.type">
                        {{ ss.name }}
                      </span>
                    </div>
                  </div>
                  <div v-if="result.dayun_analysis" class="result-card compact-card">
                    <h3 class="section-title"><el-icon><Calendar /></el-icon>大运</h3>
                    <div class="dayun-mini">
                      <span v-for="(dy, i) in (result.dayun_analysis.dayun_list || []).slice(0, 4)" :key="i" class="dy-item">
                        {{ dy.gan }}{{ dy.zhi }}
                      </span>
                      <span v-if="result.dayun_analysis.dayun_list?.length > 4" class="dy-more">...</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- 流月推演标签 -->
            <el-tab-pane label="流月推演" name="liuyue" v-if="result.liuyue_analysis?.liuyue_list?.length">
              <div class="liuyue-tab-content">
                <LiuyuePanel
                  :liuyue-list="result.liuyue_analysis.liuyue_list"
                  :months-count="result.liuyue_analysis.months_count"
                  :wuxing-xi-ji="result.liuyue_analysis.wuxing_xi_ji"
                  :llm-analysis="result.liuyue_analysis.llm_analysis"
                  :calculation-day="result.liuyue_analysis.calculation_day"
                  :include-current-month="result.liuyue_analysis.include_current_month"
                  :solar-date="result.liuyue_analysis.solar_date"
                  :lunar-date="result.liuyue_analysis.lunar_date"
                />
              </div>
            </el-tab-pane>

            <!-- AI对话标签 -->
            <el-tab-pane label="AI解读" name="chat">
              <div class="chat-tab-content">
                <BaziChatPanel ref="chatPanelRef" :llm-loading="llmLoading" :llm-progress="llmProgress" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 合盘模式结果 -->
        <div v-if="analysisMode === 'hepan' && hepanResult && !hepanLoading" class="result-wrapper hepan-result-wrapper">
          <el-tabs v-model="activeHepenTab" class="result-tabs">
            <!-- 合盘分析标签 -->
            <el-tab-pane label="合盘分析" name="hepan">
              <div class="hepan-tab-content">
                <!-- 双方四柱对比 -->
                <div class="dual-sizhu-row">
                  <div class="sizhu-card">
                    <h4 class="sizhu-title">命盘A ({{ hepanResult.birth_info_a?.gender }})</h4>
                    <BaziChart :sizhu="hepanResult.pan_a?.sizhu" :compact="true" />
                  </div>
                  <div class="vs-divider">
                    <span class="vs-text">VS</span>
                  </div>
                  <div class="sizhu-card">
                    <h4 class="sizhu-title">命盘B ({{ hepanResult.birth_info_b?.gender }})</h4>
                    <BaziChart :sizhu="hepanResult.pan_b?.sizhu" :compact="true" />
                  </div>
                </div>
                <!-- 合盘匹配分析 -->
                <HepanResultPanel :hepan-data="hepanResult.hepan" />
              </div>
            </el-tab-pane>
            <!-- AI对话标签 -->
            <el-tab-pane label="AI解读" name="chat">
              <div class="chat-tab-content">
                <BaziChatPanel 
                  mode="hepan"
                  :llm-loading="hepanLlmLoading" 
                  :llm-progress="hepanLlmProgress" 
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Document, Star, Calendar, Grid, DCaret, Connection } from '@element-plus/icons-vue';
import BaziChart from '../components/BaziChart.vue';
import BaziChatPanel from '../components/BaziChatPanel.vue';
import HepanResultPanel from '../components/HepanResultPanel.vue';
import LiuyuePanel from '../components/LiuyuePanel.vue';
import { useBaziChatStore } from '../stores/baziChat';

const baziChatStore = useBaziChatStore();
const chatPanelRef = ref<any>(null);

const loading = ref(false);
const result = ref<any>(null);

const analysisMode = ref<'single' | 'hepan'>('single');
const activeResultTab = ref<'basic' | 'liuyue' | 'chat'>('basic');  // 单人模式结果标签页
const activeHepenTab = ref<'hepan' | 'chat'>('hepan');  // 合盘模式结果标签页
const activePanels = ref(['A', 'B']);

const hepanLoading = ref(false);
const hepanResult = ref<any>(null);
const hepanLlmLoading = ref(false);
const hepanLlmProgress = ref('');
const hepanLlmContent = ref('');

// 监听模式切换，清理另一模式的数据
watch(analysisMode, (newMode) => {
  if (newMode === 'single') {
    // 切换到单人模式时，清理合盘数据
    hepanResult.value = null;
    hepanLlmContent.value = '';
    hepanLlmProgress.value = '';
    hepanLoading.value = false;
    hepanLlmLoading.value = false;
    baziChatStore.clearHepanContext();
    baziChatStore.clearMessages();
  } else {
    // 切换到合盘模式时，清理单人分析数据
    result.value = null;
    llmLoading.value = false;
    llmProgress.value = '';
    baziChatStore.clearBaziContext();
    baziChatStore.clearMessages();
  }
});

const analysisStyles = ref([
  { value: 'classic', name: '传统专业', description: '专业术语完整，分析深入全面' },
  { value: 'simple', name: '简明通俗', description: '语言生活化，适合零基础用户' },
  { value: 'life_guide', name: '人生指南', description: '更关注人生阶段与规划建议' },
  { value: 'business', name: '商业决策', description: '偏重事业与财富方向' },
  { value: 'emotion', name: '情感婚恋', description: '重点解读感情与婚姻' },
]);

const llmLoading = ref(false);
const llmProgress = ref('');

const form = reactive({
  name: '',  // 可选的名字
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
  include_liuyue: false,  // 是否包含流月推演
  liuyue_months: 6,  // 推演月数
});

const hepanForm = reactive({
  name_a: '',  // 命盘A名字（可选）
  year_a: 1990,
  month_a: 1,
  day_a: 1,
  hour_a: 11,
  gender_a: '男',
  name_b: '',  // 命盘B名字（可选）
  year_b: 1992,
  month_b: 5,
  day_b: 15,
  hour_b: 13,
  gender_b: '女',
  hepan_type: 'couple' as 'couple' | 'business',
  include_llm: true,
  analysis_style: 'emotion',
});

const zhuNameMap: Record<string, string> = {
  'nian_zhu': '年', 'yue_zhu': '月', 'ri_zhu': '日', 'shi_zhu': '时',
};

const getWuxingData = (wuxing: any) => {
  const data = wuxing?.wuxing_data || {};
  return { '金': data.jin || 0, '木': data.mu || 0, '水': data.shui || 0, '火': data.huo || 0, '土': data.tu || 0 };
};

// 拖拽调整大小
const RESIZE_HANDLE_HEIGHT = 24;
const basicResultHeight = ref(200);
const isResizing = ref(false);
const startY = ref(0);
const startHeight = ref(0);

const hepanResultHeight = ref(300);
const isHepanResizing = ref(false);
const hepanStartY = ref(0);
const hepanStartHeight = ref(0);

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
  basicResultHeight.value = Math.max(150, Math.min(500, startHeight.value + delta));
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

const startHepanResize = (e: MouseEvent) => {
  isHepanResizing.value = true;
  hepanStartY.value = e.clientY;
  hepanStartHeight.value = hepanResultHeight.value;
  document.addEventListener('mousemove', onHepanResize);
  document.addEventListener('mouseup', stopHepanResize);
  document.body.style.cursor = 'ns-resize';
  document.body.style.userSelect = 'none';
};

const onHepanResize = (e: MouseEvent) => {
  if (!isHepanResizing.value) return;
  const delta = e.clientY - hepanStartY.value;
  hepanResultHeight.value = Math.max(200, Math.min(600, hepanStartHeight.value + delta));
};

const stopHepanResize = () => {
  isHepanResizing.value = false;
  document.removeEventListener('mousemove', onHepanResize);
  document.removeEventListener('mouseup', stopHepanResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
};

onUnmounted(() => {
  document.removeEventListener('mousemove', onResize);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('mousemove', onHepanResize);
  document.removeEventListener('mouseup', stopHepanResize);
});

onMounted(async () => {
  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/styles`);
    const data = await response.json();
    if (response.ok && data.success && Array.isArray(data.styles)) {
      analysisStyles.value = data.styles;
    }
  } catch (e) {
    console.warn('获取风格列表失败');
  }
});

const handleAnalyze = async () => {
  if (!form.year || !form.month || !form.day) {
    ElMessage.warning('请填写完整的出生信息');
    return;
  }

  loading.value = true;
  result.value = null;
  baziChatStore.reset(); // 清空之前的对话
  llmProgress.value = '';

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    const response = await fetch(`${baseURL}/api/bazi/pan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name,
        year: form.year, month: form.month, day: form.day, hour: form.hour,
        gender: form.gender,
        include_wuxing: form.include_wuxing, include_shishen: form.include_shishen,
        include_dayun: form.include_dayun, include_shensha: form.include_shensha,
        include_llm: false,  // 主命盘LLM使用流式，但流月LLM会单独调用
        analysis_style: form.analysis_style,
        include_liuyue: form.include_liuyue,
        liuyue_months: form.liuyue_months,
      }),
    });

    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.detail || '分析失败');

    result.value = data;
    updateChatContext(data);
    ElMessage.success('排盘分析完成');

    // 自动开始AI深度解析
    startLLMStream();
  } catch (error: any) {
    ElMessage.error(error.message || '排盘失败');
  } finally {
    loading.value = false;
  }
};

const startLLMStream = async () => {
  llmLoading.value = true;
  llmProgress.value = '';
  baziChatStore.setLoading(true);
  
  // 先添加一个占位的助手消息，用于流式更新
  baziChatStore.appendAssistantMessage('', 'analysis');

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    
    // 构建请求体：传递前端已排好的数据，避免后端重复排盘，保证数据一致性
    const requestBody: any = {
      name: form.name,
      year: form.year,
      month: form.month,
      day: form.day,
      hour: form.hour,
      gender: form.gender,
      analysis_style: form.analysis_style,
      // 传递前端已排好的数据
      sizhu: result.value?.sizhu || null,
      wuxing_analysis: result.value?.wuxing_analysis || null,
      shishen_analysis: result.value?.shishen_analysis || null,
      dayun_analysis: result.value?.dayun_analysis || null,
      shensha_analysis: result.value?.shensha_analysis || null,
    };
    
    const response = await fetch(`${baseURL}/api/bazi/llm-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!response.body) throw new Error('不支持流式输出');

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
          console.log('[BaziView] 收到事件:', payload.type, payload.content?.substring(0, 30));
          
          if (payload.type === 'progress') {
            llmProgress.value = payload.message || '';
            baziChatStore.setProgressMessage(payload.message || '');
          }
          else if (payload.type === 'content' && payload.content) {
            // 流式更新第一条助手消息（深度分析）
            baziChatStore.updateFirstAssistantMessage(payload.content);
          }
          else if (payload.type === 'done') {
            console.log('[BaziView] 流式完成');
            if (payload.full_content) {
              // 使用replace=true替换整个内容，避免重复
              baziChatStore.updateFirstAssistantMessage(payload.full_content, true);
            }
          }
        } catch (e) {
          console.error('[BaziView] 解析错误:', e);
        }
      }
    }

    // 更新聊天上下文中的llm_analysis
    const firstMsg = baziChatStore.messages[0];
    if (firstMsg) {
      baziChatStore.setBaziContext({ llm_analysis: firstMsg.content });
    }
  } catch (error: any) {
    console.error('LLM流式解析失败:', error);
  } finally {
    llmLoading.value = false;
    baziChatStore.setLoading(false);
  }
};

const updateChatContext = (data: any) => {
  baziChatStore.setBaziContext({
    name: form.name,
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

const handleHepanAnalyze = async () => {
  if (!hepanForm.year_a || !hepanForm.month_a || !hepanForm.day_a ||
      !hepanForm.year_b || !hepanForm.month_b || !hepanForm.day_b) {
    ElMessage.warning('请填写完整的双方出生信息');
    return;
  }

  hepanLoading.value = true;
  hepanResult.value = null;
  hepanLlmContent.value = '';
  hepanLlmProgress.value = '';
  
  // 清空之前的对话消息
  baziChatStore.clearMessages();

  try {
    const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
    
    // 使用流式API
    const response = await fetch(`${baseURL}/api/bazi/hepan-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name_a: hepanForm.name_a,
        year_a: hepanForm.year_a,
        month_a: hepanForm.month_a,
        day_a: hepanForm.day_a,
        hour_a: hepanForm.hour_a,
        gender_a: hepanForm.gender_a,
        name_b: hepanForm.name_b,
        year_b: hepanForm.year_b,
        month_b: hepanForm.month_b,
        day_b: hepanForm.day_b,
        hour_b: hepanForm.hour_b,
        gender_b: hepanForm.gender_b,
        hepan_type: hepanForm.hepan_type,
        include_llm: hepanForm.include_llm,
        analysis_style: hepanForm.analysis_style,
      }),
    });

    if (!response.body) throw new Error('不支持流式输出');

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
          
          if (payload.type === 'progress') {
            hepanLlmProgress.value = payload.message || '';
            // 同步更新store中的进度消息，用于对话面板显示
            baziChatStore.setProgressMessage(payload.message || '');
          }
          else if (payload.type === 'data') {
            hepanResult.value = {
              success: true,
              pan_a: payload.pan_a,
              pan_b: payload.pan_b,
              hepan: payload.hepan,
              birth_info_a: {
                year: hepanForm.year_a,
                month: hepanForm.month_a,
                day: hepanForm.day_a,
                hour: hepanForm.hour_a,
                gender: hepanForm.gender_a,
              },
              birth_info_b: {
                year: hepanForm.year_b,
                month: hepanForm.month_b,
                day: hepanForm.day_b,
                hour: hepanForm.hour_b,
                gender: hepanForm.gender_b,
              },
            };
            hepanLlmLoading.value = true;
            // 同步设置store的loading状态
            baziChatStore.setLoading(true);
            
            // 保存合盘上下文到 store
            baziChatStore.setHepanContext({
              hepan_type: hepanForm.hepan_type,
              name_a: hepanForm.name_a,
              pan_a: payload.pan_a,
              birth_info_a: {
                year: hepanForm.year_a,
                month: hepanForm.month_a,
                day: hepanForm.day_a,
                hour: hepanForm.hour_a,
                gender: hepanForm.gender_a,
              },
              gender_a: hepanForm.gender_a,
              name_b: hepanForm.name_b,
              pan_b: payload.pan_b,
              birth_info_b: {
                year: hepanForm.year_b,
                month: hepanForm.month_b,
                day: hepanForm.day_b,
                hour: hepanForm.hour_b,
                gender: hepanForm.gender_b,
              },
              gender_b: hepanForm.gender_b,
              hepan_result: payload.hepan,
              llm_analysis: null,
            });
            
            // 添加一条空的助手消息，用于流式输出深度分析
            baziChatStore.appendAssistantMessage('', 'analysis');
          }
          else if (payload.type === 'content' && payload.content) {
            hepanLlmContent.value += payload.content;
            // 更新对话面板中的分析内容
            baziChatStore.updateFirstAssistantMessage(payload.content);
          }
          else if (payload.type === 'done') {
            if (payload.full_content) {
              hepanLlmContent.value = payload.full_content;
              // 更新对话面板中的完整分析内容
              baziChatStore.updateFirstAssistantMessage(payload.full_content, true);
              // 更新 store 中的 llm_analysis
              baziChatStore.setHepanContext({
                llm_analysis: payload.full_content,
              });
            }
            hepanLlmLoading.value = false;
            baziChatStore.setLoading(false);
          }
          else if (payload.type === 'error') {
            ElMessage.error(payload.message || '分析失败');
            hepanLlmLoading.value = false;
            baziChatStore.setLoading(false);
          }
        } catch (e) {
          console.error('[HepanView] 解析错误:', e);
        }
      }
    }

    ElMessage.success('合盘分析完成');
  } catch (error: any) {
    ElMessage.error(error.message || '合盘分析失败');
  } finally {
    hepanLoading.value = false;
    hepanLlmLoading.value = false;
    baziChatStore.setLoading(false);
  }
};

const renderMarkdown = (content: string): string => {
  if (!content) return '';
  let html = content
    .replace(/^### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^## (.*$)/gim, '<h3>$1</h3>')
    .replace(/^# (.*$)/gim, '<h2>$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^- (.*$)/gim, '<li>$1</li>')
    .replace(/\n/g, '<br>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  return html;
};
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

.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { flex: 1; min-width: 0; overflow: hidden; }

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

.result-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bazi-surface);
  border-radius: 16px;
  border: 1px solid var(--bazi-border-light);
  overflow: hidden;
}

/* 标签页样式 */
.result-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.result-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
  background: rgba(212, 175, 55, 0.05);
  border-bottom: 1px solid var(--bazi-border-light);
}

.result-tabs :deep(.el-tabs__nav-wrap) {
  padding: 8px 0;
}

.result-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  padding: 0 20px;
  height: 36px;
  line-height: 36px;
}

.result-tabs :deep(.el-tabs__item.is-active) {
  color: var(--bazi-primary);
  font-weight: 600;
}

.result-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--bazi-primary);
}

.result-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.result-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
}

.basic-result-content {
  padding: 16px;
}

.liuyue-tab-content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.chat-tab-content {
  height: 100%;
}

.chat-tab-content :deep(.bazi-chat-panel) {
  height: 100%;
}

.hepan-tab-content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.dual-sizhu-row {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.sizhu-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 12px;
}

.sizhu-title {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--bazi-text-light);
  text-align: center;
}

.vs-divider {
  padding: 0 8px;
}

.vs-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--bazi-primary);
}

.result-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--bazi-border-light);
}

.compact-card { padding: 12px 16px; }

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--bazi-text);
}

.sizhu-info { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.info-item { font-size: 14px; }
.info-item .label { color: var(--bazi-text-light); margin-right: 4px; }
.info-item .value { font-weight: 600; color: var(--bazi-primary); }

.analysis-row { display: flex; gap: 12px; margin-top: 12px; }
.analysis-row .result-card { flex: 1; }
.wuxing-mini, .shishen-mini, .dayun-mini, .shensha-mini { display: flex; flex-wrap: wrap; gap: 6px; }
.wx-item, .ss-item, .dy-item { padding: 3px 8px; background: rgba(212, 175, 55, 0.1); border-radius: 10px; font-size: 12px; }
.dy-more, .ss-more { padding: 3px 6px; color: var(--bazi-text-light); font-size: 12px; }
.shensha-吉 { background: rgba(103, 194, 58, 0.15); color: #67c23a; }
.shensha-凶 { background: rgba(245, 108, 108, 0.15); color: #f56c6c; }
.shensha-中性 { background: rgba(144, 147, 153, 0.15); color: #909399; }

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

.resize-handle:hover .resize-hint { opacity: 1; }

.chat-section { flex: 1; min-height: 200px; overflow: hidden; }
.chat-section :deep(.bazi-chat-panel) { height: 100%; }

.mode-switch {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.mode-switch :deep(.el-radio-group) {
  width: 100%;
}

.mode-switch :deep(.el-radio-button__inner) {
  width: 100%;
}

.hepan-collapse {
  margin-bottom: 16px;
  border: none;
}

.hepan-collapse :deep(.el-collapse-item__header) {
  background: rgba(212, 175, 55, 0.1);
  border-radius: 8px;
  padding: 0 16px;
  border: none;
  margin-bottom: 8px;
}

.hepan-collapse :deep(.el-collapse-item__wrap) {
  border: none;
}

.hepan-collapse :deep(.el-collapse-item__content) {
  padding: 12px 0 0 0;
}

.pan-title {
  font-weight: 500;
  color: var(--bazi-text);
}

.hepan-form {
  padding: 0 8px;
}

.hepan-options {
  padding: 16px;
  background: rgba(212, 175, 55, 0.05);
  border-radius: 12px;
  margin-top: 12px;
}

.hepan-result-wrapper {
  padding: 0;
}

.hepan-basic-section {
  flex-shrink: 0;
  overflow-y: auto;
  padding: 16px;
  min-height: 200px;
}

.dual-sizhu-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: stretch;
}

.sizhu-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid var(--bazi-border-light);
}

.sizhu-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--bazi-primary);
  text-align: center;
}

.vs-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
}

.vs-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--bazi-secondary);
  background: rgba(212, 175, 55, 0.15);
  padding: 8px 12px;
  border-radius: 50%;
}

.hepan-llm-section {
  flex: 1;
  min-height: 150px;
  overflow-y: auto;
  padding: 16px;
}

.llm-loading {
  padding: 16px;
}

.progress-text {
  margin-top: 12px;
  font-size: 13px;
  color: var(--bazi-text-light);
  text-align: center;
}

.llm-content {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--bazi-border-light);
}

.content-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: var(--bazi-primary);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--bazi-border-light);
}

.markdown-body {
  font-size: 14px;
  line-height: 1.8;
  color: var(--bazi-text);
}

.markdown-body h2 {
  font-size: 16px;
  margin: 16px 0 8px 0;
  color: var(--bazi-primary);
}

.markdown-body h3 {
  font-size: 15px;
  margin: 14px 0 6px 0;
  color: var(--bazi-text);
}

.markdown-body h4 {
  font-size: 14px;
  margin: 12px 0 6px 0;
  color: var(--bazi-text);
}

.markdown-body ul {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-body li {
  margin-bottom: 4px;
}

.llm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>