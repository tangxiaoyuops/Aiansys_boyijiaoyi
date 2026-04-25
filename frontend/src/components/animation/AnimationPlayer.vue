<template>
  <div class="animation-player" :class="{ fullscreen: store.isFullscreen }" @click="onPlayerClick">
    <!-- 背景层 -->
    <div class="background-layer">
      <GradientBg 
        v-if="backgroundType === 'gradient'" 
        :config="backgroundConfig" 
      />
      <ParticleBg 
        v-else-if="backgroundType === 'particle'" 
        :color="particleColor"
      />
      <template v-else-if="backgroundType === 'snow'">
        <GradientBg :config="backgroundConfig" />
        <SnowBg 
          :color="snowColor"
          :count="100"
        />
      </template>
    </div>
    
    <!-- 内容层 -->
    <div class="content-layer">
      <!-- 标题栏 -->
      <div class="player-header" v-if="store.currentContent">
        <h2 class="content-title">{{ store.currentContent.title }}</h2>
      </div>
      
      <!-- 场景渲染区域 -->
      <div class="scene-area" v-if="store.currentScene">
        <Transition name="scene-transition" mode="out-in">
          <SceneRenderer 
            :key="store.currentScene.id"
            :scene="store.currentScene" 
            @complete="onSceneComplete"
          />
        </Transition>
      </div>
      
      <!-- 空状态 -->
      <div class="empty-state" v-else>
        <p>请选择要播放的内容</p>
      </div>
      
      <!-- 点击提示 -->
      <div class="click-hint" v-if="showClickHint">
        <span>点击任意位置继续</span>
      </div>
    </div>
    
    <!-- 控制层 -->
    <div class="control-layer" v-if="store.currentContent" @click.stop>
      <!-- 进度条 -->
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progressPercent + '%' }"
        ></div>
        <!-- 场景指示器 -->
        <div class="scene-indicators">
          <span 
            v-for="(scene, index) in store.currentContent.scenes" 
            :key="scene.id"
            class="indicator"
            :class="{ active: index === store.currentSceneIndex, completed: index < store.currentSceneIndex }"
            @click="store.goToScene(index)"
          ></span>
        </div>
      </div>
      
      <!-- 控制按钮 -->
      <div class="controls">
        <button class="ctrl-btn" @click="store.previousScene" :disabled="!store.canPrevious">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        
        <button class="ctrl-btn" @click="handlePlayPause">
          <el-icon v-if="store.playStatus === 'playing'"><VideoPause /></el-icon>
          <el-icon v-else><VideoPlay /></el-icon>
        </button>
        
        <button class="ctrl-btn" @click="handleNext" :disabled="!store.canNext">
          <el-icon><ArrowRight /></el-icon>
        </button>
        
        <span class="scene-counter">
          {{ store.currentSceneIndex + 1 }} / {{ store.currentContent.scenes.length }}
        </span>
        
        <button class="ctrl-btn" @click="store.toggleFullscreen">
          <el-icon v-if="store.isFullscreen"><CloseBold /></el-icon>
          <el-icon v-else><FullScreen /></el-icon>
        </button>
      </div>
    </div>
    
    <!-- 关闭按钮 (全屏模式) -->
    <button class="close-btn" v-if="store.isFullscreen" @click.stop="closePlayer">
      <el-icon><Close /></el-icon>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onUnmounted } from 'vue';
import { useAnimationStore } from '@/stores/animation';
import { ArrowLeft, ArrowRight, VideoPlay, VideoPause, FullScreen, Close, CloseBold } from '@element-plus/icons-vue';
import GradientBg from './GradientBg.vue';
import ParticleBg from './ParticleBg.vue';
import SnowBg from './SnowBg.vue';
import SceneRenderer from './SceneRenderer.vue';

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const store = useAnimationStore();

// 场景是否已准备好（可以点击切换）
const sceneReady = ref(false);
// 是否显示点击提示
const showClickHint = ref(false);

// 背景类型
const backgroundType = computed(() => {
  if (!store.currentContent?.background) return 'gradient';
  return store.currentContent.background.type;
});

// 背景配置
const backgroundConfig = computed(() => {
  if (!store.currentContent?.background) {
    return { colors: ['#e8f5e9', '#c8e6c9', '#a5d6a7'], animated: true };
  }
  const bg = store.currentContent.background;
  if (bg.type === 'gradient' && typeof bg.value !== 'string') {
    return bg.value;
  }
  return { colors: ['#e8f5e9', '#c8e6c9', '#a5d6a7'], animated: true };
});

// 粒子颜色
const particleColor = computed(() => {
  return '#66bb6a';
});

// 雪花颜色
const snowColor = computed(() => {
  return '#ffffff';
});

// 进度百分比
const progressPercent = computed(() => {
  if (!store.currentContent) return 0;
  return ((store.currentSceneIndex + 1) / store.currentContent.scenes.length) * 100;
});

// 场景完成处理 - 手动模式下只标记准备好
const onSceneComplete = () => {
  sceneReady.value = true;
  if (store.canNext) {
    showClickHint.value = true;
  }
};

// 点击播放器切换到下一场景
const onPlayerClick = () => {
  if (sceneReady.value && store.canNext) {
    handleNext();
  }
};

// 处理下一个场景
const handleNext = () => {
  sceneReady.value = false;
  showClickHint.value = false;
  store.nextScene();
};

// 处理播放/暂停按钮
const handlePlayPause = () => {
  if (store.playStatus === 'playing') {
    store.pause();
  } else {
    store.play();
    sceneReady.value = false;
    showClickHint.value = false;
  }
};

// 关闭播放器
const closePlayer = () => {
  store.toggleFullscreen();
  emit('close');
};

onUnmounted(() => {
  sceneReady.value = false;
  showClickHint.value = false;
});
</script>

<style scoped>
.animation-player {
  position: relative;
  width: 100%;
  height: 480px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  box-shadow: 0 8px 32px rgba(46, 125, 50, 0.15);
  cursor: pointer;
}

.animation-player.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  border-radius: 0;
  z-index: 9999;
}

.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.content-layer {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.player-header {
  padding: 20px 30px;
  text-align: center;
}

.content-title {
  margin: 0;
  font-size: 26px;
  color: #1b5e20;
  font-weight: 600;
}

.scene-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.empty-state {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #81c784;
  font-size: 18px;
}

.click-hint {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 20px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  color: #ffffff;
  font-size: 14px;
  animation: pulse 2s infinite;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.control-layer {
  position: relative;
  z-index: 2;
  padding: 15px 20px;
  background: linear-gradient(transparent, rgba(255, 255, 255, 0.9));
  cursor: default;
}

.progress-bar {
  position: relative;
  height: 4px;
  background: rgba(46, 125, 50, 0.15);
  border-radius: 2px;
  margin-bottom: 15px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #66bb6a, #4caf50);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.scene-indicators {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(46, 125, 50, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: #4caf50;
  transform: scale(1.3);
}

.indicator.completed {
  background: #81c784;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.ctrl-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(46, 125, 50, 0.1);
  color: #2e7d32;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ctrl-btn:hover:not(:disabled) {
  background: rgba(46, 125, 50, 0.2);
}

.ctrl-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ctrl-btn.play-btn {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #66bb6a, #4caf50);
  color: #ffffff;
}

.ctrl-btn.play-btn:hover {
  background: linear-gradient(135deg, #4caf50, #388e3c);
}

.scene-counter {
  color: #66bb6a;
  font-size: 14px;
  min-width: 60px;
  text-align: center;
  font-weight: 500;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #2e7d32;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.close-btn:hover {
  background: #ffffff;
  transform: scale(1.1);
}

/* 场景过渡动画 */
.scene-transition-enter-active,
.scene-transition-leave-active {
  transition: all 0.5s ease;
}

.scene-transition-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.scene-transition-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
