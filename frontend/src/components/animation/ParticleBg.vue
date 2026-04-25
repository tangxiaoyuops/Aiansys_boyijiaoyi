<template>
  <canvas ref="canvasRef" class="particle-bg"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps<{
  color?: string;
  count?: number;
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationId: number | null = null;
let particles: Particle[] = [];

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
}

const createParticle = (width: number, height: number): Particle => ({
  x: Math.random() * width,
  y: Math.random() * height,
  size: Math.random() * 3 + 1,
  speedX: (Math.random() - 0.5) * 0.5,
  speedY: (Math.random() - 0.5) * 0.5,
  opacity: Math.random() * 0.5 + 0.3
});

const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  const color = props.color || '#4fc3f7';
  
  particles.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.globalAlpha = p.opacity;
    ctx.fill();
    
    // 更新位置
    p.x += p.speedX;
    p.y += p.speedY;
    
    // 边界检测
    if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
    if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
  });
  
  ctx.globalAlpha = 1;
  
  // 绘制连线
  particles.forEach((p1, i) => {
    particles.slice(i + 1).forEach(p2 => {
      const dx = p1.x - p2.x;
      const dy = p1.y - p2.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 100) {
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = color;
        ctx.globalAlpha = 0.1 * (1 - distance / 100);
        ctx.stroke();
      }
    });
  });
  
  animationId = requestAnimationFrame(draw);
};

const resize = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  
  // 重新创建粒子
  const count = props.count || 50;
  particles = [];
  for (let i = 0; i < count; i++) {
    particles.push(createParticle(canvas.width, canvas.height));
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
.particle-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}
</style>
