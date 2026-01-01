<template>

  <div class="app-shell">

    <header class="app-header">

      <div class="logo">博弈交易法分析助手</div>

      <div class="sub">基于 FastAPI + LangGraph</div>

    </header>

    <main class="app-main">

      <ChatView />

    </main>

  </div>

</template>



<script setup lang="ts">

import ChatView from './views/ChatView.vue';

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

</style>



