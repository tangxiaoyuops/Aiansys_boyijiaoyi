<template>
  <div class="animation-player fullscreen" @click="onPlayerClick">
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
          :count="120"
        />
      </template>
    </div>
    
    <!-- 内容层 -->
    <div class="content-layer">
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
        <span>{{ isLastScene ? '点击返回' : '点击继续' }}</span>
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
      </div>
      
      <!-- 控制按钮 -->
      <div class="controls">
        <button class="ctrl-btn" @click="store.previousScene" :disabled="!store.canPrevious">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        
        <span class="scene-counter">
          {{ store.currentSceneIndex + 1 }} / {{ store.currentContent.scenes.length }}
        </span>
        
        <button class="ctrl-btn" @click="handleNext" :disabled="!store.canNext">
          <el-icon><ArrowRight /></el-icon>
        </button>
        
        <button class="close-btn-inline" @click="closePlayer">
          <el-icon><Close /></el-icon>
          <span>返回</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onUnmounted, watch } from 'vue';
import { useAnimationStore } from '@/stores/animation';
import { ArrowLeft, ArrowRight, Close } from '@element-plus/icons-vue';
import GradientBg from './GradientBg.vue';
import ParticleBg from './ParticleBg.vue';
import SnowBg from './SnowBg.vue';
import SceneRenderer from './SceneRenderer.vue';

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const store = useAnimationStore();

// 场景是否已准备好
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

// 是否是最后一个场景
const isLastScene = computed(() => {
  if (!store.currentContent) return false;
  return store.currentSceneIndex === store.currentContent.scenes.length - 1;
});

// 监听内容变化，重置状态
watch(() => store.currentContent?.id, () => {
  sceneReady.value = false;
  showClickHint.value = false;
});

// 场景完成处理
const onSceneComplete = () => {
  sceneReady.value = true;
  showClickHint.value = true;
};

// 点击播放器
const onPlayerClick = () => {
  if (!sceneReady.value) return;
  
  if (isLastScene.value) {
    // 最后一条，点击返回列表
    closePlayer();
  } else if (store.canNext) {
    // 切换到下一条
    handleNext();
  }
};

// 处理下一个场景
const handleNext = () => {
  sceneReady.value = false;
  showClickHint.value = false;
  store.nextScene();
};

// 关闭播放器
const closePlayer = () => {
  sceneReady.value = false;
  showClickHint.value = false;
  store.reset();
  emit('close');
};

onUnmounted(() => {
  sceneReady.value = false;
  showClickHint.value = false;
});
</script>

<style scoped>
.animation-player {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  overflow: hidden;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  cursor: pointer;
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

.scene-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 60px;
}

.empty-state {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #90caf9;
  font-size: 24px;
}

.click-hint {
  position: absolute;
  bottom: 140px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 32px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  color: #1565c0;
  font-size: 18px;
  font-weight: 500;
  animation: pulse 2s infinite;
  pointer-events: none;
  box-shadow: 0 4px 20px rgba(21, 101, 192, 0.2);
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.7;
    transform: translateX(-50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.05);
  }
}

.control-layer {
  position: relative;
  z-index: 2;
  padding: 24px 40px 40px;
  background: linear-gradient(transparent, rgba(255, 255, 255, 0.95));
  cursor: default;
}

.progress-bar {
  position: relative;
  height: 6px;
  background: rgba(21, 101, 192, 0.15);
  border-radius: 3px;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #64b5f6, #1976d2);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.ctrl-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  background: rgba(21, 101, 192, 0.1);
  color: #1565c0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 20px;
}

.ctrl-btn:hover:not(:disabled) {
  background: rgba(21, 101, 192, 0.2);
  transform: scale(1.1);
}

.ctrl-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.scene-counter {
  color: #1976d2;
  font-size: 18px;
  min-width: 80px;
  text-align: center;
  font-weight: 600;
}

.close-btn-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 30px;
  background: rgba(21, 101, 192, 0.1);
  color: #1565c0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
  font-weight: 500;
}

.close-btn-inline:hover {
  background: rgba(21, 101, 192, 0.2);
}

/* 场景过渡动画 */
.scene-transition-enter-active,
.scene-transition-leave-active {
  transition: all 0.5s ease;
}

.scene-transition-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.scene-transition-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
