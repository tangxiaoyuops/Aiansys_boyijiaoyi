<template>
  <div class="bazi-chart-container" :class="{ 'compact-mode': compact }">
    <!-- 四柱八字主体 -->
    <div class="sizhu-wrapper">
      <div class="sizhu-grid">
        <!-- 年柱 -->
        <div class="zhu-column" v-if="sizhuList[0]">
          <div class="zhu-label">年柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[0].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[0].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[0].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[0].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[0].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[0].zhiWuxing }}</span>
            </div>
            <!-- 藏干显示 -->
            <div v-if="sizhuList[0].cangGan && sizhuList[0].cangGan.length > 0" class="cang-gan-section">
              <div class="cang-gan-label">藏干</div>
              <div class="cang-gan-list">
                <span 
                  v-for="(gan, idx) in sizhuList[0].cangGan" 
                  :key="idx"
                  class="cang-gan-item"
                  :class="{ 'ben-qi': idx === 0, 'zhong-qi': idx === 1, 'yu-qi': idx === 2 }"
                  :style="{ color: getWuxingColor(tianganWuxing[gan]) }"
                >
                  {{ gan }}
                </span>
              </div>
              <!-- 藏干十神 -->
              <div v-if="getCangGanShishen(0)" class="cang-gan-shishen">
                {{ getCangGanShishen(0) }}
              </div>
            </div>
            <!-- 十神 -->
            <div v-if="getShishen(0)" class="shishen-tag">
              {{ getShishen(0) }}
            </div>
            <!-- 纳音 -->
            <div v-if="getNayin(0)" class="nayin-tag">
              {{ getNayin(0) }}
            </div>
          </div>
        </div>

        <!-- 月柱 -->
        <div class="zhu-column" v-if="sizhuList[1]">
          <div class="zhu-label">月柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[1].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[1].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[1].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[1].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[1].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[1].zhiWuxing }}</span>
            </div>
            <!-- 藏干显示 -->
            <div v-if="sizhuList[1].cangGan && sizhuList[1].cangGan.length > 0" class="cang-gan-section">
              <div class="cang-gan-label">藏干</div>
              <div class="cang-gan-list">
                <span 
                  v-for="(gan, idx) in sizhuList[1].cangGan" 
                  :key="idx"
                  class="cang-gan-item"
                  :class="{ 'ben-qi': idx === 0, 'zhong-qi': idx === 1, 'yu-qi': idx === 2 }"
                  :style="{ color: getWuxingColor(tianganWuxing[gan]) }"
                >
                  {{ gan }}
                </span>
              </div>
              <!-- 藏干十神 -->
              <div v-if="getCangGanShishen(1)" class="cang-gan-shishen">
                {{ getCangGanShishen(1) }}
              </div>
            </div>
            <div v-if="getShishen(1)" class="shishen-tag">
              {{ getShishen(1) }}
            </div>
            <!-- 纳音 -->
            <div v-if="getNayin(1)" class="nayin-tag">
              {{ getNayin(1) }}
            </div>
          </div>
        </div>

        <!-- 日柱（日主） -->
        <div class="zhu-column rizhu" v-if="sizhuList[2]">
          <div class="zhu-label rizhu-label">日柱（日主）</div>
          <div class="zhu-body">
            <div 
              class="tiangan rizhu-tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[2].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[2].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[2].ganWuxing }}</span>
              <span class="rizhu-badge">日主</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[2].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[2].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[2].zhiWuxing }}</span>
            </div>
            <!-- 藏干显示 -->
            <div v-if="sizhuList[2].cangGan && sizhuList[2].cangGan.length > 0" class="cang-gan-section">
              <div class="cang-gan-label">藏干</div>
              <div class="cang-gan-list">
                <span 
                  v-for="(gan, idx) in sizhuList[2].cangGan" 
                  :key="idx"
                  class="cang-gan-item"
                  :class="{ 'ben-qi': idx === 0, 'zhong-qi': idx === 1, 'yu-qi': idx === 2 }"
                  :style="{ color: getWuxingColor(tianganWuxing[gan]) }"
                >
                  {{ gan }}
                </span>
              </div>
              <!-- 藏干十神 -->
              <div v-if="getCangGanShishen(2)" class="cang-gan-shishen">
                {{ getCangGanShishen(2) }}
              </div>
            </div>
            <div v-if="getShishen(2)" class="shishen-tag">
              {{ getShishen(2) }}
            </div>
            <!-- 纳音 -->
            <div v-if="getNayin(2)" class="nayin-tag">
              {{ getNayin(2) }}
            </div>
          </div>
        </div>

        <!-- 时柱 -->
        <div class="zhu-column" v-if="sizhuList[3]">
          <div class="zhu-label">时柱</div>
          <div class="zhu-body">
            <div 
              class="tiangan" 
              :style="{ background: getWuxingGradient(sizhuList[3].ganWuxing) }"
            >
              <span class="gan-char">{{ sizhuList[3].gan }}</span>
              <span class="wuxing-badge">{{ sizhuList[3].ganWuxing }}</span>
            </div>
            <div 
              class="dizhi" 
              :style="{ background: getWuxingGradient(sizhuList[3].zhiWuxing) }"
            >
              <span class="zhi-char">{{ sizhuList[3].zhi }}</span>
              <span class="wuxing-badge">{{ sizhuList[3].zhiWuxing }}</span>
            </div>
            <!-- 藏干显示 -->
            <div v-if="sizhuList[3].cangGan && sizhuList[3].cangGan.length > 0" class="cang-gan-section">
              <div class="cang-gan-label">藏干</div>
              <div class="cang-gan-list">
                <span 
                  v-for="(gan, idx) in sizhuList[3].cangGan" 
                  :key="idx"
                  class="cang-gan-item"
                  :class="{ 'ben-qi': idx === 0, 'zhong-qi': idx === 1, 'yu-qi': idx === 2 }"
                  :style="{ color: getWuxingColor(tianganWuxing[gan]) }"
                >
                  {{ gan }}
                </span>
              </div>
              <!-- 藏干十神 -->
              <div v-if="getCangGanShishen(3)" class="cang-gan-shishen">
                {{ getCangGanShishen(3) }}
              </div>
            </div>
            <div v-if="getShishen(3)" class="shishen-tag">
              {{ getShishen(3) }}
            </div>
            <!-- 纳音 -->
            <div v-if="getNayin(3)" class="nayin-tag">
              {{ getNayin(3) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 五行统计 -->
    <div class="wuxing-stats" v-if="wuxingAnalysis">
      <h4 class="stats-title">五行分布</h4>
      <div class="wuxing-bars">
        <div 
          v-for="item in wuxingDataList" 
          :key="item.name" 
          class="wuxing-bar-item"
        >
          <div class="bar-header">
            <span class="bar-name" :style="{ color: getWuxingColor(item.name) }">{{ item.name }}</span>
            <span class="bar-value">{{ item.value }}</span>
          </div>
          <div class="bar-track">
            <div 
              class="bar-fill" 
              :style="{ 
                width: `${(item.value / maxWuxingValue) * 100}%`,
                background: getWuxingGradient(item.name)
              }"
            ></div>
          </div>
        </div>
      </div>
      <div class="rizhu-wuxing" v-if="wuxingAnalysis?.wuxing_data?.rizhu_wuxing">
        <span class="label">日主五行：</span>
        <span 
          class="value" 
          :style="{ color: getWuxingColor(wuxingAnalysis.wuxing_data.rizhu_wuxing) }"
        >
          {{ wuxingAnalysis.wuxing_data.rizhu_wuxing }}
        </span>
      </div>
    </div>

    <!-- 五行喜忌 - 暂时隐藏，身强身弱判断需要综合分析 -->
    <div class="wuxing-xi-ji" v-if="false && wuxingXiJi">
      <h4 class="stats-title">五行喜忌</h4>
      <div class="xi-ji-content">
        <div class="rizhu-strength" :class="wuxingXiJi.is_rizhu_qiang ? 'qiang' : 'ruo'">
          <span class="label">日主：</span>
          <span class="value">{{ wuxingXiJi.is_rizhu_qiang ? '身强' : '身弱' }}</span>
        </div>
        <div class="xi-wuxing" v-if="wuxingXiJi.xi_wuxing?.length">
          <span class="label">喜用：</span>
          <span class="wuxing-tags">
            <span 
              v-for="wx in wuxingXiJi.xi_wuxing" 
              :key="wx" 
              class="wx-tag xi"
              :style="{ background: getWuxingGradient(wx), color: '#fff' }"
            >
              {{ wx }}
            </span>
          </span>
        </div>
        <div class="ji-wuxing" v-if="wuxingXiJi.ji_wuxing?.length">
          <span class="label">忌讳：</span>
          <span class="wuxing-tags">
            <span 
              v-for="wx in wuxingXiJi.ji_wuxing" 
              :key="wx" 
              class="wx-tag ji"
              :style="{ background: getWuxingLightColor(wx) }"
            >
              {{ wx }}
            </span>
          </span>
        </div>
      </div>
    </div>

    <!-- 地支关系 -->
    <div class="zhi-relations" v-if="zhiRelations && hasZhiRelations">
      <h4 class="stats-title">地支关系</h4>
      <div class="relations-grid">
        <div v-if="zhiRelations.liu_he?.length" class="relation-group">
          <span class="relation-label he">六合</span>
          <div class="relation-items">
            <span v-for="(rel, i) in zhiRelations.liu_he" :key="i" class="relation-item">
              {{ rel.desc }}
            </span>
          </div>
        </div>
        <div v-if="zhiRelations.liu_chong?.length" class="relation-group">
          <span class="relation-label chong">六冲</span>
          <div class="relation-items">
            <span v-for="(rel, i) in zhiRelations.liu_chong" :key="i" class="relation-item chong">
              {{ rel.desc }}
            </span>
          </div>
        </div>
        <div v-if="zhiRelations.san_he?.length" class="relation-group">
          <span class="relation-label he">三合</span>
          <div class="relation-items">
            <span v-for="(rel, i) in zhiRelations.san_he" :key="i" class="relation-item">
              {{ rel.desc }}
            </span>
          </div>
        </div>
        <div v-if="zhiRelations.san_xing?.length" class="relation-group">
          <span class="relation-label xing">三刑</span>
          <div class="relation-items">
            <span v-for="(rel, i) in zhiRelations.san_xing" :key="i" class="relation-item xing">
              {{ rel.desc }}
            </span>
          </div>
        </div>
        <div v-if="zhiRelations.liu_hai?.length" class="relation-group">
          <span class="relation-label hai">六害</span>
          <div class="relation-items">
            <span v-for="(rel, i) in zhiRelations.liu_hai" :key="i" class="relation-item hai">
              {{ rel.desc }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 天干关系 -->
    <div class="gan-relations" v-if="ganRelations && hasGanRelations">
      <h4 class="stats-title">天干关系</h4>
      <div class="relations-grid">
        <div v-if="ganRelations.tian_gan_he?.length" class="relation-group">
          <span class="relation-label he">合化</span>
          <div class="relation-items">
            <span v-for="(rel, i) in ganRelations.tian_gan_he" :key="i" class="relation-item">
              {{ rel.desc }}
            </span>
          </div>
        </div>
        <div v-if="ganRelations.tian_gan_chong?.length" class="relation-group">
          <span class="relation-label chong">相冲</span>
          <div class="relation-items">
            <span v-for="(rel, i) in ganRelations.tian_gan_chong" :key="i" class="relation-item chong">
              {{ rel.desc }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 扩展信息 -->
    <div class="extended-info" v-if="extendedInfo">
      <h4 class="stats-title">扩展信息</h4>
      <div class="info-grid">
        <!-- 命宫 -->
        <div class="info-item" v-if="extendedInfo.ming_gong">
          <span class="info-label">命宫</span>
          <span class="info-value">{{ extendedInfo.ming_gong.gan_zhi }}</span>
        </div>
        <!-- 胎元 -->
        <div class="info-item" v-if="extendedInfo.tai_yuan">
          <span class="info-label">胎元</span>
          <span class="info-value">{{ extendedInfo.tai_yuan.gan_zhi }}</span>
        </div>
        <!-- 身宫 -->
        <div class="info-item" v-if="extendedInfo.shen_gong">
          <span class="info-label">身宫</span>
          <span class="info-value">{{ extendedInfo.shen_gong.gan_zhi }}</span>
        </div>
        <!-- 空亡 -->
        <div class="info-item" v-if="extendedInfo.xun_kong?.kong_wang">
          <span class="info-label">空亡</span>
          <span class="info-value kong">{{ extendedInfo.xun_kong.kong_wang.join('、') }}</span>
        </div>
      </div>
    </div>

    <!-- 藏干图例说明 -->
    <div class="cang-gan-legend">
      <span class="legend-item">
        <span class="legend-dot ben-qi-dot"></span>
        <span>本气</span>
      </span>
      <span class="legend-item">
        <span class="legend-dot zhong-qi-dot"></span>
        <span>中气</span>
      </span>
      <span class="legend-item">
        <span class="legend-dot yu-qi-dot"></span>
        <span>余气</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  sizhu?: any;
  wuxingAnalysis?: any;
  shishenAnalysis?: any;
  extendedInfo?: any;
  zhiRelations?: any;
  ganRelations?: any;
  wuxingXiJi?: any;
  compact?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
});

// 天干五行映射
const tianganWuxing: Record<string, string> = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
};

// 地支五行映射
const dizhiWuxing: Record<string, string> = {
  '子': '水', '丑': '土',
  '寅': '木', '卯': '木',
  '辰': '土', '巳': '火',
  '午': '火', '未': '土',
  '申': '金', '酉': '金',
  '戌': '土', '亥': '水',
};

const sizhuList = computed(() => {
  if (!props.sizhu) return [];
  
  return [
    {
      name: '年柱',
      gan: props.sizhu.nian_zhu?.tian_gan || '',
      zhi: props.sizhu.nian_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.nian_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.nian_zhu?.di_zhi] || '',
      cangGan: props.sizhu.nian_zhu?.cang_gan || [],
    },
    {
      name: '月柱',
      gan: props.sizhu.yue_zhu?.tian_gan || '',
      zhi: props.sizhu.yue_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.yue_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.yue_zhu?.di_zhi] || '',
      cangGan: props.sizhu.yue_zhu?.cang_gan || [],
    },
    {
      name: '日柱',
      gan: props.sizhu.ri_zhu?.tian_gan || '',
      zhi: props.sizhu.ri_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.ri_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.ri_zhu?.di_zhi] || '',
      cangGan: props.sizhu.ri_zhu?.cang_gan || [],
    },
    {
      name: '时柱',
      gan: props.sizhu.shi_zhu?.tian_gan || '',
      zhi: props.sizhu.shi_zhu?.di_zhi || '',
      ganWuxing: tianganWuxing[props.sizhu.shi_zhu?.tian_gan] || '',
      zhiWuxing: dizhiWuxing[props.sizhu.shi_zhu?.di_zhi] || '',
      cangGan: props.sizhu.shi_zhu?.cang_gan || [],
    },
  ];
});

const wuxingDataList = computed(() => {
  if (!props.wuxingAnalysis?.wuxing_data) return [];
  
  const data = props.wuxingAnalysis.wuxing_data;
  return [
    { name: '金', value: data.jin || 0 },
    { name: '木', value: data.mu || 0 },
    { name: '水', value: data.shui || 0 },
    { name: '火', value: data.huo || 0 },
    { name: '土', value: data.tu || 0 },
  ];
});

const maxWuxingValue = computed(() => {
  const values = wuxingDataList.value.map(item => item.value);
  return Math.max(...values, 1);
});

// 检查是否有地支关系
const hasZhiRelations = computed(() => {
  if (!props.zhiRelations) return false;
  return (
    (props.zhiRelations.liu_he?.length > 0) ||
    (props.zhiRelations.liu_chong?.length > 0) ||
    (props.zhiRelations.san_he?.length > 0) ||
    (props.zhiRelations.san_xing?.length > 0) ||
    (props.zhiRelations.liu_hai?.length > 0)
  );
});

// 检查是否有天干关系
const hasGanRelations = computed(() => {
  if (!props.ganRelations) return false;
  return (
    (props.ganRelations.tian_gan_he?.length > 0) ||
    (props.ganRelations.tian_gan_chong?.length > 0)
  );
});

// 获取十神信息
const getShishen = (index: number) => {
  if (!props.shishenAnalysis?.shishen_data) return '';
  
  const keys = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu'];
  const key = keys[index];
  const shishen = props.shishenAnalysis.shishen_data[key];
  
  if (shishen && shishen.gan_shishen) {
    return shishen.gan_shishen;
  }
  return '';
};

// 获取藏干十神
const getCangGanShishen = (index: number) => {
  if (!props.shishenAnalysis?.shishen_data) return '';
  
  const keys = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu'];
  const key = keys[index];
  const shishen = props.shishenAnalysis.shishen_data[key];
  
  if (shishen && shishen.zhi_cang_gan_shishen && shishen.zhi_cang_gan_shishen.length > 0) {
    return shishen.zhi_cang_gan_shishen.map((item: any) => item.shishen).join('/');
  }
  return '';
};

// 获取纳音
const getNayin = (index: number) => {
  if (!props.extendedInfo?.nayin) return '';
  
  const keys = ['nian_zhu', 'yue_zhu', 'ri_zhu', 'shi_zhu'];
  const key = keys[index];
  const nayin = props.extendedInfo.nayin[key];
  
  if (nayin && nayin.name) {
    return nayin.name;
  }
  return '';
};

// 五行颜色
const getWuxingColor = (wuxing: string): string => {
  const colorMap: Record<string, string> = {
    '金': '#D4AF37',
    '木': '#228B22',
    '水': '#1E90FF',
    '火': '#DC143C',
    '土': '#8B4513',
  };
  return colorMap[wuxing] || '#666';
};

// 五行浅色
const getWuxingLightColor = (wuxing: string): string => {
  const colorMap: Record<string, string> = {
    '金': 'rgba(212, 175, 55, 0.3)',
    '木': 'rgba(34, 139, 34, 0.3)',
    '水': 'rgba(30, 144, 255, 0.3)',
    '火': 'rgba(220, 20, 60, 0.3)',
    '土': 'rgba(139, 69, 19, 0.3)',
  };
  return colorMap[wuxing] || 'rgba(100, 100, 100, 0.3)';
};

// 五行渐变
const getWuxingGradient = (wuxing: string): string => {
  const gradientMap: Record<string, string> = {
    '金': 'linear-gradient(135deg, #FFE55C 0%, #D4AF37 50%, #B8860B 100%)',
    '木': 'linear-gradient(135deg, #90EE90 0%, #228B22 50%, #006400 100%)',
    '水': 'linear-gradient(135deg, #87CEEB 0%, #1E90FF 50%, #0066CC 100%)',
    '火': 'linear-gradient(135deg, #FF6B6B 0%, #DC143C 50%, #8B0000 100%)',
    '土': 'linear-gradient(135deg, #DEB887 0%, #8B4513 50%, #654321 100%)',
  };
  return gradientMap[wuxing] || 'linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%)';
};
</script>

<style scoped>
.bazi-chart-container {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(251, 250, 248, 0.95) 0%, rgba(248, 246, 242, 0.95) 100%);
  border-radius: 16px;
  border: 1px solid rgba(139, 90, 43, 0.15);
  box-shadow: 
    0 4px 20px rgba(139, 90, 43, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* 四柱网格布局 */
.sizhu-wrapper {
  margin-bottom: 24px;
}

.sizhu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.zhu-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.zhu-label {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  padding: 6px 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(245, 242, 235, 0.9) 100%);
  border-radius: 20px;
  border: 1px solid rgba(139, 90, 43, 0.2);
  box-shadow: 0 2px 8px rgba(139, 90, 43, 0.1);
}

.zhu-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 12px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(252, 250, 245, 0.95) 100%);
  border-radius: 12px;
  border: 2px solid rgba(139, 90, 43, 0.15);
  box-shadow: 
    0 4px 16px rgba(139, 90, 43, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 1);
  min-width: 90px;
}

/* 天干样式 */
.tiangan {
  width: 64px;
  height: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 2px 0 rgba(255, 255, 255, 0.3),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.tiangan:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 8px 20px rgba(0, 0, 0, 0.2),
    inset 0 2px 0 rgba(255, 255, 255, 0.3),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
}

.gan-char {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(255, 255, 255, 0.5);
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
  letter-spacing: 2px;
}

.wuxing-badge {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(0, 0, 0, 0.25);
  padding: 1px 6px;
  border-radius: 8px;
  margin-top: 2px;
  font-weight: 500;
}

/* 地支样式 */
.dizhi {
  width: 56px;
  height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: 
    0 3px 10px rgba(0, 0, 0, 0.12),
    inset 0 2px 0 rgba(255, 255, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.dizhi:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0 6px 16px rgba(0, 0, 0, 0.18),
    inset 0 2px 0 rgba(255, 255, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.08);
}

.zhi-char {
  font-size: 30px;
  font-weight: 600;
  color: #fff;
  text-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.25),
    0 0 15px rgba(255, 255, 255, 0.4);
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
  letter-spacing: 1px;
}

/* 日主特殊样式 */
.rizhu .zhu-label {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.25) 100%);
  border-color: rgba(212, 175, 55, 0.4);
  color: #8B6914;
}

.rizhu .zhu-body {
  border-color: rgba(212, 175, 55, 0.4);
  box-shadow: 
    0 4px 20px rgba(212, 175, 55, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 1);
}

.rizhu-tiangan {
  position: relative;
}

.rizhu-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 9px;
  color: #fff;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(255, 165, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 藏干样式 */
.cang-gan-section {
  margin-top: 6px;
  padding: 6px 8px;
  background: rgba(139, 90, 43, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(139, 90, 43, 0.1);
}

.cang-gan-label {
  font-size: 10px;
  color: #8B7355;
  margin-bottom: 4px;
  text-align: center;
}

.cang-gan-list {
  display: flex;
  justify-content: center;
  gap: 4px;
  flex-wrap: wrap;
}

.cang-gan-item {
  font-size: 14px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.8);
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
}

.cang-gan-item.ben-qi {
  font-weight: 700;
  font-size: 15px;
}

.cang-gan-item.zhong-qi {
  font-size: 13px;
  opacity: 0.85;
}

.cang-gan-item.yu-qi {
  font-size: 12px;
  opacity: 0.7;
}

/* 藏干十神 */
.cang-gan-shishen {
  margin-top: 4px;
  font-size: 10px;
  color: #6B5D4D;
  text-align: center;
}

/* 十神标签 */
.shishen-tag {
  margin-top: 8px;
  padding: 4px 12px;
  font-size: 12px;
  color: #5D4E37;
  background: linear-gradient(135deg, rgba(139, 90, 43, 0.1) 0%, rgba(139, 90, 43, 0.05) 100%);
  border: 1px solid rgba(139, 90, 43, 0.2);
  border-radius: 12px;
  font-weight: 500;
}

/* 纳音标签 */
.nayin-tag {
  margin-top: 4px;
  padding: 2px 8px;
  font-size: 11px;
  color: #8B6914;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 8px;
  font-weight: 500;
}

/* 五行统计 */
.wuxing-stats {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.stats-title {
  font-size: 14px;
  font-weight: 600;
  color: #5D4E37;
  margin: 0 0 16px 0;
  padding-left: 12px;
  border-left: 3px solid #D4AF37;
}

.wuxing-bars {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.wuxing-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bar-name {
  font-size: 14px;
  font-weight: 600;
}

.bar-value {
  font-size: 16px;
  font-weight: 700;
  color: #3D3D3D;
}

.bar-track {
  height: 8px;
  background: rgba(139, 90, 43, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.rizhu-wuxing {
  margin-top: 16px;
  text-align: center;
  padding: 10px;
  background: rgba(212, 175, 55, 0.1);
  border-radius: 8px;
}

.rizhu-wuxing .label {
  font-size: 13px;
  color: #666;
  margin-right: 8px;
}

.rizhu-wuxing .value {
  font-size: 18px;
  font-weight: 700;
}

/* 五行喜忌 */
.wuxing-xi-ji {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.xi-ji-content {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.rizhu-strength {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 600;
}

.rizhu-strength.qiang {
  background: linear-gradient(135deg, rgba(220, 20, 60, 0.15) 0%, rgba(220, 20, 60, 0.05) 100%);
  color: #DC143C;
}

.rizhu-strength.ruo {
  background: linear-gradient(135deg, rgba(30, 144, 255, 0.15) 0%, rgba(30, 144, 255, 0.05) 100%);
  color: #1E90FF;
}

.xi-wuxing, .ji-wuxing {
  display: flex;
  align-items: center;
  gap: 8px;
}

.xi-wuxing .label, .ji-wuxing .label {
  font-size: 13px;
  color: #666;
}

.wuxing-tags {
  display: flex;
  gap: 4px;
}

.wx-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.wx-tag.xi {
  color: #fff;
}

.wx-tag.ji {
  color: #666;
}

/* 地支关系 */
.zhi-relations {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

/* 天干关系 */
.gan-relations {
  margin-top: 16px;
}

.relations-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.relation-group {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(139, 90, 43, 0.1);
}

.relation-label {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
}

.relation-label.he {
  background: linear-gradient(135deg, rgba(34, 139, 34, 0.2) 0%, rgba(34, 139, 34, 0.1) 100%);
  color: #228B22;
}

.relation-label.chong {
  background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(220, 20, 60, 0.1) 100%);
  color: #DC143C;
}

.relation-label.xing {
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.2) 0%, rgba(255, 165, 0, 0.1) 100%);
  color: #FF8C00;
}

.relation-label.hai {
  background: linear-gradient(135deg, rgba(139, 69, 19, 0.2) 0%, rgba(139, 69, 19, 0.1) 100%);
  color: #8B4513;
}

.relation-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.relation-item {
  font-size: 12px;
  padding: 2px 6px;
  background: rgba(139, 90, 43, 0.08);
  border-radius: 4px;
  color: #5D4E37;
}

.relation-item.chong {
  background: rgba(220, 20, 60, 0.1);
  color: #DC143C;
}

.relation-item.xing {
  background: rgba(255, 165, 0, 0.1);
  color: #FF8C00;
}

.relation-item.hai {
  background: rgba(139, 69, 19, 0.1);
  color: #8B4513;
}

/* 扩展信息 */
.extended-info {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(139, 90, 43, 0.15);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(139, 90, 43, 0.1);
}

.info-label {
  font-size: 11px;
  color: #8B7355;
}

.info-value {
  font-size: 16px;
  font-weight: 700;
  color: #5D4E37;
  font-family: 'KaiTi', 'STKaiti', 'SimSun', serif;
}

.info-value.kong {
  color: #909399;
  font-size: 14px;
}

/* 藏干图例 */
.cang-gan-legend {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 10px;
  background: rgba(139, 90, 43, 0.05);
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #5D4E37;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.ben-qi-dot {
  background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
}

.zhong-qi-dot {
  background: linear-gradient(135deg, #A0A0A0 0%, #808080 100%);
}

.yu-qi-dot {
  background: linear-gradient(135deg, #C0C0C0 0%, #A0A0A0 100%);
}

/* 响应式 */
@media (max-width: 600px) {
  .sizhu-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .wuxing-bars {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .wuxing-bar-item:nth-child(4),
  .wuxing-bar-item:nth-child(5) {
    grid-column: span 1;
  }

  .cang-gan-legend {
    flex-wrap: wrap;
    gap: 10px;
  }

  .xi-ji-content {
    flex-direction: column;
    align-items: flex-start;
  }
}

.compact-mode {
  padding: 12px;
}

.compact-mode .sizhu-wrapper {
  padding: 0;
}

.compact-mode .sizhu-grid {
  gap: 8px;
}

.compact-mode .zhu-column {
  padding: 6px;
}

.compact-mode .zhu-label {
  font-size: 11px;
  padding: 3px 8px;
  margin-bottom: 6px;
}

.compact-mode .zhu-body {
  padding: 6px;
  gap: 6px;
}

.compact-mode .tiangan,
.compact-mode .dizhi {
  width: 40px;
  height: 40px;
}

.compact-mode .gan-char {
  font-size: 24px;
}

.compact-mode .zhi-char {
  font-size: 20px;
}

.compact-mode .wuxing-badge {
  font-size: 8px;
  padding: 1px 4px;
}

.compact-mode .shishen-tag {
  font-size: 10px;
  padding: 2px 8px;
  margin-top: 4px;
}

.compact-mode .cang-gan-section,
.compact-mode .wuxing-stats,
.compact-mode .wuxing-xi-ji,
.compact-mode .zhi-relations,
.compact-mode .gan-relations,
.compact-mode .extended-info,
.compact-mode .cang-gan-legend {
  display: none;
}
</style>
