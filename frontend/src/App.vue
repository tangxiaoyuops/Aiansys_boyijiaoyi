<template>

  <div class="app-shell">

    <header class="app-header">

      <div class="logo">博弈交易法分析助手</div>

      <div class="sub">基于 FastAPI + LangGraph</div>

    </header>

    <main class="app-main">
      <nav class="app-nav">
        <router-link to="/stock" class="nav-link">股票分析</router-link>
        <router-link to="/futures" class="nav-link">期货分析</router-link>
      </nav>
      <router-view />
    </main>

  </div>

</template>



<script setup lang="ts">
// 使用路由，不再直接导入 ChatView
</script>



<style scoped>

.app-shell {

  min-height: 100vh;

  display: flex;

  flex-direction: column;

  /* 原来的纯深色背景改为稍微亮一点的灰蓝色，眼睛更舒服 */

  background: #111827;

  color: #e5e7eb;

}

.app-header {

  display: flex;

  justify-content: space-between;

  align-items: center;

  padding: 12px 20px;

  border-bottom: 1px solid #e5e7eb33;

  background: #f3f4f6;

  color: #111827;

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
}

.app-nav {
  display: flex;
  gap: 8px;
  padding: 8px 20px;
  border-bottom: 1px solid #e5e7eb33;
  background: #1f2937;
}

.nav-link {
  padding: 8px 16px;
  color: #9ca3af;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 14px;
}

.nav-link:hover {
  background: #374151;
  color: #e5e7eb;
}

.nav-link.router-link-active {
  background: #3b82f6;
  color: #ffffff;
}

</style>



