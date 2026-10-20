<script setup lang="ts">
import { computed } from 'vue'
import type { Tono } from '@/lib/labels'

const props = withDefaults(defineProps<{ tono?: Tono; label: string; dot?: boolean; size?: 'sm' | 'md' }>(), {
  tono: 'neutro',
  dot: true,
  size: 'md',
})

const estilos: Record<Tono, { caja: string; punto: string }> = {
  exito: { caja: 'bg-success-soft text-success-fg', punto: 'bg-success' },
  info: { caja: 'bg-info-soft text-info-fg', punto: 'bg-info' },
  aviso: { caja: 'bg-warning-soft text-warning-fg', punto: 'bg-warning' },
  peligro: { caja: 'bg-danger-soft text-danger-fg', punto: 'bg-danger' },
  neutro: { caja: 'bg-surface-2 text-muted', punto: 'bg-muted' },
  turquesa: { caja: 'bg-info-soft text-info-fg', punto: 'bg-info' },
  noche: { caja: 'bg-pill-active text-pill-active-fg', punto: 'bg-accent' },
  carmin: { caja: 'bg-accent-soft text-accent-fg', punto: 'bg-accent' },
}
const e = computed(() => estilos[props.tono])
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center gap-1.5 rounded-full font-medium whitespace-nowrap"
    :class="[e.caja, size === 'sm' ? 'h-6 px-2 text-xs' : 'h-7 px-2.5 text-[13px]']"
  >
    <span v-if="dot" class="size-2 rounded-full" :class="e.punto" aria-hidden="true" />
    {{ label }}
  </span>
</template>
