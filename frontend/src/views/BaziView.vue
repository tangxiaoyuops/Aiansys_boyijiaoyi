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
            <el-form-item label="分析选项">
              <el-checkbox v-model="form.include_wuxing">五行分析</el-checkbox>
              <el-checkbox v-model="form.include_shishen">十神分析</el-checkbox>
              <el-checkbox v-model="form.include_dayun">大运分析</el-checkbox>
              <el-checkbox v-model="form.include_shensha">神煞分析</el-checkbox>
              <el-checkbox v-model="form.include_llm">AI深度解析</el-checkbox>
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
                  <span class="dayun-label">第{{ index + 1 }}步大运：</span>
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
          <div v-if="result.llm_analysis" class="result-card llm-card">
            <h3 class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              AI深度解析
            </h3>
            <div class="llm-content">
              <div v-if="result.llm_analysis.success && result.llm_analysis.analysis" class="llm-text" v-html="formatLLMResponse(result.llm_analysis.analysis)"></div>
              <div v-else class="llm-error">
                <el-alert :title="result.llm_analysis.error || '分析失败'" type="error" :closable="false" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, Document, Star, Calendar, Sunny, Grid, ChatLineRound } from '@element-plus/icons-vue';
import BaziChart from '../components/BaziChart.vue';
import { getBaseURL } from '../api';

const loading = ref(false);
const result = ref<any>(null);

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
});

const zhuNameMap: Record<string, string> = {
  'nian_zhu': '年柱',
  'yue_zhu': '月柱',
  'ri_zhu': '日柱',
  'shi_zhu': '时柱',
};

const handleAnalyze = async () => {
  if (!form.year || !form.month || !form.day) {
    ElMessage.warning('请填写完整的出生信息');
    return;
  }

  loading.value = true;
  result.value = null;

  try {
    const baseURL = getBaseURL();
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
        include_llm: form.include_llm,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.detail || data.error || '分析失败');
    }

    result.value = data;
    ElMessage.success('排盘分析完成');
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
.bazi-view {
  height: 100%;
  overflow: auto;
  background: #f5f5f5;
}

.main-layout {
  display: flex;
  gap: 20px;
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.left-panel {
  width: 350px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.input-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.form-hint {
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-left: 3px solid #3b82f6;
  color: #1e40af;
  font-size: 13px;
  border-radius: 4px;
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
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.sizhu-info {
  margin-top: 16px;
}

.info-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  font-weight: 600;
  color: #666;
  margin-right: 8px;
}

.info-item .value {
  color: #333;
}

.analysis-content {
  line-height: 1.8;
  color: #333;
}

.wuxing-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.wuxing-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wuxing-name {
  font-weight: 600;
  color: #666;
}

.wuxing-value {
  font-size: 18px;
  font-weight: 600;
  color: #3b82f6;
}

.rizhu-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.shishen-table {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shishen-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shishen-zhu {
  width: 80px;
  font-weight: 600;
  color: #666;
}

.shishen-values {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.shishen-tag {
  padding: 4px 12px;
  background: #f0f9ff;
  border: 1px solid #3b82f6;
  border-radius: 4px;
  font-size: 13px;
  color: #1e40af;
}

.dayun-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dayun-item {
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 4px;
  font-size: 14px;
}

.dayun-label {
  font-weight: 600;
  color: #666;
  margin-right: 8px;
}

.dayun-value {
  font-weight: 600;
  color: #3b82f6;
  margin-right: 8px;
}

.dayun-age {
  color: #999;
}

.shensha-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shensha-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 4px;
}

.shensha-name {
  font-weight: 600;
  color: #333;
}

.shensha-position {
  color: #666;
  font-size: 13px;
}

.shensha-type {
  margin-left: auto;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.type-ji {
  background: #dcfce7;
  color: #16a34a;
}

.type-neutral {
  background: #fef3c7;
  color: #d97706;
}

.no-shensha {
  color: #999;
  text-align: center;
  padding: 20px;
}

.llm-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.llm-card .section-title {
  color: white;
}

.llm-content {
  margin-top: 16px;
}

.llm-text {
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.95);
}

.llm-error {
  margin-top: 16px;
}
</style>


