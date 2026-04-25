<template>
  <span class="typewriter">
    <span class="text">{{ displayText }}</span>
    <span class="cursor" :class="{ blink: isTyping }">|</span>
  </span>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

const props = defineProps<{
  text: string;
  speed?: number;
}>();

const emit = defineEmits<{
  (e: 'complete'): void;
}>();

const displayText = ref('');
const isTyping = ref(false);
let timer: ReturnType<typeof setInterval> | null = null;

const startTyping = () => {
  isTyping.value = true;
  displayText.value = '';
  let index = 0;
  
  if (timer) {
    clearInterval(timer);
  }
  
  timer = setInterval(() => {
    if (index < props.text.length) {
      displayText.value += props.text[index];
      index++;
    } else {
      clearInterval(timer!);
      timer = null;
      isTyping.value = false;
      emit('complete');
    }
  }, props.speed || 60);
};

watch(() => props.text, startTyping, { immediate: true });

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<style scoped>
.typewriter {
  display: inline;
}

.text {
  white-space: pre-wrap;
}

.cursor {
  color: #66bb6a;
  margin-left: 2px;
}

.cursor.blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
</style>
