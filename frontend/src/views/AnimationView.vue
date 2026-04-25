<template>
  <div class="animation-view">
    <div class="page-header">
      <h1 class="page-title">思维日志</h1>
      <p class="page-subtitle">活得轻松 · 缓步前行</p>
    </div>
    
    <!-- 分类筛选 -->
    <div class="filter-bar">
      <el-radio-group v-model="selectedType" size="large" @change="onTypeChange">
        <el-radio-button :value="null">全部</el-radio-button>
        <el-radio-button 
          v-for="type in contentTypes" 
          :key="type.value" 
          :value="type.value"
        >
          {{ type.label }}
        </el-radio-button>
      </el-radio-group>
      
      <el-input 
        v-model="searchKeyword" 
        placeholder="搜索内容..." 
        class="search-input"
        clearable
        @input="onSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <!-- 播放器区域 -->
    <div class="player-section" v-if="store.currentContent">
      <AnimationPlayer @close="closePlayer" />
    </div>
    
    <!-- 内容列表 -->
    <div class="content-section">
      <h3 class="section-title">
        {{ selectedType ? ContentTypeLabels[selectedType] : '推荐内容' }}
        <span class="count">({{ filteredContent.length }})</span>
      </h3>
      
      <div class="content-grid" v-if="filteredContent.length > 0">
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
              <span class="duration">{{ item.duration }}秒</span>
            </div>
          </div>
          <button class="favorite-btn" @click.stop="toggleFavorite(item.id)">
            <el-icon :class="{ favorited: store.isFavorite(item.id) }">
              <Star v-if="!store.isFavorite(item.id)" />
              <StarFilled v-else />
            </el-icon>
          </button>
        </div>
      </div>
      
      <el-empty v-else description="暂无相关内容" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAnimationStore } from '@/stores/animation';
import { ContentType, ContentTypeLabels, type AnimationContent } from '@/types/animation';
import { Search, VideoPlay, Star, StarFilled } from '@element-plus/icons-vue';
import AnimationPlayer from '@/components/animation/AnimationPlayer.vue';

const store = useAnimationStore();

// 分类选项
const contentTypes = [
  { value: ContentType.READING, label: ContentTypeLabels[ContentType.READING] },
  { value: ContentType.THINKING, label: ContentTypeLabels[ContentType.THINKING] },
  { value: ContentType.KNOWLEDGE, label: ContentTypeLabels[ContentType.KNOWLEDGE] },
  { value: ContentType.WISDOM, label: ContentTypeLabels[ContentType.WISDOM] },
  { value: ContentType.DAILY, label: ContentTypeLabels[ContentType.DAILY] }
];

// 选中的分类
const selectedType = ref<ContentType | null>(null);

// 搜索关键词
const searchKeyword = ref('');

// 过滤后的内容
const filteredContent = computed(() => store.filteredContent);

// 分类变化
const onTypeChange = (type: ContentType | null) => {
  store.setType(type);
};

// 搜索
const onSearch = (keyword: string) => {
  store.setSearchKeyword(keyword);
};

// 获取缩略图样式 - 春日草木风格
const getThumbnailStyle = (item: AnimationContent) => {
  const colors = [
    ['#a8e6cf', '#88d8b0'],  // 嫩绿
    ['#dcedc1', '#c5e1a5'],  // 浅草绿
    ['#ffd3b6', '#ffaaa5'],  // 桃花粉
    ['#d4f0f0', '#a8d8ea'],  // 天空蓝
    ['#fff1c1', '#ffeaa7'],  // 暖阳黄
    ['#e8f5e9', '#c8e6c9']   // 薄荷绿
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

// 切换收藏
const toggleFavorite = (id: string) => {
  store.toggleFavorite(id);
};

onMounted(() => {
  store.init();
});
</script>

<style scoped>
.animation-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fdf8 0%, #e8f5e9 100%);
  min-height: calc(100vh - 60px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
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

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  gap: 20px;
  flex-wrap: wrap;
  padding: 15px 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(46, 125, 50, 0.08);
}

.search-input {
  width: 250px;
}

.player-section {
  margin-bottom: 30px;
}

.content-section {
  margin-top: 20px;
}

.section-title {
  margin: 0 0 20px;
  font-size: 18px;
  color: #388e3c;
  font-weight: 500;
  padding-left: 10px;
  border-left: 3px solid #66bb6a;
}

.section-title .count {
  font-size: 14px;
  color: #81c784;
  margin-left: 8px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
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
  height: 130px;
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
  font-size: 48px;
  color: #2e7d32;
}

.card-info {
  padding: 16px;
}

.card-title {
  margin: 0;
  font-size: 16px;
  color: #1b5e20;
  font-weight: 600;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.type-tag {
  font-size: 12px;
  padding: 4px 12px;
  background: linear-gradient(135deg, #a8e6cf, #88d8b0);
  color: #1b5e20;
  border-radius: 20px;
  font-weight: 500;
}

.duration {
  font-size: 12px;
  color: #81c784;
}

.favorite-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #81c784;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.favorite-btn:hover {
  background: #ffffff;
  transform: scale(1.1);
}

.favorite-btn .favorited {
  color: #ffc107;
}
</style>
