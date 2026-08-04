<template>
  <div ref="canvasContainer" class="taiji-background"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';

interface Props {
  intensity?: number;
  isShaking?: boolean;
  shakeLevel?: number;
}

const props = withDefaults(defineProps<Props>(), {
  intensity: 0.5,
  isShaking: false,
  shakeLevel: 0
});

const emit = defineEmits<{
  (e: 'animation-ready'): void
}>();

const canvasContainer = ref<HTMLDivElement | null>(null);

let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let animationId: number;
let clock: THREE.Clock;

let taijiGroup: THREE.Group;
let yangFish: THREE.Group;
let yinFish: THREE.Group;
let energyRings: THREE.Mesh[] = [];
let particles: THREE.Points;
let stars: THREE.Points;

let targetSeparation = 0;
let currentSeparation = 0;
let energyPulse = 0;
let time = 0;

/**
 * 太极图原理：
 * 阳鱼和阴鱼的形状完全一样，只是颜色相反
 * 阴鱼旋转180度后就能和阳鱼完美咬合形成S曲线
 */

// 创建鱼几何体（阳鱼形状：上凸下凹）
function createFishGeometry(radius: number): THREE.ShapeGeometry {
  const R = radius;
  const r = R / 2;
  const shape = new THREE.Shape();

  // 起点：右侧中点 (R, 0)
  shape.moveTo(R, 0);

  // 1. 大圆右上弧到上方 (0, R)
  shape.absarc(0, 0, R, 0, Math.PI / 2, false);

  // 2. 上小圆左半弧（凸出到左边）
  shape.absarc(0, r, r, Math.PI / 2, -Math.PI / 2, true);

  // 3. 下小圆右半弧（凹陷到右边）
  shape.absarc(0, -r, r, Math.PI / 2, -Math.PI / 2, false);

  // 4. 大圆右下弧回到起点
  shape.absarc(0, 0, R, -Math.PI / 2, 0, false);

  return new THREE.ShapeGeometry(shape, 64);
}

// 创建阳鱼
function createYangFish(radius: number): THREE.Group {
  const group = new THREE.Group();
  const R = radius;
  const r = R / 2;

  const yangMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.92,
    side: THREE.DoubleSide
  });

  const yinMat = new THREE.MeshBasicMaterial({
    color: 0x111111,
    side: THREE.DoubleSide
  });

  const geo = createFishGeometry(R);
  const mesh = new THREE.Mesh(geo, yangMat);
  group.add(mesh);

  // 阴眼（黑点，在下小圆凸出的头部）- 改到下小圆位置
  const eyeGeo = new THREE.CircleGeometry(R * 0.18, 32);
  const eye = new THREE.Mesh(eyeGeo, yinMat);
  eye.position.set(0, -r, 0.02);
  group.add(eye);

  return group;
}

// 创建阴鱼（与阳鱼相同形状，旋转180度，颜色相反）
function createYinFish(radius: number): THREE.Group {
  const group = new THREE.Group();
  const R = radius;
  const r = R / 2;

  const yinMat = new THREE.MeshBasicMaterial({
    color: 0x111111,
    transparent: true,
    opacity: 0.92,
    side: THREE.DoubleSide
  });

  const yangMat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide
  });

  const geo = createFishGeometry(R);
  const mesh = new THREE.Mesh(geo, yinMat);
  group.add(mesh);

  // 阳眼（白点，在下小圆凸出的头部）- 改到下小圆位置，旋转180度后会到上小圆
  const eyeGeo = new THREE.CircleGeometry(R * 0.18, 32);
  const eye = new THREE.Mesh(eyeGeo, yangMat);
  eye.position.set(0, -r, 0.02);
  group.add(eye);

  // 旋转180度
  group.rotation.z = Math.PI;

  return group;
}

// 创建太极图
function createTaiji(radius: number): THREE.Group {
  const group = new THREE.Group();

  yangFish = createYangFish(radius);
  yinFish = createYinFish(radius);

  group.add(yangFish);
  group.add(yinFish);

  return group;
}

// 创建能量环
function createEnergyRings(radius: number): THREE.Mesh[] {
  const rings: THREE.Mesh[] = [];
  const colors = [0xffd700, 0x4ecdc4, 0xff6b9d, 0x88ccee];

  colors.forEach((color, i) => {
    const ringGeo = new THREE.TorusGeometry(radius * (1.3 + i * 0.25), 0.02, 8, 128);
    const ringMat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.4 - i * 0.08
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = Math.PI / 2;
    rings.push(ring);
  });

  return rings;
}

// 创建粒子
function createParticles(radius: number): THREE.Points {
  const count = 80;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const velocities: { speed: number; theta: number; radius: number }[] = [];
  const palette = [[1, 0.85, 0], [0.3, 0.8, 0.77], [1, 0.42, 0.62]];

  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const rad = radius * (1.5 + Math.random() * 1.5);
    positions[i * 3] = Math.cos(theta) * rad;
    positions[i * 3 + 1] = Math.sin(theta) * rad;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 0.2;

    const c = palette[Math.floor(Math.random() * 3)];
    colors[i * 3] = c[0];
    colors[i * 3 + 1] = c[1];
    colors[i * 3 + 2] = c[2];
    velocities.push({ speed: 0.008 + Math.random() * 0.012, theta, radius: rad });
  }

  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const mat = new THREE.PointsMaterial({
    size: 0.12,
    transparent: true,
    opacity: 0.8,
    vertexColors: true,
    blending: THREE.AdditiveBlending
  });

  const points = new THREE.Points(geo, mat);
  (points.userData as any).velocities = velocities;
  return points;
}

// 创建星空背景
function createStars(): THREE.Points {
  const starCount = 500;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(starCount * 3);
  const colors = new Float32Array(starCount * 3);

  for (let i = 0; i < starCount; i++) {
    const r = 30 + Math.random() * 50;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);

    const brightness = 0.3 + Math.random() * 0.7;
    colors[i * 3] = brightness;
    colors[i * 3 + 1] = brightness;
    colors[i * 3 + 2] = brightness + Math.random() * 0.2;
  }

  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const mat = new THREE.PointsMaterial({
    size: 0.15,
    vertexColors: true,
    transparent: true,
    opacity: 0.6
  });

  return new THREE.Points(geo, mat);
}

function triggerShakeAnimation(level: number) {
  targetSeparation = level * 0.5;
  energyPulse = level * 0.3;
}

function resetAnimation() {
  targetSeparation = 0;
  energyPulse = 0;
}

watch(() => props.isShaking, (newVal) => {
  if (newVal) {
    triggerShakeAnimation(props.shakeLevel || 3);
  } else {
    resetAnimation();
  }
});

watch(() => props.shakeLevel, (newVal) => {
  if (props.isShaking) {
    triggerShakeAnimation(newVal);
  }
});

onMounted(() => {
  if (!canvasContainer.value) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050510);

  camera = new THREE.PerspectiveCamera(
    60,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    200
  );
  camera.position.set(0, 0, 15);

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  });
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x050510, 1);
  canvasContainer.value.appendChild(renderer.domElement);

  taijiGroup = createTaiji(2.5);
  scene.add(taijiGroup);

  energyRings = createEnergyRings(2.5);
  energyRings.forEach(ring => scene.add(ring));

  particles = createParticles(2.5);
  scene.add(particles);

  stars = createStars();
  scene.add(stars);

  clock = new THREE.Clock();

  const animate = () => {
    animationId = requestAnimationFrame(animate);
    const delta = clock.getDelta();
    time += delta;

    const baseSpeed = 0.008 + props.intensity * 0.008;
    taijiGroup.rotation.z += baseSpeed;

    currentSeparation += (targetSeparation - currentSeparation) * 0.05;

    // 阴阳鱼沿S曲线方向分离
    const yangAngle = Math.PI / 5;
    yangFish.position.x = Math.cos(yangAngle) * currentSeparation * 1.1;
    yangFish.position.y = Math.sin(yangAngle) * currentSeparation * 0.9;
    yangFish.rotation.z = currentSeparation * 0.12;

    yinFish.position.x = Math.cos(yangAngle + Math.PI) * currentSeparation * 1.1;
    yinFish.position.y = Math.sin(yangAngle + Math.PI) * currentSeparation * 0.9;
    // 阴鱼基础旋转是π，再加上分离动画的旋转
    yinFish.rotation.z = Math.PI - currentSeparation * 0.12;

    energyRings.forEach((ring, i) => {
      ring.rotation.z += 0.015 * (i % 2 === 0 ? 1 : -1);
      const baseOpacity = 0.4 - i * 0.08;
      const pulse = Math.sin(time * 2 + i) * (0.1 + energyPulse);
      (ring.material as THREE.MeshBasicMaterial).opacity = baseOpacity + pulse;
    });

    const pos = particles.geometry.attributes.position.array as Float32Array;
    const velocities = (particles.userData as any).velocities;
    velocities.forEach((v: { speed: number; theta: number; radius: number }, i: number) => {
      v.theta += v.speed * (1 + energyPulse);
      pos[i * 3] = v.radius * Math.cos(v.theta);
      pos[i * 3 + 1] = v.radius * Math.sin(v.theta);
    });
    particles.geometry.attributes.position.needsUpdate = true;

    stars.rotation.y += 0.0002;
    stars.rotation.x += 0.0001;

    renderer.render(scene, camera);
  };

  animate();
  emit('animation-ready');

  const handleResize = () => {
    if (!canvasContainer.value) return;
    camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  };
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId);
  }
  if (renderer) {
    renderer.dispose();
  }
});
</script>

<style scoped>
.taiji-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
</style>
