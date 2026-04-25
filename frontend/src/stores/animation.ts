/**
 * 动画演示模块状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  AnimationContent, 
  ContentType, 
  PlayStatus,
  Scene 
} from '@/types/animation';
import { 
  allContent, 
  getContentByType, 
  getContentById, 
  searchContent 
} from '@/data/animationContent';

export const useAnimationStore = defineStore('animation', () => {
  // 当前播放内容
  const currentContent = ref<AnimationContent | null>(null);
  
  // 当前场景索引
  const currentSceneIndex = ref(0);
  
  // 播放状态
  const playStatus = ref<PlayStatus>('idle');
  
  // 是否全屏
  const isFullscreen = ref(false);
  
  // 搜索关键词
  const searchKeyword = ref('');
  
  // 选中的分类
  const selectedType = ref<ContentType | null>(null);
  
  // 历史记录
  const history = ref<string[]>([]);
  
  // 收藏列表
  const favorites = ref<string[]>([]);
  
  // 计算属性：当前场景
  const currentScene = computed<Scene | null>(() => {
    if (!currentContent.value) return null;
    return currentContent.value.scenes[currentSceneIndex.value] || null;
  });
  
  // 计算属性：是否可以上一个/下一个
  const canPrevious = computed(() => currentSceneIndex.value > 0);
  const canNext = computed(() => {
    if (!currentContent.value) return false;
    return currentSceneIndex.value < currentContent.value.scenes.length - 1;
  });
  
  // 计算属性：过滤后的内容列表
  const filteredContent = computed(() => {
    let result = allContent;
    
    // 按类型过滤
    if (selectedType.value) {
      result = getContentByType(selectedType.value);
    }
    
    // 按关键词搜索
    if (searchKeyword.value.trim()) {
      result = searchContent(searchKeyword.value.trim());
    }
    
    return result;
  });
  
  // 加载内容
  function loadContent(id: string) {
    const content = getContentById(id);
    if (content) {
      currentContent.value = content;
      currentSceneIndex.value = 0;
      playStatus.value = 'idle';
      
      // 添加到历史记录
      if (!history.value.includes(id)) {
        history.value.unshift(id);
        // 只保留最近20条
        if (history.value.length > 20) {
          history.value = history.value.slice(0, 20);
        }
      }
    }
  }
  
  // 播放
  function play() {
    playStatus.value = 'playing';
  }
  
  // 暂停
  function pause() {
    playStatus.value = 'paused';
  }
  
  // 切换播放/暂停
  function togglePlay() {
    if (playStatus.value === 'playing') {
      pause();
    } else {
      play();
    }
  }
  
  // 下一个场景
  function nextScene() {
    if (canNext.value) {
      currentSceneIndex.value++;
    }
  }
  
  // 上一个场景
  function previousScene() {
    if (canPrevious.value) {
      currentSceneIndex.value--;
    }
  }
  
  // 跳转到指定场景
  function goToScene(index: number) {
    if (currentContent.value && index >= 0 && index < currentContent.value.scenes.length) {
      currentSceneIndex.value = index;
    }
  }
  
  // 播放结束
  function end() {
    playStatus.value = 'ended';
  }
  
  // 切换全屏
  function toggleFullscreen() {
    isFullscreen.value = !isFullscreen.value;
  }
  
  // 设置分类
  function setType(type: ContentType | null) {
    selectedType.value = type;
  }
  
  // 设置搜索关键词
  function setSearchKeyword(keyword: string) {
    searchKeyword.value = keyword;
  }
  
  // 切换收藏
  function toggleFavorite(id: string) {
    const index = favorites.value.indexOf(id);
    if (index > -1) {
      favorites.value.splice(index, 1);
    } else {
      favorites.value.push(id);
    }
    // 保存到本地存储
    localStorage.setItem('animation_favorites', JSON.stringify(favorites.value));
  }
  
  // 检查是否收藏
  function isFavorite(id: string): boolean {
    return favorites.value.includes(id);
  }
  
  // 初始化：从本地存储加载收藏
  function init() {
    const savedFavorites = localStorage.getItem('animation_favorites');
    if (savedFavorites) {
      try {
        favorites.value = JSON.parse(savedFavorites);
      } catch {
        favorites.value = [];
      }
    }
  }
  
  // 重置播放状态
  function reset() {
    currentContent.value = null;
    currentSceneIndex.value = 0;
    playStatus.value = 'idle';
  }
  
  return {
    // 状态
    currentContent,
    currentSceneIndex,
    playStatus,
    isFullscreen,
    searchKeyword,
    selectedType,
    history,
    favorites,
    
    // 计算属性
    currentScene,
    canPrevious,
    canNext,
    filteredContent,
    
    // 方法
    loadContent,
    play,
    pause,
    togglePlay,
    nextScene,
    previousScene,
    goToScene,
    end,
    toggleFullscreen,
    setType,
    setSearchKeyword,
    toggleFavorite,
    isFavorite,
    init,
    reset
  };
});
