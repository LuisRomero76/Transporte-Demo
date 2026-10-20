<script setup lang="ts">
import {
  BarChart3,
  BookOpen,
  Bus,
  ClipboardList,
  House,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Package,
  PackagePlus,
  PanelLeftClose,
  PanelLeftOpen,
  Receipt,
  RotateCcw,
  ScanLine,
  Search,
  ShieldCheck,
  Sun,
  Ticket,
  UserRound,
  Users,
  X,
} from '@lucide/vue'
import { onKeyStroke, useStorage } from '@vueuse/core'
import { DialogContent, DialogOverlay, DialogPortal, DialogRoot, DialogTitle } from 'reka-ui'
import { computed, ref, watch, type Component } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import LogoMark from '@/components/brand/LogoMark.vue'
import { iniciales } from '@/lib/format'
import { ROL } from '@/lib/labels'
import { ACCESO } from '@/lib/roles'
import { useAuthStore, type Rol } from '@/stores/auth'
import { useTemaStore } from '@/stores/tema'

const auth = useAuthStore()
const tema = useTemaStore()
const route = useRoute()
const router = useRouter()
const menuMovil = ref(false)
watch(() => route.fullPath, () => (menuMovil.value = false))

// Rail lateral: solo iconos o expandido con texto (preferencia de cada navegador).
const railAbierto = useStorage('em.panel.rail', false)

interface Item {
  to: string
  label: string
  icono: Component
  roles: Rol[]
}
const secciones: { titulo: string; items: Item[] }[] = [
  {
    titulo: 'Operación',
    items: [
      { to: '/admin', label: 'Tablero', icono: LayoutDashboard, roles: ACCESO.tablero },
      { to: '/admin/salidas', label: 'Salidas', icono: Bus, roles: ACCESO.salidas },
      { to: '/admin/boleteria', label: 'Boletería', icono: Ticket, roles: ACCESO.boleteria },
      { to: '/admin/abordaje', label: 'Abordaje', icono: ScanLine, roles: ACCESO.abordaje },
      { to: '/admin/ventas', label: 'Ventas', icono: ClipboardList, roles: ACCESO.ventas },
      { to: '/admin/pagos-whatsapp', label: 'Pagos por WhatsApp', icono: Receipt, roles: ACCESO.pagosWhatsapp },
      { to: '/admin/reembolsos', label: 'Reembolsos', icono: RotateCcw, roles: ACCESO.reembolsos },
    ],
  },
  {
    titulo: 'Carga',
    items: [
      { to: '/admin/encomiendas', label: 'Encomiendas', icono: Package, roles: ACCESO.encomiendas },
      { to: '/admin/encomiendas/nueva', label: 'Nueva encomienda', icono: PackagePlus, roles: ACCESO.encomiendasRegistrar },
      { to: '/admin/puerta-a-puerta', label: 'Puerta a puerta', icono: House, roles: ACCESO.puerta },
    ],
  },
  {
    titulo: 'Administración',
    items: [
      { to: '/admin/catalogos', label: 'Catálogos', icono: BookOpen, roles: ACCESO.catalogos },
      { to: '/admin/personal', label: 'Personal', icono: Users, roles: ACCESO.personal },
      { to: '/admin/clientes', label: 'Clientes', icono: UserRound, roles: ACCESO.clientes },
      { to: '/admin/reportes', label: 'Reportes', icono: BarChart3, roles: ACCESO.reportes },
      { to: '/admin/auditoria', label: 'Auditoría', icono: ShieldCheck, roles: ACCESO.auditoria },
    ],
  },
]
const visibles = computed(() =>
  secciones.map((s) => ({ ...s, items: s.items.filter((i) => auth.puede(i.roles)) })).filter((s) => s.items.length),
)
function activo(to: string): boolean {
  if (to === '/admin') return route.path === '/admin'
  if (to === '/admin/encomiendas') return route.path.startsWith('/admin/encomiendas') && route.path !== '/admin/encomiendas/nueva'
  return route.path.startsWith(to)
}
// Barra inferior en móvil: tres accesos frecuentes (según permisos) y el menú completo.
const rapidos = computed(() =>
  visibles.value.flatMap((s) => s.items).filter((i) => ['/admin', '/admin/boleteria', '/admin/encomiendas'].includes(i.to)),
)

async function salir(): Promise<void> {
  await auth.cerrarSesion()
  void router.push({ name: 'admin-login' })
}

// Buscador global: guía (8 dígitos), reserva (6 caracteres) o cliente (documento/nombre).
const busqueda = ref('')
const campo = ref<HTMLInputElement | null>(null)
onKeyStroke('/', (e) => {
  const t = e.target as HTMLElement | null
  if (t && ['INPUT', 'TEXTAREA', 'SELECT'].includes(t.tagName)) return
  e.preventDefault()
  campo.value?.focus()
})
function buscar(): void {
  const q = busqueda.value.trim()
  if (!q) return
  const digitos = q.replace(/\D/g, '')
  if (/^\d{8}$/.test(q) && auth.puede(ACCESO.encomiendas)) void router.push({ name: 'admin-encomienda', params: { guia: q } })
  else if (/^[A-Za-z0-9]{6}$/.test(q) && /[A-Za-z]/.test(q) && auth.puede(ACCESO.ventas))
    void router.push({ name: 'admin-ventas', query: { codigo: q.toUpperCase() } })
  else if (auth.puede(ACCESO.clientes)) void router.push({ name: 'admin-clientes', query: { q } })
  else if (digitos) void router.push({ name: 'admin-encomiendas', query: { q } })
  busqueda.value = ''
}
const titulo = computed(() => route.meta.title ?? 'Panel')
const nombreCompleto = computed(() => `${auth.usuario?.nombres ?? ''} ${auth.usuario?.apellidos ?? ''}`)
</script>

<template>
  <div class="min-h-dvh bg-canvas text-fg">
    <aside
      class="no-print fixed inset-y-3 left-3 z-30 hidden flex-col gap-2 transition-[width] duration-300 ease-[cubic-bezier(.2,.8,.2,1)] lg:flex"
      :class="railAbierto ? 'w-58' : 'w-14'"
    >
      <RouterLink
        to="/admin"
        class="flex h-14 shrink-0 items-center overflow-hidden rounded-full border border-line bg-surface shadow-suave"
        :class="railAbierto ? 'px-3' : 'justify-center'"
        aria-label="TransDemo, ir al tablero"
      >
        <LogoMark :size="32" tone="dark" :wordmark="railAbierto" subtitle="Panel de operación" />
      </RouterLink>

      <nav aria-label="Panel" class="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto [scrollbar-width:thin]">
        <div
          v-for="s in visibles"
          :key="s.titulo"
          class="flex shrink-0 flex-col gap-0.5 border border-line bg-surface p-1 shadow-suave"
          :class="railAbierto ? 'rounded-inner' : 'rounded-full'"
          role="group"
          :aria-label="s.titulo"
        >
          <p v-if="railAbierto" class="px-3 pt-1.5 pb-0.5 text-xs text-muted">{{ s.titulo }}</p>
          <RouterLink
            v-for="i in s.items"
            :key="i.to"
            :to="i.to"
            class="flex shrink-0 items-center gap-3 rounded-full text-[13px] transition-colors"
            :class="[
              railAbierto ? 'h-9 px-3.5' : 'h-10 justify-center',
              activo(i.to) ? 'bg-pill-active font-medium text-pill-active-fg' : 'text-muted hover:bg-surface-2 hover:text-fg',
            ]"
            :aria-current="activo(i.to) ? 'page' : undefined"
            :title="railAbierto ? undefined : i.label"
          >
            <component :is="i.icono" class="size-[18px] shrink-0" aria-hidden="true" />
            <span :class="railAbierto ? 'truncate' : 'sr-only'">{{ i.label }}</span>
          </RouterLink>
        </div>
      </nav>

      <div class="flex shrink-0 flex-col gap-1 border border-line bg-surface p-1 shadow-suave" :class="railAbierto ? 'rounded-inner' : 'rounded-full'">
        <button
          class="flex h-11 items-center gap-3 rounded-full text-[13px] text-muted transition-colors hover:bg-surface-2 hover:text-fg"
          :class="railAbierto ? 'px-3.5' : 'justify-center'"
          :aria-label="railAbierto ? 'Contraer menú' : 'Expandir menú'"
          :aria-expanded="railAbierto"
          :title="railAbierto ? undefined : 'Expandir menú'"
          @click="railAbierto = !railAbierto"
        >
          <PanelLeftClose v-if="railAbierto" class="size-[18px] shrink-0" aria-hidden="true" />
          <PanelLeftOpen v-else class="size-[18px] shrink-0" aria-hidden="true" />
          <span v-if="railAbierto">Contraer</span>
        </button>
        <button
          class="flex h-11 items-center gap-3 rounded-full text-[13px] text-muted transition-colors hover:bg-danger-soft hover:text-danger-fg"
          :class="railAbierto ? 'px-3.5' : 'justify-center'"
          aria-label="Cerrar sesión"
          title="Cerrar sesión"
          @click="salir"
        >
          <LogOut class="size-[18px] shrink-0" aria-hidden="true" />
          <span v-if="railAbierto">Cerrar sesión</span>
        </button>
      </div>
    </aside>

    <div class="flex min-h-dvh flex-col transition-[padding] duration-300" :class="railAbierto ? 'lg:pl-64' : 'lg:pl-20'">
      <header class="no-print sticky top-0 z-20 flex items-center gap-3 px-3 pt-3 pb-2 sm:px-6 lg:pr-8 lg:pl-4">
        <div class="pill-group min-w-0 items-center lg:hidden">
          <RouterLink to="/admin" class="flex size-9 shrink-0 items-center justify-center" aria-label="TransDemo, ir al tablero">
            <LogoMark :size="30" :wordmark="false" />
          </RouterLink>
          <span class="truncate pr-3 text-[13px] font-medium">{{ titulo }}</span>
        </div>
        <form class="hidden max-w-md flex-1 md:block" role="search" @submit.prevent="buscar">
          <label for="buscador-global" class="sr-only">Buscar guía, reserva o cliente</label>
          <div
            class="flex h-11 items-center gap-2 rounded-full border border-line bg-surface px-4 shadow-suave transition-colors focus-within:border-accent-line focus-within:ring-4 focus-within:ring-(--ring)"
          >
            <Search class="size-4 text-muted" aria-hidden="true" />
            <input
              id="buscador-global"
              ref="campo"
              v-model="busqueda"
              class="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted"
              placeholder="Guía, código de reserva o CI"
              autocomplete="off"
            />
            <kbd class="rounded-full border border-line bg-surface-2 px-2 text-[11px] text-muted">/</kbd>
          </div>
        </form>
        <div class="pill-group ml-auto shrink-0 items-center">
          <RouterLink :to="{ name: 'inicio' }" class="hidden h-9 items-center rounded-full px-3.5 text-[13px] font-medium text-muted hover:bg-surface-2 hover:text-fg xl:inline-flex">
            Ver portal
          </RouterLink>
          <button
            class="flex size-9 items-center justify-center rounded-full text-muted transition-colors hover:bg-surface-2 hover:text-fg"
            :aria-label="tema.oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
            :aria-pressed="tema.oscuro"
            @click="tema.alternar()"
          >
            <Sun v-if="tema.oscuro" class="size-[18px]" /><Moon v-else class="size-[18px]" />
          </button>
          <span class="hidden items-center gap-2.5 rounded-full bg-surface-2 py-1 pr-4 pl-1 sm:flex">
            <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-pill-active text-[12px] font-medium text-pill-active-fg">
              {{ iniciales(nombreCompleto) }}
            </span>
            <span class="min-w-0 text-[12px] leading-tight">
              <span class="block max-w-36 truncate font-medium">{{ auth.usuario?.nombres }} {{ auth.usuario?.apellidos?.split(' ')[0] }}</span>
              <span class="block max-w-36 truncate text-muted">{{ ROL[auth.usuario?.rol ?? ''] }}</span>
            </span>
          </span>
        </div>
      </header>
      <main id="contenido" class="flex-1 px-3 pt-4 pb-28 sm:px-6 lg:pr-8 lg:pb-8 lg:pl-4" tabindex="-1">
        <RouterView />
      </main>
    </div>

    <nav
      aria-label="Accesos rápidos del panel"
      class="no-print fixed inset-x-3 bottom-[max(0.75rem,env(safe-area-inset-bottom))] z-30 flex gap-1 rounded-full border border-line bg-surface/95 p-1 shadow-flotante backdrop-blur lg:hidden"
    >
      <RouterLink
        v-for="i in rapidos"
        :key="i.to"
        :to="i.to"
        class="flex h-13 min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-full text-[11px] font-medium transition-colors"
        :class="activo(i.to) ? 'bg-pill-active text-pill-active-fg' : 'text-muted hover:text-fg'"
        :aria-current="activo(i.to) ? 'page' : undefined"
      >
        <component :is="i.icono" class="size-5" aria-hidden="true" /><span class="max-w-full truncate px-1">{{ i.label }}</span>
      </RouterLink>
      <button
        class="flex h-13 flex-1 flex-col items-center justify-center gap-0.5 rounded-full text-[11px] font-medium text-muted hover:text-fg"
        aria-label="Abrir menú"
        @click="menuMovil = true"
      >
        <Menu class="size-5" aria-hidden="true" />Menú
      </button>
    </nav>

    <DialogRoot v-model:open="menuMovil">
      <DialogPortal>
        <DialogOverlay class="fixed inset-0 z-50 bg-overlay lg:hidden" />
        <DialogContent
          class="fixed inset-y-3 left-3 z-50 flex w-[calc(82vw-0.75rem)] max-w-xs flex-col rounded-card border border-line bg-surface text-fg shadow-flotante data-[state=open]:animate-aparecer lg:hidden"
        >
          <div class="flex items-center justify-between px-5 pt-5 pb-3">
            <DialogTitle class="sr-only">Menú del panel</DialogTitle>
            <LogoMark :size="30" tone="dark" />
            <button class="flex size-10 items-center justify-center rounded-full bg-surface-2 text-muted hover:text-fg" aria-label="Cerrar menú" @click="menuMovil = false"><X class="size-5" /></button>
          </div>
          <form class="px-4 pb-2" role="search" @submit.prevent="buscar">
            <label for="buscador-movil" class="sr-only">Buscar</label>
            <input
              id="buscador-movil"
              v-model="busqueda"
              class="h-11 w-full rounded-full border border-line bg-surface-2 px-4 text-sm text-fg outline-none placeholder:text-muted focus:border-accent-line focus:ring-4 focus:ring-(--ring)"
              placeholder="Guía, reserva o CI"
            />
          </form>
          <nav aria-label="Panel móvil" class="flex-1 overflow-y-auto px-3 pb-4">
            <div v-for="s in visibles" :key="s.titulo" class="mt-3">
              <p class="px-3 pb-1.5 text-xs text-muted">{{ s.titulo }}</p>
              <RouterLink
                v-for="i in s.items"
                :key="i.to"
                :to="i.to"
                class="flex h-11 items-center gap-3 rounded-full px-3.5 text-[15px] transition-colors"
                :class="activo(i.to) ? 'bg-pill-active font-medium text-pill-active-fg' : 'hover:bg-surface-2'"
              >
                <component :is="i.icono" class="size-5" aria-hidden="true" />{{ i.label }}
              </RouterLink>
            </div>
          </nav>
          <button class="m-4 flex h-11 items-center justify-center gap-2 rounded-full border border-line bg-surface-2 font-medium text-fg hover:text-danger-fg" @click="salir">
            <LogOut class="size-4" aria-hidden="true" />Cerrar sesión
          </button>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </div>
</template>
