<template>
  <div class="solar-system-container">
    <div ref="canvasContainer" class="canvas-wrapper"></div>
    
    <!-- 控制面板 -->
    <div class="controls">
      <div class="speed-control">
        <label>运动速度</label>
        <input type="range" v-model="speedMultiplier" min="0" max="5" step="0.1" />
        <span>{{ speedMultiplier.toFixed(1) }}x</span>
      </div>
    </div>
    
    <!-- 行星信息 -->
    <div class="planet-info" v-if="selectedPlanet">
      <h2>{{ selectedPlanet.name }}</h2>
      <p>{{ selectedPlanet.desc }}</p>
    </div>
    
    <!-- 宇宙事件通知 -->
    <div class="event-notification" v-if="eventNotification">
      <span class="event-icon">🌌</span>
      <span class="event-text">{{ eventNotification }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const canvasContainer = ref<HTMLDivElement | null>(null);
const speedMultiplier = ref(1);
const selectedPlanet = ref<{ name: string; desc: string } | null>(null);
const eventNotification = ref('');

// 类型定义
interface PlanetData {
  name: string;
  radius: number;
  distance: number;
  speed: number;
  color: number;
  tilt: number;
  desc: string;
  hasMoon?: boolean;
  hasRing?: boolean;
  thinRing?: boolean;
  isGas?: boolean;
}

interface CosmicEvent {
  type: 'blackHole' | 'whiteHole' | 'explosion' | 'collision';
  life: number;
  [key: string]: any;
}

// 行星数据
const planetData: PlanetData[] = [
  { name: '水星', radius: 2, distance: 28, speed: 4.15, color: 0x8c8c8c, tilt: 7, desc: '最小的行星，离太阳最近' },
  { name: '金星', radius: 3.5, distance: 36, speed: 1.62, color: 0xffd700, tilt: 3.4, desc: '最亮的行星，被称为启明星' },
  { name: '地球', radius: 4, distance: 45, speed: 1, color: 0x4169e1, tilt: 0, desc: '我们的家园，唯一已知有生命的行星', hasMoon: true },
  { name: '火星', radius: 3, distance: 55, speed: 0.53, color: 0xff4500, tilt: 1.9, desc: '红色星球，人类探索的目标' },
  { name: '木星', radius: 12, distance: 85, speed: 0.084, color: 0xffa500, tilt: 1.3, desc: '最大的行星，有著名的大红斑', isGas: true },
  { name: '土星', radius: 10, distance: 115, speed: 0.034, color: 0xf0e68c, tilt: 2.5, desc: '拥有美丽的光环系统', hasRing: true },
  { name: '天王星', radius: 7, distance: 145, speed: 0.012, color: 0x40e0d0, tilt: 0.8, desc: '躺着自转的冰巨星', hasRing: true, thinRing: true },
  { name: '海王星', radius: 6.5, distance: 175, speed: 0.006, color: 0x4169e1, tilt: 1.8, desc: '最远的大行星，深蓝色' },
  { name: '冥王星', radius: 1.5, distance: 200, speed: 0.004, color: 0xdeb887, tilt: 17.2, desc: '矮行星，曾经是第9大行星' }
];

// Three.js 对象
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let animationId: number;
let solarSystemGroup: THREE.Group;
let sun: THREE.Mesh;
let corona: THREE.Mesh;
let planets: THREE.Mesh[] = [];
let planetTrails: THREE.Points[] = [];
let sunRays: THREE.Mesh[] = [];
let cosmicEvents: { blackHoles: THREE.Group[]; whiteHoles: THREE.Group[]; explosions: THREE.Group[]; collisions: THREE.Group[] } = {
  blackHoles: [],
  whiteHoles: [],
  explosions: [],
  collisions: []
};
let meteors: THREE.Group[] = [];
let comets: THREE.Group[] = [];
let meteorShower: THREE.Group;
let movingStars: THREE.Points;
let sphereStars: THREE.Points;
let galaxy: THREE.Points;
let nebula: THREE.Group;
let eventTimer: number;

// 创建太阳纹理
function createSunTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d')!;
  
  const gradient = ctx.createRadialGradient(256, 256, 0, 256, 256, 256);
  gradient.addColorStop(0, '#ffff00');
  gradient.addColorStop(0.5, '#ffa500');
  gradient.addColorStop(1, '#ff4500');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 512);
  
  for (let i = 0; i < 50; i++) {
    const x = Math.random() * 512;
    const y = Math.random() * 512;
    const radius = Math.random() * 20 + 5;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, ${100 + Math.random() * 100}, 0, ${Math.random() * 0.5})`;
    ctx.fill();
  }
  
  return new THREE.CanvasTexture(canvas);
}

// 创建行星纹理
function createPlanetTexture(planetName: string, baseColor: number): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d')!;
  
  const color = new THREE.Color(baseColor);
  ctx.fillStyle = `rgb(${Math.floor(color.r * 255)}, ${Math.floor(color.g * 255)}, ${Math.floor(color.b * 255)})`;
  ctx.fillRect(0, 0, 256, 256);
  
  if (planetName === '地球') {
    ctx.fillStyle = '#4169e1';
    ctx.fillRect(0, 0, 256, 256);
    ctx.fillStyle = '#228b22';
    for (let i = 0; i < 20; i++) {
      ctx.beginPath();
      ctx.ellipse(Math.random() * 256, Math.random() * 256, Math.random() * 40 + 10, Math.random() * 30 + 10, Math.random() * Math.PI, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    for (let i = 0; i < 30; i++) {
      ctx.beginPath();
      ctx.arc(Math.random() * 256, Math.random() * 256, Math.random() * 20 + 5, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (planetName === '木星') {
    const colors = ['#ffa500', '#ff8c00', '#ff4500', '#ffd700', '#ff6347'];
    for (let i = 0; i < 256; i += 20) {
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
      ctx.fillRect(0, i, 256, 20);
    }
    ctx.fillStyle = '#ff4500';
    ctx.beginPath();
    ctx.ellipse(180, 150, 30, 20, 0, 0, Math.PI * 2);
    ctx.fill();
  } else if (planetName === '火星') {
    ctx.fillStyle = '#ff4500';
    ctx.fillRect(0, 0, 256, 256);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 256, 30);
    ctx.fillRect(0, 226, 256, 30);
    ctx.fillStyle = '#8b0000';
    for (let i = 0; i < 15; i++) {
      ctx.beginPath();
      ctx.arc(Math.random() * 256, Math.random() * 256, Math.random() * 15 + 5, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (planetName === '金星') {
    const gradient = ctx.createLinearGradient(0, 0, 256, 256);
    gradient.addColorStop(0, '#ffd700');
    gradient.addColorStop(0.5, '#ffec8b');
    gradient.addColorStop(1, '#daa520');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 256, 256);
    ctx.fillStyle = 'rgba(255, 255, 200, 0.3)';
    for (let i = 0; i < 10; i++) {
      ctx.fillRect(0, i * 26, 256, 13);
    }
  } else if (planetName === '土星') {
    const colors = ['#f0e68c', '#daa520', '#ffd700', '#eee8aa'];
    for (let i = 0; i < 256; i += 25) {
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
      ctx.fillRect(0, i, 256, 25);
    }
  }
  
  return new THREE.CanvasTexture(canvas);
}

// 创建星空
function createSphereStars(): THREE.Points {
  const starCount = 8000;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(starCount * 3);
  const colors = new Float32Array(starCount * 3);
  
  for (let i = 0; i < starCount; i++) {
    const radius = 5000;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
    const brightness = 0.5 + Math.random() * 0.5;
    colors[i * 3] = brightness;
    colors[i * 3 + 1] = brightness;
    colors[i * 3 + 2] = brightness + Math.random() * 0.3;
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const material = new THREE.PointsMaterial({ size: 3, vertexColors: true, transparent: true, opacity: 0.9 });
  return new THREE.Points(geometry, material);
}

function createMovingStars(): THREE.Points {
  const count = 2000;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 10000;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 10000;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 10000;
    const brightness = 0.7 + Math.random() * 0.3;
    colors[i * 3] = brightness;
    colors[i * 3 + 1] = brightness;
    colors[i * 3 + 2] = brightness;
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const material = new THREE.PointsMaterial({ size: 2, vertexColors: true, transparent: true, opacity: 0.8 });
  return new THREE.Points(geometry, material);
}

function createGalaxy(): THREE.Points {
  const count = 6000;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2;
    const phi = (Math.random() - 0.5) * 0.4;
    const radius = 6000 + Math.random() * 3000;
    positions[i * 3] = radius * Math.cos(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * 300;
    positions[i * 3 + 2] = radius * Math.cos(phi) * Math.sin(theta);
    
    const colorChoice = Math.random();
    if (colorChoice < 0.4) {
      colors[i * 3] = 0.5 + Math.random() * 0.5;
      colors[i * 3 + 1] = 0.5 + Math.random() * 0.3;
      colors[i * 3 + 2] = 0.8 + Math.random() * 0.2;
    } else {
      colors[i * 3] = 0.9 + Math.random() * 0.1;
      colors[i * 3 + 1] = 0.9 + Math.random() * 0.1;
      colors[i * 3 + 2] = 0.9 + Math.random() * 0.1;
    }
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const material = new THREE.PointsMaterial({ size: 5, vertexColors: true, transparent: true, opacity: 0.8 });
  const galaxy = new THREE.Points(geometry, material);
  galaxy.rotation.x = Math.PI / 2;
  return galaxy;
}

function createNebula(): THREE.Group {
  const nebulaGroup = new THREE.Group();
  const nebulaColors = [0xff6b9d, 0x4ecdc4, 0x9b59b6, 0x3498db, 0xf39c12];
  
  nebulaColors.forEach((color) => {
    const particleCount = 300;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const center = { x: (Math.random() - 0.5) * 8000, y: (Math.random() - 0.5) * 3000, z: (Math.random() - 0.5) * 8000 };
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = center.x + (Math.random() - 0.5) * 2000;
      positions[i * 3 + 1] = center.y + (Math.random() - 0.5) * 1000;
      positions[i * 3 + 2] = center.z + (Math.random() - 0.5) * 2000;
    }
    
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({ color, size: 10, transparent: true, opacity: 0.25, blending: THREE.AdditiveBlending });
    nebulaGroup.add(new THREE.Points(geo, mat));
  });
  
  return nebulaGroup;
}

// 创建流星
function createMeteors(): THREE.Group[] {
  const meteors: THREE.Group[] = [];
  for (let i = 0; i < 30; i++) {
    const meteorGroup = new THREE.Group();
    const headGeo = new THREE.SphereGeometry(1.5, 8, 8);
    const headMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9 });
    const head = new THREE.Mesh(headGeo, headMat);
    meteorGroup.add(head);
    
    const tailGeo = new THREE.ConeGeometry(0.8, 20, 8);
    const tailMat = new THREE.MeshBasicMaterial({ color: 0x88ccff, transparent: true, opacity: 0.4 });
    const tail = new THREE.Mesh(tailGeo, tailMat);
    tail.position.x = -10;
    tail.rotation.z = Math.PI / 2;
    meteorGroup.add(tail);
    
    meteorGroup.position.set((Math.random() - 0.5) * 8000, (Math.random() - 0.5) * 6000, (Math.random() - 0.5) * 8000);
    meteorGroup.rotation.y = Math.random() * Math.PI * 2;
    meteorGroup.rotation.z = -Math.PI / 6 + (Math.random() - 0.5) * 0.5;
    (meteorGroup as any).userData = { speed: 30 + Math.random() * 20, life: Math.random() * 5000 };
    meteors.push(meteorGroup);
    scene.add(meteorGroup);
  }
  return meteors;
}

// 创建彗星
function createComets(): THREE.Group[] {
  const comets: THREE.Group[] = [];
  for (let i = 0; i < 5; i++) {
    const cometGroup = new THREE.Group();
    const coreGeo = new THREE.SphereGeometry(5, 16, 16);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0xffffcc, transparent: true, opacity: 0.8 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    cometGroup.add(core);
    
    const tailColors = [0x66aaff, 0x88ccff, 0xaaddff];
    tailColors.forEach((color, index) => {
      const tailGeo = new THREE.ConeGeometry(3 + index * 2, 100 + index * 50, 8);
      const tailMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.3 - index * 0.08 });
      const tail = new THREE.Mesh(tailGeo, tailMat);
      tail.position.x = -50 - index * 30;
      tail.rotation.z = Math.PI / 2;
      cometGroup.add(tail);
    });
    
    cometGroup.position.set((Math.random() - 0.5) * 10000, (Math.random() - 0.5) * 8000, (Math.random() - 0.5) * 10000);
    cometGroup.rotation.y = Math.random() * Math.PI * 2;
    cometGroup.rotation.z = -Math.PI / 8;
    (cometGroup as any).userData = { speed: 20 + Math.random() * 10, orbitSpeed: 0.001 + Math.random() * 0.002 };
    comets.push(cometGroup);
    scene.add(cometGroup);
  }
  return comets;
}

// 创建流星雨
function createMeteorShower(): THREE.Group {
  const showerGroup = new THREE.Group();
  for (let i = 0; i < 100; i++) {
    const particleGeo = new THREE.SphereGeometry(0.5 + Math.random() * 1, 4, 4);
    const particleMat = new THREE.MeshBasicMaterial({
      color: Math.random() > 0.5 ? 0xffffff : 0xaaddff,
      transparent: true,
      opacity: 0.7 + Math.random() * 0.3
    });
    const particle = new THREE.Mesh(particleGeo, particleMat);
    particle.position.set((Math.random() - 0.5) * 3000, (Math.random() - 0.5) * 3000, (Math.random() - 0.5) * 3000);
    (particle as any).userData = { speed: 10 + Math.random() * 15, offset: Math.random() * Math.PI * 2 };
    showerGroup.add(particle);
  }
  showerGroup.position.set(3000, 1000, 2000);
  showerGroup.rotation.z = -Math.PI / 4;
  scene.add(showerGroup);
  return showerGroup;
}

// 创建黑洞
function createBlackHole(): THREE.Group {
  const blackHoleGroup = new THREE.Group();
  const coreGeo = new THREE.SphereGeometry(40, 32, 32);
  const coreMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
  const core = new THREE.Mesh(coreGeo, coreMat);
  blackHoleGroup.add(core);
  
  const diskGeo = new THREE.RingGeometry(50, 100, 64);
  const diskMat = new THREE.MeshBasicMaterial({ color: 0x6600ff, transparent: true, opacity: 0.7, side: THREE.DoubleSide });
  const disk = new THREE.Mesh(diskGeo, diskMat);
  disk.rotation.x = Math.PI / 2;
  blackHoleGroup.add(disk);
  
  const outerDiskGeo = new THREE.RingGeometry(110, 150, 64);
  const outerDiskMat = new THREE.MeshBasicMaterial({ color: 0x9900ff, transparent: true, opacity: 0.4, side: THREE.DoubleSide });
  const outerDisk = new THREE.Mesh(outerDiskGeo, outerDiskMat);
  outerDisk.rotation.x = Math.PI / 2;
  blackHoleGroup.add(outerDisk);
  
  blackHoleGroup.position.set((Math.random() - 0.5) * 3000, (Math.random() - 0.5) * 2000, (Math.random() - 0.5) * 3000);
  (blackHoleGroup as any).userData = { type: 'blackHole', life: 15000 + Math.random() * 5000, rotationSpeed: 0.03 };
  
  return blackHoleGroup;
}

// 创建白洞
function createWhiteHole(): THREE.Group {
  const whiteHoleGroup = new THREE.Group();
  const coreGeo = new THREE.SphereGeometry(25, 32, 32);
  const coreMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 1 });
  const core = new THREE.Mesh(coreGeo, coreMat);
  whiteHoleGroup.add(core);
  
  const jetGeo = new THREE.ConeGeometry(20, 150, 32);
  const jetMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 });
  const jet = new THREE.Mesh(jetGeo, jetMat);
  jet.position.y = 75;
  whiteHoleGroup.add(jet);
  
  const jet2 = jet.clone();
  jet2.position.y = -75;
  jet2.rotation.x = Math.PI;
  whiteHoleGroup.add(jet2);
  
  const particles = new THREE.Group();
  for (let i = 0; i < 50; i++) {
    const particleGeo = new THREE.SphereGeometry(2, 4, 4);
    const particleMat = new THREE.MeshBasicMaterial({
      color: Math.random() > 0.5 ? 0xffffff : 0xaaddff,
      transparent: true,
      opacity: 0.8
    });
    const particle = new THREE.Mesh(particleGeo, particleMat);
    (particle as any).userData = { speed: 2 + Math.random() * 3, angle: Math.random() * Math.PI * 2, distance: 0 };
    particles.add(particle);
  }
  whiteHoleGroup.add(particles);
  
  whiteHoleGroup.position.set((Math.random() - 0.5) * 10000, (Math.random() - 0.5) * 6000, (Math.random() - 0.5) * 10000);
  (whiteHoleGroup as any).userData = { type: 'whiteHole', life: 8000 + Math.random() * 4000, particles };
  
  return whiteHoleGroup;
}

// 创建恒星爆炸
function createStarExplosion(): THREE.Group {
  const explosionGroup = new THREE.Group();
  const coreGeo = new THREE.SphereGeometry(8, 24, 24);
  const coreMat = new THREE.MeshBasicMaterial({ color: 0xffdd00, transparent: true, opacity: 0.9 });
  const core = new THREE.Mesh(coreGeo, coreMat);
  explosionGroup.add(core);
  
  const shockWave = new THREE.Group();
  const sizes = [12, 20, 28];
  const colors = [0xffcc00, 0xff8800, 0xff5500];
  const opacities = [0.6, 0.4, 0.2];
  
  for (let i = 0; i < 3; i++) {
    const waveGeo = new THREE.SphereGeometry(sizes[i], 20, 20);
    const waveMat = new THREE.MeshBasicMaterial({ color: colors[i], transparent: true, opacity: opacities[i], side: THREE.BackSide });
    const wave = new THREE.Mesh(waveGeo, waveMat);
    shockWave.add(wave);
  }
  explosionGroup.add(shockWave);
  
  const debris = new THREE.Group();
  for (let i = 0; i < 60; i++) {
    const size = 0.5 + Math.random() * 1.5;
    const debrisGeo = new THREE.SphereGeometry(size, 4, 4);
    const debrisMat = new THREE.MeshBasicMaterial({
      color: Math.random() > 0.4 ? 0xffaa00 : Math.random() > 0.5 ? 0xffcc00 : 0xff6600,
      transparent: true,
      opacity: 0.85
    });
    const piece = new THREE.Mesh(debrisGeo, debrisMat);
    (piece as any).userData = { velocity: new THREE.Vector3((Math.random() - 0.5) * 1.2, (Math.random() - 0.5) * 1.2, (Math.random() - 0.5) * 1.2) };
    debris.add(piece);
  }
  explosionGroup.add(debris);
  
  explosionGroup.position.set((Math.random() - 0.5) * 2500, (Math.random() - 0.5) * 1800, (Math.random() - 0.5) * 2500);
  (explosionGroup as any).userData = { type: 'explosion', life: 7000, shockWave, debris, maxScale: 50 };
  
  return explosionGroup;
}

// 显示事件通知
function showEventNotification(eventType: string) {
  const names: Record<string, string> = {
    blackHole: '黑洞',
    whiteHole: '白洞',
    explosion: '恒星爆炸',
    collision: '行星相撞'
  };
  eventNotification.value = `检测到 ${names[eventType]}！`;
  setTimeout(() => { eventNotification.value = ''; }, 2000);
}

// 生成宇宙事件
function spawnCosmicEvent() {
  const eventTypes = ['blackHole', 'whiteHole', 'explosion'] as const;
  const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
  
  let event: THREE.Group;
  switch (eventType) {
    case 'blackHole':
      event = createBlackHole();
      cosmicEvents.blackHoles.push(event);
      break;
    case 'whiteHole':
      event = createWhiteHole();
      cosmicEvents.whiteHoles.push(event);
      break;
    case 'explosion':
      event = createStarExplosion();
      cosmicEvents.explosions.push(event);
      break;
  }
  
  scene.add(event);
  showEventNotification(eventType);
  
  setTimeout(() => {
    scene.remove(event);
    const index = cosmicEvents[eventType + 's' as keyof typeof cosmicEvents]?.indexOf(event);
    if (index && index > -1) {
      (cosmicEvents[eventType + 's' as keyof typeof cosmicEvents] as THREE.Group[]).splice(index, 1);
    }
  }, (event as any).userData.life);
}

onMounted(() => {
  if (!canvasContainer.value) return;
  
  // 场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000005);
  
  // 相机
  camera = new THREE.PerspectiveCamera(60, canvasContainer.value.clientWidth / canvasContainer.value.clientHeight, 0.1, 50000);
  camera.position.set(0, 150, 300);
  
  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  canvasContainer.value.appendChild(renderer.domElement);
  
  // 控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 50;
  controls.maxDistance = 2000;
  
  // 太阳系组
  solarSystemGroup = new THREE.Group();
  scene.add(solarSystemGroup);
  
  // 太阳
  const sunGeometry = new THREE.SphereGeometry(20, 64, 64);
  const sunTexture = createSunTexture();
  const sunMaterial = new THREE.MeshBasicMaterial({ map: sunTexture });
  sun = new THREE.Mesh(sunGeometry, sunMaterial);
  solarSystemGroup.add(sun);
  
  // 太阳日冕
  const coronaGeo = new THREE.SphereGeometry(25, 32, 32);
  const coronaMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0.3, side: THREE.BackSide });
  corona = new THREE.Mesh(coronaGeo, coronaMat);
  solarSystemGroup.add(corona);
  
  // 太阳光芒
  for (let i = 0; i < 12; i++) {
    const rayGeo = new THREE.ConeGeometry(2, 15, 4);
    const rayMat = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.2 });
    const ray = new THREE.Mesh(rayGeo, rayMat);
    ray.rotation.x = Math.PI / 2;
    ray.rotation.z = (i / 12) * Math.PI * 2;
    sunRays.push(ray);
    solarSystemGroup.add(ray);
  }
  
  // 光源
  const sunLight = new THREE.PointLight(0xffffff, 2, 500);
  solarSystemGroup.add(sunLight);
  const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
  scene.add(ambientLight);
  
  // 创建行星
  planetData.forEach((data, index) => {
    const geometry = new THREE.SphereGeometry(data.radius, 32, 32);
    const texture = createPlanetTexture(data.name, data.color);
    const material = new THREE.MeshStandardMaterial({ map: texture, metalness: 0.2, roughness: 0.8 });
    const planet = new THREE.Mesh(geometry, material);
    
    const angle = (index / planetData.length) * Math.PI * 2;
    planet.position.x = Math.cos(angle) * data.distance;
    planet.position.z = Math.sin(angle) * data.distance;
    (planet as any).userData = {
      name: data.name,
      distance: data.distance,
      speed: data.speed,
      angle,
      tilt: data.tilt * Math.PI / 180,
      desc: data.desc
    };
    
    solarSystemGroup.add(planet);
    planets.push(planet);
    
    // 轨迹拖尾
    const trailLength = 30;
    const trailGeometry = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(trailLength * 3);
    const trailColors = new Float32Array(trailLength * 3);
    
    for (let i = 0; i < trailLength; i++) {
      trailPositions[i * 3] = planet.position.x;
      trailPositions[i * 3 + 1] = planet.position.y;
      trailPositions[i * 3 + 2] = planet.position.z;
      const alpha = 1 - (i / trailLength);
      const color = new THREE.Color(data.color);
      trailColors[i * 3] = color.r * alpha;
      trailColors[i * 3 + 1] = color.g * alpha;
      trailColors[i * 3 + 2] = color.b * alpha;
    }
    
    trailGeometry.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
    trailGeometry.setAttribute('color', new THREE.BufferAttribute(trailColors, 3));
    const trailMaterial = new THREE.PointsMaterial({ size: data.radius * 0.5, vertexColors: true, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending });
    const trail = new THREE.Points(trailGeometry, trailMaterial);
    solarSystemGroup.add(trail);
    planetTrails.push(trail);
    
    // 月球
    if (data.hasMoon) {
      const moonGeo = new THREE.SphereGeometry(1, 16, 16);
      const moonTexture = createPlanetTexture('月球', 0xaaaaaa);
      const moonMat = new THREE.MeshStandardMaterial({ map: moonTexture, metalness: 0.1, roughness: 0.9 });
      const moon = new THREE.Mesh(moonGeo, moonMat);
      (moon as any).userData = { angle: 0, distance: 8, speed: 2 };
      planet.add(moon);
      (planet as any).userData.moon = moon;
    }
    
    // 光环
    if (data.hasRing) {
      const innerRadius = data.thinRing ? data.radius * 1.8 : data.radius * 1.4;
      const outerRadius = data.thinRing ? data.radius * 2.0 : data.radius * 2.2;
      const ringGeo = new THREE.RingGeometry(innerRadius, outerRadius, 64);
      const ringMat = new THREE.MeshBasicMaterial({ color: data.thinRing ? 0x40e0d0 : 0xf0e68c, transparent: true, opacity: data.thinRing ? 0.4 : 0.6, side: THREE.DoubleSide });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      planet.add(ring);
    }
    
    // 轨道线
    const orbitGeo = new THREE.RingGeometry(data.distance - 0.3, data.distance + 0.3, 128);
    const orbitMat = new THREE.MeshBasicMaterial({ color: 0x666666, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
    const orbit = new THREE.Mesh(orbitGeo, orbitMat);
    orbit.rotation.x = Math.PI / 2;
    orbit.rotation.y = data.tilt * Math.PI / 180;
    solarSystemGroup.add(orbit);
  });
  
  // 星空背景
  sphereStars = createSphereStars();
  scene.add(sphereStars);
  movingStars = createMovingStars();
  scene.add(movingStars);
  galaxy = createGalaxy();
  scene.add(galaxy);
  nebula = createNebula();
  scene.add(nebula);
  
  // 流星彗星
  meteors = createMeteors();
  comets = createComets();
  meteorShower = createMeteorShower();
  
  // 初始事件
  setTimeout(() => spawnCosmicEvent(), 1000);
  setTimeout(() => spawnCosmicEvent(), 3000);
  setTimeout(() => spawnCosmicEvent(), 5000);
  
  // 定期生成事件
  eventTimer = window.setInterval(() => {
    if (Math.random() > 0.2) {
      spawnCosmicEvent();
    }
  }, 4000);
  
  // 点击检测
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  
  renderer.domElement.addEventListener('click', (event) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(planets);
    
    if (intersects.length > 0) {
      const planet = intersects[0].object;
      selectedPlanet.value = { name: (planet as any).userData.name, desc: (planet as any).userData.desc };
      setTimeout(() => { selectedPlanet.value = null; }, 3000);
    }
  });
  
  // 动画
  let time = 0;
  const animate = () => {
    animationId = requestAnimationFrame(animate);
    time += 0.016 * speedMultiplier.value;
    
    // 移动的星星
    const starPos = movingStars.geometry.attributes.position.array as Float32Array;
    for (let i = 0; i < starPos.length / 3; i++) {
      starPos[i * 3] -= 5 * speedMultiplier.value;
      if (starPos[i * 3] < -5000) {
        starPos[i * 3] = 5000;
        starPos[i * 3 + 1] = (Math.random() - 0.5) * 10000;
        starPos[i * 3 + 2] = (Math.random() - 0.5) * 10000;
      }
    }
    movingStars.geometry.attributes.position.needsUpdate = true;
    
    // 流星
    meteors.forEach((meteor) => {
      meteor.position.x -= (meteor as any).userData.speed * speedMultiplier.value;
      (meteor as any).userData.life -= speedMultiplier.value;
      if (meteor.position.x < -5000 || (meteor as any).userData.life <= 0) {
        meteor.position.set(5000 + Math.random() * 2000, (Math.random() - 0.5) * 6000, (Math.random() - 0.5) * 8000);
        (meteor as any).userData.life = 5000 + Math.random() * 3000;
      }
    });
    
    // 彗星
    comets.forEach((comet) => {
      comet.position.x -= (comet as any).userData.speed * speedMultiplier.value;
      comet.rotation.y += (comet as any).userData.orbitSpeed * speedMultiplier.value;
      if (comet.position.x < -8000) {
        comet.position.set(8000 + Math.random() * 3000, (Math.random() - 0.5) * 8000, (Math.random() - 0.5) * 10000);
      }
    });
    
    // 行星公转
    planets.forEach((planet, index) => {
      (planet as any).userData.angle += (planet as any).userData.speed * 0.02 * speedMultiplier.value;
      const x = Math.cos((planet as any).userData.angle) * (planet as any).userData.distance;
      const z = Math.sin((planet as any).userData.angle) * (planet as any).userData.distance;
      const y = z * Math.sin((planet as any).userData.tilt);
      const adjustedZ = z * Math.cos((planet as any).userData.tilt);
      
      planet.position.x = x;
      planet.position.y = y;
      planet.position.z = adjustedZ;
      planet.rotation.y += 0.01 * speedMultiplier.value;
      
      // 更新轨迹
      const trail = planetTrails[index];
      const positions = trail.geometry.attributes.position.array as Float32Array;
      for (let i = positions.length / 3 - 1; i > 0; i--) {
        positions[i * 3] = positions[(i - 1) * 3];
        positions[i * 3 + 1] = positions[(i - 1) * 3 + 1];
        positions[i * 3 + 2] = positions[(i - 1) * 3 + 2];
      }
      positions[0] = x;
      positions[1] = y;
      positions[2] = adjustedZ;
      trail.geometry.attributes.position.needsUpdate = true;
      
      // 月球
      if ((planet as any).userData.moon) {
        const moon = (planet as any).userData.moon;
        (moon as any).userData.angle += (moon as any).userData.speed * 0.05 * speedMultiplier.value;
        moon.position.x = Math.cos((moon as any).userData.angle) * (moon as any).userData.distance;
        moon.position.z = Math.sin((moon as any).userData.angle) * (moon as any).userData.distance;
      }
    });
    
    // 太阳动画
    sun.rotation.y += 0.002 * speedMultiplier.value;
    sunRays.forEach((ray, i) => {
      ray.rotation.z += 0.01 * speedMultiplier.value * (i % 2 === 0 ? 1 : -1);
    });
    const pulse = 1 + Math.sin(time * 3) * 0.1;
    corona.scale.setScalar(pulse);
    
    // 星空旋转
    sphereStars.rotation.y += 0.0001 * speedMultiplier.value;
    galaxy.rotation.z += 0.00005 * speedMultiplier.value;
    nebula.rotation.y += 0.0001 * speedMultiplier.value;
    
    // 宇宙事件更新
    cosmicEvents.blackHoles.forEach((blackHole) => {
      blackHole.rotation.y += (blackHole as any).userData.rotationSpeed * speedMultiplier.value;
      (blackHole.children[1] as any).rotation.z += 0.05 * speedMultiplier.value;
    });
    
    cosmicEvents.whiteHoles.forEach((whiteHole) => {
      const particles = (whiteHole as any).userData.particles;
      particles.children.forEach((particle: THREE.Mesh) => {
        (particle as any).userData.distance += (particle as any).userData.speed * speedMultiplier.value;
        particle.position.x = Math.cos((particle as any).userData.angle) * (particle as any).userData.distance;
        particle.position.z = Math.sin((particle as any).userData.angle) * (particle as any).userData.distance;
        particle.position.y = (Math.random() - 0.5) * (particle as any).userData.distance;
      });
    });
    
    cosmicEvents.explosions.forEach((explosion) => {
      const shockWave = (explosion as any).userData.shockWave;
      const scale = 1 + 0.01 * speedMultiplier.value;
      shockWave.scale.multiplyScalar(scale);
      if (shockWave.scale.x > 3) {
        shockWave.scale.setScalar(3);
      }
      const debris = (explosion as any).userData.debris;
      debris.children.forEach((piece: THREE.Mesh) => {
        piece.position.add((piece as any).userData.velocity.clone().multiplyScalar(speedMultiplier.value));
        (piece.material as any).opacity -= 0.0015 * speedMultiplier.value;
      });
    });
    
    controls.update();
    renderer.render(scene, camera);
  };
  
  animate();
  
  // 窗口调整
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
  if (eventTimer) {
    clearInterval(eventTimer);
  }
  if (renderer) {
    renderer.dispose();
  }
});
</script>

<style scoped>
.solar-system-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #000;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
}

.controls {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  padding: 15px 20px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.speed-control label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.speed-control input[type="range"] {
  width: 150px;
}

.speed-control span {
  font-size: 14px;
  color: #ffd700;
  min-width: 40px;
}

.planet-info {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: rgba(0, 0, 0, 0.7);
  padding: 15px 30px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.planet-info h2 {
  font-size: 20px;
  margin-bottom: 5px;
  color: #ffd700;
}

.planet-info p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.event-notification {
  position: fixed;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: rgba(0, 0, 0, 0.8);
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid rgba(78, 205, 196, 0.5);
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-icon {
  font-size: 20px;
}

.event-text {
  font-size: 14px;
  color: #4ecdc4;
}
</style>
