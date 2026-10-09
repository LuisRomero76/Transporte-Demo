<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { CircleCheck, Clock, FileSearch, TriangleAlert } from '@lucide/vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { api, unwrap } from '@/api/client'
import LogoMark from '@/components/brand/LogoMark.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import QrCode from '@/components/ui/QrCode.vue'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'
import { useCuentaRegresiva } from '@/composables/useCuentaRegresiva'
import { bsExacto, fechaHora, hora } from '@/lib/format'

const route = useRoute()
const codigo = computed(() => String(route.params.codigo ?? '').toUpperCase())

const pago = useQuery({
  queryKey: computed(() => ['pago-qr', codigo.value]),
  queryFn: () => unwrap(api.GET('/api/v1/reservas/{codigo}/pago-qr', { params: { path: { codigo: codigo.value } } })),
  // Refresca para mostrar el cambio a «en revisión» o «pagada» sin recargar.
  refetchInterval: 30_000,
})

const datos = computed(() => pago.data.value)
const { texto: restante, vencido } = useCuentaRegresiva(computed(() => datos.value?.expira_at ?? null))
const pendiente = computed(() => datos.value?.estado === 'pendiente_pago' && !datos.value.en_revision && !vencido.value)
</script>

<template>
  <section class="mx-auto flex w-full max-w-md flex-col gap-5 px-4 py-10">
    <ErrorState v-if="pago.isError.value" :error="pago.error.value" @retry="pago.refetch()" />
    <SkeletonBlock v-else-if="pago.isLoading.value" class="h-[540px] rounded-3xl" />

    <template v-else-if="datos">
      <article class="overflow-hidden rounded-3xl border border-line bg-surface shadow-suave">
        <header class="flex items-center justify-between bg-noche-900 px-5 py-4 text-white">
          <LogoMark :size="30" subtitle="Cobro QR" />
          <span class="rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-bold tracking-wider">DEMO</span>
        </header>

        <div class="flex flex-col items-center gap-4 px-6 py-6 text-center">
          <template v-if="pendiente && datos.qr_payload">
            <p class="text-sm text-muted">Escanea con la app de tu banco</p>
            <QrCode :value="datos.qr_payload" :size="220" label="Código QR para pagar la reserva" />
            <p class="font-display text-4xl font-bold tabular">{{ bsExacto(datos.total_bs) }}</p>
            <p class="flex items-center gap-1.5 text-sm font-semibold text-carmin-700">
              <Clock class="size-4" aria-hidden="true" /> Vence en {{ restante }} · a las {{ hora(datos.expira_at) }}
            </p>
          </template>

          <div v-else-if="datos.en_revision" class="flex flex-col items-center gap-3 py-6">
            <FileSearch class="size-12 text-info-600" aria-hidden="true" />
            <h1 class="text-xl font-bold">Comprobante en revisión</h1>
            <p class="text-sm text-muted">Te avisaremos por WhatsApp cuando confirmemos tu compra.</p>
          </div>

          <div v-else-if="datos.estado === 'pagada'" class="flex flex-col items-center gap-3 py-6">
            <CircleCheck class="size-12 text-exito-600" aria-hidden="true" />
            <h1 class="text-xl font-bold">Compra confirmada</h1>
            <p class="text-sm text-muted">Presenta tu carnet al abordar. ¡Buen viaje!</p>
          </div>

          <div v-else class="flex flex-col items-center gap-3 py-6">
            <TriangleAlert class="size-12 text-aviso-600" aria-hidden="true" />
            <h1 class="text-xl font-bold">Esta reserva ya no se puede pagar</h1>
            <p class="text-sm text-muted">El plazo venció y los asientos se liberaron. Escríbenos por WhatsApp para reservar de nuevo.</p>
          </div>

          <dl class="grid w-full grid-cols-2 gap-x-4 gap-y-2 rounded-2xl bg-canvas p-4 text-left text-sm">
            <dt class="text-muted">Reserva</dt>
            <dd class="codigo text-right">{{ datos.codigo_reserva }}</dd>
            <dt class="text-muted">Viaje</dt>
            <dd class="text-right font-semibold">{{ datos.origen }} → {{ datos.destino }}</dd>
            <dt class="text-muted">Salida</dt>
            <dd class="text-right">{{ fechaHora(datos.fecha_hora_salida) }}</dd>
            <dt class="text-muted">Pasajes</dt>
            <dd class="text-right">{{ datos.boletos }}</dd>
          </dl>
        </div>
      </article>

      <ol v-if="pendiente" class="flex list-decimal flex-col gap-2 rounded-2xl border border-line bg-surface p-5 pl-10 text-sm text-muted">
        <li>Abre la app de tu banco y elige «Pagar con QR».</li>
        <li>Escanea el código y paga exactamente {{ bsExacto(datos.total_bs) }}.</li>
        <li>Envía la foto del comprobante por el mismo chat de WhatsApp.</li>
      </ol>
      <p class="text-center text-xs text-muted">Página de demostración: este QR no corresponde a ninguna cuenta bancaria.</p>
    </template>
  </section>
</template>
