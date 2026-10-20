<script setup lang="ts">
import type { Component } from 'vue'
import SkeletonBlock from './SkeletonBlock.vue'

defineProps<{ label: string; value: string; hint?: string; tone?: 'exito' | 'aviso' | 'neutro'; icon?: Component; loading?: boolean }>()
</script>

<template>
  <div class="flex flex-col gap-1.5 rounded-card border border-line bg-surface p-5 shadow-suave">
    <div class="flex items-center justify-between gap-2 text-[13px] text-muted">
      <span>{{ label }}</span>
      <span v-if="icon" class="grid size-8 shrink-0 place-items-center rounded-full bg-accent-soft text-accent-fg"><component :is="icon" class="size-4" aria-hidden="true" /></span>
    </div>
    <SkeletonBlock v-if="loading" class="h-8 w-32" />
    <span v-else class="text-[28px] leading-tight font-semibold tracking-tight tabular">{{ value }}</span>
    <span
      v-if="hint"
      class="text-[13px] font-medium"
      :class="tone === 'exito' ? 'text-success-fg' : tone === 'aviso' ? 'text-warning-fg' : 'text-muted'"
    >
      {{ hint }}
    </span>
    <slot />
  </div>
</template>
