import axios from 'axios';

// 获取并处理baseURL，确保协议正确
// 这个函数应该被所有地方使用，确保协议一致
export const getBaseURL = () => {
  let baseURL = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').trim().replace(/\/+$/, '');
  
  // 如果设置了HTTPS但当前页面是HTTP，自动转换为HTTP（避免协议不匹配）
  if (typeof window !== 'undefined' && window.location.protocol === 'http:') {
    if (baseURL.startsWith('https://')) {
      console.warn('[API] 检测到协议不匹配（HTTPS->HTTP），自动转换:', baseURL);
      baseURL = baseURL.replace('https://', 'http://');
    }
  }
  
  // 确保baseURL有协议前缀
  if (!baseURL.startsWith('http://') && !baseURL.startsWith('https://')) {
    baseURL = 'http://' + baseURL;
  }
  
  console.log('[API] 最终baseURL:', baseURL);
  return baseURL;
};

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 120000 // 120秒超时，因为LLM分析可能需要较长时间
});

api.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
);

// 默认导出，方便使用
export default api;



