<template>
  <div 
    class="scene-container" 
    :class="[animationClass]"
    :style="containerStyle"
  >
    <!-- 标题类型 -->
    <template v-if="scene.type === 'title'">
      <h1 class="scene-title" :style="textStyle">
        <TypeWriter 
          v-if="scene.animation === 'typewriter'" 
          :text="textContent" 
          :speed="80"
          @complete="onComplete"
        />
        <span v-else>{{ textContent }}</span>
      </h1>
    </template>
    
    <!-- 文本类型 -->
    <template v-else-if="scene.type === 'text'">
      <p class="scene-text" :style="textStyle">
        <TypeWriter 
          v-if="scene.animation === 'typewriter'" 
          :text="textContent" 
          :speed="80"
          @complete="onComplete"
        />
        <span v-else>{{ textContent }}</span>
      </p>
    </template>
    
    <!-- 引用类型 -->
    <template v-else-if="scene.type === 'quote'">
      <blockquote class="scene-quote" :style="textStyle">
        <span class="quote-mark">"</span>
        <TypeWriter 
          v-if="scene.animation === 'typewriter'" 
          :text="textContent" 
          :speed="50"
          @complete="onComplete"
        />
        <span v-else>{{ textContent }}</span>
        <span class="quote-mark">"</span>
      </blockquote>
    </template>
    
    <!-- 列表类型 -->
    <template v-else-if="scene.type === 'list'">
      <ul class="scene-list" :style="textStyle">
        <li 
          v-for="(item, index) in listContent" 
          :key="index"
          :style="{ animationDelay: `${(scene.delay || 400) * index}ms` }"
          class="list-item"
        >
          {{ item }}
        </li>
      </ul>
    </template>
    
    <!-- 卡片类型 -->
    <template v-else-if="scene.type === 'card'">
      <div class="scene-card" :style="cardStyle">
        <p :style="textStyle">{{ textContent }}</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import type { Scene, SceneStyle } from '@/types/animation';
import TypeWriter from './TypeWriter.vue';

const props = defineProps<{
  scene: Scene;
}>();

const emit = defineEmits<{
  (e: 'complete'): void;
}>();

const isVisible = ref(false);
const animationComplete = ref(false);

// 获取文本内容
const textContent = computed(() => {
  if (typeof props.scene.content === 'string') {
    return props.scene.content;
  }
  return '';
});

// 获取列表内容
const listContent = computed(() => {
  if (Array.isArray(props.scene.content)) {
    return props.scene.content;
  }
  return [];
});

// 文本样式 - 全屏大字体
const textStyle = computed<Partial<SceneStyle>>(() => ({
  fontSize: props.scene.style?.fontSize || '36px',
  color: props.scene.style?.color || '#0d47a1',
  textAlign: props.scene.style?.textAlign || 'center',
  fontWeight: props.scene.style?.fontWeight || '400'
}));

// 容器样式
const containerStyle = computed(() => ({
  paddingTop: props.scene.style?.paddingTop || '20px',
  paddingBottom: props.scene.style?.paddingBottom || '20px'
}));

// 卡片样式
const cardStyle = computed(() => ({
  background: props.scene.style?.background || 'rgba(255, 255, 255, 0.95)',
  borderRadius: '24px',
  padding: '48px',
  boxShadow: '0 8px 40px rgba(21, 101, 192, 0.15)'
}));

// 动画类名
const animationClass = computed(() => {
  if (!isVisible.value) return '';
  
  const animations: Record<string, string> = {
    fadeIn: 'animate-fade-in',
    slideUp: 'animate-slide-up',
    slideLeft: 'animate-slide-left',
    bounce: 'animate-bounce',
    flip: 'animate-flip',
    zoom: 'animate-zoom',
    typewriter: 'animate-fade-in'
  };
  
  return animations[props.scene.animation] || '';
});

const onComplete = () => {
  animationComplete.value = true;
  emit('complete');
};

onMounted(() => {
  setTimeout(() => {
    isVisible.value = true;
  }, props.scene.delay || 0);
  
  if (props.scene.animation !== 'typewriter') {
    setTimeout(() => {
      onComplete();
    }, props.scene.duration);
  }
});

watch(() => props.scene.id, () => {
  isVisible.value = false;
  animationComplete.value = false;
  setTimeout(() => {
    isVisible.value = true;
  }, props.scene.delay || 0);
});
</script>

<style scoped>
.scene-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 1100px;
  padding: 40px;
  box-sizing: border-box;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.scene-container.animate-fade-in {
  animation: fadeIn 0.8s ease forwards;
}

.scene-container.animate-slide-up {
  animation: slideUp 0.8s ease forwards;
}

.scene-container.animate-slide-left {
  animation: slideLeft 0.8s ease forwards;
}

.scene-container.animate-bounce {
  animation: bounce 0.8s ease forwards;
}

.scene-container.animate-flip {
  animation: flip 0.8s ease forwards;
}

.scene-container.animate-zoom {
  animation: zoom 0.8s ease forwards;
}

.scene-title {
  margin: 0;
  line-height: 1.4;
}

.scene-text {
  margin: 0;
  line-height: 2;
  max-width: 1000px;
}

.scene-quote {
  margin: 0;
  padding: 40px 60px;
  position: relative;
  max-width: 900px;
  line-height: 2.2;
}

.quote-mark {
  font-size: 1.4em;
  color: #64b5f6;
  margin: 0 10px;
}

.scene-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-width: 800px;
}

.list-item {
  margin: 20px 0;
  padding: 24px 36px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  border-left: 5px solid #64b5f6;
  opacity: 0;
  animation: listItemFade 0.5s ease forwards;
  box-shadow: 0 4px 20px rgba(21, 101, 192, 0.1);
  line-height: 1.8;
  font-size: 28px;
}

.scene-card {
  max-width: 700px;
  text-align: center;
}

/* 动画关键帧 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(60px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideLeft {
  from {
    opacity: 0;
    transform: translateX(60px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes bounce {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.95); }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes flip {
  0% {
    opacity: 0;
    transform: perspective(400px) rotateY(90deg);
  }
  100% {
    opacity: 1;
    transform: perspective(400px) rotateY(0);
  }
}

@keyframes zoom {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes listItemFade {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
