<template>

  <div class="app-shell">

    <header class="app-header">

      <div class="logo">博弈交易法分析助手</div>

      <div class="sub">基于 FastAPI + LangGraph</div>

      <nav class="app-nav">
        <router-link to="/stock" class="nav-link">股票分析</router-link>
        <router-link to="/futures" class="nav-link">期货分析</router-link>
        <router-link to="/ziwei" class="nav-link">紫微斗数</router-link>
        <router-link to="/divination" class="nav-link">六爻卜卦</router-link>
        <router-link to="/bazi" class="nav-link">八字排盘</router-link>
        <router-link to="/huangdi" class="nav-link">黄帝内经</router-link>
        <router-link to="/feedback" class="nav-link">反馈中心</router-link>
      </nav>

    </header>

    <main class="app-main">
      <router-view v-slot="{ Component, route }">
        <Suspense>
          <component :is="Component" v-if="Component" :key="route.path" />
          <template #fallback>
            <div class="loading-container">
              <div class="loading-text">加载中...</div>
            </div>
          </template>
        </Suspense>
      </router-view>
    </main>

  </div>

</template>



<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
  console.log('App组件已挂载');
});
</script>



<style scoped>

.app-shell {

  height: 100vh;

  display: flex;

  flex-direction: column;

  /* 原来的纯深色背景改为稍微亮一点的灰蓝色，眼睛更舒服 */

  background: #111827;

  color: #e5e7eb;

  overflow: hidden;

}

.app-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  padding: 12px 20px;

  border-bottom: 1px solid #e5e7eb33;

  background: #f3f4f6;

  color: #111827;

  flex-shrink: 0;

}

.app-nav {

  display: flex;

  gap: 16px;

}

.nav-link {

  padding: 6px 12px;

  border-radius: 4px;

  text-decoration: none;

  color: #6b7280;

  transition: all 0.2s;

}

.nav-link:hover {

  background: #e5e7eb;

  color: #111827;

}

.nav-link.router-link-active {

  background: #3b82f6;

  color: white;

}

.logo {

  font-weight: 600;

  letter-spacing: 0.5px;

}

.sub {

  font-size: 13px;

  color: #6b7280;

}

.app-main {

  flex: 1;

  display: flex;

  flex-direction: column;

  overflow: hidden;

  min-height: 0;

}

.loading-container {

  display: flex;

  align-items: center;

  justify-content: center;

  height: 100%;

  color: #6b7280;

}

.loading-text {

  font-size: 16px;

}

</style>



