<template>
  <div class="llm-content" v-html="safeHtml"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

interface Props {
  content?: string
}

const props = withDefaults(defineProps<Props>(), {
  content: ''
})

const allowedProtocols = ['http:', 'https:', 'mailto:']

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  // @ts-expect-error: markdown-it supports validateLink but types may miss it
  validateLink: (url: string) => {
    try {
      const u = new URL(url, 'http://x')
      return allowedProtocols.includes(u.protocol)
    } catch {
      return false
    }
  }
})

const defaultLinkOpen = md.renderer.rules.link_open
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const href = tokens[idx].attrGet('href') || ''
  try {
    const u = new URL(href, 'http://x')
    if (!allowedProtocols.includes(u.protocol)) {
      tokens[idx].attrSet('href', '')
    }
  } catch {
    tokens[idx].attrSet('href', '')
  }
  const tIdx = tokens[idx].attrIndex('target')
  if (tIdx < 0) tokens[idx].attrPush(['target', '_blank'])
  else tokens[idx].attrs![tIdx][1] = '_blank'
  const rIdx = tokens[idx].attrIndex('rel')
  const relVal = 'noopener noreferrer nofollow'
  if (rIdx < 0) tokens[idx].attrPush(['rel', relVal])
  else tokens[idx].attrs![rIdx][1] = relVal
  if (defaultLinkOpen) return defaultLinkOpen(tokens, idx, options, env, self)
  return self.renderToken(tokens, idx, options)
}

const defaultImage = md.renderer.rules.image
md.renderer.rules.image = (tokens, idx, options, env, self) => {
  const src = tokens[idx].attrGet('src') || ''
  try {
    const u = new URL(src, 'http://x')
    if (!allowedProtocols.includes(u.protocol)) {
      tokens[idx].attrSet('src', '')
    }
  } catch {
    tokens[idx].attrSet('src', '')
  }
  const lIdx = tokens[idx].attrIndex('loading')
  if (lIdx < 0) tokens[idx].attrPush(['loading', 'lazy'])
  const dIdx = tokens[idx].attrIndex('decoding')
  if (dIdx < 0) tokens[idx].attrPush(['decoding', 'async'])
  const rpIdx = tokens[idx].attrIndex('referrerpolicy')
  if (rpIdx < 0) tokens[idx].attrPush(['referrerpolicy', 'no-referrer'])
  if (defaultImage) return defaultImage(tokens, idx, options, env, self)
  return self.renderToken(tokens, idx, options)
}

const safeHtml = computed(() => md.render(props.content || ''))
</script>

<style scoped>
.llm-content {
  color: #374151;
  line-height: 2;
  font-size: 15px;
  word-break: break-word;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.llm-content :deep(h1),
.llm-content :deep(h2),
.llm-content :deep(h3),
.llm-content :deep(h4),
.llm-content :deep(h5),
.llm-content :deep(h6) {
  color: #1b4332;
  font-weight: 600;
  margin: 20px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.llm-content :deep(h1:first-child),
.llm-content :deep(h2:first-child),
.llm-content :deep(h3:first-child),
.llm-content :deep(h4:first-child),
.llm-content :deep(h5:first-child),
.llm-content :deep(h6:first-child) {
  margin-top: 0;
}

.llm-content :deep(p) {
  margin: 12px 0;
}

.llm-content :deep(ul),
.llm-content :deep(ol) {
  margin: 12px 0;
  padding-left: 2em;
}

.llm-content :deep(li) {
  margin: 8px 0;
  line-height: 1.8;
}
</style>
