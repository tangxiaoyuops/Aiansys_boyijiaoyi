import axios from 'axios';

// 如果设置了环境变量则使用，否则在生产环境使用相对路径，开发环境使用 localhost:8000
const getBaseURL = () => {
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  // 生产环境（集成到后端）使用相对路径
  if (import.meta.env.PROD) {
    return '';
  }
  // 开发环境使用 localhost:8000
  return 'http://localhost:8000';
};

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 20000
});

api.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
);



