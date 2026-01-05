import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE || 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // 如果是HTTPS但证书有问题，设置为false
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('代理错误:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('代理请求:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('代理响应:', proxyRes.statusCode, req.url);
          });
        },
      }
    }
  }
});



