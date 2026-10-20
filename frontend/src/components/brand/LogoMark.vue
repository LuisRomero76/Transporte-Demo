<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{ size?: number; wordmark?: boolean; tone?: 'light' | 'dark'; subtitle?: string }>(), {
  size: 36,
  wordmark: true,
  tone: 'light',
})
const degradado = `logo-${useId()}`
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <svg :width="size" :height="size" viewBox="0 0 44 44" aria-hidden="true" class="shrink-0">
      <defs>
        <linearGradient :id="degradado" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="var(--accent)" />
          <stop offset="1" stop-color="var(--accent-2)" />
        </linearGradient>
      </defs>
      <rect width="44" height="44" rx="22" :fill="`url(#${degradado})`" />
      <path d="M11 30 C17 30 18 14 24 14 S31 24 33 24" fill="none" stroke="var(--on-accent)" stroke-width="3" stroke-linecap="round" />
      <circle cx="11" cy="30" r="3.2" fill="var(--ink)" />
      <circle cx="33" cy="24" r="3.2" fill="var(--on-accent)" />
    </svg>
    <span v-if="wordmark" class="flex flex-col leading-tight">
      <span class="text-[16px] font-semibold tracking-tight" :class="tone === 'light' ? 'text-on-accent' : 'text-fg'">TransDemo</span>
      <span v-if="subtitle" class="text-xs" :class="tone === 'light' ? 'text-on-accent/80' : 'text-muted'">{{ subtitle }}</span>
    </span>
  </span>
</template>
