<script setup lang="ts">
import { usePreferredReducedMotion } from '@vueuse/core'
import { onBeforeUnmount, ref, watch } from 'vue'
import SkeletonBlock from './SkeletonBlock.vue'

/**
 * Tarjeta héroe de acento: el único bloque de color fuerte de la vista.
 * Si `amount` es numérico la cifra cuenta desde 0; `progress` (0-100) dibuja la barra.
 */
const props = defineProps<{
  label: string
  value?: string
  amount?: number
  format?: (n: number) => string
  unit?: string
  aside?: string
  progress?: number
  hint?: string
  loading?: boolean
}>()

const movimiento = usePreferredReducedMotion()
const mostrado = ref(0)
const barra = ref(0)
let marco = 0

function animar(hasta: number): void {
  cancelAnimationFrame(marco)
  if (movimiento.value === 'reduce') {
    mostrado.value = hasta
    return
  }
  const desde = 0
  const inicio = performance.now()
  const paso = (t: number) => {
    const k = Math.min(1, (t - inicio) / 1200)
    mostrado.value = desde + (hasta - desde) * (1 - Math.pow(1 - k, 3))
    if (k < 1) marco = requestAnimationFrame(paso)
  }
  marco = requestAnimationFrame(paso)
}
watch(
  () => [props.amount, props.loading] as const,
  ([a, cargando]) => {
    if (!cargando && typeof a === 'number') animar(a)
  },
  { immediate: true },
)
watch(
  () => [props.progress, props.loading] as const,
  ([p, cargando]) => {
    if (cargando || p == null) return
    requestAnimationFrame(() => (barra.value = Math.max(0, Math.min(100, p))))
  },
  { immediate: true },
)
onBeforeUnmount(() => cancelAnimationFrame(marco))

const texto = (n: number) => (props.format ? props.format(n) : Math.round(n).toLocaleString('es-BO'))
</script>

<template>
  <section class="hero flex flex-col gap-5 p-6">
    <div class="flex items-start justify-between gap-3">
      <span class="hero-chip"><slot name="icon" />{{ label }}</span>
      <span v-if="aside" class="text-[13px] text-on-accent/85">{{ aside }}</span>
    </div>
    <div>
      <SkeletonBlock v-if="loading" class="h-12 w-48 !bg-on-accent/25" />
      <p v-else class="flex items-baseline gap-2">
        <span class="text-[44px] leading-none font-semibold tracking-tight tabular md:text-[52px]">
          {{ typeof amount === 'number' ? texto(mostrado) : value }}
        </span>
        <span v-if="unit" class="text-sm text-on-accent/85">{{ unit }}</span>
      </p>
    </div>
    <div v-if="progress != null" class="hero-progress" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100" :aria-label="label">
      <i :style="{ width: `${barra}%` }" />
    </div>
    <div v-if="hint || $slots.default" class="flex flex-wrap items-center gap-3 text-[13px] text-on-accent/85">
      <slot />
      <span v-if="hint">{{ hint }}</span>
    </div>
  </section>
</template>
