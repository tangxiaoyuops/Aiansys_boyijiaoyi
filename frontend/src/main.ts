import { createApp } from 'vue';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import './style.css';
import './responsive.css';
import App from './App.vue';
import router from './router';

console.log('开始初始化应用...');

try {
  const app = createApp(App);
  console.log('Vue应用创建成功');
  
  app.use(createPinia());
  console.log('Pinia注册成功');
  
  app.use(router);
  console.log('Router注册成功');
  
  app.use(ElementPlus);
  console.log('ElementPlus注册成功');
  
  app.mount('#app');
  console.log('应用挂载成功');
} catch (error) {
  console.error('应用初始化失败:', error);
  document.getElementById('app')!.innerHTML = `
    <div style="padding: 20px; color: red;">
      <h1>应用初始化失败</h1>
      <pre>${error}</pre>
    </div>
  `;
}



