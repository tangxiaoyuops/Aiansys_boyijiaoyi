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

        <div v-if="result && !loading" class="result-container">
          <!-- 完整命盘图 -->
          <div v-if="result.pan_data" class="result-card pan-card">
            <h3 class="section-title">
              <el-icon><Document /></el-icon>
              完整命盘
            </h3>
            <ZiweiPan :pan-data="result.pan_data" :size="900" />
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

          <!-- LLM深度分析 -->
          <div v-if="result.llm_analysis" class="result-card llm-card">
            <h3 class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              AI深度解析
            </h3>
            <div class="llm-content">
              <div v-if="result.llm_analysis.response" class="llm-text" v-html="formatLLMResponse(result.llm_analysis.response)"></div>
              <div v-else-if="result.llm_analysis.error" class="llm-error">
                <p>⚠️ LLM分析失败: {{ result.llm_analysis.error }}</p>
              </div>
              <div v-else class="llm-text">{{ formatAnalysis(result.llm_analysis) }}</div>
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
import api from '../api';
import { MagicStick, Document, Star, Calendar, Sunny, Grid, ChatLineRound } from '@element-plus/icons-vue';
import ZiweiPan from '../components/ZiweiPan.vue';

const loading = ref(false);
const result = ref<any>(null);

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
  include_llm: true,
});

const getPalaceName = (index: number) => {
  const names = ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄', '迁移', '奴仆', '官禄', '田宅', '福德', '父母'];
  return names[index] || '未知';
};

const formatAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  // 尝试提取summary或description
  if (analysis.summary) return analysis.summary;
  if (analysis.description) return analysis.description;
  if (analysis.analysis) return analysis.analysis;
  
  // 如果是对象，格式化显示
  const formatted = JSON.stringify(analysis, null, 2);
  return `<pre style="white-space: pre-wrap; word-wrap: break-word;">${formatted}</pre>`;
};

const formatSiHuaAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  // 显示统计信息
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
  
  // 显示详细分析
  if (analysis.summary) {
    html += `<div class="si-hua-summary">${analysis.summary}</div>`;
  }
  
  // 显示宫位分析
  if (analysis.palace_analysis && analysis.palace_analysis.length > 0) {
    html += '<div class="si-hua-palaces"><p><strong>各宫位四化情况：</strong></p><ul>';
    analysis.palace_analysis.forEach((item: any) => {
      html += `<li><strong>${item.palace}：</strong>${item.si_hua.join('、')}`;
      if (item.impact) html += ` - ${item.impact}`;
      html += `</li>`;
    });
    html += '</ul></div>';
  }
  
  // 显示化忌重点分析
  if (analysis.hua_ji_analysis) {
    html += `<div class="si-hua-warning"><p><strong>⚠️ 化忌重点分析：</strong></p>`;
    const huaJi = analysis.hua_ji_analysis;
    
    // 如果有message（无化忌的情况）
    if (huaJi.message) {
      html += `<p>${huaJi.message}</p>`;
    } else {
      // 显示化忌位置
      if (huaJi.locations && huaJi.locations.length > 0) {
        html += `<p><strong>化忌位置：</strong></p><ul>`;
        huaJi.locations.forEach((loc: any) => {
          html += `<li>${loc.palace} - ${loc.star}化忌${loc.is_ming_gong ? '（命宫，需特别注意）' : ''}</li>`;
        });
        html += `</ul>`;
      }
      
      // 显示警告信息
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
  
  // 显示化禄重点分析
  if (analysis.hua_lu_analysis) {
    html += `<div class="si-hua-lucky"><p><strong>💰 化禄重点分析：</strong></p>`;
    const huaLu = analysis.hua_lu_analysis;
    
    // 如果有message（无化禄的情况）
    if (huaLu.message) {
      html += `<p>${huaLu.message}</p>`;
    } else {
      // 显示化禄位置
      if (huaLu.locations && huaLu.locations.length > 0) {
        html += `<p><strong>化禄位置：</strong></p><ul>`;
        huaLu.locations.forEach((loc: any) => {
          html += `<li>${loc.palace} - ${loc.star}化禄${loc.is_ming_gong ? '（命宫，自身财运好）' : ''}</li>`;
        });
        html += `</ul>`;
      }
      
      // 显示机会信息
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
  
  // 处理嵌套的 daxian_analysis 结构
  const daxianData = analysis.daxian_analysis || analysis;
  
  // 显示总结
  if (daxianData.summary) {
    html += `<div class="daxian-summary"><p>${daxianData.summary}</p></div>`;
  }
  
  // 显示当前大限
  const currentDaxian = analysis.current_daxian || daxianData.current_daxian;
  if (currentDaxian) {
    html += '<div class="daxian-current"><p><strong>当前大限：</strong></p>';
    html += `<p>第${currentDaxian.number}大限，${currentDaxian.start_age}-${currentDaxian.end_age}岁，位于${getPalaceName(currentDaxian.palace)}宫</p>`;
    html += '</div>';
  }
  
  // 显示所有大限列表
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
  
  // 显示大限宫位分析
  if (daxianData.palace) {
    html += '<div class="daxian-palace"><p><strong>大限宫位：</strong></p>';
    const palace = daxianData.palace;
    html += `<p>${palace.name || getPalaceName(palace.index)}</p>`;
    if (palace.main_stars && palace.main_stars.length > 0) {
      html += `<p>主星：${palace.main_stars.join('、')}</p>`;
    }
    if (palace.auxiliary_stars && palace.auxiliary_stars.length > 0) {
      html += `<p>辅星：${palace.auxiliary_stars.join('、')}</p>`;
    }
    html += '</div>';
  }
  
  // 显示大限影响分析
  if (daxianData.analysis) {
    html += '<div class="daxian-impact"><p><strong>大限影响：</strong></p>';
    const impact = daxianData.analysis;
    if (impact.main_stars) {
      html += `<p>主星影响：${impact.main_stars.summary || JSON.stringify(impact.main_stars)}</p>`;
    }
    if (impact.auxiliary_stars) {
      html += `<p>辅星影响：${impact.auxiliary_stars.summary || JSON.stringify(impact.auxiliary_stars)}</p>`;
    }
    if (impact.si_hua) {
      html += `<p>四化影响：${impact.si_hua.summary || JSON.stringify(impact.si_hua)}</p>`;
    }
    html += '</div>';
  }
  
  // 如果没有格式化内容，显示原始数据（降级处理）
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatShenshaAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  // 处理嵌套的 shensha_analysis 结构
  const shenshaData = analysis.shensha_analysis || analysis;
  
  // 显示总结
  if (shenshaData.summary) {
    html += `<div class="shensha-summary"><p>${shenshaData.summary}</p></div>`;
  }
  
  // 显示各神煞分析
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
  
  // 如果没有格式化内容，显示原始数据（降级处理）
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatGejuAnalysis = (analysis: any): string => {
  if (!analysis) return '';
  if (typeof analysis === 'string') return analysis;
  
  let html = '';
  
  // 处理嵌套的 geju_analysis 结构
  const gejuData = analysis.geju_analysis || analysis;
  
  // 显示总结
  if (gejuData.summary) {
    html += `<div class="geju-summary"><p>${gejuData.summary}</p></div>`;
  }
  
  // 显示检测到的格局
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
  
  // 显示各格局的详细分析
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
  
  // 显示命宫三方分析
  if (gejuData.ming_gong_triangular) {
    html += '<div class="geju-triangular"><p><strong>命宫三方分析：</strong></p>';
    const triangular = gejuData.ming_gong_triangular;
    if (triangular.main_star_count !== undefined) {
      html += `<p>主星数量：${triangular.main_star_count}个</p>`;
    }
    if (triangular.palaces && Array.isArray(triangular.palaces)) {
      html += `<p>三方宫位：${triangular.palaces.map((p: any) => p.name || p).join('、')}</p>`;
    }
    html += '</div>';
  }
  
  // 显示命宫四正分析
  if (gejuData.ming_gong_four_corners) {
    html += '<div class="geju-four-corners"><p><strong>命宫四正分析：</strong></p>';
    const fourCorners = gejuData.ming_gong_four_corners;
    if (fourCorners.palaces && Array.isArray(fourCorners.palaces)) {
      html += `<p>四正宫位：${fourCorners.palaces.map((p: any) => p.name || p).join('、')}</p>`;
    }
    html += '</div>';
  }
  
  // 如果没有格式化内容，显示原始数据（降级处理）
  if (!html) {
    return formatAnalysis(analysis);
  }
  
  return html;
};

const formatLLMResponse = (response: string): string => {
  if (!response) return '';
  // 将换行符转换为HTML
  return response.replace(/\n/g, '<br>');
};

const handleAnalyze = async () => {
  loading.value = true;
  result.value = null;
  try {
    console.log('开始排盘分析:', form);
    const response = await api.post('/api/ziwei/pan', {
      year: form.year,
      month: form.month,
      day: form.day,
      hour: form.hour,
      gender: form.gender,
      include_daxian: form.include_daxian,
      include_shensha: form.include_shensha,
      include_geju: form.include_geju,
      include_llm: form.include_llm,
    });
    console.log('排盘结果:', response.data);
    result.value = response.data;
  } catch (error: any) {
    console.error('排盘失败:', error);
    ElMessage.error('排盘失败: ' + (error.response?.data?.detail || error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
};
</script>


<style scoped>
/* 优雅明亮主题色彩变量 - 舒适护眼风格 */
.ziwei-view {
  --mystical-bg: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #f0f4f8 100%);
  --mystical-surface: rgba(255, 255, 255, 0.85);
  --mystical-surface-dark: rgba(248, 250, 252, 0.95);
  --mystical-primary: #6366f1;
  --mystical-secondary: #818cf8;
  --mystical-accent: #f59e0b;
  --mystical-glow: #a5b4fc;
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

/* 柔和光效背景 - 明亮优雅 */
.ziwei-view::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 80% 70%, rgba(245, 158, 11, 0.06) 0%, transparent 60%),
    radial-gradient(circle at 50% 50%, rgba(129, 140, 248, 0.05) 0%, transparent 70%);
  animation: backgroundPulse 10s ease-in-out infinite;
  z-index: 0;
  pointer-events: none;
}

@keyframes backgroundPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.05);
  }
}

/* 柔和装饰粒子 */
.ziwei-view::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(1px 1px at 30px 40px, rgba(99, 102, 241, 0.3), transparent),
    radial-gradient(1px 1px at 70px 80px, rgba(245, 158, 11, 0.25), transparent),
    radial-gradient(0.5px 0.5px at 120px 100px, rgba(129, 140, 248, 0.2), transparent);
  background-repeat: repeat;
  background-size: 300px 300px;
  animation: gentleTwinkle 12s linear infinite;
  z-index: 0;
  pointer-events: none;
  opacity: 0.4;
}

@keyframes gentleTwinkle {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.6; }
}

.main-layout {
  display: flex;
  height: 100%;
  gap: 24px;
  padding: 24px;
  overflow: hidden;
  position: relative;
  z-index: 1;
  perspective: 2000px;
}

.left-panel {
  width: 380px;
  flex-shrink: 0;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.right-panel {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
  position: relative;
  z-index: 1;
}

/* 明亮玻璃态卡片 - 优雅风格 */
.input-card {
  background: var(--mystical-surface);
  border: 1px solid var(--mystical-border-light);
  border-radius: 24px;
  padding: 28px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 16px rgba(99, 102, 241, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform-style: preserve-3d;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: cardFloat 8s ease-in-out infinite;
  position: relative;
  overflow: hidden;
}

.input-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(99, 102, 241, 0.05), transparent);
  animation: cardShine 4s infinite;
  pointer-events: none;
}

@keyframes cardFloat {
  0%, 100% {
    transform: translateY(0px) rotateX(0deg);
  }
  50% {
    transform: translateY(-8px) rotateX(2deg);
  }
}

@keyframes cardShine {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.input-card:hover {
  transform: translateY(-6px) rotateX(2deg) rotateY(1deg);
  box-shadow: 
    0 16px 48px rgba(0, 0, 0, 0.12),
    0 4px 24px rgba(99, 102, 241, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 1);
  border-color: rgba(99, 102, 241, 0.4);
}

.card-title {
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--mystical-primary) 0%, var(--mystical-accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
  animation: titleGlow 3s ease-in-out infinite;
  letter-spacing: 1px;
}


.form-hint {
  font-size: 13px;
  color: var(--mystical-text-light);
  margin-bottom: 12px;
  padding-left: 4px;
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
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 明亮结果卡片 - 优雅玻璃态 */
.result-card {
  background: var(--mystical-surface);
  border: 1px solid var(--mystical-border-light);
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 16px rgba(99, 102, 241, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform-style: preserve-3d;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: resultCardEnter 0.6s ease-out;
}

@keyframes resultCardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) rotateX(-10deg);
  }
  to {
    opacity: 1;
    transform: translateY(0) rotateX(0deg);
  }
}

.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.08), transparent);
  transition: left 0.5s;
}

.result-card:hover {
  transform: translateY(-8px) rotateX(2deg) rotateY(1deg);
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.1),
    0 4px 24px rgba(99, 102, 241, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 1);
  border-color: rgba(99, 102, 241, 0.4);
}

.result-card:hover::before {
  left: 100%;
}

.llm-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(245, 158, 11, 0.08) 100%);
  border: 2px solid rgba(99, 102, 241, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 0 30px rgba(99, 102, 241, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.llm-card::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, var(--mystical-primary), var(--mystical-accent), var(--mystical-primary));
  background-size: 200% 200%;
  border-radius: 24px;
  opacity: 0.2;
  z-index: -1;
  filter: blur(8px);
  animation: borderGlow 4s ease-in-out infinite;
}

@keyframes borderGlow {
  0%, 100% {
    opacity: 0.2;
    background-position: 0% 50%;
  }
  50% {
    opacity: 0.4;
    background-position: 100% 50%;
  }
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--mystical-text);
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--mystical-border-light);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--mystical-primary), var(--mystical-secondary), var(--mystical-accent));
  border-radius: 2px;
  animation: titleUnderline 4s ease-in-out infinite;
}

@keyframes titleUnderline {
  0%, 100% {
    width: 80px;
    opacity: 1;
  }
  50% {
    width: 150px;
    opacity: 0.8;
  }
}

.pan-basic-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
}

.info-item .label {
  font-weight: 600;
  color: var(--mystical-text-light);
  min-width: 80px;
}

.info-item .value {
  color: var(--mystical-text);
  font-size: 16px;
  line-height: 1.8;
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

.analysis-content :deep(pre) {
  background: rgba(241, 245, 249, 0.8);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--mystical-border-light);
  overflow-x: auto;
  color: var(--mystical-text);
  font-family: 'Courier New', monospace;
  font-size: 14px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.llm-content {
  color: var(--mystical-text);
  line-height: 2;
}

.llm-text {
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--mystical-text);
}

/* 优雅滚动条样式 */
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 10px;
}

.left-panel::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: rgba(241, 245, 249, 0.8);
  border-radius: 5px;
}

.left-panel::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--mystical-primary), var(--mystical-secondary));
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
  transition: all 0.3s;
}

.left-panel::-webkit-scrollbar-thumb:hover,
.right-panel::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, var(--mystical-secondary), var(--mystical-primary));
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.4);
}

.pan-card {
  text-align: center;
  overflow: visible;
}

.pan-card .ziwei-pan-wrapper {
  margin: 20px 0;
  min-height: 800px;
  height: auto;
}

/* 命盘容器特殊样式 */
.pan-card .result-card {
  overflow: visible;
  padding: 0;
}

.pan-card .section-title {
  padding: 24px 32px 20px;
  margin: 0;
}

.si-hua-stats,
.si-hua-summary,
.si-hua-palaces,
.si-hua-warning,
.si-hua-lucky {
  margin: 16px 0;
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  border-left: 4px solid var(--mystical-border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
.si-hua-palaces ul {
  margin: 8px 0;
  padding-left: 24px;
}

.si-hua-stats li,
.si-hua-palaces li {
  margin: 4px 0;
  line-height: 1.6;
}

.llm-error {
  color: #dc2626;
  padding: 16px;
  background: rgba(254, 226, 226, 0.6);
  border-radius: 12px;
  border-left: 4px solid #ef4444;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 大限分析样式 */
.daxian-summary,
.daxian-current,
.daxian-palace,
.daxian-impact {
  margin: 16px 0;
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  border-left: 4px solid var(--mystical-border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.daxian-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  background: var(--mystical-surface);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.daxian-table th,
.daxian-table td {
  padding: 12px 16px;
  text-align: left;
  border: 1px solid var(--mystical-border-light);
}

.daxian-table th {
  background: rgba(99, 102, 241, 0.1);
  font-weight: 600;
  color: var(--mystical-text);
}

.daxian-table td {
  color: var(--mystical-text);
}

.daxian-table tr:nth-child(even) {
  background: rgba(248, 250, 252, 0.5);
}

/* 格局分析样式 */
.geju-summary,
.geju-detected,
.geju-details,
.geju-triangular,
.geju-four-corners {
  margin: 16px 0;
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  border-left: 4px solid var(--mystical-border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.geju-item {
  margin: 12px 0;
  padding: 16px;
  background: var(--mystical-surface);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.geju-item h4 {
  margin: 0 0 8px 0;
  color: var(--mystical-accent);
  font-size: 18px;
  font-weight: 700;
}

.geju-item p {
  margin: 6px 0;
  color: var(--mystical-text);
  line-height: 1.6;
}

/* 神煞分析样式 */
.shensha-summary,
.shensha-list {
  margin: 16px 0;
  padding: 16px;
  background: rgba(241, 245, 249, 0.6);
  border-radius: 12px;
  border-left: 4px solid var(--mystical-border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.shensha-list ul {
  margin: 8px 0;
  padding-left: 24px;
}

.shensha-list li {
  margin: 4px 0;
  line-height: 1.6;
}

/* Element Plus 组件样式覆盖 - 3D效果 */
:deep(.el-input-number),
:deep(.el-input),
:deep(.el-select),
:deep(.el-button) {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, var(--mystical-primary) 0%, var(--mystical-accent) 100%);
  border: none;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
  transform: translateZ(0);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(139, 92, 246, 0.4);
}

:deep(.el-button--primary:active) {
  transform: translateY(0);
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner) {
  background: var(--mystical-surface);
  border-color: var(--mystical-border-light);
  color: var(--mystical-text);
  backdrop-filter: blur(10px);
}

:deep(.el-input__inner:focus),
:deep(.el-select .el-input__inner:focus) {
  border-color: var(--mystical-primary);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
  background: rgba(255, 255, 255, 0.95);
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner),
:deep(.el-radio__input.is-checked .el-radio__inner) {
  background-color: var(--mystical-primary);
  border-color: var(--mystical-primary);
}

/* 空状态和加载状态动画 */
.empty-state,
.loading-state {
  position: relative;
  background: var(--mystical-surface);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  border: 1px solid var(--mystical-border-light);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.loading-state :deep(.el-skeleton__item) {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.1) 25%, rgba(99, 102, 241, 0.2) 50%, rgba(99, 102, 241, 0.1) 75%);
  background-size: 200% 100%;
  animation: skeletonLoading 1.5s ease-in-out infinite;
}

@keyframes skeletonLoading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
