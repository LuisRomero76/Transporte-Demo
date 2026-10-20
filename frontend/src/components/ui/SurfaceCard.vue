<script setup lang="ts">
withDefaults(defineProps<{ title?: string; subtitle?: string; padded?: boolean; as?: string }>(), { padded: true })
</script>

<template>
  <component :is="as ?? 'section'" class="rounded-card border border-line bg-surface text-fg shadow-suave">
    <div v-if="title || $slots.actions" class="flex flex-wrap items-center justify-between gap-3 px-5 pt-5 pb-1 sm:px-6">
      <div class="min-w-0">
        <h2 v-if="title" class="text-base font-medium tracking-tight">{{ title }}</h2>
        <p v-if="subtitle" class="mt-0.5 text-[13px] text-muted">{{ subtitle }}</p>
      </div>
      <div class="flex items-center gap-2"><slot name="actions" /></div>
    </div>
    <div :class="padded === false ? '' : 'p-5 sm:p-6'"><slot /></div>
  </component>
</template>
