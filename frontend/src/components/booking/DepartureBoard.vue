<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { Radio } from '@lucide/vue'
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
const esHoy = (iso: string) => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/La_Paz' }) === hoyISO()
</script>

<template>
  <section class="overflow-hidden rounded-card border border-line bg-surface text-fg shadow-suave" aria-labelledby="tablero-titulo">
    <div class="flex items-center justify-between gap-3 px-5 pt-5 pb-2 sm:px-6">
      <h2 id="tablero-titulo" class="flex items-center gap-2.5 text-lg font-medium tracking-tight">
        <span class="relative flex size-2.5" aria-hidden="true">
          <span class="absolute inline-flex size-full animate-ping rounded-full bg-accent opacity-60" />
          <span class="relative inline-flex size-2.5 rounded-full bg-accent" />
        </span>
        Salidas en vivo
      </h2>
      <span class="flex items-center gap-1.5 rounded-full bg-surface-2 px-2.5 py-1 text-xs text-muted"><Radio class="size-3.5" aria-hidden="true" />Se actualiza cada minuto</span>
    </div>
    <div v-if="isLoading" class="flex flex-col gap-3 p-5">
      <SkeletonBlock v-for="n in 4" :key="n" class="h-10" />
    </div>
    <p v-else-if="isError" class="px-6 py-8 text-sm text-muted">No pudimos cargar el tablero en este momento.</p>
    <p v-else-if="!data?.length" class="px-6 py-8 text-sm text-muted">No hay salidas en las próximas horas.</p>
    <table v-else class="w-full text-sm">
      <caption class="sr-only">Próximas salidas de todas las rutas</caption>
      <thead class="text-left text-xs text-muted">
        <tr>
          <th scope="col" class="px-5 py-2.5 font-medium sm:px-6">Hora</th>
          <th scope="col" class="px-2 py-2.5 font-medium">Ruta</th>
          <th scope="col" class="hidden px-2 py-2.5 font-medium md:table-cell">Andén</th>
          <th scope="col" class="hidden px-2 py-2.5 font-medium sm:table-cell">Libres</th>
          <th scope="col" class="px-5 py-2.5 text-right font-medium sm:px-6">Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in data" :key="s.id" class="border-t border-line">
          <td class="px-5 py-3.5 sm:px-6">
            <span class="text-base font-semibold tabular">{{ hora(s.fecha_hora_salida) }}</span>
            <span v-if="!esHoy(s.fecha_hora_salida)" class="ml-1.5 text-xs text-muted">{{ fechaCorta(s.fecha_hora_salida) }}</span>
          </td>
          <td class="px-2 py-3 font-medium">{{ s.origen }} <span class="text-accent-fg">→</span> {{ s.destino }}</td>
          <td class="hidden px-2 py-3 text-muted md:table-cell">{{ s.anden ?? '—' }}</td>
          <td class="hidden px-2 py-3 text-muted tabular sm:table-cell">{{ libres(s) }}</td>
          <td class="px-5 py-3 text-right sm:px-6"><StatusBadge size="sm" :tono="estado(s).tono" :label="estado(s).label" /></td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
