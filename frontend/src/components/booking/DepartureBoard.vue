<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { ArrowRight, Radio } from '@lucide/vue'
import { RouterLink } from 'vue-router'
import { api, unwrap } from '@/api/client'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { fechaCorta, hora, hoyISO } from '@/lib/format'
import { ESTADO_SALIDA, etiqueta } from '@/lib/labels'

const { data, isLoading, isError } = useQuery({
  queryKey: ['salidas-proximas'],
  queryFn: () => unwrap(api.GET('/api/v1/salidas/proximas', { params: { query: { limite: 8 } } })),
  refetchInterval: 60_000,
})

function estado(s: { estado: string; minutos_demora: number }) {
  const e = etiqueta(ESTADO_SALIDA, s.estado)
  return s.estado === 'demorada' ? { ...e, label: `+${s.minutos_demora} min` } : e
}
const libres = (s: { clases: { asientos_libres: number }[] }) => s.clases.reduce((t, c) => t + c.asientos_libres, 0)
const diaISO = (iso: string) => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/La_Paz' })
const esHoy = (iso: string) => diaISO(iso) === hoyISO()
// Cada salida lleva a la búsqueda de pasajes de esa ruta y ese día.
const buscar = (s: { origen: string; destino: string; fecha_hora_salida: string }) => ({
  name: 'resultados',
  query: { origen: s.origen, destino: s.destino, fecha: diaISO(s.fecha_hora_salida), pasajeros: '1' },
})
</script>

<template>
  <section class="flex flex-col gap-5" aria-labelledby="tablero-titulo">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 id="tablero-titulo" class="flex items-center gap-3 text-[28px] font-medium tracking-tight sm:text-[30px]">
          <span class="relative flex size-3" aria-hidden="true">
            <span class="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-60" />
            <span class="relative inline-flex size-3 rounded-full bg-accent" />
          </span>
          Salidas en vivo
        </h2>
        <p class="mt-1 text-muted">Elige una salida y compra tu pasaje en minutos.</p>
      </div>
      <span class="flex items-center gap-1.5 rounded-full bg-surface px-3 py-1.5 text-xs text-muted"><Radio class="size-3.5" aria-hidden="true" />Se actualiza cada minuto</span>
    </div>
    <div v-if="isLoading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <SkeletonBlock v-for="n in 4" :key="n" class="h-40 rounded-card" />
    </div>
    <p v-else-if="isError" class="rounded-card border border-line bg-surface px-6 py-8 text-sm text-muted">No pudimos cargar las salidas en este momento.</p>
    <p v-else-if="!data?.length" class="rounded-card border border-line bg-surface px-6 py-8 text-sm text-muted">No hay salidas en las próximas horas.</p>
    <ul v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <li v-for="s in data" :key="s.id" class="flex flex-col gap-4 rounded-card border border-line bg-surface p-5 shadow-suave">
        <div class="flex items-start justify-between gap-2">
          <div>
            <span class="text-[28px] leading-none font-semibold tracking-tight tabular">{{ hora(s.fecha_hora_salida) }}</span>
            <span class="mt-1 block text-xs text-muted">{{ esHoy(s.fecha_hora_salida) ? 'Hoy' : fechaCorta(s.fecha_hora_salida) }}</span>
          </div>
          <StatusBadge size="sm" :tono="estado(s).tono" :label="estado(s).label" />
        </div>
        <p class="font-medium">{{ s.origen }} <span class="text-accent-fg">→</span> {{ s.destino }}</p>
        <div class="mt-auto flex items-center justify-between gap-2 border-t border-line pt-3 text-[13px] text-muted">
          <span>{{ libres(s) }} asientos libres<template v-if="s.anden"> · Andén {{ s.anden }}</template></span>
          <RouterLink v-if="libres(s) > 0" :to="buscar(s)" class="flex shrink-0 items-center gap-1 font-medium text-accent-fg hover:underline">
            Comprar <ArrowRight class="size-3.5" aria-hidden="true" />
          </RouterLink>
        </div>
      </li>
    </ul>
  </section>
</template>
