import axios from 'axios';

// 获取API基础URL
// 如果设置了VITE_API_BASE，使用它；否则在开发环境使用代理，生产环境使用相对路径
const getBaseURL = () => {
  const envBase = import.meta.env.VITE_API_BASE;
  
  // 开发环境：优先使用代理（通过vite.config.ts配置）
  if (import.meta.env.DEV) {
    if (!envBase) {
      // 没有设置环境变量，使用相对路径走Vite代理
      return '';
    }
    // 如果设置了环境变量，检查协议匹配
    if (envBase.startsWith('https://') && window.location.protocol === 'http:') {
      console.warn('[API] 检测到协议不匹配，将HTTPS改为HTTP:', envBase);
      return envBase.replace('https://', 'http://');
    }
    return envBase;
  }
  
  // 生产环境：使用环境变量或默认值
  if (envBase) {
    // 检查协议匹配
    if (envBase.startsWith('https://') && window.location.protocol === 'http:') {
      console.warn('[API] 检测到协议不匹配，将HTTPS改为HTTP:', envBase);
      return envBase.replace('https://', 'http://');
    }
    return envBase;
  }
  
  return 'http://localhost:8000';
};

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 120000, // 120秒超时，因为LLM分析可能需要较长时间
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('[API请求]', config.method?.toUpperCase(), config.url, config.baseURL);
    return config;
  },
  (error) => {
    console.error('[API请求错误]', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (res) => {
    console.log('[API响应]', res.status, res.config.url);
    return res;
  },
  (err) => {
    console.error('[API响应错误]', err.response?.status, err.config?.url, err.message);
    if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
      console.error('[API连接失败]', '无法连接到服务器，请检查：');
      console.error('1. 后端服务是否启动');
      console.error('2. API地址是否正确:', err.config?.baseURL);
      console.error('3. 网络连接是否正常');
      console.error('4. 防火墙是否阻止了连接');
    }
    return Promise.reject(err);
  }
);

// 默认导出，方便使用
export default api;



