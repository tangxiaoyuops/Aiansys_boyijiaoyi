<template>
  <div class="agent-chat-view">
    <!-- 左侧工具面板 -->
    <div class="sidebar left-sidebar">
      <div class="sidebar-header">
        <h3>🛠️ Agent工具库</h3>
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

    <!-- 中间对话区域 -->
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

    <!-- 右侧详情面板 -->
    <div class="sidebar right-sidebar" v-if="currentExecutionDetails">
      <div class="sidebar-header">
        <h3>📊 执行详情</h3>
      </div>
      
      <!-- 执行统计 -->
      <div class="execution-stats">
        <div class="stat-card">
          <div class="stat-label">迭代次数</div>
          <div class="stat-value">{{ currentExecutionDetails.iterations || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">工具调用</div>
          <div class="stat-value">{{ currentExecutionDetails.executionTrace?.length || 0 }}次</div>
        </div>
      </div>

      <!-- 执行轨迹 -->
      <div class="execution-trace-panel">
        <div class="panel-header">
          <span>🔍 执行轨迹</span>
          <el-button 
            text 
            size="small" 
            @click="expandAllTrace = !expandAllTrace"
          >
            {{ expandAllTrace ? '全部收起' : '全部展开' }}
          </el-button>
        </div>
        
        <div class="trace-list">
          <div
            v-for="(trace, index) in currentExecutionDetails.executionTrace"
            :key="index"
            class="trace-item"
          >
            <div class="trace-header" @click="trace.expanded = !trace.expanded">
              <div class="trace-title">
                <el-tag :type="trace.result?.status === 'success' ? 'success' : 'danger'" size="small">
                  第{{ index + 1 }}轮
                </el-tag>
                <span class="tool-name">{{ trace.tool || trace.decision?.action?.tool || '思考' }}</span>
              </div>
              <div class="trace-meta">
                <span class="time">{{ trace.result?.execution_time?.toFixed(2) || 0 }}s</span>
                <el-icon :class="{'expanded': trace.expanded}">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
            
            <el-collapse-transition>
              <div v-show="trace.expanded || expandAllTrace" class="trace-body">
                <!-- 思考 -->
                <div class="trace-section" v-if="trace.decision?.thinking">
                  <div class="section-label">💭 思考</div>
                  <div class="section-content">{{ trace.decision.thinking }}</div>
                </div>
                
                <!-- 工具参数 -->
                <div class="trace-section" v-if="trace.parameters || trace.decision?.action?.parameters">
                  <div class="section-label">⚙️ 参数</div>
                  <pre class="code-block">{{ JSON.stringify(trace.parameters || trace.decision?.action?.parameters, null, 2) }}</pre>
                </div>
                
                <!-- 执行结果 -->
                <div class="trace-section">
                  <div class="section-label">📋 结果</div>
                  <div v-if="trace.result?.error" class="error-box">
                    ❌ {{ trace.result.error }}
                  </div>
                  <pre v-else-if="trace.result?.result" class="code-block">{{ JSON.stringify(trace.result.result, null, 2) }}</pre>
                  <div v-else class="empty-result">无结果数据</div>
                </div>
              </div>
            </el-collapse-transition>
          </div>
          
          <el-empty v-if="!currentExecutionDetails.executionTrace?.length" description="暂无执行轨迹" />
        </div>
      </div>

      <!-- 收集的数据 -->
      <div class="collected-data-panel">
        <div class="panel-header">
          <span>📦 收集的数据</span>
          <el-badge :value="Object.keys(currentExecutionDetails.collectedInfo || {}).length" />
        </div>
        
        <div class="data-list">
          <div
            v-for="(data, toolName, index) in currentExecutionDetails.collectedInfo"
            :key="toolName"
            class="data-item"
          >
            <div class="data-header" @click="data.expanded = !data.expanded">
              <el-tag size="small" type="info">{{ toolName }}</el-tag>
              <el-icon :class="{'expanded': data.expanded}">
                <ArrowDown />
              </el-icon>
            </div>
            
            <el-collapse-transition>
              <pre v-show="data.expanded" class="code-block">{{ JSON.stringify(data, null, 2) }}</pre>
            </el-collapse-transition>
          </div>
          
          <el-empty v-if="!Object.keys(currentExecutionDetails.collectedInfo || {}).length" description="暂无收集数据" />
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
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  CircleCheck,
  CircleClose,
  Tools,
  ArrowDown,
} from '@element-plus/icons-vue';
import axios from 'axios';
import AgentMessage from '../components/AgentMessage_v2.vue';

// API基础URL
const API_BASE = 'http://localhost:8000/api';

// 状态
const isConfigured = ref(false);
const loading = ref(false);
const configuring = ref(false);
const showConfigDialog = ref(false);
const expandAllTrace = ref(false);

// 配置表单
const configForm = ref({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
  model: import.meta.env.VITE_QWEN_MODEL || 'GLM-5',
  baseUrl: import.meta.env.VITE_OPENAI_BASE_URL || '',
});

// 对话相关
const messages = ref<Array<any>>([]);
const userInput = ref('');

// 当前执行的详情(显示在右侧面板)
const currentExecutionDetails = ref<any>(null);

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
        content: `✅ Agent配置成功! 已加载 ${response.data.tools_count} 个工具。`,
        type: 'config'
      }];
      
      currentExecutionDetails.value = null; // 清空右侧面板
      
      ElMessage.success('Agent配置成功!');
    }
  } catch (error: any) {
    console.error('配置失败:', error);
    
    messages.value.push({
      role: 'system',
      content: `❌ 配置失败: ${error.response?.data?.detail || error.message}`,
      type: 'error'
    });
    
    ElMessage.error('配置失败');
  } finally {
    configuring.value = false;
  }
};

// 发送消息
const handleSend = async () => {
  if (!isConfigured.value || !userInput.value.trim()) return;

  const userMessage = userInput.value.trim();
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage
  });

  userInput.value = '';
  loading.value = true;

  // 初始化执行详情(显示在右侧面板)
  currentExecutionDetails.value = {
    iterations: 0,
    executionTrace: [],
    collectedInfo: {}
  };

  // 添加系统处理中消息
  const systemMessageIndex = messages.value.length;
  messages.value.push({
    role: 'system',
    content: '⏳ 正在分析中...',
    type: 'loading'
  });

  try {
    const response = await axios.post(`${API_BASE}/agent/analyze`, {
      task: userMessage,
      max_iterations: 10,
      context: {
        conversation_history: messages.value.slice(0, -1).map(m => ({
          role: m.role,
          content: m.content
        }))
      }
    });

    if (response.data.success) {
      // 更新消息
      messages.value[systemMessageIndex] = {
        role: 'system',
        content: response.data.response,
        type: 'result'
      };

      // 更新右侧面板的执行详情
      currentExecutionDetails.value = {
        iterations: response.data.iterations,
        executionTrace: response.data.execution_trace || [],
        collectedInfo: response.data.collected_info || {}
      };
    }

  } catch (error: any) {
    console.error('分析失败:', error);
    
    messages.value[systemMessageIndex] = {
      role: 'system',
      content: `❌ 分析失败: ${error.response?.data?.detail || error.message}`,
      type: 'error'
    };
    
    currentExecutionDetails.value = null;
  } finally {
    loading.value = false;
  }
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
  
  if (configForm.value.apiKey && configForm.value.baseUrl) {
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
      content: '👋 欢迎使用博弈交易Agent框架!\n\n请先点击左侧"配置Agent"按钮开始使用。',
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

/* 侧边栏通用样式 */
.sidebar {
  width: 280px;
  padding: 15px;
  background: white;
  flex-shrink: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e4e7ed;
}

.left-sidebar {
  border-right: 1px solid #e4e7ed;
}

.right-sidebar {
  border-right: none;
  border-left: 1px solid #e4e7ed;
  width: 320px;
}

.sidebar-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Agent状态 */
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

/* 工具列表 */
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

/* 中间对话区域 */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
  min-width: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
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

/* 右侧面板 - 执行统计 */
.execution-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

/* 右侧面板 - 执行轨迹 */
.execution-trace-panel {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 10px;
  font-weight: 600;
  font-size: 14px;
}

.trace-list {
  flex: 1;
  overflow-y: auto;
}

.trace-item {
  margin-bottom: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.trace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  background: #f9fafb;
  transition: all 0.3s;
}

.trace-header:hover {
  background: #f3f4f6;
}

.trace-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trace-title .tool-name {
  font-weight: 500;
  color: #374151;
}

.trace-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time {
  color: #9ca3af;
  font-size: 12px;
}

.trace-meta .el-icon {
  transition: transform 0.3s;
}

.trace-meta .el-icon.expanded {
  transform: rotate(180deg);
}

.trace-body {
  padding: 12px;
  background: white;
}

.trace-section {
  margin-bottom: 12px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 6px;
}

.section-content {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
}

.code-block {
  background: #1f2937;
  color: #e5e7eb;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
  margin: 0;
}

.error-box {
  background: #fef2f2;
  color: #dc2626;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.empty-result {
  color: #9ca3af;
  font-size: 13px;
  text-align: center;
  padding: 10px;
}

/* 右侧面板 - 收集的数据 */
.collected-data-panel {
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px;
}

.data-list {
  flex: 1;
  overflow-y: auto;
}

.data-item {
  margin-bottom: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  background: #f9fafb;
}

.data-header .el-icon {
  transition: transform 0.3s;
}

.data-header .el-icon.expanded {
  transform: rotate(180deg);
}

/* 响应式 */
@media (max-width: 1200px) {
  .right-sidebar {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .right-sidebar {
    display: none;
  }
}

@media (max-width: 767.98px) {
  .agent-chat-view {
    flex-direction: column;
  }

  .left-sidebar {
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
