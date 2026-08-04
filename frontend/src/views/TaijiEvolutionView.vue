<template>
  <div class="taiji-container">
    <div ref="canvasContainer" class="canvas-wrapper"></div>
    
    <!-- 控制面板 -->
    <div class="controls">
      <div class="stage-info">
        <span class="stage-label">当前阶段：</span>
        <span id="current-stage" class="stage-name">{{ stageNames[stage] }}</span>
      </div>
      <div class="btn-group">
        <button id="playPauseBtn" class="ctrl-btn" @click="togglePlay">
          {{ isPlaying ? '暂停' : '播放' }}
        </button>
        <button id="nextBtn" class="ctrl-btn" @click="nextStage">下一步</button>
        <button id="resetBtn" class="ctrl-btn" @click="reset">重置</button>
      </div>
    </div>
    
    <!-- 节气详情弹窗 -->
    <div id="solar-term-modal" class="modal hidden" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeModal">×</button>
        <h3 id="modal-title"></h3>
        <div id="modal-body"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

// 24节气数据
const SOLAR_TERMS_DATA = [
  { name: '立春', season: '春', dateRange: '2月3-5日', meaning: '春季开始', climate: '气温回升，万物复苏', health: '养肝护阳，宜食辛甘' },
  { name: '雨水', season: '春', dateRange: '2月18-20日', meaning: '降雨开始', climate: '降水增多，草木萌动', health: '健脾祛湿，调和脾胃' },
  { name: '惊蛰', season: '春', dateRange: '3月5-7日', meaning: '春雷乍动', climate: '蛰虫惊醒，天气转暖', health: '养肝明目，疏肝理气' },
  { name: '春分', season: '春', dateRange: '3月20-22日', meaning: '昼夜平分', climate: '阳光直射赤道，昼夜等长', health: '阴阳平衡，调和营卫' },
  { name: '清明', season: '春', dateRange: '4月4-6日', meaning: '天清地明', climate: '气候温和，草木繁茂', health: '养肝舒筋，踏青运动' },
  { name: '谷雨', season: '春', dateRange: '4月19-21日', meaning: '雨生百谷', climate: '降水充沛，谷物生长', health: '健脾利湿，防春火' },
  { name: '立夏', season: '夏', dateRange: '5月5-7日', meaning: '夏季开始', climate: '气温升高，万物繁茂', health: '养心安神，清热消暑' },
  { name: '小满', season: '夏', dateRange: '5月20-22日', meaning: '麦粒饱满', climate: '夏熟作物籽粒饱满', health: '清热利湿，调养心脾' },
  { name: '芒种', season: '夏', dateRange: '6月5-7日', meaning: '有芒之谷', climate: '抢收抢种，气温升高', health: '防暑降温，清淡饮食' },
  { name: '夏至', season: '夏', dateRange: '6月21-22日', meaning: '日长至极', climate: '白昼最长，炎热盛夏', health: '养阳防暑，清心宁神' },
  { name: '小暑', season: '夏', dateRange: '7月6-8日', meaning: '天气炎热', climate: '气温升高，进入伏天', health: '清热解暑，养心安神' },
  { name: '大暑', season: '夏', dateRange: '7月22-24日', meaning: '酷热盛夏', climate: '最热时期，暴雨频繁', health: '防暑降温，冬病夏治' },
  { name: '立秋', season: '秋', dateRange: '8月7-9日', meaning: '秋季开始', climate: '暑去凉来，秋高气爽', health: '养肺润燥，滋阴清热' },
  { name: '处暑', season: '秋', dateRange: '8月22-24日', meaning: '暑气终止', climate: '炎热结束，气温下降', health: '润肺生津，防秋燥' },
  { name: '白露', season: '秋', dateRange: '9月7-9日', meaning: '露凝而白', climate: '天气转凉，晨露晶莹', health: '养肺润燥，早晚添衣' },
  { name: '秋分', season: '秋', dateRange: '9月22-24日', meaning: '昼夜平分', climate: '阳光直射赤道，昼夜等长', health: '阴阳平衡，润燥养肺' },
  { name: '寒露', season: '秋', dateRange: '10月8-9日', meaning: '露气寒冷', climate: '气温下降，露水凝结', health: '养阴防燥，润肺益胃' },
  { name: '霜降', season: '秋', dateRange: '10月23-24日', meaning: '初霜出现', climate: '天气渐冷，开始降霜', health: '防寒保暖，润燥养肺' },
  { name: '立冬', season: '冬', dateRange: '11月7-8日', meaning: '冬季开始', climate: '气温下降，万物收藏', health: '养肾防寒，早睡晚起' },
  { name: '小雪', season: '冬', dateRange: '11月22-23日', meaning: '开始降雪', climate: '气温骤降，雪花飘落', health: '温补肾阳，防寒保暖' },
  { name: '大雪', season: '冬', dateRange: '12月6-8日', meaning: '雪量增大', climate: '大雪纷飞，天寒地冻', health: '养阴潜阳，补肾固本' },
  { name: '冬至', season: '冬', dateRange: '12月21-23日', meaning: '日短至极', climate: '白昼最短，数九寒冬', health: '养阳藏精，进补时节' },
  { name: '小寒', season: '冬', dateRange: '1月5-7日', meaning: '天气寒冷', climate: '气温骤降，滴水成冰', health: '温阳补肾，防寒保暖' },
  { name: '大寒', season: '冬', dateRange: '1月20-21日', meaning: '严寒盛极', climate: '最冷时期，冰天雪地', health: '温补肾阳，养精蓄锐' }
];

const canvasContainer = ref<HTMLDivElement | null>(null);
const stage = ref(0);
const isPlaying = ref(true);
const stageNames = ['太极', '两仪', '四象', '八卦'];

let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let taiji: Taiji;
let bagua: Bagua;
let solarTerms: SolarTerms;
let animationId: number;
let clock: THREE.Clock;

// 太极类
class Taiji {
  group: THREE.Group;
  yangGroup: THREE.Group | null = null;
  yinGroup: THREE.Group | null = null;
  energyRings: THREE.Mesh[] = [];
  particles: THREE.Points | null = null;
  currentStage: number = 0;
  separation: number = 0;
  targetSeparation: number = 0;
  rotationSpeed: number = 0.012;
  isPlaying: boolean = true;
  radius: number = 2.5;
  time: number = 0;

  constructor(scene: THREE.Scene) {
    this.group = new THREE.Group();
    this._build();
    scene.add(this.group);
  }

  _build() {
    const r = this.radius;
    const thickness = 0.3;
    this._createDoubleSidedTaiji(r, thickness);
    this._createEnergyRings(r);
    this._createParticles(r);
  }

  _createDoubleSidedTaiji(radius: number, thickness: number) {
    const r = radius;
    const r2 = r / 2;

    const whiteMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0x888888,
      emissiveIntensity: 0.3,
      metalness: 0.4,
      roughness: 0.3,
      side: THREE.DoubleSide
    });

    const blackMat = new THREE.MeshStandardMaterial({
      color: 0x111111,
      emissive: 0x000000,
      metalness: 0.4,
      roughness: 0.3,
      side: THREE.DoubleSide
    });

    // 阳鱼
    this.yangGroup = new THREE.Group();
    const yangFront = this._createTaijiPart(r, r2, whiteMat, blackMat, true);
    yangFront.position.z = thickness / 2;
    this.yangGroup.add(yangFront);

    const yangBack = this._createTaijiPart(r, r2, whiteMat, blackMat, true);
    yangBack.position.z = -thickness / 2;
    yangBack.scale.z = -1;
    this.yangGroup.add(yangBack);

    const edgeGeo = new THREE.TorusGeometry(r, thickness / 2, 8, 64, Math.PI);
    const edgeMat = new THREE.MeshStandardMaterial({
      color: 0x111111,
      emissive: 0x000000,
      metalness: 0.4,
      roughness: 0.3,
      side: THREE.DoubleSide
    });
    const yangEdge = new THREE.Mesh(edgeGeo, edgeMat);
    yangEdge.rotation.z = Math.PI / 2;
    this.yangGroup.add(yangEdge);
    this.group.add(this.yangGroup);

    // 阴鱼
    this.yinGroup = new THREE.Group();
    const yinFront = this._createTaijiPart(r, r2, blackMat, whiteMat, false);
    yinFront.position.z = thickness / 2;
    this.yinGroup.add(yinFront);

    const yinBack = this._createTaijiPart(r, r2, blackMat, whiteMat, false);
    yinBack.position.z = -thickness / 2;
    yinBack.scale.z = -1;
    this.yinGroup.add(yinBack);

    const yinEdge = new THREE.Mesh(edgeGeo, blackMat);
    yinEdge.rotation.z = -Math.PI / 2;
    this.yinGroup.add(yinEdge);
    this.group.add(this.yinGroup);
  }

  _createTaijiPart(r: number, r2: number, mainMat: THREE.Material, eyeMat: THREE.Material, isYang: boolean) {
    const group = new THREE.Group();
    const halfCircleGeo = new THREE.CircleGeometry(r, 64, isYang ? -Math.PI/2 : Math.PI/2, Math.PI);
    const halfCircle = new THREE.Mesh(halfCircleGeo, mainMat);
    group.add(halfCircle);

    const smallCircleGeo = new THREE.CircleGeometry(r2, 64);
    const smallCircle = new THREE.Mesh(smallCircleGeo, mainMat);
    smallCircle.position.set(0, isYang ? r2 : -r2, 0.01);
    group.add(smallCircle);

    const eyeGeo = new THREE.CircleGeometry(r * 0.15, 32);
    const eye = new THREE.Mesh(eyeGeo, eyeMat);
    eye.position.set(0, isYang ? r2 : -r2, 0.02);
    group.add(eye);

    return group;
  }

  _createEnergyRings(r: number) {
    const colors = [0xffd700, 0x4ecdc4, 0xff6b9d, 0x88ccee, 0xffffff];
    colors.forEach((color, i) => {
      const ringGeo = new THREE.TorusGeometry(r * (1.3 + i * 0.2), 0.015, 8, 128);
      const ringMat = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.6 - i * 0.08
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2;
      this.energyRings.push(ring);
      this.group.add(ring);
    });
  }

  _createParticles(r: number) {
    const count = 100;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const velocities: { speed: number; theta: number; radius: number }[] = [];
    const palette = [[1, 0.85, 0], [0.3, 0.8, 0.77], [1, 0.42, 0.62], [0.53, 0.8, 0.93]];

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const rad = r * (1.5 + Math.random() * 2);
      positions[i * 3] = Math.cos(theta) * rad;
      positions[i * 3 + 1] = Math.sin(theta) * rad;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 0.3;
      const c = palette[Math.floor(Math.random() * 4)];
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
      opacity: 0.9,
      vertexColors: true,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geo, mat);
    (this.particles as any).userData = { velocities };
    this.group.add(this.particles);
  }

  setStage(s: number) {
    this.currentStage = s;
    if (s === 0) {
      this.targetSeparation = 0;
      (this.yangGroup as any).visible = true;
      (this.yinGroup as any).visible = true;
    } else if (s === 1) {
      this.targetSeparation = 3.5;
      (this.yangGroup as any).visible = true;
      (this.yinGroup as any).visible = true;
    } else if (s >= 2) {
      (this.yangGroup as any).visible = false;
      (this.yinGroup as any).visible = false;
    }
  }

  update(delta: number) {
    if (!this.isPlaying) return;
    this.time += delta;
    this.separation += (this.targetSeparation - this.separation) * 0.04;
    this.group.rotation.z += this.rotationSpeed;

    if (this.currentStage === 1) {
      (this.yangGroup as any).position.x = this.separation * 0.7;
      (this.yinGroup as any).position.x = -this.separation * 0.7;
    } else if (this.currentStage <= 0) {
      (this.yangGroup as any).position.x = 0;
      (this.yinGroup as any).position.x = 0;
    }

    this.energyRings.forEach((ring, i) => {
      ring.rotation.z += 0.02 * (i % 2 === 0 ? 1 : -1);
      (ring.material as any).opacity = (0.6 - i * 0.08) + Math.sin(this.time * 2 + i) * 0.15;
    });

    if (this.particles) {
      const pos = (this.particles.geometry.attributes.position.array as Float32Array);
      const velocities = (this.particles as any).userData.velocities;
      velocities.forEach((v: any, i: number) => {
        v.theta += v.speed;
        pos[i * 3] = v.radius * Math.cos(v.theta);
        pos[i * 3 + 1] = v.radius * Math.sin(v.theta);
      });
      this.particles.geometry.attributes.position.needsUpdate = true;
    }
  }

  setPlaying(playing: boolean) {
    this.isPlaying = playing;
  }

  reset() {
    this.setStage(0);
    this.separation = 0;
    (this.yangGroup as any).position.set(0, 0, 0);
    (this.yinGroup as any).position.set(0, 0, 0);
    (this.yangGroup as any).visible = true;
    (this.yinGroup as any).visible = true;
    this.group.rotation.z = 0;
  }
}

// 八卦类
class Bagua {
  group: THREE.Group;
  trigrams: THREE.Group[] = [];
  radius: number = 5.5;
  rotationSpeed: number = 0.005;
  isPlaying: boolean = true;
  currentStage: number = 0;
  time: number = 0;
  data: any[];

  constructor(scene: THREE.Scene) {
    this.group = new THREE.Group();
    this.data = [
      { name: '乾', lines: [1, 1, 1], nature: '阳', color: 0xffd700 },
      { name: '兑', lines: [1, 1, 0], nature: '阳', color: 0xffaa00 },
      { name: '离', lines: [1, 0, 1], nature: '阳', color: 0xff6b9d },
      { name: '震', lines: [1, 0, 0], nature: '阳', color: 0xff8855 },
      { name: '坤', lines: [0, 0, 0], nature: '阴', color: 0x4ecdc4 },
      { name: '艮', lines: [0, 0, 1], nature: '阴', color: 0x88ccee },
      { name: '坎', lines: [0, 1, 0], nature: '阴', color: 0x99ddff },
      { name: '巽', lines: [0, 1, 1], nature: '阴', color: 0x66ffcc }
    ];
    this._build();
    scene.add(this.group);
  }

  _build() {
    this.data.forEach((item, index) => {
      const trigram = this._createTrigram(item, index);
      const angle = (index / 8) * Math.PI * 2 - Math.PI / 2;
      (trigram as any).userData = {
        angle,
        index,
        nature: item.nature,
        name: item.name,
        baseRadius: this.radius,
        floatOffset: Math.random() * Math.PI * 2
      };
      trigram.position.set(Math.cos(angle) * this.radius, Math.sin(angle) * this.radius, 0);
      this.trigrams.push(trigram);
      this.group.add(trigram);
    });
  }

  _createTrigram(item: any, index: number) {
    const g = new THREE.Group();
    const glowGeo = new THREE.RingGeometry(0.8, 1.0, 32);
    const glowMat = new THREE.MeshBasicMaterial({
      color: item.color,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide
    });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    glow.rotation.x = Math.PI / 2;
    g.add(glow);

    const yangMat = new THREE.MeshStandardMaterial({
      color: item.color,
      emissive: item.color,
      emissiveIntensity: 0.8,
      metalness: 0.8,
      roughness: 0.2
    });

    const yinMat = new THREE.MeshStandardMaterial({
      color: item.color,
      emissive: item.color,
      emissiveIntensity: 0.6,
      metalness: 0.8,
      roughness: 0.2
    });

    const lineWidth = 0.6;
    const lineHeight = 0.08;
    const lineDepth = 0.1;
    const gap = 0.2;

    item.lines.forEach((isYang: number, i: number) => {
      const y = (1 - i) * gap;
      if (isYang) {
        const bar = new THREE.Mesh(new THREE.BoxGeometry(lineWidth, lineHeight, lineDepth), yangMat);
        bar.position.y = y;
        g.add(bar);
      } else {
        const half = lineWidth * 0.35;
        const left = new THREE.Mesh(new THREE.BoxGeometry(half, lineHeight, lineDepth), yinMat);
        left.position.set(-lineWidth * 0.32, y, 0);
        const right = new THREE.Mesh(new THREE.BoxGeometry(half, lineHeight, lineDepth), yinMat);
        right.position.set(lineWidth * 0.32, y, 0);
        g.add(left);
        g.add(right);
      }
    });

    const label = this._createLabel(item.name, item.color);
    label.position.set(0, -0.6, 0.1);
    g.add(label);

    return g;
  }

  _createLabel(text: string, color: number) {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d')!;
    ctx.font = 'bold 90px Microsoft YaHei, sans-serif';
    ctx.fillStyle = '#' + color.toString(16).padStart(6, '0');
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = '#' + color.toString(16).padStart(6, '0');
    ctx.shadowBlur = 20;
    ctx.fillText(text, 64, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, blending: THREE.AdditiveBlending });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(0.8, 0.8, 1);
    return sprite;
  }

  setStage(s: number) {
    this.currentStage = s;
  }

  update(delta: number) {
    if (!this.isPlaying) return;
    this.time += delta;
    this.group.rotation.z += this.rotationSpeed;

    this.trigrams.forEach((t, i) => {
      const angle = (t as any).userData.angle;
      const radius = (t as any).userData.baseRadius;
      const floatOffset = (t as any).userData.floatOffset;
      const floatY = Math.sin(this.time * 2 + floatOffset) * 0.3;
      const floatZ = Math.cos(this.time * 1.5 + floatOffset) * 0.2;
      const breathScale = 1 + Math.sin(this.time * 3 + i) * 0.1;

      let expandedRadius = radius;
      if (this.currentStage >= 3) {
        expandedRadius = radius * 1.3;
      }

      t.position.set(Math.cos(angle) * expandedRadius, Math.sin(angle) * expandedRadius + floatY, floatZ);
      t.scale.setScalar(breathScale);

      if (this.currentStage >= 3) {
        t.rotation.z += 0.01;
      }
    });
  }

  setPlaying(playing: boolean) {
    this.isPlaying = playing;
  }

  reset() {
    this.setStage(0);
    this.group.rotation.z = 0;
    this.trigrams.forEach((t) => {
      const angle = (t as any).userData.angle;
      t.position.set(Math.cos(angle) * this.radius, Math.sin(angle) * this.radius, 0);
      t.rotation.z = 0;
      t.scale.setScalar(1);
    });
  }
}

// 节气类
class SolarTerms {
  group: THREE.Group;
  labels: THREE.Sprite[] = [];
  radius: number = 8.0;
  rotationSpeed: number = 0.001;
  isPlaying: boolean = true;
  activeIndex: number;
  raycaster: THREE.Raycaster;
  mouse: THREE.Vector2;
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;

  constructor(scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer) {
    this.group = new THREE.Group();
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.activeIndex = this._getCurrentTermIndex();
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this._build();
    scene.add(this.group);
  }

  _build() {
    SOLAR_TERMS_DATA.forEach((data, index) => {
      const angle = (index / 24) * Math.PI * 2 - Math.PI / 2;
      const isActive = index === this.activeIndex;
      const sprite = this._createSimpleLabel(data.name, isActive);
      (sprite as any).userData = { index, data, angle, isActive };
      sprite.position.set(Math.cos(angle) * this.radius, Math.sin(angle) * this.radius, 0);
      this.labels.push(sprite);
      this.group.add(sprite);
    });
  }

  _createSimpleLabel(name: string, isActive: boolean) {
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 60;
    const ctx = canvas.getContext('2d')!;
    ctx.font = 'bold 32px Microsoft YaHei, sans-serif';
    ctx.fillStyle = isActive ? '#4ecdc4' : 'rgba(255, 255, 255, 0.6)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    if (isActive) {
      ctx.shadowColor = '#4ecdc4';
      ctx.shadowBlur = 15;
    }
    ctx.fillText(name, 100, 30);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(1.5, 0.45, 1);
    return sprite;
  }

  _getCurrentTermIndex() {
    const now = new Date();
    const month = now.getMonth() + 1;
    const day = now.getDate();
    const md = month * 100 + day;
    const approxStarts = [204, 219, 306, 321, 405, 420, 506, 521, 606, 621, 707, 723, 808, 823, 908, 923, 1008, 1023, 1107, 1122, 1207, 1222, 105, 120];
    let best = 0;
    for (let i = 0; i < 24; i++) {
      const start = approxStarts[i];
      const next = approxStarts[(i + 1) % 24];
      if (start < next) {
        if (md >= start && md < next) { best = i; break; }
      } else {
        if (md >= start || md < next) { best = i; break; }
      }
    }
    return best;
  }

  update() {
    if (!this.isPlaying) return;
    this.group.rotation.z += this.rotationSpeed;
    const active = this.labels[this.activeIndex];
    if (active) {
      const pulse = 1 + Math.sin(Date.now() * 0.005) * 0.15;
      active.scale.set(1.8 * pulse, 0.54 * pulse, 1);
    }
  }

  setPlaying(playing: boolean) {
    this.isPlaying = playing;
  }

  reset() {
    this.group.rotation.z = 0;
  }

  showModal(data: any) {
    const modal = document.getElementById('solar-term-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    if (modal && title && body) {
      title.textContent = data.name + '（' + data.season + '）';
      body.innerHTML =
        '<div class="info-item"><span class="info-label">日期范围</span><div class="info-value">' + data.dateRange + '</div></div>' +
        '<div class="info-item"><span class="info-label">含义</span><div class="info-value">' + data.meaning + '</div></div>' +
        '<div class="info-item"><span class="info-label">气候特征</span><div class="info-value">' + data.climate + '</div></div>' +
        '<div class="info-item"><span class="info-label">养生建议</span><div class="info-value">' + data.health + '</div></div>';
      modal.classList.remove('hidden');
      requestAnimationFrame(() => modal.classList.add('show'));
    }
  }
}

// 方法
const togglePlay = () => {
  isPlaying.value = !isPlaying.value;
  taiji.setPlaying(isPlaying.value);
  bagua.setPlaying(isPlaying.value);
  solarTerms.setPlaying(isPlaying.value);
};

const nextStage = () => {
  if (stage.value >= 3) return;
  stage.value += 1;
  taiji.setStage(stage.value);
  bagua.setStage(stage.value);
};

const reset = () => {
  stage.value = 0;
  taiji.reset();
  bagua.reset();
  solarTerms.reset();
};

const closeModal = () => {
  const modal = document.getElementById('solar-term-modal');
  if (modal) {
    modal.classList.remove('show');
    setTimeout(() => modal.classList.add('hidden'), 300);
  }
};

onMounted(() => {
  if (!canvasContainer.value) return;

  // 场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050510);

  // 相机
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 0, 20);

  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.5;
  canvasContainer.value.appendChild(renderer.domElement);

  // 控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 10;
  controls.maxDistance = 40;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.8;

  // 灯光
  const ambient = new THREE.AmbientLight(0x222244, 0.5);
  scene.add(ambient);

  // 动态彩色灯光
  const lightColors = [0xffd700, 0x4ecdc4, 0xff6b9d, 0x88ccee];
  const lights: { light: THREE.PointLight; baseAngle: number }[] = [];
  lightColors.forEach((color, i) => {
    const light = new THREE.PointLight(color, 2.0, 30);
    const angle = (i / 4) * Math.PI * 2;
    light.position.set(Math.cos(angle) * 10, Math.sin(angle) * 10, 5);
    scene.add(light);
    lights.push({ light, baseAngle: angle });
  });

  // 星空背景
  const starCount = 1500;
  const starsGeo = new THREE.BufferGeometry();
  const starPos = new Float32Array(starCount * 3);
  const starColors = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount; i++) {
    const r = 50 + Math.random() * 100;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    starPos[i * 3 + 2] = r * Math.cos(phi);
    const brightness = 0.3 + Math.random() * 0.7;
    starColors[i * 3] = brightness;
    starColors[i * 3 + 1] = brightness;
    starColors[i * 3 + 2] = brightness + Math.random() * 0.3;
  }
  starsGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  starsGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));
  const starsMat = new THREE.PointsMaterial({ size: 0.3, vertexColors: true, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending });
  const stars = new THREE.Points(starsGeo, starsMat);
  scene.add(stars);

  // 能量粒子流
  const particleCount = 800;
  const particlesGeo = new THREE.BufferGeometry();
  const particlePos = new Float32Array(particleCount * 3);
  const particleColors = new Float32Array(particleCount * 3);
  const particleVelocities: { speed: number; theta: number; radius: number }[] = [];
  const particleColorPalette = [[1.0, 0.85, 0], [0.3, 0.8, 0.77], [1.0, 0.42, 0.62], [0.53, 0.8, 0.93]];
  for (let i = 0; i < particleCount; i++) {
    const r = 3 + Math.random() * 12;
    const theta = Math.random() * Math.PI * 2;
    particlePos[i * 3] = r * Math.cos(theta);
    particlePos[i * 3 + 1] = r * Math.sin(theta);
    particlePos[i * 3 + 2] = (Math.random() - 0.5) * 2;
    const color = particleColorPalette[Math.floor(Math.random() * 4)];
    particleColors[i * 3] = color[0];
    particleColors[i * 3 + 1] = color[1];
    particleColors[i * 3 + 2] = color[2];
    particleVelocities.push({ speed: 0.005 + Math.random() * 0.01, theta, radius: r });
  }
  particlesGeo.setAttribute('position', new THREE.BufferAttribute(particlePos, 3));
  particlesGeo.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));
  const particlesMat = new THREE.PointsMaterial({ size: 0.12, transparent: true, opacity: 0.9, vertexColors: true, blending: THREE.AdditiveBlending, depthWrite: false });
  const energyParticles = new THREE.Points(particlesGeo, particlesMat);
  scene.add(energyParticles);

  // 核心模块
  taiji = new Taiji(scene);
  bagua = new Bagua(scene);
  solarTerms = new SolarTerms(scene, camera, renderer);

  clock = new THREE.Clock();
  let time = 0;

  const animate = () => {
    animationId = requestAnimationFrame(animate);
    const delta = clock.getDelta();
    time += delta;

    controls.update();
    taiji.update(delta);
    bagua.update(delta);
    solarTerms.update();

    // 动态灯光旋转
    lights.forEach((item, i) => {
      const angle = item.baseAngle + time * (0.3 + i * 0.1);
      item.light.position.set(Math.cos(angle) * 10, Math.sin(angle) * 10, 5 + Math.sin(time * 2 + i) * 2);
      item.light.intensity = 1.5 + Math.sin(time * 3 + i) * 0.5;
    });

    // 星空缓慢旋转
    stars.rotation.y += 0.0001;
    stars.rotation.x += 0.00005;

    // 能量粒子流动
    const pos = particlesGeo.attributes.position.array as Float32Array;
    particleVelocities.forEach((v, i) => {
      v.theta += v.speed;
      pos[i * 3] = v.radius * Math.cos(v.theta);
      pos[i * 3 + 1] = v.radius * Math.sin(v.theta);
      pos[i * 3 + 2] += Math.sin(time + i) * 0.005;
    });
    particlesGeo.attributes.position.needsUpdate = true;

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

  // 点击事件
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  renderer.domElement.addEventListener('click', (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(solarTerms.labels, false);
    if (hits.length) {
      solarTerms.showModal((hits[0].object as any).userData.data);
    }
  });
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
.taiji-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #050510;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
}

.controls {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20px;
  background: rgba(0, 0, 0, 0.6);
  padding: 12px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.stage-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stage-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.stage-name {
  font-size: 18px;
  font-weight: bold;
  color: #4ecdc4;
}

.btn-group {
  display: flex;
  gap: 10px;
}

.ctrl-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.ctrl-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}

.modal.show {
  opacity: 1;
  visibility: visible;
}

.modal.hidden {
  display: none;
}

.modal-content {
  background: #1f2937;
  padding: 24px;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-content h3 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #4ecdc4;
}

.info-item {
  margin-bottom: 12px;
}

.info-label {
  display: inline-block;
  width: 80px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  display: inline;
  color: rgba(255, 255, 255, 0.6);
}
</style>
