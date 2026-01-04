/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router';

console.log('开始加载路由配置...');

// 使用动态导入，避免组件加载失败导致整个应用崩溃
const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/stock',
  },
  {
    path: '/stock',
    name: 'stock',
    component: () => import('./views/ChatView.vue'),
    meta: { title: '股票分析' },
  },
  {
    path: '/futures',
    name: 'futures',
    component: () => import('./views/FuturesView.vue'),
    meta: { title: '期货分析' },
  },
  {
    path: '/ziwei',
    name: 'ziwei',
    component: () => import('./views/ZiweiView.vue'),
    meta: { title: '紫微斗数' },
  },
  {
    path: '/divination',
    name: 'divination',
    component: () => import('./views/DivinationView.vue'),
    meta: { title: '六爻卜卦' },
  },
  {
    path: '/bazi',
    name: 'bazi',
    component: () => import('./views/BaziView.vue'),
    meta: { title: '八字排盘' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  console.log('路由跳转:', from.path, '->', to.path);
  next();
});

router.onError((error) => {
  console.error('路由错误:', error);
});

console.log('路由配置加载完成');

export default router;

