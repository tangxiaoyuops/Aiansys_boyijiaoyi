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
.ziwei-view {
  height: 100%;
  overflow: hidden;
  background: #111827;
  color: #e5e7eb;
}

.main-layout {
  display: flex;
  height: 100%;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.left-panel {
  width: 350px;
  flex-shrink: 0;
  overflow-y: auto;
}

.right-panel {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}

.input-card {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 24px;
}

.card-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-hint {
  font-size: 13px;
  color: #9ca3af;
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

.result-card {
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 12px;
  padding: 24px;
}

.llm-card {
  background: linear-gradient(135deg, #1f2937 0%, #2d3748 100%);
  border: 1px solid #4a5568;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #374151;
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
  font-weight: 500;
  color: #9ca3af;
  min-width: 80px;
}

.info-item .value {
  color: #e5e7eb;
  font-size: 16px;
  line-height: 1.8;
}

.date-label {
  color: #9ca3af;
  font-weight: 500;
  margin-right: 4px;
}

.gan-zhi {
  color: #a78bfa;
  font-size: 14px;
}

.analysis-content {
  color: #d1d5db;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.analysis-content :deep(pre) {
  background: #111827;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #374151;
  overflow-x: auto;
  color: #d1d5db;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.llm-content {
  color: #e5e7eb;
  line-height: 2;
}

.llm-text {
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 滚动条样式 */
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 8px;
}

.left-panel::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: #111827;
}

.left-panel::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 4px;
}

.left-panel::-webkit-scrollbar-thumb:hover,
.right-panel::-webkit-scrollbar-thumb:hover {
  background: #5a6578;
}

.pan-card {
  text-align: center;
}

.si-hua-stats,
.si-hua-summary,
.si-hua-palaces,
.si-hua-warning,
.si-hua-lucky {
  margin: 16px 0;
  padding: 12px;
  background: #111827;
  border-radius: 8px;
  border-left: 3px solid #4a5568;
}

.si-hua-warning {
  border-left-color: #f87171;
  background: #7f1d1d20;
}

.si-hua-lucky {
  border-left-color: #fbbf24;
  background: #78350f20;
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
  color: #f87171;
  padding: 12px;
  background: #7f1d1d20;
  border-radius: 8px;
  border-left: 3px solid #f87171;
}

/* 大限分析样式 */
.daxian-summary,
.daxian-current,
.daxian-palace,
.daxian-impact {
  margin: 16px 0;
  padding: 12px;
  background: #111827;
  border-radius: 8px;
  border-left: 3px solid #4a5568;
}

.daxian-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  background: #111827;
}

.daxian-table th,
.daxian-table td {
  padding: 8px 12px;
  text-align: left;
  border: 1px solid #374151;
}

.daxian-table th {
  background: #1f2937;
  font-weight: 600;
  color: #e5e7eb;
}

.daxian-table td {
  color: #d1d5db;
}

.daxian-table tr:nth-child(even) {
  background: #1a1f2e;
}

/* 格局分析样式 */
.geju-summary,
.geju-detected,
.geju-details,
.geju-triangular,
.geju-four-corners {
  margin: 16px 0;
  padding: 12px;
  background: #111827;
  border-radius: 8px;
  border-left: 3px solid #4a5568;
}

.geju-item {
  margin: 12px 0;
  padding: 12px;
  background: #1a1f2e;
  border-radius: 6px;
}

.geju-item h4 {
  margin: 0 0 8px 0;
  color: #facc15;
  font-size: 16px;
}

.geju-item p {
  margin: 4px 0;
  color: #d1d5db;
}

/* 神煞分析样式 */
.shensha-summary,
.shensha-list {
  margin: 16px 0;
  padding: 12px;
  background: #111827;
  border-radius: 8px;
  border-left: 3px solid #4a5568;
}

.shensha-list ul {
  margin: 8px 0;
  padding-left: 24px;
}

.shensha-list li {
  margin: 4px 0;
  line-height: 1.6;
}
</style>
