import axios from 'axios';
import { ElMessage } from 'element-plus';
import { getTimestamp } from './accessLogger';

const service = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟超时，因为AI分析可能需要很长时间
  headers: {
    'Content-Type': 'application/json'
  }
});

service.interceptors.request.use(
  (config) => {
    const timestamp = getTimestamp();
    const url = `${config.baseURL || ''}${config.url || ''}`;
    const method = (config.method || 'GET').toUpperCase();
    (config as any).metadata = { startTime: Date.now() };
    console.log(`[${timestamp}] [Axios] ${method} ${url}`, config.params || config.data || {});
    return config;
  },
  (error) => {
    console.error('[Axios] 请求错误:', error);
    ElMessage.error(error.message || '请求失败');
    return Promise.reject(error);
  }
);

service.interceptors.response.use(
  (response) => {
    const timestamp = getTimestamp();
    const startTime = (response.config as any)?.metadata?.startTime || Date.now();
    const durationMs = Date.now() - startTime;
    const url = `${response.config.baseURL || ''}${response.config.url || ''}`;
    const method = (response.config.method || 'GET').toUpperCase();
    console.log(`[${timestamp}] [Axios] ${method} ${url} -> ${response.status} (${durationMs}ms)`);
    
    const res = response.data;
    
    if (res && typeof res === 'object' && 'success' in res) {
      console.log('[Axios] 返回格式化响应:', res);
      return res;
    }
    
    return response.data;
  },
  (error) => {
    const timestamp = getTimestamp();
    const startTime = (error.config as any)?.metadata?.startTime || Date.now();
    const durationMs = Date.now() - startTime;
    const url = `${error.config?.baseURL || ''}${error.config?.url || ''}`;
    const method = (error.config?.method || 'GET').toUpperCase();
    const status = error.response?.status || 'NO_RESPONSE';
    console.error(`[${timestamp}] [Axios] ${method} ${url} -> ${status} (${durationMs}ms)`, error);
    
    if (error.code === 'ECONNABORTED') {
      ElMessage({
        message: '分析请求超时，AI分析可能需要较长时间，请稍后重试或减少分析轮次',
        type: 'warning',
        duration: 5000
      });
    } else if (error.response) {
      const status = error.response.status;
      if (status === 401) {
        ElMessage.error('未授权，请重新登录');
      } else if (status === 403) {
        ElMessage.error('没有权限访问');
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在');
      } else if (status === 500) {
        ElMessage.error('服务器错误，请稍后重试');
      } else {
        ElMessage.error(`请求失败: ${error.message}`);
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接');
    } else {
      ElMessage.error(`请求配置错误: ${error.message}`);
    }
    
    return Promise.reject(error);
  }
);

export default service;
