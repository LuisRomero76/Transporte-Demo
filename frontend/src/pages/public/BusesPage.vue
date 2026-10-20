<script setup lang="ts">
import { Armchair, Bath, Luggage, PawPrint, Snowflake, Thermometer, Tv, Usb } from '@lucide/vue'
import type { Component } from 'vue'
import { usePoliticas, useTiposAsiento } from '@/api/queries'
import BaseButton from '@/components/ui/BaseButton.vue'
import SkeletonBlock from '@/components/ui/SkeletonBlock.vue'

const { data: tipos, isLoading } = useTiposAsiento()
const { data: politicas } = usePoliticas()

const iconos: Record<string, Component> = {
  asientos_reclinables: Armchair,
  cargadores_usb: Usb,
  calefaccion: Thermometer,
  bano_unisex: Bath,
  tv_individual: Tv,
  tv_cabina: Tv,
  aire_acondicionado: Snowflake,
}
</script>

<template>
  <div>
    <section class="hero rounded-none!">
      <div class="contenedor py-10 sm:py-14">
        <h1 class="text-[34px] font-medium tracking-tight sm:text-[44px]">Nuestros buses</h1>
        <p class="mt-2 max-w-2xl text-on-accent/85">
          Flota de dos pisos pensada para viajar de noche: Suite Cama en la planta alta y Leito Cama en la planta baja.
        </p>
      </div>
    </section>
    <div class="contenedor flex flex-col gap-10 py-10">
      <div class="grid gap-6 lg:grid-cols-2">
        <template v-if="isLoading"><SkeletonBlock v-for="n in 2" :key="n" class="h-80 rounded-card" /></template>
        <article
          v-for="t in tipos ?? []"
          :key="t.id"
          class="flex flex-col gap-5 overflow-hidden rounded-card border border-line bg-surface p-7 shadow-suave sm:p-8"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <span class="rounded-full bg-accent-soft px-2.5 py-1 text-xs text-accent-fg">
                Planta {{ t.planta }}
              </span>
              <h2 class="mt-2 text-[30px] font-medium tracking-tight">{{ t.nombre }}</h2>
            </div>
            <div class="text-right">
              <span class="text-5xl font-semibold tracking-tight">{{ t.inclinacion_grados }}°</span>
              <p class="text-xs text-muted">de reclinación</p>
            </div>
          </div>
          <p class="text-muted">{{ t.descripcion }}</p>
          <ul class="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <li
              v-for="c in t.comodidades"
              :key="c.codigo"
              class="flex flex-col items-start gap-2 rounded-inner border border-line bg-surface-2 p-4 text-sm font-medium"
            >
              <span class="grid size-8 place-items-center rounded-full bg-accent-soft text-accent-fg"><component :is="iconos[c.codigo] ?? Armchair" class="size-4" aria-hidden="true" /></span>
              {{ c.nombre }}
            </li>
          </ul>
        </article>
      </div>

      <section class="grid gap-4 md:grid-cols-2">
        <div class="flex gap-4 rounded-card border border-line bg-surface p-6">
          <span class="grid size-11 shrink-0 place-items-center rounded-full bg-accent-soft text-accent-fg"><Luggage class="size-5" aria-hidden="true" /></span>
          <div>
            <h2 class="font-sans text-lg font-medium tracking-tight">Equipaje</h2>
            <p class="mt-1 text-sm text-muted">
              {{ politicas?.equipaje_bodega_kg ?? 20 }} kg en bodega y {{ politicas?.equipaje_mano_kg ?? 5 }} kg de mano por pasajero.
              El exceso se cobra por kilo según la ruta.
            </p>
          </div>
        </div>
        <div class="flex gap-4 rounded-card border border-line bg-surface p-6">
          <span class="grid size-11 shrink-0 place-items-center rounded-full bg-accent-soft text-accent-fg"><PawPrint class="size-5" aria-hidden="true" /></span>
          <div>
            <h2 class="font-sans text-lg font-medium tracking-tight">Mascotas</h2>
            <p class="mt-1 text-sm text-muted">{{ politicas?.mascotas }}</p>
          </div>
        </div>
      </section>
      <BaseButton :to="{ name: 'inicio' }" size="lg" class="self-center">Buscar pasajes</BaseButton>
    </div>
  </div>
</template>
