import axios from 'axios';
import { ElMessage } from 'element-plus';

const service = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5分钟超时，因为AI分析可能需要很长时间
  headers: {
    'Content-Type': 'application/json'
  }
});

service.interceptors.request.use(
  (config) => {
    console.log('[Axios] 请求配置:', config);
    console.log('[Axios] 请求URL:', config.url);
    console.log('[Axios] baseURL:', config.baseURL);
    console.log('[Axios] 完整URL:', config.baseURL + config.url);
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
    console.log('[Axios] 响应拦截:', response);
    console.log('[Axios] 响应状态:', response.status);
    console.log('[Axios] 响应配置:', response.config);
    console.log('[Axios] 响应数据:', response.data);
    
    const res = response.data;
    
    if (res && typeof res === 'object' && 'success' in res) {
      console.log('[Axios] 返回格式化响应:', res);
      return res;
    }
    
    return response.data;
  },
  (error) => {
    console.error('[Axios] 响应错误:', error);
    
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
