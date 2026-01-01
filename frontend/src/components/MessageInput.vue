<template>

  <div class="input-bar card">

    <div class="form-row">

      <el-input

        v-model="localMessage"

        type="textarea"

        rows="2"

        placeholder="请输入分析问题，例如：分析000001的博弈分析"

        :disabled="loading"

      />

    </div>

    <div class="form-row options">

      <el-input

        v-model="form.stock_code"

        placeholder="股票代码(可选)"

        style="max-width: 120px"

        :disabled="loading"

      />

      <el-select

        v-model="form.analysis_type"

        placeholder="分析类型"

        style="max-width: 140px"

        :disabled="loading"

      >

        <el-option label="自动" value="auto" />

        <el-option label="常规分析" value="regular" />

        <el-option label="博弈分析" value="game_theory" />

      </el-select>

      <el-input-number

        v-model="form.days"

        :min="30"

        :max="400"

        :step="10"

        :disabled="loading"

        controls-position="right"

      />

      <el-input-number

        v-model="form.initial_capital"

        :min="10000"

        :step="10000"

        :disabled="loading"

        controls-position="right"

        placeholder="初始资金"

        style="max-width: 160px"

      />

      <el-switch

        v-model="form.run_backtest"

        active-text="回测"

        :disabled="loading"

      />

      <el-button type="primary" :loading="loading" @click="handleSend">

        发送

      </el-button>

    </div>

  </div>

</template>



<script setup lang="ts">

import { reactive, ref, watch } from 'vue';

import { useChatStore } from '../stores/chat';



const emit = defineEmits<{

  (e: 'send', message: string): void;

}>();



const props = defineProps<{

  loading: boolean;

}>();



const store = useChatStore();

const localMessage = ref('');

const form = reactive({ ...store.form });



watch(

  form,

  (v) => {

    store.form = { ...v };

  },

  { deep: true }

);



const handleSend = () => {

  if (!localMessage.value.trim()) return;

  emit('send', localMessage.value.trim());

  localMessage.value = '';

};

</script>



<style scoped>

.input-bar {

  padding: 12px;

  border-top: 1px solid #1f2937;

}

.form-row {

  display: flex;

  gap: 8px;

}

.form-row + .form-row {

  margin-top: 10px;

}

.options {

  align-items: center;

}

</style>





