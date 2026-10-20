<script setup lang="ts">
defineProps<{
  id: string
  label?: string
  hint?: string
  error?: string | null
  required?: boolean
}>()
</script>

<template>
  <div class="flex min-w-0 flex-col gap-1.5">
    <label v-if="label" :for="id" class="text-[13px] font-medium text-fg">
      {{ label }}<span v-if="required" class="text-accent-fg" aria-hidden="true"> *</span>
    </label>
    <slot :describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined" :invalid="!!error" />
    <p v-if="error" :id="`${id}-error`" class="text-[13px] font-medium text-danger-fg" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="`${id}-hint`" class="text-[13px] text-muted">{{ hint }}</p>
  </div>
</template>
