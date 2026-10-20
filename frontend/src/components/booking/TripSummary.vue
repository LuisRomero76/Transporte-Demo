<script setup lang="ts">
import type { Schemas } from '@/api/client'
import { fechaCorta, hora } from '@/lib/format'

defineProps<{ salida: Schemas['SalidaResumen'] | Schemas['SalidaDeReserva']; etiqueta?: string }>()
</script>

<template>
  <div class="hero flex flex-col gap-2 rounded-none! px-5 py-5">
    <span class="hero-chip w-fit">{{ etiqueta ?? 'Tu viaje' }}</span>
    <strong class="text-xl font-semibold tracking-tight">{{ salida.origen }} → {{ salida.destino }}</strong>
    <span class="text-sm text-on-accent/85">
      {{ fechaCorta(salida.fecha_hora_salida) }} · {{ hora(salida.fecha_hora_salida) }} → {{ hora(salida.fecha_hora_llegada_estimada) }}
      <template v-if="salida.anden"> · Andén {{ salida.anden }}</template>
    </span>
    <slot />
  </div>
</template>
