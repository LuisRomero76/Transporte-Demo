<script setup lang="ts">
import { useResizeObserver } from '@vueuse/core'
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'

/** Navegación en pastilla con la opción activa invertida; la pastilla se desliza entre opciones. */
const props = defineProps<{ items: { key: string; label: string; to: RouteLocationRaw; active: boolean }[]; label: string }>()

const caja = ref<HTMLElement | null>(null)
const marca = ref({ left: 0, width: 0, visible: false })

function medir(): void {
  const activo = caja.value?.querySelector<HTMLElement>('[data-activo="true"]')
  marca.value = activo ? { left: activo.offsetLeft, width: activo.offsetWidth, visible: true } : { ...marca.value, visible: false }
}
onMounted(medir)
watch(() => props.items.map((i) => i.active).join(), () => nextTick(medir))
useResizeObserver(caja, medir)
</script>

<template>
  <nav :aria-label="label" class="pill-group relative max-w-full overflow-x-auto [scrollbar-width:none]">
    <div ref="caja" class="relative flex gap-1">
      <span
        aria-hidden="true"
        class="absolute inset-y-0 rounded-full bg-pill-active transition-[left,width,opacity] duration-300 ease-[cubic-bezier(.2,.8,.2,1)]"
        :style="{ left: `${marca.left}px`, width: `${marca.width}px`, opacity: marca.visible ? 1 : 0 }"
      />
      <RouterLink
        v-for="i in items"
        :key="i.key"
        :to="i.to"
        :data-activo="i.active"
        :aria-current="i.active ? 'page' : undefined"
        class="relative rounded-full px-3.5 py-2 text-[13px] whitespace-nowrap transition-colors duration-200"
        :class="i.active ? 'text-pill-active-fg' : 'text-muted hover:text-fg'"
      >
        {{ i.label }}
      </RouterLink>
    </div>
  </nav>
</template>
