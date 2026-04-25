<template>
  <div class="animation-view">
    <!-- 全屏播放器模式 -->
    <template v-if="store.currentContent">
      <AnimationPlayer @close="closePlayer" :fullscreen="true" />
    </template>
    
    <!-- 选择内容模式 -->
    <template v-else>
      <div class="page-header">
        <h1 class="page-title">思维日志</h1>
        <p class="page-subtitle">活得轻松 · 缓步前行</p>
      </div>
      
      <!-- 内容列表 -->
      <div class="content-section">
        <div class="content-grid">
          <div 
            v-for="item in filteredContent" 
            :key="item.id" 
            class="content-card"
            @click="playContent(item)"
          >
            <div class="card-thumbnail" :style="getThumbnailStyle(item)">
              <div class="play-overlay">
                <el-icon class="play-icon"><VideoPlay /></el-icon>
              </div>
            </div>
            <div class="card-info">
              <h4 class="card-title">{{ item.title }}</h4>
              <div class="card-meta">
                <span class="type-tag">{{ ContentTypeLabels[item.type] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAnimationStore } from '@/stores/animation';
import { ContentType, ContentTypeLabels, type AnimationContent } from '@/types/animation';
import { VideoPlay } from '@element-plus/icons-vue';
import AnimationPlayer from '@/components/animation/AnimationPlayer.vue';

const store = useAnimationStore();

// 过滤后的内容
const filteredContent = computed(() => store.filteredContent);

// 获取缩略图样式
const getThumbnailStyle = (item: AnimationContent) => {
  const colors = [
    ['#a8e6cf', '#88d8b0'],
    ['#dcedc1', '#c5e1a5'],
    ['#ffd3b6', '#ffaaa5'],
    ['#d4f0f0', '#a8d8ea'],
    ['#fff1c1', '#ffeaa7'],
    ['#e8f5e9', '#c8e6c9']
  ];
  const colorPair = colors[Math.abs(item.id.charCodeAt(0)) % colors.length];
  return {
    background: `linear-gradient(135deg, ${colorPair[0]}, ${colorPair[1]})`
  };
};

// 播放内容
const playContent = (item: AnimationContent) => {
  store.loadContent(item.id);
  store.play();
};

// 关闭播放器
const closePlayer = () => {
  store.reset();
};

onMounted(() => {
  store.init();
});
</script>

<style scoped>
.animation-view {
  min-height: calc(100vh - 60px);
  background: linear-gradient(180deg, #f8fdf8 0%, #e8f5e9 100%);
}

.page-header {
  text-align: center;
  padding: 40px 20px 20px;
}

.page-title {
  margin: 0;
  font-size: 36px;
  color: #2e7d32;
  font-weight: 600;
  letter-spacing: 2px;
}

.page-subtitle {
  margin: 10px 0 0;
  font-size: 15px;
  color: #66bb6a;
}

.content-section {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.content-card {
  position: relative;
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(46, 125, 50, 0.1);
}

.content-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 35px rgba(46, 125, 50, 0.2);
}

.card-thumbnail {
  height: 150px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.content-card:hover .play-overlay {
  opacity: 1;
}

.play-icon {
  font-size: 56px;
  color: #2e7d32;
}

.card-info {
  padding: 20px;
}

.card-title {
  margin: 0;
  font-size: 18px;
  color: #1b5e20;
  font-weight: 600;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.type-tag {
  font-size: 12px;
  padding: 4px 12px;
  background: linear-gradient(135deg, #a8e6cf, #88d8b0);
  color: #1b5e20;
  border-radius: 20px;
  font-weight: 500;
}
</style>
