/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router';
import ChatView from './views/ChatView.vue';
import FuturesView from './views/FuturesView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/stock',
  },
  {
    path: '/stock',
    name: 'stock',
    component: ChatView,
    meta: { title: '股票分析' },
  },
  {
    path: '/futures',
    name: 'futures',
    component: FuturesView,
    meta: { title: '期货分析' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

