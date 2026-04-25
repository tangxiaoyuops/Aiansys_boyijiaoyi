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
          :style="{ animationDelay: `${(scene.delay || 300) * index}ms` }"
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

// 文本样式 - 春日草木风格默认配色
const textStyle = computed<Partial<SceneStyle>>(() => ({
  fontSize: props.scene.style?.fontSize || '24px',
  color: props.scene.style?.color || '#1b5e20',
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
  background: props.scene.style?.background || 'rgba(255, 255, 255, 0.9)',
  borderRadius: '16px',
  padding: '24px',
  boxShadow: '0 4px 20px rgba(46, 125, 50, 0.1)'
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
  // 延迟显示实现入场动画
  setTimeout(() => {
    isVisible.value = true;
  }, props.scene.delay || 0);
  
  // 非打字机动画，自动触发完成
  if (props.scene.animation !== 'typewriter') {
    setTimeout(() => {
      onComplete();
    }, props.scene.duration);
  }
});

// 监听场景变化
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
  padding: 20px;
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
  line-height: 1.6;
  max-width: 800px;
}

.scene-quote {
  margin: 0;
  padding: 20px 40px;
  position: relative;
  max-width: 700px;
  line-height: 1.8;
}

.quote-mark {
  font-size: 1.5em;
  color: #66bb6a;
  margin: 0 4px;
}

.scene-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-width: 600px;
}

.list-item {
  margin: 12px 0;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border-left: 3px solid #66bb6a;
  opacity: 0;
  animation: listItemFade 0.5s ease forwards;
  box-shadow: 0 2px 10px rgba(46, 125, 50, 0.08);
}

.scene-card {
  max-width: 500px;
  text-align: center;
}

/* 动画关键帧 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideLeft {
  from {
    opacity: 0;
    transform: translateX(50px);
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
  50% {
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
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
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
