<template>
  <div class="coin-toss-container">
    <div class="coins-display">
      <div
        v-for="(coin, index) in coins"
        :key="index"
        :class="['coin', { flipping: isFlipping, 'coin-heads': coin === 1, 'coin-tails': coin === 0 }]"
      >
        <div class="coin-face coin-front">
          <span class="coin-text">正</span>
        </div>
        <div class="coin-face coin-back">
          <span class="coin-text">反</span>
        </div>
      </div>
    </div>
    
    <div v-if="!disabled && !hasResult" class="coin-controls">
      <el-button
        type="primary"
        :loading="isFlipping"
        :disabled="isFlipping"
        @click="handleToss"
        class="toss-button"
      >
        {{ isFlipping ? '摇卦中...' : '摇卦' }}
      </el-button>
    </div>
    
    <div v-if="hasResult" class="result-display">
      <div class="yao-result">
        <span class="yao-symbol">{{ yaoSymbol }}</span>
        <span class="yao-description">{{ yaoDescription }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

interface Props {
  disabled?: boolean;
  initialResult?: [number, number, number];
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  initialResult: undefined,
});

const emit = defineEmits<{
  (e: 'result', result: { coins: [number, number, number], yaoType: string, yaoNumber: number }): void;
}>();

const coins = ref<[number, number, number]>([0, 0, 0]);
const isFlipping = ref(false);
const hasResult = ref(false);

// 如果提供了初始结果，直接使用
watch(() => props.initialResult, (newVal) => {
  if (newVal) {
    coins.value = newVal;
    hasResult.value = true;
    calculateYao();
  }
}, { immediate: true });

const yaoSymbol = ref('');
const yaoDescription = ref('');

// 计算爻信息
function calculateYao() {
  const headsCount = coins.value.reduce((sum, coin) => sum + coin, 0);
  
  if (headsCount === 3) {
    // 三正：老阳（动爻，记为9）
    yaoSymbol.value = '⚊';
    yaoDescription.value = '老阳（动爻）';
    emit('result', { coins: coins.value, yaoType: '老阳', yaoNumber: 9 });
  } else if (headsCount === 0) {
    // 三反：老阴（动爻，记为6）
    yaoSymbol.value = '⚋';
    yaoDescription.value = '老阴（动爻）';
    emit('result', { coins: coins.value, yaoType: '老阴', yaoNumber: 6 });
  } else if (headsCount === 2) {
    // 两正一反：少阳（静爻，记为7）
    yaoSymbol.value = '⚊';
    yaoDescription.value = '少阳（静爻）';
    emit('result', { coins: coins.value, yaoType: '少阳', yaoNumber: 7 });
  } else {
    // 两反一正：少阴（静爻，记为8）
    yaoSymbol.value = '⚋';
    yaoDescription.value = '少阴（静爻）';
    emit('result', { coins: coins.value, yaoType: '少阴', yaoNumber: 8 });
  }
}

// 摇卦处理
function handleToss() {
  if (isFlipping.value || props.disabled) return;
  
  isFlipping.value = true;
  hasResult.value = false;
  
  // 动画持续时间1.5秒
  setTimeout(() => {
    // 随机生成3枚铜钱的结果（0=反面，1=正面）
    const result: [number, number, number] = [
      Math.random() < 0.5 ? 0 : 1,
      Math.random() < 0.5 ? 0 : 1,
      Math.random() < 0.5 ? 0 : 1,
    ];
    
    coins.value = result;
    isFlipping.value = false;
    hasResult.value = true;
    calculateYao();
  }, 1500);
}

// 重置
function reset() {
  coins.value = [0, 0, 0];
  isFlipping.value = false;
  hasResult.value = false;
  yaoSymbol.value = '';
  yaoDescription.value = '';
}

defineExpose({ reset });
</script>

<style scoped>
.coin-toss-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.coins-display {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
}

.coin {
  width: 70px;
  height: 70px;
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  cursor: pointer;
}

.coin.flipping {
  animation: coinFlip3D 1.8s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 3D翻转动画 - 多轴旋转 */
@keyframes coinFlip3D {
  0% {
    transform: rotateY(0deg) rotateX(0deg) rotateZ(0deg);
  }
  25% {
    transform: rotateY(180deg) rotateX(45deg) rotateZ(90deg) translateZ(20px);
  }
  50% {
    transform: rotateY(360deg) rotateX(90deg) rotateZ(180deg) translateZ(30px);
  }
  75% {
    transform: rotateY(540deg) rotateX(45deg) rotateZ(270deg) translateZ(20px);
  }
  100% {
    transform: rotateY(720deg) rotateX(0deg) rotateZ(360deg) translateZ(0px);
  }
}

.coin:hover:not(.flipping) {
  transform: translateY(-8px) rotateY(15deg) scale(1.1);
  filter: drop-shadow(0 10px 20px rgba(139, 92, 246, 0.4));
}

.coin-face {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backface-visibility: hidden;
  border: 3px solid;
  font-weight: 900;
  font-size: 22px;
  box-shadow: 
    inset 0 -8px 16px rgba(0, 0, 0, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

.coin-front {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
  border-color: #d97706;
  color: #78350f;
  text-shadow: 0 2px 4px rgba(120, 53, 15, 0.3);
}

.coin-back {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 50%, #4b5563 100%);
  border-color: #4b5563;
  color: #f3f4f6;
  transform: rotateY(180deg);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.coin-text {
  user-select: none;
}

.coin-controls {
  display: flex;
  justify-content: center;
}

.toss-button {
  min-width: 120px;
  height: 40px;
}

.result-display {
  text-align: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(245, 158, 11, 0.15) 100%);
  border-radius: 16px;
  min-width: 220px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  animation: resultPulse 2s ease-in-out infinite;
}

@keyframes resultPulse {
  0%, 100% {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 0 20px rgba(139, 92, 246, 0.2);
  }
  50% {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 0 40px rgba(139, 92, 246, 0.4);
  }
}

.yao-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.yao-symbol {
  font-size: 42px;
  font-weight: 900;
  background: linear-gradient(135deg, #8b5cf6 0%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(139, 92, 246, 0.5);
  animation: symbolGlow 3s ease-in-out infinite;
  display: inline-block;
}

@keyframes symbolGlow {
  0%, 100% {
    filter: brightness(1) drop-shadow(0 0 10px rgba(139, 92, 246, 0.5));
  }
  50% {
    filter: brightness(1.3) drop-shadow(0 0 20px rgba(139, 92, 246, 0.8));
  }
}

.yao-description {
  font-size: 14px;
  color: #9ca3af;
}
</style>


