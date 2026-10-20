<script setup lang="ts">
import { BusFront, CircleHelp, Menu, MessageCircle, Package, Ticket, X } from '@lucide/vue'
import { DialogContent, DialogOverlay, DialogPortal, DialogRoot, DialogTitle } from 'reka-ui'
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useEmpresa } from '@/api/queries'
import LogoMark from '@/components/brand/LogoMark.vue'
import PillNav from '@/components/ui/PillNav.vue'
import { telefono, whatsappUrl } from '@/lib/format'

const route = useRoute()
const { data: empresa } = useEmpresa()
const menuAbierto = ref(false)
watch(() => route.fullPath, () => (menuAbierto.value = false))

const enlaces = [
  { to: { name: 'inicio' }, label: 'Pasajes', nombre: 'inicio' },
  { to: { name: 'rutas' }, label: 'Rutas', nombre: 'rutas' },
  { to: { name: 'buses' }, label: 'Nuestros buses', nombre: 'buses' },
  { to: { name: 'carga' }, label: 'Carga', nombre: 'carga' },
  { to: { name: 'oficinas' }, label: 'Oficinas', nombre: 'oficinas' },
  { to: { name: 'ayuda' }, label: 'Ayuda', nombre: 'ayuda' },
]
const inferior = [
  { to: { name: 'inicio' }, label: 'Pasajes', icono: BusFront, nombres: ['inicio', 'resultados', 'asientos', 'pasajeros', 'pago'] },
  { to: { name: 'rastreo' }, label: 'Envíos', icono: Package, nombres: ['rastreo', 'carga', 'puerta-a-puerta'] },
  { to: { name: 'mi-reserva' }, label: 'Mi reserva', icono: Ticket, nombres: ['mi-reserva', 'confirmacion'] },
  { to: { name: 'ayuda' }, label: 'Ayuda', icono: CircleHelp, nombres: ['ayuda', 'oficinas'] },
]
const activo = (nombres: string[]) => nombres.includes(String(route.name))
const menu = computed(() => enlaces.map((e) => ({ key: e.nombre, label: e.label, to: e.to, active: route.name === e.nombre })))
</script>

<template>
  <div class="flex min-h-dvh flex-col bg-canvas">
    <header class="no-print sticky top-0 z-40 border-b border-line bg-surface/95 backdrop-blur supports-[backdrop-filter]:bg-surface/85">
      <div class="contenedor flex h-16 items-center justify-between gap-4 md:h-[72px]">
        <RouterLink :to="{ name: 'inicio' }" aria-label="TransDemo, ir al inicio" class="shrink-0">
          <LogoMark :size="34" tone="dark" />
        </RouterLink>
        <PillNav :items="menu" label="Principal" plano class="hidden lg:block" />
        <div class="flex items-center gap-2">
          <RouterLink
            :to="{ name: 'mi-reserva' }"
            class="hidden h-10 items-center gap-2 rounded-full border border-line-strong px-4 text-sm font-medium text-fg transition-colors hover:bg-surface-2 sm:inline-flex"
          >
            <Ticket class="size-4" aria-hidden="true" />Mi reserva
          </RouterLink>
          <a
            v-if="empresa?.whatsapp_central_e164"
            :href="whatsappUrl(empresa.whatsapp_central_e164, 'Hola, quiero hacer una consulta.')"
            target="_blank"
            rel="noopener noreferrer"
            class="hidden h-10 items-center gap-2 rounded-full bg-pill-active px-4 text-sm font-medium text-pill-active-fg transition-opacity hover:opacity-85 md:inline-flex"
          >
            <MessageCircle class="size-4" aria-hidden="true" />{{ telefono(empresa.whatsapp_central_e164).replace('+591 ', '') }}
          </a>
          <button class="flex size-11 items-center justify-center rounded-full text-fg hover:bg-surface-2 lg:hidden" aria-label="Abrir menú" @click="menuAbierto = true">
            <Menu class="size-6" />
          </button>
        </div>
      </div>
    </header>

    <DialogRoot v-model:open="menuAbierto">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-overlay lg:hidden" />
        <DialogContent
          class="fixed inset-y-0 right-0 z-50 flex w-[86vw] max-w-sm flex-col border-l border-line bg-surface p-5 text-fg shadow-flotante data-[state=open]:animate-aparecer lg:hidden"
        >
          <div class="flex items-center justify-between">
            <DialogTitle class="sr-only">Menú</DialogTitle>
            <LogoMark :size="30" tone="dark" />
            <button class="flex size-11 items-center justify-center rounded-full bg-surface-2 text-muted hover:text-fg" aria-label="Cerrar menú" @click="menuAbierto = false">
              <X class="size-5" />
            </button>
          </div>
          <nav aria-label="Menú móvil" class="mt-6 flex flex-col gap-1">
            <RouterLink
              v-for="e in enlaces"
              :key="e.nombre"
              :to="e.to"
              class="rounded-full px-4 py-3 text-[17px] font-medium transition-colors hover:bg-surface-2"
              exact-active-class="!bg-accent-soft text-accent-fg"
            >
              {{ e.label }}
            </RouterLink>
            <RouterLink :to="{ name: 'rastreo' }" class="rounded-full px-4 py-3 text-[17px] font-medium hover:bg-surface-2">Rastrear envío</RouterLink>
            <RouterLink :to="{ name: 'mi-reserva' }" class="rounded-full px-4 py-3 text-[17px] font-medium hover:bg-surface-2">Mi reserva</RouterLink>
          </nav>
          <a
            v-if="empresa?.whatsapp_central_e164"
            :href="whatsappUrl(empresa.whatsapp_central_e164, 'Hola, quiero hacer una consulta.')"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-auto flex h-12 items-center justify-center gap-2 rounded-full bg-accent font-medium text-on-accent hover:bg-accent-2"
          >
            <MessageCircle class="size-5" aria-hidden="true" />Escríbenos por WhatsApp
          </a>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>

    <main id="contenido" class="flex-1" tabindex="-1">
      <RouterView v-slot="{ Component }">
        <Transition name="pagina" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
    </main>

    <footer class="no-print mt-12 bg-ink pb-20 text-on-accent/70 lg:pb-0">
      <div class="contenedor grid gap-10 py-14 md:grid-cols-[1.4fr_1fr_1fr_1fr]">
        <div class="flex flex-col gap-4">
          <LogoMark :size="34" subtitle="Pasajes · Carga · Encomiendas" />
          <p class="max-w-sm text-sm leading-relaxed">
            Empresa regulada y fiscalizada por la Autoridad de Telecomunicaciones y Transportes (ATT) del Estado
            Plurinacional de Bolivia.
          </p>
        </div>
        <div class="flex flex-col gap-2.5 text-sm">
          <p class="font-medium text-on-accent">Viaja</p>
          <RouterLink :to="{ name: 'inicio' }" class="hover:text-on-accent">Comprar pasajes</RouterLink>
          <RouterLink :to="{ name: 'rutas' }" class="hover:text-on-accent">Rutas e itinerarios</RouterLink>
          <RouterLink :to="{ name: 'buses' }" class="hover:text-on-accent">Nuestros buses</RouterLink>
          <RouterLink :to="{ name: 'mi-reserva' }" class="hover:text-on-accent">Mi reserva</RouterLink>
        </div>
        <div class="flex flex-col gap-2.5 text-sm">
          <p class="font-medium text-on-accent">Envía</p>
          <RouterLink :to="{ name: 'carga' }" class="hover:text-on-accent">Carga y encomiendas</RouterLink>
          <RouterLink :to="{ name: 'rastreo' }" class="hover:text-on-accent">Rastrear envío</RouterLink>
          <RouterLink :to="{ name: 'puerta-a-puerta' }" class="hover:text-on-accent">Puerta a puerta</RouterLink>
          <RouterLink :to="{ name: 'oficinas' }" class="hover:text-on-accent">Boleterías y bodegas</RouterLink>
        </div>
        <div class="flex flex-col gap-2.5 text-sm">
          <p class="font-medium text-on-accent">Contacto</p>
          <span>WhatsApp {{ telefono(empresa?.whatsapp_central_e164) }}</span>
          <span>Atención al cliente {{ telefono(empresa?.telefono_atencion_cliente_e164) }}</span>
          <RouterLink :to="{ name: 'ayuda' }" class="hover:text-on-accent">Centro de ayuda</RouterLink>
          <RouterLink :to="{ name: 'terminos' }" class="hover:text-on-accent">Términos y condiciones</RouterLink>
        </div>
      </div>
      <div class="border-t border-on-accent/10">
        <div class="contenedor flex flex-col gap-2 py-5 text-xs sm:flex-row sm:justify-between">
          <span>© {{ new Date().getFullYear() }} TransDemo S.R.L.</span>
          <RouterLink :to="{ name: 'admin-login' }" class="hover:text-on-accent">Acceso del personal</RouterLink>
        </div>
      </div>
    </footer>

    <nav
      aria-label="Accesos rápidos"
      class="no-print fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-surface/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
    >
      <RouterLink
        v-for="i in inferior"
        :key="i.label"
        :to="i.to"
        class="flex h-16 flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors"
        :class="activo(i.nombres) ? 'text-accent-fg' : 'text-muted hover:text-fg'"
        :aria-current="activo(i.nombres) ? 'page' : undefined"
      >
        <span class="flex h-7 w-14 items-center justify-center rounded-full transition-colors" :class="activo(i.nombres) ? 'bg-accent-soft' : ''">
          <component :is="i.icono" class="size-5" aria-hidden="true" />
        </span>
        {{ i.label }}
      </RouterLink>
    </nav>
  </div>
</template>

<style>
.pagina-enter-active,
.pagina-leave-active {
  transition: opacity 0.15s ease;
}
.pagina-enter-from,
.pagina-leave-to {
  opacity: 0;
}
</style>
