<script setup lang="ts" generic="T extends string | number">
import { useId } from 'vue'

defineProps<{
  options: { value: T; label: string; hint?: string; disabled?: boolean }[]
  label: string
  /** "pills": tarjetas seleccionables; "switch": control compacto de fondo gris */
  variant?: 'pills' | 'switch'
  hideLabel?: boolean
}>()
const modelo = defineModel<T>()
const nombre = useId()
</script>

<template>
  <fieldset class="m-0 min-w-0 border-0 p-0">
    <legend class="mb-2 text-[13px] font-semibold" :class="hideLabel ? 'sr-only' : ''">{{ label }}</legend>
    <div
      v-if="variant === 'switch'"
      class="flex rounded-full border border-line bg-surface-2 p-1"
    >
      <label
        v-for="o in options"
        :key="o.value"
        class="flex h-9 flex-1 cursor-pointer items-center justify-center rounded-full px-3.5 text-[13px] font-medium whitespace-nowrap transition-colors has-focus-visible:outline-2 has-focus-visible:outline-accent"
        :class="modelo === o.value ? 'bg-surface text-fg shadow-suave' : 'text-muted hover:text-fg'"
      >
        <input v-model="modelo" class="sr-only" type="radio" :name="nombre" :value="o.value" :disabled="o.disabled" />
        {{ o.label }}
      </label>
    </div>
    <div v-else class="flex flex-wrap gap-2">
      <label
        v-for="o in options"
        :key="o.value"
        class="flex min-h-11 cursor-pointer items-center gap-2.5 rounded-inner border px-4 py-2 text-sm transition-colors has-focus-visible:outline-2 has-focus-visible:outline-accent"
        :class="[
          modelo === o.value
            ? 'border-accent-line bg-accent-soft font-medium text-fg'
            : 'border-line bg-surface hover:border-line-strong',
          o.disabled ? 'cursor-not-allowed opacity-50' : '',
        ]"
      >
        <input v-model="modelo" class="size-4 accent-(--accent)" type="radio" :name="nombre" :value="o.value" :disabled="o.disabled" />
        <span class="flex flex-col leading-tight">
          <span>{{ o.label }}</span>
          <span v-if="o.hint" class="text-xs font-normal text-muted">{{ o.hint }}</span>
        </span>
      </label>
    </div>
  </fieldset>
</template>
