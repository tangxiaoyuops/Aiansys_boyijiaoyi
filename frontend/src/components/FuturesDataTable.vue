<template>
  <div class="futures-data-table card">
    <div class="table-title">{{ title || '期货数据表格' }}</div>
    <el-table
      :data="tableData"
      stripe
      border
      style="width: 100%"
      :max-height="maxHeight"
      :default-sort="{ prop: 'date', order: 'descending' }"
    >
      <el-table-column prop="date" label="日期" width="120" sortable />
      <el-table-column prop="open" label="开盘" width="100" sortable>
        <template #default="{ row }">
          {{ row.open.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="high" label="最高" width="100" sortable>
        <template #default="{ row }">
          {{ row.high.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="low" label="最低" width="100" sortable>
        <template #default="{ row }">
          {{ row.low.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="close" label="收盘" width="100" sortable>
        <template #default="{ row }">
          <span :class="getPriceClass(row.close, row.open)">
            {{ row.close.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="成交量" width="120" sortable>
        <template #default="{ row }">
          {{ row.volume.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="open_interest" label="持仓量" width="120" sortable>
        <template #default="{ row }">
          {{ row.open_interest.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="change" label="涨跌" width="100" sortable>
        <template #default="{ row }">
          <span :class="getChangeClass(row.change)">
            {{ row.change > 0 ? '+' : '' }}{{ row.change.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="change_pct" label="涨跌幅" width="100" sortable>
        <template #default="{ row }">
          <span :class="getChangeClass(row.change)">
            {{ row.change > 0 ? '+' : '' }}{{ row.change_pct.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  data?: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    open_interest: number;
  }>;
  title?: string;
  maxHeight?: number;
}>();

const tableData = computed(() => {
  if (!props.data || props.data.length === 0) return [];
  
  return props.data.map((item, index) => {
    const prevClose = index > 0 ? props.data![index - 1].close : item.close;
    const change = item.close - prevClose;
    const changePct = (change / prevClose) * 100;
    
    return {
      ...item,
      change,
      change_pct: changePct
    };
  });
});

const getPriceClass = (close: number, open: number) => {
  if (close > open) return 'price-up';
  if (close < open) return 'price-down';
  return '';
};

const getChangeClass = (change: number) => {
  if (change > 0) return 'change-up';
  if (change < 0) return 'change-down';
  return '';
};
</script>

<style scoped>
.futures-data-table {
  margin-top: 12px;
  padding: 8px;
}
.table-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #374151;
}
.price-up {
  color: #16a34a;
  font-weight: 500;
}
.price-down {
  color: #dc2626;
  font-weight: 500;
}
.change-up {
  color: #16a34a;
  font-weight: 500;
}
.change-down {
  color: #dc2626;
  font-weight: 500;
}
</style>

