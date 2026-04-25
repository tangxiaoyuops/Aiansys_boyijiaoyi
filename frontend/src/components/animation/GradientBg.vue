<template>
  <div class="gradient-bg" :style="containerStyle">
    <div class="gradient-layer" :style="gradientStyle"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import type { GradientConfig } from '@/types/animation';

const props = defineProps<{
  config: GradientConfig;
}>();

const angle = ref(props.config.angle || 135);

const containerStyle = computed(() => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  overflow: 'hidden'
}));

const gradientStyle = computed(() => {
  const colors = props.config.colors;
  const gradientAngle = angle.value;
  
  if (props.config.animated) {
    return {
      background: `linear-gradient(${gradientAngle}deg, ${colors.join(', ')})`,
      backgroundSize: '400% 400%',
      animation: 'gradientMove 15s ease infinite'
    };
  }
  
  return {
    background: `linear-gradient(${gradientAngle}deg, ${colors.join(', ')})`
  };
});

onMounted(() => {
  if (props.config.animated) {
    // 动态改变角度实现更丰富的动画效果
    setInterval(() => {
      angle.value = (angle.value + 1) % 360;
    }, 100);
  }
});
</script>

<style scoped>
.gradient-bg {
  z-index: 0;
}

.gradient-layer {
  width: 100%;
  height: 100%;
  transition: background 0.5s ease;
}

@keyframes gradientMove {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
