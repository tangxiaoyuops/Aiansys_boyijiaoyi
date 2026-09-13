<template>
  <div class="agent-chat-view">
    <!-- 左侧工具面板 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>Agent工具库</h3>
      </div>
      
      <!-- Agent状态 -->
      <div class="agent-status">
        <div class="status-item">
          <el-icon :class="{'status-active': isConfigured}">
            <CircleCheck v-if="isConfigured" />
            <CircleClose v-else />
          </el-icon>
          <span>{{ isConfigured ? '已就绪' : '未配置' }}</span>
        </div>
        <div class="status-item">
          <el-icon><Tools /></el-icon>
          <span>工具: {{ tools.length }}</span>
        </div>
      </div>

      <!-- 配置按钮 -->
      <el-button
        v-if="!isConfigured"
        type="primary"
        size="small"
        @click="showConfigDialog = true"
        style="width: 100%; margin-bottom: 15px"
      >
        配置Agent
      </el-button>

      <!-- 工具列表 -->
      <div class="tools-list">
        <div class="tools-header">可用工具</div>
        <div
          v-for="tool in tools"
          :key="tool.name"
          class="tool-item"
          @click="showToolDetail(tool)"
        >
          <div class="tool-name">{{ tool.name }}</div>
          <el-tag size="small" type="info">{{ tool.type }}</el-tag>
        </div>
      </div>
    </div>

    <!-- 右侧对话区域 -->
    <div class="content">
      <!-- 消息列表 -->
      <div class="messages-container">
        <AgentMessage
          v-for="(msg, index) in messages"
          :key="index"
          :message="msg"
        />
        
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <el-empty description="开始对话吧!" />
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="footer">
        <div class="input-container">
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="3"
            placeholder="输入您的分析需求,例如:&#10;- 分析股票000001的阶段&#10;- 识别洗盘特征&#10;- 给出买卖建议"
            :disabled="!isConfigured || loading"
            @keydown.enter.ctrl="handleSend"
          />
          <div class="input-actions">
            <div class="quick-actions">
              <el-button
                v-for="task in quickTasks"
                :key="task.label"
                size="small"
                :disabled="!isConfigured || loading"
                @click="userInput = task.task"
              >
                {{ task.label }}
              </el-button>
            </div>
            <el-button
              type="primary"
              :loading="loading"
              :disabled="!isConfigured || !userInput.trim()"
              @click="handleSend"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="配置Agent"
      width="500px"
    >
      <el-form label-position="top">
        <el-form-item label="OpenAI API Key *" required>
          <el-input
            v-model="configForm.apiKey"
            type="password"
            placeholder="sk-..."
            show-password
          />
        </el-form-item>

        <el-form-item label="模型">
          <el-input v-model="configForm.model" placeholder="GLM-5" />
        </el-form-item>

        <el-form-item label="API Base URL (可选)">
          <el-input
            v-model="configForm.baseUrl"
            placeholder="https://api.openai.com/v1"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="configuring"
          @click="configureAgent"
        >
          配置
        </el-button>
      </template>
    </el-dialog>

    <!-- 工具详情对话框 -->
    <el-dialog v-model="toolDetailVisible" title="工具详情" width="500px">
      <div v-if="selectedTool">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="工具名称">
            {{ selectedTool.name }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ selectedTool.description }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag>{{ selectedTool.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="能力标签">
            <el-tag
              v-for="cap in selectedTool.capabilities"
              :key="cap"
              size="small"
              style="margin-right: 5px"
            >
              {{ cap }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  CircleCheck,
  CircleClose,
  Tools,
} from '@element-plus/icons-vue';
import axios from 'axios';
import AgentMessage from '../components/AgentMessage.vue';

// API基础URL
const API_BASE = 'http://localhost:8000/api';

// 状态
const isConfigured = ref(false);
const loading = ref(false);
const configuring = ref(false);
const showConfigDialog = ref(false);

// 从环境变量读取默认配置
const defaultApiKey = import.meta.env.VITE_OPENAI_API_KEY || '';
const defaultBaseUrl = import.meta.env.VITE_OPENAI_BASE_URL || '';
const defaultModel = import.meta.env.VITE_QWEN_MODEL || 'GLM-5';

// 配置表单
const configForm = ref({
  apiKey: defaultApiKey,
  model: defaultModel,
  baseUrl: defaultBaseUrl,
});

// 对话相关
const messages = ref<Array<any>>([]);
const userInput = ref('');

// 工具相关
const tools = ref<any[]>([]);
const toolDetailVisible = ref(false);
const selectedTool = ref<any>(null);

// 快速任务
const quickTasks = [
  { label: '阶段分析', task: '分析股票000001,判断当前所处的阶段' },
  { label: '洗盘识别', task: '分析股票000001,识别洗盘特征' },
  { label: '买卖建议', task: '分析股票000001,给出买卖建议' },
  { label: '完整分析', task: '完整分析股票000001' },
];

// 加载工具列表
const loadTools = async () => {
  try {
    const response = await axios.get(`${API_BASE}/agent/tools`);
    tools.value = response.data.tools || [];
  } catch (error) {
    console.error('加载工具失败:', error);
  }
};

// 配置Agent
const configureAgent = async () => {
  if (!configForm.value.apiKey) {
    ElMessage.warning('请输入API Key');
    return;
  }

  configuring.value = true;
  try {
    const response = await axios.post(`${API_BASE}/agent/config`, {
      api_key: configForm.value.apiKey,
      model: configForm.value.model,
      base_url: configForm.value.baseUrl || null,
    });

    if (response.data.success) {
      isConfigured.value = true;
      showConfigDialog.value = false;
      
      messages.value = [{
        role: 'system',
        content: `✅ Agent配置成功! 已加载 ${response.data.tools_count} 个工具。\n\n现在可以开始对话了。`,
        type: 'config'
      }];
      
      ElMessage.success('Agent配置成功!');
    }
  } catch (error: any) {
    console.error('配置失败:', error);
    let errorMsg = '配置失败';
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail;
    } else if (error.message) {
      errorMsg = error.message;
    }
    
    messages.value.push({
      role: 'system',
      content: `❌ 配置失败: ${errorMsg}`,
      type: 'error'
    });
    
    ElMessage.error(errorMsg);
  } finally {
    configuring.value = false;
  }
};

// 发送消息 - 使用流式API
const handleSend = async () => {
  if (!isConfigured.value) {
    ElMessage.warning('请先配置Agent');
    return;
  }

  if (!userInput.value.trim()) {
    return;
  }

  const userMessage = userInput.value.trim();
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage
  });

  // 清空输入
  userInput.value = '';
  loading.value = true;

  // 添加系统处理中消息
  const systemMessageIndex = messages.value.length;
  messages.value.push({
    role: 'system',
    content: '⏳ 正在连接...',
    type: 'loading',
    details: {
      iterations: 0,
      executionTrace: [],
      collectedInfo: {},
      progress: 0
    }
  });

  try {
    // 使用流式API
    const response = await fetch(`${API_BASE}/agent/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task: userMessage,
        max_iterations: 10,
        context: {
          conversation_history: messages.value.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content
          }))
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 读取流式响应
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        // 解码数据块
        buffer += decoder.decode(value, { stream: true });
        
        // 按行分割SSE数据
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // 保留最后一个不完整的块
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleStreamEvent(data, systemMessageIndex);
            } catch (e) {
              console.error('解析SSE数据失败:', e, line);
            }
          }
        }
      }
    }

  } catch (error: any) {
    console.error('分析失败:', error);
    
    let errorMsg = '网络错误';
    if (error.message) {
      errorMsg = error.message;
    }
    
    messages.value[systemMessageIndex] = {
      role: 'system',
      content: `❌ 分析失败: ${errorMsg}`,
      type: 'error'
    };
  } finally {
    loading.value = false;
  }
};

// 处理流式事件
const handleStreamEvent = (data: any, messageIndex: number) => {
  const msg = messages.value[messageIndex];
  
  switch (data.type) {
    case 'start':
      msg.content = '🚀 ' + data.message;
      break;

    case 'iteration_start':
      msg.content = `⏳ 第 ${data.iteration} 轮分析...`;
      msg.details.iterations = data.iteration;
      break;

    case 'thinking':
      msg.content = '💭 ' + data.message;
      break;

    case 'thought':
      // 添加到执行轨迹
      msg.details.executionTrace.push({
        iteration: msg.details.executionTrace.length + 1,
        decision: {
          observation: data.observation,
          thinking: data.thinking,
          action: data.action,
          evaluation: data.evaluation
        }
      });
      msg.content = `💭 思考: ${data.thinking?.substring(0, 50)}...`;
      break;

    case 'action_start':
      msg.content = `🔧 调用工具: ${data.tool}`;
      // 更新最后一步的工具信息
      const lastTrace = msg.details.executionTrace[msg.details.executionTrace.length - 1];
      if (lastTrace) {
        lastTrace.tool = data.tool;
        lastTrace.parameters = data.parameters;
      }
      break;

    case 'action_result':
      msg.content = `${data.status === 'success' ? '✅' : '❌'} ${data.tool}: ${data.status}`;
      // 更新最后一步的结果
      const lastTraceResult = msg.details.executionTrace[msg.details.executionTrace.length - 1];
      if (lastTraceResult) {
        lastTraceResult.result = {
          status: data.status,
          result: data.result,
          error: data.error,
          execution_time: data.execution_time
        };
      }
      break;

    case 'evaluation':
      if (data.task_complete) {
        msg.content = '✅ 任务完成,正在生成报告...';
      }
      break;

    case 'complete':
      // 最终结果
      msg.content = data.response;
      msg.type = 'result';
      msg.details.iterations = data.iterations;
      msg.details.executionTrace = data.execution_trace || msg.details.executionTrace;
      msg.details.collectedInfo = data.collected_info || {};
      break;

    case 'error':
      msg.content = `❌ 错误: ${data.message}`;
      msg.type = 'error';
      break;
  }

  // 强制更新视图
  messages.value = [...messages.value];
};

// 显示工具详情
const showToolDetail = (tool: any) => {
  selectedTool.value = tool;
  toolDetailVisible.value = true;
};

// 检查健康状态
const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE}/health`);
    if (response.data.agent_configured) {
      isConfigured.value = true;
    }
  } catch (error) {
    console.log('服务未启动或未配置');
  }
};

onMounted(() => {
  loadTools();
  checkHealth();
  
  // 检查是否有环境变量配置
  if (defaultApiKey && defaultBaseUrl) {
    messages.value.push({
      role: 'system',
      content: '🔄 检测到环境变量配置,正在自动初始化...',
      type: 'loading'
    });
    
    setTimeout(() => {
      configureAgent();
    }, 1000);
  } else {
    messages.value.push({
      role: 'system',
      content: '👋 欢迎使用博弈交易Agent框架!\n\n这是一个支持多轮对话的智能分析系统。\n\n请先点击左侧"配置Agent"按钮开始使用。',
      type: 'welcome'
    });
  }
});
</script>

<style scoped>
.agent-chat-view {
  display: flex;
  flex-direction: row;
  height: 100%;
  overflow: hidden;
  background: #f5f7fa;
}

/* 左侧工具面板 */
.sidebar {
  width: 260px;
  padding: 15px;
  border-right: 1px solid #e4e7ed;
  background: white;
  flex-shrink: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  margin-bottom: 15px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.agent-status {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.status-active {
  color: #67c23a;
}

.tools-list {
  flex: 1;
  overflow-y: auto;
}

.tools-header {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.tool-item {
  padding: 10px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-item:hover {
  background: #e6f7ff;
  border-left: 3px solid #409eff;
}

.tool-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

/* 右侧对话区域 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.footer {
  flex-shrink: 0;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 响应式 */
@media (max-width: 767.98px) {
  .agent-chat-view {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }

  .tools-list {
    display: none;
  }
}
</style>
