<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { refDebounced } from '@vueuse/core'
import { Calculator, Home, Mail, MapPinned, Package, Satellite, Truck } from '@lucide/vue'
import { computed, reactive, watch } from 'vue'
import { api, unwrap } from '@/api/client'
import { useCiudades } from '@/api/queries'
import BaseButton from '@/components/ui/BaseButton.vue'
import CheckboxInput from '@/components/ui/CheckboxInput.vue'
import SegmentedControl from '@/components/ui/SegmentedControl.vue'
import SelectInput from '@/components/ui/SelectInput.vue'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'
import TextInput from '@/components/ui/TextInput.vue'
import { bsExacto } from '@/lib/format'
import { TIPO_ENVIO } from '@/lib/labels'

const { data: ciudades } = useCiudades({ carga: true })
const form = reactive({ origen: 'Sucre', destino: 'Santa Cruz', peso: '5', tipo: 'auto' as 'auto' | 'sobre' | 'paquete' | 'carga', puerta: false })

const opcionesCiudad = computed(() => (ciudades.value ?? []).map((c) => ({ value: c.nombre, label: c.nombre })))
const destinoConPuerta = computed(() => !!ciudades.value?.find((c) => c.nombre === form.destino)?.tiene_puerta_a_puerta)
watch(destinoConPuerta, (v) => !v && (form.puerta = false))

const parametros = computed(() => ({
  origen: form.origen,
  destino: form.destino,
  peso_kg: Number(String(form.peso).replace(',', '.')),
  tipo: form.tipo === 'auto' ? undefined : form.tipo,
  puerta_a_puerta: form.puerta,
}))
const debounced = refDebounced(parametros, 400)
const valido = computed(() => debounced.value.peso_kg > 0 && debounced.value.origen !== debounced.value.destino)

const cotizacion = useQuery({
  queryKey: computed(() => ['cotizar', debounced.value]),
  queryFn: () => unwrap(api.GET('/api/v1/carga/cotizar', { params: { query: debounced.value } })),
  enabled: valido,
  retry: false,
})

const servicios = [
  { icono: Mail, titulo: 'Sobres y paquetes', texto: 'Hasta 30 kg. Pago en origen o en destino. Cuentas corporativas.' },
  { icono: Satellite, titulo: 'Carga con GPS', texto: 'Más de 30 kg, en furgones con seguimiento satelital. También mudanzas.' },
  { icono: Home, titulo: 'Puerta a puerta', texto: 'Desde 1 kg en Sucre y Santa Cruz: recogemos y entregamos en tu dirección.' },
]
</script>

<template>
  <div>
    <section class="contenedor pt-2">
      <div class="hero px-6 sm:px-10 flex flex-col gap-4 py-10 sm:py-14">
        <span class="hero-chip w-fit">7 ciudades · rastreo en tiempo real</span>
        <h1 class="max-w-2xl text-[34px] leading-tight font-medium tracking-tight sm:text-[44px]">Carga y encomiendas con guía electrónica</h1>
        <p class="max-w-2xl text-on-accent/85">
          Sucre, Camargo, Santa Cruz, Tarija, La Paz, El Alto y Potosí. Cada envío tiene su guía de 8 dígitos y un código de
          retiro para el destinatario.
        </p>
        <div class="flex flex-wrap gap-3 pt-2">
          <BaseButton variant="white" :to="{ name: 'rastreo' }"><MapPinned class="size-4" aria-hidden="true" />Rastrear un envío</BaseButton>
          <BaseButton variant="secondary" :to="{ name: 'puerta-a-puerta' }"><Truck class="size-4" aria-hidden="true" />Pedir recojo a domicilio</BaseButton>
        </div>
      </div>
    </section>

    <div class="contenedor flex flex-col gap-12 py-10">
      <ul class="grid gap-4 md:grid-cols-3">
        <li v-for="s in servicios" :key="s.titulo" class="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
          <span class="flex size-11 items-center justify-center rounded-full bg-accent-soft text-accent-fg"><component :is="s.icono" class="size-5" aria-hidden="true" /></span>
          <h2 class="font-sans text-lg font-medium tracking-tight">{{ s.titulo }}</h2>
          <p class="text-sm text-muted">{{ s.texto }}</p>
        </li>
      </ul>

      <section aria-labelledby="cotizador-titulo" class="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <form class="flex flex-col gap-5 rounded-card border border-line bg-surface p-5 sm:p-6" @submit.prevent>
          <h2 id="cotizador-titulo" class="flex items-center gap-2 text-xl font-medium tracking-tight"><Calculator class="size-5 text-accent-fg" aria-hidden="true" />Cotiza tu envío</h2>
          <div class="grid gap-4 sm:grid-cols-2">
            <SelectInput v-model="form.origen" label="Desde" :options="opcionesCiudad" />
            <SelectInput v-model="form.destino" label="Hasta" :options="opcionesCiudad" />
          </div>
          <div class="grid gap-4 sm:grid-cols-[180px_1fr]">
            <TextInput v-model="form.peso" label="Peso (kg)" inputmode="decimal" placeholder="5" />
            <SegmentedControl
              v-model="form.tipo"
              label="Tipo de envío"
              variant="switch"
              :options="[
                { value: 'auto', label: 'Automático' },
                { value: 'sobre', label: 'Sobre' },
                { value: 'paquete', label: 'Paquete' },
                { value: 'carga', label: 'Carga' },
              ]"
            />
          </div>
          <CheckboxInput
            v-model="form.puerta"
            :disabled="!destinoConPuerta"
            label="Entrega puerta a puerta"
            :hint="destinoConPuerta ? 'Te lo llevamos a la dirección del destinatario.' : 'Disponible solo con destino Sucre o Santa Cruz.'"
          />
          <p v-if="form.origen === form.destino" class="text-sm font-medium text-danger-fg" role="alert">El origen y el destino deben ser distintos.</p>
        </form>

        <div class="flex flex-col gap-4 rounded-card border border-line bg-surface shadow-suave p-6 text-fg" aria-live="polite">
          <span class="text-xs font-medium text-accent-fg">Cotización</span>
          <template v-if="cotizacion.isFetching.value && !cotizacion.data.value">
            <SkeletonBlock class="h-10 w-40" /><SkeletonBlock class="h-24" />
          </template>
          <p v-else-if="cotizacion.isError.value" class="rounded-inner bg-danger-soft p-4 text-sm text-danger-fg" role="alert">
            {{ (cotizacion.error.value as Error).message }}
          </p>
          <template v-else-if="cotizacion.data.value">
            <div>
              <span class="text-[44px] leading-none font-bold tabular">{{ bsExacto(cotizacion.data.value.total_bs) }}</span>
              <p class="mt-1 text-sm text-muted">
                {{ TIPO_ENVIO[cotizacion.data.value.tipo_envio] }} de {{ cotizacion.data.value.peso_kg }} kg ·
                {{ cotizacion.data.value.origen }} → {{ cotizacion.data.value.destino }}
              </p>
            </div>
            <dl class="flex flex-col gap-2 border-t border-line pt-4 text-sm">
              <div class="flex justify-between"><dt class="text-muted">Tarifa base</dt><dd class="tabular">{{ bsExacto(cotizacion.data.value.precio_base_bs) }}</dd></div>
              <div v-if="cotizacion.data.value.kg_adicionales > 0" class="flex justify-between">
                <dt class="text-muted">{{ cotizacion.data.value.kg_adicionales }} kg adicionales × {{ bsExacto(cotizacion.data.value.precio_kg_adicional_bs) }}</dt>
                <dd class="tabular">{{ bsExacto(cotizacion.data.value.cargo_peso_adicional_bs) }}</dd>
              </div>
              <div v-if="cotizacion.data.value.puerta_a_puerta" class="flex justify-between">
                <dt class="text-muted">Puerta a puerta</dt><dd class="tabular">{{ bsExacto(cotizacion.data.value.recargo_puerta_a_puerta_bs) }}</dd>
              </div>
            </dl>
            <p class="text-sm text-muted">Pagas en la bodega de origen o al recoger en destino. Precio referencial sujeto a verificación del peso.</p>
          </template>
          <p v-else class="text-sm text-muted">Completa los datos para ver el precio.</p>
          <BaseButton variant="secondary" class="mt-auto" :to="{ name: 'oficinas' }"><Package class="size-4" aria-hidden="true" />Ver bodegas para enviar</BaseButton>
        </div>
      </section>
    </div>
  </div>
</template>
