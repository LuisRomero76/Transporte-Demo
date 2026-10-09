<script setup lang="ts">
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { CircleAlert, ImageOff, Maximize2, MessageCircleWarning, TriangleAlert } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { API_BASE, ApiError, api, unwrap, type Schemas } from '@/api/client'
import AppDialog from '@/components/ui/AppDialog.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaginationBar from '@/components/ui/PaginationBar.vue'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import TabsBar from '@/components/ui/TabsBar.vue'
import TextArea from '@/components/ui/TextArea.vue'
import { bsExacto, fechaHora, telefono } from '@/lib/format'
import { ESTADO_COMPROBANTE, etiqueta } from '@/lib/labels'
import { useToastStore } from '@/stores/toast'

type Comprobante = Schemas['ComprobanteOut']
type Estado = Schemas['EstadoComprobante']

const avisos = useToastStore()
const cliente = useQueryClient()

const pestana = ref<string>('en_revision')
const offset = ref(0)
const LIMITE = 12
watch(pestana, () => (offset.value = 0))

const lista = useQuery({
  queryKey: computed(() => ['admin-comprobantes', pestana.value, offset.value]),
  queryFn: () =>
    unwrap(
      api.GET('/api/v1/admin/comprobantes', {
        params: {
          query: {
            estado: pestana.value === 'todos' ? undefined : (pestana.value as Estado),
            limit: LIMITE,
            offset: offset.value,
          },
        },
      }),
    ),
  placeholderData: keepPreviousData,
  // Los comprobantes llegan por WhatsApp en cualquier momento; la imagen, segundos después del chat.
  refetchInterval: 30_000,
})

const pestanas = [
  { key: 'en_revision', label: 'Por revisar' },
  { key: 'aprobado', label: 'Aprobados' },
  { key: 'rechazado', label: 'Rechazados' },
  { key: 'todos', label: 'Todos' },
]

const urlImagen = (c: Comprobante) => `${API_BASE}/api/v1/admin/comprobantes/${c.id}/imagen`
const sinVistaPrevia = ref(new Set<string>())
const ampliada = ref<Comprobante | null>(null)

function refrescar() {
  void cliente.invalidateQueries({ queryKey: ['admin-comprobantes'] })
  void cliente.invalidateQueries({ queryKey: ['resumen'] })
}

const aprobando = ref<Comprobante | null>(null)
const aprobar = useMutation({
  mutationFn: (c: Comprobante) =>
    unwrap(api.POST('/api/v1/admin/comprobantes/{comprobante_id}/aprobar', { params: { path: { comprobante_id: c.id } } })),
  onSuccess: (c) => {
    avisos.exito(`Compra ${c.codigo_reserva} confirmada`, 'Le avisamos al cliente por WhatsApp.')
    aprobando.value = null
    refrescar()
  },
  onError: (e) => avisos.error('No se pudo aprobar', e instanceof ApiError ? e.message : undefined),
})

const rechazando = ref<Comprobante | null>(null)
const motivo = ref('')
const MOTIVOS = ['el monto no coincide', 'el pago no llegó a nuestra cuenta', 'la imagen no se lee bien', 'el comprobante es de otra fecha']
const rechazar = useMutation({
  mutationFn: () =>
    unwrap(
      api.POST('/api/v1/admin/comprobantes/{comprobante_id}/rechazar', {
        params: { path: { comprobante_id: rechazando.value!.id } },
        body: { motivo: motivo.value.trim() },
      }),
    ),
  onSuccess: (c) => {
    avisos.exito(`Comprobante de ${c.codigo_reserva} rechazado`, 'El cliente recibió el motivo por WhatsApp.')
    rechazando.value = null
    motivo.value = ''
    refrescar()
  },
  onError: (e) => avisos.error('No se pudo rechazar', e instanceof ApiError ? e.message : undefined),
})
const motivoValido = computed(() => motivo.value.trim().length >= 3)
</script>

<template>
  <div class="flex flex-col gap-6">
    <PageHeader
      title="Pagos por WhatsApp"
      subtitle="Comprobantes de pago por QR enviados al bot. Al aprobar se emiten los boletos; al rechazar, el cliente tiene 1 hora para enviar otro."
    />

    <div class="overflow-hidden rounded-2xl border border-line bg-surface">
      <TabsBar v-model="pestana" :tabs="pestanas" label="Estado de los comprobantes" class="px-3" />

      <ErrorState v-if="lista.isError.value" :error="lista.error.value" class="m-5" @retry="lista.refetch()" />
      <div v-else-if="lista.isLoading.value" class="grid gap-4 p-5 lg:grid-cols-2">
        <SkeletonBlock v-for="i in 4" :key="i" class="h-64 rounded-2xl" />
      </div>
      <EmptyState
        v-else-if="!lista.data.value?.items.length"
        class="py-14"
        title="No hay comprobantes en esta bandeja"
        :text="pestana === 'en_revision' ? 'Cuando un cliente envíe su comprobante por WhatsApp aparecerá aquí.' : undefined"
      />

      <ul v-else class="grid gap-4 p-5 lg:grid-cols-2">
        <li v-for="c in lista.data.value.items" :key="c.id" class="flex flex-col overflow-hidden rounded-2xl border border-line sm:flex-row">
          <!-- Imagen -->
          <div class="relative flex h-56 shrink-0 items-center justify-center overflow-hidden bg-surface-2 sm:h-auto sm:min-h-64 sm:w-44">
            <template v-if="c.tiene_imagen && !sinVistaPrevia.has(c.id)">
              <img
                :src="urlImagen(c)"
                :alt="`Comprobante de la reserva ${c.codigo_reserva}`"
                class="absolute inset-0 size-full object-cover object-top"
                loading="lazy"
                @error="sinVistaPrevia.add(c.id)"
              />
              <button
                type="button"
                class="absolute right-2 bottom-2 inline-flex size-9 items-center justify-center rounded-full bg-noche-900/80 text-white hover:bg-noche-900"
                aria-label="Ver comprobante en grande"
                @click="ampliada = c"
              >
                <Maximize2 class="size-4" aria-hidden="true" />
              </button>
            </template>
            <a v-else-if="c.tiene_imagen" :href="urlImagen(c)" target="_blank" rel="noopener" class="px-4 text-center text-sm font-semibold underline">
              Abrir archivo
            </a>
            <p v-else class="flex flex-col items-center gap-2 px-4 text-center text-xs text-muted">
              <ImageOff class="size-6" aria-hidden="true" />
              La imagen llega unos segundos después de que termina el chat.
            </p>
          </div>

          <!-- Datos -->
          <div class="flex min-w-0 flex-1 flex-col gap-3 p-4">
            <div class="flex flex-wrap items-center gap-2">
              <span class="codigo text-lg">{{ c.codigo_reserva }}</span>
              <StatusBadge size="sm" v-bind="etiqueta(ESTADO_COMPROBANTE, c.estado)" />
              <StatusBadge v-if="c.estado === 'en_revision' && c.salida_proxima" size="sm" tono="peligro" label="Sale pronto" />
            </div>
            <p class="text-sm">
              <strong>{{ c.comprador }}</strong>
              <span v-if="c.telefono" class="text-muted"> · {{ telefono(c.telefono) }}</span>
              <span class="block text-muted">{{ c.viaje }} · {{ fechaHora(c.fecha_hora_salida) }} · {{ c.boletos }} pasaje(s)</span>
            </p>

            <dl class="grid grid-cols-2 gap-x-3 gap-y-1.5 rounded-xl bg-canvas p-3 text-[13px]">
              <dt class="text-muted">Total de la reserva</dt>
              <dd class="text-right font-bold tabular">{{ bsExacto(c.total_bs) }}</dd>
              <dt class="text-muted">Monto leído</dt>
              <dd class="text-right tabular" :class="c.monto_coincide ? 'text-exito-800' : 'font-bold text-peligro-600'">
                {{ c.monto_leido_bs != null ? bsExacto(c.monto_leido_bs) : '—' }}
              </dd>
              <dt class="text-muted">N.º de transacción</dt>
              <dd class="truncate text-right font-mono" :title="c.numero_transaccion ?? ''">{{ c.numero_transaccion ?? '—' }}</dd>
              <dt class="text-muted">Fecha · banco</dt>
              <dd class="truncate text-right">{{ [c.fecha_leida, c.banco].filter(Boolean).join(' · ') || '—' }}</dd>
            </dl>

            <p v-if="c.transaccion_repetida" class="flex items-start gap-1.5 text-[13px] font-semibold text-peligro-600">
              <TriangleAlert class="mt-0.5 size-4 shrink-0" aria-hidden="true" /> Este número de transacción aparece en otro comprobante.
            </p>
            <p v-if="c.motivo_rechazo" class="text-[13px] text-muted">Motivo del rechazo: {{ c.motivo_rechazo }}</p>
            <p v-if="c.notificacion_error" class="flex items-start gap-1.5 text-[13px] text-aviso-700">
              <MessageCircleWarning class="mt-0.5 size-4 shrink-0" aria-hidden="true" /> No se pudo avisar al cliente por WhatsApp.
            </p>

            <div class="mt-auto flex items-center justify-between gap-2 pt-1">
              <span class="text-xs text-muted">{{ c.revisado_at ? `Revisado ${fechaHora(c.revisado_at)}` : `Recibido ${fechaHora(c.created_at)}` }}</span>
              <div v-if="c.estado === 'en_revision'" class="flex gap-2">
                <BaseButton size="sm" variant="subtle" @click="rechazando = c">Rechazar</BaseButton>
                <BaseButton size="sm" variant="success" @click="aprobando = c">Aprobar</BaseButton>
              </div>
            </div>
          </div>
        </li>
      </ul>

      <PaginationBar v-if="lista.data.value?.total" v-model:offset="offset" :total="lista.data.value.total" :limit="LIMITE" />
    </div>

    <AppDialog :open="!!ampliada" size="lg" :title="`Comprobante · ${ampliada?.codigo_reserva ?? ''}`" @update:open="(v) => !v && (ampliada = null)">
      <img v-if="ampliada" :src="urlImagen(ampliada)" :alt="`Comprobante de la reserva ${ampliada.codigo_reserva}`" class="mx-auto max-h-[75vh] rounded-xl" />
    </AppDialog>

    <ConfirmDialog
      :open="!!aprobando"
      title="Aprobar pago"
      :description="aprobando ? `${aprobando.codigo_reserva} · ${aprobando.comprador} · ${bsExacto(aprobando.total_bs)}` : ''"
      confirm-label="Aprobar y emitir boletos"
      :loading="aprobar.isPending.value"
      @update:open="(v) => !v && (aprobando = null)"
      @confirm="aprobando && aprobar.mutate(aprobando)"
    >
      <p class="flex items-start gap-2 text-sm text-muted">
        <CircleAlert class="mt-0.5 size-4 shrink-0" aria-hidden="true" />
        Confirma en el banco que el dinero llegó a la cuenta. El cliente recibirá «Compra confirmada» por WhatsApp.
      </p>
    </ConfirmDialog>

    <ConfirmDialog
      :open="!!rechazando"
      title="Rechazar comprobante"
      :description="rechazando ? `${rechazando.codigo_reserva} · ${rechazando.comprador}` : ''"
      confirm-label="Rechazar y avisar"
      danger
      :loading="rechazar.isPending.value"
      @update:open="(v) => !v && ((rechazando = null), (motivo = ''))"
      @confirm="motivoValido ? rechazar.mutate() : avisos.error('Indica el motivo del rechazo')"
    >
      <div class="flex flex-col gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="m in MOTIVOS"
            :key="m"
            type="button"
            class="rounded-full border border-line-strong px-3 py-1 text-xs hover:border-noche-400"
            :class="motivo === m ? 'border-carmin-600 bg-carmin-50' : ''"
            @click="motivo = m"
          >
            {{ m }}
          </button>
        </div>
        <TextArea v-model="motivo" label="Motivo (se le envía al cliente)" :rows="2" maxlength="200" />
      </div>
    </ConfirmDialog>
  </div>
</template>
