<template>
  <div ref="canvasContainer" class="taiji-background"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';

interface YaoData {
  symbol: string;
  description: string;
  yaoNumber: number;
  isYang: boolean;
  isDong: boolean;
}

interface Props {
  intensity?: number;
  isShaking?: boolean;
  shakeLevel?: number;
  yaoResults?: (YaoData | null)[];
}

const props = withDefaults(defineProps<Props>(), {
  intensity: 0.5,
  isShaking: false,
  shakeLevel: 0,
  yaoResults: () => Array(6).fill(null)
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
let baguaGroup: THREE.Group;
let hexagramGroup: THREE.Group;
let energyRings: THREE.Mesh[] = [];
let particles: THREE.Points;
let stars: THREE.Points;
let yaoLines: THREE.Group[] = [];

let targetSeparation = 0;
let currentSeparation = 0;
let energyPulse = 0;
let time = 0;

// 八卦数据
const BAGUA_DATA = [
  { name: '乾', lines: [1, 1, 1], nature: '阳', color: 0xffd700 },
  { name: '巽', lines: [1, 1, 0], nature: '阴', color: 0x4ecdc4 },
  { name: '坎', lines: [0, 1, 0], nature: '阴', color: 0x99ddff },
  { name: '艮', lines: [0, 0, 1], nature: '阳', color: 0x88ccee },
  { name: '坤', lines: [0, 0, 0], nature: '阴', color: 0x4ecdc4 },
  { name: '震', lines: [1, 0, 0], nature: '阳', color: 0xff8855 },
  { name: '离', lines: [1, 0, 1], nature: '阳', color: 0xff6b9d },
  { name: '兑', lines: [1, 1, 0], nature: '阴', color: 0xffaa00 },
];

// 创建鱼几何体
function createFishGeometry(radius: number): THREE.ShapeGeometry {
  const R = radius;
  const r = R / 2;
  const shape = new THREE.Shape();

  shape.moveTo(R, 0);
  shape.absarc(0, 0, R, 0, Math.PI / 2, false);
  shape.absarc(0, r, r, Math.PI / 2, -Math.PI / 2, true);
  shape.absarc(0, -r, r, Math.PI / 2, -Math.PI / 2, false);
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

  const eyeGeo = new THREE.CircleGeometry(R * 0.18, 32);
  const eye = new THREE.Mesh(eyeGeo, yinMat);
  eye.position.set(0, -r, 0.02);
  group.add(eye);

  return group;
}

// 创建阴鱼
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

  const eyeGeo = new THREE.CircleGeometry(R * 0.18, 32);
  const eye = new THREE.Mesh(eyeGeo, yangMat);
  eye.position.set(0, -r, 0.02);
  group.add(eye);

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

// 创建八卦标签
function createBaguaLabel(text: string, color: number): THREE.Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d')!;
  
  ctx.font = 'bold 72px Microsoft YaHei, sans-serif';
  ctx.fillStyle = '#' + color.toString(16).padStart(6, '0');
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = '#' + color.toString(16).padStart(6, '0');
  ctx.shadowBlur = 20;
  ctx.fillText(text, 64, 64);

  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ 
    map: texture, 
    transparent: true,
    blending: THREE.AdditiveBlending 
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(1.2, 1.2, 1);
  return sprite;
}

// 创建八卦
function createBagua(radius: number): THREE.Group {
  const group = new THREE.Group();
  const baguaRadius = radius * 2.2;

  BAGUA_DATA.forEach((data, index) => {
    const trigramGroup = new THREE.Group();
    const angle = (index / 8) * Math.PI * 2 - Math.PI / 2;
    
    // 创建三爻
    const lineHeight = 0.5;
    const lineGap = 0.25;
    
    data.lines.forEach((isYang, i) => {
      const lineMat = new THREE.MeshBasicMaterial({
        color: data.color,
        transparent: true,
        opacity: 0.8
      });
      
      if (isYang) {
        // 阳爻（实线）
        const lineGeo = new THREE.BoxGeometry(0.8, 0.1, 0.05);
        const line = new THREE.Mesh(lineGeo, lineMat);
        line.position.y = (1 - i) * lineGap;
        trigramGroup.add(line);
      } else {
        // 阴爻（断线）
        const halfGeo = new THREE.BoxGeometry(0.3, 0.1, 0.05);
        const left = new THREE.Mesh(halfGeo, lineMat);
        left.position.set(-0.25, (1 - i) * lineGap, 0);
        const right = new THREE.Mesh(halfGeo, lineMat);
        right.position.set(0.25, (1 - i) * lineGap, 0);
        trigramGroup.add(left, right);
      }
    });

    // 添加卦名标签
    const label = createBaguaLabel(data.name, data.color);
    label.position.y = -0.6;
    trigramGroup.add(label);

    trigramGroup.position.set(
      Math.cos(angle) * baguaRadius,
      Math.sin(angle) * baguaRadius,
      0
    );
    
    (trigramGroup as any).userData = { 
      baseAngle: angle, 
      baseRadius: baguaRadius,
      floatOffset: Math.random() * Math.PI * 2 
    };
    
    group.add(trigramGroup);
  });

  return group;
}

// 创建爻线（用于弹出动画）
function createYaoLine(isYang: boolean, index: number): THREE.Group {
  const group = new THREE.Group();
  
  const color = isYang ? 0xffd700 : 0x4ecdc4;
  const lineMat = new THREE.MeshBasicMaterial({
    color,
    transparent: true,
    opacity: 0.9
  });

  if (isYang) {
    const lineGeo = new THREE.BoxGeometry(4, 0.4, 0.1);
    const line = new THREE.Mesh(lineGeo, lineMat);
    group.add(line);
  } else {
    const halfGeo = new THREE.BoxGeometry(1.8, 0.4, 0.1);
    const left = new THREE.Mesh(halfGeo, lineMat);
    left.position.x = -1.1;
    const right = new THREE.Mesh(halfGeo, lineMat);
    right.position.x = 1.1;
    group.add(left, right);
  }

  // 初始位置在太极中心
  group.position.set(0, 0, 0);
  group.scale.set(0, 0, 0);
  
  (group as any).userData = {
    targetY: 3.5 - index * 1.2, // 从上到下排列
    targetScale: 1,
    currentScale: 0,
    index
  };

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
  const count = 100;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const velocities: { speed: number; theta: number; radius: number }[] = [];
  const palette = [[1, 0.85, 0], [0.3, 0.8, 0.77], [1, 0.42, 0.62]];

  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const rad = radius * (1.5 + Math.random() * 2);
    positions[i * 3] = Math.cos(theta) * rad;
    positions[i * 3 + 1] = Math.sin(theta) * rad;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 0.3;

    const c = palette[Math.floor(Math.random() * 3)];
    colors[i * 3] = c[0];
    colors[i * 3 + 1] = c[1];
    colors[i * 3 + 2] = c[2];
    velocities.push({ speed: 0.01 + Math.random() * 0.015, theta, radius: rad });
  }

  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const mat = new THREE.PointsMaterial({
    size: 0.15,
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
  const starCount = 600;
  const geo = new THREE.BufferGeometry();
  const positions = new Float32Array(starCount * 3);
  const colors = new Float32Array(starCount * 3);

  for (let i = 0; i < starCount; i++) {
    const r = 40 + Math.random() * 60;
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
    size: 0.2,
    vertexColors: true,
    transparent: true,
    opacity: 0.6
  });

  return new THREE.Points(geo, mat);
}

// 更新爻线动画
function updateYaoLines() {
  props.yaoResults.forEach((yao, index) => {
    if (yao && yaoLines[index]) {
      const line = yaoLines[index];
      const data = (line as any).userData;
      
      // 弹出动画
      if (data.currentScale < data.targetScale) {
        data.currentScale += 0.08;
        line.scale.setScalar(data.currentScale);
        line.position.y = data.targetY * data.currentScale;
      }
    }
  });
}

// 重置爻线
function resetYaoLines() {
  yaoLines.forEach(line => {
    if (line) {
      line.scale.set(0, 0, 0);
      line.position.set(0, 0, 0);
      (line as any).userData.currentScale = 0;
    }
  });
}

function triggerShakeAnimation(level: number) {
  targetSeparation = level * 0.6;
  energyPulse = level * 0.4;
}

function resetAnimation() {
  targetSeparation = 0;
  energyPulse = 0;
}

function clearYaoLines() {
  yaoLines.forEach(line => {
    if (line) {
      hexagramGroup.remove(line);
      line.geometry?.dispose();
      (line.material as THREE.Material)?.dispose();
    }
  });
  yaoLines = [];
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

// 监听爻结果变化
watch(() => props.yaoResults, (newResults) => {
  // 检查是否所有爻都被清空（重置）
  const allCleared = newResults.every(yao => yao === null);
  
  if (allCleared) {
    // 清除所有爻线
    yaoLines.forEach(line => {
      if (line) {
        hexagramGroup.remove(line);
        line.geometry?.dispose();
        (line.material as THREE.Material)?.dispose();
      }
    });
    yaoLines = [];
  } else {
    // 创建新的爻线
    newResults.forEach((yao, index) => {
      if (yao && !yaoLines[index]) {
        const line = createYaoLine(yao.isYang, index);
        yaoLines[index] = line;
        hexagramGroup.add(line);
      }
    });
  }
}, { deep: true });

onMounted(() => {
  if (!canvasContainer.value) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050510);

  camera = new THREE.PerspectiveCamera(
    60,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    300
  );
  camera.position.set(0, 2, 20);

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  });
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x050510, 1);
  canvasContainer.value.appendChild(renderer.domElement);

  // 太极图
  taijiGroup = createTaiji(2.5);
  scene.add(taijiGroup);

  // 八卦
  baguaGroup = createBagua(2.5);
  scene.add(baguaGroup);

  // 卦象容器
  hexagramGroup = new THREE.Group();
  scene.add(hexagramGroup);

  // 能量环
  energyRings = createEnergyRings(2.5);
  energyRings.forEach(ring => scene.add(ring));

  // 粒子
  particles = createParticles(2.5);
  scene.add(particles);

  // 星空
  stars = createStars();
  scene.add(stars);

  clock = new THREE.Clock();

  const animate = () => {
    animationId = requestAnimationFrame(animate);
    const delta = clock.getDelta();
    time += delta;

    const baseSpeed = 0.008 + props.intensity * 0.008;
    // 顺时针旋转（减去角度）
    taijiGroup.rotation.z -= baseSpeed;

    // 八卦顺时针旋转
    baguaGroup.rotation.z -= 0.003;

    // 八卦浮动效果
    baguaGroup.children.forEach((trigram) => {
      const data = (trigram as any).userData;
      const floatY = Math.sin(time * 1.5 + data.floatOffset) * 0.15;
      const breathScale = 1 + Math.sin(time * 2 + data.floatOffset) * 0.05;
      trigram.position.y = Math.sin(data.baseAngle) * data.baseRadius + floatY;
      trigram.scale.setScalar(breathScale);
    });

    // 阴阳鱼分离
    currentSeparation += (targetSeparation - currentSeparation) * 0.05;

    const yangAngle = Math.PI / 5;
    yangFish.position.x = Math.cos(yangAngle) * currentSeparation * 1.1;
    yangFish.position.y = Math.sin(yangAngle) * currentSeparation * 0.9;
    yangFish.rotation.z = currentSeparation * 0.12;

    yinFish.position.x = Math.cos(yangAngle + Math.PI) * currentSeparation * 1.1;
    yinFish.position.y = Math.sin(yangAngle + Math.PI) * currentSeparation * 0.9;
    yinFish.rotation.z = Math.PI - currentSeparation * 0.12;

    // 能量环顺时针旋转
    energyRings.forEach((ring, i) => {
      ring.rotation.z -= 0.015 * (i % 2 === 0 ? 1 : -1);
      const baseOpacity = 0.4 - i * 0.08;
      const pulse = Math.sin(time * 2 + i) * (0.1 + energyPulse);
      (ring.material as THREE.MeshBasicMaterial).opacity = baseOpacity + pulse;
    });

    // 粒子
    const pos = particles.geometry.attributes.position.array as Float32Array;
    const velocities = (particles.userData as any).velocities;
    velocities.forEach((v: { speed: number; theta: number; radius: number }, i: number) => {
      v.theta += v.speed * (1 + energyPulse);
      pos[i * 3] = v.radius * Math.cos(v.theta);
      pos[i * 3 + 1] = v.radius * Math.sin(v.theta);
    });
    particles.geometry.attributes.position.needsUpdate = true;

    // 星空顺时针旋转
    stars.rotation.y -= 0.0002;
    stars.rotation.x -= 0.0001;

    // 更新爻线动画
    updateYaoLines();

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
