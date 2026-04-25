<template>
  <div class="fengshui-view">
    <!-- 顶部进度指示器 -->
    <div class="progress-bar">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          class="step-item"
          :class="{ active: currentStep >= index, completed: currentStep > index }"
        >
          <div class="step-circle">
            <el-icon v-if="currentStep > index"><Check /></el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>
      <div class="progress-line">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 步骤1: 基本信息 -->
      <transition name="slide-fade">
        <div v-if="currentStep === 0" class="step-panel">
          <div class="panel-header">
            <div class="step-icon">👤</div>
            <h2>您好，请告诉我您的基本信息</h2>
            <p class="step-desc">用于计算您的命卦，这是风水分析的基础</p>
          </div>
          
          <div class="input-section">
            <div class="input-group">
              <label class="input-label">
                <span class="label-icon">🎂</span>
                出生年份
              </label>
              <div class="year-selector">
                <el-slider 
                  v-model="form.birth_year" 
                  :min="1940" 
                  :max="2010" 
                  :marks="yearMarks"
                  show-input
                  :show-input-controls="false"
                />
              </div>
              <div class="hint-text">
                <el-icon><InfoFilled /></el-icon>
                {{ form.birth_year }}年出生，今年{{ new Date().getFullYear() - form.birth_year }}岁
              </div>
            </div>
            
            <div class="input-group">
              <label class="input-label">
                <span class="label-icon">⚧</span>
                性别
              </label>
              <div class="gender-cards">
                <div 
                  class="gender-card male"
                  :class="{ selected: form.gender === '男' }"
                  @click="form.gender = '男'"
                >
                  <div class="gender-icon">👨</div>
                  <div class="gender-text">男性</div>
                </div>
                <div 
                  class="gender-card female"
                  :class="{ selected: form.gender === '女' }"
                  @click="form.gender = '女'"
                >
                  <div class="gender-icon">👩</div>
                  <div class="gender-text">女性</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 实时命卦预览 -->
          <transition name="fade">
            <div v-if="showMinguaPreview" class="preview-card">
              <div class="preview-header">
                <el-icon><Star /></el-icon>
                您的命卦预览
              </div>
              <div class="preview-content">
                <div class="mingua-badge" :class="minguaPreview.dong_si_xi_si === '东四命' ? 'dong' : 'xi'">
                  <span class="mingua-char">{{ minguaPreview.mingua }}</span>
                  <span class="mingua-type">{{ minguaPreview.dong_si_xi_si }}</span>
                </div>
                <div class="mingua-info">
                  <div class="info-item">
                    <span class="info-label">命卦五行</span>
                    <span class="info-value">{{ minguaPreview.wuxing }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">命卦数字</span>
                    <span class="info-value">{{ minguaPreview.number }}</span>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </transition>

      <!-- 步骤2: 房屋朝向 -->
      <transition name="slide-fade">
        <div v-if="currentStep === 1" class="step-panel">
          <div class="panel-header">
            <div class="step-icon">🧭</div>
            <h2>您的房屋朝向是？</h2>
            <p class="step-desc">选择房屋的主要采光面方向，即阳台或主窗的朝向</p>
          </div>
          
          <div class="compass-section">
            <!-- 罗盘可视化 -->
            <div class="compass-container">
              <div class="compass">
                <div class="compass-ring outer"></div>
                <div class="compass-ring inner"></div>
                <div class="compass-center">
                  <div class="center-dot"></div>
                </div>
                <!-- 八个方位 -->
                <div 
                  v-for="dir in compassDirections" 
                  :key="dir.name"
                  class="compass-direction"
                  :class="{ selected: isDirectionSelected(dir.name) }"
                  :style="dir.style"
                  @click="selectDirection(dir)"
                >
                  <span class="dir-name">{{ dir.label }}</span>
                  <span class="dir-shan" v-if="form.house_direction">{{ getSelectedShan(dir.name) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 二十四山选择 -->
            <transition name="expand">
              <div v-if="selectedOctant" class="shan-selector">
                <div class="shan-header">
                  <h4>请选择具体山向</h4>
                  <p class="shan-explain">
                    <strong>如何获取？</strong>使用手机指南针APP，站在房屋主要采光面（阳台/窗户）面向外测量，记录指向的方位即可。如果指南针显示约0°（正北），选"子山"；显示约350°，选"壬山"。
                  </p>
                </div>
                <div class="shan-buttons">
                  <div 
                    v-for="shan in currentOctantShans" 
                    :key="shan.value"
                    class="shan-btn"
                    :class="{ selected: form.house_direction === shan.value }"
                    @click="form.house_direction = shan.value; selectedOctant = null"
                  >
                    <span class="shan-char">{{ shan.value }}</span>
                    <span class="shan-label-text">{{ shan.label }}</span>
                  </div>
                </div>
              </div>
            </transition>
          </div>
          
          <!-- 已选择的朝向显示 -->
          <div v-if="form.house_direction" class="selected-direction">
            <el-icon><Compass /></el-icon>
            已选择：<strong>{{ form.house_direction }}山</strong>（{{ getDirectionDetail() }}）
          </div>
        </div>
      </transition>

      <!-- 步骤3: 房屋形状 -->
      <transition name="slide-fade">
        <div v-if="currentStep === 2" class="step-panel">
          <div class="panel-header">
            <div class="step-icon">🏠</div>
            <h2>您的房屋是什么形状？</h2>
            <p class="step-desc">选择最接近的房屋平面形状</p>
          </div>
          
          <div class="shape-selector">
            <div 
              v-for="shape in houseShapes" 
              :key="shape.value"
              class="shape-card"
              :class="{ selected: form.house_shape === shape.value }"
              @click="form.house_shape = shape.value"
            >
              <div class="shape-icon" v-html="shape.icon"></div>
              <div class="shape-name">{{ shape.label }}</div>
              <div class="shape-desc">{{ shape.desc }}</div>
              <div class="shape-score">
                <span class="score-label">格局评分</span>
                <span class="score-value">{{ shape.score }}分</span>
              </div>
            </div>
          </div>
          
          <!-- 房屋形状说明 -->
          <div class="shape-tip">
            <el-icon><WarningFilled /></el-icon>
            <span>{{ getCurrentShapeTip() }}</span>
          </div>
        </div>
      </transition>

      <!-- 步骤4: 职业与选项 -->
      <transition name="slide-fade">
        <div v-if="currentStep === 3" class="step-panel">
          <div class="panel-header">
            <div class="step-icon">💼</div>
            <h2>您的职业类型是？</h2>
            <p class="step-desc">用于优化办公桌摆放建议（可选）</p>
          </div>
          
          <div class="occupation-grid">
            <div 
              v-for="occ in occupations" 
              :key="occ.value"
              class="occupation-card"
              :class="{ selected: form.occupation_type === occ.value }"
              @click="form.occupation_type = occ.value"
            >
              <div class="occ-icon">{{ occ.icon }}</div>
              <div class="occ-name">{{ occ.label }}</div>
              <div class="occ-wuxing">五行：{{ occ.wuxing }}</div>
            </div>
          </div>
          
          <!-- 高级选项 -->
          <div class="advanced-options">
            <div class="options-header" @click="showAdvanced = !showAdvanced">
              <span>高级选项</span>
              <el-icon :class="{ rotated: showAdvanced }"><ArrowDown /></el-icon>
            </div>
            <transition name="expand">
              <div v-if="showAdvanced" class="options-content">
                <div class="option-item">
                  <span class="option-label">建造年份</span>
                  <el-input-number 
                    v-model="form.construction_year" 
                    :min="1900" 
                    :max="2100"
                    placeholder="用于飞星计算"
                    clearable
                  />
                </div>
                <div class="option-item">
                  <span class="option-label">分析风格</span>
                  <el-select v-model="form.analysis_style">
                    <el-option label="传统专业" value="classic" />
                    <el-option label="简洁通俗" value="simple" />
                    <el-option label="商业事业" value="business" />
                    <el-option label="健康养生" value="health" />
                    <el-option label="综合全面" value="comprehensive" />
                  </el-select>
                </div>
                <div class="option-item checkbox-item">
                  <el-checkbox v-model="form.include_llm">
                    AI深度解读
                    <el-tooltip content="使用AI生成更详细的风水解读" placement="top">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </el-checkbox>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </transition>

      <!-- 步骤5: 分析结果 -->
      <transition name="slide-fade">
        <div v-if="currentStep === 4" class="step-panel result-panel">
          <div v-if="loading" class="loading-section">
            <div class="loading-animation">
              <div class="bagua-loader">
                <div class="bagua-ring"></div>
                <div class="yin-yang"></div>
              </div>
            </div>
            <h3>正在为您分析风水布局...</h3>
            <p class="loading-tip">{{ loadingTips[currentTipIndex] }}</p>
          </div>
          
          <div v-else-if="analysisResult" class="result-section">
            <!-- 综合评分 -->
            <div class="score-display">
              <div class="score-circle" :style="{ '--score-color': scoreColor }">
                <svg viewBox="0 0 100 100">
                  <circle class="score-bg" cx="50" cy="50" r="45" />
                  <circle class="score-progress" cx="50" cy="50" r="45" 
                    :stroke-dasharray="scoreDashArray" />
                </svg>
                <div class="score-text">
                  <span class="score-number">{{ analysisResult.overall_score }}</span>
                  <span class="score-label">综合评分</span>
                </div>
              </div>
              <div class="score-level" :class="scoreLevel">
                {{ analysisResult.summary?.overall_level || '分析中' }}
              </div>
            </div>
            
            <!-- 命卦卡片 -->
            <div class="result-card mingua-card" v-if="analysisResult.mingua">
              <div class="card-header">
                <span class="card-icon">☯</span>
                <span class="card-title">您的命卦</span>
              </div>
              <div class="mingua-display">
                <div class="mingua-main">
                  <span class="mingua-char">{{ analysisResult.mingua.mingua }}</span>
                  <span class="mingua-type" :class="analysisResult.mingua.dong_si_xi_si === '东四命' ? 'dong' : 'xi'">
                    {{ analysisResult.mingua.dong_si_xi_si }}
                  </span>
                </div>
                <div class="mingua-detail">
                  <span>五行：{{ analysisResult.mingua.mingua_wuxing }}</span>
                  <span>命卦数：{{ analysisResult.mingua.mingua_number }}</span>
                </div>
              </div>
            </div>
            
            <!-- 吉凶方位 -->
            <div class="result-card fangwei-card" v-if="analysisResult.mingua?.ji_fangwei">
              <div class="card-header">
                <span class="card-icon">🎯</span>
                <span class="card-title">吉凶方位</span>
              </div>
              <div class="card-content">
                <p class="fangwei-tip">根据您的命卦，以下方位对您有利或不利，可用于房屋布局参考</p>
                
                <!-- 八方位图 -->
                <div class="bagua-map">
                  <div class="bagua-center">
                    <span class="center-mingua">{{ analysisResult.mingua?.mingua }}</span>
                    <span class="center-label">您的命卦</span>
                  </div>
                  
                  <!-- 八个方位 -->
                  <div class="bagua-position pos-north" :class="getFangweiClass('北')">
                    <span class="pos-label">北</span>
                    <span class="pos-name">{{ getFangweiName('北') }}</span>
                  </div>
                  <div class="bagua-position pos-northeast" :class="getFangweiClass('东北')">
                    <span class="pos-label">东北</span>
                    <span class="pos-name">{{ getFangweiName('东北') }}</span>
                  </div>
                  <div class="bagua-position pos-east" :class="getFangweiClass('东')">
                    <span class="pos-label">东</span>
                    <span class="pos-name">{{ getFangweiName('东') }}</span>
                  </div>
                  <div class="bagua-position pos-southeast" :class="getFangweiClass('东南')">
                    <span class="pos-label">东南</span>
                    <span class="pos-name">{{ getFangweiName('东南') }}</span>
                  </div>
                  <div class="bagua-position pos-south" :class="getFangweiClass('南')">
                    <span class="pos-label">南</span>
                    <span class="pos-name">{{ getFangweiName('南') }}</span>
                  </div>
                  <div class="bagua-position pos-southwest" :class="getFangweiClass('西南')">
                    <span class="pos-label">西南</span>
                    <span class="pos-name">{{ getFangweiName('西南') }}</span>
                  </div>
                  <div class="bagua-position pos-west" :class="getFangweiClass('西')">
                    <span class="pos-label">西</span>
                    <span class="pos-name">{{ getFangweiName('西') }}</span>
                  </div>
                  <div class="bagua-position pos-northwest" :class="getFangweiClass('西北')">
                    <span class="pos-label">西北</span>
                    <span class="pos-name">{{ getFangweiName('西北') }}</span>
                  </div>
                </div>
                
                <!-- 图例说明 -->
                <div class="fangwei-legend">
                  <div class="legend-item">
                    <span class="legend-color ji"></span>
                    <span class="legend-text">吉位：适合卧室、书房、客厅</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color xiong"></span>
                    <span class="legend-text">凶位：适合卫生间、储藏室</span>
                  </div>
                </div>
                
                <!-- 详细列表 -->
                <div class="fangwei-details">
                  <div class="fangwei-detail-section">
                    <h4><span class="dot ji"></span>四吉方位</h4>
                    <div class="detail-items">
                      <div v-for="(info, name) in analysisResult.mingua.ji_fangwei" :key="name" class="detail-item ji">
                        <span class="detail-name">{{ name }}</span>
                        <span class="detail-arrow">→</span>
                        <span class="detail-dir">{{ info.fangwei }}</span>
                        <span class="detail-desc">适合{{ getFangweiSuggest(name, true) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="fangwei-detail-section">
                    <h4><span class="dot xiong"></span>四凶方位</h4>
                    <div class="detail-items">
                      <div v-for="(info, name) in analysisResult.mingua.xiong_fangwei" :key="name" class="detail-item xiong">
                        <span class="detail-name">{{ name }}</span>
                        <span class="detail-arrow">→</span>
                        <span class="detail-dir">{{ info.fangwei }}</span>
                        <span class="detail-desc">适合{{ getFangweiSuggest(name, false) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 朝向分析 -->
            <div class="result-card" v-if="analysisResult.orientation_analysis">
              <div class="card-header">
                <span class="card-icon">🧭</span>
                <span class="card-title">朝向分析</span>
                <el-tag :type="getScoreType(analysisResult.orientation_analysis.orientation_score)" size="small">
                  {{ analysisResult.orientation_analysis.orientation_level }}
                </el-tag>
              </div>
              <div class="card-content">
                <div class="info-row">
                  <span class="info-label">房屋朝向</span>
                  <span class="info-value">{{ form.house_direction }}山（{{ analysisResult.orientation_analysis.house_fangwei }}）</span>
                </div>
                <div class="info-row">
                  <span class="info-label">适配评分</span>
                  <span class="info-value">{{ analysisResult.orientation_analysis.orientation_score }}分</span>
                </div>
                <div class="suggestion-list" v-if="analysisResult.orientation_analysis.orientation_suggestions">
                  <div v-for="(s, i) in analysisResult.orientation_analysis.orientation_suggestions" :key="i" class="suggestion-item">
                    {{ s }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 格局分析 -->
            <div class="result-card" v-if="analysisResult.layout_analysis">
              <div class="card-header">
                <span class="card-icon">📐</span>
                <span class="card-title">格局分析</span>
                <el-tag :type="getScoreType(analysisResult.layout_analysis.layout_score)" size="small">
                  {{ analysisResult.layout_analysis.layout_score }}分
                </el-tag>
              </div>
              <div class="card-content">
                <div class="info-row">
                  <span class="info-label">房屋形状</span>
                  <span class="info-value">{{ analysisResult.layout_analysis.house_shape }}</span>
                </div>
                <div class="defect-list" v-if="analysisResult.layout_analysis.defects?.length">
                  <div v-for="(d, i) in analysisResult.layout_analysis.defects" :key="i" class="defect-item">
                    <el-icon><WarningFilled /></el-icon>
                    <span>{{ d.position }}: {{ d.impact }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 房间定位 -->
            <div class="result-card" v-if="analysisResult.room_analysis?.room_positions">
              <div class="card-header">
                <span class="card-icon">🛏️</span>
                <span class="card-title">房间定位建议</span>
              </div>
              <div class="room-grid">
                <div v-for="(pos, room) in analysisResult.room_analysis.room_positions" :key="room" class="room-card">
                  <div class="room-name">{{ room }}</div>
                  <div class="room-pos">{{ pos.best_position }}</div>
                  <div class="room-reason">{{ pos.reason }}</div>
                </div>
              </div>
            </div>
            
            <!-- 工位分析 -->
            <div class="result-card" v-if="analysisResult.desk_analysis?.desk_position">
              <div class="card-header">
                <span class="card-icon">🖥️</span>
                <span class="card-title">工位摆放建议</span>
              </div>
              <div class="card-content">
                <div class="desk-info">
                  <div class="desk-item">
                    <span class="desk-label">最佳位置</span>
                    <span class="desk-value">{{ analysisResult.desk_analysis.desk_position.area }}</span>
                  </div>
                  <div class="desk-item" v-if="analysisResult.desk_analysis.face_direction">
                    <span class="desk-label">面朝方向</span>
                    <span class="desk-value">{{ analysisResult.desk_analysis.face_direction }}</span>
                  </div>
                </div>
                <div class="enhancement-section" v-if="analysisResult.desk_analysis.enhancement_items?.length">
                  <h4>增运物品</h4>
                  <div class="enhancement-list">
                    <div v-for="(item, i) in analysisResult.desk_analysis.enhancement_items" :key="i" class="enhancement-item">
                      <span class="item-icon">✨</span>
                      <span class="item-name">{{ item.item }}</span>
                      <span class="item-reason">{{ item.reason }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 综合建议 -->
            <div class="result-card" v-if="analysisResult.recommendations?.length">
              <div class="card-header">
                <span class="card-icon">📋</span>
                <span class="card-title">综合建议</span>
              </div>
              <div class="card-content">
                <div class="recommendation-list">
                  <div v-for="(rec, i) in analysisResult.recommendations" :key="i" class="recommendation-item">
                    <span class="rec-num">{{ i + 1 }}</span>
                    <span class="rec-text">{{ rec }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 底部导航按钮 -->
    <div class="navigation-buttons">
      <el-button 
        v-if="currentStep > 0 && currentStep < 4"
        @click="prevStep"
        size="large"
      >
        <el-icon><ArrowLeft /></el-icon>
        上一步
      </el-button>
      <div v-else></div>
      
      <el-button 
        v-if="currentStep < 3"
        type="primary"
        @click="nextStep"
        size="large"
        :disabled="!canProceed"
      >
        下一步
        <el-icon><ArrowRight /></el-icon>
      </el-button>
      
      <el-button 
        v-if="currentStep === 3"
        type="primary"
        @click="startAnalysis"
        size="large"
        :loading="loading"
      >
        <el-icon><Compass /></el-icon>
        开始分析
      </el-button>
      
      <el-button 
        v-if="currentStep === 4 && !loading"
        type="success"
        @click="resetAnalysis"
        size="large"
      >
        <el-icon><RefreshRight /></el-icon>
        重新分析
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Compass, ArrowLeft, ArrowRight, Check, InfoFilled, 
  Star, WarningFilled, ArrowDown, QuestionFilled, RefreshRight 
} from '@element-plus/icons-vue'
import axios from 'axios'

const currentStep = ref(0)
const loading = ref(false)
const analysisResult = ref(null)
const showAdvanced = ref(false)
const selectedOctant = ref(null)
const currentTipIndex = ref(0)
let tipTimer = null

const steps = [
  { label: '基本信息' },
  { label: '房屋朝向' },
  { label: '房屋形状' },
  { label: '职业选择' },
  { label: '分析结果' },
]

const form = reactive({
  birth_year: 1990,
  gender: '男',
  house_shape: '矩形',
  house_direction: '',
  construction_year: null,
  occupation_type: '管理',
  include_llm: false,
  analysis_style: 'classic',
})

const yearMarks = {
  1940: '1940',
  1960: '1960',
  1980: '1980',
  2000: '2000',
  2010: '2010',
}

const houseShapes = [
  { 
    value: '矩形', 
    label: '方正', 
    desc: '四四方方，格局完整',
    score: 100,
    icon: '<svg viewBox="0 0 60 60"><rect x="10" y="10" width="40" height="40" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="2"/></svg>'
  },
  { 
    value: 'L形', 
    label: 'L形', 
    desc: '有缺角，需化解',
    score: 75,
    icon: '<svg viewBox="0 0 60 60"><path d="M10 10 H40 V30 H50 V50 H10 Z" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="2"/></svg>'
  },
  { 
    value: 'U形', 
    label: 'U形', 
    desc: '两面有缺，注意中心',
    score: 70,
    icon: '<svg viewBox="0 0 60 60"><path d="M10 10 H25 V40 H35 V10 H50 V50 H10 Z" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="2"/></svg>'
  },
  { 
    value: '不规则', 
    label: '不规则', 
    desc: '多角或缺角，需专业调理',
    score: 60,
    icon: '<svg viewBox="0 0 60 60"><path d="M15 10 L45 15 L50 35 L40 50 L20 45 L10 30 Z" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="2"/></svg>'
  },
]

const occupations = [
  { value: '管理', label: '管理', icon: '👔', wuxing: '土' },
  { value: '技术', label: '技术', icon: '💻', wuxing: '金' },
  { value: '销售', label: '销售', icon: '📊', wuxing: '水' },
  { value: '创意', label: '创意', icon: '🎨', wuxing: '木' },
  { value: '教育', label: '教育', icon: '📚', wuxing: '木' },
  { value: '金融', label: '金融', icon: '💰', wuxing: '金' },
  { value: '医疗', label: '医疗', icon: '🏥', wuxing: '水' },
  { value: '法律', label: '法律', icon: '⚖️', wuxing: '金' },
  { value: '艺术', label: '艺术', icon: '🎭', wuxing: '火' },
  { value: '餐饮', label: '餐饮', icon: '🍳', wuxing: '火' },
]

const compassDirections = [
  { name: '北', label: '北', angle: 0, shans: ['壬', '子', '癸'], shanLabels: ['壬山(偏西)', '子山(正北)', '癸山(偏东)'] },
  { name: '东北', label: '东北', angle: 45, shans: ['丑', '艮', '寅'], shanLabels: ['丑山(偏北)', '艮山(正东北)', '寅山(偏东)'] },
  { name: '东', label: '东', angle: 90, shans: ['甲', '卯', '乙'], shanLabels: ['甲山(偏北)', '卯山(正东)', '乙山(偏南)'] },
  { name: '东南', label: '东南', angle: 135, shans: ['辰', '巽', '巳'], shanLabels: ['辰山(偏东)', '巽山(正东南)', '巳山(偏南)'] },
  { name: '南', label: '南', angle: 180, shans: ['丙', '午', '丁'], shanLabels: ['丙山(偏东)', '午山(正南)', '丁山(偏西)'] },
  { name: '西南', label: '西南', angle: 225, shans: ['未', '坤', '申'], shanLabels: ['未山(偏南)', '坤山(正西南)', '申山(偏西)'] },
  { name: '西', label: '西', angle: 270, shans: ['庚', '酉', '辛'], shanLabels: ['庚山(偏南)', '酉山(正西)', '辛山(偏北)'] },
  { name: '西北', label: '西北', angle: 315, shans: ['戌', '乾', '亥'], shanLabels: ['戌山(偏西)', '乾山(正西北)', '亥山(偏北)'] },
].map(dir => ({
  ...dir,
  style: {
    '--angle': `${dir.angle}deg`,
    transform: `rotate(${dir.angle}deg) translateY(-100px) rotate(-${dir.angle}deg)`,
  }
}))

const loadingTips = [
  '正在计算您的命卦...',
  '分析房屋朝向与命卦匹配度...',
  '检测房屋格局优劣...',
  '计算各房间最佳位置...',
  '优化工位摆放建议...',
  '生成综合风水报告...',
]

const progressWidth = computed(() => {
  return `${(currentStep.value / (steps.length - 1)) * 100}%`
})

const canProceed = computed(() => {
  if (currentStep.value === 0) return form.birth_year && form.gender
  if (currentStep.value === 1) return form.house_direction
  if (currentStep.value === 2) return form.house_shape
  if (currentStep.value === 3) return form.occupation_type
  return true
})

const showMinguaPreview = computed(() => {
  return form.birth_year && form.gender
})

const minguaPreview = computed(() => {
  if (!showMinguaPreview.value) return {}
  const num = form.gender === '男' 
    ? (100 - (form.birth_year % 100)) % 9 
    : ((form.birth_year % 100) - 4) % 9
  const actualNum = num === 0 ? 9 : num
  const minguaMap = { 1: '坎', 2: '坤', 3: '震', 4: '巽', 6: '乾', 7: '兑', 8: '艮', 9: '离' }
  const actualMingua = minguaMap[actualNum] || '坤'
  const dongXi = ['坎', '离', '震', '巽'].includes(actualMingua) ? '东四命' : '西四命'
  const wuxingMap = { '坎': '水', '离': '火', '震': '木', '巽': '木', '乾': '金', '兑': '金', '艮': '土', '坤': '土' }
  return {
    mingua: actualMingua,
    number: actualNum === 5 ? (form.gender === '男' ? 2 : 8) : actualNum,
    dong_si_xi_si: dongXi,
    wuxing: wuxingMap[actualMingua] || '土',
  }
})

const currentOctantShans = computed(() => {
  if (!selectedOctant.value) return []
  const dir = compassDirections.find(d => d.name === selectedOctant.value)
  if (!dir) return []
  return dir.shans.map((shan, i) => ({
    value: shan,
    label: dir.shanLabels?.[i] || shan,
    deg: '',
  }))
})

const scoreColor = computed(() => {
  const score = analysisResult.value?.overall_score || 0
  if (score >= 85) return '#67C23A'
  if (score >= 70) return '#409EFF'
  if (score >= 50) return '#E6A23C'
  return '#F56C6C'
})

const scoreLevel = computed(() => {
  const score = analysisResult.value?.overall_score || 0
  if (score >= 85) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 50) return 'normal'
  return 'poor'
})

const scoreDashArray = computed(() => {
  const score = analysisResult.value?.overall_score || 0
  const circumference = 2 * Math.PI * 45
  const dash = (score / 100) * circumference
  return `${dash} ${circumference}`
})

function isDirectionSelected(dirName) {
  if (!form.house_direction) return false
  const dir = compassDirections.find(d => d.name === dirName)
  return dir && dir.shans.includes(form.house_direction)
}

function selectDirection(dir) {
  selectedOctant.value = dir.name
}

function getSelectedShan(dirName) {
  if (!form.house_direction) return ''
  const dir = compassDirections.find(d => d.name === dirName)
  if (dir && dir.shans.includes(form.house_direction)) {
    return form.house_direction
  }
  return ''
}

function getDirectionDetail() {
  const shanDetails = {
    '壬': '正北偏西，五行属水',
    '子': '正北，五行属水',
    '癸': '正北偏东，五行属水',
    '丑': '东北偏北，五行属土',
    '艮': '东北，五行属土',
    '寅': '东北偏东，五行属木',
    '甲': '正东偏北，五行属木',
    '卯': '正东，五行属木',
    '乙': '正东偏南，五行属木',
    '辰': '东南偏东，五行属土',
    '巽': '东南，五行属木',
    '巳': '东南偏南，五行属火',
    '丙': '正南偏东，五行属火',
    '午': '正南，五行属火',
    '丁': '正南偏西，五行属火',
    '未': '西南偏南，五行属土',
    '坤': '西南，五行属土',
    '申': '西南偏西，五行属金',
    '庚': '正西偏南，五行属金',
    '酉': '正西，五行属金',
    '辛': '正西偏北，五行属金',
    '戌': '西北偏西，五行属土',
    '乾': '西北，五行属金',
    '亥': '西北偏北，五行属水',
  }
  return shanDetails[form.house_direction] || ''
}

function getCurrentShapeTip() {
  const tips = {
    '矩形': '方正格局气场流通顺畅，是理想的房屋形状',
    'L形': 'L形房屋存在缺角，建议在缺角处放置对应五行物品化解',
    'U形': 'U形房屋中心采光可能不足，可在中心设置天井或明亮装饰',
    '不规则': '不规则格局气场不稳定，建议通过隔断优化空间布局',
  }
  return tips[form.house_shape] || ''
}

function getScoreType(score) {
  if (score >= 85) return 'success'
  if (score >= 70) return 'primary'
  if (score >= 50) return 'warning'
  return 'danger'
}

function nextStep() {
  if (canProceed.value && currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function startAnalysis() {
  currentStep.value = 4
  loading.value = true
  analysisResult.value = null
  
  tipTimer = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % loadingTips.length
  }, 2000)
  
  try {
    const response = await axios.post('/api/fengshui/analyze', {
      birth_year: form.birth_year,
      gender: form.gender,
      house_shape: form.house_shape,
      house_direction: form.house_direction,
      construction_year: form.construction_year || null,
      occupation_type: form.occupation_type,
      include_llm: form.include_llm,
      analysis_style: form.analysis_style,
    })
    
    if (response.data.success) {
      analysisResult.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('风水分析失败:', error)
    ElMessage.error(error.response?.data?.detail || '分析请求失败')
  } finally {
    loading.value = false
    if (tipTimer) {
      clearInterval(tipTimer)
      tipTimer = null
    }
  }
}

function resetAnalysis() {
  currentStep.value = 0
  analysisResult.value = null
}

// 获取方位的吉凶类型
function getFangweiClass(fangwei) {
  if (!analysisResult.value?.mingua) return ''
  const jiFangwei = analysisResult.value.mingua.ji_fangwei || {}
  const xiongFangwei = analysisResult.value.mingua.xiong_fangwei || {}
  
  for (const name in jiFangwei) {
    if (jiFangwei[name].fangwei === fangwei) return 'ji'
  }
  for (const name in xiongFangwei) {
    if (xiongFangwei[name].fangwei === fangwei) return 'xiong'
  }
  return ''
}

// 获取方位的名称（如：生气、天医等）
function getFangweiName(fangwei) {
  if (!analysisResult.value?.mingua) return ''
  const jiFangwei = analysisResult.value.mingua.ji_fangwei || {}
  const xiongFangwei = analysisResult.value.mingua.xiong_fangwei || {}
  
  for (const name in jiFangwei) {
    if (jiFangwei[name].fangwei === fangwei) return name
  }
  for (const name in xiongFangwei) {
    if (xiongFangwei[name].fangwei === fangwei) return name
  }
  return ''
}

// 获取方位建议
function getFangweiSuggest(name, isJi) {
  const suggestions = {
    '生气': isJi ? '卧室、书房、办公室' : '',
    '天医': isJi ? '卧室、老人房' : '',
    '延年': isJi ? '客厅、餐厅' : '',
    '伏位': isJi ? '书房、卧室' : '',
    '绝命': !isJi ? '卫生间、储藏室' : '',
    '五鬼': !isJi ? '卫生间、厨房' : '',
    '六煞': !isJi ? '卫生间、阳台' : '',
    '祸害': !isJi ? '卫生间、杂物间' : '',
  }
  return suggestions[name] || ''
}

onMounted(() => {
  currentTipIndex.value = 0
})

onUnmounted(() => {
  if (tipTimer) {
    clearInterval(tipTimer)
  }
})
</script>

<style scoped>
.fengshui-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

/* 进度条 */
.progress-bar {
  position: relative;
  padding: 30px 60px;
  margin-bottom: 20px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2a2a4a;
  border: 2px solid #444;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s ease;
}

.step-item.active .step-circle {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.step-item.completed .step-circle {
  background: #67C23A;
  border-color: #67C23A;
}

.step-label {
  font-size: 12px;
  color: #888;
  transition: color 0.3s;
}

.step-item.active .step-label {
  color: #667eea;
  font-weight: bold;
}

.progress-line {
  position: absolute;
  top: 50%;
  left: 60px;
  right: 60px;
  height: 2px;
  background: #333;
  transform: translateY(-50%);
  z-index: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.5s ease;
}

/* 主内容 */
.main-content {
  flex: 1;
  overflow-y: auto;
}

.step-panel {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.panel-header {
  text-align: center;
  margin-bottom: 40px;
}

.step-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.panel-header h2 {
  font-size: 28px;
  margin: 0 0 10px;
}

.step-desc {
  color: #888;
  font-size: 14px;
}

/* 输入区域 */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.input-group {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
}

.label-icon {
  font-size: 20px;
}

.year-selector {
  padding: 10px 0;
}

.hint-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #888;
  font-size: 13px;
  margin-top: 12px;
}

/* 性别选择 */
.gender-cards {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.gender-card {
  flex: 1;
  max-width: 200px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.gender-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.gender-card.male.selected {
  border-color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
}

.gender-card.female.selected {
  border-color: #F56C6C;
  background: rgba(245, 108, 108, 0.1);
}

.gender-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.gender-text {
  font-size: 18px;
  font-weight: 500;
}

/* 命卦预览 */
.preview-card {
  margin-top: 30px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 16px;
  padding: 20px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #667eea;
  font-weight: 500;
  margin-bottom: 16px;
}

.preview-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.mingua-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.mingua-badge.dong {
  background: linear-gradient(135deg, #67C23A, #409EFF);
}

.mingua-badge.xi {
  background: linear-gradient(135deg, #E6A23C, #F56C6C);
}

.mingua-char {
  font-size: 32px;
  font-weight: bold;
}

.mingua-type {
  font-size: 12px;
  opacity: 0.9;
}

.mingua-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  gap: 12px;
}

.info-label {
  color: #888;
  font-size: 14px;
}

.info-value {
  font-weight: 500;
}

/* 罗盘 */
.compass-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.compass-container {
  position: relative;
}

.compass {
  width: 280px;
  height: 280px;
  position: relative;
}

.compass-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.compass-ring.outer {
  inset: 0;
}

.compass-ring.inner {
  inset: 30px;
}

.compass-center {
  position: absolute;
  inset: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.center-dot {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
}

.compass-direction {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  margin-left: -30px;
  margin-top: -30px;
}

.compass-direction:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: scale(1.1);
}

.compass-direction.selected {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}

.dir-name {
  font-size: 14px;
  font-weight: bold;
}

.dir-shan {
  font-size: 11px;
  color: #888;
}

/* 二十四山选择 */
.shan-selector {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
}

.shan-header {
  margin-bottom: 16px;
}

.shan-selector h4 {
  margin: 0 0 8px;
  color: #667eea;
}

.shan-explain {
  font-size: 13px;
  color: #888;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  text-align: left;
}

.shan-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.shan-btn {
  width: 100px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.shan-btn:hover {
  background: rgba(102, 126, 234, 0.2);
}

.shan-btn.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.2);
}

.shan-char {
  display: block;
  font-size: 28px;
  font-weight: bold;
}

.shan-deg {
  display: block;
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.shan-label-text {
  display: block;
  font-size: 11px;
  color: #667eea;
  margin-top: 2px;
}

.selected-direction {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  color: #67C23A;
  font-size: 16px;
}

/* 房屋形状选择 */
.shape-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.shape-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.shape-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.shape-card.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.shape-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  color: #667eea;
}

.shape-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}

.shape-desc {
  font-size: 13px;
  color: #888;
  margin-bottom: 12px;
}

.shape-score {
  display: flex;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
}

.score-label {
  color: #888;
}

.score-value {
  color: #67C23A;
  font-weight: bold;
}

.shape-tip {
  margin-top: 20px;
  padding: 16px;
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #E6A23C;
}

/* 职业选择 */
.occupation-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.occupation-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.occupation-card:hover {
  background: rgba(255, 255, 255, 0.1);
}

.occupation-card.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.occ-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.occ-name {
  font-size: 14px;
  font-weight: 500;
}

.occ-wuxing {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

/* 高级选项 */
.advanced-options {
  margin-top: 30px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.options-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  color: #888;
}

.options-header .el-icon {
  transition: transform 0.3s;
}

.options-header .el-icon.rotated {
  transform: rotate(180deg);
}

.options-content {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-label {
  color: #888;
}

.checkbox-item {
  justify-content: flex-start;
}

/* 结果面板 */
.result-panel {
  padding-bottom: 100px;
}

.loading-section {
  text-align: center;
  padding: 60px 20px;
}

.loading-animation {
  margin-bottom: 30px;
}

.bagua-loader {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  position: relative;
}

.bagua-ring {
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.yin-yang {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: linear-gradient(to bottom, #fff 50%, #333 50%);
  border-radius: 50%;
  animation: spin 3s linear infinite reverse;
}

.yin-yang::before,
.yin-yang::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.yin-yang::before {
  top: 10px;
  left: 0;
  background: #333;
}

.yin-yang::after {
  top: 10px;
  right: 0;
  background: #fff;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-tip {
  color: #888;
  font-size: 14px;
  margin-top: 20px;
}

/* 结果展示 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-display {
  text-align: center;
  padding: 30px;
}

.score-circle {
  width: 160px;
  height: 160px;
  margin: 0 auto 20px;
  position: relative;
}

.score-circle svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 8;
}

.score-progress {
  fill: none;
  stroke: var(--score-color, #667eea);
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dasharray 1s ease;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  display: block;
  font-size: 48px;
  font-weight: bold;
}

.score-label {
  display: block;
  font-size: 14px;
  color: #888;
}

.score-level {
  display: inline-block;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 18px;
  font-weight: bold;
}

.score-level.excellent {
  background: linear-gradient(135deg, #67C23A, #409EFF);
}

.score-level.good {
  background: linear-gradient(135deg, #409EFF, #667eea);
}

.score-level.normal {
  background: linear-gradient(135deg, #E6A23C, #F56C6C);
}

.score-level.poor {
  background: #F56C6C;
}

/* 结果卡片 */
.result-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-icon {
  font-size: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  flex: 1;
}

.card-content {
  padding: 20px;
}

/* 命卦卡片 */
.mingua-card .mingua-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
}

.mingua-main {
  text-align: center;
}

.mingua-char {
  display: block;
  font-size: 72px;
  font-weight: bold;
  line-height: 1;
}

.mingua-type {
  display: block;
  font-size: 16px;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 12px;
}

.mingua-type.dong {
  background: linear-gradient(135deg, #67C23A, #409EFF);
}

.mingua-type.xi {
  background: linear-gradient(135deg, #E6A23C, #F56C6C);
}

.mingua-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #888;
}

/* 吉凶方位卡片 */
.fangwei-card .card-content {
  padding: 20px;
}

.fangwei-tip {
  color: #888;
  font-size: 14px;
  margin: 0 0 20px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

/* 八卦方位图 */
.bagua-map {
  width: 280px;
  height: 280px;
  margin: 0 auto 20px;
  position: relative;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.bagua-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.center-mingua {
  font-size: 24px;
  font-weight: bold;
}

.center-label {
  font-size: 10px;
  opacity: 0.8;
}

.bagua-position {
  position: absolute;
  width: 70px;
  height: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.bagua-position.ji {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.3), rgba(103, 194, 58, 0.1));
  border: 1px solid rgba(103, 194, 58, 0.5);
}

.bagua-position.xiong {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.3), rgba(245, 108, 108, 0.1));
  border: 1px solid rgba(245, 108, 108, 0.5);
}

.pos-north { top: 5px; left: 50%; transform: translateX(-50%); }
.pos-south { bottom: 5px; left: 50%; transform: translateX(-50%); }
.pos-east { right: 5px; top: 50%; transform: translateY(-50%); }
.pos-west { left: 5px; top: 50%; transform: translateY(-50%); }
.pos-northeast { top: 40px; right: 40px; }
.pos-northwest { top: 40px; left: 40px; }
.pos-southeast { bottom: 40px; right: 40px; }
.pos-southwest { bottom: 40px; left: 40px; }

.pos-label {
  font-weight: bold;
}

.pos-name {
  font-size: 10px;
  opacity: 0.8;
}

.bagua-position.ji .pos-name {
  color: #67C23A;
}

.bagua-position.xiong .pos-name {
  color: #F56C6C;
}

/* 图例 */
.fangwei-legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.ji {
  background: linear-gradient(135deg, #67C23A, #409EFF);
}

.legend-color.xiong {
  background: linear-gradient(135deg, #E6A23C, #F56C6C);
}

.legend-text {
  font-size: 13px;
  color: #888;
}

/* 详细列表 */
.fangwei-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.fangwei-detail-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px;
  font-size: 14px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.ji {
  background: #67C23A;
}

.dot.xiong {
  background: #F56C6C;
}

.detail-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
}

.detail-item.ji {
  background: rgba(103, 194, 58, 0.1);
  border-left: 3px solid #67C23A;
}

.detail-item.xiong {
  background: rgba(245, 108, 108, 0.1);
  border-left: 3px solid #F56C6C;
}

.detail-name {
  font-weight: bold;
  min-width: 45px;
}

.detail-arrow {
  color: #666;
}

.detail-dir {
  color: #fff;
  font-weight: 500;
}

.detail-desc {
  color: #888;
  font-size: 11px;
  margin-left: auto;
}

/* 方位网格 */
.fangwei-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
}

.fangwei-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
}

.fangwei-section.ji h4 {
  color: #67C23A;
}

.fangwei-section.xiong h4 {
  color: #F56C6C;
}

.fangwei-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fangwei-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.fangwei-name {
  font-weight: bold;
  min-width: 50px;
}

.fangwei-dir {
  flex: 1;
}

.fangwei-gua {
  font-size: 12px;
  color: #888;
}

/* 房间网格 */
.room-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 20px;
}

.room-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.room-name {
  font-weight: bold;
  margin-bottom: 8px;
}

.room-pos {
  color: #67C23A;
  font-size: 18px;
  margin-bottom: 4px;
}

.room-reason {
  font-size: 12px;
  color: #888;
}

/* 工位信息 */
.desk-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.desk-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.desk-label {
  display: block;
  color: #888;
  font-size: 13px;
  margin-bottom: 8px;
}

.desk-value {
  font-size: 20px;
  font-weight: bold;
  color: #67C23A;
}

.enhancement-section {
  margin-top: 20px;
}

.enhancement-section h4 {
  margin: 0 0 12px;
  color: #888;
}

.enhancement-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.enhancement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
}

.item-icon {
  color: #FFD700;
}

.item-name {
  font-weight: 500;
}

.item-reason {
  font-size: 12px;
  color: #888;
}

/* 建议列表 */
.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.rec-num {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.rec-text {
  flex: 1;
  line-height: 1.6;
}

/* 信息行 */
.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-label {
  color: #888;
}

.info-value {
  font-weight: 500;
}

.suggestion-list {
  margin-top: 16px;
}

.suggestion-item {
  padding: 8px 0;
  color: #888;
  line-height: 1.6;
}

.defect-list {
  margin-top: 12px;
}

.defect-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 8px;
  margin-bottom: 8px;
  color: #F56C6C;
}

/* 底部按钮 */
.navigation-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 20px 40px;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 200px;
}

/* 响应式 */
@media (max-width: 768px) {
  .progress-bar {
    padding: 20px;
  }
  
  .step-label {
    display: none;
  }
  
  .shape-selector {
    grid-template-columns: 1fr;
  }
  
  .occupation-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .fangwei-grid {
    grid-template-columns: 1fr;
  }
  
  .room-grid {
    grid-template-columns: 1fr;
  }
  
  .gender-cards {
    flex-direction: column;
  }
  
  .gender-card {
    max-width: 100%;
  }
}
</style>
