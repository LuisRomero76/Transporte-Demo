<script setup lang="ts">
defineProps<{ tabs: { key: string; label: string; count?: number | null }[]; label: string }>()
const activo = defineModel<string>({ required: true })

function mover(e: KeyboardEvent, tabs: { key: string }[]): void {
  const i = tabs.findIndex((t) => t.key === activo.value)
  if (e.key === 'ArrowRight') activo.value = tabs[(i + 1) % tabs.length].key
  else if (e.key === 'ArrowLeft') activo.value = tabs[(i - 1 + tabs.length) % tabs.length].key
  else return
  e.preventDefault()
  ;(e.currentTarget as HTMLElement).querySelector<HTMLElement>('[aria-selected="true"]')?.focus()
}
</script>

<template>
  <div role="tablist" :aria-label="label" class="flex w-fit max-w-full gap-1 overflow-x-auto rounded-full border border-line bg-surface-2 p-1" @keydown="mover($event, tabs)">
    <button
      v-for="t in tabs"
      :key="t.key"
      role="tab"
      type="button"
      :aria-selected="activo === t.key"
      :tabindex="activo === t.key ? 0 : -1"
      class="flex h-9 shrink-0 items-center gap-2 rounded-full px-3.5 text-[13px] font-medium transition-colors"
      :class="activo === t.key ? 'bg-surface text-fg shadow-suave' : 'text-muted hover:text-fg'"
      @click="activo = t.key"
    >
      {{ t.label }}
      <span
v-if="t.count != null" class="rounded-full px-2 py-0.5 text-xs font-medium"
        :class="activo === t.key ? 'bg-accent-soft text-accent-fg' : 'bg-surface text-muted'">{{ t.count }}</span>
    </button>
  </div>
</template>
