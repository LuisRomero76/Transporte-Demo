<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(
  defineProps<{ icon: Component; tone?: 'accent' | 'neutro' | 'exito' | 'peligro' | 'aviso' | 'info'; size?: 'sm' | 'md' | 'lg' }>(),
  { tone: 'accent', size: 'md' },
)
const tonos = {
  accent: 'bg-accent-soft text-accent-fg',
  neutro: 'bg-surface-2 text-muted',
  exito: 'bg-success-soft text-success-fg',
  peligro: 'bg-danger-soft text-danger-fg',
  aviso: 'bg-warning-soft text-warning-fg',
  info: 'bg-info-soft text-info-fg',
}
const tamanos = { sm: ['size-7', 'size-3.5'], md: ['size-8', 'size-4'], lg: ['size-11', 'size-5'] }
</script>

<template>
  <span class="grid shrink-0 place-items-center rounded-full" :class="[tonos[tone], tamanos[size][0]]">
    <component :is="icon" :class="tamanos[size][1]" aria-hidden="true" />
  </span>
</template>
