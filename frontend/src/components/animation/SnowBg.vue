<template>
  <canvas ref="canvasRef" class="snow-bg"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps<{
  color?: string;
  count?: number;
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationId: number | null = null;
let snowflakes: Snowflake[] = [];

interface Snowflake {
  x: number;
  y: number;
  radius: number;
  speed: number;
  opacity: number;
  drift: number;
  wobble: number;
  wobbleSpeed: number;
}

const createSnowflake = (width: number, height: number): Snowflake => ({
  x: Math.random() * width,
  y: Math.random() * height - height,
  radius: Math.random() * 3 + 2,
  speed: Math.random() * 1 + 0.5,
  opacity: Math.random() * 0.6 + 0.4,
  drift: (Math.random() - 0.5) * 0.5,
  wobble: Math.random() * Math.PI * 2,
  wobbleSpeed: Math.random() * 0.02 + 0.01
});

const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const color = props.color || '#ffffff';
  
  snowflakes.forEach(snow => {
    ctx.beginPath();
    ctx.arc(snow.x, snow.y, snow.radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.globalAlpha = snow.opacity;
    ctx.fill();
    
    // 添加光晕效果
    const gradient = ctx.createRadialGradient(
      snow.x, snow.y, 0,
      snow.x, snow.y, snow.radius * 2
    );
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.globalAlpha = snow.opacity * 0.3;
    ctx.beginPath();
    ctx.arc(snow.x, snow.y, snow.radius * 2, 0, Math.PI * 2);
    ctx.fill();
    
    // 更新位置
    snow.y += snow.speed;
    snow.x += Math.sin(snow.wobble) * 0.5 + snow.drift;
    snow.wobble += snow.wobbleSpeed;
    
    // 重置到顶部
    if (snow.y > canvas.height + 10) {
      snow.y = -10;
      snow.x = Math.random() * canvas.width;
    }
    
    // 水平边界
    if (snow.x > canvas.width + 10) {
      snow.x = -10;
    } else if (snow.x < -10) {
      snow.x = canvas.width + 10;
    }
  });
  
  ctx.globalAlpha = 1;
  animationId = requestAnimationFrame(draw);
};

const resize = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  
  // 初始化雪花
  const count = props.count || 80;
  snowflakes = [];
  for (let i = 0; i < count; i++) {
    const snow = createSnowflake(canvas.width, canvas.height);
    snow.y = Math.random() * canvas.height; // 初始分布在整个画面
    snowflakes.push(snow);
  }
};

onMounted(() => {
  resize();
  draw();
  window.addEventListener('resize', resize);
});

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId);
  }
  window.removeEventListener('resize', resize);
});
</script>

<style scoped>
.snow-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}
</style>
