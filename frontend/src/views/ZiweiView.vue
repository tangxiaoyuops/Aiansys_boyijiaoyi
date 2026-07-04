<template>
  <div class="ziwei-view">
    <div class="main-layout">
      <!-- 左侧输入区域 -->
      <div class="left-panel">
        <div class="input-card">
          <h2 class="card-title">排盘信息</h2>
          <div class="form-hint">请输入公历日期</div>
          <el-form :model="form" label-width="90px" class="ziwei-form">
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
              <el-checkbox v-model="form.include_daxian">大限分析</el-checkbox>
              <el-checkbox v-model="form.include_shensha">神煞分析</el-checkbox>
              <el-checkbox v-model="form.include_geju">格局分析</el-checkbox>
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

        <!-- 结果展示 - 使用标签页切换 -->
        <div v-if="result && !loading" class="result-wrapper">
          <el-tabs v-model="activeResultTab" class="result-tabs">
            <!-- 命盘分析标签 -->
            <el-tab-pane label="命盘分析" name="analysis">
              <div class="analysis-tab-content">
                <div class="result-container">
                  <!-- 完整命盘图 -->
                  <div v-if="result.pan_data" class="result-card pan-card">
                    <h3 class="section-title">
                      <el-icon><Document /></el-icon>
                      完整命盘
                    </h3>
                    <ZiweiPan :pan-data="result.pan_data" :size="800" />
                    <div class="pan-basic-info">
                      <div class="info-item">
                        <span class="label">命宫：</span>
                        <span class="value">{{ getPalaceName(result.pan_data.ming_gong) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">身宫：</span>
                        <span class="value">{{ getPalaceName(result.pan_data.shen_gong) }}</span>
                      </div>
                      <div v-if="result.pan_data.birth_info" class="info-item">
                        <span class="label">出生信息：</span>
                        <span class="value">
                          <span class="date-label">公历：</span>
                          {{ result.pan_data.birth_info.year }}年
                          {{ result.pan_data.birth_info.month }}月
                          {{ result.pan_data.birth_info.day }}日
                          {{ result.pan_data.birth_info.hour }}时
                          <template v-if="result.pan_data.birth_info.lunar_year">
                            <br />
                            <span class="date-label">农历：</span>
                            {{ result.pan_data.birth_info.lunar_year }}年
                            {{ result.pan_data.birth_info.lunar_month }}月
                            {{ result.pan_data.birth_info.lunar_day }}日
                          </template>
                          <br />
                          <span class="gan-zhi">({{ result.pan_data.birth_info.year_gan }}{{ result.pan_data.birth_info.year_zhi }}年)</span>
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 四化分析 -->
                  <div v-if="result.si_hua_analysis" class="result-card">
                    <h3 class="section-title">
                      <el-icon><Star /></el-icon>
                      四化星分析
                    </h3>
                    <div class="analysis-content" v-html="formatSiHuaAnalysis(result.si_hua_analysis)"></div>
                  </div>

                  <!-- 大限分析 -->
                  <div v-if="result.daxian_analysis" class="result-card">
                    <h3 class="section-title">
                      <el-icon><Calendar /></el-icon>
                      大限分析
                    </h3>
                    <div class="analysis-content" v-html="formatDaxianAnalysis(result.daxian_analysis)"></div>
                  </div>

                  <!-- 神煞分析 -->
                  <div v-if="result.shensha_analysis" class="result-card">
                    <h3 class="section-title">
                      <el-icon><Sunny /></el-icon>
                      神煞分析
                    </h3>
                    <div class="analysis-content" v-html="formatShenshaAnalysis(result.shensha_analysis)"></div>
                  </div>

                  <!-- 格局分析 -->
                  <div v-if="result.geju_analysis" class="result-card">
                    <h3 class="section-title">
                      <el-icon><Grid /></el-icon>
                      格局分析
                    </h3>
                    <div class="analysis-content" v-html="formatGejuAnalysis(result.geju_analysis)"></div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <!-- AI对话标签 -->
            <el-tab-pane label="AI对话" name="chat">
              <div class="chat-tab-content">
                <ZiweiChatPanel 
                  :llm-loading="llmLoading"
                  :llm-progress="llmProgress"
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
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import api from '../api';
import { MagicStick, Document, Star, Calendar, Sunny, Grid, ChatLineRound, Loading } from '@element-plus/icons-vue';
import ZiweiPan from '../components/ZiweiPan.vue';
import ZiweiChatPanel from '../components/ZiweiChatPanel.vue';
import { useZiweiChatStore } from '../stores/ziweiChat';

const loading = ref(false);
const llmLoading = ref(false);
const result = ref<any>(null);
const progressMessage = ref('');
const llmProgress = ref('');
const activeResultTab = ref('analysis');

const chatStore = useZiweiChatStore();

onMounted(() => {
  console.log('ZiweiView 组件已挂载');
});

const form = reactive({
  year: new Date().getFullYear(),
  month: 1,
  day: 1,
  hour: 11,
  gender: '男',
  include_daxian: true,
  include_shensha: true,
  include_geju: true,
  include_llm: true,  // 保留选项，但处理方式不同
});

const getPalaceName = (index: number) => {
  const names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母'];
  return names[index] || '未知';
};

const formatAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  if (analysis.summary) return analysis.summary;
  if (analysis.description) return analysis.description;
  if (analysis.analysis) return analysis.analysis;
  
  const formatted = JSON.stringify(analysis, null, 2);
  return `<pre style="white-space: pre-wrap; word-wrap: break-word;">${formatted}</pre>`;
};

const formatSiHuaAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  if (analysis.statistics) {
    html += '<div class="si-hua-stats">';
    html += `<p><strong>四化星统计：</strong></p>`;
    html += `<ul>`;
    if (analysis.statistics.化禄_count) html += `<li>化禄：${analysis.statistics.化禄_count}个</li>`;
    if (analysis.statistics.化权_count) html += `<li>化权：${analysis.statistics.化权_count}个</li>`;
    if (analysis.statistics.化科_count) html += `<li>化科：${analysis.statistics.化科_count}个</li>`;
    if (analysis.statistics.化忌_count) html += `<li>化忌：${analysis.statistics.化忌_count}个</li>`;
    html += `</ul>`;
    html += '</div>';
  }
  
  if (analysis.summary) {
    html += `<div class="si-hua-summary">${analysis.summary}</div>`;
  }
  
  if (analysis.palace_analysis && analysis.palace_analysis.length > 0) {
    html += '<div class="si-hua-palaces"><p><strong>各宫位四化情况：</strong></p><ul>';
    analysis.palace_analysis.forEach((item: any) => {
      html += `<li><strong>${item.palace}：</strong>${item.si_hua.join('、')}`;
      if (item.impact) html += ` - ${item.impact}`;
      html += `</li>`;
    });
    html += '</ul></div>';
  }
  
  if (analysis.hua_ji_analysis) {
    html += `<div class="si-hua-warning"><p><strong>化忌重点分析：</strong></p>`;
    const huaJi = analysis.hua_ji_analysis;
    
    if (huaJi.message) {
      html += `<p>${huaJi.message}</p>`;
    } else {
      if (huaJi.locations && huaJi.locations.length > 0) {
        html += `<p><strong>化忌位置：</strong></p><ul>`;
        huaJi.locations.forEach((loc: any) => {
          html += `<li>${loc.palace} - ${loc.star}化忌${loc.is_ming_gong ? '（命宫，需特别注意）' : ''}</li>`;
        });
        html += `</ul>`;
      }
      
      if (huaJi.warnings && huaJi.warnings.length > 0) {
        html += `<p><strong>注意事项：</strong></p><ul>`;
        huaJi.warnings.forEach((warning: string) => {
          html += `<li>${warning}</li>`;
        });
        html += `</ul>`;
      }
    }
    html += `</div>`;
  }
  
  if (analysis.hua_lu_analysis) {
    html += `<div class="si-hua-lucky"><p><strong>化禄重点分析：</strong></p>`;
    const huaLu = analysis.hua_lu_analysis;
    
    if (huaLu.message) {
      html += `<p>${huaLu.message}</p>`;
    } else {
      if (huaLu.locations && huaLu.locations.length > 0) {
        html += `<p><strong>化禄位置：</strong></p><ul>`;
        huaLu.locations.forEach((loc: any) => {
          html += `<li>${loc.palace} - ${loc.star}化禄${loc.is_ming_gong ? '（命宫，自身财运好）' : ''}</li>`;
        });
        html += `</ul>`;
      }
      
      if (huaLu.opportunities && huaLu.opportunities.length > 0) {
        html += `<p><strong>财运机会：</strong></p><ul>`;
        huaLu.opportunities.forEach((opp: string) => {
          html += `<li>${opp}</li>`;
        });
        html += `</ul>`;
      }
    }
    html += `</div>`;
  }
  
  return html || formatAnalysis(analysis);
};

const formatDaxianAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  const daxianData = analysis.daxian_analysis || analysis;
  
  if (daxianData.summary) {
    html += `<div class="daxian-summary"><p>${daxianData.summary}</p></div>`;
  }
  
  const currentDaxian = analysis.current_daxian || daxianData.current_daxian;
  if (currentDaxian) {
    html += '<div class="daxian-current"><p><strong>当前大限：</strong></p>';
    html += `<p>第${currentDaxian.number}大限，${currentDaxian.start_age}-${currentDaxian.end_age}岁，位于${getPalaceName(currentDaxian.palace)}宫</p>`;
    html += '</div>';
  }
  
  const allDaxian = analysis.all_daxian;
  if (allDaxian && Array.isArray(allDaxian) && allDaxian.length > 0) {
    html += '<div class="daxian-all"><p><strong>所有大限：</strong></p>';
    html += '<table class="daxian-table"><thead><tr><th>序号</th><th>年龄</th><th>宫位</th><th>方向</th></tr></thead><tbody>';
    allDaxian.forEach((daxian: any) => {
      html += `<tr>`;
      html += `<td>${daxian.number || daxian.index + 1}</td>`;
      html += `<td>${daxian.start_age}-${daxian.end_age}岁</td>`;
      html += `<td>${getPalaceName(daxian.palace)}</td>`;
      html += `<td>${daxian.direction || '未知'}</td>`;
      html += `</tr>`;
    });
    html += '</tbody></table></div>';
  }
  
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatShenshaAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  const shenshaData = analysis.shensha_analysis || analysis;
  
  if (shenshaData.summary) {
    html += `<div class="shensha-summary"><p>${shenshaData.summary}</p></div>`;
  }
  
  if (shenshaData.shensha_list && Array.isArray(shenshaData.shensha_list)) {
    html += '<div class="shensha-list"><p><strong>神煞分布：</strong></p><ul>';
    shenshaData.shensha_list.forEach((item: any) => {
      html += `<li><strong>${item.name}：</strong>${getPalaceName(item.palace)}`;
      if (item.impact) {
        html += ` - ${item.impact}`;
      }
      html += `</li>`;
    });
    html += '</ul></div>';
  }
  
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatGejuAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  const gejuData = analysis.geju_analysis || analysis;
  
  if (gejuData.summary) {
    html += `<div class="geju-summary"><p>${gejuData.summary}</p></div>`;
  }
  
  if (gejuData.detected_geju && Object.keys(gejuData.detected_geju).length > 0) {
    html += '<div class="geju-detected"><p><strong>检测到的格局：</strong></p><ul>';
    Object.entries(gejuData.detected_geju).forEach(([gejuName, gejuInfo]: [string, any]) => {
      html += `<li><strong>${gejuName}：</strong>`;
      if (gejuInfo.description) {
        html += gejuInfo.description;
      }
      html += `</li>`;
    });
    html += '</ul></div>';
  }
  
  if (gejuData.geju_analysis && Object.keys(gejuData.geju_analysis).length > 0) {
    html += '<div class="geju-details"><p><strong>格局详细分析：</strong></p>';
    Object.entries(gejuData.geju_analysis).forEach(([gejuName, gejuDetail]: [string, any]) => {
      html += `<div class="geju-item">`;
      html += `<h4>${gejuName}</h4>`;
      if (gejuDetail.impact) {
        html += `<p><strong>影响：</strong>${gejuDetail.impact}</p>`;
      }
      if (gejuDetail.description) {
        html += `<p><strong>描述：</strong>${gejuDetail.description}</p>`;
      }
      html += `</div>`;
    });
    html += '</div>';
  }
  
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatLLMResponse = (response: string): string => {
  if (!response) return '';
  return response.replace(/\n/g, '<br>');
};

const handleAnalyze = async () => {
  loading.value = true;
  result.value = null;
  llmProgress.value = '';
  
  // 清空之前的对话
  chatStore.reset();
  chatStore.clearZiweiContext();
  
  try {
    console.log('开始排盘分析:', form);
    
    // 第一步：排盘（不包含LLM，快速返回）
    const response = await api.post('/api/ziwei/pan', {
      year: form.year,
      month: form.month,
      day: form.day,
      hour: form.hour,
      gender: form.gender,
      include_daxian: form.include_daxian,
      include_shensha: form.include_shensha,
      include_geju: form.include_geju,
      include_llm: false,  // 排盘时不调用LLM，快速返回
    });
    console.log('排盘结果:', response.data);
    result.value = response.data;
    
    // 设置对话上下文
    chatStore.setZiweiContext({
      pan_data: response.data.pan_data,
      si_hua_analysis: response.data.si_hua_analysis,
      daxian_analysis: response.data.daxian_analysis,
      liunian_analysis: response.data.liunian_analysis,
      shensha_analysis: response.data.shensha_analysis,
      geju_analysis: response.data.geju_analysis,
      llm_analysis: null,  // LLM分析稍后获取
      gender: form.gender,
      birth_info: response.data.pan_data?.birth_info || null,
    });
    
  } catch (error: any) {
    console.error('排盘失败:', error);
    ElMessage.error('排盘失败: ' + (error.response?.data?.detail || error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
  
  // 第二步：如果勾选了AI深度解析，调用流式LLM接口
  if (form.include_llm && result.value) {
    await fetchZiweiLLMStream();
  }
};

const fetchZiweiLLMStream = async () => {
  llmLoading.value = true;
  llmProgress.value = 'AI正在深度分析...';
  
  // 添加一条空的助手消息，用于流式更新（显示在"AI对话"标签页）
  chatStore.appendAssistantMessage('', 'analysis');
  
  try {
    const requestBody = {
      year: form.year,
      month: form.month,
      day: form.day,
      hour: form.hour,
      gender: form.gender,
      pan_data: result.value?.pan_data || null,
      si_hua_analysis: result.value?.si_hua_analysis || null,
      daxian_analysis: result.value?.daxian_analysis || null,
      shensha_analysis: result.value?.shensha_analysis || null,
      geju_analysis: result.value?.geju_analysis || null,
    };
    
    const response = await fetch('/api/ziwei/llm-stream', {
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
          
          if (payload.type === 'progress') {
            llmProgress.value = payload.message || '';
          }
          else if (payload.type === 'content' && payload.content) {
            // 流式更新对话中的分析消息
            chatStore.updateFirstAssistantMessage(payload.content);
          }
          else if (payload.type === 'done') {
            if (payload.full_content) {
              // 替换完整内容
              chatStore.updateFirstAssistantMessage(payload.full_content, true);
              // 更新对话上下文，供追问使用
              chatStore.setZiweiContext({
                llm_analysis: payload.full_content,
              });
            }
          }
        } catch (e) {
          console.error('[ZiweiView] 解析错误:', e);
        }
      }
    }
  } catch (error: any) {
    console.error('LLM流式解析失败:', error);
    ElMessage.error('AI分析失败: ' + (error.message || '未知错误'));
  } finally {
    llmLoading.value = false;
    llmProgress.value = '';
  }
};
</script>


<style scoped>
/* 优雅明亮主题色彩变量 */
.ziwei-view {
  --mystical-bg: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #f0f4f8 100%);
  --mystical-surface: rgba(255, 255, 255, 0.85);
  --mystical-primary: #6366f1;
  --mystical-secondary: #818cf8;
  --mystical-accent: #f59e0b;
  --mystical-text: #1e293b;
  --mystical-text-light: #64748b;
  --mystical-border: rgba(99, 102, 241, 0.2);
  --mystical-border-light: rgba(148, 163, 184, 0.3);
}

.ziwei-view {
  height: 100%;
  overflow: hidden;
  background: var(--mystical-bg);
  color: var(--mystical-text);
  position: relative;
}

/* 柔和光效背景 */
.ziwei-view::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 80% 70%, rgba(245, 158, 11, 0.06) 0%, transparent 60%);
  z-index: 0;
  pointer-events: none;
}

.main-layout {
  display: flex;
  height: 100%;
  gap: 24px;
  padding: 24px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.left-panel {
  width: 360px;
  flex-shrink: 0;
  overflow-y: auto;
}

.right-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* 卡片样式 */
.input-card {
  background: var(--mystical-surface);
  border: 1px solid var(--mystical-border-light);
  border-radius: 20px;
  padding: 24px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.card-title {
  margin: 0 0 20px 0;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--mystical-primary) 0%, var(--mystical-accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-hint {
  font-size: 13px;
  color: var(--mystical-text-light);
  margin-bottom: 12px;
}

.ziwei-form {
  margin-top: 16px;
}

.empty-state,
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  background: var(--mystical-surface);
  border-radius: 20px;
}

/* 结果包装器 */
.result-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--mystical-surface);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

/* 标签页样式 */
.result-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.result-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 20px;
  background: rgba(99, 102, 241, 0.05);
  border-bottom: 1px solid var(--mystical-border-light);
}

.result-tabs :deep(.el-tabs__nav-wrap) {
  padding: 10px 0;
}

.result-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  padding: 0 24px;
  height: 40px;
  line-height: 40px;
  color: var(--mystical-text-light);
}

.result-tabs :deep(.el-tabs__item.is-active) {
  color: var(--mystical-primary);
  font-weight: 600;
}

.result-tabs :deep(.el-tabs__active-bar) {
  background-color: var(--mystical-primary);
}

.result-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

.result-tabs :deep(.el-tab-pane) {
  height: 100%;
}

/* 分析标签内容 */
.analysis-tab-content {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

/* 对话标签内容 */
.chat-tab-content {
  height: 100%;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--mystical-border-light);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(10px);
}

.llm-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(245, 158, 11, 0.06) 100%);
  border: 2px solid rgba(99, 102, 241, 0.25);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--mystical-text);
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--mystical-border-light);
}

.pan-card {
  text-align: center;
}

.pan-basic-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  margin-top: 16px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  padding: 6px 0;
}

.info-item .label {
  font-weight: 600;
  color: var(--mystical-text-light);
  min-width: 80px;
}

.info-item .value {
  color: var(--mystical-text);
  font-size: 15px;
  line-height: 1.7;
}

.date-label {
  color: var(--mystical-text-light);
  font-weight: 500;
  margin-right: 4px;
}

.gan-zhi {
  color: var(--mystical-primary);
  font-size: 14px;
  font-weight: 600;
}

.analysis-content {
  color: var(--mystical-text);
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.llm-content {
  color: var(--mystical-text);
  line-height: 1.9;
}

.llm-text {
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.llm-error {
  color: #dc2626;
  padding: 12px;
  background: rgba(254, 226, 226, 0.6);
  border-radius: 10px;
}

.llm-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--mystical-primary);
  font-size: 15px;
  padding: 16px;
  background: rgba(99, 102, 241, 0.08);
  border-radius: 10px;
}

.llm-loading .el-icon {
  font-size: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 滚动条样式 */
.left-panel::-webkit-scrollbar,
.analysis-tab-content::-webkit-scrollbar {
  width: 8px;
}

.left-panel::-webkit-scrollbar-track,
.analysis-tab-content::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.8);
  border-radius: 4px;
}

.left-panel::-webkit-scrollbar-thumb,
.analysis-tab-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--mystical-primary), var(--mystical-secondary));
  border-radius: 4px;
}

/* 分析样式 */
.si-hua-stats,
.si-hua-summary,
.si-hua-palaces,
.si-hua-warning,
.si-hua-lucky {
  margin: 12px 0;
  padding: 12px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 10px;
  border-left: 3px solid var(--mystical-border-light);
}

.si-hua-warning {
  border-left-color: #ef4444;
  background: rgba(254, 226, 226, 0.6);
}

.si-hua-lucky {
  border-left-color: var(--mystical-accent);
  background: rgba(254, 243, 199, 0.6);
}

.si-hua-stats ul,
.si-hua-palaces ul,
.shensha-list ul {
  margin: 6px 0;
  padding-left: 20px;
}

.si-hua-stats li,
.si-hua-palaces li,
.shensha-list li {
  margin: 3px 0;
  line-height: 1.6;
}

.daxian-summary,
.daxian-current,
.shensha-summary,
.geju-summary,
.geju-detected {
  margin: 12px 0;
  padding: 12px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 10px;
  border-left: 3px solid var(--mystical-border-light);
}

.daxian-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  overflow: hidden;
}

.daxian-table th,
.daxian-table td {
  padding: 10px 14px;
  text-align: left;
  border: 1px solid var(--mystical-border-light);
}

.daxian-table th {
  background: rgba(99, 102, 241, 0.1);
  font-weight: 600;
}

.geju-item {
  margin: 10px 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
}

.geju-item h4 {
  margin: 0 0 6px 0;
  color: var(--mystical-accent);
  font-size: 16px;
  font-weight: 700;
}

/* 响应式 */
@media (max-width: 1200px) {
  .main-layout {
    gap: 20px;
    padding: 20px;
  }
  
  .left-panel {
    width: 320px;
  }
}

@media (max-width: 992px) {
  .main-layout {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
    height: auto;
    min-height: 100%;
  }
  
  .left-panel {
    width: 100%;
  }
  
  .right-panel {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .main-layout {
    padding: 12px;
    gap: 12px;
  }
  
  .input-card {
    padding: 16px;
    border-radius: 16px;
  }
  
  .card-title {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .result-wrapper {
    border-radius: 16px;
  }
  
  .result-tabs :deep(.el-tabs__header) {
    padding: 0 12px;
  }
  
  .result-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 16px;
  }
  
  .analysis-tab-content {
    padding: 12px;
  }
  
  .result-card {
    padding: 14px;
    border-radius: 12px;
  }
  
  .section-title {
    font-size: 15px;
  }
}
</style>
