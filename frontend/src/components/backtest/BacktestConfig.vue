<template>
  <el-card class="backtest-config">
    <template #header>
      <span>回测配置</span>
    </template>
    
    <el-form :model="config" label-width="140px" class="config-form">
      <div class="form-row">
        <div class="form-col">
          <el-form-item label="回测类型">
            <el-select 
              v-model="backtestType" 
              @change="onBacktestTypeChange"
              size="large"
              style="width: 100%"
            >
              <el-option label="期货" value="futures" />
              <el-option label="股票" value="stock" />
            </el-select>
          </el-form-item>
        </div>
        
        <div class="form-col">
          <el-form-item :label="backtestType === 'futures' ? '期货代码' : '股票代码'">
            <el-input 
              v-if="backtestType === 'futures'"
              v-model="(config as any).futures_code" 
              placeholder="如：rb2501"
              size="large"
            />
            <el-input 
              v-else
              v-model="(config as any).stock_code" 
              placeholder="如：000001"
              size="large"
            />
          </el-form-item>
        </div>
        
        <div class="form-col">
          <el-form-item label="策略">
            <el-select 
              v-model="config.strategy_name" 
              @change="onStrategyChange"
              size="large"
              style="width: 100%"
            >
              <el-option
                v-for="strategy in strategies"
                :key="strategy"
                :label="getStrategyLabel(strategy)"
                :value="strategy"
              />
            </el-select>
          </el-form-item>
        </div>
      </div>
      
      <el-form-item label="策略参数" v-if="strategyParams && Object.keys(strategyParams).length > 0">
        <div class="strategy-params">
          <div class="params-grid">
            <el-form-item
              v-for="(param, key) in strategyParams"
              :key="key"
              :label="param.description"
              class="param-item"
            >
              <el-input-number
                v-if="param.type === 'number'"
                v-model="config.strategy_params[key]"
                :min="param.min !== undefined ? param.min : (key.includes('threshold') || key.includes('ratio') ? -10 : 0)"
                :max="param.max !== undefined ? param.max : undefined"
                :step="param.step !== undefined ? param.step : (key.includes('threshold') || key.includes('ratio') ? 0.1 : 1)"
                :precision="param.precision !== undefined ? param.precision : (key.includes('threshold') || key.includes('ratio') ? 1 : 0)"
                size="large"
                style="width: 100%"
              />
              <el-switch
                v-else-if="param.type === 'boolean'"
                v-model="config.strategy_params[key]"
                size="large"
              />
            </el-form-item>
          </div>
        </div>
      </el-form-item>
      
      <div class="form-row">
        <div class="form-col">
          <el-form-item label="回测天数">
            <el-input-number 
              v-model="config.days" 
              :min="30" 
              :max="1000"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
        
        <div class="form-col">
          <el-form-item label="初始资金">
            <el-input-number 
              v-model="config.initial_capital" 
              :min="10000" 
              :step="10000"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-col">
          <el-form-item label="手续费率">
            <el-input-number 
              v-model="config.commission_rate" 
              :min="0" 
              :max="0.01" 
              :step="0.0001" 
              :precision="4"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
        
        <div class="form-col">
          <el-form-item label="滑点">
            <el-input-number 
              v-model="config.slippage" 
              :min="0" 
              :max="0.01" 
              :step="0.0001" 
              :precision="4"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
      </div>
      
      <!-- 期货特有字段 -->
      <template v-if="backtestType === 'futures'">
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="保证金率">
              <el-input-number 
                v-model="(config as any).margin_rate" 
                :min="0" 
                :max="1" 
                :step="0.01" 
                :precision="2"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          
          <div class="form-col">
            <el-form-item label="合约乘数">
              <el-input-number 
                v-model="(config as any).contract_multiplier" 
                :min="1" 
                :step="1"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="最大持仓">
              <el-input-number 
                v-model="(config as any).max_position" 
                :min="1" 
                :step="1"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          
          <div class="form-col">
            <el-form-item label="最大保证金率">
              <el-input-number 
                v-model="(config as any).max_margin_rate" 
                :min="0" 
                :max="1" 
                :step="0.01" 
                :precision="2"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
        </div>
      </template>
      
      <!-- 股票特有字段 -->
      <template v-else>
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="印花税">
              <el-input-number 
                v-model="(config as any).stamp_tax_rate" 
                :min="0" 
                :max="0.01" 
                :step="0.0001" 
                :precision="4"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          
          <div class="form-col">
            <el-form-item label="最小手续费">
              <el-input-number 
                v-model="(config as any).min_commission" 
                :min="0" 
                :step="1"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="最大持仓(股)">
              <el-input-number 
                v-model="(config as any).max_position" 
                :min="1" 
                :step="100"
                size="large"
                style="width: 100%"
              />
            </el-form-item>
          </div>
        </div>
      </template>
      
      <!-- 通用字段 -->
      <div class="form-row">
        <div class="form-col">
          <el-form-item label="止损比例">
            <el-input-number 
              v-model="config.stop_loss_ratio" 
              :min="0" 
              :max="1" 
              :step="0.01" 
              :precision="2"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
        
        <div class="form-col">
          <el-form-item label="止盈比例">
            <el-input-number 
              v-model="config.take_profit_ratio" 
              :min="0" 
              :max="1" 
              :step="0.01" 
              :precision="2"
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </div>
      </div>
      
      <el-form-item class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleRun" 
          :loading="loading"
          size="large"
          class="run-button"
        >
          <el-icon v-if="!loading"><VideoPlay /></el-icon>
          <span style="margin-left: 8px">运行回测</span>
        </el-button>
        <el-button 
          @click="handleReset"
          size="large"
        >
          <el-icon><Refresh /></el-icon>
          <span style="margin-left: 8px">重置</span>
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { VideoPlay, Refresh } from '@element-plus/icons-vue';
import { getStrategyTemplates, getStrategyParams } from '../../api/strategy';
import { useBacktestStore } from '../../stores/backtest';
import type { BacktestRequest, StockBacktestRequest } from '../../api/backtest';

const emit = defineEmits<{
  (e: 'run', config: BacktestRequest | StockBacktestRequest, type: 'futures' | 'stock'): void;
}>();

const backtestStore = useBacktestStore();
const loading = computed(() => backtestStore.loading);

const backtestType = ref<'futures' | 'stock'>('futures');
const strategies = ref<string[]>([]);
const strategyParams = ref<Record<string, any>>({});

const config = ref<BacktestRequest | StockBacktestRequest>({
  futures_code: '',
  strategy_name: 'dual_ma',
  strategy_params: {},
  days: 180,
  initial_capital: 100000,
  commission_rate: 0.0003,
  slippage: 0.0002,
  margin_rate: 0.15,
  contract_multiplier: 10,
  max_position: 10,
  max_margin_rate: 0.8,
  stop_loss_ratio: 0.05,
  take_profit_ratio: 0.10
} as BacktestRequest);

const strategyLabels: Record<string, string> = {
  dual_ma: '双均线策略',
  triple_ma: '三均线策略',
  bollinger_bands: '布林带策略',
  rsi: 'RSI策略',
  game_theory: '博弈分析策略'
};

function getStrategyLabel(strategy: string): string {
  return strategyLabels[strategy] || strategy;
}

function onBacktestTypeChange() {
  // 切换回测类型时重新初始化配置
  if (backtestType.value === 'futures') {
    config.value = {
      futures_code: (config.value as any).futures_code || (config.value as any).stock_code || '',
      strategy_name: config.value.strategy_name,
      strategy_params: config.value.strategy_params,
      days: config.value.days,
      initial_capital: config.value.initial_capital,
      commission_rate: config.value.commission_rate,
      slippage: config.value.slippage,
      margin_rate: (config.value as any).margin_rate ?? 0.15,
      contract_multiplier: (config.value as any).contract_multiplier ?? 10,
      max_position: (config.value as any).max_position ?? 10,
      max_margin_rate: (config.value as any).max_margin_rate ?? 0.8,
      stop_loss_ratio: config.value.stop_loss_ratio,
      take_profit_ratio: config.value.take_profit_ratio
    } as BacktestRequest;
  } else {
    config.value = {
      stock_code: (config.value as any).stock_code || (config.value as any).futures_code || '',
      strategy_name: config.value.strategy_name,
      strategy_params: config.value.strategy_params,
      days: config.value.days,
      initial_capital: config.value.initial_capital,
      commission_rate: config.value.commission_rate,
      slippage: config.value.slippage,
      stamp_tax_rate: (config.value as any).stamp_tax_rate ?? 0.001,
      min_commission: (config.value as any).min_commission ?? 5.0,
      max_position: (config.value as any).max_position ?? 10000,
      stop_loss_ratio: config.value.stop_loss_ratio,
      take_profit_ratio: config.value.take_profit_ratio
    } as StockBacktestRequest;
  }
}

async function onStrategyChange() {
  if (config.value.strategy_name) {
    strategyParams.value = await getStrategyParams(config.value.strategy_name);
    // 初始化参数默认值
    const params: Record<string, any> = {};
    for (const [key, param] of Object.entries(strategyParams.value)) {
      // 确保布尔类型参数正确初始化
      if (param.type === 'boolean') {
        params[key] = param.default !== undefined ? param.default : false;
      } else {
        params[key] = param.default !== undefined ? param.default : (param.type === 'number' ? 0 : '');
      }
    }
    config.value.strategy_params = params;
  }
}

function handleRun() {
  emit('run', { ...config.value }, backtestType.value);
}

function handleReset() {
  if (backtestType.value === 'futures') {
    config.value = {
      futures_code: '',
      strategy_name: 'dual_ma',
      strategy_params: {},
      days: 180,
      initial_capital: 100000,
      commission_rate: 0.0003,
      slippage: 0.0002,
      margin_rate: 0.15,
      contract_multiplier: 10,
      max_position: 10,
      max_margin_rate: 0.8,
      stop_loss_ratio: 0.05,
      take_profit_ratio: 0.10
    } as BacktestRequest;
  } else {
    config.value = {
      stock_code: '',
      strategy_name: 'dual_ma',
      strategy_params: {},
      days: 180,
      initial_capital: 100000,
      commission_rate: 0.0003,
      slippage: 0.0002,
      stamp_tax_rate: 0.001,
      min_commission: 5.0,
      max_position: 10000,
      stop_loss_ratio: 0.05,
      take_profit_ratio: 0.10
    } as StockBacktestRequest;
  }
  onStrategyChange();
}

onMounted(async () => {
  strategies.value = await getStrategyTemplates();
  await onStrategyChange();
});
</script>


<style scoped>
.backtest-config {
  margin-bottom: 0;
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  border: none;
}

:deep(.el-card__header span) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.config-form {
  max-width: 100%;
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 0;
}

.form-col {
  min-width: 0;
}

.strategy-params {
  border: 1px solid #e5e7eb;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
  margin-top: 8px;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.param-item {
  margin-bottom: 0;
}

.param-item :deep(.el-form-item__label) {
  font-size: 13px;
  margin-bottom: 8px;
}

.action-buttons {
  margin-top: 32px;
  margin-bottom: 0;
  text-align: center;
}

.action-buttons :deep(.el-form-item__content) {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.run-button {
  min-width: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  font-size: 16px;
  padding: 14px 32px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.run-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

:deep(.el-input),
:deep(.el-select),
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .params-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons :deep(.el-form-item__content) {
    flex-direction: column;
  }
  
  .run-button {
    width: 100%;
  }
}
</style>

