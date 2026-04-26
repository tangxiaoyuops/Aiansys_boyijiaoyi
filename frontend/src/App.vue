<template>

  <div class="app-shell">

    <header class="app-header">
      <div class="header-left">
        <div class="logo">博弈交易法分析助手</div>
        <div class="sub hidden-mobile">基于 FastAPI + LangGraph</div>
      </div>

      <!-- 桌面端导航 -->
      <nav class="app-nav hidden-mobile">
        <router-link to="/stock" class="nav-link">股票分析</router-link>
        <router-link to="/futures" class="nav-link">期货分析</router-link>
        <router-link to="/panic-scan" class="nav-link">恐慌点扫描</router-link>
        <router-link to="/backtest" class="nav-link">量化回测</router-link>
        <router-link to="/commodity" class="nav-link">大宗商品</router-link>
        <router-link to="/bazi" class="nav-link">八字排盘</router-link>
        <router-link to="/ziwei" class="nav-link">紫微斗数</router-link>
        <router-link to="/divination" class="nav-link">六爻卜卦</router-link>
        <router-link to="/fengshui" class="nav-link">风水布局</router-link>
        <router-link to="/animation" class="nav-link">思维日志</router-link>
      </nav>

      <!-- 移动端菜单按钮 -->
      <button class="mobile-menu-btn hidden-desktop" @click="toggleMobileMenu" :class="{ active: showMobileMenu }">
        <span class="menu-icon"></span>
      </button>

    </header>

    <!-- 移动端侧边导航 -->
    <Teleport to="body">
      <div class="mobile-nav-overlay" :class="{ show: showMobileMenu }" @click="closeMobileMenu"></div>
      <nav class="mobile-nav" :class="{ show: showMobileMenu }">
        <div class="mobile-nav-header">
          <span class="mobile-nav-title">导航菜单</span>
          <button class="close-btn" @click="closeMobileMenu">×</button>
        </div>
        <div class="mobile-nav-content">
          <router-link to="/stock" class="mobile-nav-link" @click="closeMobileMenu">股票分析</router-link>
          <router-link to="/futures" class="mobile-nav-link" @click="closeMobileMenu">期货分析</router-link>
          <router-link to="/panic-scan" class="mobile-nav-link" @click="closeMobileMenu">恐慌点扫描</router-link>
          <router-link to="/backtest" class="mobile-nav-link" @click="closeMobileMenu">量化回测</router-link>
          <router-link to="/commodity" class="mobile-nav-link" @click="closeMobileMenu">大宗商品</router-link>
          <router-link to="/bazi" class="mobile-nav-link" @click="closeMobileMenu">八字排盘</router-link>
          <router-link to="/ziwei" class="mobile-nav-link" @click="closeMobileMenu">紫微斗数</router-link>
          <router-link to="/divination" class="mobile-nav-link" @click="closeMobileMenu">六爻卜卦</router-link>
          <router-link to="/fengshui" class="mobile-nav-link" @click="closeMobileMenu">风水布局</router-link>
          <router-link to="/animation" class="mobile-nav-link" @click="closeMobileMenu">思维日志</router-link>
        </div>
      </nav>
    </Teleport>

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
import { ref, onMounted, onUnmounted } from 'vue';

const showMobileMenu = ref(false);

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
  document.body.style.overflow = showMobileMenu.value ? 'hidden' : '';
};

const closeMobileMenu = () => {
  showMobileMenu.value = false;
  document.body.style.overflow = '';
};

onMounted(() => {
  console.log('App组件已挂载');
});

onUnmounted(() => {
  document.body.style.overflow = '';
});
</script>



<style scoped>

.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
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
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

/* 自定义滚动条样式 */
.app-main::-webkit-scrollbar {
  width: 12px;
}

.app-main::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 6px;
}

.app-main::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 6px;
  transition: background 0.3s;
}

.app-main::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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

/* ========== 移动端菜单按钮 ========== */
.mobile-menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.mobile-menu-btn:hover {
  background: #e5e7eb;
}

.menu-icon {
  position: relative;
  width: 22px;
  height: 2px;
  background: #374151;
  border-radius: 2px;
  transition: all 0.3s;
}

.menu-icon::before,
.menu-icon::after {
  content: '';
  position: absolute;
  left: 0;
  width: 22px;
  height: 2px;
  background: #374151;
  border-radius: 2px;
  transition: all 0.3s;
}

.menu-icon::before {
  top: -7px;
}

.menu-icon::after {
  top: 7px;
}

/* 汉堡菜单动画 */
.mobile-menu-btn.active .menu-icon {
  background: transparent;
}

.mobile-menu-btn.active .menu-icon::before {
  top: 0;
  transform: rotate(45deg);
}

.mobile-menu-btn.active .menu-icon::after {
  top: 0;
  transform: rotate(-45deg);
}

/* ========== 移动端侧边导航 ========== */
.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}

.mobile-nav-overlay.show {
  opacity: 1;
  visibility: visible;
}

.mobile-nav {
  position: fixed;
  top: 0;
  right: -280px;
  width: 280px;
  height: 100%;
  background: #ffffff;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.15);
  transition: right 0.3s ease-out;
}

.mobile-nav.show {
  right: 0;
}

.mobile-nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.mobile-nav-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.mobile-nav-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.mobile-nav-link {
  display: block;
  padding: 14px 20px;
  color: #374151;
  text-decoration: none;
  font-size: 15px;
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s;
}

.mobile-nav-link:hover {
  background: #f3f4f6;
}

.mobile-nav-link.router-link-active {
  background: #eff6ff;
  color: #3b82f6;
  font-weight: 500;
  border-left: 3px solid #3b82f6;
}

/* ========== 响应式适配 ========== */
@media (max-width: 767.98px) {
  .app-header {
    padding: 10px 12px;
  }

  .logo {
    font-size: 15px;
  }

  .app-main {
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .loading-text {
    font-size: 14px;
  }
}

@media (max-width: 375px) {
  .logo {
    font-size: 14px;
  }
}
</style>

