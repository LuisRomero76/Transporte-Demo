<script setup lang="ts">
import {
  ArrowRight,
  BadgePercent,
  Bed,
  Home,
  Package,
  PackageSearch,
  ReceiptText,
  RotateCcw,
  ShieldCheck,
  Ticket,
  TicketCheck,
  Truck,
} from '@lucide/vue'
import { useQuery } from '@tanstack/vue-query'
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, unwrap } from '@/api/client'
import { useRutas, useTiposAsiento } from '@/api/queries'
import DepartureBoard from '@/components/booking/DepartureBoard.vue'
import TripSearchForm from '@/components/booking/TripSearchForm.vue'
import RouteMapArt from '@/components/brand/RouteMapArt.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'
import TextInput from '@/components/ui/TextInput.vue'
import { bs, duracion, hoyISO, sumarDias } from '@/lib/format'

const router = useRouter()
const pestana = ref<'pasajes' | 'rastreo' | 'reserva'>('pasajes')
const guia = ref('')
const codigo = ref('')
const documento = ref('')

const { data: rutas, isLoading: cargandoRutas } = useRutas()
const { data: tipos } = useTiposAsiento()
const { data: faqs } = useQuery({ queryKey: ['faqs'], queryFn: () => unwrap(api.GET('/api/v1/faqs')) })

const rutasDesdeSucre = computed(() => (rutas.value ?? []).filter((r) => r.origen === 'Sucre'))
const destacadas = computed(() => (faqs.value ?? []).flatMap((c) => c.preguntas).slice(0, 4))

function rastrear(): void {
  const limpia = guia.value.replace(/\D/g, '')
  if (limpia) void router.push({ name: 'rastreo', params: { guia: limpia } })
}
function verReserva(): void {
  if (!codigo.value.trim() || !documento.value.trim()) return
  // El documento viaja en el estado del historial, no en la URL.
  void router.push({ name: 'mi-reserva', query: { codigo: codigo.value.trim().toUpperCase() }, state: { documento: documento.value.trim() } })
}
function buscarRuta(origen: string, destino: string): void {
  void router.push({ name: 'resultados', query: { origen, destino, fecha: sumarDias(hoyISO(), 1), pasajeros: '1' } })
}

const pestanas = [
  { key: 'pasajes', label: 'Pasajes de bus' },
  { key: 'rastreo', label: 'Rastrear envío' },
  { key: 'reserva', label: 'Mi reserva' },
] as const

// Accesos directos del cliente: cada uno lleva a una sección que ya existe.
const accesos = [
  { icono: Ticket, titulo: 'Comprar pasaje', texto: 'Busca tu salida y elige tu asiento', to: { name: 'inicio', hash: '#buscador' } },
  { icono: TicketCheck, titulo: 'Mi reserva', texto: 'Consulta, paga o descarga tu e-ticket', to: { name: 'mi-reserva' } },
  { icono: PackageSearch, titulo: 'Rastrear envío', texto: 'Sigue tu encomienda con la guía', to: { name: 'rastreo' } },
  { icono: Package, titulo: 'Enviar encomienda', texto: 'Cotiza y envía a 7 ciudades', to: { name: 'carga' } },
]

const ventajas = [
  { icono: ReceiptText, titulo: 'Tu e-ticket es tu factura', texto: 'Recíbelo al instante y muéstralo desde tu celular.' },
  { icono: ShieldCheck, titulo: 'Pago 100 % seguro', texto: 'QR de bancos bolivianos, tarjeta Visa o Mastercard y Tigo Money.' },
  { icono: RotateCcw, titulo: 'Reembolso del 85 %', texto: 'Si cambias de planes, hasta 2 horas antes de la salida.' },
  { icono: Home, titulo: 'Puerta a puerta', texto: 'Recogemos y entregamos tus envíos en Sucre y Santa Cruz.' },
]
</script>

<template>
  <div>
    <section>
      <div class="hero rounded-none!">
      <div class="contenedor grid items-center gap-10 pt-12 pb-44 sm:pb-40 lg:grid-cols-[1.1fr_1fr] lg:pt-16 lg:pb-36">
        <div class="relative flex flex-col gap-5">
          <span class="hero-chip w-fit sm:text-[13px]">Sucre · Santa Cruz · Tarija · La Paz</span>
          <h1 class="text-[40px] leading-[1.05] font-semibold tracking-tight sm:text-5xl lg:text-[56px]">Viaja de noche,<br />llega descansado.</h1>
          <p class="max-w-xl text-base leading-relaxed text-on-accent/85 sm:text-lg">
            Buses de dos pisos con asientos que se reclinan hasta 180°. Compra en línea en minutos y paga con QR, tarjeta o Tigo
            Money.
          </p>
          <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-on-accent/85">
            <span class="flex items-center gap-2"><ShieldCheck class="size-4.5" aria-hidden="true" />Regulada por la ATT</span>
            <span class="flex items-center gap-2"><Bed class="size-4.5" aria-hidden="true" />Suite Cama 180°</span>
          </div>
        </div>
        <div class="relative hidden lg:block"><RouteMapArt /></div>
      </div>
      </div>

      <div id="buscador" class="contenedor relative -mt-36 scroll-mt-24 sm:-mt-32 lg:-mt-28">
        <div class="rounded-card border border-line bg-surface p-4 pb-5 text-fg shadow-flotante sm:p-5">
          <div role="tablist" aria-label="¿Qué quieres hacer?" class="mb-4 flex w-fit max-w-full gap-1 overflow-x-auto rounded-full border border-line bg-surface-2 p-1">
            <button
              v-for="p in pestanas"
              :key="p.key"
              role="tab"
              :aria-selected="pestana === p.key"
              class="h-10 shrink-0 rounded-full px-4 text-sm font-medium transition-colors"
              :class="pestana === p.key ? 'bg-surface text-fg shadow-suave' : 'text-muted hover:text-fg'"
              @click="pestana = p.key"
            >
              {{ p.label }}
            </button>
          </div>
          <TripSearchForm v-if="pestana === 'pasajes'" />
          <form v-else-if="pestana === 'rastreo'" class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="rastrear">
            <TextInput v-model="guia" label="Número de guía" placeholder="8 dígitos, p. ej. 26000101" inputmode="numeric" mono size="lg" class="flex-1" maxlength="12" />
            <BaseButton type="submit" size="lg" class="h-14">Rastrear envío</BaseButton>
          </form>
          <form v-else class="flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="verReserva">
            <TextInput v-model="codigo" label="Código de reserva" placeholder="MX7K2P" mono size="lg" class="flex-1" maxlength="8" autocomplete="off" />
            <TextInput v-model="documento" label="Documento del comprador o pasajero" placeholder="CI" size="lg" class="flex-1" autocomplete="off" />
            <BaseButton type="submit" size="lg" class="h-14">Ver mi reserva</BaseButton>
          </form>
        </div>
      </div>
    </section>

    <nav aria-label="Accesos directos" class="contenedor mt-8">
      <ul class="entrada grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
        <li v-for="a in accesos" :key="a.titulo">
          <RouterLink
            :to="a.to"
            class="group flex h-full items-center gap-4 rounded-card border border-line bg-surface p-4 shadow-suave transition-colors hover:border-accent-line sm:p-5"
            @click="a.to.name === 'inicio' && (pestana = 'pasajes')"
          >
            <span class="grid size-12 shrink-0 place-items-center rounded-full bg-accent-soft text-accent-fg">
              <component :is="a.icono" class="size-5" aria-hidden="true" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block font-medium">{{ a.titulo }}</span>
              <span class="hidden text-[13px] text-muted sm:block">{{ a.texto }}</span>
            </span>
            <ArrowRight class="hidden size-4 shrink-0 text-muted transition-transform group-hover:translate-x-0.5 group-hover:text-accent-fg sm:block" aria-hidden="true" />
          </RouterLink>
        </li>
      </ul>
    </nav>

    <div class="contenedor flex flex-col gap-16 pt-16">
      <DepartureBoard />

      <section aria-labelledby="rutas-titulo" class="flex flex-col gap-6">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="rutas-titulo" class="text-[28px] font-medium tracking-tight text-fg sm:text-[30px]">Rutas y horarios</h2>
            <p class="mt-1 text-muted">Salidas todas las noches desde y hacia Sucre.</p>
          </div>
          <RouterLink :to="{ name: 'rutas' }" class="flex items-center gap-1 font-semibold text-accent-fg hover:underline">
            Ver itinerarios <ArrowRight class="size-4" aria-hidden="true" />
          </RouterLink>
        </div>
        <div class="grid gap-5 md:grid-cols-3">
          <template v-if="cargandoRutas"><SkeletonBlock v-for="n in 3" :key="n" class="h-48 rounded-card" /></template>
          <article v-for="r in rutasDesdeSucre" v-else :key="r.id" class="group flex flex-col gap-4 rounded-card border border-line bg-surface p-6 transition shadow-suave hover:-translate-y-0.5 hover:border-line-strong">
            <h3 class="flex items-center gap-3 text-xl font-semibold text-fg">
              {{ r.origen }} <ArrowRight class="size-5 text-accent-fg" aria-hidden="true" /> {{ r.destino }}
            </h3>
            <p class="flex flex-wrap gap-x-5 gap-y-1 text-sm text-muted">
              <span>{{ r.distancia_km }} km</span><span>{{ duracion(r.duracion_estimada_min) }}</span>
              <span v-if="r.horarios?.length">Salidas {{ r.horarios.join(' · ') }}</span>
            </p>
            <div class="mt-auto flex items-center justify-between border-t border-line pt-4">
              <div>
                <span class="text-[13px] text-muted">Desde</span>
                <div class="text-2xl font-semibold tracking-tight">{{ bs(r.precio_desde_bs) }}</div>
              </div>
              <BaseButton variant="outline" size="sm" class="h-11" @click="buscarRuta(r.origen, r.destino)">Ver salidas</BaseButton>
            </div>
          </article>
        </div>
      </section>

    </div>

    <div class="mt-16 border-y border-line bg-surface">
      <div class="contenedor flex flex-col gap-10 py-16">
      <section aria-labelledby="buses-titulo" class="flex flex-col gap-6">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 id="buses-titulo" class="text-[28px] font-medium tracking-tight sm:text-[30px]">Nuestros buses</h2>
            <p class="mt-1 text-muted">Dos pisos pensados para viajar de noche.</p>
          </div>
          <RouterLink :to="{ name: 'buses' }" class="flex items-center gap-1 font-semibold text-accent-fg hover:underline">
            Conocer la flota <ArrowRight class="size-4" aria-hidden="true" />
          </RouterLink>
        </div>
        <div class="grid gap-5 md:grid-cols-2">
        <article
          v-for="t in tipos ?? []"
          :key="t.id"
          class="flex flex-col gap-3 rounded-card border border-line bg-canvas p-7"
        >
          <span class="w-fit rounded-full bg-accent-soft px-2.5 py-1 text-xs text-accent-fg">Planta {{ t.planta }}</span>
          <h3 class="text-[26px] font-medium tracking-tight">{{ t.nombre }} · {{ t.inclinacion_grados }}°</h3>
          <p class="text-muted">{{ t.descripcion }}</p>
          <ul class="mt-1 grid grid-cols-2 gap-2 text-sm">
            <li v-for="c in t.comodidades" :key="c.codigo" class="flex items-center gap-2">
              <span class="size-1.5 rounded-full bg-accent" aria-hidden="true" />{{ c.nombre }}
            </li>
          </ul>
        </article>
      </div>
      </section>

      <section aria-labelledby="ventajas-titulo">
        <h2 id="ventajas-titulo" class="sr-only">Por qué viajar con nosotros</h2>
        <ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <li v-for="v in ventajas" :key="v.titulo" class="flex gap-4 rounded-card border border-line bg-canvas p-5">
            <span class="flex size-11 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent-fg">
              <component :is="v.icono" class="size-5" aria-hidden="true" />
            </span>
            <div>
              <p class="font-semibold">{{ v.titulo }}</p>
              <p class="mt-1 text-sm text-muted">{{ v.texto }}</p>
            </div>
          </li>
        </ul>
      </section>
      </div>
    </div>

    <div class="contenedor flex flex-col gap-16 pt-16">

      <section aria-labelledby="carga-titulo" class="grid gap-8 overflow-hidden rounded-card border border-line bg-surface p-6 sm:p-10 lg:grid-cols-[1.2fr_1fr]">
        <div class="flex flex-col gap-4">
          <span class="flex size-12 items-center justify-center rounded-full bg-accent-soft text-accent-fg"><Package class="size-6" aria-hidden="true" /></span>
          <h2 id="carga-titulo" class="text-[28px] font-medium tracking-tight text-fg">Carga y encomiendas a 7 ciudades</h2>
          <p class="max-w-xl text-muted">
            Sobres y paquetes hasta 30 kg, carga con GPS y mudanzas. Paga en origen o en destino y sigue tu envío en tiempo real.
          </p>
          <div class="mt-2 flex flex-wrap gap-3">
            <BaseButton variant="secondary" :to="{ name: 'carga' }"><BadgePercent class="size-4" aria-hidden="true" />Cotizar un envío</BaseButton>
            <BaseButton variant="outline" :to="{ name: 'puerta-a-puerta' }"><Truck class="size-4" aria-hidden="true" />Pedir recojo a domicilio</BaseButton>
          </div>
        </div>
        <form class="flex flex-col gap-3 self-center rounded-inner border border-line bg-surface-2 p-5" @submit.prevent="rastrear">
          <TextInput v-model="guia" label="Rastrea tu envío" placeholder="Número de guía" inputmode="numeric" mono maxlength="12" />
          <BaseButton type="submit" block>Rastrear</BaseButton>
          <p class="text-[13px] text-muted">La guía de 8 dígitos está en tu comprobante de envío.</p>
        </form>
      </section>

      <section v-if="destacadas.length" aria-labelledby="faq-titulo" class="flex flex-col gap-5">
        <div class="flex flex-wrap items-end justify-between gap-3">
          <h2 id="faq-titulo" class="text-[28px] font-medium tracking-tight text-fg">Antes de viajar</h2>
          <RouterLink :to="{ name: 'ayuda' }" class="flex items-center gap-1 font-semibold text-accent-fg hover:underline">
            Centro de ayuda <ArrowRight class="size-4" aria-hidden="true" />
          </RouterLink>
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <RouterLink
            v-for="f in destacadas"
            :key="f.slug"
            :to="{ name: 'ayuda', hash: `#${f.slug}` }"
            class="rounded-card border border-line bg-surface p-5 transition hover:border-line-strong"
          >
            <p class="font-semibold text-fg">{{ f.pregunta }}</p>
            <p class="mt-1.5 line-clamp-2 text-sm text-muted">{{ f.respuesta_corta_voz ?? f.respuesta }}</p>
          </RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>
