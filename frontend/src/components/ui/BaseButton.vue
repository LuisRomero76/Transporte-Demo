<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import SpinnerIcon from './SpinnerIcon.vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'subtle' | 'white' | 'success'
    size?: 'sm' | 'md' | 'lg'
    type?: 'button' | 'submit' | 'reset'
    to?: RouteLocationRaw
    href?: string
    loading?: boolean
    disabled?: boolean
    block?: boolean
    iconOnly?: boolean
  }>(),
  { variant: 'primary', size: 'md', type: 'button' },
)

const clases = computed(() => {
  const base =
    'relative inline-flex items-center justify-center gap-2 font-medium whitespace-nowrap rounded-full transition-[background-color,color,border-color,opacity] duration-200 select-none disabled:cursor-not-allowed aria-disabled:cursor-not-allowed'
  const tam = {
    sm: props.iconOnly ? 'size-9' : 'h-9 px-3 text-sm',
    md: props.iconOnly ? 'size-11' : 'h-11 px-4 text-[15px]',
    lg: props.iconOnly ? 'size-13' : 'h-13 px-6 text-base',
  }[props.size]
  const variante = {
    primary: 'bg-accent text-white hover:bg-accent-2 disabled:bg-surface-2 disabled:text-muted',
    secondary: 'bg-pill-active text-pill-active-fg hover:opacity-85 disabled:opacity-50',
    outline: 'border border-line-strong bg-surface text-fg hover:bg-surface-2 disabled:opacity-50',
    ghost: 'text-fg hover:bg-surface-2 disabled:opacity-50',
    subtle: 'border border-line bg-surface-2 text-fg hover:border-line-strong disabled:opacity-50',
    danger: 'bg-danger text-white hover:opacity-90 disabled:opacity-50',
    white: 'bg-white text-ink hover:opacity-90',
    success: 'bg-success text-white hover:opacity-90 disabled:opacity-50',
  }[props.variant]
  return [base, tam, variante, props.block ? 'w-full' : ''].join(' ')
})

const inactivo = computed(() => props.disabled || props.loading)
</script>

<template>
  <RouterLink v-if="to && !inactivo" :to="to" :class="clases"><slot /></RouterLink>
  <a v-else-if="href && !inactivo" :href="href" :class="clases" target="_blank" rel="noopener noreferrer"><slot /></a>
  <button v-else :type="type" :class="clases" :disabled="inactivo" :aria-busy="loading || undefined">
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center"><SpinnerIcon class="size-5" /></span>
    <span class="inline-flex items-center gap-2" :class="loading ? 'invisible' : ''"><slot /></span>
  </button>
</template>
