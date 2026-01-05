import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        // 从环境变量获取，如果设置了HTTPS但后端是HTTP，自动转换为HTTP
        target: (() => {
          const envBase = process.env.VITE_API_BASE || 'http://localhost:8000';
          // 如果环境变量是HTTPS但后端实际是HTTP，转换为HTTP
          if (envBase.startsWith('https://')) {
            const httpBase = envBase.replace('https://', 'http://');
            console.log(`[Vite代理] 检测到HTTPS，转换为HTTP: ${envBase} -> ${httpBase}`);
            return httpBase;
          }
          return envBase;
        })(),
        changeOrigin: true,
        secure: false, // 允许自签名证书
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('[Vite代理错误]', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('[Vite代理请求]', req.method, req.url, '->', proxyReq.path);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('[Vite代理响应]', proxyRes.statusCode, req.url);
          });
        },
      }
    }
  }
});



