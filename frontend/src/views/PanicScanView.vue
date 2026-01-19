<template>
  <div class="panic-scan-view">
    <div class="view-header">
      <h1>每日恐慌点扫描</h1>
      <p class="subtitle">基于博弈交易法的恐慌点识别与推荐系统</p>
    </div>

    <div class="view-content">
      <!-- 控制面板 -->
      <el-card class="control-panel">
        <template #header>
          <div class="card-header">
            <span>扫描控制</span>
            <el-button
              type="primary"
              :loading="scanning"
              @click="handleTriggerScan"
              :disabled="scanning"
            >
              {{ scanning ? '扫描中...' : '触发扫描' }}
            </el-button>
          </div>
        </template>

        <div class="control-content">
          <div class="date-selector">
            <el-select
              v-model="selectedDate"
              placeholder="选择日期"
              @change="handleDateChange"
              style="width: 200px"
            >
              <el-option
                v-for="file in scanFiles"
                :key="file.date"
                :label="file.date"
                :value="file.date"
              />
            </el-select>
            <el-button @click="loadLatest" :loading="loading">加载最新</el-button>
          </div>

          <div class="stats" v-if="scanResult">
            <el-tag type="info">扫描日期: {{ scanResult.date }}</el-tag>
            <el-tag type="success">候选数量: {{ scanResult.count || 0 }}</el-tag>
            <el-tag type="warning">文件: {{ scanResult.filename }}</el-tag>
          </div>
        </div>
      </el-card>

      <!-- 筛选和排序 -->
      <el-card class="filter-panel" v-if="records.length > 0">
        <template #header>
          <span>筛选与排序</span>
        </template>
        <div class="filters">
          <el-input
            v-model="searchText"
            placeholder="搜索股票代码或名称"
            clearable
            style="width: 250px"
            @input="handleFilter"
          />
          <el-select
            v-model="filterType"
            placeholder="恐慌类型"
            clearable
            style="width: 200px"
            @change="handleFilter"
          >
            <el-option label="5阶段恐慌" value="stage5_panic" />
            <el-option label="一阶段恐慌" value="stage1_panic" />
            <el-option label="洗盘恐慌" value="washout_panic" />
            <el-option label="上涨趋势恐慌" value="uptrend_panic" />
            <el-option label="通用恐慌" value="general_panic" />
          </el-select>
          <el-select
            v-model="sortField"
            placeholder="排序字段"
            style="width: 150px"
            @change="handleSort"
          >
            <el-option label="评分" value="score" />
            <el-option label="跌幅" value="drop_pct" />
            <el-option label="放量倍数" value="vol_ratio" />
            <el-option label="20日涨幅" value="recent_gain_20d" />
          </el-select>
          <el-radio-group v-model="sortOrder" @change="handleSort">
            <el-radio-button label="desc">降序</el-radio-button>
            <el-radio-button label="asc">升序</el-radio-button>
          </el-radio-group>
        </div>
      </el-card>

      <!-- 错误提示 -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="true"
        @close="error = ''"
        class="error-alert"
      />

      <!-- 数据表格 -->
      <el-card class="table-card" v-if="filteredRecords.length > 0">
        <template #header>
          <span>恐慌点候选列表 ({{ filteredRecords.length }} 条)</span>
        </template>
        <el-table
          :data="filteredRecords"
          stripe
          border
          style="width: 100%"
          :default-sort="{ prop: 'score', order: 'descending' }"
          @sort-change="handleTableSort"
        >
          <el-table-column prop="code" label="代码" width="100" fixed="left" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="panic_date" label="恐慌日期" width="120" />
          <el-table-column prop="panic_type" label="恐慌类型" width="140">
            <template #default="{ row }">
              <el-tag :type="getTypeTagType(row.panic_type)" size="small">
                {{ getTypeLabel(row.panic_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="drop_pct" label="跌幅%" width="100" sortable>
            <template #default="{ row }">
              <span :class="{ 'negative': row.drop_pct < 0 }">
                {{ row.drop_pct.toFixed(2) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="vol_ratio" label="放量倍数" width="110" sortable>
            <template #default="{ row }">
              <el-tag type="warning" size="small">{{ row.vol_ratio.toFixed(2) }}x</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="评分" width="100" sortable>
            <template #default="{ row }">
              <el-tag :type="getScoreTagType(row.score)" size="small">
                {{ row.score.toFixed(2) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="current_price" label="当前价" width="100" />
          <el-table-column prop="ma60" label="MA60" width="100" />
          <el-table-column prop="over_ma60_pct" label="超MA60%" width="110">
            <template #default="{ row }">
              <span v-if="row.over_ma60_pct !== null && row.over_ma60_pct !== undefined">
                {{ row.over_ma60_pct.toFixed(2) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="recent_gain_20d" label="20日涨幅%" width="110" sortable>
            <template #default="{ row }">
              <span
                v-if="row.recent_gain_20d !== null && row.recent_gain_20d !== undefined"
                :class="{ 'positive': row.recent_gain_20d > 0, 'negative': row.recent_gain_20d < 0 }"
              >
                {{ row.recent_gain_20d.toFixed(2) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="panic_desc" label="描述" min-width="300" show-overflow-tooltip />
        </el-table>
      </el-card>

      <!-- 空状态 -->
      <el-empty
        v-else-if="!loading && records.length === 0"
        description="暂无扫描结果"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  listScanResults,
  getLatestScanResult,
  getScanResultByDate,
  triggerScan,
  type PanicScanRecord,
  type ScanFile,
  type ScanResult
} from '../api/panicScan';

const loading = ref(false);
const scanning = ref(false);
const error = ref('');
const scanFiles = ref<ScanFile[]>([]);
const selectedDate = ref('');
const scanResult = ref<ScanResult | null>(null);
const records = ref<PanicScanRecord[]>([]);

// 筛选和排序
const searchText = ref('');
const filterType = ref('');
const sortField = ref('score');
const sortOrder = ref<'asc' | 'desc'>('desc');

// 计算过滤后的记录
const filteredRecords = computed(() => {
  let result = [...records.value];

  // 文本搜索
  if (searchText.value) {
    const text = searchText.value.toLowerCase();
    result = result.filter(
      (r) =>
        r.code.toLowerCase().includes(text) ||
        r.name.toLowerCase().includes(text) ||
        r.panic_desc.toLowerCase().includes(text)
    );
  }

  // 类型筛选
  if (filterType.value) {
    result = result.filter((r) => r.panic_type === filterType.value);
  }

  // 排序
  if (sortField.value) {
    result.sort((a, b) => {
      const aVal = (a as any)[sortField.value];
      const bVal = (b as any)[sortField.value];
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      const diff = aVal - bVal;
      return sortOrder.value === 'asc' ? diff : -diff;
    });
  }

  return result;
});

// 加载文件列表
async function loadFileList() {
  try {
    const result = await listScanResults();
    if (result.success && result.files) {
      scanFiles.value = result.files;
      if (scanFiles.value.length > 0 && !selectedDate.value) {
        selectedDate.value = scanFiles.value[0].date;
      }
    }
  } catch (err: any) {
    console.error('加载文件列表失败:', err);
    error.value = err.response?.data?.detail || '加载文件列表失败';
  }
}

// 加载最新结果
async function loadLatest() {
  loading.value = true;
  error.value = '';
  try {
    const result = await getLatestScanResult();
    if (result.success && result.records) {
      scanResult.value = result;
      records.value = result.records;
      selectedDate.value = result.date || '';
      ElMessage.success(`已加载 ${result.count} 条记录`);
    } else {
      error.value = result.message || '未找到扫描结果';
      records.value = [];
      scanResult.value = null;
    }
  } catch (err: any) {
    console.error('加载最新结果失败:', err);
    const errorMsg = err.response?.data?.detail || '加载最新结果失败';
    // 如果是404，说明还没有扫描结果，这是正常的
    if (err.response?.status === 404) {
      error.value = '暂无扫描结果，请先触发扫描';
      ElMessage.info('暂无扫描结果，请先触发扫描');
    } else {
      error.value = errorMsg;
      ElMessage.error(error.value);
    }
    records.value = [];
    scanResult.value = null;
  } finally {
    loading.value = false;
  }
}

// 根据日期加载
async function handleDateChange(date: string) {
  if (!date) return;
  loading.value = true;
  error.value = '';
  try {
    const result = await getScanResultByDate(date);
    if (result.success && result.records) {
      scanResult.value = result;
      records.value = result.records;
      ElMessage.success(`已加载 ${result.count} 条记录`);
    } else {
      error.value = result.message || '未找到扫描结果';
    }
  } catch (err: any) {
    console.error('加载扫描结果失败:', err);
    error.value = err.response?.data?.detail || '加载扫描结果失败';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
}

// 触发扫描
async function handleTriggerScan() {
  scanning.value = true;
  error.value = '';
  try {
    const result = await triggerScan({
      days: 300,
      panic_window: 60,
      recent_days: 5,
      top_k: 50
    });
    if (result.success) {
      ElMessage.success('扫描任务已启动，请稍后刷新查看结果');
      // 3秒后刷新文件列表
      setTimeout(() => {
        loadFileList();
      }, 3000);
    }
  } catch (err: any) {
    console.error('触发扫描失败:', err);
    error.value = err.response?.data?.detail || '触发扫描失败';
    ElMessage.error(error.value);
  } finally {
    scanning.value = false;
  }
}

// 筛选处理
function handleFilter() {
  // 计算属性会自动更新
}

// 排序处理
function handleSort() {
  // 计算属性会自动更新
}

// 表格排序
function handleTableSort({ prop, order }: { prop: string; order: string }) {
  sortField.value = prop;
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc';
}

// 获取类型标签样式
function getTypeTagType(type: string): string {
  const map: Record<string, string> = {
    stage5_panic: 'danger',
    stage1_panic: 'warning',
    washout_panic: 'info',
    uptrend_panic: 'success',
    general_panic: ''
  };
  return map[type] || '';
}

// 获取类型标签文本
function getTypeLabel(type: string): string {
  const map: Record<string, string> = {
    stage5_panic: '5阶段恐慌',
    stage1_panic: '一阶段恐慌',
    washout_panic: '洗盘恐慌',
    uptrend_panic: '上涨趋势恐慌',
    general_panic: '通用恐慌'
  };
  return map[type] || type;
}

// 获取评分标签样式
function getScoreTagType(score: number): string {
  if (score >= 10) return 'success';
  if (score >= 5) return 'warning';
  return 'info';
}

onMounted(() => {
  loadFileList();
  loadLatest();
});
</script>

<style scoped>
.panic-scan-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.view-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 24px;
  text-align: center;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.view-header h1 {
  margin: 0 0 8px 0;
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.view-header .subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.95;
  font-weight: 400;
}

.view-content {
  max-width: 1920px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 48px;
  min-height: calc(100vh - 200px);
}

.control-panel,
.filter-panel,
.table-card {
  margin-bottom: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.date-selector {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.error-alert {
  margin-bottom: 24px;
  border-radius: 8px;
}

.positive {
  color: #67c23a;
  font-weight: 500;
}

.negative {
  color: #f56c6c;
  font-weight: 500;
}

:deep(.el-card__header) {
  padding: 20px 28px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  background: #fafbfc;
}

:deep(.el-card__body) {
  padding: 32px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}
</style>

