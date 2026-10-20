<script setup lang="ts">
import { Eye, EyeOff, Headset, LockKeyhole, ShieldCheck, Ticket, Truck, UserCog, Warehouse } from '@lucide/vue'
import { nextTick, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import LogoMark from '@/components/brand/LogoMark.vue'
import RouteMapArt from '@/components/brand/RouteMapArt.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import TextInput from '@/components/ui/TextInput.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const ver = ref(false)
const cargando = ref(false)
const error = ref<string | null>(null)
const formulario = ref<HTMLFormElement | null>(null)

/**
 * Cuentas de demostración (las mismas de backend/seeds/data/demo.py). Este proyecto es una demo
 * pública: se muestran para que cualquiera pueda recorrer el panel con cada rol.
 */
const PASSWORD_DEMO = 'TransDemo2026!'
const CUENTAS_DEMO = [
  { rol: 'Administrador', correo: 'admin@transdemo.com', icono: ShieldCheck },
  { rol: 'Supervisor', correo: 'supervisor@transdemo.com', icono: UserCog },
  { rol: 'Boletería', correo: 'boleteria.sucre@transdemo.com', icono: Ticket },
  { rol: 'Bodega', correo: 'bodega.sucre@transdemo.com', icono: Warehouse },
  { rol: 'Repartidor', correo: 'reparto.sucre@transdemo.com', icono: Truck },
  { rol: 'Soporte', correo: 'soporte@transdemo.com', icono: Headset },
]

/** Rellena el formulario con la cuenta elegida y deja el foco en "Entrar". */
async function usarCuenta(correo: string): Promise<void> {
  email.value = correo
  password.value = PASSWORD_DEMO
  error.value = null
  await nextTick()
  formulario.value?.querySelector<HTMLButtonElement>('button[type=submit]')?.focus()
}

/** Solo se permite volver a rutas internas del panel (evita redirecciones abiertas). */
function destinoSeguro(): string {
  const s = route.query.siguiente
  return typeof s === 'string' && s.startsWith('/admin') && !s.startsWith('//') && !s.includes('\\') ? s : '/admin'
}

async function entrar(): Promise<void> {
  error.value = null
  if (!email.value.includes('@') || password.value.length < 1) {
    error.value = 'Ingresa tu correo y contraseña.'
    return
  }
  cargando.value = true
  try {
    await auth.iniciarSesion(email.value, password.value)
    password.value = ''
    await router.replace(destinoSeguro())
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'No pudimos iniciar sesión.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="grid min-h-dvh bg-canvas lg:grid-cols-[1.1fr_1fr]">
    <section class="hero m-3 hidden flex-col justify-between p-12 lg:flex">
      <LogoMark :size="40" subtitle="Panel de operación" />
      <div class="mx-auto w-full max-w-lg"><RouteMapArt /></div>
      <div>
        <p class="text-3xl leading-tight font-semibold tracking-tight">Salidas, boletería y carga<br />en un solo lugar.</p>
        <p class="mt-3 text-on-accent/85">Acceso exclusivo para el personal de TransDemo.</p>
      </div>
    </section>
    <section class="flex items-center justify-center px-4 py-12 sm:px-8">
      <form ref="formulario" class="flex w-full max-w-sm flex-col gap-5" novalidate @submit.prevent="entrar">
        <div class="lg:hidden"><LogoMark :size="36" tone="dark" /></div>
        <div>
          <h1 class="text-[28px] font-medium tracking-tight">Iniciar sesión</h1>
          <p class="mt-1 text-muted">Usa tu correo institucional.</p>
        </div>
        <TextInput id="login-email" v-model="email" label="Correo" type="email" autocomplete="username" required autofocus />
        <TextInput id="login-password" v-model="password" label="Contraseña" :type="ver ? 'text' : 'password'" autocomplete="current-password" required>
          <template #sufijo>
            <button type="button" class="-mr-1 flex size-9 items-center justify-center rounded-full text-muted hover:text-fg" :aria-label="ver ? 'Ocultar contraseña' : 'Mostrar contraseña'" @click="ver = !ver">
              <EyeOff v-if="ver" class="size-[18px]" /><Eye v-else class="size-[18px]" />
            </button>
          </template>
        </TextInput>
        <p v-if="error" class="rounded-inner bg-danger-soft px-4 py-3 text-sm font-medium text-danger-fg" role="alert">{{ error }}</p>
        <BaseButton type="submit" size="lg" block :loading="cargando"><LockKeyhole class="size-4" aria-hidden="true" />Entrar</BaseButton>

        <!-- Demo pública: un clic rellena el correo y la contraseña de cada rol -->
        <fieldset class="flex flex-col gap-3 rounded-card border border-line bg-surface p-4">
          <legend class="sr-only">Cuentas de demostración</legend>
          <div>
            <p class="text-sm font-semibold">Cuentas de demostración</p>
            <p class="mt-0.5 text-xs text-muted">
              Elige un rol para rellenar el acceso. Contraseña para todas:
              <code class="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-fg">{{ PASSWORD_DEMO }}</code>
            </p>
          </div>
          <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
            <button
              v-for="c in CUENTAS_DEMO"
              :key="c.correo"
              type="button"
              class="flex items-center gap-2 rounded-inner border px-3 py-2 text-left text-sm font-medium transition-colors"
              :class="email === c.correo ? 'border-accent-line bg-accent-soft text-accent-fg' : 'border-line hover:border-line-strong hover:bg-surface-2'"
              :aria-pressed="email === c.correo"
              :title="c.correo"
              @click="usarCuenta(c.correo)"
            >
              <component :is="c.icono" class="size-4 shrink-0" aria-hidden="true" />
              <span class="truncate">{{ c.rol }}</span>
            </button>
          </div>
        </fieldset>
        <RouterLink :to="{ name: 'inicio' }" class="text-center text-sm font-semibold text-muted hover:text-fg">← Volver al sitio</RouterLink>
      </form>
    </section>
  </div>
</template>
