<template>
  <div class="agent-message" :class="message.role">
    <!-- 用户消息 -->
    <div v-if="message.role === 'user'" class="user-message">
      <div class="message-header">
        <el-icon><User /></el-icon>
        <span>我</span>
      </div>
      <div class="message-content">{{ message.content }}</div>
    </div>

    <!-- 系统消息 -->
    <div v-else class="system-message">
      <div class="message-header">
        <el-icon v-if="message.type === 'error'" color="#f56c6c"><CircleClose /></el-icon>
        <el-icon v-else-if="message.type === 'loading'" class="is-loading"><Loading /></el-icon>
        <el-icon v-else color="#67c23a"><CircleCheck /></el-icon>
        <span>系统</span>
        <el-tag v-if="message.type === 'config'" size="small" type="success">配置</el-tag>
        <el-tag v-if="message.type === 'result'" size="small" type="primary">分析结果</el-tag>
        <el-tag v-if="message.type === 'error'" size="small" type="danger">错误</el-tag>
      </div>
      
      <!-- 基础内容 -->
      <div class="message-content">{{ message.content }}</div>

      <!-- 详细信息(可展开) -->
      <div v-if="message.details" class="message-details">
        <el-collapse>
          <!-- 执行统计 -->
          <el-collapse-item title="📊 执行统计" name="stats">
            <div class="stats-grid">
              <div class="stat-item">
                <span class="label">迭代次数:</span>
                <span class="value">{{ message.details.iterations }}</span>
              </div>
              <div class="stat-item">
                <span class="label">工具调用:</span>
                <span class="value">{{ message.details.executionTrace?.length || 0 }} 次</span>
              </div>
            </div>
          </el-collapse-item>

          <!-- 执行轨迹 -->
          <el-collapse-item title="🔍 执行轨迹(每轮详细过程)" name="trace">
            <div class="execution-trace">
              <div
                v-for="(trace, index) in message.details.executionTrace"
                :key="index"
                class="trace-step"
              >
                <div class="step-header">
                  <el-tag :type="trace.result?.status === 'success' ? 'success' : 'danger'">
                    第 {{ index + 1 }} 轮
                  </el-tag>
                  <span class="step-time">{{ trace.result?.execution_time?.toFixed(2) || 0 }}s</span>
                </div>
                
                <div class="step-content">
                  <!-- 思考过程 -->
                  <div class="step-section">
                    <div class="section-title">💭 思考</div>
                    <div class="section-content">{{ trace.decision?.thinking || '无' }}</div>
                  </div>

                  <!-- 观察 -->
                  <div class="step-section">
                    <div class="section-title">👁️ 观察</div>
                    <div class="section-content">{{ trace.decision?.observation || '无' }}</div>
                  </div>

                  <!-- 行动 -->
                  <div class="step-section">
                    <div class="section-title">🎬 行动</div>
                    <div class="section-content">
                      <div class="tool-info">
                        <el-tag size="small">工具: {{ trace.decision?.action?.tool || 'none' }}</el-tag>
                      </div>
                      <div v-if="trace.decision?.action?.parameters" class="parameters">
                        <strong>参数:</strong>
                        <pre>{{ JSON.stringify(trace.decision.action.parameters, null, 2) }}</pre>
                      </div>
                    </div>
                  </div>

                  <!-- 执行结果 -->
                  <div class="step-section">
                    <div class="section-title">📋 执行结果</div>
                    <div class="section-content">
                      <div class="result-status">
                        状态: 
                        <el-tag :type="trace.result?.status === 'success' ? 'success' : 'danger'" size="small">
                          {{ trace.result?.status || 'unknown' }}
                        </el-tag>
                      </div>
                      
                      <!-- 成功时显示结果 -->
                      <div v-if="trace.result?.status === 'success' && trace.result?.result" class="result-content">
                        <details>
                          <summary>查看返回数据</summary>
                          <pre>{{ JSON.stringify(trace.result.result, null, 2) }}</pre>
                        </details>
                      </div>

                      <!-- 错误时显示错误信息 -->
                      <div v-if="trace.result?.error" class="error-info">
                        <el-alert type="error" :closable="false">
                          {{ trace.result.error }}
                        </el-alert>
                      </div>
                    </div>
                  </div>

                  <!-- 判断 -->
                  <div class="step-section" v-if="trace.decision?.evaluation">
                    <div class="section-title">✅ 判断</div>
                    <div class="section-content">
                      <div>任务完成: {{ trace.decision.evaluation.task_complete ? '是' : '否' }}</div>
                      <div>理由: {{ trace.decision.evaluation.reason || '无' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>

          <!-- 收集的信息 -->
          <el-collapse-item title="📦 收集的数据" name="collected">
            <div class="collected-info">
              <div v-if="Object.keys(message.details.collectedInfo || {}).length === 0" class="empty">
                无收集的数据
              </div>
              <div v-else>
                <div
                  v-for="(info, toolName) in message.details.collectedInfo"
                  :key="toolName"
                  class="info-item"
                >
                  <div class="info-header">
                    <el-tag size="small">{{ toolName }}</el-tag>
                  </div>
                  <details>
                    <summary>查看数据</summary>
                    <pre>{{ JSON.stringify(info, null, 2) }}</pre>
                  </details>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue';

defineProps<{
  message: any;
}>();
</script>

<style scoped>
.agent-message {
  margin-bottom: 20px;
}

.user-message,
.system-message {
  padding: 15px;
  border-radius: 8px;
}

.user-message {
  background: #e6f7ff;
  border-left: 4px solid #1890ff;
}

.system-message {
  background: #f6f8fa;
  border-left: 4px solid #52c41a;
}

.system-message.error {
  border-left-color: #f5222d;
  background: #fff1f0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  font-size: 14px;
}

.message-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

.message-details {
  margin-top: 15px;
  border-top: 1px dashed #e8e8e8;
  padding-top: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.stat-item .label {
  color: #666;
}

.stat-item .value {
  font-weight: 600;
  color: #1890ff;
}

.execution-trace {
  max-height: 600px;
  overflow-y: auto;
}

.trace-step {
  margin-bottom: 20px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.step-time {
  color: #999;
  font-size: 12px;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-section {
  background: white;
  padding: 10px;
  border-radius: 4px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 13px;
}

.section-content {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.tool-info {
  margin-bottom: 8px;
}

.parameters pre,
.result-content pre,
.info-item pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.result-status {
  margin-bottom: 8px;
}

.error-info {
  margin-top: 8px;
}

.collected-info {
  max-height: 400px;
  overflow-y: auto;
}

.info-item {
  margin-bottom: 12px;
  padding: 10px;
  background: #fafafa;
  border-radius: 4px;
}

.info-header {
  margin-bottom: 8px;
}

.empty {
  color: #999;
  text-align: center;
  padding: 20px;
}

/* 折叠面板样式 */
:deep(.el-collapse-item__header) {
  font-weight: 600;
  font-size: 14px;
}

:deep(.el-collapse-item__content) {
  padding: 15px 0;
}

details summary {
  cursor: pointer;
  color: #1890ff;
  font-size: 13px;
}

details summary:hover {
  text-decoration: underline;
}

details pre {
  margin-top: 10px;
}
</style>
