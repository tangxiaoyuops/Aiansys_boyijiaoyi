<template>
  <div class="futures-view">
    <div class="sidebar">
      <ProgressPanel :progress="store.progress" />
      <RiskPanel :risk-data="store.analysisResults.risk" />
      <SpreadPanel :spread-data="store.analysisResults.spread" />
      <FundamentalPanel :fundamental-data="store.analysisResults.fundamental" />
    </div>
    <div class="content">
      <div class="main-content">
        <MessageList :messages="store.messages" />
        <FuturesChart
          v-if="store.futuresData && store.futuresData.data"
          :data="store.futuresData.data"
          :title="`${store.futuresData.name || store.futuresData.code} - K线图`"
        />
        <FuturesDataTable
          v-if="store.futuresData && store.futuresData.data"
          :data="store.futuresData.data"
          title="期货数据表格"
        />
      </div>
      <div class="footer">
        <FuturesInput :loading="store.loading" @send="handleSend" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFuturesStore } from '../stores/futures';
import MessageList from '../components/MessageList.vue';
import FuturesInput from '../components/FuturesInput.vue';
import ProgressPanel from '../components/ProgressPanel.vue';
import FuturesChart from '../components/FuturesChart.vue';
import FuturesDataTable from '../components/FuturesDataTable.vue';
import RiskPanel from '../components/RiskPanel.vue';
import SpreadPanel from '../components/SpreadPanel.vue';
import FundamentalPanel from '../components/FundamentalPanel.vue';
import { startFuturesStream } from '../utils/futures-sse';
import { getFuturesData } from '../api/futures';

const store = useFuturesStore();
let stopStream: (() => void) | null = null;

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const handleSend = async (msg: string) => {
  // 停止上一条流
  if (stopStream) stopStream();

  store.appendMessage({ role: 'user', content: msg });
  store.setLoading(true);
  store.clearProgress();

  const payload = store.buildPayload(msg);
  
  // 如果有期货代码，先获取数据
  if (payload.futures_code) {
    try {
      const dataRes = await getFuturesData(payload.futures_code, payload.days || 180);
      if (dataRes.data.success) {
        store.setFuturesData({
          code: dataRes.data.futures_code,
          name: dataRes.data.futures_name,
          data: dataRes.data.data
        });
      }
    } catch (err) {
      console.error('获取期货数据失败:', err);
    }
  }

  stopStream = startFuturesStream({
    baseURL,
    ...payload,
    onEvent: (data) => {
      const type = data.type || 'message';
      if (type === 'start') {
        store.appendMessage({ role: 'system', content: data.message || '开始期货分析...', type });
        if (data.session_id) {
          store.setSessionId(data.session_id);
        }
      } else if (type === 'progress') {
        store.addProgress(data.node, data.message || data.node);
      } else if (type === 'result') {
        store.appendMessage({ role: 'system', content: data.report || '', type });
        if (data.session_id) {
          store.setSessionId(data.session_id);
        }
      } else if (type === 'detail') {
        // 保存分析结果数据
        if (data.data) {
          store.setAnalysisResults(data.data);
        }
        store.appendMessage({
          role: 'system',
          content: '',
          type,
          meta: data.data
        });
      } else if (type === 'error') {
        store.appendMessage({ role: 'system', content: `错误：${data.message || ''}`, type });
        store.setLoading(false);
      } else if (type === 'done') {
        store.appendMessage({ role: 'system', content: '分析完成', type });
        store.setLoading(false);
      }
    },
    onError: (err) => {
      store.appendMessage({ role: 'system', content: `流式连接错误：${err?.message || err}`, type: 'error' });
      store.setLoading(false);
    }
  });
};
</script>

<style scoped>
.futures-view {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
.sidebar {
  width: 300px;
  padding: 12px;
  border-right: 1px solid #1f2937;
  flex-shrink: 0;
  overflow-y: auto;
  background-color: #f9fafb;
}
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
.footer {
  border-top: 1px solid #1f2937;
  flex-shrink: 0;
}
</style>

