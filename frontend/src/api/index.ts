import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000 // 180秒超时（3分钟），紫薇斗数分析较慢
});

api.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
);

// 默认导出，方便使用
export default api;



