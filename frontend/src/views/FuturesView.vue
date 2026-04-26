<template>
  <div class="futures-view">
    <!-- 侧边栏：进度面板 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3 class="sidebar-title">分析进度</h3>
        <div class="status-indicator" :class="{ active: store.loading }">
          <span class="status-dot"></span>
          <span class="status-text">{{ store.loading ? '分析中' : '就绪' }}</span>
        </div>
      </div>
      <ProgressPanel :progress="store.progress" />
    </aside>

    <!-- 主内容区 -->
    <main class="content">
      <!-- 消息列表容器 -->
      <div class="message-container">
        <MessageList :messages="store.messages" />
      </div>

      <!-- 输入区域 -->
      <div class="footer">
        <FuturesMessageInput :loading="store.loading" @send="handleSend" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useFuturesStore } from '../stores/futures';
import MessageList from '../components/MessageList.vue';
import FuturesMessageInput from '../components/FuturesMessageInput.vue';
import ProgressPanel from '../components/ProgressPanel.vue';
import { startFuturesStream } from '../utils/futures-sse';

const store = useFuturesStore();
let stopStream: (() => void) | null = null;

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const handleSend = (msg: string) => {
  // 停止上一条流
  if (stopStream) stopStream();

  store.appendMessage({ role: 'user', content: msg });
  store.setLoading(true);
  store.clearProgress();

  const payload = store.buildPayload(msg);
  stopStream = startFuturesStream({
    baseURL,
    ...payload,
    onEvent: (data) => {
      const type = data.type || 'message';
      if (type === 'start') {
        store.appendMessage({ role: 'system', content: data.message || '开始分析...', type });
      } else if (type === 'progress') {
        store.addProgress(data.node, data.message || data.node);
      } else if (type === 'result') {
        store.appendMessage({ role: 'system', content: data.report || '', type });
      } else if (type === 'detail') {
        store.appendMessage({
          role: 'system',
          content: '',
          type: 'detail',
          meta: data,
        });
      } else if (type === 'error') {
        store.appendMessage({ role: 'system', content: `错误: ${data.message || '未知错误'}`, type: 'error' });
        store.setLoading(false);
      } else if (type === 'done') {
        store.setLoading(false);
      }
    },
  });
};
</script>

<style scoped>
/* 金融科技主题颜色变量 */
.futures-view {
  --fintech-bg: #0F172A;
  --fintech-surface: #1E293B;
  --fintech-surface-elevated: #334155;
  --fintech-primary: #F59E0B;
  --fintech-secondary: #FBBF24;
  --fintech-accent: #8B5CF6;
  --fintech-text: #F8FAFC;
  --fintech-text-secondary: #CBD5E1;
  --fintech-border: #334155;
  --fintech-border-light: #475569;
  --fintech-success: #10B981;
  --fintech-danger: #EF4444;
  --fintech-glass: rgba(255, 255, 255, 0.05);
  --fintech-glass-border: rgba(255, 255, 255, 0.1);
}

.futures-view {
  display: flex;
  height: 100%;
  overflow: hidden;
  background: var(--fintech-bg);
  color: var(--fintech-text);
  position: relative;
}

/* 侧边栏：现代化玻璃态设计 */
.sidebar {
  width: 280px;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--fintech-surface) 0%, var(--fintech-bg) 100%);
  border-right: 1px solid var(--fintech-border);
  backdrop-filter: blur(10px);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--fintech-border);
  background: var(--fintech-glass);
  backdrop-filter: blur(10px);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--fintech-text);
  letter-spacing: 0.5px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  background: var(--fintech-surface-elevated);
  border: 1px solid var(--fintech-border);
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: rgba(245, 158, 11, 0.15);
  border-color: var(--fintech-primary);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--fintech-text-secondary);
  transition: all 0.3s ease;
}

.status-indicator.active .status-dot {
  background: var(--fintech-primary);
  box-shadow: 0 0 8px var(--fintech-primary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 13px;
  color: var(--fintech-text-secondary);
  font-weight: 500;
}

.status-indicator.active .status-text {
  color: var(--fintech-primary);
}

/* 主内容区：现代化卡片布局 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--fintech-bg);
  position: relative;
}

.content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(245, 158, 11, 0.1) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.message-container {
  flex: 1;
  position: relative;
  z-index: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 输入区域：玻璃态底部栏 */
.footer {
  flex-shrink: 0;
  padding: 20px 24px;
  border-top: 1px solid var(--fintech-border);
  background: linear-gradient(180deg, var(--fintech-bg) 0%, var(--fintech-surface) 100%);
  backdrop-filter: blur(20px);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 2;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
  }
}

@media (max-width: 767.98px) {
  .futures-view {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-width: 100%;
    height: auto;
    max-height: 180px;
    border-right: none;
    border-bottom: 1px solid var(--fintech-border);
    order: 2;
  }

  .sidebar-header {
    padding: 12px 16px;
  }

  .sidebar-title {
    font-size: 14px;
    margin-bottom: 8px;
  }

  .status-indicator {
    padding: 4px 10px;
  }

  .status-text {
    font-size: 12px;
  }

  .content {
    order: 1;
    flex: 1;
    min-height: 0;
  }

  .content::before {
    display: none;
  }

  .message-container {
    min-height: 200px;
  }

  .footer {
    order: 3;
    padding: 12px 16px;
    flex-shrink: 0;
  }
}

@media (max-width: 575.98px) {
  .sidebar {
    max-height: 140px;
  }

  .sidebar-header {
    padding: 10px 12px;
  }

  .sidebar-title {
    font-size: 13px;
  }

  .status-dot {
    width: 6px;
    height: 6px;
  }

  .footer {
    padding: 10px 12px;
  }
}

/* 横屏模式优化 */
@media (max-height: 500px) and (orientation: landscape) {
  .futures-view {
    flex-direction: row;
  }

  .sidebar {
    width: 200px;
    min-width: 200px;
    height: 100%;
    max-height: none;
    border-right: 1px solid var(--fintech-border);
    border-bottom: none;
    order: 1;
  }

  .content {
    order: 2;
  }

  .footer {
    order: 3;
  }
}
</style>
